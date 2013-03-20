"""Tests Spoke mbx.py module."""
# core modules
import unittest
# own modules
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.log as logger
from spoke.lib.mbx import SpokeMbx

class SpokeMbxTest(unittest.TestCase):

    """A Class for testing the Spoke mbx.py module."""
    
    def __init__(self, methodName):
        """Setup config data and Cyrus connection."""
        unittest.TestCase.__init__(self, methodName)
        common_config = '../../contrib/spoke.conf'
        custom_config = '/tmp/spoke.conf'
        config_files = (common_config, custom_config)
        self.config = config.setup(config_files)
        self.log = logger.log_to_console()
        self.user = self.config.get('IMAP', 'user')
        self.sep = '/'
        self.mbx_name = 'test@test.mailbox.loc'
        
    def setUp(self): 
        mbx = SpokeMbx()
        mbx.create(self.mbx_name)

    def tearDown(self):
        mbx = SpokeMbx()
        mbx.delete(self.mbx_name)
    
    def test_create_mailbox(self):
        """Create a mailbox; return True."""
        mbx_name = 'create@test.mailbox.loc'
        mbx = SpokeMbx()
        self.assertTrue(mbx.create(mbx_name))
        mbx.delete(mbx_name)
        
    def test_create_mailbox_twice(self):
        """Create mailbox twice; raise SpokeIMAPError."""
        mbx = SpokeMbx()
        self.assertRaises(error.SpokeIMAPError, mbx.create, self.mbx_name)
         
    def test_get_mailbox(self):
        """Retrieve a mailbox; return a list of tuples."""
        flags = '\\HasNoChildren'
        expected_result = [(self.mbx_name, self.sep, flags)]
        mbx = SpokeMbx()
        result = mbx.get(self.mbx_name)
        self.assertEqual(expected_result, result)
        
    def test_input_nvalid_mailbox(self):
        """Retrieve an invalid mailbox; raise InputError."""
        mbx_name = '*@test.mailbox.loc'
        mbx = SpokeMbx()
        self.assertRaises(error.InputError, mbx.get, mbx_name)     
        
    def test_delete_mailbox(self):
        """Delete a mailbox; return True."""
        mbx_name = 'delete@test.create.mailbox.loc'
        mbx = SpokeMbx()
        mbx.create(mbx_name)
        self.assertTrue(mbx.delete(mbx_name))
        
    def test_delete_missing_mailbox(self):
        """Delete a missing mailbox; raise SpokeIMAPError."""
        mbx_name = 'deletemissing@test.create.mailbox.loc'
        mbx = SpokeMbx()
        self.assertRaises(error.SpokeIMAPError, mbx.delete, mbx_name)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
