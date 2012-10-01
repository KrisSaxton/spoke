"""Tests Spoke dns.py module."""
# core modules
import unittest
# own modules
import spoke.lib.error as error
import spoke.lib.config as config
from spoke.lib.org import SpokeOrg
from spoke.lib.dns import SpokeDNSZone
from spoke.lib.dns import SpokeDNSNS
from spoke.lib.dns import SpokeDNSSOA
from spoke.lib.dns import SpokeDNSA
from spoke.lib.dns import SpokeDNSCNAME
from spoke.lib.dns import SpokeDNSMX
from spoke.lib.dns import SpokeDNSTXT
from spoke.lib.dns import SpokeDNSPTR

class SpokeDNSTest(unittest.TestCase):
    
    """A class for testing the Spoke dns.py module."""
    
    def __init__(self, methodName):
        """Setup config data and LDAP connection."""
        unittest.TestCase.__init__(self, methodName)
        common_config = '../../contrib/spoke.conf'
        custom_config = '/tmp/spoke.conf'
        config_files = (common_config, custom_config)
        self.config = config.setup(config_files)
        self.base_dn = self.config.get('LDAP', 'basedn')
        self.search_scope = 2 # ldap.SUB
        self.retrieve_attr = None
        self.org_name = 'SpokeOrgDNSTest'
        self.org_attr = self.config.get('ATTR_MAP', 'org_attr')
        self.org_def_children = self.config.get('ATTR_MAP', 'org_def_children')
        self.org_children = self.org_def_children.split(',')
        self.dns_zone_name = 'spoke.test.zone'
        self.dns_cont_attr = self.config.get('DNS', 'dns_cont_attr')
        self.dns_cont_name = self.config.get('DNS', 'dns_cont_name')
        self.dns_zone_name_attr = self.config.get('DNS', 'dns_zone_attr')
        self.dns_zone_name_class = self.config.get('DNS', 'dns_zone_class')
        self.dns_record_class = 'IN'
        self.dns_default_ttl = self.config.get('DNS', 'dns_default_ttl')
        self.dns_min_ttl = self.config.get('DNS', 'dns_min_ttl')
        self.dns_serial_start = self.config.get('DNS', 'dns_serial_start')
        self.dns_slave_refresh = self.config.get('DNS', 'dns_slave_refresh')
        self.dns_slave_retry = self.config.get('DNS', 'dns_slave_retry')
        self.dns_slave_expire = self.config.get('DNS', 'dns_slave_expire')
        self.dns_ns_attr = self.config.get('DNS', 'dns_ns_attr')
        self.dns_soa_attr = self.config.get('DNS', 'dns_soa_attr')
        self.dns_a_attr = self.config.get('DNS', 'dns_a_attr')
        self.dns_cname_attr = self.config.get('DNS', 'dns_cname_attr')
        self.dns_mx_attr = self.config.get('DNS', 'dns_mx_attr')
        self.dns_txt_attr = self.config.get('DNS', 'dns_txt_attr')
        self.dns_ptr_attr = self.config.get('DNS', 'dns_ptr_attr')
        self.dns_zone_name = 'test.dhcp.server.local'
        self.dns_base = '%s=%s,%s=%s,%s' % (self.dns_cont_attr, 
                                            self.dns_cont_name, self.org_attr,
                                            self.org_name, self.base_dn)
        self.dn_zone_dn = '%s=%s,%s' % (self.dns_zone_name_attr,
                                        self.dns_zone_name, self.dns_base)
            
    def setUp(self):
        org = SpokeOrg()
        org.create(self.org_name, self.org_children)
        zone = SpokeDNSZone(self.org_name, self.dns_zone_name)
        zone.create()

    def tearDown(self):
        zone = SpokeDNSZone(self.org_name, self.dns_zone_name)
        zone.delete()
        org = SpokeOrg()
        org.delete(self.org_name, self.org_children)
        
    # DNS Zone tests
    def test_instanciate_dns_zone_with_missing_org(self):
        """Instanciate a DNS zone in a missing Org; raise NotFound."""
        dns_zone = 'testcreate.dhcp.server.local'
        org_name = 'TestMissingOrg'
        self.assertRaises(error.NotFound, SpokeDNSZone, org_name, dns_zone)
        
    def test_create_dns_zone(self):
        """Create a DNS zone; return results object."""
        dns_zone = 'testcreate.dhcp.server.local'      
        zone = SpokeDNSZone(self.org_name, dns_zone)
        result = zone.create()['data']  
        basedn = '%s=%s,%s=%s,%s' % (self.dns_cont_attr, self.dns_cont_name,
                                     self.org_attr, self.org_name,
                                     self.base_dn)
        dn = '%s=%s,%s' % (self.dns_zone_name_attr, dns_zone, basedn)
        dn_info = {'objectClass': ['top', self.dns_zone_name_class],
                   'relativeDomainName': ['@'],
                   'zoneName': [dns_zone]}
                   
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        zone.delete()
        
    def test_create_local_dns_zone_twice(self):
        """Create a DNS zone twice within same Org; raise AlreadyExists."""
        zone = SpokeDNSZone(self.org_name, self.dns_zone_name)
        self.assertRaises(error.AlreadyExists, zone.create)
        
    def test_create_dns_zone_with_missing_container(self):
        """Create a DNS zone in a missing dns container; return result object."""
        dns_zone = 'testcreate.dhcp.server.local'
        org_name = 'TestMissingContainerOrg'
        org_def_children = 'people,groups'
        org_children = org_def_children.split(',')       
        org = SpokeOrg()
        org.create(org_name, org_children)
             
        zone = SpokeDNSZone(org_name, dns_zone)
        result = zone.create()['data']
        basedn = '%s=%s,%s=%s,%s' % (self.dns_cont_attr, self.dns_cont_name,
                                     self.org_attr, org_name, self.base_dn)
        dn = '%s=%s,%s' % (self.dns_zone_name_attr, dns_zone, basedn)
        dn_info = {'objectClass': ['top', self.dns_zone_name_class],
                   'relativeDomainName': ['@'],
                   'zoneName': [dns_zone]}
                   
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        zone.delete()
        org.delete(org_name)
        
    def test_get_dns_zone(self):
        """Retrieve a DNS zone; return a DNS zone object."""
        zone = SpokeDNSZone(self.org_name, self.dns_zone_name)
        result = zone.get()['data']
        basedn = '%s=%s,%s=%s,%s' % (self.dns_cont_attr, self.dns_cont_name,
                                     self.org_attr, self.org_name,
                                     self.base_dn)
        dn = '%s=%s,%s' % (self.dns_zone_name_attr, self.dns_zone_name, basedn)
        dn_info = {'objectClass': ['top', self.dns_zone_name_class],
                   'relativeDomainName': ['@'],
                   'zoneName': [self.dns_zone_name]}
                   
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        
    def test_get_missing_dns_zone(self):
        """Retrieve a missing DNS zone; return empty list."""
        dns_zone = 'testgetmissing.dhcp.server.local'
        zone = SpokeDNSZone(self.org_name, dns_zone)
        result = zone.get()['data']
        expected_result = []
        self.assertEqual(result, expected_result)
        
    def test_delete_dns_zone(self):
        """Delete a DNS zone; return True."""
        dns_zone = 'testdelete.dhcp.server.local'
        zone = SpokeDNSZone(self.org_name, dns_zone)
        zone.create()
        self.assertTrue(zone.delete())
        
    def test_delete__missing_dns_zone_twice(self): # Really, this should raise something
        """Delete a DNS zone twice; raise NotFound"""
        dns_zone = 'testdeletemissing.dhcp.server.local'
        zone = SpokeDNSZone(self.org_name, dns_zone)
        self.assertRaises(error.NotFound, zone.delete)
        
    def test_invalid_zone_input_wildcard(self):    
        """Input wildcard domain name; raise InputError."""
        dns_zone = '*.domain.loc'
        self.assertRaises(error.InputError, SpokeDNSZone, self.org_name,
                          dns_zone)
        
    def test_invalid_zone_input_hyphen(self):    
        """Input domain name starting with hyphen; raise InputError."""
        dns_zone = '-domain.loc'
        self.assertRaises(error.InputError, SpokeDNSZone, self.org_name,
                          dns_zone)
    
# Tests relating to DNSAttribute derived objects.
    def test_create_ns_record(self):
        """Create an NS record; return results object."""
        type = 'NS'
        ns0 = 'ns0.aethernet.local'
        ns = SpokeDNSNS(self.org_name, self.dns_zone_name)
        result = ns.create(type, ns0)['data']
        dn = '%s=%s,%s' % (self.dns_zone_name_attr, self.dns_zone_name,
                           self.dns_base)
        dn_info = {self.dns_ns_attr: [ns0 + '.']}                   
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        
    def test_create_two_ns_records(self):
        """Create two NS records; return results object."""
        type = 'NS'
        ns0 = 'ns0.aethernet.local'
        ns1 = 'ns1.aethernet.local'
        ns = SpokeDNSNS(self.org_name, self.dns_zone_name)
        ns.create(type, ns0)
        result = ns.create(type, ns1)['data']
        dn = '%s=%s,%s' % (self.dns_zone_name_attr, self.dns_zone_name,
                           self.dns_base)
        dn_info = {self.dns_ns_attr: [ns0 + '.', ns1 +'.']}                   
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        
    def test_get_ns_record(self):
        """Retrieve NS record; return results object."""
        type = 'NS'
        ns0 = 'ns0.aethernet.local'
        ns = SpokeDNSNS(self.org_name, self.dns_zone_name)
        result = ns.create(type, ns0)['data']
        dn = '%s=%s,%s' % (self.dns_zone_name_attr, self.dns_zone_name,
                           self.dns_base)
        dn_info = {self.dns_ns_attr: [ns0 +'.']}                   
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        
    def test_get_ns_records(self):
        """Retrieve all NS records; return NS record objects."""
        type = 'NS'
        ns0 = 'ns0.aethernet.local'
        ns1 = 'ns1.aethernet.local'
        ns = SpokeDNSNS(self.org_name, self.dns_zone_name)
        ns.create(type, ns0)
        ns.create(type, ns1)
        result = ns.get(type)['data']
        dn = '%s=%s,%s' % (self.dns_zone_name_attr, self.dns_zone_name,
                           self.dns_base)
        dn_info = {'objectClass': ['top', self.dns_zone_name_class],
                   'relativeDomainName': ['@'],
                   'zoneName': [self.dns_zone_name],
                   self.dns_ns_attr: [ns0 + '.', ns1 + '.']}                   
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        
    def test_get_missing_ns_record(self):
        """Retrieve a missing NS record; return an empty list."""
        type = 'NS'
        ns = SpokeDNSNS(self.org_name, self.dns_zone_name)
        result = ns.get(type)['data']
        expected_result = []
        self.assertEqual(result, expected_result)
        
    def test_delete_ns_record(self):
        """Delete an NS record; return True."""
        type = 'NS'
        ns0 = 'nsdelete.aethernet.local'
        ns = SpokeDNSNS(self.org_name, self.dns_zone_name)
        ns.create(type, ns0)
        self.assertTrue(ns.delete(type, ns0))
        
    def test_delete_specific_ns_record(self):
        """Delete specific NS record; return remaining NS record object."""
        type = 'NS'
        ns0 = 'ns0.aethernet.local'
        ns1 = 'ns1.aethernet.local'
        ns = SpokeDNSNS(self.org_name, self.dns_zone_name)
        ns.create(type, ns0)
        ns.create(type, ns1)
        ns.delete(type, ns0)
        result = ns.get(type)['data']
        dn = '%s=%s,%s' % (self.dns_zone_name_attr, self.dns_zone_name,
                           self.dns_base)
        dn_info = {'objectClass': ['top', self.dns_zone_name_class],
                   'relativeDomainName': ['@'],
                   'zoneName': [self.dns_zone_name],
                   self.dns_ns_attr: [ns1 +'.']}                   
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        
    def test_delete_missing_ns_record(self):
        """Delete a missing NS record; raise NotFound."""
        type = 'NS'
        ns0 = 'nsdelete.aethernet.local'
        ns = SpokeDNSNS(self.org_name, self.dns_zone_name)
        self.assertRaises(error.NotFound, ns.delete, type, ns0)   
    
# Tests relating to DNSResource derived objects.            
    def test_create_a_record(self):
        """Create an A record; return an results object."""
        type = 'A'
        rdn = 'www'
        ip = '172.16.1.10'
        entry = [rdn,ip]
        a = SpokeDNSA(self.org_name, self.dns_zone_name)
        result = a.create(type, entry)['data']
        dn = '%s=%s,%s' % ('relativeDomainName', rdn, self.dn_zone_dn)
        dn_info = {'objectClass': ['top', self.dns_zone_name_class],
                   'relativeDomainName': [rdn],
                   'zoneName': [self.dns_zone_name],
                   'dNSTTL' : [self.dns_default_ttl],
                   'dNSClass' : [self.dns_record_class],
                   self.dns_a_attr: [ip]}
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        a.delete(type, rdn)
        
    def test_create_a_record_twice(self):
        """Create an A record twice; raise AlreadyExists."""
        type = 'A'
        rdn = 'www-two'
        ip = '172.16.1.10'
        entry = [rdn,ip]
        a = SpokeDNSA(self.org_name, self.dns_zone_name)
        a.create(type, entry)
        self.assertRaises(error.AlreadyExists, a.create, type, entry)
        a.delete(type, rdn)
        
    def test_create_a_record_in_missing_zone(self):
        """Create an A record in a missing DNS zone; raise NotFound."""
        dns_zone_name = 'missing.aethernet.local'
        type = 'A'
        rdn = 'missing'
        ip = '172.16.1.10'
        entry = [rdn,ip]
        a = SpokeDNSA(self.org_name, dns_zone_name)
        self.assertRaises(error.NotFound, a.create, type, entry)
        
    def test_get_a_record(self):
        """Retrieve an A record; return a results object."""
        type = 'A'
        rdn = 'geta'
        ip = '172.16.1.10'
        entry = [rdn,ip]
        a = SpokeDNSA(self.org_name, self.dns_zone_name)
        a.create(type, entry)
        result = a.get(type, entry)['data']
        dn = '%s=%s,%s' % ('relativeDomainName', rdn, self.dn_zone_dn)
        dn_info = {'objectClass': ['top', self.dns_zone_name_class],
                   'relativeDomainName': [rdn],
                   'zoneName': [self.dns_zone_name],
                   'dNSTTL' : [self.dns_default_ttl],
                   'dNSClass' : [self.dns_record_class],
                   self.dns_a_attr: [ip]}
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        a.delete(type, rdn)
        
    def test_get_missing_a_record(self):
        """Retrieve a missing A record; return an empty list."""
        type = 'A'
        rdn = 'missing'
        ip = '172.16.1.10'
        entry = [rdn,ip]
        a = SpokeDNSA(self.org_name, self.dns_zone_name)
        result = a.get(type, entry)['data']
        expected_result = []
        self.assertEqual(result, expected_result)
        
    def test_delete_a_record(self):
        """Delete an A record; return True."""
        type = 'A'
        rdn = 'geta'
        ip = '172.16.1.10'
        entry = [rdn,ip]
        a = SpokeDNSA(self.org_name, self.dns_zone_name)
        a.create(type, entry)
        self.assertTrue(a.delete(type, rdn))
        
    def test_delete_missing_a_record(self):
        """Delete a missing A record; raise NotFound."""
        type = 'A'
        rdn = 'geta'
        a = SpokeDNSA(self.org_name, self.dns_zone_name)
        self.assertRaises(error.NotFound, a.delete, type, rdn)
    
# Tests for where objects deviate from standard Resource/Attribute classes.    
    def test_create_cname_record(self):
        """Create a CNAME record; return results object."""
        type = 'CNAME'
        rdn = 'www'
        hostname = 'some.other.host'
        entry = [rdn,hostname]
        cname = SpokeDNSCNAME(self.org_name, self.dns_zone_name)
        result = cname.create(type, entry)['data']
        zone_dn = '%s=%s,%s' % (self.dns_zone_name_attr, self.dns_zone_name,
                                self.dns_base)
        dn = '%s=%s,%s' % ('relativeDomainName', rdn, zone_dn)
        dn_info = {'objectClass': ['top', self.dns_zone_name_class],
                   'relativeDomainName': [rdn],
                   'zoneName': [self.dns_zone_name],
                   'dNSTTL' : [self.dns_default_ttl],
                   'dNSClass' : [self.dns_record_class],
                   self.dns_cname_attr: [hostname + '.']}
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        cname.delete(type, rdn)
        
    def test_create_mx_record(self):
        """Create an MX record; return results object."""
        type = 'MX'
        priority = '10'
        hostname = 'some.other.host'
        entry = priority + ' ' + hostname
        mx = SpokeDNSMX(self.org_name, self.dns_zone_name)
        result = mx.create(type, entry)['data']
        dn = '%s=%s,%s' % (self.dns_zone_name_attr, self.dns_zone_name,
                           self.dns_base)
        dn_info = {self.dns_mx_attr: [priority + ' ' + hostname + '.']}                   
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        mx.delete(type, entry)
        
    def test_invalid_mx_record_priority(self):    
        """Input non integer MX record priority; raise InputError."""
        type = 'MX'
        priority = '1A'
        hostname = 'some.other.host'
        entry = priority + ' ' + hostname
        mx = SpokeDNSMX(self.org_name, self.dns_zone_name)
        self.assertRaises(error.InputError, mx.create, type, entry)
        
    def test_invalid_mx_record_hostname(self):    
        """Input non integer MX record priority; raise InputError."""
        type = 'MX'
        priority = '20'
        hostname = 'some other.host'
        entry = priority + ' ' + hostname
        mx = SpokeDNSMX(self.org_name, self.dns_zone_name)
        self.assertRaises(error.InputError, mx.create, type, entry)

    def test_create_soa_record(self):
        """Create an SOA record; return results object."""
        type = 'SOA'
        ns = 'ns0.aethernet.local'
        email = 'postmaster' + self.dns_zone_name
        serial = 1
        slave_refresh = 1800
        slave_retry = 900
        slave_expire = 302400
        min_ttl = 43200
        entry = '%s. %s. %s %s %s %s %s' % (ns, email, serial,
                                            slave_refresh, slave_retry,
                                            slave_expire, min_ttl)
        soa = SpokeDNSSOA(self.org_name, self.dns_zone_name)
        result = soa.create(ns=ns, email=email, serial=serial,
                            slave_refresh=slave_refresh,
                            slave_retry=slave_retry,
                            min_ttl=min_ttl,
                            slave_expire=slave_expire)['data']
        dn = '%s=%s,%s' % (self.dns_zone_name_attr, self.dns_zone_name,
                           self.dns_base)
        dn_info = {self.dns_soa_attr: [entry]}                
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        
    def test_invalid_soa_record(self):
        """Create SOA record with a non-integer ttl; raise InputError."""
        type = 'SOA'
        ns = 'ns0.aethernet.local'
        email = 'postmaster' + self.dns_zone_name
        ttl = 'A'
        soa = SpokeDNSSOA(self.org_name, self.dns_zone_name)
        self.assertRaises(error.InputError, soa.create, ns=ns,
                          email=email, min_ttl=ttl)
        
    def test_create_soa_record_with_missing_email(self):
        """Create SOA record with a missing email; raise InputError."""
        type = 'SOA'
        ns = 'ns0.aethernet.local'
        soa = SpokeDNSSOA(self.org_name, self.dns_zone_name)
        self.assertRaises(error.InputError, soa.create, ns=ns, email=None)
 
    def test_get_soa_record(self):
        """Create an SOA record; return an SOA record object."""
        type = 'SOA'
        ns = 'ns0.aethernet.local'
        email = 'postmaster' + self.dns_zone_name
        entry = '%s. %s. %s %s %s %s %s' % (ns, email, self.dns_serial_start,
                                            self.dns_slave_refresh,
                                            self.dns_slave_retry,
                                            self.dns_slave_expire,
                                            self.dns_min_ttl)
        soa = SpokeDNSSOA(self.org_name, self.dns_zone_name)
        soa.create(ns=ns, email=email)
        result = soa.get(type)['data']
        dn = '%s=%s,%s' % (self.dns_zone_name_attr, self.dns_zone_name,
                           self.dns_base)
        dn_info = {'objectClass': ['top', self.dns_zone_name_class],
                   'relativeDomainName': ['@'],
                   'zoneName': [self.dns_zone_name],
                   self.dns_soa_attr: [entry]}                
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        
    def test_delete_soa_record(self):
        """Delete SOA record; return True."""
        type = 'SOA'
        ns = 'ns0.aethernet.local'
        email = 'test.aethernet.local'
        soa = SpokeDNSSOA(self.org_name, self.dns_zone_name)
        soa.create(ns, email)
        self.assertTrue(soa.delete(type))
        
    def test_create_txt_record(self):
        """Create a TXT record; return results object."""
        type = 'TXT'
        entry = '"v=spf1 ip4:82.211.95.70 mx -all"' # SPF record
        txt = SpokeDNSTXT(self.org_name, self.dns_zone_name)
        result = txt.create(type, entry)['data']
        dn = '%s=%s,%s' % (self.dns_zone_name_attr, self.dns_zone_name,
                           self.dns_base)
        dn_info = {self.dns_txt_attr: [entry]}                   
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        txt.delete(type, entry)

    def test_create_ptr_record(self):
        """Create a pointer record; return results object."""
        type = 'PTR'
        rdn = 'ptr.aethernet.local'
        ip = '10'
        entry = [ip,rdn]
        ptr = SpokeDNSPTR(self.org_name, self.dns_zone_name)
        result = ptr.create(type, entry)['data']
        zone_dn = '%s=%s,%s' % (self.dns_zone_name_attr, self.dns_zone_name,
                                self.dns_base)
        dn = '%s=%s,%s' % ('relativeDomainName', ip, zone_dn)
        dn_info = {'objectClass': ['top', self.dns_zone_name_class],
                   'relativeDomainName': [ip],
                   'zoneName': [self.dns_zone_name],
                   'dNSClass': ['IN'],
                   'dNSTTL': [self.dns_default_ttl],
                   self.dns_ptr_attr: [rdn + '.']}                   
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        ptr.delete(type, ip)
        
    def test_create_ptr_record_custom_ttl(self):
        """Create a pointer record with TTL; return results object."""
        type = 'PTR'
        rdn = 'ptr.aethernet.local'
        ip = '10'
        entry = [ip,rdn]
        ttl = 3200
        ptr = SpokeDNSPTR(self.org_name, self.dns_zone_name)
        result = ptr.create(type, entry, ttl)['data']
        zone_dn = '%s=%s,%s' % (self.dns_zone_name_attr, self.dns_zone_name,
                                self.dns_base)
        dn = '%s=%s,%s' % ('relativeDomainName', ip, zone_dn)
        dn_info = {'objectClass': ['top', self.dns_zone_name_class],
                   'relativeDomainName': [ip],
                   'zoneName': [self.dns_zone_name],
                   'dNSClass' : [self.dns_record_class],
                   'dNSTTL': [str(ttl)],
                   self.dns_ptr_attr: [rdn + '.']}                   
        expected_result = [(dn, dn_info)]
        self.assertEqual(result, expected_result)
        ptr.delete(type, ip)       

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
