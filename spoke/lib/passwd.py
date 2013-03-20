"""LDAP user account management module.

Classes:
SpokePwd - Creation/deletion/retrieval of LDAP user passwords.
Exceptions:
AuthError - raised on failed authentication attempts.
NotFound - raised on failure to find an object when one is expected.
AlreadyExists -raised on attempts to create an object when one already exists.
"""
# core modules
import os
import logging
import hashlib
from base64 import encodestring as encode
from base64 import decodestring as decode

# own modules
import spoke.lib.error as error
import spoke.lib.config as config
from spoke.lib.directory import SpokeLDAP
from spoke.lib.user import SpokeUser

# 3rd party modules
import ldap

class SpokePwd(SpokeLDAP):
    
    """Provide CRUD methods to LDAP password objects."""

    def __init__(self, org_name, user_id):
        """Get config, setup logging and LDAP connection."""
        SpokeLDAP.__init__(self)
        self.config = config.setup()
        self.log = logging.getLogger(__name__)
        try:
            self.user_pwd_attr = self.config.get('ATTR_MAP', 'user_password')
        except:
            self.user_pwd_attr = 'userPassword'
        self.retrieve_attr = [self.user_pwd_attr]
        self.filter = self.user_pwd_attr + '=*'
        self.org_name = org_name
        self.user_id = user_id
        self.user = self._get_user(self.org_name, self.user_id)
        self.user_dn = self.user['data'][0].__getitem__(0)
        self.user_attrs = self.user['data'][0].__getitem__(1)
        self.user_classes = self.user_attrs['objectClass']
        self.server = self.config.get('LDAP', 'server')
        self.port = self.config.get('LDAP', 'port', '389')
        self.start_tls = self.config.get('LDAP', 'start_tls', False)
        self.search_scope = 2 # ldap.SUB
        
    def _get_user(self, org_name, user_id):
        """Retrieve a user object."""
        user = SpokeUser(org_name)
        result = user.get(user_id, unique=True)
        if result == []:
            msg = "Can't find user %s with org %s" % (user_id, org_name)
            self.log.error(msg)
            raise error.NotFound(msg)          
        return result
    
    def _gen_hash_ssha(self, password):
        """Return a {SSHA} (RFC 2307) password value from a string."""
        salt = os.urandom(4)
        hash = hashlib.sha1(password)
        hash.update(salt)
        return "{SSHA}" + encode(hash.digest() + salt)[:-1]

    def _check_password(self, challenge_password, password):
        challenge_bytes = decode(challenge_password[6:])
        digest = challenge_bytes[:20]
        salt = challenge_bytes[20:]
        hash = hashlib.sha1(password)
        hash.update(salt)
        return digest == hash.digest()

    def create(self, password):
        """Create a user account's password; return True."""
        password_hash = self._gen_hash_ssha(password)
        dn = self.user_dn
        dn_info = []
        if self.user_pwd_attr in self.user_attrs:
            msg = 'Password already set for user %s.' % self.user_dn
            raise error.AlreadyExists(msg)
        dn_info.append((ldap.MOD_ADD, self.user_pwd_attr, password_hash)) 
        self.log.debug('Adding %s to %s ' % (dn_info, dn))
        result = self._create_object(dn, dn_info)
        if len(result['data']) == 1: # we got our user object back
            result['data'] = ['success']
            result['msg'] = 'Password created for user %s' % self.user_id
        self.log.debug('Result: %s' % result)
        return result

    def get(self, password):
        """Find a user account's password; return password object."""
        testldap = ldap.initialize('ldap://%s:%s' %
                                         (self.server, self.port))
        self.LDAP.protocol_version = 3 #ldap.VERSION3
        if self.start_tls:
            testldap.start_tls_s()
        try:
            testldap.simple_bind_s(self.user_dn, password)                     
        except ldap.INVALID_CREDENTIALS:
            msg = "Invalid password for user %s" % self.user_id
            raise error.AuthError(msg)
        result = ['success']
        result = self._process_results(result, __name__)
        result['msg'] = 'Password validated for user %s' % self.user_id
        self.log.debug('Result: %s' % result)
        return result
    
    def modify(self, password, new_password):
        """Modify a user account's password; return True."""
        result = False   
        if password == new_password:
            msg = 'New password matches old, nothing to do'
            raise error.AlreadyExists(msg)
        # Verify old password before proceeding
        if self.get(password):
            if self.delete():
                # We need to fetch our user attributes again or self.create
                # will use the old attributes and think the pwd is still set.
                self.user = self._get_user(self.org_name, self.user_id)
                self.user_attrs = self.user['data'][0].__getitem__(1)         
                result = self.create(new_password)
                result['msg'] = 'Password modified for user %s' % self.user_id
        return result
           
    def delete(self):
        """Delete a user account's password; return True."""           
        dn_info = []
        dn = self.user_dn
        if not self.user_pwd_attr in self.user_attrs:
            msg = 'Password missing for user %s, cannot delete.' % self.user_id
            raise error.NotFound(msg)
        dn_info.append((ldap.MOD_DELETE, self.user_pwd_attr, None))
        self.log.debug('Deleting %s from user %s ' % (dn_info, dn))
        result = self._delete_object(dn, dn_info)
        result['msg'] = 'Password deleted for user %s' % self.user_id
        self.log.debug('Result: %s' % result)
        return result
