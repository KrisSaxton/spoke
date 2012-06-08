"""Tests Spoke ldap.py module."""
import unittest

import config
import error
import ldap_helper

class SpokeLDAPTest(unittest.TestCase):
    
    """A class for testing the SpokeLDAP module."""
    
    def __init__(self, methodName):
        """Setup config data and LDAP connection."""
        unittest.TestCase.__init__(self, methodName)
        common_config = '../../contrib/spoke.conf'
        custom_config = '/tmp/spoke.conf'
        config_files = (common_config, custom_config)
        self.config = config.setup(config_files)
        try:
            self.ldap = ldap_helper.SpokeLDAP()
        except:
            raise
        self.base_dn = self.config.get('LDAP', 'basedn')
        self.search_scope = 2
        self.retrieve_attr = None
        self.org_names = ['test', 'test1']
        self.org_attr = self.config.get('ATTR_MAP', 'org_attr')
        self.org_def_children = self.config.get('ATTR_MAP', 'org_def_children')           
        self.org_children = self.org_def_children.split(',')
        self.user_key = self.config.get('ATTR_MAP', 'user_key') 
        self.first = 'kris'
        self.last = 'saxton'
        self.user_id = self.first + self.last      
    
    def setUp(self): pass       

    def tearDown(self): pass
    
    def test_spoke_LDAP_search_unique(self):
        """Successful search for unique object, returns object."""
        
        """Setup our test data"""
        org_name = 'testSpokeLDAPSearchUnique'
        base_dn = self.base_dn
        rdn = 'o=%s' % org_name
        dn = '%s,%s' % (rdn, base_dn)
        dn_info = {'o': [org_name], 
                       'objectClass': ['top', 'organization'] }
        dn_attributes = [(k, v) for (k, v) in dn_info.items()]
        self.ldap.LDAP.add_s(dn, dn_attributes)
        search_scope = self.search_scope
        retrieve_attr = ['dn']
        search_filter = rdn
        expected_results = [(rdn + ',' + base_dn, {})] # Single entry

        """Make sure search returns what we expect."""
        self.assertEqual(self.ldap.search_uniq(base_dn, 
                                               search_scope, 
                                               search_filter, 
                                               retrieve_attr),
                                               expected_results)
        """Delete data."""
        self.ldap.LDAP.delete_s(dn)
    
    def test_spoke_LDAP_search_missing(self):
        """Search for missing object should return None."""
        org_name = 'testSpokeLDAPSearchMissing'
        base_dn = self.base_dn
        search_scope = self.search_scope
        retrieve_attr = self.retrieve_attr
        search_filter = 'o=%s' % org_name
        
        self.assertFalse(self.ldap.search_uniq(base_dn, search_scope, 
                                               search_filter, retrieve_attr))      
        
    def test_spoke_LDAP_search_unique_multiple(self):
        """Unique search raises SearchUniqueError when multiple results found.
        """
        
        """Setup our test data"""
        org_names = ['testSpokeLDAPSearchUniqueMultiple1',
                     'testSpokeLDAPSearchUniqueMultiple2' ]
        uid = 'testSpokeLDAPSearchUniqueMultiple'
        for org_name in org_names:
            base_dn = self.base_dn
            rdn = 'o=%s' % org_name
            dn = '%s,%s' % (rdn, base_dn)
            dn_info = {'o': [org_name], 
                       'objectClass': ['top', 'organization'] }
            dn_attributes = [(k, v) for (k, v) in dn_info.items()]
            # Create the org.
            self.ldap.LDAP.add_s(dn, dn_attributes)
            # Now create the user.
            base_dn = dn
            dn = 'uid=%s,%s' % (uid, base_dn)
            dn_info = {
                       'objectClass': ['top', 'inetOrgPerson', 'aenetAccount'],
                       'uid': [uid],
                       'cn': [uid], 'sn': [uid], 
                       'aenetAccountDisplayName': [uid],
                       'aenetAccountLoginName': [uid],
                       'aenetAccountEnabled': ['TRUE'] 
                       }
            dn_attributes = [(k, v) for (k, v) in dn_info.items()]
            self.ldap.LDAP.add_s(dn, dn_attributes)
        
        """Run the tests"""    
        search_filter = 'uid=' + uid
        self.assertRaises(error.SearchUniqueError, self.ldap.search_uniq, 
                          self.base_dn, self.search_scope,
                          search_filter, self.retrieve_attr)   
        
        """Delete the test data"""
        for org_name in org_names:
            base_dn = self.base_dn
            org = 'o=%s' % org_name
            dn = 'uid=%s,%s,%s' % (uid, org, base_dn)
            # Delete the user.
            self.ldap.LDAP.delete_s(dn)
            # Delete the org.
            dn = '%s,%s' % (org, base_dn)
            self.ldap.LDAP.delete_s(dn)  
        
if __name__ == "__main__":
    unittest.main()