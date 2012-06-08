"Tests Spoke xml_helper.py module."""
import unittest

import config
import xml_helper

class SpokeXMLTest(unittest.TestCase):

    """A Class for testing the Spoke xml_helper.py module."""
    
    def __init__(self, methodName):
        """Setup config data."""
        unittest.TestCase.__init__(self, methodName)
        common_config = '../../contrib/spoke.conf'
        custom_config = '/tmp/spoke.conf'
        config_files = (common_config, custom_config)
        self.config = config.setup(config_files)
        self.vm1 = '''<domain type='xen'>
  <name>webmail01</name>
  <uuid>00000000-0000-0000-0006-000000000000</uuid>
  <memory>524288</memory>
  <currentMemory>262144</currentMemory>
  <vcpu>1</vcpu>
  <bootloader>/usr/bin/pygrub</bootloader>
  <bootloader_args>-q</bootloader_args>
  <os>
    <type>linux</type>
  </os>
  <clock offset='utc'/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <devices>
    <emulator>/usr/lib/xen/bin/qemu-dm</emulator>
    <disk type='block' device='disk'>
      <driver name='phy'/>
      <source dev='/dev/vg01/webmail01'/>
      <target dev='hda' bus='ide'/>
    </disk>
    <interface type='bridge'>
      <mac address='00:16:3e:af:00:00'/>
      <source bridge='eth3'/>
      <script path='vif-bridge'/>
      <target dev='vif-1.0'/>
    </interface>
    <interface type='bridge'>
      <mac address='00:16:3e:af:01:00'/>
      <source bridge='eth0'/>
      <script path='vif-bridge'/>
      <target dev='vif-1.1'/>
    </interface>
    <console type='pty'>
      <target type='xen' port='0'/>
    </console>
    <input type='mouse' bus='xen'/>
    <graphics type='vnc' port='5906' autoport='no' listen='0.0.0.0'/>
  </devices>
</domain>'''
        self.vm2 = '''<domain type='xen'>
  <name>wiki01</name>
  <uuid>00000000-0000-0000-0009-000000000000</uuid>
  <memory>524288</memory>
  <currentMemory>65536</currentMemory>
  <vcpu>1</vcpu>
  <bootloader>/usr/bin/pygrub</bootloader>
  <bootloader_args>-q</bootloader_args>
  <os>
    <type>linux</type>
  </os>
  <clock offset='utc'/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <devices>
    <emulator>/usr/lib/xen/bin/qemu-dm</emulator>
    <disk type='block' device='disk'>
      <driver name='phy'/>
      <source dev='/dev/vg01/wiki01'/>
      <target dev='hda' bus='ide'/>
    </disk>
    <interface type='bridge'>
      <mac address='00:16:3e:b2:00:00'/>
      <source bridge='eth3'/>
      <script path='vif-bridge'/>
      <target dev='vif-1.0'/>
    </interface>
    <interface type='bridge'>
      <mac address='00:16:3e:b2:00:01'/>
      <source bridge='eth0'/>
      <script path='vif-bridge'/>
      <target dev='vif-1.1'/>
    </interface>
    <console type='pty'>
      <target type='xen' port='0'/>
    </console>
    <input type='mouse' bus='xen'/>
    <graphics type='vnc' port='5909' autoport='no' listen='0.0.0.0'/>
  </devices>
</domain>'''
        self.vm_list = [self.vm1, self.vm2]
        self.text = '''name       uuid                                 
webmail01  00000000-0000-0000-0006-000000000000 
wiki01     00000000-0000-0000-0009-000000000000 
'''
        
    def setUp(self): 
        pass

    def tearDown(self):
        pass
    
    def test_xml_to_text(self):
        """Take XML document; return human-readable test."""
        headers = ['name', 'uuid']
        result = xml_helper.xml_to_text(self.vm_list, headers)
        self.assertEqual(result, self.text)
        
