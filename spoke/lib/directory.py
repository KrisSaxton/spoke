"""Provides LDAP access and management.

Classes:
SpokeLDAP - extends ldap with several convenience classes.

Exceptions:
NotFound - raised on failure to find an object when one is expected.
AlreadyExists -raised on attempts to create an object when one already exists.
InputError - raised on invalid input.
ValidationError - raised when an action completes OK but validation fails.
SpokeError - raised when action fails for unknown reason.
SearchUniqueError - a unique search returned multiple results.
SaveTheBabies - raised on attempts to delete a child object when parent exists.
SpokeLDAPError - raised on errors during LDAP operations.

TODO - greater use of ValidationError instead of NotFound or AlreadyExists
"""
# core modules
import logging
import traceback

# own modules
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.common as common

# 3rd party modules
try:
    import ldap
    import ldap.modlist
except:
    msg = 'Failed to import ldap'
    raise error.SpokeLDAPError(msg)

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
        self.log = logging.getLogger(__name__)
        self.search_scope = ldap.SCOPE_SUBTREE #(2)
        self.server = self.config.get('LDAP', 'server')
        self.port = self.config.get('LDAP', 'port', '389')
        self.bind_dn = self.config.get('LDAP', 'binddn')
        self.start_tls = self.config.get('LDAP', 'start_tls', False)
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
        except ldap.LDAPError:
            trace = traceback.format_exc()
            msg = 'Failed to bind to LDAP server %s:%s as %s' % \
                (self.server,self.port, self.bind_dn)
            raise error.SpokeLDAPError(msg, trace)
        except Exception:
            trace = traceback.format_exc()
            msg = 'Unknown error'
            raise error.SpokeError(msg, trace)

class SpokeLDAP:
    
    """Extend ldap class with convenience methods."""
    
    def __init__(self):
        """Bind to LDAP directory; return an LDAP connection object."""
        self.config = config.setup()
        self.log = logging.getLogger(__name__)
        self.LDAP = setup().LDAP

    def _create_object(self, dn, dn_info):
        """Create a new LDAP object (e.g. a dn or attribute)."""
        # Allowed LDAP operations
        operation = {'add':self.LDAP.add_s, 'mod':self.LDAP.modify_s}
        try:
            int(dn_info[0][0]) #attribute mod opertations begin with an integer.
            type = 'mod'
            attrlist = [] # Collect a list of attributes to return
            for item in dn_info:
                attrlist.append(item[1])
        except:
            type = 'add' #if it's not a modification, it's an add operation.
            attrlist = None
        
        try:
            operation[type](dn, dn_info)
        except ldap.ALREADY_EXISTS:
            msg = 'Entry %s already exists.' % dn
            raise error.AlreadyExists(msg)
        except ldap.TYPE_OR_VALUE_EXISTS:
            msg = 'Attempt to add attribute to %s which already exists.' % dn
            raise error.AlreadyExists(msg)
        except ldap.CONSTRAINT_VIOLATION:
            msg = 'Attribute already exists and does not support multiples'
            raise error.AlreadyExists(msg)
        except ldap.NO_SUCH_OBJECT:
            msg = "Part of %s missing, can't create." % dn
            raise error.NotFound(msg)
        except ldap.LDAPError, e:
            trace = traceback.format_exc()
            raise error.SpokeLDAPError(e, trace)
        except Exception, e:
            trace = traceback.format_exc()
            msg = 'Unknown error'
            raise error.SpokeError(msg, trace)
        result = self._get_object(dn, scope=ldap.SCOPE_BASE, attr=attrlist)
        if result['exit_code'] == 0 and result['count'] == 1:
            result['msg'] = "Created %s:" % result['type']
            return result
        else:
            msg = 'Create operation returned OK, but unable to find object'
            raise error.NotFound(msg)
        
    def _get_object(self, dn, scope, filter=None, attr=None, unique=False):
        """Retrieve an LDAP object (e.g. a dn or attribute)."""
        if scope is None:
            scope = self.search_scope
        if filter is None:
            filter = '(objectClass=*)'
        #if attr is not None:
        #    attr = self.retrieve_attr 
        try:
            result = self.LDAP.search_s(dn, scope, filter, attr)
        except ldap.NO_SUCH_OBJECT, e:
            self.log.debug('Get failed; part of dn %s does not exist' % dn)
            result = [] # treat missing branch elements as missing leaf
        except ldap.LDAPError, e:
            trace = traceback.format_exc()
            raise error.SpokeLDAPError(e, trace)
        except Exception, e:
            trace = traceback.format_exc()
            msg = 'Unknown error'
            raise error.SpokeError(msg, trace)
        
        if unique != False and len(result) > 1:
            msg = 'Multiple results found yet uniqueness requested'
            raise error.SearchUniqueError(msg)
        result = self._process_results(result, __name__)
        return result

    def _modify_attributes(self, dn, new_attrs, old_attrs=None):
        """Modify an LDAP object (e.g. a dn or attribute)."""
        ignore_old = 0
        if old_attrs==None:
            old_object = self._get_object(dn, ldap.SCOPE_BASE,
                                        '(objectClass=*)', unique=True)
            if old_object['data'] == []:
                msg = '%s does not exist, cannot modify' % dn
                raise error.NotFound(msg)
            old_attrs = old_object['data'][0][1]
            ignore_old = 1
            
        dn_info = ldap.modlist.modifyModlist(old_attrs, new_attrs, 
                                             ignore_oldexistent=ignore_old)   
        try:
            self.LDAP.modify_s(dn, dn_info)
        except ldap.NO_SUCH_ATTRIBUTE, e:
            msg = 'Attribute does not exist, cannot modify'
            raise error.NotFound(msg)
        except ldap.LDAPError, e:
            trace = traceback.format_exc()
            raise error.SpokeLDAPError(e, trace)
        except Exception, e:
            trace = traceback.format_exc()
            msg = 'Unknown error'
            raise error.SpokeError(msg, trace)
        attrs = []
        for attr in new_attrs:
            attrs.append(attr)
        result = self._get_object(dn, scope=ldap.SCOPE_BASE, 
                                  attr=attrs, unique=True)
        result['msg'] = "Modified %s attribute:" % result['type']
        return result

    def _delete_object(self, dn, dn_info=None):
        """Delete an LDAP object (e.g. a dn or attribute)."""
        operation = {'del_dn':self.LDAP.delete_s,
                     'del_attr':self.LDAP.modify_s}
        filter = 'objectClass=*'
        if dn_info == None:
            del_type = 'del_dn' # We're deleting a dn
            kargs = {'dn':dn}
            attrlist = None
        else:
            del_type = 'del_attr' # We're deleting an attribute
            kargs = {'dn': dn, 'modlist': dn_info}
            attrlist = [] # Collect a list of attributes to return
            for item in dn_info:
                attrlist.append(item[1])
            #if len(dn_info) == 1: # Try and construct a filter
            #    filter = '%s=%s' % (dn_info[0][1], dn_info[0][2])
        #self.log.debug('Running with filter %s' % filter)
        try:
            operation[del_type](**kargs)
        except ldap.NO_SUCH_OBJECT, e:
            msg = '%s does not exist, cannot delete' % dn
            raise error.NotFound(msg)
        except ldap.NO_SUCH_ATTRIBUTE, e:
            msg = 'Attribute does not exist, cannot delete'
            raise error.NotFound(msg)
        except ldap.NOT_ALLOWED_ON_NONLEAF, e:
            msg = '%s still has children, can\'t delete' % dn
            raise error.SaveTheBabies(msg)
        except ldap.LDAPError, e:
            trace = traceback.format_exc()
            raise error.SpokeLDAPError(e, trace)
        except Exception, e:
            trace = traceback.format_exc()
            msg = 'Unknown error'
            raise error.SpokeError(msg, trace)
        result = self._get_object(dn, scope=ldap.SCOPE_BASE, filter=filter, 
                                  attr=attrlist)
        if del_type == 'del_dn': # we expect nothing back
            if result['exit_code'] == 3 and result['count'] == 0:
                result['msg'] = "Deleted %s:" % result['type']
                return result
            else:
                msg = 'Delete operation returned OK, but object still there?'
                raise error.ValidationError(msg)
        else: # we're deleting an attribute so we expect an object back
            if result['exit_code'] == 0 and result['count'] == 1:
                result['msg'] = "Deleted %s attribute:" % result['type']
                return result
            else:
                msg = 'Delete attribute operation returned OK, but unable to find object'
                raise error.NotFound(msg)

    def _validate_exists(self, dn, filter=None, unique=False, attr=None):
        """Return result under supplied dn; otherwise raise NotFound."""
        try:
            result = self._get_object(dn, self.search_scope, filter, attr)
        except ldap.NO_SUCH_OBJECT, e:
            result = []
        if not result:
            msg = 'Validate exists failed'
            raise error.NotFound(msg)
        elif unique != False and len(result) > 1:
            msg = 'Multiple results found yet uniqueness requested'
            raise error.SearchUniqueError(msg)
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
            raise error.AlreadyExists(msg)
        return True
    
    def _process_results(self, data, name=None):
        '''Take result data; return full result object.'''
        result = {}
        result['data'] = data
        if not name:
            thing = 'object'
        else:
            thing = common.is_shell_safe(name)
        result['type'] = name
        count = len(data)
        result['count'] = count 
        if count == 0:
            result['exit_code'] = 3    
            result['msg'] = 'No ' + thing + '(s) found'
        else:
            result['exit_code'] = 0
            if count == 1:
                result['msg'] = "Found %s:" % thing
            else:
                result['msg'] = 'Found ' + str(count) + ' ' + thing + 's:'
        return result
