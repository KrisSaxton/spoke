"""Tests Spoke vm.py module."""
# core modules
import re
import unittest
# own modules
import spoke.lib.error as error
import spoke.lib.config as config
from spoke.lib.vm_storage import SpokeVMStorageXen
from spoke.lib.vm_power import SpokeVMPowerXen

class SpokeVMStorageTest(unittest.TestCase):

    """A Class for testing the Spoke vm.py module."""
    
    def __init__(self, methodName):
        """Setup config data and hypervisor connection."""
        unittest.TestCase.__init__(self, methodName)
        common_config = '../../contrib/spoke.conf'
        custom_config = '/tmp/spoke.conf'
        config_files = (common_config, custom_config)
        self.config = config.setup(config_files)
        self.hv_uri = 'test:///default'
        #self.xen_uuid_template = '00000000-0000-0000-0000-XXXXXXXXXXXX'
        self.vm_name = 'testhost'
        self.vm_uuid = '1'
        self.vm_mem = '256'
        self.vm_cpu = '1'
        self.vm_family = 'xen'
        self.vm_storage_layout = 'basic'
        self.vm_network_layout = 'with_internet'
        #self.vm_extra_opts = 'test'
        #self.vm_type = 'full'
        self.vm_install = True
        self.vm_disks=None
        self.vm_interfaces=None
        
    def setUp(self): 
        # A VM with a name of 'test' is always present with the test driver.
        pass

    def tearDown(self):
        pass
    
    def test_create_vm(self):
        """Create a virtual machine object; return True."""
        vm = SpokeVMStorageXen(self.hv_uri)
        self.assertTrue(vm.create(self.vm_name, self.vm_uuid, self.vm_mem, 
                                 self.vm_cpu, self.vm_family,
                                 self.vm_storage_layout, self.vm_network_layout, 
                                 self.vm_install, self.vm_disks,
                                 self.vm_interfaces))
        vm.conn.close()
        
    def test_create_vm_twice(self):
        """Create virtual machine twice; raise AlreadExists."""
        vm = SpokeVMStorageXen(self.hv_uri)
        vm.create(self.vm_name, self.vm_uuid, self.vm_mem, 
                                 self.vm_cpu, self.vm_family,
                                 self.vm_storage_layout, self.vm_network_layout, 
                                 self.vm_install, self.vm_disks,
                                 self.vm_interfaces)
        self.assertRaises(error.AlreadyExists, vm.create, self.vm_name, 
                                 self.vm_uuid, self.vm_mem, 
                                 self.vm_cpu, self.vm_family,
                                 self.vm_storage_layout, self.vm_network_layout, 
                                 self.vm_install, self.vm_disks,
                                 self.vm_interfaces)
        vm.conn.close()
         
    def test_get_vm(self):
        """Retrieve a virtual machine; return a vm object."""
        vm = SpokeVMStorageXen(self.hv_uri)
        vm_name = 'test'
        data = vm.get(vm_name)['data']
        # UUID is different each time so we need to strip it out
        ruuid = re.compile(r'<uuid.*?uuid>\n  ')
        result = ruuid.sub('', data[0])
        result = [result]
        expected_result = ["<domain type='test'>\n  <name>test</name>\n  <memory>8388608</memory>\n  <currentMemory>2097152</currentMemory>\n  <vcpu>2</vcpu>\n  <os>\n    <type arch='i686'>hvm</type>\n    <boot dev='hd'/>\n  </os>\n  <clock offset='utc'/>\n  <on_poweroff>destroy</on_poweroff>\n  <on_reboot>restart</on_reboot>\n  <on_crash>destroy</on_crash>\n  <devices>\n  </devices>\n</domain>\n"]
        self.assertEquals(result, expected_result)
        
    def test_get_all_vms(self):
        """Retrieve a virtual machine; return a vm object."""
        vm = SpokeVMStorageXen(self.hv_uri)
        vm_name = 'test2ndvm'
        vm.create(vm_name, self.vm_uuid, self.vm_mem, 
                                 self.vm_cpu, self.vm_family,
                                 self.vm_storage_layout, self.vm_network_layout, 
                                 self.vm_install, self.vm_disks,
                                 self.vm_interfaces)
        data = vm.get()['data']
        # UUID is different each time so we need to strip it out
        ruuid = re.compile(r'<uuid.*?uuid>\n  ')
        out = ruuid.sub('', data[0])
        result = [out, data[1]]
        expected_result = ["<domain type='test'>\n  <name>test</name>\n  <memory>8388608</memory>\n  <currentMemory>2097152</currentMemory>\n  <vcpu>2</vcpu>\n  <os>\n    <type arch='i686'>hvm</type>\n    <boot dev='hd'/>\n  </os>\n  <clock offset='utc'/>\n  <on_poweroff>destroy</on_poweroff>\n  <on_reboot>restart</on_reboot>\n  <on_crash>destroy</on_crash>\n  <devices>\n  </devices>\n</domain>\n", "<domain type='xen'>\n  <name>test2ndvm</name>\n  <uuid>00000000-0000-0000-0000-000000000001</uuid>\n  <memory>262144</memory>\n  <currentMemory>262144</currentMemory>\n  <vcpu>1</vcpu>\n  <bootloader>/usr/sbin/pypxeboot</bootloader>\n  <bootloader_args>--udhcpc=/usr/local/pkg/udhcp/sbin/udhcpc --interface=eth3 mac=02:00:00:01:00:00 --label=install-aethernet</bootloader_args>\n  <os>\n    <type arch='i686'>hvm</type>\n  </os>\n  <clock offset='utc'/>\n  <on_poweroff>destroy</on_poweroff>\n  <on_reboot>restart</on_reboot>\n  <on_crash>restart</on_crash>\n  <devices>\n    <emulator>/usr/lib/xen/bin/qemu-dm</emulator>\n    <disk type='block' device='disk'>\n      <driver name='phy'/>\n      <source dev='/dev/vg01/test2ndvm'/>\n      <target dev='hda' bus='ide'/>\n      <address type='drive' controller='0' bus='0' unit='0'/>\n    </disk>\n    <disk type='block' device='disk'>\n      <driver name='phy'/>\n      <source dev='/dev/vg02/test2ndvm'/>\n      <target dev='hdb' bus='ide'/>\n      <address type='drive' controller='0' bus='0' unit='1'/>\n    </disk>\n    <controller type='ide' index='0'/>\n    <interface type='bridge'>\n      <mac address='02:00:00:01:00:00'/>\n      <source bridge='eth3'/>\n      <script path='vif-bridge'/>\n      <target dev='vif-1.0'/>\n    </interface>\n    <interface type='bridge'>\n      <mac address='02:00:00:01:01:00'/>\n      <source bridge='eth0'/>\n      <script path='vif-bridge'/>\n      <target dev='vif-1.1'/>\n    </interface>\n    <console type='pty'>\n      <target type='xen' port='0'/>\n    </console>\n    <input type='mouse' bus='ps2'/>\n    <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0'/>\n    <video>\n      <model type='cirrus' vram='9216' heads='1'/>\n    </video>\n    <memballoon model='xen'/>\n  </devices>\n</domain>\n"]
        self.assertEquals(result, expected_result)
        
    def test_get_invalid_vm(self):
        """Retrieve an invalid vm; raise InputError."""
        vm_name = 'c*@t'
        vm = SpokeVMStorageXen(self.hv_uri)
        self.assertRaises(error.InputError, vm.get, vm_name) 
        
    def test_input_invalid_vm(self):
        """Retrieve an invalid vm; raise InputError."""
        vm_name = 'c*@t'
        vm = SpokeVMStorageXen(self.hv_uri)
        self.assertRaises(error.InputError, vm.get, vm_name)  

# This doesn't seem to work with the test libvirt driver
#    def test_delete_vm(self):
#        """Delete a virtual machine object; return True."""
#        vm_name = 'testdelete'
#        vm = SpokeVMStorageXen(self.hv_uri)
#        vm.create(vm_name, self.vm_uuid, self.vm_mem, 
#                                 self.vm_cpu, self.vm_family,
#                                 self.vm_storage_layout, self.vm_network_layout, 
#                                 self.vm_install, self.vm_disks,
#                                 self.vm_interfaces)
#        self.assertTrue(vm.delete(vm_name))
        
    def test_delete_running_vm(self):
        """Delete a running virtual machine object; raise VMRunning."""
        vm_name = 'test'
        vm = SpokeVMStorageXen(self.hv_uri)
        self.assertRaises(error.VMRunning, vm.delete, vm_name)
        
    def test_delete_missing_vm(self):
        """Delete a running virtual machine object; raise NotFound."""
        vm_name = 'missingvmtest'
        vm = SpokeVMStorageXen(self.hv_uri)
        self.assertRaises(error.NotFound, vm.delete, vm_name)
        
    def test_create_vm_with_invalid_vm_name(self):
        """Create a virtual machine object; return True."""
        vm_name = 'c*@t'
        vm = SpokeVMStorageXen(self.hv_uri)
        self.assertRaises(error.InputError, vm.create, vm_name, 
                          self.vm_uuid, self.vm_mem, self.vm_cpu, 
                          self.vm_family, self.vm_storage_layout,
                          self.vm_network_layout, self.vm_install, 
                          self.vm_disks, self.vm_interfaces)
        vm.conn.close()

    def test_create_vm_with_invalid_vm_uuid(self):
        """Create a vm object with an invalid uuid; raise InputError."""
        vm_uuid = 'c*@t'
        vm = SpokeVMStorageXen(self.hv_uri)
        self.assertRaises(error.InputError, vm.create, self.vm_name, 
                          vm_uuid, self.vm_mem, self.vm_cpu, 
                          self.vm_family, self.vm_storage_layout,
                          self.vm_network_layout, self.vm_install, 
                          self.vm_disks, self.vm_interfaces)
        vm.conn.close()
        
    def test_create_vm_with_invalid_vm_cpu(self):
        """Create a vm object with an invalid cpu; raise InputError."""
        vm_cpu = 'c*@t'
        vm = SpokeVMStorageXen(self.hv_uri)
        self.assertRaises(error.InputError, vm.create, self.vm_name, 
                          self.vm_uuid, self.vm_mem, vm_cpu, 
                          self.vm_family, self.vm_storage_layout,
                          self.vm_network_layout, self.vm_install, 
                          self.vm_disks, self.vm_interfaces)
        vm.conn.close()
        
    def test_create_vm_with_invalid_vm_mem(self):
        """Create a vm object with an invalid mem; raise InputError."""
        vm_mem = 'c*@t'
        vm = SpokeVMStorageXen(self.hv_uri)
        self.assertRaises(error.InputError, vm.create, self.vm_name, 
                          self.vm_uuid, vm_mem, self.vm_cpu, 
                          self.vm_family, self.vm_storage_layout,
                          self.vm_network_layout, self.vm_install, 
                          self.vm_disks, self.vm_interfaces)
        vm.conn.close()

    def test_create_vm_with_invalid_vm_family(self):
        """Create a vm object with an invalid family; raise InputError."""
        vm_family = 'c*@t'
        vm = SpokeVMStorageXen(self.hv_uri)
        self.assertRaises(error.InputError, vm.create, self.vm_name, 
                          self.vm_uuid, self.vm_mem, self.vm_cpu, 
                          vm_family, self.vm_storage_layout,
                          self.vm_network_layout, self.vm_install, 
                          self.vm_disks, self.vm_interfaces)
        vm.conn.close()

    def test_create_vm_with_invalid_network_layout(self):
        """Create a vm object with an invalid network layout;
         raise InputError."""
        vm_network_layout = 'c*@t'
        vm = SpokeVMStorageXen(self.hv_uri)
        self.assertRaises(error.InputError, vm.create, self.vm_name, 
                          self.vm_uuid, self.vm_mem, self.vm_cpu, 
                          self.vm_family, self.vm_storage_layout,
                          vm_network_layout, self.vm_install, 
                          self.vm_disks, self.vm_interfaces)
        vm.conn.close()
        
    def test_create_vm_with_invalid_storage_layout(self):
        """Create a vm object with an invalid storage layout;
         raise InputError."""
        vm_storage_layout = 'c*@t'
        vm = SpokeVMStorageXen(self.hv_uri)
        self.assertRaises(error.InputError, vm.create, self.vm_name, 
                          self.vm_uuid, self.vm_mem, self.vm_cpu, 
                          self.vm_family, vm_storage_layout,
                          self.vm_network_layout, self.vm_install, 
                          self.vm_disks, self.vm_interfaces)
        vm.conn.close()
        
# VM Power Tests
    def test_get_vm_power_status(self):
        """Retrieve virtual machine power status; return power status object."""
        vm_name = 'test'
        vm = SpokeVMPowerXen(self.hv_uri, vm_name)
        result = vm.get()['data'][0]['state']
        expected_result = 'On'
        self.assertEquals(result, expected_result)
        
    def test_poweron_vm_twice(self):
        """Power on a running virtual machine object; raise VMRunning"""
        vm_name = 'test'
        vm = SpokeVMPowerXen(self.hv_uri, vm_name)
        self.assertRaises(error.VMRunning, vm.create)
        
    def test_poweroff_vm(self):
        """Power off a running virtual machine object; return True"""
        vm_name = 'test'
        vm = SpokeVMPowerXen(self.hv_uri, vm_name)
        self.assertTrue(vm.delete)
        
    def test_poweroff_stopped_vm(self):
        """Power off a non-running virtual machine object; raise VMStopped"""
        vm_name = 'test'
        vm = SpokeVMPowerXen(self.hv_uri, vm_name)
        vm.delete()
        self.assertRaises(error.VMStopped, vm.delete)
        
    def test_force_poweroff_vm(self):
        """Force power off a running virtual machine object; return True"""
        vm_name = 'test'
        vm = SpokeVMPowerXen(self.hv_uri, vm_name)
        self.assertTrue(vm.delete(force=True))
 
# This test does't work with libvirt test driver as the test VM is never really
# shutdown        
#    def test_force_poweroff_stopped_vm(self):
#        """Force power off a non-running virtual machine; raise VMStopped"""
#        vm_name = 'test'
#        vm = SpokeVMPowerXen(self.hv_uri, vm_name)
#       vm.delete()
#        self.assertRaises(error.VMStopped, vm.delete, force=True)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
