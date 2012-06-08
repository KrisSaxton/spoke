"""Tests Spoke config.py module"""
import os
import unittest

import error
import config

class SpokeConfigTest(unittest.TestCase):
    
    """A Class for testing the Spoke config,py module"""
    
    def __init__(self, methodName):
        """Define test config data, write, parse and return config object."""
        unittest.TestCase.__init__(self, methodName)
        self.test_config = '''
[testsection1]
key1=value1
key2 = value 2

[testsection2]
key1=value1
key2 = value 2
'''

    def setUp(self):
        self.test_config_filename = '/tmp/spoke_test_config.conf'
        test_config_file = open(self.test_config_filename, 'w')
        test_config_file.write(self.test_config)
        test_config_file.close()
        self.config = config.setup(self.test_config_filename)

    def tearDown(self):
        """Remove test config and log file"""
        os.remove(self.test_config_filename)
        config.gConfig = None

    def test_section_true(self):
        """Test for present section; return True."""
        self.assertTrue(self.config.has_section('testsection1'))

    def test_section_false(self):
        """Test for absent section; return False."""
        self.assertFalse(self.config.has_section('bogussection'))
        
    def test_key_true(self):
        """Test for present key; return True."""
        self.assertTrue(self.config.has_option('testsection1', 'key1'))
    
    def test_key_false(self):
        """Test for absent key; return False."""
        self.assertFalse(self.config.has_option('testsection2', 'key3'))
    
    def test_val_true(self):
        """Fetch a particular value."""
        self.assertEqual(self.config.get('testsection1','key1'), 'value1')
    
    def test_val_true_with_space(self):
        """Fetch a value containing a space."""
        self.assertEqual(self.config.get('testsection1','key2'), 'value 2') 
    
    def test_config_object_reuse(self):
        """Call setup multiple times; parse the config file only once."""
        test_config_filename = '/tmp/spoke_test_config_object_reuse.conf'
        test_config_file = open(test_config_filename, 'w')
        test_config_file.write(self.test_config)
        test_config_file.close()
        config.gConfig = None
        self.config = config.setup(test_config_filename)
        os.remove(test_config_filename)
        self.config = config.setup()
        self.assertTrue(self.config.has_section('testsection1'))
        
    def test_config_missing_config_file(self):
        """Parse missing filename; raise ConfigError."""
        test_config_filename = '/tmp/test_config_missing_config_file.conf'
        config.gConfig = None
        self.assertRaises(error.ConfigError,config.setup, test_config_filename)
        
    def test_config_file_missing(self):
        """Instantiate without config file; raise ConfigError."""
        config.gConfig = None
        self.assertRaises(error.ConfigError,config.setup)
        
    def test_spoke_LDAP_missing_LDAP_config_section(self):
        """Parse config with missing LDAP section; raise ConfigError."""
        self.assertRaises(error.ConfigError,self.config.get,'LDAP','server')
        
    def test_spoke_LDAP_missing_server_config_key(self):
        """Parse config with missing ldap server key; raise ConfigError."""
        config.gConfig = None
        self.test_nosrvr_config = '''
[LDAP]
key1=value1
key2 = value 2
'''
        self.test_nosrvr_config_filename = '/tmp/spoke_test_nosrvr_config.conf'
        test_nosrvr_config_file = open(self.test_nosrvr_config_filename, 'w')
        test_nosrvr_config_file.write(self.test_nosrvr_config)
        test_nosrvr_config_file.close()
        self.config = config.setup(self.test_nosrvr_config_filename)
        self.assertRaises(error.ConfigError,self.config.get,'LDAP','server')
        os.remove(self.test_nosrvr_config_filename)
        
    def test_zzz_finish(self): pass
           
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
