"""SpokeMailingList module.

Classes:
SpokeMailingList - Creation/deletion/modification/retrieval of SpokeMailingList.
Exceptions:
NotFound - raised on failure to find an object when one is expected.
InputError - raised on invalid input.

ldap.MOD_DELETE = 1
ldap.MOD_ADD = 0
"""

# own modules
import spoke.lib.common as common
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.logger as logger

from directory import SpokeLDAP
from org import SpokeOrg

class SpokeMailingList(SpokeLDAP):
    
    """Provide CRUD methods to SpokeMailingList objects."""

    def __init__(self, org_name):
        """Get config, setup logging and LDAP connection."""
        SpokeLDAP.__init__(self)
        self.config = config.setup()
        self.log = logger.setup(__name__)
        self.base_dn = self.config.get('LDAP', 'basedn')
        self.search_scope = 2 #ldap.SCOPE_SUB
        self.org_name = org_name
        self.org = self._get_org(self.org_name)
        self.org_dn = self.org['data'][0].__getitem__(0)
        self.org_attrs = self.org['data'][0].__getitem__(1)
        self.org_classes = self.org_attrs['objectClass']
        self.container_attr = self.config.get('ATTR_MAP', 'container_attr', 'ou')
        self.list_container = self.config.get('ATTR_MAP', 'user_container', 'people')
        self.list_key = self.config.get('ATTR_MAP', 'user_key', 'uid')
        self.list_class = self.config.get('ATTR_MAP', 'smtp_class', 'aenetPostfix')
        self.list_address_attr = self.config.get('ATTR_MAP', 'smtp_address', 'aenetPostfixEmailAccept')
        self.list_destination_attr = self.config.get('ATTR_MAP', \
                                'smtp_destination', 'aenetPostfixEmailDeliver')
        self.list_enable_attr = self.config.get('ATTR_MAP', 'smtp_enable', 'aenetPostfixEnabled')
        self.list_pri_address_attr = self.config.get('ATTR_MAP', \
                                'smtp_pri_address', 'aenetPostfixEmailAddress')
        self.retrieve_attr = [self.list_address_attr]
    
    def _validate_input(self, list_address):
        """Ensure input is a valid."""
        list_address = common.validate_email_address(list_address)
        return list_address
        
    def _get_org(self, org_name):
        """Retrieve our org object."""
        org = SpokeOrg()
        result = org.get(org_name)
        if result['data'] == []:
            msg = "Can't find org %s" % org_name
            raise error.NotFound(msg)          
        return result

    def create(self, list_address, list_member):
        """Create mailing list; return mailing list info."""
        list_address = self._validate_input(list_address)
        list_member = self._validate_input(list_member)
        list_name, list_domain = list_address.split('@')
        filter = '%s=%s' % (self.list_address_attr, list_address) 
        self.log.debug('Creating mailing list %s in org: %s' % \
                      (list_address, self.org_name))  
       
        rdn = '%s=%s' % (self.list_key, list_name)
        container = '%s=%s' % (self.container_attr, self.list_container)
        dn = '%s,%s,%s' % (rdn, container, self.org_dn)
        dn_attr = { 'objectClass': ['top', 'inetOrgPerson', self.list_class],
                    'uid': [list_name], 'sn': [list_name], 'cn': [list_name],
                    self.list_pri_address_attr: [list_address],
                    self.list_enable_attr: ['TRUE'],
                    self.list_destination_attr: [list_member],
                    self.list_address_attr: [list_address]
                    }
        dn_info = [(k, v) for (k, v) in dn_attr.items()]
        result = self._create_object(dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result

    def get(self, list_address=None):
        """Find a mailing list; return mailing list info."""
        if list_address:
            list_address = self._validate_input(list_address)
            list_name, list_domain = list_address.split('@')
            filter = '%s=%s' % (self.list_address_attr, list_address)
            truefalse = True
        else:
            filter = '%s=*' % self.list_address_attr
            truefalse = False
        container = '%s=%s' % (self.container_attr, self.list_container)
        dn = '%s,%s' % (container, self.org_dn)
        result = self._get_object(dn, self.search_scope, filter, 
                                  unique=truefalse)
        self.log.debug('Result: %s' % result)
        return result
 
    def modify(self, list_address, enable):
        """Enable/Disable a mailing list; return True."""
        list_address = self._validate_input(list_address)
        list_info = self.get(list_address)
        if list_info['data'] == []:
            msg = 'Unable to modify mailing list access, no list found.'
            raise error.NotFound(msg)
        dn = list_info['data'][0].__getitem__(0)
        old_result = list_info['data'][0].__getitem__(1)
        old_attrs = {self.list_enable_attr: old_result[self.list_enable_attr]}
        if enable == True:
            new_attrs = {self.list_enable_attr: 'TRUE'}
        elif enable == False:
            new_attrs = {self.list_enable_attr: 'FALSE'}
        else:
            msg = 'enable can only be one of True or False'
            raise error.InputError(msg)
        result = self._modify_attributes(dn, new_attrs, old_attrs)
        self.log.debug('Result: %s' % result)
        return result
            
    def delete(self, list_address):
        """Delete a mailing list; return True."""
        list_address = self._validate_input(list_address)
        list_name, list_domain = list_address.split('@')        
        rdn = '%s=%s' % (self.list_key, list_name)
        container = '%s=%s' % (self.container_attr, self.list_container)
        dn = '%s,%s,%s' % (rdn, container, self.org_dn)
        self.log.info('Deleting mailing list: ' + dn)  
        result = self._delete_object(dn)
        self.log.debug('Result: %s' % result)
        return result
    
class SpokeMailingListMember(SpokeLDAP):
    
    """Provide CRUD methods to SpokeMailingListMember objects."""

    def __init__(self, org_name, list_address):
        """Get config, setup logging and LDAP connection."""
        SpokeLDAP.__init__(self)
        self.config = config.setup()
        self.log = logger.setup(self.__module__)
        self.base_dn = self.config.get('LDAP', 'basedn')
        self.search_scope = 0 #ldap.SCOPE_BASE
        self.org_name = org_name
        self.list_address = self._validate_input(list_address)
        self.list_name, self.list_domain = self.list_address.split('@')
        self.list = self._get_list(self.org_name, self.list_address)
        self.list_dn = self.list['data'][0].__getitem__(0)
        self.list_attrs = self.list['data'][0].__getitem__(1)
        self.list_classes = self.list_attrs['objectClass']
        
        self.list_key = self.config.get('ATTR_MAP', 'user_key', 'uid')
        self.list_class = self.config.get('ATTR_MAP', 'smtp_class', 'aenetPostfix')
        self.list_address_attr = self.config.get('ATTR_MAP', 'smtp_address', 'aenetPostfixEmailAccept')
        self.list_destination_attr = self.config.get('ATTR_MAP', \
                                'smtp_destination', 'aenetPostfixEmailDeliver')
        self.list_enable_attr = self.config.get('ATTR_MAP', 'smtp_enable', 'aenetPostfixEnabled')
        self.list_pri_address_attr = self.config.get('ATTR_MAP', \
                                'smtp_pri_address', 'aenetPostfixEmailAddress')
        self.retrieve_attr = [self.list_destination_attr]
        
    def _validate_input(self, list_address):
        """Ensure input is a valid."""
        list_address = common.validate_email_address(list_address)
        return list_address
    
    def _get_list(self, org_name, list_address):
        list = SpokeMailingList(org_name)
        result = list.get(list_address)
        if result['data'] == []:
            msg = "Can't find mailing list %s in %s" % (list_address, org_name)
            self.log.error(msg)
            raise error.NotFound(msg)          
        return result
    
    def create(self, member_address):
        """Create a mailing list member entry; return member info."""
        member_address = self._validate_input(member_address)
        dn = self.list_dn
        dn_info = [(0, self.list_destination_attr, member_address)]
        self.log.debug('Adding email member %s to %s list %s ' %
                           (member_address, self.org_name, self.list_name))
        result = self._create_object(dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result
        
    def get(self, member_address=None):
        """Find a mailing list member(s); return member result list."""
        dn = self.list_dn
        if member_address:
            member_address = self._validate_input(member_address)
            filter = '%s=%s' % (self.list_destination_attr, member_address)
        else:
            filter = '%s=*' % self.list_destination_attr
        result = self._get_object(dn, self.search_scope, filter, 
                                  attr=self.retrieve_attr)
        self.log.debug('Result: %s' % result)
        return result
        
    def delete(self, member_address):
        """Delete an email address."""
        member_address = self._validate_input(member_address)
        dn_info = [(1, self.list_destination_attr, 
                    member_address)]                    
        self.log.debug('Deleting email member %s to %s list %s ' %
                           (member_address, self.org_name, self.list_name))
        result = self._delete_object(self.list_dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result
        
