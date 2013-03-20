"""Tests user.py module."""
# core modules
import unittest
# own modules
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.log as logger
from spoke.lib.org import SpokeOrg
from spoke.lib.user import SpokeUser

class SpokeUserTest(unittest.TestCase):
    
    """A test Class for the spoke_user.py module."""
    
    def __init__(self, methodName):
        """Setup config data and LDAP connection."""
        unittest.TestCase.__init__(self, methodName)
        common_config = '../../contrib/spoke.conf'
        custom_config = '/tmp/spoke.conf'
        config_files = (common_config, custom_config)
        self.config = config.setup(config_files)
        self.log = logger.log_to_console()
        self.base_dn = self.config.get('LDAP', 'basedn')
        self.search_scope = 2 # ldap.SCOPE_SUBTREE
        self.retrieve_attr = None
        self.org_name = 'SpokeUserTest'
        self.org_attr = self.config.get('ATTR_MAP', 'org_attr')
        self.org_def_children = self.config.get('ATTR_MAP', 'org_def_children')
        self.org_children = self.org_def_children.split(',')
        self.container_attr = self.config.get('ATTR_MAP', 'container_attr')
        self.user_container = self.config.get('ATTR_MAP', 'user_container')
        self.user_key = self.config.get('ATTR_MAP', 'user_key')
        self.user_login = self.config.get('ATTR_MAP', 'user_login')
        self.user_class = self.config.get('ATTR_MAP', 'user_class')
        self.user_name = self.config.get('ATTR_MAP', 'user_name')
        self.user_enable = self.config.get('ATTR_MAP', 'user_enable')
        self.first = 'timmy'
        self.last = 'test'
        self.user_id = self.first
        self.email_dom = 'test.user.loc'
        self.email_addr = self.user_id + '@' + self.email_dom
        self.org_dn = '%s=%s,%s' % (self.org_attr, self.org_name, self.base_dn)
        self.user_container_dn = '%s=%s,%s' % (self.container_attr, \
                                            self.user_container, self.org_dn)
    
    def setUp(self):
        """Create test organisation and user."""
        org = SpokeOrg()
        org.create(self.org_name, self.org_children)
        user = SpokeUser(self.org_name)
        user.create(self.email_addr, self.first)
    
    def tearDown(self):
        """Delete test organisation and user"""
        user = SpokeUser(self.org_name)
        user.delete(self.first)
        org = SpokeOrg()
        org.delete(self.org_name, self.org_children)
    
    def test_get_all_users(self):
        """Retrieve all user accounts; return a list of user objects."""
        user_id2 = 'timmy2'
        email_addr2 = user_id2 + '@' + self.email_dom
        expected_result = []
        for u in (self.first, user_id2):
            rdn = '%s=%s' % (self.user_key, u)
            dn = '%s,%s' % (rdn, self.user_container_dn)
            dn_info = {self.user_name: [u],
                   self.user_key: [u],
                   'objectClass': ['top', 'inetOrgPerson', self.user_class],
                   self.user_login: [u + '@' + self.email_dom],
                   self.user_enable: ['TRUE'],
                   'sn': [u], 'cn': [u]
                   }
            append_this = (dn, dn_info)
            expected_result.append(append_this)
        user = SpokeUser(self.org_name)
        user.create(email_addr2, user_id2)
        result = user.get()['data']
        self.assertEqual(result, expected_result)
        user.delete(user_id2)
    
    def test_get_user(self):
        """Retrieve a user account; return a user object."""
        rdn = '%s=%s' % (self.user_key, self.user_id)
        dn = '%s,%s' % (rdn, self.user_container_dn)
        dn_info = {self.user_name: [self.user_id],
                   self.user_key: [self.user_id],
                   'objectClass': ['top', 'inetOrgPerson', self.user_class],
                   self.user_login: [self.email_addr],
                   self.user_enable: ['TRUE'],
                   'sn': [self.first], 'cn': [self.first]
                   }
        expected_result = [(dn, dn_info)]
        user = SpokeUser(self.org_name)
        result = user.get(self.first)['data']
        self.assertEqual(result, expected_result)
    
    def test_get_missing_user(self):
        """Retrieve a missing user account; return an empty list."""
        user_id = 'missinguser'
        expected_result = []
        user = SpokeUser(self.org_name)
        result = user.get(user_id)['data']
        self.assertEqual(result, expected_result)
    
    def test_create_user_first(self):
        """Create a user without a surname; return a user object."""
        first = 'testCreateDeleteUserFirst'
        user_id = first
        email_addr = user_id + '@' + self.email_dom
        email_addr = email_addr.lower()
        rdn = '%s=%s' % (self.user_key, user_id)
        container = '%s=%s' % (self.container_attr, self.user_container)
        base_dn = '%s,%s=%s,%s' % (container, self.org_attr,
                                   self.org_name, self.base_dn)
        dn = '%s,%s' % (rdn, base_dn)
        dn_info = {self.user_name: [user_id],
                   self.user_key: [user_id],
                   'objectClass': ['top', 'inetOrgPerson', self.user_class],
                   self.user_login: [email_addr],
                   self.user_enable: ['TRUE'],
                   'sn': [first], 'cn': [first]
                   }
        expected_result = [(dn, dn_info)]
        user = SpokeUser(self.org_name)
        result = user.create(email_addr, first)['data']
        self.assertEqual(result, expected_result)
        user.delete(first)
    
    def test_create_user_first_last(self):
        """Create a user with a first and surname; return a user object."""
        first = 'testCreateUserFirst'
        last = 'Last'
        user_id = first + last
        email_addr = user_id + '@' + self.email_dom
        email_addr = email_addr.lower()
        rdn = '%s=%s' % (self.user_key, user_id)
        container = '%s=%s' % (self.container_attr, self.user_container)
        base_dn = '%s,%s=%s,%s' % (container, self.org_attr,
                                   self.org_name, self.base_dn)
        dn = '%s,%s' % (rdn, base_dn)
        dn_info = {self.user_name: [user_id],
                   self.user_key: [user_id],
                   'objectClass': ['top', 'inetOrgPerson', self.user_class],
                   self.user_login: [email_addr],
                   self.user_enable: ['TRUE'],
                   'sn': [last], 'cn': [first]
                   }
        expected_result = [(dn, dn_info)]
        user = SpokeUser(self.org_name)
        result = user.create(email_addr, first, last)['data']
        self.assertEqual(result, expected_result)
        user.delete(first, last)
    
    def test_create_user_twice(self):
        """Create a user that already exists; raise AlreadyExists."""
        user = SpokeUser(self.org_name)
        self.assertRaises(error.AlreadyExists, user.create, self.email_addr, \
                          self.first)
    
    def test_create_user_with_invalid_email(self):
        """Create a user with an invalid email address; raise InputError."""
        user = SpokeUser(self.org_name)
        email = 'invalidaddress'
        self.assertRaises(error.InputError, user.create, email, self.first)
    
    def test_delete_user(self):
        """Delete user; return True."""
        user = SpokeUser(self.org_name)
        first = 'test_delete_user'
        email_addr = first + '@' + self.email_dom
        user.create(email_addr, first)
        self.assertTrue(user.delete(first))
    
    def test_delete_non_existant_user(self):
        """Delete non-existent user; raise NotFound."""
        user = SpokeUser(self.org_name)
        first = 'test_delete_non_existant_user'
        self.assertRaises(error.NotFound, user.delete, first)
    
    def test_get_user_with_missing_org(self):
        """Retrieve a user with no org; raise NotFound."""
        org_name = 'SpokeMissingOrg'
        self.assertRaises(error.NotFound, SpokeUser, org_name)

if __name__ == "__main__":
    unittest.main()
