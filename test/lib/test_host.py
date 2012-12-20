"""Tests host.py module."""
# core modules
import unittest
# own modules
import spoke.lib.error as error
import spoke.lib.config as config
from spoke.lib.org import SpokeOrg
from spoke.lib.host import SpokeHost
from spoke.lib.host import SpokeHostUUID

class SpokeHostTest(unittest.TestCase):
    
    def __init__(self, methodName):
        """Setup config data and LDAP connection."""
        unittest.TestCase.__init__(self, methodName)
        common_config = '../../contrib/spoke.conf'
        custom_config = '/tmp/spoke.conf'
        config_files = (common_config, custom_config)
        self.config = config.setup(config_files)
        self.base_dn = self.config.get('LDAP', 'basedn')
        self.search_scope = 2 # ldap.SCOPE_SUBTREE
        self.retrieve_attr = None
        self.org_name = 'spokehosttest'
        self.org_attr = self.config.get('ATTR_MAP', 'org_attr')
        self.org_def_children = self.config.get('ATTR_MAP', 'org_def_children')
        self.org_children = self.org_def_children.split(',')
        self.org_dn = '%s=%s,%s' % (self.org_attr, self.org_name, self.base_dn)
        self.container_attr = self.config.get('ATTR_MAP', 'container_attr')

        self.host_container = self.config.get('HOST', 'host_container')
        self.host_container_dn = '%s=%s,%s' % (self.container_attr, \
                                            self.host_container, self.org_dn)
        self.host_class = self.config.get('HOST', 'host_class')
        self.host_key = self.config.get('HOST', 'host_key')

        self.host_uuid_attr = self.config.get('HOST', 'host_uuid_attr')
        self.host_name_attr = self.config.get('HOST', 'host_name_attr')
        self.host_cpu_attr = self.config.get('HOST', 'host_cpu_attr')
        self.host_mem_attr = self.config.get('HOST', 'host_mem_attr')
        self.host_extra_opts_attr = self.config.get('HOST', 
                                                    'host_extra_opts_attr')
        self.host_family_attr = self.config.get('HOST', 'host_family_attr')
        self.host_network_layout_attr = self.config.get('HOST', 
                                                    'host_network_layout_attr')
        self.host_storage_layout_attr = self.config.get('HOST', 
                                                    'host_storage_layout_attr')
        self.host_type_attr = self.config.get('HOST', 'host_type_attr')
        self.next_uuid_attr = self.config.get('UUID', 'next_uuid_attr')
        self.next_uuid_dn = self.config.get('UUID', 'next_uuid_dn')
        self.next_uuid_start = self.config.get('UUID', 'next_uuid_start')
        
        self.host_name = 'testhost'
        self.host_uuid = '1'
        self.host_mem = '256'
        self.host_mem_kb = '%s' % (int(self.host_mem)*1024)
        self.host_cpu = '1'
        self.host_extra_opts = 'test'
        self.host_family = 'xen'
        self.host_storage_layout = 'basic'
        self.host_network_layout = 'with_internet'
        self.host_type = 'full'
        
    def setUp(self):
        """Create test organisation and host."""
        org = SpokeOrg()
        org.create(self.org_name, self.org_children)
        next_uuid = SpokeHostUUID()
        next_uuid.create(self.next_uuid_start)
        host = SpokeHost(self.org_name)
        host.create(self.host_name, self.host_uuid, self.host_mem, 
                    self.host_cpu,  self.host_family, self.host_type,
                    self.host_storage_layout,self.host_network_layout,  
                    self.host_extra_opts)
    
    def tearDown(self):
        """Delete test organisation and host"""
        host = SpokeHost(self.org_name)
        host.delete(self.host_name)
        org = SpokeOrg()
        org.delete(self.org_name, self.org_children)
        next_uuid = SpokeHostUUID()
        next_uuid.delete()

# UUID Tests       
    def test_get_missing_next_free_uuid(self):
        """Retrieve missing next free uuid; raise NotFound"""
        next_uuid = SpokeHostUUID()
        next_uuid.delete()
        next_uuid.__init__()
        self.assertRaises(error.NotFound, next_uuid.get)
        next_uuid.create(self.next_uuid_start)
        
    def test_create_next_free_uuid(self):
        """Create next free uuid; return uuid as list."""
        next_uuid = SpokeHostUUID()
        next_uuid.delete()
        # Re init so it detects the delete
        next_uuid.__init__()
        result = next_uuid.create(self.next_uuid_start)
        expected_data = [1]
        self.assertEqual(result['data'], expected_data)

    def test_create_next_free_uuid_mac(self):
        """Create next free uuid + mac; return as tuple."""
        next_uuid = SpokeHostUUID()
        next_uuid.delete()
        # Re init so it detects the delete
        next_uuid.__init__()
        result = next_uuid.create(self.next_uuid_start, get_mac=True)
        expected_data = (1, '02:00:00:01:00:00')
        self.assertEqual(result['data'], expected_data)
        
    def test_create_existing_free_uuid(self):
        """Create existing next free uuid; raise AlreadyExists."""
        next_uuid = SpokeHostUUID()
        self.assertRaises(error.AlreadyExists, next_uuid.create, 
                          self.next_uuid_start)
        
    def test_create_next_free_uuid_non_integer(self):
        """Create next free uuid with non integer; raise InputError."""
        next_uuid = SpokeHostUUID()
        next_uuid.delete()
        # Re init so it detects the delete
        next_uuid.__init__()
        next_uuid_start = 'three'
        self.assertRaises(error.InputError, next_uuid.create, next_uuid_start)
        next_uuid.create(self.next_uuid_start)
        
    def test_update_and_get_next_free_uuid(self):
        """Get next free uuid; return uuid as list."""
        next_uuid = SpokeHostUUID()
        result = next_uuid.modify()
        expected_data = [1]
        self.assertEquals(result['data'], expected_data)
        
    def test_update_and_get_next_free_uuid_mac(self):
        """Get next free uuid and mac; return as tuple."""
        next_uuid = SpokeHostUUID()
        result = next_uuid.modify(get_mac=True)
        expected_data = ([1], ['02:00:00:01:00:00'])
        self.assertEquals(result['data'], expected_data)
        
    def test_get_next_free_uuid(self):
        """Retrieve next free uuid; return uuid as list."""
        next_uuid = SpokeHostUUID()
        result = next_uuid.get()
        expected_data = [1]
        self.assertEquals(result['data'], expected_data)

    def test_increment_and_get_multiple_next_free_uuid(self):
        """Get next 4 free uuids; return uuids as list of integers."""
        next_uuid = SpokeHostUUID()
        result = next_uuid.modify(4)
        expected_data = [1, 2, 3, 4]
        self.assertEquals(result['data'], expected_data)
        
    def test_increment_and_get_multiple_next_free_uuid_and_mac(self):
        """Get next 4 free uuids and macs; return uuids as list of integers."""
        next_uuid = SpokeHostUUID()
        result = next_uuid.modify(4, get_mac=True)
        expected_data = ([1, 2, 3, 4], ['02:00:00:01:00:00', '02:00:00:02:00:00', '02:00:00:03:00:00', '02:00:00:04:00:00'])
        self.assertEquals(result['data'], expected_data)

    def test_update_next_free_uuid_with_string(self):
        """Increment next free UUID with string; raise InputError."""
        next_uuid = SpokeHostUUID()
        self.assertRaises(error.InputError, next_uuid.modify, 'four')
        
# Host Tests
    def test_get_all_hosts(self):
        """Retrieve all hosts; return list of hosts objects."""
        host_name = 'testhost2'

        expected_data = []
        for h in (self.host_name, host_name):
            rdn = '%s=%s' % (self.host_key, h)
            dn = '%s,%s' % (rdn, self.host_container_dn)
            dn_info = {
                   'objectClass': ['top', self.host_class],
                   self.host_cpu_attr: [self.host_cpu],
                   self.host_extra_opts_attr: [self.host_extra_opts],
                   self.host_family_attr: [self.host_family],
                   self.host_mem_attr: [self.host_mem_kb],
                   self.host_name_attr: [h],
                   self.host_network_layout_attr: [self.host_network_layout],
                   self.host_storage_layout_attr: [self.host_storage_layout],
                   self.host_type_attr: [self.host_type],
                   self.host_uuid_attr: [self.host_uuid],
                   self.host_key: [h]
                   }
            append_this = (dn, dn_info)
            expected_data.append(append_this)
        host = SpokeHost(self.org_name)
        host.create(host_name, self.host_uuid, self.host_mem, self.host_cpu, 
                    self.host_family, self.host_type, self.host_storage_layout, 
                    self.host_network_layout, self.host_extra_opts)
        result = host.get()
        self.assertEquals(result['data'], expected_data)
        host.delete(host_name)
        
    def test_get_host(self):
        """Retrieve host; return a host object."""
       
        rdn = '%s=%s' % (self.host_key, self.host_name)
        dn = '%s,%s' % (rdn, self.host_container_dn)
        dn_info = {
                   'objectClass': ['top', self.host_class],
                   self.host_cpu_attr: [self.host_cpu],
                   self.host_extra_opts_attr: [self.host_extra_opts],
                   self.host_family_attr: [self.host_family],
                   self.host_mem_attr: [self.host_mem_kb],
                   self.host_name_attr: [self.host_name],
                   self.host_network_layout_attr: [self.host_network_layout],
                   self.host_storage_layout_attr: [self.host_storage_layout],
                   self.host_type_attr: [self.host_type],
                   self.host_uuid_attr: [self.host_uuid],
                   self.host_key: [self.host_name]
                   }
        expected_data = [(dn, dn_info)]
        host = SpokeHost(self.org_name)
        result = host.get(self.host_name)
        self.assertEquals(result['data'], expected_data)
        
    def test_get_missing_host(self):
        """Retrieve a missing host account; return empty list."""
        host_name = 'missinghost'
        host = SpokeHost(self.org_name)
        result = host.get(host_name)
        expected_data = []
        self.assertEquals(result['data'], expected_data)
        
    def test_create_host_twice(self):
        """Create a host that already exists; raise AlreadyExists."""
        host = SpokeHost(self.org_name)
        self.assertRaises(error.AlreadyExists, host.create, self.host_name, 
                          self.host_uuid, self.host_mem, self.host_cpu,  
                          self.host_family, self.host_type,
                          self.host_storage_layout, self.host_network_layout,
                          self.host_extra_opts)
        
    def test_delete_host(self):
        """Delete host; return an empty search result."""
        host = SpokeHost(self.org_name)
        host_name = 'testhostdelete'
        host.create(host_name, self.host_uuid, self.host_mem, self.host_cpu,  
                          self.host_family, self.host_type, 
                          self.host_storage_layout, self.host_network_layout,  
                          self.host_extra_opts)
        expected_data = []
        result = host.delete(host_name)
        self.assertEquals(result['data'], expected_data)
    
    def test_delete_non_existant_host(self):
        """Delete non-existent host; raise MissingHost."""
        host = SpokeHost(self.org_name)
        host_name = 'testhostdeletemissing'
        self.assertRaises(error.NotFound, host.delete, host_name)
    
    def test_get_user_with_missing_org(self):
        """Retrieve a host with no org; raise NotFound."""
        org_name = 'SpokeMissingOrg'
        self.assertRaises(error.NotFound, SpokeHost, org_name)
        
    def test_create_host_with_invalid_host_name(self):
        """Create a host with an invalid hostname; raise InputError."""
        host = SpokeHost(self.org_name)
        host_name = 'invalid host'
        self.assertRaises(error.InputError, host.create, host_name, 
                          self.host_uuid, self.host_mem, self.host_cpu,  
                          self.host_family, self.host_type,
                          self.host_storage_layout, self.host_network_layout, 
                          self.host_extra_opts)
        
    def test_create_host_with_invalid_cpu(self):
        """Create a host with an invalid cpu value; raise InputError."""
        host = SpokeHost(self.org_name)
        host_name = 'validhost'
        host_cpu = 3
        self.assertRaises(error.InputError, host.create, host_name, 
                          self.host_uuid, self.host_mem, host_cpu,  
                          self.host_family, self.host_type, 
                          self.host_storage_layout, self.host_network_layout,  
                          self.host_extra_opts)
        
    def test_create_host_with_invalid_mem(self):
        """Create a host with an invalid memory value; raise InputError."""
        host = SpokeHost(self.org_name)
        host_name = 'validhost'
        host_mem = 10240
        self.assertRaises(error.InputError, host.create, host_name, 
                          self.host_uuid, host_mem, self.host_cpu,  
                          self.host_family, self.host_type, 
                          self.host_storage_layout, self.host_network_layout,
                          self.host_extra_opts)
        
    def test_create_host_with_invalid_type(self):
        """Create a host with an invalid type value; raise InputError."""
        host = SpokeHost(self.org_name)
        host_name = 'validhost'
        host_type = 'virtualbox'
        self.assertRaises(error.InputError, host.create, host_name, 
                          self.host_uuid, self.host_mem, self.host_cpu,  
                          self.host_family, host_type, self.host_storage_layout, 
                          self.host_network_layout, self.host_extra_opts)
        
    def test_create_host_with_invalid_family(self):
        """Create a host with an invalid family value; raise InputError."""
        host = SpokeHost(self.org_name)
        host_name = 'validhost'
        host_family = 'virtualbox'
        self.assertRaises(error.InputError, host.create, host_name, 
                          self.host_uuid, self.host_mem, self.host_cpu,  
                          host_family, self.host_type, self.host_storage_layout, 
                          self.host_network_layout, self.host_extra_opts)
        
    def test_create_host_with_invalid_extra_opts(self):
        """Create a host with an invalid extra opts value; raise InputError."""
        host = SpokeHost(self.org_name)
        host_name = 'validhost'
        host_extra_opts = 'thing; naughty'
        self.assertRaises(error.InputError, host.create, host_name, 
                          self.host_uuid, self.host_mem, self.host_cpu,  
                          self.host_family, self.host_type,
                          self.host_storage_layout, self.host_network_layout,
                          host_extra_opts)
        
    def test_create_host_with_invalid_uuid(self):
        """Create a host with an invalid uuid value; raise InputError."""
        host = SpokeHost(self.org_name)
        host_name = 'validhost'
        host_uuid = '00000000-0000-0000-0000-00000000001'
        self.assertRaises(error.InputError, host.create, host_name, 
                          host_uuid, self.host_mem, self.host_cpu,  
                          self.host_family, self.host_type, 
                          self.host_storage_layout,self.host_network_layout,  
                          self.host_extra_opts)
        
    def test_create_host_with_unkown_storage_layout(self):
        """Create a host with an unknown storage layout; raise InputError."""
        host = SpokeHost(self.org_name)
        host_name = 'validhost'
        host_storage_layout = 'supermagicsan'
        self.assertRaises(error.InputError, host.create, host_name, 
                          self.host_uuid, self.host_mem, self.host_cpu,  
                          self.host_family, self.host_type, host_storage_layout, 
                          self.host_network_layout, self.host_extra_opts)
        
    def test_create_host_with_unkown_network_layout(self):
        """Create a host with an unknown network layout; raise InputError."""
        host = SpokeHost(self.org_name)
        host_name = 'validhost'
        host_network_layout = 'infiniband'
        self.assertRaises(error.InputError, host.create, host_name, 
                          self.host_uuid, self.host_mem, self.host_cpu,  
                          self.host_family, self.host_type, 
                          self.host_storage_layout, host_network_layout,  
                          self.host_extra_opts)
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
