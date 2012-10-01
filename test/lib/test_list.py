"""Tests Spoke list.py module"""
# core modules
import unittest
# own modules
import spoke.lib.error as error
import spoke.lib.config as config
from spoke.lib.org import SpokeOrg
from spoke.lib.list import SpokeMailingList
from spoke.lib.list import SpokeMailingListMember

class TestSpokeMailingList(unittest.TestCase):
    
    """A class for testing the Spoke list.py module."""
    
    def __init__(self, methodName):
        """Setup config data and LDAP connection."""
        unittest.TestCase.__init__(self, methodName)
        common_config = '../../contrib/spoke.conf'
        custom_config = '/tmp/spoke.conf'
        config_files = (common_config, custom_config)
        self.config = config.setup(config_files)
        self.base_dn = self.config.get('LDAP', 'basedn')
        self.search_scope = 2 # ldap.SCOPE_SUBTREE
        self.retrieve_attr = None
        self.org_name = 'SpokeListTest'
        self.org_attr = self.config.get('ATTR_MAP', 'org_attr')
        self.org_def_children = self.config.get('ATTR_MAP', 'org_def_children')
        self.org_children = self.org_def_children.split(',')
        self.container_attr = self.config.get('ATTR_MAP', 'container_attr')
        self.list_container = self.config.get('ATTR_MAP', 'user_container')
        self.list_class = self.config.get('ATTR_MAP', 'smtp_class')
        self.list_key = self.config.get('ATTR_MAP', 'user_key')
        self.list_address_attr = self.config.get('ATTR_MAP', 'smtp_address')
        self.list_destination_attr = self.config.get('ATTR_MAP', 'smtp_destination')
        self.list_enable_attr = self.config.get('ATTR_MAP', 'smtp_enable')
        self.list_pri_address_attr = self.config.get('ATTR_MAP', 'smtp_pri_address')
        self.list_address = 'testlist@testdomain.loc'
        self.list_member = 'testmember@testdomain.loc'
        
    def setUp(self):
        org = SpokeOrg()
        org.create(self.org_name)
        list = SpokeMailingList(self.org_name)
        list.create(self.list_address, self.list_member)
        
    def tearDown(self):
        list = SpokeMailingList(self.org_name)
        list.delete(self.list_address)
        org = SpokeOrg()
        org.delete(self.org_name)

# Mailing List tests.
  
    def test_create_mailing_list(self):
        """Create a mailing list; return results object."""
        list_name = 'testcreatelist'
        list_domain = 'testdomain.loc'
        list_address = list_name + '@' + list_domain
        list_member = 'testcreatemember' + '@' + list_domain
        list = SpokeMailingList(self.org_name)
        result = list.create(list_address, list_member)['data']
        
        rdn = '%s=%s' % (self.list_key, list_name)
        container = '%s=%s' % (self.container_attr, self.list_container)
        base_dn = '%s,%s=%s,%s' % (container, self.org_attr,
                                   self.org_name, self.base_dn)
        dn = '%s,%s' % (rdn, base_dn)
        dn_info = {'objectClass': ['top', 'inetOrgPerson', self.list_class],
                    self.list_key: [list_name],
                    'sn': [list_name], 'cn': [list_name],
                    self.list_pri_address_attr: [list_address],
                    self.list_enable_attr: ['TRUE'],
                    self.list_destination_attr: [list_member],
                    self.list_address_attr: [list_address]
                   }
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        list.delete(list_address)
        
    def test_create_mailing_list_twice(self):
        """Create a mailling list twice; raise AlreadyExists."""
        list = SpokeMailingList(self.org_name)
        self.assertRaises(error.AlreadyExists, list.create, self.list_address,
                            self.list_member)
        
    def test_create_mailing_list_missing_org(self):
        """Create a mailing list in a missing org; raise NotFound."""
        org_name = 'TestMissingOrg'
        self.assertRaises(error.NotFound, SpokeMailingList, org_name)
        
    def test_create_invalid_mailing_list(self):
        """Create a mailing list with invalid name; raise InputError."""
        list_address = 'testnodomain@'
        list_member = 'test@validdomain.loc'
        list = SpokeMailingList(self.org_name)
        self.assertRaises(error.InputError, list.create,
                            list_address, list_member)
        
    def test_get_mailing_list(self):
        """Retrieve a mailing list; return results object."""
        list = SpokeMailingList(self.org_name)
        result = list.get(self.list_address)['data']
        list_name, list_domain = self.list_address.split('@')
        rdn = '%s=%s' % (self.list_key, list_name)
        container = '%s=%s' % (self.container_attr, self.list_container)
        base_dn = '%s,%s=%s,%s' % (container, self.org_attr,
                                   self.org_name, self.base_dn)
        dn = '%s,%s' % (rdn, base_dn)
        dn_info = {'objectClass': ['top', 'inetOrgPerson', self.list_class],
                    self.list_key: [list_name],
                    'sn': [list_name], 'cn': [list_name],
                    self.list_pri_address_attr: [self.list_address],
                    self.list_enable_attr: ['TRUE'],
                    self.list_destination_attr: [self.list_member],
                    self.list_address_attr: [self.list_address]
                   }
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        
    def test_get_all_mailing_lists(self):
        """Retrieve all mailing lists; return results object."""      
        expected_result = []
        list_address2 = 'testlist2@testdomain.loc'
        list_member2 = 'testmember2@testdomain.loc' 
        for u in ((self.list_address, self.list_member), 
                  (list_address2, list_member2)):
            list_address = u[0]
            list_member = u[1]
            list_name, list_domain = list_address.split('@')
            rdn = '%s=%s' % (self.list_key, list_name)
            container = '%s=%s' % (self.container_attr, self.list_container)
            base_dn = '%s,%s=%s,%s' % (container, self.org_attr,
                                   self.org_name, self.base_dn)
            dn = '%s,%s' % (rdn, base_dn)
            dn_info = {'objectClass': ['top', 'inetOrgPerson', 
                                       self.list_class],
                    self.list_key: [list_name],
                    'sn': [list_name], 'cn': [list_name],
                    self.list_pri_address_attr: [list_address],
                    self.list_enable_attr: ['TRUE'],
                    self.list_destination_attr: [list_member],
                    self.list_address_attr: [list_address]
                   }
            append_this = (dn, dn_info)
            expected_result.append(append_this)
        list = SpokeMailingList(self.org_name)
        list.create(list_address2, list_member2)
        result = list.get()['data']
        self.assertEqual(result, expected_result)
        list.delete(list_address2)
        
    def test_get_missing_mailing_list(self):
        """Retrieve missing mailing list; return empty list."""
        list_address = 'testmissing@testdomain.loc'
        list = SpokeMailingList(self.org_name)
        self.assertFalse(list.get(list_address)['data'])
        
    def test_disable_mailing_list(self):
        """Disable mailing list; verify mailing list disabled."""
        list_name, list_domain = self.list_address.split('@')
        list = SpokeMailingList(self.org_name)
        rdn = '%s=%s' % (self.list_key, list_name)
        container = '%s=%s' % (self.container_attr, self.list_container)
        base_dn = '%s,%s=%s,%s' % (container, self.org_attr,
                                   self.org_name, self.base_dn)
        dn = '%s,%s' % (rdn, base_dn)
        dn_info = {self.list_enable_attr: ['FALSE']}
        expected_result = [(dn, dn_info)]
        result = list.modify(self.list_address, enable=False)['data']
        self.assertEqual(result, expected_result)
        
    def test_delete_mailing_list(self):
        """Delete a mailing list; return True."""
        list_address = 'testdelete@acme.loc'
        list_member = 'testmember@acme.loc'
        list = SpokeMailingList(self.org_name)
        list.create(list_address, list_member)
        self.assertTrue(list.delete(list_address))
        
    def test_delete_missing_mailing_list(self):
        """Delete a non existent mailing list; raise NotFound."""
        list_address = 'testmissing@testdomain.loc'
        list = SpokeMailingList(self.org_name)
        self.assertRaises(error.NotFound, list.delete, list_address)
        
# Mailing List member tests

    def test_create_mailing_list_member(self):
        """Create mailing list member; return True."""
        member_address = 'testcreatemember@testdomain.loc'
        member = SpokeMailingListMember(self.org_name, self.list_address)
        result = member.create(member_address)['data']
        
        list_name, list_domain = self.list_address.split('@')
        rdn = '%s=%s' % (self.list_key, list_name)
        container = '%s=%s' % (self.container_attr, self.list_container)
        base_dn = '%s,%s=%s,%s' % (container, self.org_attr,
                                   self.org_name, self.base_dn)
        dn = '%s,%s' % (rdn, base_dn)
        dn_info = {
                   self.list_destination_attr:[self.list_member,member_address]
                   }
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
    
    def test_create_mailing_list_member_twice(self):
        """Create mailing list member twice; raise AlreadyExists."""
        member_address = self.list_member
        member = SpokeMailingListMember(self.org_name, self.list_address)
        self.assertRaises(error.AlreadyExists, member.create, member_address)
    
    def test_create_mailing_list_member_missing_mailing_list(self):
        """Create mailing list member in list; raise NotFound."""
        list_address = 'missinglist@testdomain.loc'
        self.assertRaises(error.NotFound, SpokeMailingListMember,
                          self.org_name, list_address)
    
    def test_create_invalid_mailing_list_member(self):
        """Create invalid mailing list member; raise InputError."""
        member_address = 'invalidmember@'
        member = SpokeMailingListMember(self.org_name, self.list_address)
        self.assertRaises(error.InputError, member.create, member_address)

    def test_get_mailing_list_member(self):
        """Retrieve mailing list member; retrieve list member object."""
        member = SpokeMailingListMember(self.org_name, self.list_address)
        result = member.get(self.list_member)['data']
        
        list_name, list_domain = self.list_address.split('@')
        rdn = '%s=%s' % (self.list_key, list_name)
        container = '%s=%s' % (self.container_attr, self.list_container)
        base_dn = '%s,%s=%s,%s' % (container, self.org_attr,
                                   self.org_name, self.base_dn)
        dn = '%s,%s' % (rdn, base_dn)
        dn_info = {self.list_destination_attr:[self.list_member]}
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
    
    def test_get_all_mailing_list_members(self):
        """Retrieve all list members; retrieve list of member objects."""
        member_address = 'testcreatemember@testdomain.loc'
        member = SpokeMailingListMember(self.org_name, self.list_address)
        member.create(member_address)
        result = member.get(member_address)['data']
        
        list_name, list_domain = self.list_address.split('@')
        rdn = '%s=%s' % (self.list_key, list_name)
        container = '%s=%s' % (self.container_attr, self.list_container)
        base_dn = '%s,%s=%s,%s' % (container, self.org_attr,
                                   self.org_name, self.base_dn)
        dn = '%s,%s' % (rdn, base_dn)
        dn_info = {
                   self.list_destination_attr:[self.list_member,member_address]
                   }
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
    
    def test_get_missing_mailing_list_member(self):
        """Retrieve missing mailing list member; return empty list."""
        member_address = 'missingaddress@testdomain.loc'
        member = SpokeMailingListMember(self.org_name, self.list_address)
        self.assertFalse(member.get(member_address)['data'])
        
    def test_delete_mailing_list_member(self):
        """Delete mailing list member; return True."""
        member_address = 'testdeletemember@testdomain.loc'
        member = SpokeMailingListMember(self.org_name, self.list_address)
        member.create(member_address)
        self.assertTrue(member.delete(member_address))
    
    def test_delete_missing_mailing_list_member(self):
        """Delete missing mailing list member; raise NotFound."""
        member_address = 'testdeletemissing@testdomain.loc'
        member = SpokeMailingListMember(self.org_name, self.list_address)
        self.assertRaises(error.NotFound, member.delete, member_address)
        
    
if __name__ == '__main__':
    unittest.main()
