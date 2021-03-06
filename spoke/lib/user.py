"""LDAP user account management module.

Classes:
SpokeUser - Allows easy creation/deletion/retrieval of LDAP user accounts.

Exceptions:
NotFound - raised on attempts to delete a missing object.
InputError - raised on invalid input.
"""
# core modules
import logging

# own modules
import spoke.lib.common as common
import spoke.lib.error as error
import spoke.lib.config as config
from spoke.lib.directory import SpokeLDAP
from spoke.lib.org import SpokeOrg

class SpokeUser(SpokeLDAP):
    
    """Provide CRUD methods to LDAP user account objects."""

    def __init__(self, org_name):
        """Get config, setup logging and LDAP connection."""
        SpokeLDAP.__init__(self)     
        self.config = config.setup()
        self.log = logging.getLogger(__name__)
        self.search_scope = 2 #ldap.SCOPE_SUBTREE
        self.retrieve_attr = None
        self.org_name = org_name
        self.org = self._get_org(self.org_name)
        self.org_dn = self.org['data'][0].__getitem__(0)
        self.org_attrs = self.org['data'][0].__getitem__(1)
        self.org_classes = self.org_attrs['objectClass']
        self.org_attr = self.config.get('ATTR_MAP', 'org_attr', 'o')
        self.container_attr = self.config.get('ATTR_MAP', 'container_attr', 'ou')
        self.user_login = self.config.get('ATTR_MAP', 'user_login', 'aenetAccountLoginName')
        self.user_class = self.config.get('ATTR_MAP', 'user_class', 'aenetAccount')
        self.user_key = self.config.get('ATTR_MAP', 'user_key', 'uid')
        self.user_name = self.config.get('ATTR_MAP', 'user_name', 'aenetAccountDisplayName')
        self.user_enable = self.config.get('ATTR_MAP', 'user_enable', 'aenetAccountEnabled')
        self.user_container = self.config.get('ATTR_MAP', 'user_container', 'people')
        
    def _get_org(self, org_name):
        """Retrieve our org object."""
        org = SpokeOrg()
        result = org.get(org_name)
        if result['data'] == []:
            msg = "Can't find org %s" % org_name
            self.log.error(msg)
            raise error.NotFound(msg)          
        return result
  
    def _gen_user_info(self, first, last=None):
        self.cn = first
        if last is None:
            self.sn = self.cn
            self.user_id = self.cn
        else:
            self.sn = last
            self.user_id = self.cn + last

    def create(self, email_addr, first, last=None):
        """Create a user account; return a user object"""
        self._gen_user_info(first, last)
        email_addr = common.validate_email_address(email_addr)
        filter = '%s=%s' % (self.user_key, self.user_id) 
        self.log.debug('Creating user %s in org: %s' % \
                      (self.user_id, self.org_name))  
        
        rdn = '%s=%s' % (self.user_key, self.user_id)
        container = '%s=%s' % (self.container_attr, self.user_container)
        dn = '%s,%s,%s' % (rdn, container, self.org_dn)
        dn_attr = { 'objectClass': ['top', 'inetOrgPerson', self.user_class],
                    self.user_key: [self.user_id],
                    'cn': [self.cn], 'sn': [self.sn], 
                    self.user_name: [self.user_id],
                    self.user_login: [email_addr],
                    self.user_enable: ['TRUE'] }
        dn_info = [(k, v) for (k, v) in dn_attr.items()]
        self.log.debug('Adding %s to %s ' % (dn_info, dn))
        result = self._create_object(dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result
                
    def get(self, first=None, last=None, unique=False):
        """Retrieve a user account; return user object."""
        if first is None and last is None:
            if unique:
                raise error.InputError('You must target a specific user in \
                order to search for a unique value')
            filter = '%s=*' % self.user_key # Return a list of all users
        else:
            self._gen_user_info(first, last)
            filter = '%s=%s' % (self.user_key, self.user_id)
        if unique: 
            trueorfalse = True
        else:
            trueorfalse = False
        msg = 'Searching at %s with scope %s and filter %s' % \
            (self.org_dn, self.search_scope, filter)
        self.log.debug(msg)
        result = self._get_object(self.org_dn, self.search_scope, \
                                  filter, unique=trueorfalse)
        self.log.debug('Result: %s' % result)
        return result
            
    def delete(self, first, last=None):
        """Delete a user account; return True."""
        self._gen_user_info(first, last)
        filter = '%s=%s' % (self.user_key, self.user_id)
        rdn = '%s=%s' % (self.user_key, self.user_id)
        container = '%s=%s' % (self.container_attr, self.user_container)
        dn = '%s,%s,%s' % (rdn, container, self.org_dn)
        self.log.debug('Deleting %s' % dn)
        result = self._delete_object(dn)
        self.log.debug('Result: %s' % result)
        return result
