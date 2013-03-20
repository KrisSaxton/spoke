"""Tests Spoke vcs.py module"""
# core modules
import unittest
# own modules
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.log as logger
from spoke.lib.org import SpokeOrg
from spoke.lib.user import SpokeUser
from spoke.lib.vcs import SpokeSVN

class SpokeVCSTest(unittest.TestCase):
    
    """A class for testing the Spoke vcs.py module."""
    
    def __init__(self, methodName):
        """Setup config data and LDAP connection."""
        unittest.TestCase.__init__(self, methodName)
        common_config = '../../contrib/spoke.conf'
        custom_config = '/tmp/spoke.conf'
        config_files = (common_config, custom_config)
        self.config = config.setup(config_files)
        self.log = logger.log_to_console()
        self.base_dn = self.config.get('LDAP', 'basedn')
        self.search_scope = 2 # ldap.SUB
        self.retrieve_attr = None
        self.container_attr = self.config.get('ATTR_MAP', 'container_attr')
        self.user_container = self.config.get('ATTR_MAP', 'user_container')
        self.user_key = self.config.get('ATTR_MAP', 'user_key')
        self.svn_class = self.config.get('VCS', 'svn_class')
        self.svn_repo_attr = self.config.get('VCS', 'svn_repo_attr')
        self.svn_enable_attr = self.config.get('VCS', 'svn_enable_attr')
        self.org_name = 'SpokeOrgSvnTest'
        self.first = 'simon'
        self.last = 'sourcecontrol'
        self.user_id = self.first + self.last
        self.email_dom = 'test.user.org'
        self.email_addr = self.user_id + '@' + self.email_dom
        self.svn_repo_name = 'main'
        
    def setUp(self):
        """Create test organisation and user."""
        org = SpokeOrg()
        org.create(self.org_name)
        user = SpokeUser(self.org_name)
        user.create(self.email_addr, self.first, self.last)
        svn = SpokeSVN(self.org_name, self.user_id)
        svn.create(self.svn_repo_name)

    def tearDown(self):
        """Delete test organisation and user"""
        user = SpokeUser(self.org_name)
        user.delete(self.first, self.last)
        org = SpokeOrg()
        org.delete(self.org_name)
        
        
    def test_add_svn_repo(self):
        """Add a svn repo to a user account; return svn account details."""
        repo = 'testcreaterepo'
        org = 'o=%s' % (self.org_name)
        people = '%s=%s' % (self.container_attr, self.user_container)
        uid = '%s=%s' % (self.user_key, self.user_id)
        dn = '%s,%s,%s,%s' % (uid, people, org, self.base_dn)
        dn_info = {self.svn_repo_attr: [self.svn_repo_name, repo]}
        expected_result = [(dn, dn_info)]
        svn = SpokeSVN(self.org_name, self.user_id)
        result = svn.create(repo)['data'][0]
        attrs = result[1]
        svn_attrs = {}
        svn_attrs[self.svn_repo_attr] = attrs[self.svn_repo_attr]
        svn_result = [(result[0], svn_attrs)]
        self.assertEqual(svn_result, expected_result)
    
    def test_add_svn_repo_twice(self):
        """Add an existing svn repo to a user account; raise AlreadyExists."""
        svn = SpokeSVN(self.org_name, self.user_id)
        self.assertRaises(error.AlreadyExists, svn.create, self.svn_repo_name)
        
    def test_add_svn_repo_to_missing_user(self):
        """Add a svn repo to a missing user; raise MissingUser."""
        user_id = 'svntestmissinguser'
        self.assertRaises(error.NotFound, SpokeSVN, self.org_name, user_id)
    
    def test_add_invalid_svn_repo(self):
        """Add a svn repo with an invalid name; raise InputError."""
        pass
    
    def test_get_svn_repo(self):
        """Retrieve an svn repo; return svn account details."""
        org = 'o=%s' % (self.org_name)
        people = '%s=%s' % (self.container_attr, self.user_container)
        uid = '%s=%s' % (self.user_key, self.user_id)
        dn = '%s,%s,%s,%s' % (uid, people, org, self.base_dn)
        dn_info = {self.svn_enable_attr: ['TRUE'],
                self.svn_repo_attr: [self.svn_repo_name]}
        expected_result = [(dn, dn_info)]
        svn = SpokeSVN(self.org_name, self.user_id)
        result = svn.get(self.svn_repo_name)['data']
        self.assertEqual(result, expected_result)
    
    def test_get_all_svn_repos(self):
        """Retrieve all svn repos for a user; return svn account details."""
        repo = 'testcreaterepo'
        org = 'o=%s' % (self.org_name)
        people = '%s=%s' % (self.container_attr, self.user_container)
        uid = '%s=%s' % (self.user_key, self.user_id)
        dn = '%s,%s,%s,%s' % (uid, people, org, self.base_dn)
        dn_info = {self.svn_enable_attr: ['TRUE'],
                   self.svn_repo_attr: [self.svn_repo_name, repo]}
        expected_result = [(dn, dn_info)]
        svn = SpokeSVN(self.org_name, self.user_id)
        svn.create(repo)
        result = svn.get()['data']
        self.assertEqual(result, expected_result)
    
    def test_get_missing_svn_repo(self):
        """Retrieve a missing svn repo; return empty list."""
        repo = 'testgetmissingrepo'
        svn = SpokeSVN(self.org_name, self.user_id)
        self.assertFalse(svn.get(repo)['data'])
    
    def test_delete_svn_repo(self):
        """Delete an svn repo; return True."""
        svn = SpokeSVN(self.org_name, self.user_id)
        self.assertTrue(svn.delete(self.svn_repo_name))
    
    def test_delete_missing_svn_repo(self):
        """Delete a missing svn repo; return True."""
        repo = 'testdeletemissingrepo'
        svn = SpokeSVN(self.org_name, self.user_id)
        self.assertRaises(error.NotFound, svn.delete, repo)
    
    def test_disable_svn_access(self):
        """Disable svn access; verify svn access disabled."""
        org = 'o=%s' % (self.org_name)
        people = '%s=%s' % (self.container_attr, self.user_container)
        uid = '%s=%s' % (self.user_key, self.user_id)
        dn = '%s,%s,%s,%s' % (uid, people, org, self.base_dn)
        dn_info = {self.svn_enable_attr: ['FALSE']}
        expected_result = [(dn, dn_info)]
        svn = SpokeSVN(self.org_name, self.user_id)
        result = svn.modify(enable=False)['data']
        self.assertEqual(result, expected_result)
        
    def test_disable_missing_svn_access(self):
        """Disable missing svn access; raise NotFound.."""
        svn = SpokeSVN(self.org_name, self.user_id)
        svn.delete(self.svn_repo_name)
        self.assertRaises(error.NotFound, svn.modify, enable=False)
        
    def test_enable_missing_svn_access(self):
        """Enable missing svn access; raise NotFound."""
        svn = SpokeSVN(self.org_name, self.user_id)
        svn.delete(self.svn_repo_name)
        self.assertRaises(error.NotFound, svn.modify, enable=True)
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
