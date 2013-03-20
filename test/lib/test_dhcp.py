"""Tests Spoke dhcp.py module.
TODO match tests to full results object instead of just result['data']
TODO match delete tests to results object instead of True/False."""
# core modules
import unittest
# own modules
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.log as logger
from spoke.lib.dhcp import SpokeDHCPServer
from spoke.lib.dhcp import SpokeDHCPService
from spoke.lib.dhcp import SpokeDHCPSubnet
from spoke.lib.dhcp import SpokeDHCPGroup
from spoke.lib.dhcp import SpokeDHCPHost
from spoke.lib.dhcp import SpokeDHCPAttr

class SpokeDHCPTest(unittest.TestCase):
    
    """A class for testing the Spoke dhcp.py module."""
    
    def __init__(self, methodName):
        """Setup config data and LDAP connection."""
        unittest.TestCase.__init__(self, methodName)
        common_config = '../../contrib/spoke.conf'
        custom_config = '/tmp/spoke.conf'
        config_files = (common_config, custom_config)
        self.config = config.setup(config_files)
        self.log = logger.log_to_console()
        self.org_name = 'SpokeOrgTest'
        self.base_dn = self.config.get('DHCP', 'dhcp_basedn')
        self.search_scope = 2 # ldap.SUB
        self.retrieve_attr = None
        self.dhcp_server_class = 'dhcpServer'
        self.dhcp_service_class = 'dhcpService'
        self.dhcp_subnet_class = 'dhcpSubnet'
        self.dhcp_options_class = 'dhcpOptions'
        self.dhcp_group_class = 'dhcpGroup'
        self.dhcp_host_class = 'dhcpHost'
        self.dhcp_option_attr = 'dhcpOption'
        self.dhcp_statement_attr = 'dhcpStatement'
        self.dhcp_mac_attr = 'dhcpHWAddress'
        self.dhcp_conf_suffix = self.config.get('DHCP', 'dhcp_conf_suffix')
        self.dhcp_server = 'test.dhcp.server.local'
        self.dhcp_group = 'testgroup'
        self.dhcp_host = 'testhost'
            
    def setUp(self):
        server = SpokeDHCPServer()
        server.create(self.dhcp_server)
        dhcp = SpokeDHCPService()
        dhcp.create(self.dhcp_server)
        group = SpokeDHCPGroup(self.dhcp_server)
        group.create(self.dhcp_group)
        host = SpokeDHCPHost(self.dhcp_server, self.dhcp_group)
        host.create(self.dhcp_host)

    def tearDown(self):
        host = SpokeDHCPHost(self.dhcp_server, self.dhcp_group)
        host.delete(self.dhcp_host)
        group = SpokeDHCPGroup(self.dhcp_server)
        group.delete(self.dhcp_group)
        dhcp = SpokeDHCPService()
        dhcp.delete(self.dhcp_server)
        server = SpokeDHCPServer()
        server.delete(self.dhcp_server)
        
    # DHCP Server tests
    def test_create_dhcp_server(self):
        """Create DHCP server; return True."""
        dhcp_server = 'testcreate.dhcp.server.local'
        dhcp = SpokeDHCPServer()
        result = dhcp.create(dhcp_server)['data']
        dn = 'cn=%s,%s' % (dhcp_server, self.base_dn)
        service_name = dhcp_server + self.dhcp_conf_suffix
        service_dn = 'cn=%s,%s' % (service_name, self.base_dn)
        dn_info = {'objectClass': ['top', self.dhcp_server_class],
                   'cn': [dhcp_server],
                   'dhcpServiceDN': [service_dn]}
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        dhcp.delete(dhcp_server)
    
    def test_create_dhcp_server_twice(self):
        """Create DHCP server twice; raise AlreadyExists."""
        dhcp = SpokeDHCPServer()
        self.assertRaises(error.AlreadyExists, dhcp.create, self.dhcp_server)
        
    def test_get_dhcp_server(self):
        """Fetch DHCP server; return True."""
        dhcp_server = 'testget.dhcp.server.local'
        dhcp = SpokeDHCPServer()
        dhcp.create(dhcp_server)
        result = dhcp.get(dhcp_server)['data']
        dn = 'cn=%s,%s' % (dhcp_server, self.base_dn)
        service_name = dhcp_server + self.dhcp_conf_suffix
        service_dn = 'cn=%s,%s' % (service_name, self.base_dn)
        dn_info = {'objectClass': ['top', self.dhcp_server_class],
                   'cn': [dhcp_server],
                   'dhcpServiceDN': [service_dn]}
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        dhcp.delete(dhcp_server)
        
    def test_get_missing_dhcp_server(self):
        """Fetch missing DHCP server; return empty list."""
        dhcp_server = 'testgetmissing.dhcp.server.local'
        dhcp = SpokeDHCPServer()
        result = dhcp.get(dhcp_server)['data']
        expected_result = []
        self.assertEqual(result, expected_result)
    
    def test_delete_dhcp_server(self):
        """Delete DHCP server; return True."""
        dhcp_server = 'testdelete.dhcp.server.local'
        dhcp = SpokeDHCPServer()
        dhcp.create(dhcp_server)
        self.assertTrue(dhcp.delete(dhcp_server))
        
    def test_delete_missing_dhcp_server(self):
        """Delete missing DHCP server; raise NotFound."""
        dhcp_server = 'testdeletemissing.dhcp.server.local'
        dhcp = SpokeDHCPServer()
        self.assertRaises(error.NotFound, dhcp.delete, dhcp_server)
    
    # DHCP Service Tests    
    def test_create_dhcp_service(self):
        """Create DHCP service; return result object."""
        dhcp_server = 'testcreate.dhcp.service.local'
        dhcp = SpokeDHCPService()
        result = dhcp.create(dhcp_server)['data']
        service_name = dhcp_server + self.dhcp_conf_suffix
        dn = 'cn=%s,%s' % (service_name, self.base_dn)
        primary_dn = 'cn=%s,%s' % (dhcp_server, self.base_dn)
        dn_info = {'objectClass': ['top', self.dhcp_service_class,
                                   self.dhcp_options_class],
                   'cn': [service_name],
                   'dhcpPrimaryDN': [primary_dn]}
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        dhcp.delete(dhcp_server)
        
    def test_create_dhcp_service_twice(self):
        """Create DHCP service twice; raise AlreadyExists."""
        dhcp_server = 'testcreatettwice.dhcp.service.local'
        dhcp = SpokeDHCPService()
        dhcp.create(dhcp_server)
        self.assertRaises(error.AlreadyExists, dhcp.create, dhcp_server)      
        dhcp.delete(dhcp_server)
        
    def test_get_dhcp_service(self):
        """Fetch DHCP service; return DHCP service objects."""
        dhcp_server = 'testget.dhcp.service.local'
        dhcp = SpokeDHCPService()
        dhcp.create(dhcp_server)
        result = dhcp.get(dhcp_server)['data']
        service_name = dhcp_server + self.dhcp_conf_suffix
        dn = 'cn=%s,%s' % (service_name, self.base_dn)
        primary_dn = 'cn=%s,%s' % (dhcp_server, self.base_dn)
        dn_info = {'objectClass': ['top', self.dhcp_service_class,
                                   self.dhcp_options_class],
                   'cn': [service_name],
                   'dhcpPrimaryDN': [primary_dn]}
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        dhcp.delete(dhcp_server)
        
    def test_get_missing_dhcp_service(self):
        """Fetch missing DHCP service; return empty list."""
        dhcp_server = 'testgetmissing.dhcp.service.local'
        dhcp = SpokeDHCPService()
        result = dhcp.get(dhcp_server)['data']
        expected_result = []
        self.assertEqual(result, expected_result)
        
    def test_delete_dhcp_service(self):
        """Delete DHCP service, return empty results object."""
        dhcp_server = 'testdelete.dhcp.service.local'
        dhcp = SpokeDHCPService()
        dhcp.create(dhcp_server)
        self.assertTrue(dhcp.delete(dhcp_server))
        
    def test_delete_missing_dhcp_service(self):
        """Delete missing DHCP service; raise NotFound."""
        dhcp_server = 'testdeletemissing.dhcp.service.local'
        dhcp = SpokeDHCPService()
        self.assertRaises(error.NotFound, dhcp.delete, dhcp_server)
        
    def test_delete_dhcp_service_before_subnet(self):
        """Delete DHCP service while subnet present, raise SaveTheBabies."""
        dhcp_server = 'deletechildren.dhcp.service.local'
        dhcp = SpokeDHCPService()
        dhcp.create(dhcp_server)
        subnet = '10.0.0.0'
        mask = '16'
        sub = SpokeDHCPSubnet(dhcp_server)
        sub.create(subnet, mask)
        self.assertRaises(error.SaveTheBabies, dhcp.delete, dhcp_server)
        sub.delete(subnet)
        dhcp.delete(dhcp_server)
        
    def test_create_dhcp_subnet(self):
        """Create DHCP subnet; return True."""
        subnet = '10.0.0.0'
        subnet_mask = '16'
        sub = SpokeDHCPSubnet(self.dhcp_server)
        result = sub.create(subnet, subnet_mask)['data']
        service_name = self.dhcp_server + self.dhcp_conf_suffix
        service_dn = 'cn=%s,%s' % (service_name, self.base_dn)
        dn = 'cn=%s,%s' % (subnet, service_dn)
        dn_info = {'objectClass': ['top', self.dhcp_subnet_class],
                   'cn': [subnet],
                   'dhcpNetMask': [subnet_mask]}
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        sub.delete(subnet)
        
    def test_create_dhcp_subnet_twice(self):
        """Create DHCP subnet twice; raise AlreadyExists."""
        subnet = '10.0.0.0'
        subnet_mask = '16'
        sub = SpokeDHCPSubnet(self.dhcp_server)
        sub.create(subnet, subnet_mask)
        self.assertRaises(error.AlreadyExists, sub.create, subnet, subnet_mask)
        sub.delete(subnet)
        
    def test_create_dhcp_subnet_with_missing_service(self):
        """Create DHCP subnet with missing service; raise NotFound"""
        dhcp_server = 'missing.dhcp.service.local'
        self.assertRaises(error.NotFound, SpokeDHCPSubnet, 
                          dhcp_server)
        
    def test_create_dhcp_subnet_with_invalid_subnet(self):
        """Create DHCP subnet with non-IP subnet; raise InputError."""
        subnet = '10.0.0'
        subnet_mask = '16'
        sub = SpokeDHCPSubnet(self.dhcp_server)
        self.assertRaises(error.InputError, sub.create, subnet, subnet_mask)
        
    def test_create_dhcp_subnet_with_invalid_mask(self):
        """Create DHCP subnet with non-integer mask; raise InputError."""
        subnet = '10.0.0.0'
        subnet_mask = '255.0.0.0'
        sub = SpokeDHCPSubnet(self.dhcp_server)
        self.assertRaises(error.InputError,sub.create, subnet, subnet_mask)
        
    def test_create_dhcp_subnet_with_integer_mask(self):
        """Create DHCP subnet with integer mask; return True."""
        subnet = '10.0.0.0'
        subnet_mask = 16
        sub = SpokeDHCPSubnet(self.dhcp_server)
        result = sub.create(subnet, subnet_mask)['data']
        service_name = self.dhcp_server + self.dhcp_conf_suffix
        service_dn = 'cn=%s,%s' % (service_name, self.base_dn)
        dn = 'cn=%s,%s' % (subnet, service_dn)
        dn_info = {'objectClass': ['top', self.dhcp_subnet_class],
                   'cn': [subnet],
                   'dhcpNetMask': [str(subnet_mask)]}
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        sub.delete(subnet)
        
    def test_create_dhcp_subnet_with_range(self):
        """Create DHCP subnet with IP range; return True."""
        subnet = '10.0.0.0'
        mask = '16'
        start_ip = '10.0.0.1'
        stop_ip = '10.0.0.254'
        subnet_range = start_ip + ' ' + stop_ip
        sub = SpokeDHCPSubnet(self.dhcp_server)
        result = sub.create(subnet, mask, start_ip, stop_ip)['data']
        service_name = self.dhcp_server + self.dhcp_conf_suffix
        service_dn = 'cn=%s,%s' % (service_name, self.base_dn)
        dn = 'cn=%s,%s' % (subnet, service_dn)
        dn_info = {'objectClass': ['top', self.dhcp_subnet_class],
                   'cn': [subnet],
                   'dhcpNetMask': [str(mask)],
                   'dhcpRange': [subnet_range]}
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        sub.delete(subnet)
        
    def test_create_dhcp_subnet_with_non_ip_range(self):
        """Create DHCP subnet with non IP range; raise InputError."""
        subnet = '10.0.0.0'
        subnet_mask = '16'
        start_ip = '10.0.0'
        stop_ip = '10.0.0.254'
        sub = SpokeDHCPSubnet(self.dhcp_server)
        self.assertRaises(error.InputError, sub.create, subnet, subnet_mask, 
                          start_ip, stop_ip)
        
    def test_create_dhcp_subnet_with_missing_stop_ip(self):
        """Create DHCP subnet with no stop IP; raise InputError."""
        subnet = '10.0.0.0'
        subnet_mask = '16'
        start_ip = '10.0.0.1'
        sub = SpokeDHCPSubnet(self.dhcp_server)
        self.assertRaises(error.InputError, sub.create, subnet, subnet_mask, 
                          start_ip)

    def test_create_dhcp_subnet_with_stop_ip_preceding_start_ip(self):
        """Create DHCP subnet with the stop IP preceding the start ip; \
        raise InputError."""
        subnet = '10.0.0.0'
        subnet_mask = '16'
        start_ip = '10.0.2.25'
        stop_ip = '10.0.1.250'
        sub = SpokeDHCPSubnet(self.dhcp_server)
        self.assertRaises(error.InputError, sub.create, subnet, subnet_mask, 
                          start_ip, stop_ip)
    
    def test_get_dhcp_subnet(self):
        """Fetch DHCP subnet; return True."""
        subnet = '10.0.0.0'
        mask = '16'
        start_ip = '10.0.0.1'
        stop_ip = '10.0.0.254'
        subnet_range = start_ip + ' ' + stop_ip
        sub = SpokeDHCPSubnet(self.dhcp_server)
        result = sub.create(subnet, mask, start_ip, stop_ip)['data']
        service_name = self.dhcp_server + self.dhcp_conf_suffix
        service_dn = 'cn=%s,%s' % (service_name, self.base_dn)
        dn = 'cn=%s,%s' % (subnet, service_dn)
        dn_info = {'objectClass': ['top', self.dhcp_subnet_class],
                   'cn': [subnet],
                   'dhcpNetMask': [str(mask)],
                   'dhcpRange': [subnet_range]}
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        sub.delete(subnet)
        
    def test_get_missing_dhcp_subnet(self):
        """Fetch missing DHCP subnet; return empty list."""
        subnet = '192.168.0.0'
        sub = SpokeDHCPSubnet(self.dhcp_server)
        result = sub.get(subnet)['data']
        expected_result = []
        self.assertEqual(result, expected_result)

    def test_get_invalid_dhcp_subnet(self):
        """Fetch DHCP invalid subnet; raise InputError."""
        subnet = '10.0.0'
        sub = SpokeDHCPSubnet(self.dhcp_server)
        self.assertRaises(error.InputError, sub.get, subnet)
        
    def test_delete_dhcp_subnet(self):
        """Delete DHCP subnet, return True."""
        subnet = '172.16.1.0'
        mask = '8'
        sub = SpokeDHCPSubnet(self.dhcp_server)
        sub.create(subnet, mask)
        self.assertTrue(sub.delete(subnet))
        
    def test_delete_missing_dhcp_subnet(self):
        """Delete missing DHCP subnet; raise NotFound."""
        # This should be deleted when the instantiation raises the error.
        subnet = '172.16.2.0'
        sub = SpokeDHCPSubnet(self.dhcp_server)
        self.assertRaises(error.NotFound, sub.delete, subnet)
        
    def test_create_dhcp_group(self):
        """Create DHCP group; return results object."""
        group_name = 'testcreategroup'
        group = SpokeDHCPGroup(self.dhcp_server)
        result = group.create(group_name)['data']
        service_name = self.dhcp_server + self.dhcp_conf_suffix
        conf_base_dn = 'cn=%s,%s' % (service_name, self.base_dn)
        dn = 'cn=%s,%s' % (group_name, conf_base_dn)
        dn_info = {'objectClass': ['top', self.dhcp_group_class,
                                   self.dhcp_options_class],
                   'cn': [group_name]}
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        group.delete(group_name)
    
    def test_create_dhcp_group_twice(self):
        """Create DHCP group twice; raise AlreadyExists."""
        group_name = 'testcreategroup'
        group = SpokeDHCPGroup(self.dhcp_server)
        group.create(group_name)
        self.assertRaises(error.AlreadyExists, group.create, group_name)
        group.delete(group_name)
        
    def test_get_dhcp_group(self):
        """Fetch DHCP group; return True."""
        group_name = 'testgetgroup'
        group = SpokeDHCPGroup(self.dhcp_server)
        group.create(group_name)
        result = group.get(group_name)['data']
        service_name = self.dhcp_server + self.dhcp_conf_suffix
        conf_base_dn = 'cn=%s,%s' % (service_name, self.base_dn)
        dn = 'cn=%s,%s' % (group_name, conf_base_dn)
        dn_info = {'objectClass': ['top', self.dhcp_group_class,
                                   self.dhcp_options_class],
                   'cn': [group_name]}
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        group.delete(group_name)
        
    def test_get_missing_dhcp_group(self):
        """Fetch missing DHCP group; return empty list."""
        group_name = 'testgetmissinggroup'
        group = SpokeDHCPGroup(self.dhcp_server)
        result = group.get(group_name)['data']
        expected_result = []
        self.assertEqual(result, expected_result)
        
    def test_delete_dhcp_group(self):
        """Delete DHCP group, return True."""
        group_name = 'testdeletegroup'
        group = SpokeDHCPGroup(self.dhcp_server)
        group.create(group_name)
        self.assertTrue(group.delete(group_name))
        
    def test_delete_missing_dhcp_group(self):
        """Delete missing DHCP group; raise NotFound."""
        group_name = 'testdeletemissing'
        group = SpokeDHCPGroup(self.dhcp_server)
        self.assertRaises(error.NotFound, group.delete, group_name)
        
    def test_delete_dhcp_group_before_hosts(self):
        """Delete DHCP group while hosts present, raise SaveTheBabies."""
        dhcp_host = 'testdeletebeforehost'
        host = SpokeDHCPHost(self.dhcp_server, self.dhcp_group)
        host.create(dhcp_host)
        group = SpokeDHCPGroup(self.dhcp_server)
        self.assertRaises(error.SaveTheBabies, group.delete, self.dhcp_group)
        host.delete(dhcp_host)
        
    def test_create_dhcp_host(self):
        """Create DHCP host; return results object."""
        dhcp_host = 'testcreatehost'
        host = SpokeDHCPHost(self.dhcp_server, self.dhcp_group)
        result = host.create(dhcp_host)['data']
        service_name = self.dhcp_server + self.dhcp_conf_suffix
        group_base_dn = 'cn=%s,cn=%s,%s' % (self.dhcp_group, service_name,
                                            self.base_dn)
        dn = 'cn=%s,%s' % (dhcp_host, group_base_dn)
        dn_info = {'objectClass': ['top', self.dhcp_host_class,
                                   self.dhcp_options_class],
                   'cn': [dhcp_host]}
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        host.delete(dhcp_host)
    
    def test_create_dhcp_host_twice(self):
        """Create DHCP host twice; raise AlreadyExists."""
        dhcp_host = 'testcreatehosttwice'
        host = SpokeDHCPHost(self.dhcp_server, self.dhcp_group)
        host.create(dhcp_host)
        self.assertRaises(error.AlreadyExists, host.create, dhcp_host)
        host.delete(dhcp_host)
        
    def test_create_dhcp_host_with_missing_group(self):
        """Create DHCP host with missing group; raise NotFound."""
        dhcp_group = 'missinggroup'
        self.assertRaises(error.NotFound, SpokeDHCPHost, 
                          self.dhcp_server, dhcp_group)
        
    def test_create_dhcp_host_with_same_name_as_server(self):
        """Create DHCP host with same name as server; raise InputError."""
        dhcp_host = self.dhcp_server
        host = SpokeDHCPHost(self.dhcp_server, self.dhcp_group)
        self.assertRaises(error.InputError, host.create, dhcp_host)
        
    def test_get_dhcp_host(self):
        """Fetch DHCP host; return True."""
        dhcp_host = 'testgethost'
        host = SpokeDHCPHost(self.dhcp_server, self.dhcp_group)
        host.create(dhcp_host)
        result = host.get(dhcp_host)['data']
        service_name = self.dhcp_server + self.dhcp_conf_suffix
        group_base_dn = 'cn=%s,cn=%s,%s' % (self.dhcp_group, service_name,
                                            self.base_dn)
        dn = 'cn=%s,%s' % (dhcp_host, group_base_dn)
        dn_info = {'objectClass': ['top', self.dhcp_host_class,
                                   self.dhcp_options_class],
                   'cn': [dhcp_host]}
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        host.delete(dhcp_host)
        
    def test_get_missing_dhcp_host(self):
        """Fetch missing DHCP host; return empty list."""
        dhcp_host = 'testgetmissinghost'
        host = SpokeDHCPHost(self.dhcp_server, self.dhcp_group)
        result = host.get(dhcp_host)['data']
        expected_result = []
        self.assertEqual(result, expected_result)
        
    def test_delete_dhcp_host(self):
        """Delete DHCP host, return True."""
        dhcp_host = 'testdeletehost'
        host = SpokeDHCPHost(self.dhcp_server, self.dhcp_group)
        host.create(dhcp_host)
        self.assertTrue(host.delete(dhcp_host))
        
    def test_delete_missing_dhcp_host(self):
        """Delete missing DHCP host; raise NotFound."""
        dhcp_host = 'testdeletemissing.dhcp.host.local'
        host = SpokeDHCPHost(self.dhcp_server, self.dhcp_group)
        self.assertRaises(error.NotFound, host.delete, dhcp_host)
        
    def test_create_dhcp_service_option(self):
        """Create a DHCP option on a service object; return True."""
        dhcp_option = 'domain-name "aethernet-local"'
        attr = SpokeDHCPAttr(self.dhcp_server)
        result = attr.create(self.dhcp_option_attr, dhcp_option)['data']
        service_name = self.dhcp_server + self.dhcp_conf_suffix
        dn = 'cn=%s,%s' % (service_name, self.base_dn)
        dn_info = {self.dhcp_option_attr: [dhcp_option]}
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        
    def test_create_dhcp_service_option_twice(self):
        """Create a DHCP option twice; return True."""
        dhcp_option = 'domain-name "aethernet-local"'
        attr = SpokeDHCPAttr(self.dhcp_server)
        attr.create(self.dhcp_option_attr, dhcp_option)
        self.assertRaises(error.AlreadyExists, attr.create, self.dhcp_option_attr, dhcp_option)
        
    def test_create_two_dhcp_service_options(self):
        """Create two DHCP options; return results object."""
        dhcp_option1 = 'domain-name "aethernet-local"'
        dhcp_option2 = 'root-path "10.0.16.16:/usr/local/netboot/nfsroot"'
        attr = SpokeDHCPAttr(self.dhcp_server)
        attr.create(self.dhcp_option_attr, dhcp_option1)
        result = attr.create(self.dhcp_option_attr, dhcp_option2)['data']
        service_name = self.dhcp_server + self.dhcp_conf_suffix
        dn = 'cn=%s,%s' % (service_name, self.base_dn)
        dn_info = {self.dhcp_option_attr: [dhcp_option1, dhcp_option2]}
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        
    def test_get_dhcp_service_option(self):
        """Fetch DHCP option; return option value."""
        dhcp_option = 'routers 10.0.0.1'
        attr = SpokeDHCPAttr(self.dhcp_server)
        attr.create(self.dhcp_option_attr, dhcp_option)
        result = attr.get(self.dhcp_option_attr, dhcp_option)['data']
        service_name = self.dhcp_server + self.dhcp_conf_suffix
        dn = 'cn=%s,%s' % (service_name, self.base_dn)
        dn_info = {self.dhcp_option_attr: [dhcp_option]}
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        
    def test_get_missing_dhcp_service_option(self):
        """Fetch missing DHCP option; return empty List."""
        dhcp_option = 'routers 10.0.0.1'
        attr = SpokeDHCPAttr(self.dhcp_server)
        result = attr.get(self.dhcp_option_attr, dhcp_option)['data']
        expected_result = []
        self.assertEqual(result, expected_result)
        
    def test_delete_dhcp_service_option(self):
        """Delete DHCP option; return True."""
        dhcp_option = 'ddns-update-style none'
        attr = SpokeDHCPAttr(self.dhcp_server)
        attr.create(self.dhcp_option_attr, dhcp_option)
        self.assertTrue(attr.delete(self.dhcp_option_attr, dhcp_option))
        
    def test_delete_missing_dhcp_service_option(self):
        """Delete missing DHCP option; raise NotFound."""
        dhcp_option = 'max-lease-time 7200'
        attr = SpokeDHCPAttr(self.dhcp_server)
        self.assertRaises(error.NotFound, attr.delete, self.dhcp_option_attr, dhcp_option)
        
    def test_delete_dhcp_option_on_missing_service(self):
        """Change DHCP option on missing service; raise NotFound."""
        dhcp_server = 'missing.dhcp.service.local'
        self.assertRaises(error.NotFound, SpokeDHCPAttr, dhcp_server)
        
    def test_create_dhcp_group_option(self):
        """Create a DHCP option on a group object; return results object."""
        dhcp_option = 'domain-name "aethernet-local"'
        attr = SpokeDHCPAttr(self.dhcp_server, self.dhcp_group)
        result = attr.create(self.dhcp_option_attr, dhcp_option)['data']
        service_name = self.dhcp_server + self.dhcp_conf_suffix
        service_dn = 'cn=%s,%s' % (service_name, self.base_dn)
        group_dn = 'cn=%s,%s' % (self.dhcp_group, service_dn)
        dn_info = {self.dhcp_option_attr: [dhcp_option]}
        expected_result = [(group_dn, dn_info)]
        self.assertEqual(result, expected_result)
        
    def test_create_identical_dhcp_group_option_twice(self):
        """Create the same DHCP option on a group twice; raise AlreadyExists."""
        dhcp_option = 'domain-name "aethernet-local"'
        attr = SpokeDHCPAttr(self.dhcp_server, self.dhcp_group)
        attr.create(self.dhcp_option_attr, dhcp_option)
        self.assertRaises(error.AlreadyExists, attr.create, self.dhcp_option_attr, dhcp_option)
        
    def test_create_multiple_dhcp_group_options(self):
        """Create multiple DHCP options on a group; return results object."""
        dhcp_option = 'domain-name "aethernet-local"'
        dhcp_option2 = 'domain-name "aethernet.com"'
        attr = SpokeDHCPAttr(self.dhcp_server, self.dhcp_group)
        attr.create(self.dhcp_option_attr, dhcp_option)
        attr.create(self.dhcp_option_attr, dhcp_option2)
        result = attr.get(self.dhcp_option_attr, dhcp_option)['data']
        service_name = self.dhcp_server + self.dhcp_conf_suffix
        service_dn = 'cn=%s,%s' % (service_name, self.base_dn)
        group_dn = 'cn=%s,%s' % (self.dhcp_group, service_dn)
        dn_info = {self.dhcp_option_attr: [dhcp_option, dhcp_option2]}
        expected_result = [(group_dn, dn_info)]
        self.assertEqual(result, expected_result)
        
    def test_get_dhcp_group_option(self):
        """Fetch DHCP option on group; return option value."""
        dhcp_option = 'domain-name "aethernet-local"'
        attr = SpokeDHCPAttr(self.dhcp_server, self.dhcp_group)
        attr.create(self.dhcp_option_attr, dhcp_option)
        result = attr.get(self.dhcp_option_attr, dhcp_option)['data']
        service_name = self.dhcp_server + self.dhcp_conf_suffix
        service_dn = 'cn=%s,%s' % (service_name, self.base_dn)
        group_dn = 'cn=%s,%s' % (self.dhcp_group, service_dn)
        dn_info = {self.dhcp_option_attr: [dhcp_option]}
        expected_result = [(group_dn, dn_info)]
        self.assertEqual(result, expected_result)

    def test_get_dhcp_group_option_with_missing_group(self):
        """Fetch DHCP option with missing group; raise NotFound."""
        dhcp_group = 'missinggroup'
        self.assertRaises(error.NotFound, SpokeDHCPAttr, 
                          self.dhcp_server,  dhcp_group)
        
    def test_get_missing_dhcp_group_option(self):
        """Fetch missing DHCP group option; return empty List."""
        dhcp_option = 'routers 10.0.0.1'
        attr = SpokeDHCPAttr(self.dhcp_server, self.dhcp_group)
        result = attr.get(self.dhcp_option_attr, dhcp_option)['data']
        expected_result = []
        self.assertEqual(result, expected_result)
        
    def test_delete_dhcp_group_option(self):
        """Delete DHCP group option; return True."""
        dhcp_option = 'ddns-update-style none'
        attr = SpokeDHCPAttr(self.dhcp_server, self.dhcp_group)
        attr.create(self.dhcp_option_attr, dhcp_option)
        self.assertTrue(attr.delete(self.dhcp_option_attr, dhcp_option))
        
    def test_delete_missing_dhcp_group_option(self):
        """Delete missing DHCP group option; raise NotFound."""
        dhcp_option = 'max-lease-time 7200'
        attr = SpokeDHCPAttr(self.dhcp_server, self.dhcp_group)
        self.assertRaises(error.NotFound, attr.delete, self.dhcp_option_attr, dhcp_option)
        
    def test_create_dhcp_host_option(self):
        """Create a DHCP option on a host object; return option value."""
        dhcp_option = 'domain-name "aethernet-local"'
        attr = SpokeDHCPAttr(self.dhcp_server, self.dhcp_group, self.dhcp_host)
        result = attr.create(self.dhcp_option_attr, dhcp_option)['data']
        service_name = self.dhcp_server + self.dhcp_conf_suffix
        service_dn = 'cn=%s,%s' % (service_name, self.base_dn)
        group_dn = 'cn=%s,%s' % (self.dhcp_group, service_dn)
        host_dn = 'cn=%s,%s' % (self.dhcp_host, group_dn)
        dn_info = {self.dhcp_option_attr: [dhcp_option]}
        expected_result = [(host_dn, dn_info)]
        self.assertEqual(result, expected_result)
        
    def test_create_two_dhcp_host_options(self):
        """Create two DHCP options on a host object; return True."""
        dhcp_option1 = 'domain-name "aethernet-local"'
        dhcp_option2 = 'root-path "10.0.16.16:/usr/local/netboot/nfsroot"'
        attr = SpokeDHCPAttr(self.dhcp_server, self.dhcp_group, self.dhcp_host)
        attr.create(self.dhcp_option_attr, dhcp_option1)
        result = attr.create(self.dhcp_option_attr, dhcp_option2)['data']
        service_name = self.dhcp_server + self.dhcp_conf_suffix
        service_dn = 'cn=%s,%s' % (service_name, self.base_dn)
        group_dn = 'cn=%s,%s' % (self.dhcp_group, service_dn)
        host_dn = 'cn=%s,%s' % (self.dhcp_host, group_dn)
        dn_info = {self.dhcp_option_attr: [dhcp_option1, dhcp_option2]}
        expected_result = [(host_dn, dn_info)]
        self.assertEqual(result, expected_result)
        
    def test_create_dhcp_host_option_twice(self):
        """Create the same DHCP option on a host twice; raise AleadyExists."""
        dhcp_option = 'domain-name "aethernet-local"'
        attr = SpokeDHCPAttr(self.dhcp_server, self.dhcp_group, self.dhcp_host)
        attr.create(self.dhcp_option_attr, dhcp_option)
        self.assertRaises(error.AlreadyExists, attr.create, 
                          self.dhcp_option_attr, dhcp_option)
        
    def test_get_dhcp_host_option(self):
        """Fetch DHCP option on host; return option value."""
        dhcp_option = 'domain-name "aethernet-local"'
        attr = SpokeDHCPAttr(self.dhcp_server, self.dhcp_group, self.dhcp_host)
        attr.create(self.dhcp_option_attr, dhcp_option)
        result = attr.get(self.dhcp_option_attr, dhcp_option)['data']
        service_name = self.dhcp_server + self.dhcp_conf_suffix
        service_dn = 'cn=%s,%s' % (service_name, self.base_dn)
        group_dn = 'cn=%s,%s' % (self.dhcp_group, service_dn)
        host_dn = 'cn=%s,%s' % (self.dhcp_host, group_dn)
        dn_info = {self.dhcp_option_attr: [dhcp_option]}
        expected_result = [(host_dn, dn_info)]
        self.assertEqual(result, expected_result)
        
    def test_get_missing_dhcp_host_option(self):
        """Fetch missing DHCP host option; return empty List."""
        dhcp_option = 'routers 10.0.0.1'
        attr = SpokeDHCPAttr(self.dhcp_server, self.dhcp_group, self.dhcp_host)
        result = attr.get(self.dhcp_option_attr, dhcp_option)['data']
        expected_result = []
        self.assertEqual(result, expected_result)
        
    def test_delete_dhcp_host_option(self):
        """Delete DHCP host option; return True."""
        dhcp_option = 'ddns-update-style none'
        attr = SpokeDHCPAttr(self.dhcp_server, self.dhcp_group, self.dhcp_host)
        attr.create(self.dhcp_option_attr, dhcp_option)
        self.assertTrue(attr.delete(self.dhcp_option_attr, dhcp_option))
        
    def test_delete_missing_dhcp_host_option(self):
        """Delete missing DHCP host option; raise NotFound."""
        dhcp_option = 'max-lease-time 7200'
        attr = SpokeDHCPAttr(self.dhcp_server, self.dhcp_group, self.dhcp_host)
        self.assertRaises(error.NotFound, attr.delete, self.dhcp_option_attr,
                           dhcp_option)
        
    def test_delete_dhcp_option_on_missing_host(self):
        """Delete DHCP option on missing DHCP host; raise NotFound."""
        dhcp_host = 'missinghost'
        self.assertRaises(error.NotFound, SpokeDHCPAttr, 
                          self.dhcp_server, self.dhcp_group, dhcp_host)
