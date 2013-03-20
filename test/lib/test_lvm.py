"""Tests lvm.py module.
NB This isn't really a set of unit tests, these are integration tests.
The tests touch the filesystem, so use with extreme caution
They require a system with LVM2 support and the lVM2 user land tools
They also expect a single volume group with at least 1G of free space"""
# core modules
import sys
import unittest
import decimal
# own modules
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.log as logger
from spoke.lib.lvm import SpokeLVM

# This volume group must exist, be empty and have at least 1G of free space
# before running these tests
test_vg_name = 'testvg01'

class SpokeLVMTest(unittest.TestCase):
    
    def __init__(self, methodName):
        """Setup config data."""
        unittest.TestCase.__init__(self, methodName)
        common_config = '../../contrib/spoke.conf'
        custom_config = '/tmp/spoke.conf'
        config_files = (common_config, custom_config)
        self.config = config.setup(config_files)
        self.log = logger.log_to_console()
        self.lv_units = self.config.get('LVM', 'lv_units')
        self.lv_name = 'testlv01'
        self.lv_size = 1
        self.TWOPLACES = decimal.Decimal(10) ** -2  # same as Decimal('0.01')
        self.lv_size_dec = str(decimal.Decimal(self.lv_size).quantize(self.TWOPLACES))
        self.lv_size_fmt = self.lv_size_dec + self.lv_units.upper()
        self.vg_name = test_vg_name
        # If we don't get an empty volume group here, abort
        try:
            self.lvm = SpokeLVM(self.vg_name)
            lv_list = self.lvm.get()['data']
        except Exception, e:
            print 'Exception'
            print e
            sys.exit(1)
        if lv_list != []:
            print 'Volume group %s is not empty' % self.vg_name
            sys.exit(1)
        
    def setUp(self):
        """Create test lvm."""
        self.lvm.create(self.lv_name, self.lv_size)
    
    def tearDown(self):
        """Delete test lvm"""
        self.lvm.delete(self.lv_name)
    
    def test_get_lv(self):
        """Search for an LV; return list."""
        result = self.lvm.get(self.lv_name)['data']
        expected_result = [{'lv_size':self.lv_size_fmt,'lv_name':self.lv_name}]
        self.assertEqual(result, expected_result) 

    def test_get_missing_lv(self):
        """Search for missing LV; return empty list."""
        lv_name = 'missing_lv'
        result = self.lvm.get(lv_name)['data']
        expected_result = []
        self.assertEqual(result, expected_result)

    def test_get_missing_vg(self):
        """Search for an LV in a missing VG; raise MissingLVGroup."""
        vg_name = 'missing_vg'
        lvm = SpokeLVM(vg_name)
        self.assertRaises(error.NotFound, lvm.get, self.lv_name)

    def test_get_invalid_lv(self):
        """Search for an LV with an invalid name; raise InputError."""
        lv_name = 'du$$_lv'
        lvm = SpokeLVM(self.vg_name)
        self.assertRaises(error.InputError, lvm.get, lv_name)

    def test_get_invalid_vg(self):
        """Search for an LV with an invalid VG name; raise InputError."""
        vg_name = 'du$$_lv'
        self.assertRaises(error.InputError, SpokeLVM, vg_name)

    def test_get_multiple_lvs(self):
        """Search for all LVs; return list."""
        lv_name = 'testlv02'
        lv_size = 2
        lv_size_dec = str(decimal.Decimal(lv_size).quantize(self.TWOPLACES))
        lv_size_fmt = lv_size_dec + self.lv_units.upper()
        lvm = SpokeLVM(self.vg_name)
        lvm.create(lv_name, lv_size)
        result = lvm.get()['data']
        expected_result = [{'lv_size':self.lv_size_fmt,
                            'lv_name':self.lv_name},
                           {'lv_size': lv_size_fmt,
                            'lv_name': lv_name}]
        self.assertEqual(result, expected_result)
        lvm.delete(lv_name)

    def test_create_lv(self):
        """Create LV; return results object."""
        lv_name = 'testlv03'
        lv_size = 1
        expected_result = [{'lv_size':self.lv_size_fmt,'lv_name':lv_name}]
        lvm = SpokeLVM(self.vg_name)
        result = lvm.create(lv_name, lv_size)['data']
        self.assertEqual(result, expected_result)
        lvm.delete(lv_name)

    def test_create_existing_lv(self):
        """Create existing LV; raise AlreadyExists."""
        lvm = SpokeLVM(self.vg_name)
        self.assertRaises(error.AlreadyExists, lvm.create, self.lv_name, self.lv_size)

    def test_create_invalid_lv(self):
        """Create an LV with an invalid name; raise InputError."""
        lv_name = 'du$$_lv'
        lvm = SpokeLVM(self.vg_name)
        self.assertRaises(error.InputError, lvm.create, lv_name, self.lv_size)

    def test_create_invalid_size_lv(self):
        """Create an LV with an invalid size; raise InputError."""
        lv_name = 'testlv04'
        lv_size = 1000
        lvm = SpokeLVM(self.vg_name)
        self.assertRaises(error.InputError, lvm.create, lv_name, lv_size)

    def test_create_too_large_lv(self):
        """Create an LV with size greater than in VG; raise InsufficientResource."""
        lv_name = 'testlv05'
        lv_size = 100
        lvm = SpokeLVM(self.vg_name)
        self.assertRaises(error.InsufficientResource, lvm.create, lv_name, lv_size)

    def test_delete_lv(self):
        """Delete an LV; return True."""
        lv_name = 'testlv06'
        lv_size = 1
        lvm = SpokeLVM(self.vg_name)
        lvm.create(lv_name, lv_size)
        self.assertFalse(lvm.delete(lv_name)['data'])

    def test_delete_missing_lv(self):
        """Delete a missing LV; raise NotFound."""
        lv_name = 'testlv07'
        lvm = SpokeLVM(self.vg_name)
        self.assertRaises(error.NotFound, lvm.delete, lv_name)

    def test_delete_invalid_lv(self):
        lv_name = 'du$$_lv'
        lvm = SpokeLVM(self.vg_name)
        self.assertRaises(error.InputError, lvm.delete, lv_name)

if __name__ == "__main__":
    unittest.main()
