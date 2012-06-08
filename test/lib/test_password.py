"""Tests Spoke pwd.py module"""
import unittest

import error
import config

from org import SpokeOrg
from user import SpokeUser
from passwd import SpokePwd


class SpokePasswordTest(unittest.TestCase):
    
    """A class for testing the Spoke dns.py module."""
    
    def __init__(self, methodName):
        """Setup config data and LDAP connection."""
        unittest.TestCase.__init__(self, methodName)
        common_config = '../../contrib/spoke.conf'
        custom_config = '/tmp/spoke.conf'
        config_files = (common_config, custom_config)
        self.config = config.setup(config_files)
        self.base_dn = self.config.get('LDAP', 'basedn')
        self.search_scope = 2 # ldap.SUB
        self.retrieve_attr = None
        self.container_attr = self.config.get('ATTR_MAP', 'container_attr')
        self.org_name = 'SpokeOrgPwdTest'
        self.org_attr = self.config.get('ATTR_MAP', 'org_attr')
        self.org_def_children = self.config.get('ATTR_MAP', 'org_def_children')
        self.org_children = self.org_def_children.split(',')
        self.user_container = self.config.get('ATTR_MAP', 'user_container')
        self.user_key = self.config.get('ATTR_MAP', 'user_key') 
        self.user_login = self.config.get('ATTR_MAP', 'user_login')
        self.user_class = self.config.get('ATTR_MAP', 'user_class')
        self.user_name = self.config.get('ATTR_MAP', 'user_name')
        self.user_enable = self.config.get('ATTR_MAP', 'user_enable')
        self.user_def_pwd = self.config.get('ATTR_MAP', 'user_def_pwd')
        self.first = 'peter'
        self.last = 'password'
        self.user_id = self.first + self.last
        self.email_dom = 'test.user.loc'
        self.email_addr = self.user_id + '@' + self.email_dom

    def setUp(self):
        """Create test organisation and user."""
        org = SpokeOrg()
        org.create(self.org_name, self.org_children)
        user = SpokeUser(self.org_name)
        user.create(self.email_addr, self.first, self.last)
        pwd = SpokePwd(self.org_name, self.user_id)
        pwd.create(self.user_def_pwd)

    def tearDown(self):
        """Delete test organisation and user"""
        user = SpokeUser(self.org_name)
        user.delete(self.first, self.last)
        org = SpokeOrg()
        org.delete(self.org_name, self.org_children)

    def test_create_password(self):
        """Create a user password; return success result."""
        first = 'test'
        last = 'createpassword'
        user_id = first + last
        email_addr = user_id + '@' + self.email_dom
        password = 'testcreatepassword'       
        user = SpokeUser(self.org_name)
        user.create(email_addr, first, last)  
        expected_result = ['success']
        pwd = SpokePwd(self.org_name, user_id)
        result = pwd.create(password)['data']
        self.assertEquals(result, expected_result)
        user.delete(first, last)
    
    def test_create_password_twice(self):
        """Create a user password twice; raise AlreadyExists."""
        pwd = SpokePwd(self.org_name, self.user_id)
        self.assertRaises(error.AlreadyExists, pwd.create, self.user_def_pwd)
    
    def test_get_password(self):
        """Verify a user password; return success result."""        
        pwd = SpokePwd(self.org_name, self.user_id)
        expected_result = ['success']
        result = pwd.get(self.user_def_pwd)['data']
        self.assertEquals(result, expected_result)
        
    def test_get_missing_password(self):
        """Verify a missing password; raise AuthError."""
        first = 'test'
        last = 'getmissingpassword'
        user_id = first + last
        email_addr = user_id + '@' + self.email_dom
        password = 'getmissingpassword'        
        user = SpokeUser(self.org_name)
        user.create(email_addr, first, last)       
        pwd = SpokePwd(self.org_name, user_id)
        self.assertRaises(error.AuthError, pwd.get, password)
        user.delete(first, last)
        
    def test_get_with_wrong_password(self):
        """Verify a bad user password; raise AuthError."""
        first = 'test'
        last = 'getbadpassword'
        user_id = first + last
        email_addr = user_id + '@' + self.email_dom
        password = 'password'
        badpassword = 'badpassword'        
        user = SpokeUser(self.org_name)
        user.create(email_addr, first, last)        
        pwd = SpokePwd(self.org_name, user_id)
        pwd.create(password)        
        self.assertRaises(error.AuthError, pwd.get, badpassword)       
        user.delete(first, last)
    
    def test_update_password(self):
        """Update existing user password; return success result."""
        new_password = 'test_update_password'
        pwd = SpokePwd(self.org_name, self.user_id)
        expected_result = ['success']
        result = pwd.modify(self.user_def_pwd, new_password)['data']
        self.assertEquals(result, expected_result)
        
    def test_update_password_with_wrong_old_password(self):
        """Update user password with wrong old password; raise AuthError."""
        new_pass = 'test_update_newpass'
        bad_pass = 'test_update_badpass'
        pwd = SpokePwd(self.org_name, self.user_id)
        self.assertRaises(error.AuthError, pwd.modify, bad_pass, new_pass)
    
    def test_update_with_invalid_password(self):
        """Update user password with bad new password; raise InputError."""
        pass
    
    def test_delete_password(self):
        """Delete user password; return True."""
        first = 'test'
        last = 'deletepassword'
        user_id = first + last
        email_addr = user_id + '@' + self.email_dom
        password = 'testdeletepassword'       
        user = SpokeUser(self.org_name)
        user.create(email_addr, first, last)
        pwd = SpokePwd(self.org_name, user_id)
        pwd.create(password)
        self.assertTrue(pwd.delete, password)
        user.delete(first, last)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()