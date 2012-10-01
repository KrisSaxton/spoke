"""DNS container management module.

Classes:
SpokeDNSZone - Creation/deletion/retrieval of DNS zone objects.
SpokeDNSResouceRecord - Creation/deletion/retrieval of DNS resource records.
SpokeDNSResourceAttribute - Creation/deletion/retrieval of DNS resource attributes.

Exceptions:
NotFound - raised on failure to find an object when one is expected.
InputError - raised on invalid input.

ldap.MOD_DELETE = 1
ldap.MOD_ADD = 0
"""

# own modules
import spoke.lib.common as common
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.logger as logger
from spoke.lib.directory import SpokeLDAP
from spoke.lib.org import SpokeOrg

class SpokeDNSResource(SpokeLDAP):
    
    """Provide CRUD methods to DNS resource objects."""
    
    def __init__(self, org_name, domain_name):
        """Get config, setup logging and LDAP connection."""
        SpokeLDAP.__init__(self)
        self.config = config.setup()
        self.log = logger.setup(__name__)
        self.base_dn = self.config.get('LDAP', 'basedn')
        self.search_scope = 2 # ldap.SUB
        self.retrieve_attr = None
        self.org_name = org_name
        self.org = self._get_org(self.org_name)
        self.org_dn = self.org['data'][0].__getitem__(0)
        self.org_attrs = self.org['data'][0].__getitem__(1)
        self.org_classes = self.org_attrs['objectClass']
        self.dns_cont_attr = self.config.get('DNS', 'dns_cont_attr', 'ou')
        self.dns_cont_name = self.config.get('DNS', 'dns_cont_name', 'dns')
        self.dns_cont_class = self.config.get('ATTR_MAP', \
                                        'container_class', 'organizationalUnit')
        self.dns_zone_name_attr = self.config.get('DNS', 'dns_zone_attr', 'zoneName')
        self.dns_zone_class = self.config.get('DNS', 'dns_zone_class', 'dNSZone')
        self.dns_resource_attr = self.config.get('DNS','dns_resource_attr', 'relativeDomainName')
        self.dns_record_class = self.config.get('DNS','dns_record_class', 'IN')
        self.dns_default_ttl = self.config.get('DNS', 'dns_default_ttl', '86400')
        self.dns_min_ttl = self.config.get('DNS', 'dns_min_ttl', '3600')
        self.dns_serial_start = self.config.get('DNS', 'dns_serial_start', '1')
        self.dns_slave_refresh = self.config.get('DNS','dns_slave_refresh', '3600')
        self.dns_slave_retry = self.config.get('DNS', 'dns_slave_retry', '600')
        self.dns_slave_expire = self.config.get('DNS', 'dns_slave_expire', '86400')
        self.dns_ns_attr = self.config.get('DNS', 'dns_ns_attr', 'nSRecord')
        self.dns_soa_attr = self.config.get('DNS', 'dns_soa_attr', 'sOARecord')
        self.dns_a_attr = self.config.get('DNS', 'dns_a_attr', 'aRecord')
        self.dns_cname_attr = self.config.get('DNS', 'dns_cname_attr', 'cNAMERecord')
        self.dns_mx_attr = self.config.get('DNS', 'dns_mx_attr', 'mXRecord')
        self.dns_txt_attr = self.config.get('TXT', 'dns_txt_attr', 'tXTRecord')
        self.dns_ptr_attr = self.config.get('PTR', 'dns_ptr_attr', 'pTRRecord')
        self.dns_type_attrs = {'SOA':self.dns_soa_attr,
                               'NS':self.dns_ns_attr,
                               'A':self.dns_a_attr,
                               'CNAME':self.dns_cname_attr,
                               'MX': self.dns_mx_attr,
                               'TXT': self.dns_txt_attr,
                               'PTR': self.dns_ptr_attr}
        self.domain_name = common.validate_domain(domain_name)
        self.dns_dn = '%s=%s,%s' % (self.dns_cont_attr, self.dns_cont_name, \
                                                                self.org_dn)
        self.zone_dn = '%s=%s,%s' % (self.dns_zone_name_attr, \
                                                self.domain_name, self.dns_dn)
        
    def _validate_input(self, entry):
        """Stub validation method."""
        return entry
    
    def _validate_number(self, name, number):
        try:
            int(number)
        except:
            msg = '%s must be an integer, you passed %s' % (name, number)
            self.log.error(msg)
            raise error.InputError(msg)
        return number
             
    def _get_type_attr(self, type):
        """Validate resource type; return resource type's LDAP attribute."""
        if type in self.dns_type_attrs:
            return self.dns_type_attrs[type]
        else:
            msg = 'Unknown DNS resource type'
            raise error.InputError(msg)

    def _get_org(self, org_name):
        """Retrieve our org object."""
        org = SpokeOrg()
        result = org.get(org_name)
        if result['data'] == []:
            msg = "Can't find org %s" % org_name
            self.log.error(msg)
            raise error.NotFound(msg)          
        return result

class SpokeDNSZone(SpokeDNSResource):
    
    """Provide CRUD methods to DNS zone objects."""
            
    def create(self):       
        """Create a DNS zone; return a DNS zone object."""
        filter = '(%s:dn:=%s)' % (self.dns_zone_name_attr, self.domain_name)
        dn = self.zone_dn      
        dn_attr = {'objectClass': ['top', self.dns_zone_class],
                   'relativeDomainName': ['@'],
                   'zoneName': [self.domain_name]}  
        dn_info = [(k, v) for (k, v) in dn_attr.items()]
        self.log.debug('Adding DNS zone: ' + dn)
        try:
            result = self._create_object(dn, dn_info)
        except error.NotFound:
            # Let's see if it's just the dns container missing.
            child_dn = '%s=%s,%s' % (self.dns_cont_attr, self.dns_cont_name, \
                                                                self.org_dn)
            child_dn_attr = { 'objectClass': ['top', self.dns_cont_class],
                       self.dns_cont_attr: [self.dns_cont_name] }
            child_dn_info = [(k, v) for (k, v) in child_dn_attr.items()]
            try:
                self._create_object(child_dn, child_dn_info)
            except error.NotFound:
                # Not it wasn't just the dns container
                msg = "Part of %s missing, can't create." % dn
                raise error.NotFound(msg)
            # And then try the original create zone again.
            result = self._create_object(dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result
        
    def get(self):
        """Search for a DNS zone; return a results list."""
        filter = '%s=%s' % (self.dns_zone_name_attr, self.domain_name)
        result = self._get_object(self.zone_dn, self.search_scope, filter)
        self.log.debug('Result: %s' % result)
        return result
    
    def delete(self):
        """Delete a DNS zone; return True."""
        self.log.debug('Deleting DNS zone entry: ' + self.zone_dn)
        result = self._delete_object(self.zone_dn)
        self.log.debug('Result: %s' % result)
        return result

class SpokeDNSResourceRecord(SpokeDNSResource):

    """Provide CRUD methods to DNS resource record objects."""
        
    def create(self, type, entry, ttl=None):
        """Create a DNS resource record; return a resource record object."""
        ldap_attr = self._get_type_attr(type)
        entry = self._validate_input(entry)
        rdn = entry[0]
        value = entry[1]
        if ttl == None:
            ttl = self.dns_default_ttl
        ttl = str(ttl)
        dn = '%s=%s,%s' % (self.dns_resource_attr, rdn, self.zone_dn)
        dn_info = {'objectClass': ['top', self.dns_zone_class],
                   'relativeDomainName': [rdn],
                   'zoneName': [self.domain_name],
                   'dNSClass': self.dns_record_class,
                   'dNSTTL': ttl, 
                    ldap_attr: value}  
        dn_attributes = [(k, v) for (k, v) in dn_info.items()]
        self.log.info('Adding DNS resource record: ' + dn)
        result = self._create_object(dn, dn_attributes)
        self.log.debug('Result: %s' % result)
        return result
    
    def get(self, type, entry):
        """Search for a DNS resource record; return a results list."""        
        ldap_attr = self._get_type_attr(type)
        # More validation, stub method __validate_entry
        entry = self._validate_input(entry)
        rdn = entry[0]
        value = entry[1]
        if value == None:
            value = '*'
        dn = '%s=%s,%s' % (self.dns_resource_attr, rdn, self.zone_dn)
        filter = '%s=%s' % (ldap_attr, value)
        result = self._get_object(dn, self.search_scope, filter)
        self.log.debug('Result: %s' % result)
        return result
    
    def delete(self, type, rdn):
        """Delete a DNS resource record; return True."""
        resource_dn = '%s=%s,%s' % (self.dns_resource_attr, rdn, self.zone_dn)
        self.log.debug('Deleting DNS resource record: ' + resource_dn)
        result = self._delete_object(resource_dn)
        self.log.debug('Result: %s' % result)
        return result

class SpokeDNSResourceAttribute(SpokeDNSResource):
    
    """Provide CRUD methods to DNS resource attribute objects."""
    
    def _validate_input(self, entry):
        """Check input and add trailing period."""
        entry = common.validate_domain(entry)
        return entry + '.'
                      
    def create(self, type, entry):       
        """Create a resource attribute; return a resource attribute object."""
        ldap_attr = self._get_type_attr(type)
        entry = self._validate_input(entry)
        dn_info = []
        dn_info.append((0, ldap_attr, entry))  # ldap.MOD_ADD = 0
        self.log.debug('Adding DNS resource record %s:%s in %s ' % \
                      (type, entry, self.domain_name))
        result = self._create_object(self.zone_dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result
    
    def get(self, type, entry=None):
        """Search for a resource attribute; return a results list.""" 
        if entry == None:
            entry = '*'
        else:
            entry = self._validate_input(entry)       
        ldap_attr = self._get_type_attr(type)
        filter = '%s=%s' % (ldap_attr, entry)     
        result = self._get_object(self.zone_dn, self.search_scope, filter)
        self.log.debug('Result: %s' % result)
        return result
    
    def delete(self, type, entry=None):
        """Delete resource attribute(s); return True."""
        ldap_attr = self._get_type_attr(type)
        if entry is not None:
            entry = self._validate_input(entry)
        dn_info = []
        dn_info.append((1, ldap_attr, entry)) # ldap.MOD_DELETE = 1
        self.log.debug('Deleting DNS resource record %s:%s in %s ' % \
                      (type, entry, self.domain_name))
        result = self._delete_object(self.zone_dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result
    
class SpokeDNSNS(SpokeDNSResourceAttribute):
    
    """Provide CRUD methods to DNS name server objects."""
    
class SpokeDNSMX(SpokeDNSResourceAttribute):
    
    """Provide CRUD methods to DNS MX record object."""
    
    def _validate_input(self, entry):
        """Check input and add trailing period to hostname."""
        entry_list = entry.split(' ')
        if len(entry_list) > 2:
            msg = 'Too many entries: do you have a space somewhere?'
            self.log.error(msg)
            raise error.InputError(msg)
        if len(entry_list) < 2:
            msg = 'Too few entries: are you missing the priority?'
            self.log.error(msg)
            raise error.InputError(msg)
        priority = entry_list[0]
        hostname = entry_list[1]
        try:
            int(priority)
        except:
            msg = 'MX record priority:%s must be an integer.' % priority
            self.log.error(msg)
            raise error.InputError(msg)       
        hostname = common.validate_domain(hostname)
        return priority + ' ' + hostname + '.'
    
class SpokeDNSSOA(SpokeDNSResourceAttribute):
    
    """Provide CRUD methods to DNS SOA objects."""
    
    def _validate_input(self, ns=None, email=None, serial=None,
                        slave_refresh=None, slave_retry=None,
                        slave_expire=None, min_ttl=None):
        """Check and process inputs; return dictionary."""
        ns = common.validate_domain(ns)    
        email = common.validate_domain(email)
        
        if serial is None:
            serial = self.dns_serial_start
        serial = self._validate_number('serial', serial)

        if slave_refresh is None:
            slave_refresh = self.dns_slave_refresh
        slave_refresh = self._validate_number('slave_refresh', slave_refresh)
        
        if slave_retry is None:
            slave_retry = self.dns_slave_retry
        slave_retry = self._validate_number('slave_retry', slave_retry)
        
        if slave_expire is None:
            slave_expire = self.dns_slave_expire
        slave_expire = self._validate_number('slave_expire', slave_expire)
        
        if min_ttl is None:
            min_ttl = self.dns_min_ttl
        min_ttl = self._validate_number('min_ttl', min_ttl)
        
        return (ns, email, serial, slave_refresh, slave_retry, slave_expire,
                min_ttl) 
        
    def create(self, ns, email, serial=None, slave_refresh=None,
               slave_retry=None, slave_expire=None, min_ttl=None):  
        """Create an SOA record; return an SOA record object."""        
        type = 'SOA'
        ldap_attr = self._get_type_attr(type)
        (ns, email, serial, slave_refresh, slave_retry, slave_expire,
        min_ttl) = self._validate_input(ns, email, serial, slave_refresh,
                                        slave_retry, slave_expire, min_ttl)
        entry = '%s. %s. %s %s %s %s %s' % (ns, email, serial, slave_refresh,
                                            slave_retry, slave_expire, min_ttl)
        dn_info = []
        dn_info.append((0, ldap_attr, entry)) # ldap.MOD_ADD = 0
        self.log.debug('Adding SOA record: ' + self.zone_dn)
        result = self._create_object(self.zone_dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result
    
class SpokeDNSA(SpokeDNSResourceRecord):
    
    """Provide CRUD methods to DNS A record objects."""
    
class SpokeDNSCNAME(SpokeDNSResourceRecord):
    
    """Provide CRUD methods to DNS CNAME record objects."""
    
    def _validate_input(self, entry):
        """Check input and add trailing period."""
        rdn = entry[0]
        hostname = entry[1]
        hostname = common.validate_domain(hostname)
        entry = [rdn, hostname + '.']
        return entry
    
class SpokeDNSPTR(SpokeDNSResourceRecord):
    
    """Provide CRUD methods to DNS PTR record objects."""
    
    def _validate_input(self, entry):
        """Check input and add trailing period."""
        rdn = entry[0]
        value = common.validate_domain(entry[1]) + '.'
        return [rdn, value]
    
class SpokeDNSTXT(SpokeDNSResourceAttribute):
    
    """Provide CRUD methods to DNS TXT record objects."""
    
    def _validate_input(self, entry):
        """Dummy method until we work out what is not allowed."""
        return entry
