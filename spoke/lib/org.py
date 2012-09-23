"""LDAP container management module.

Classes:
SpokeOrg - Create/Get/Modify/Delete LDAP organisation containers.
SpokeOrgChild - Create/Get/Modify/Delete LDAP organisation child containers.

Exceptions:
NotFound - raised when an operation fails to find an expected object.
"""

# own modules
import error
import config
import logger
from directory import SpokeLDAP

class SpokeOrg(SpokeLDAP):
    
    """Provide CRUD methods to LDAP organisation objects."""
    
    def __init__(self):
        """Get config, setup logging and LDAP connection."""
        SpokeLDAP.__init__(self)
        self.config = config.setup()
        self.log = logger.setup(__name__)
        self.search_scope = 2 # ldap.SCOPE_SUBTREE
        self.retrieve_attr = None
        self.base_dn = self.config.get('LDAP', 'basedn')
        self.org_class = self.config.get('ATTR_MAP', 'org_class', 'organization')
        self.user_class = self.config.get('ATTR_MAP', 'user_class', 'aenetAccount')
        self.org_attr = self.config.get('ATTR_MAP', 'org_attr', 'o')
        self.container_attr = self.config.get('ATTR_MAP', 'container_attr', 'ou')
        self.container_class = self.config.get('ATTR_MAP', \
                                        'container_class', 'organizationalUnit')
        self.org_def_children = self.config.get('ATTR_MAP', \
                                'org_def_children', 'people,groups,dns,hosts')
        self.org_children = self.org_def_children.split(',')
        self.org_suffix_attr = self.config.get('ATTR_MAP', 'org_suffix', 'aenetAccountSuffix')
            
    def create(self, org_name, org_children=None, suffix=None):
        """Create organisation (+containers); return organisation object."""
        dn = self.org_attr + '=' + org_name + ',' + self.base_dn
        if org_children is None:
            org_children = self.org_children
        if suffix is None:
            dn_attr = {'objectClass': ['top', self.org_class],
                       self.org_attr: [org_name]}
        else:
            dn_attr = {'objectClass': ['top', self.org_class, self.user_class],
                       self.org_attr: [org_name],
                       self.org_suffix_attr: [suffix]}
        dn_info = [(k, v) for (k, v) in dn_attr.items()] 
        msg = 'Creating %s with attributes %s' % (dn, dn_info)
        self.log.debug(msg)
        result = self._create_object(dn, dn_info)         
        # Add any children
        for child_name in org_children:
            child = SpokeOrgChild(org_name)
            child.create(child_name)
        filter = '%s=%s' % (self.org_attr, org_name)
        self.log.debug('Result: %s' % result)
        return result
    
    def get(self, org_name=None):
        """Find an Organisation; return result(s) list."""      
        if org_name is None: # Return a list of all orgs
            filter = '%s=*' % self.org_attr
            scope = 1
            trueorfalse = False
        else:
            filter = '%s=%s' % (self.org_attr, org_name)
            scope = self.search_scope
            trueorfalse = True           
        result = self._get_object(self.base_dn, scope, filter, \
                                  unique=trueorfalse)
        self.log.debug('Result: %s' % result)
        return result
    
    def modify(self, org_name, suffix):
        """Modify an org's default suffix; return True."""
        org_info = self.get(org_name)['data']
        if org_info == []:
            msg = 'Unable to modify org suffix, no org found.'
            self.log.error(msg)
            raise error.NotFound(msg)
        dn = org_info[0].__getitem__(0)
        old_result = org_info[0].__getitem__(1)
        old_classes = old_result['objectClass']
        
        try:
            old_attrs = {self.org_suffix_attr:old_result[self.org_suffix_attr]}    
        except KeyError: # suffix has not been set.
            old_attrs = {self.org_suffix_attr: ''}
            #new_attrs = {'objectClass': [self.user_class] }
                         #self.org_suffix_attr: suffix}
        new_attrs = {self.org_suffix_attr: suffix}
        if not self.user_class in old_classes:
            new_attrs['objectClass'] = self.user_class
        if new_attrs == old_attrs:
            msg = 'New suffix is equal to old suffix, nothing to update.'
            self.log.debug(msg)
            return True
        self._modify_attributes(dn, new_attrs, old_attrs)
        
    def delete(self, org_name, org_children=None):
        """Delete an organisation; return True."""
        if org_children is None:
            org_children = self.org_children
        # First delete any children
        for child_name in org_children:
            child = SpokeOrgChild(org_name)
            try:
                child.delete(child_name)
            except error.NotFound:
                pass          
        # Now delete the parent org
        dn = self.org_attr + '=' + org_name + ',' + self.base_dn
        msg = 'Deleting %s' % dn
        self.log.debug(msg)
        result = self._delete_object(dn)
        self.log.debug('Result: %s' % result)
        return result
    
class SpokeOrgChild(SpokeLDAP):
    
    """Provide CRUD methods to LDAP organisation child container objects."""
    
    def __init__(self, org_name):
        """Get config, setup logging and LDAP connection."""
        SpokeLDAP.__init__(self)
        self.config = config.setup()
        self.log = logger.setup(__name__)
        self.search_scope = 2 # ldap.SCOPE_SUBTREE
        self.retrieve_attr = None
        self.base_dn = self.config.get('LDAP', 'basedn')
        self.org_name = org_name
        self.org = self._get_org(self.org_name)
        if self.org['data'] == []:
            msg = 'Org %s not found: cannot delete children' % self.org_name
            raise error.NotFound(msg)
        self.org_dn = self.org['data'][0].__getitem__(0)
        self.container_attr = self.config.get('ATTR_MAP', 'container_attr', 'ou')
        self.container_class = self.config.get('ATTR_MAP', \
                                        'container_class', 'organizationalUnit')
            
    def _get_org(self, org_name):
        """Retrieve our org object."""
        org = SpokeOrg()
        result = org.get(org_name)
        if result == []:
            msg = "Can't find org %s" % org_name
            self.log.error(msg)
            raise error.NotFound(msg)          
        return result

    def create(self, child_name):
        org_dn = self.org_dn
        dn = self.container_attr + '=' + child_name + ',' + org_dn
        dn_attr = { 'objectClass': ['top', self.container_class],
                       self.container_attr: [child_name] }
        dn_info = [(k, v) for (k, v) in dn_attr.items()]
        msg = 'Creating %s with attributes %s' % (dn, dn_info)
        self.log.debug(msg)
        result = self._create_object(dn, dn_info)
        filter = '%s=%s' % (self.container_attr, child_name)
        self.log.debug('Result: %s' % result)
        return result
    
    def get(self, child_name=None):
        """Fetch an org's children; return a list of child containers."""
        dn = self.org_dn
        if child_name is None:
            filter = 'objectClass=%s' % self.container_class
            msg = 'Searching for children of org %s' % self.org_name
        else:
            filter = self.container_attr + '=' + child_name
        search_scope = 1 #scope one level
        msg = 'Searching at %s with scope %s and filter %s' % \
            (dn, search_scope, filter)
        self.log.debug(msg)
        result = self._get_object(dn, search_scope, filter)
        self.log.debug('Result: %s' % result)
        return result
    
    def delete(self, child_name):
        org_dn = self.org_dn
        dn = self.container_attr + '=' + child_name + ',' + org_dn
        msg = 'Deleting %s' % dn
        self.log.debug(msg)
        result = self._delete_object(dn)
        self.log.debug('Result: %s' % result)
        return result