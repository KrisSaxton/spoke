"""Tests Spoke ip.py module."""
# core modules
import unittest
# own modules
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.log as logger
from spoke.lib.ip import SpokeSubnet

class SpokeIPTest(unittest.TestCase):

    """A Class for testing the Spoke ip.py module."""
    
    def __init__(self, methodName):
        """Setup config data and redis connection."""
        unittest.TestCase.__init__(self, methodName)
        common_config = '../../contrib/spoke.conf'
        custom_config = '/tmp/spoke.conf'
        config_files = (common_config, custom_config)
        self.config = config.setup(config_files)
        self.log = logger.log_to_console()
        self.subnet = '192.168.1.0'
        self.mask = 24
        self.ip_ldap_key = self.config.get('IP', 'ip_ldap_key')
        
    def setUp(self): 
        sub = SpokeSubnet(self.subnet, self.mask)
        sub.create()

    def tearDown(self):
        sub = SpokeSubnet(self.subnet, self.mask)
        sub.delete()
    
    def test_create_subnet(self):
        """Create a subnet object; return results object."""
        subnet = '10.0.0.0'
        mask = 30
        expected_result = [(subnet, {'aloc': [0], 'free': [2]})]
        sub = SpokeSubnet(subnet, mask)
        result = sub.create()['data']
        self.assertEqual(result, expected_result)
        sub.delete()
        
    def test_create_subnet_too_large(self):
        """Create a subnet larger than /16; raise InputError"""
        subnet = '10.0.0.0'
        mask = 8
        sub = SpokeSubnet(subnet, mask)
        self.assertRaises(error.InputError, sub.create)
        
    def test_create_subnet_mask_string(self):
        """Create a subnet with a mask as string; return True"""
        subnet = '10.0.0.0'
        mask = '30'
        expected_result = [(subnet, {'aloc': [0], 'free': [2]})]
        sub = SpokeSubnet(subnet, mask)
        result = sub.create()['data']
        self.assertEqual(result, expected_result)
        sub.delete()
        
    def test_create_subnet_mask_dotted_decimal(self):
        """Create a subnet with a mask as dotted decimal; raise InputError"""
        subnet = '172.16.1.1'
        mask = '255.255.255.0'
        self.assertRaises(error.InputError, SpokeSubnet, subnet, mask)
        
    def test_create_invalid_subnet(self):
        """Create a subnet with an invalid subnet; raise InputError"""
        subnet = '192.16.1'
        mask = 30
        self.assertRaises(error.InputError, SpokeSubnet, subnet, mask)
        
    def test_create_subnet_with_dc_prefix(self):
        """Create a subnet with a data centre prefix; return True."""
        dc = 'dc1'
        subnet = '10.0.0.0'
        mask = 30
        expected_result = [(dc + subnet, {'aloc': [0], 'free': [2]})]
        sub = SpokeSubnet(subnet, mask, dc)
        result = sub.create()['data']
        self.assertEqual(result, expected_result)
        sub.delete()
        
    def test_get_subnet_ip_info(self):
        """Get a subnet's free and aloc IP status; return as list"""
        ip = '172.16.1.1'
        network = '172.16.1.0'
        mask = 24
        expected_result = [(network, {'free': [254], 'aloc': [0]})]
        sub = SpokeSubnet(ip, mask)
        sub.create()
        result = sub.get()['data']
        self.assertEqual(result, expected_result)
        sub.delete()
        
    def test_get_empty_subnet_ip_info(self):
        """Get a non-existent subnet's free/aloc IP status; return empty list"""
        ip = '172.16.3.1'
        mask = 24
        expected_result = []
        sub = SpokeSubnet(ip, mask)
        result = sub.get()['data']
        self.assertEqual(result, expected_result)
     
    def test_delete_subnet(self):
        """Delete a subnet; return True"""
        subnet = '172.16.4.1'
        mask = 24
        sub = SpokeSubnet(subnet, mask)
        sub.create()
        self.assertTrue(sub.delete())
        
    def test_delete_missing_subnet(self):
        """Delete a missing subnet; raise NotFound"""
        subnet = '172.16.5.1'
        mask = 24
        sub = SpokeSubnet(subnet, mask)
        self.assertRaises(error.NotFound, sub.delete)
        
    def test_len_reserve_single_ip_from_subnet(self):
        """Request an ip from a subnet; return a single IP address as list."""
        subnet = '172.16.1.1'
        mask = '30'
        sub = SpokeSubnet(subnet, mask)
        sub.create()
        result = sub.modify(reserve=1)['data']
        self.assertEquals(len(result), 1)
        sub.delete()
        
    def test_free_aloc_reserve_ip_from_subnet(self):
        """Request an ip from a subnet; verify free/aloc addresses."""
        ip = '172.16.1.1'
        network = '172.16.1.0'
        mask = '30'
        expected_result = [(network, {'free': [1], 'aloc': [1]})]
        sub = SpokeSubnet(ip, mask)
        sub.create()
        sub.modify(reserve=1)
        result = sub.get()['data']
        self.assertEqual(result, expected_result)
        sub.delete()
        
    def test_reserve_ip_from_exhausted_subnet(self):
        """Request an ip from an exhausted subnet; raise InsufficientResouce."""
        subnet = '172.16.1.1'
        mask = '30'
        sub = SpokeSubnet(subnet, mask)
        sub.create()
        self.assertRaises(error.InsufficientResource, sub.modify, reserve=3)
        sub.delete()
        
    def test_free_aloc_release_ip_from_subnet(self):
        """Release an ip from a subnet; verify free/aloc addresses."""
        ip = '172.16.1.1'
        network = '172.16.1.0'
        mask = '30'
        expected_result = [(network, {'free': [1], 'aloc': [1]})]
        sub = SpokeSubnet(ip, mask)
        sub.create()
        sub.modify(reserve=2)
        sub.modify(release='172.16.1.2')
        result = sub.get()['data']
        self.assertEqual(result, expected_result)
        sub.delete()
        
    def test_release_ip_from_subnet(self):
        """Release an ip from a subnet; return a results object."""
        subnet = '172.16.2.1'
        network = '172.16.2.0'
        mask = '30'
        expected_result = [(network, {'free': [1], 'aloc': [2]})]
        sub = SpokeSubnet(subnet, mask)
        sub.create()
        sub.modify(reserve=2)
        result = sub.modify(release='172.16.1.2')['data']
        self.assertEqual(result, expected_result)
        sub.delete()
    
    def test_release_ip_twice_from_subnet(self):
        """Release an ip twice from a subnet; return True."""
        ip = '172.16.2.1'
        mask = '30'
        sub = SpokeSubnet(ip, mask)
        sub.create()
        sub.modify(reserve=2)
        sub.modify(release='172.16.1.2')
        self.assertTrue(sub.modify(release='172.16.1.2'))
        sub.delete()
