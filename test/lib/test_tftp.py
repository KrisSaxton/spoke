"""Tests tftp.py module."""

import os
import unittest

import error
import config

from tftp import SpokeTFTP

class SpokeTFTPTest(unittest.TestCase):
    
    def __init__(self, methodName):
        """Setup config data."""
        unittest.TestCase.__init__(self, methodName)
        common_config = '../../contrib/spoke.conf'
        custom_config = '/tmp/spoke.conf'
        config_files = (common_config, custom_config)
        self.config = config.setup(config_files)
        self.tftp_root = self.config.get('TFTP', 'tftp_root')
        self.tftp_conf_dir = self.config.get('TFTP', 'tftp_conf_dir')
        self.tftp_mac_prefix = self.config.get('TFTP', 'tftp_mac_prefix')
        self.mac = '00:0C:29:57:3B:31'
        self.target = 'testfile'
        self.tftp_dir = self.tftp_root + "/" + self.tftp_conf_dir + "/"
        
        
    def setUp(self):
        """Create test tftp file structure."""
        for d in self.tftp_root, self.tftp_dir:
            if not (os.path.exists(d)):
                try:
                    os.makedirs(d)
                except Exception as e:
                    raise e
        if not os.path.exists(self.tftp_dir + self.target):
            open(self.tftp_dir + self.target, 'w').close()
        tftp = SpokeTFTP(self.tftp_root)
        tftp.create(self.mac, self.target)
    
    def tearDown(self):
        """Delete test tftp file structure."""
        tftp = SpokeTFTP(self.tftp_root)
        tftp.delete(self.mac)
        if os.path.exists(self.tftp_dir + self.target):
            os.remove(self.tftp_dir + self.target)
        for d in self.tftp_dir, self.tftp_root:
            if (os.path.exists(d)):
                try:
                    os.removedirs(d)
                except Exception as e:
                    raise e
                
    def test_get_tftp_link(self):
        """Search for a tftp association; return list."""
        # mac should be returned as lower case, with s/:/- and with prefix
        mac = self.tftp_mac_prefix + '-' + '00-0c-29-57-3b-31'
        tftp = SpokeTFTP(self.tftp_root)
        result = tftp.search(self.mac)['data']
        expected_result = [{mac:[self.target]}]
        self.assertEqual(result, expected_result) 

    def test_get_missing_mac(self):
        """Search for missing mac link; return empty list."""
        mac = '00:00:00:00:00:02'
        tftp = SpokeTFTP(self.tftp_root)
        result = tftp.search(mac)['data']
        expected_result = []
        self.assertEqual(result, expected_result)

    def test_get_missing_target(self):
        """Search for missing target; raise NotFound."""
        target = 'missing'
        tftp = SpokeTFTP(self.tftp_root)
        self.assertRaises(error.NotFound, tftp.search, target=target)
        
    def test_get_unused_target(self):
        """Search for target with no linked macs; return empty list."""
        target = 'unused'
        tftp = SpokeTFTP(self.tftp_root)
        open(self.tftp_dir + target, 'w').close()
        result = tftp.search(target=target)['data']
        expected_result = []
        self.assertEqual(result, expected_result)
        os.remove(self.tftp_dir + target)

    def test_get_invalid_mac(self):
        """Search for an invalid mac; raise InputError."""
        mac = '00:00:00:00:00'
        tftp = SpokeTFTP(self.tftp_root)
        self.assertRaises(error.InputError, tftp.search, mac)

    def test_get_invalid_target(self):
        """Search for an invalid target; raise InputError."""
        target = 'du$$_lv'
        tftp = SpokeTFTP(self.tftp_root)
        self.assertRaises(error.InputError, tftp.search, target)

    def test_get_multiple_macs(self):
        """Search for all macs associated with target; return list."""        
        # macs should be returned as lower case, with s/:/- and with prefix
        mac1 = self.tftp_mac_prefix + '-' + '00-0c-29-57-3b-31'
        raw_mac2 = '00:00:00:00:00:02'
        mac2 = self.tftp_mac_prefix + '-' + '00-00-00-00-00-02'
        target = self.target 
        
        tftp = SpokeTFTP(self.tftp_root)
        tftp.create(raw_mac2, target)
        result = tftp.search(target=target)['data']
        expected_result = [{self.target:[mac2, mac1]}]
        self.assertEqual(result, expected_result)
        tftp.delete(raw_mac2)
        
    def test_get_all_macs_targets(self):
        """Search for all macs and targets; return list."""
        # macs should be returned as lower case, with s/:/- and with prefix
        mac1 = self.tftp_mac_prefix + '-' + '00-0c-29-57-3b-31'
        raw_mac3 = '00:00:00:00:00:03'
        mac3 = self.tftp_mac_prefix + '-' + '00-00-00-00-00-03'
        raw_mac4 = '00:00:00:00:00:04'
        mac4 = self.tftp_mac_prefix + '-' + '00-00-00-00-00-04'
        target = self.target
        target2 = 'newtarget'
        open(self.tftp_dir + target2, 'w').close()
        tftp = SpokeTFTP(self.tftp_root)
        tftp.create(raw_mac3, target2)
        tftp.create(raw_mac4, target2)
        result = tftp.search()['data']
        expected_result = [{target2 : [mac3, mac4] ,target : [mac1]}]
        self.assertEqual(result, expected_result)
        tftp.delete(raw_mac3)
        tftp.delete(raw_mac4)
        os.remove(self.tftp_dir + target2)

    def test_create_association(self):
        """Create association between mac and target; return results object."""
        mac = '00:00:00:00:00:02'
        mac_file = '01-00-00-00-00-00-02'
        tftp = SpokeTFTP(self.tftp_root)
        expected_result = [{mac_file: [self.target]}]
        result = tftp.create(mac, self.target)['data']
        self.assertEqual(result, expected_result)
        tftp.delete(mac)

    def test_create_existing_association(self):
        """Create existing association; raise AlreadyExists."""
        tftp = SpokeTFTP(self.tftp_root)
        self.assertRaises(error.AlreadyExists, tftp.create, 
                          self.mac, self.target)
        
    def test_create_association_with_missing_target(self):
        """Create association to missing target; raise NotFound."""
        mac = '00:00:00:00:00:03'
        target = 'missing'
        tftp = SpokeTFTP(self.tftp_root)
        self.assertRaises(error.NotFound, tftp.create, mac, target)    

    def test_create_invalid_mac(self):
        """Create an association with an invalid mac; raise InputError."""
        mac = '00:00:00:00:00'
        tftp = SpokeTFTP(self.tftp_root)
        self.assertRaises(error.InputError, tftp.search, mac)
        
    def test_create_invalid_target(self):
        """Create an association with an invalid target; raise InputError."""
        target = 'du$$_lv'
        tftp = SpokeTFTP(self.tftp_root)
        self.assertRaises(error.InputError, tftp.search, target)

    def test_delete_mac(self):
        """Delete an association with target; return True."""
        tftp = SpokeTFTP(self.tftp_root)
        self.assertTrue(tftp.delete(self.mac))
        tftp.create(self.mac, self.target)
        
    def test_delete_missing_mac(self):
        """Delete a missing association; raise NotFound."""
        mac = '00:00:00:00:00:02'
        tftp = SpokeTFTP(self.tftp_root)
        self.assertRaises(error.NotFound, tftp.delete, mac)

if __name__ == "__main__":
    unittest.main()
