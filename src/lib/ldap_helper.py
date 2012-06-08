"""Provides LDAP access and management.

Classes:
SpokeLDAP - extends ldap with several convenience classes.

Exceptions:
NotFound - raised on failure to find an object when one is expected.
AlreadyExists -raised on attempts to create an object when one already exists.
InputError - raised on invalid input.
ConfigError - raised on invalid configuration data.
SaveTheBabies - raised on attempted child removal where parent still exists.
SpokeError - raised when action fails for unknown reason.
SearchUniqueError - a unique search returned multiple results.
"""

import ldap
import ldap.modlist

import error
import config
import logger

hLDAP = None

def setup():
    """Instantiate (once only) and return LDAP connection object"""
    global hLDAP
    if hLDAP is not None:
        pass
    else:
        hLDAP = SpokeLDAPConn()  
    return hLDAP

class SpokeLDAPConn:
    
    """Extend ldap class with convenience methods."""
    
    def __init__(self):
        """Bind to LDAP directory, return an ldap object."""
        self.config = config.setup()
        self.log = logger.setup(self.__module__)
        self.search_scope = 2 # ldap.SCOPE_SUBTREE
        self.server = self.config.get('LDAP', 'server')
        try:
            self.port = self.config.get('LDAP', 'port')
        except:
            self.port = '389'
        self.bind_dn = self.config.get('LDAP', 'binddn')
        try:
            self.start_tls = self.config.get('LDAP', 'start_tls')
        except:
            self.start_tls = False
        self.bind_password = self.config.get('LDAP', 'bindpw')
        try:
            self.LDAP = ldap.initialize('ldap://%s:%s' %
                                         (self.server, self.port))
            self.LDAP.protocol_version = 3 #ldap.VERSION3
            if self.start_tls:
                self.LDAP.start_tls_s()
            self.LDAP.simple_bind_s(self.bind_dn, self.bind_password)
            self.log.debug('Bound to LDAP server %s:%s as %s' % 
                           (self.server, self.port, self.bind_dn))
        except ldap.SERVER_DOWN, e:
            msg = e.message.get('desc')
            self.log.error(msg)
            raise error.SpokeError(msg)
        except ldap.CONFIDENTIALITY_REQUIRED, e:
            msg = '''Server is insisting on greater security,
 try adding 'start_tls' or 'with_ssl' to your spoke.conf'''
            self.log.error(msg)
            raise error.ConfigError(msg)
        except ldap.LDAPError, e:
            self.log.error('Failed to bind to LDAP server %s:%s as %s' %
                           (self.server, self.port, self.bind_dn))
            self.log.error(e)
            raise e

class SpokeLDAP:
    
    """Extend ldap class with convenience methods."""
    
    def __init__(self):
        """Parse configuration, setup logging; 
        bind to LDAP directory and return an LDAP connection object."""
        self.config = config.setup()
        self.log = logger.setup(self.__module__)
        self.LDAP = setup().LDAP     

    def search_uniq(self, base_dn, search_scope, search_filter, retrieve_attr):
        """Extend basic ldap search. Return None if object requested not found,
        result if unique result found and throw SearchUniqueError exception
        if multiple results found."""
        
        result = self.LDAP.search_s(base_dn, search_scope, search_filter,
                                    retrieve_attr)
        if not result:
            self.log.debug('No results found for filter: %s at base: %s with \
scope: %s' % (search_filter, base_dn, search_scope))
        elif len(result) > 1:
            self.log.error('Multiple results found yet uniqueness requested')
            for r in result:
                self.log.debug('Found: ' + r[0])
            raise error.SearchUniqueError('Multiple results returned')
        elif len(result) == 1:
            self.log.debug('Found: ' + result[0][0])
            return result
        return result

    def _create_object(self, dn, dn_info):
        """Create a new LDAP object (e.g. a dn or attribute)."""
        # Allowed LDAP operations
        operation = {'add':self.LDAP.add_s, 'mod':self.LDAP.modify_s}
        try:
            # attribute modification entries begin with an operation integer.
            int(dn_info[0][0])
            type = 'mod'
        except:
            # if it's not a modification, it's an add operation.
            type = 'add'
        try:
            self.log.debug('Performing %s of %s at %s' % (type, dn_info, dn))
            operation[type](dn, dn_info)
        except ldap.ALREADY_EXISTS:
            msg = 'Entry %s already exists.' % dn
            self.log.warn(msg)
            raise error.AlreadyExists(msg)
        except  ldap.TYPE_OR_VALUE_EXISTS:
            msg = 'Attempt to add attribute to %s which already exists.' % dn
            self.log.warn(msg)
            raise error.AlreadyExists(msg)
        except ldap.NO_SUCH_OBJECT:
            msg = "Part of %s missing, can't create." % dn
            self.log.error(msg)
            raise error.NotFound(msg)
        except ldap.LDAPError, e:
            self.log.error('LDAP Error %s' % e)
            raise e
        return True
        
    def _get_object(self, dn, scope, filter=None,
                   attr=None, attrs_only=0, unique=False):
        """Retrieve an LDAP object (e.g. a dn or attribute)."""
        if scope is None:
            scope = self.search_scope
        if filter is None:
            filter = '(objectClass=*)'
        #if attr is None:
        #    attr = self.retrieve_attr     
        try:
            self.log.debug('Searching under dn %s with scope %s, filter %s, \
returning attributes %s' % (dn, scope, filter, attr))
            result = self.LDAP.search_s(dn, scope, filter, attr)
        except ldap.NO_SUCH_OBJECT, e:
            self.log.debug('Get failed; part of dn %s does not exist' % dn)
            result = [] # treat missing branch elements as missing leaf.
        except ldap.LDAPError, e:
            self.log.debug(e)
            raise e
        if not result:
            self.log.debug('No results found for filter: %s at base: %s with \
scope: %s' % (filter, dn, scope))
        elif unique != False and len(result) > 1:
            self.log.error('Multiple results found yet uniqueness requested')
            for r in result:
                self.log.debug('Found: ' + r[0])
            raise error.SearchUniqueError('Multiple results returned')
        elif len(result) == 1:
            self.log.debug('Found: ' + result[0][0])
            return result
        return result
    
    def _delete_object(self, dn, dn_info=None):
        """Delete an LDAP object (e.g. a dn or attribute)."""
        operation = {'del_dn':self.LDAP.delete_s,
                     'del_attr':self.LDAP.modify_s}
        if dn_info == None:
            type = 'del_dn' # We're deleting a dn
            kargs = {'dn':dn}
        else:
            type = 'del_attr' # We're deleting an attribute
            kargs = {'dn': dn, 'modlist': dn_info}         
        try:
            operation[type](**kargs)
        except ldap.NO_SUCH_OBJECT, e:
            msg = '%s does not exist, cannot delete' % dn
            self.log.warn(msg)
            self.log.debug(e)
            raise error.NotFound(msg)
        except ldap.NO_SUCH_ATTRIBUTE, e:
            msg = 'Attribute does not exist, cannot delete'
            self.log.warn(msg)
            self.log.debug(e)
            raise error.NotFound(msg)
        except ldap.NOT_ALLOWED_ON_NONLEAF, e:
            msg = '%s still has children, can\'t delete' % dn
            self.log.error(msg)
            raise error.SaveTheBabies(msg)
        except ldap.LDAPError, e:
            self.log.error('LDAP Error %s' % e)
            raise e
        
    def _modify_attributes(self, dn, new_attrs, old_attrs=None):
        """Modify an LDAP object (e.g. a dn or attribute)."""
        if old_attrs==None:
            old_attrs = {}
        self.log.debug('Using old_attrs %s' % old_attrs)
        self.log.debug('Using new_attrs %s' % new_attrs)
        dn_info = ldap.modlist.modifyModlist(old_attrs, new_attrs)       
        try:
            self.log.debug('Modifying dn %s with %s' % (dn, dn_info))
            self.LDAP.modify_s(dn, dn_info)
        except ldap.NO_SUCH_OBJECT, e:
            msg = '%s does not exist, cannot modify' % dn
            self.log.warn(msg)
            self.log.debug(e)
            raise error.NotFound(msg)
        except ldap.NO_SUCH_ATTRIBUTE, e:
            msg = 'Attribute does not exist, cannot modify'
            self.log.warn(msg)
            raise error.NotFound(msg)
        except ldap.LDAPError, e:
            self.log.error('LDAP Error %s' % e)
            raise e

    def _validate_exists(self, dn, filter=None, unique=False, attr=None):
        """Return result under supplied dn; otherwise raise NotFound."""
        try:
            result = self._get_object(dn, self.search_scope, filter, attr)
        except ldap.NO_SUCH_OBJECT, e:
            result = []
        if not result:
            self.log.debug('Validation failed')
            raise error.NotFound('Object not found')
        elif unique != False and len(result) > 1:
            self.log.error('Multiple results found yet uniqueness requested')
            for r in result:
                self.log.debug('Found: ' + r[0])
            raise error.SearchUniqueError('Multiple results returned')
        #return result
        return True
        
    def _validate_missing(self, dn, filter=None):
        """Return true if not found; otherwise raise AlreadyExists.
        TODO add global option to replace _get_global."""
        try:
            result = self._get_object(dn, self.search_scope, filter)
        except ldap.NO_SUCH_OBJECT, e:
            return True
        if result != []:
            msg = 'Entry found, validate missing failed.'
            self.log.debug(msg)
            raise error.AlreadyExists(result)
        return True
