"""Tests tftp.py module."""
# core modules
import os
import unittest
# own modules
import spoke.lib.error as error
import spoke.lib.config as config
from spoke.lib.tftp import SpokeTFTP

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
        self.template = 'testfile.template'
        self.run_id = 23123132
        self.tftp_dir = self.tftp_root + "/" + self.tftp_conf_dir + "/"
        
        
    def setUp(self):
        """Create test tftp file structure."""
        for d in self.tftp_root, self.tftp_dir:
            if not (os.path.exists(d)):
                try:
                    os.makedirs(d)
                except Exception as e:
                    raise e
        if not os.path.exists(self.tftp_dir + self.template):
            f = open(self.tftp_dir + self.template, 'w')
            f.write("default local\nkernel linux\nappend somearg=2")
            f.close
        tftp = SpokeTFTP(self.tftp_root)
        tftp.create(self.mac, self.template)
    
    def tearDown(self):
        """Delete test tftp file structure."""
        tftp = SpokeTFTP(self.tftp_root)
        tftp.delete(self.mac)
        if os.path.exists(self.tftp_dir + self.template):
            os.remove(self.tftp_dir + self.template)
        
        for d in self.tftp_dir, self.tftp_root:
            if (os.path.exists(d)):
                try:
                    os.removedirs(d)
                except Exception as e:
                    raise e
                
    def test_get_tftp_mac(self):
        """Search for a tftp mac config; return list."""
        # mac should be returned as lower case, with s/:/- and with prefix
        mac = self.tftp_mac_prefix + '-' + '00-0c-29-57-3b-31'
        tftp = SpokeTFTP(self.tftp_root)
        result = tftp.search(self.mac)['data']
        expected_result = [[mac]]
        self.assertEqual(result, expected_result) 

    def test_get_missing_mac(self):
        """Search for missing mac config; return empty list."""
        mac = '00:00:00:00:00:02'
        tftp = SpokeTFTP(self.tftp_root)
        result = tftp.search(mac)['data']
        expected_result = []
        self.assertEqual(result, expected_result)

    def test_get_missing_template(self):
        """Search for missing template; raise NotFound."""
        template = 'missing'
        tftp = SpokeTFTP(self.tftp_root)
        self.assertRaises(error.NotFound, tftp.search, template=template)

    def test_get_invalid_mac(self):
        """Search for an invalid mac; raise InputError."""
        mac = '00:00:00:00:00'
        tftp = SpokeTFTP(self.tftp_root)
        self.assertRaises(error.InputError, tftp.search, mac)

    def test_get_invalid_template(self):
        """Search for an invalid template; raise InputError."""
        template = 'du$$_lv'
        tftp = SpokeTFTP(self.tftp_root)
        self.assertRaises(error.InputError, tftp.search, template)

        
    def test_get_all_macs_templates(self):
        """Search for all macs and templates; return list."""
        # macs should be returned as lower case, with s/:/- and with prefix
        raw_mac1 = '00-0c-29-57-3b-31'
        raw_mac3 = '00-00-00-00-00-03'
        raw_mac4 = '00-00-00-00-00-04'
        template = self.template
        template2 = 'newtemplate.template'
        open(self.tftp_dir + template2, 'w').close()
        tftp = SpokeTFTP(self.tftp_root)
        tftp.create(raw_mac3, template2)
        tftp.create(raw_mac4, template2)
        result = tftp.search()['data']
        expected_result = [{'templates' : [template, template2], 'configs' : [raw_mac3, raw_mac4, raw_mac1]}]
        tftp.delete(raw_mac3)
        tftp.delete(raw_mac4)
        os.remove(self.tftp_dir + template2)
        self.assertEqual(result, expected_result)
        

    def test_create_association(self):
        """Create mac config with no run id; return results object."""
        mac = '00:00:00:00:00:02'
        mac_file = '01-00-00-00-00-00-02'
        tftp = SpokeTFTP(self.tftp_root)
        expected_result = [[mac_file]]
        result = tftp.create(mac, self.template)['data']
        tftp.delete(mac)
        self.assertEqual(result, expected_result)
        
    def test_create_association_runid(self):
        """Create mac config with run_id; return results object."""
        mac = '00:00:00:00:00:02'
        mac_file = '01-00-00-00-00-00-02'
        tftp = SpokeTFTP(self.tftp_root)
        expected_result = [[mac_file]]
        result = tftp.create(mac, self.template, self.run_id)['data']
        tftp.delete(mac)
        self.assertEqual(result, expected_result)
        
    def test_template_no_kernelargs(self):
        """Create mac config with bad template file contents; raises InputError."""
        tftp = SpokeTFTP(self.tftp_root)
        temp = open(self.tftp_dir + 'badtemplate.template', 'w')
        temp.write("default local\nkernel linux\n")
        temp.close
        self.assertRaises(error.InputError, tftp.create, self.mac, 'badtemplate.template', self.run_id)
        os.remove(self.tftp_dir + 'badtemplate.template')
        
    def test_invalid_runid(self):
        """Create mac config with invalid run_id; raises InputError."""
        run_id = 'alksdj'
        tftp = SpokeTFTP(self.tftp_root)
        self.assertRaises(error.InputError, tftp.create, self.mac, self.template, run_id)
        
    def test_create_existing_association(self):
        """Create existing mac config; raise AlreadyExists."""
        tftp = SpokeTFTP(self.tftp_root)
        self.assertRaises(error.AlreadyExists, tftp.create, 
                          self.mac, self.template)
       
    def test_create_association_with_missing_template(self):
        """Create mac config using missing template; raise NotFound."""
        mac = '00:00:00:00:00:03'
        template = 'missing'
        tftp = SpokeTFTP(self.tftp_root)
        self.assertRaises(error.NotFound, tftp.create, mac, template)
            
    def test_create_association_with_template_noext(self):
        """Create mac config using missing template; raise NotFound."""
        mac = '00:00:00:00:00:03'
        tftp = SpokeTFTP(self.tftp_root)
        open(self.tftp_dir + 'template.conf', 'w').close
        self.assertRaises(error.InputError, tftp.create, mac, 'template.conf')
        os.remove(self.tftp_dir + 'template.conf')
        
    def test_create_invalid_mac(self):
        """Create config with an invalid mac; raise InputError."""
        mac = '00:00:00:00:00'
        tftp = SpokeTFTP(self.tftp_root)
        self.assertRaises(error.InputError, tftp.search, mac)
        
    def test_create_invalid_template(self):
        """Create a config with an invalid template; raise InputError."""
        template = 'du$$_lv'
        tftp = SpokeTFTP(self.tftp_root)
        self.assertRaises(error.InputError, tftp.search, template)

    def test_delete_mac(self):
        """Delete a config; return True."""
        tftp = SpokeTFTP(self.tftp_root)
        self.assertTrue(tftp.delete(self.mac))
        tftp.create(self.mac, self.template)
        
    def test_delete_missing_mac(self):
        """Delete a missing config; raise NotFound."""
        mac = '00:00:00:00:00:02'
        tftp = SpokeTFTP(self.tftp_root)
        self.assertRaises(error.NotFound, tftp.delete, mac)

if __name__ == "__main__":
    unittest.main()
