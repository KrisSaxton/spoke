"""Tests Spoke org.py module."""
# core modules
import unittest
# own modules
import spoke.lib.error as error
import spoke.lib.config as config
from spoke.lib.org import SpokeOrg
from spoke.lib.org import SpokeOrgChild

class SpokeOrgTest(unittest.TestCase):
    
    """A class for testing the Spoke org.py module."""
    
    def __init__(self, methodName):
        """Setup config data and LDAP connection."""
        unittest.TestCase.__init__(self, methodName)
        common_config = '../../contrib/spoke.conf'
        custom_config = '/tmp/spoke.conf'
        config_files = (common_config, custom_config)
        self.config = config.setup(config_files)
        self.org_name = 'SpokeOrgTest'
        self.org_suffix_name = 'spokeorg.com'
        self.base_dn = self.config.get('LDAP', 'basedn')
        self.search_scope = 1 # ldap.ONELEVEL
        self.retrieve_attr = None
        self.org_class = self.config.get('ATTR_MAP', 'org_class')
        self.user_class = self.config.get('ATTR_MAP', 'user_class')
        self.org_attr = self.config.get('ATTR_MAP', 'org_attr')   
        self.org_def_children = self.config.get('ATTR_MAP', 'org_def_children')
        self.org_children = self.org_def_children.split(',')
        self.org_suffix_attr = self.config.get('ATTR_MAP', 'org_suffix')
        self.container_class = self.config.get('ATTR_MAP', 'container_class')
        self.container_attr = self.config.get('ATTR_MAP', 'container_attr')
            
    def setUp(self):
        org = SpokeOrg()
        org.create(self.org_name, self.org_children)

    def tearDown(self):
        org = SpokeOrg()
        org.delete(self.org_name, self.org_children) 

# Org tests

    def test_spoke_org_create(self):
        """Create an org with default children; return True."""
        org_name = 'testSpokeOrgCreate'
        base_dn = self.base_dn
        org = SpokeOrg()
        dn = 'o=%s,%s' % (org_name, base_dn)
        dn_info = {'objectClass': ['top', self.org_class], 
                   self.org_attr: [org_name]}
        expected_result = [(dn, dn_info)]
        self.assertTrue(org.create(org_name))
        result = org.get(org_name)['data']
        self.assertEqual(result, expected_result)
        
        for child_name in self.org_children:
            child = SpokeOrgChild(org_name)
            rdn = self.container_attr + '=' + child_name
            organisation = self.org_attr + '=' + org_name
            dn = rdn + ',' + organisation + ',' + self.base_dn
            dn_info = {'objectClass': ['top', self.container_class],
                       self.container_attr: [child_name]}
            expected_result = [(dn, dn_info)]
            result = child.get(child_name)['data']
            self.assertEqual(result, expected_result)        
        org.delete(org_name)

    def test_spoke_org_suffix_create(self):
        """Create an org with specific suffix; return True."""
        org_name = 'testSpokeOrgCreate'
        base_dn = self.base_dn
        org = SpokeOrg()
        dn = 'o=%s,%s' % (org_name, base_dn)
        dn_info = {'objectClass': ['top', self.org_class, self.user_class], 
                   self.org_attr: [org_name],
                   self.org_suffix_attr: [self.org_suffix_name]}
        expected_result = [(dn, dn_info)]
        
        self.assertTrue(org.create(org_name, suffix=self.org_suffix_name))
        result = org.get(org_name)['data']
        self.assertEqual(result, expected_result)        
        org.delete(org_name, self.org_children)
        
    def test_create_org_twice(self):
        """Create an org twice; raise AlreadyExists."""
        org = SpokeOrg()
        self.assertRaises(error.AlreadyExists, org.create, self.org_name)
        
    def test_spoke_org_get(self):
        """Retrieve an org; return an org object."""
        org = SpokeOrg()
        dn = '%s=%s,%s' % (self.org_attr, self.org_name, self.base_dn)
        dn_info = {'objectClass': ['top', self.org_class],
                   self.org_attr: [self.org_name]}
        expected_result = [(dn, dn_info)]
        
        result = org.get(self.org_name)['data']
        self.assertEqual(result, expected_result)
        
    def test_spoke_org_get_all(self):
        """Retrieve all orgs; return a list of org objects."""
        # First org is already created by SetUp()
        org2 = 'SpokeOrgTest2'
        org_dn1 = '%s=%s,%s' % (self.org_attr, self.org_name, self.base_dn)
        org_dn2 = '%s=%s,%s' % (self.org_attr, org2, self.base_dn)
        org_dn1_info = {'objectClass': ['top', self.org_class],
                   self.org_attr: [self.org_name]}
        org_dn2_info = {'objectClass': ['top', self.org_class],
                   self.org_attr: [org2]}
        expected_result = [(org_dn1, org_dn1_info), (org_dn2, org_dn2_info)]
        
        org = SpokeOrg()
        org.create(org2)  
        result = org.get()['data']
        self.assertEqual(result, expected_result)
        org.delete(org2, self.org_children)
        
    def test_spoke_org_get_missing(self):
        """Retrieve a missing org; return an empty list."""
        org_name = 'testSpokeOrgMissing'
        org = SpokeOrg()
        expected_result = []
        result = org.get(org_name)['data']
        self.assertEqual(result, expected_result)
        
    def test_spoke_org_update_org_suffix(self):
        """Modify an org's suffix; return updated org object."""
        old_suffix = self.org_suffix_name
        new_suffix = 'neworgsuffix.org'
        org_name = 'testOrgModSuffix'
    
        dn = 'o=%s,%s' % (org_name, self.base_dn)
        dn_info = {'objectClass': ['top', self.org_class, self.user_class], 
                   self.org_attr: [org_name],
                   self.org_suffix_attr: [old_suffix]}
        expected_result = [(dn, dn_info)]
        org = SpokeOrg()
        org.create(org_name, suffix=new_suffix)
        org.modify(org_name, suffix=old_suffix)
        result = org.get(org_name)['data']
        self.assertEqual(result, expected_result)        
        org.delete(org_name, self.org_children)
    
    def test_spoke_org_delete(self):
        """Delete an org; return True."""
        org_name = 'testSpokeOrgDelete'
        org = SpokeOrg()
        org.create(org_name)
        self.assertTrue(org.delete(org_name))
        
    def test_spoke_org_delete_missing(self):
        """Delete missing org; raise NotFound."""
        org_name = 'testSpokeOrgMissing'
        org = SpokeOrg()
        self.assertRaises(error.NotFound, org.delete, org_name)
        
    def test_spoke_org_delete_with_children(self):
        """Delete an org with still present children; raise SaveTheBabies."""
        org = SpokeOrg()
        child_name = 'WouldBeOrphaned'
        child = SpokeOrgChild(self.org_name)
        child.create(child_name)
        self.assertRaises(error.SaveTheBabies, org.delete, self.org_name)
        child.delete(child_name)
        
# Org Child tests

    def test_create_child_container(self):
        """Create a child container; return True."""      
        child_name = 'test'
        child = self.container_attr + '=' + child_name
        organisation = self.org_attr + '=' + self.org_name
        dn = child + ',' + organisation + ',' + self.base_dn
        dn_info = {'objectClass': ['top', self.container_class],
                   self.container_attr: [child_name]}
        expected_result = [(dn, dn_info)]       
        child = SpokeOrgChild(self.org_name)
        self.assertTrue(child.create(child_name))
        result = child.get(child_name)['data']
        self.assertEqual(result, expected_result)
        child.delete(child_name)
        
    def test_create_child_twice(self):
        """Create an existing child container twice; raise AlreadyExists."""
        child_name = 'people' # Already created in SetUP.
        child = SpokeOrgChild(self.org_name)
        self.assertRaises(error.AlreadyExists, child.create, child_name)
        
    def test_create_child_with_missing_parent(self):
        """Create child with missing parent; raise NotFound."""
        org_name = 'MissingParent'
        self.assertRaises(error.NotFound, SpokeOrgChild, org_name)
        
    def test_spoke_org_get_children(self):
        """Retrieve all an org's immediate child containers; return a list."""
        expected_result = []
        for child_name in self.org_children:
            dn = '%s=%s,%s=%s,%s' % (self.container_attr, child_name,
                        self.org_attr, self.org_name, self.base_dn)
            dn_info = {'objectClass': ['top', self.container_class],
                       self.container_attr: [child_name]}
            expected_result.append((dn, dn_info))
            
        child = SpokeOrgChild(self.org_name)
        result = child.get()['data']
        self.assertEqual(result, expected_result)
        
    def test_spoke_org_get_child(self):
        """Retrieve an org's child; return a child object."""
        child_name = 'people'
        rdn = self.container_attr + '=' + child_name
        organisation = self.org_attr + '=' + self.org_name
        dn = rdn + ',' + organisation + ',' + self.base_dn
        dn_info = {'objectClass': ['top', self.container_class],
                   self.container_attr: [child_name]}
        expected_result = [(dn, dn_info)]
        child = SpokeOrgChild(self.org_name)   
        result = child.get(child_name)['data']
        self.assertEqual(result, expected_result)
        
    def test_spoke_org_get_child_missing(self):
        """Retrieve an org's missing child; return an empty list."""
        child_name = 'child_missing'
        child = SpokeOrgChild(self.org_name)
        self.assertFalse(child.get(child_name)['data'])
        
    def test_spoke_org_child_delete(self):
        """Delete an org's child; return True."""
        child_name = 'people'
        child = SpokeOrgChild(self.org_name)
        self.assertTrue(child.delete(child_name))
        
    def test_spoke_org_child_delete_missing(self):
        """Delete an org's missing child; raise NotFound."""
        child_name = 'testMissing'
        child = SpokeOrgChild(self.org_name)
        self.assertRaises(error.NotFound, child.delete, child_name)

if __name__ == "__main__":
    unittest.main()
