"""IP address management module.

Classes:
SpokeIP - Creation/deletion/modification/retrieval of IP account details.
Exceptions:
NotFound - raised on failure to find an object when one is expected.
AlreadyExists -raised on attempts to create an object when one already exists.
InputError - raised on invalid input.
ConfigError - raised on invalid configuration data.
InsufficientResource - raised on a lack of a required resource.
SearchError - raised to indicate unwanted search results were returned.
"""

# own modules
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.logger as logger
import spoke.lib.common as common
import spoke.lib.ip_helper as ip_helper
from spoke.lib.directory import SpokeLDAP
from spoke.lib.kv import SpokeKV

class SpokeSubnet(SpokeKV):
    
    """Provide CRUD methods to subnet objects."""
    
    def __init__(self, ip=None, mask=None, dc=None):   
        """Get config, setup logging and Redis connection."""
        SpokeKV.__init__(self)
        self.config = config.setup()
        self.log = logger.setup(__name__)
        self.max_mask = 16 # This is the largest network we can work with
        # Check our subnet is well formatted in dotted decimal
        if ip and mask:
            common.validate_ip_address(ip)
            # Check our netmask is well formatted and NOT in dotted decimal
            try:
                common.validate_ip_address(mask)
            except:
                pass # It's not a dotted decimal format subnet, good
            else:
                # It validated as a dotted decimal, but we need an integer
                msg = 'IPv4 subnet mask must be between %s and 32' % self.max_mask
                raise error.InputError(msg)
            
            self.subnet = ip_helper.Network(ip, int(mask))
            self.network = self.subnet.network()
            self.mask = self.subnet.mask
        
            if dc is not None:
                self.kv_name = dc + str(self.network)
                self.kv_free = '%s:%s:%s:free' % (dc, self.network, self.mask)
                self.kv_aloc = '%s:%s:%s:aloc' % (dc, self.network, self.mask)
            else:
                self.kv_name = str(self.network)
                self.kv_free = '%s:%s:free' % (self.network, self.mask)
                self.kv_aloc = '%s:%s:aloc' % (self.network, self.mask)
            self.ip_ldap_enabled = self.config.get('IP', 'ip_ldap_enabled', False)
            self.ip_ldap_attr = self.config.get('IP', 'ip_ldap_attr', 'dhcpStatements')
            self.ip_ldap_key = self.config.get('IP', 'ip_ldap_key', 'fixed-address')
            self.ip_ldap_search_base = self.config.get('IP', 'ip_ldap_search_base', False)
        else:
            (self.network, self.mask) = (None, None)

    def _populate_from_ldap(self):
        """Create a list of allocated IP addresses from LDAP"""
        if not self.ip_ldap_search_base:
            msg = 'LDAP enabled but no LDAP search base defined'
            raise error.ConfigError(msg)
        # Do LDAP search and populate allocated IP address store
        ldap = SpokeLDAP()
        dn = self.ip_ldap_search_base
        search_scope = 2 # ldap.SCOPE_SUBTREE
        # Filter requires a modified DHCP schema with substr match support
        filter = '%s=%s*' % (self.ip_ldap_attr, self.ip_ldap_key)
        attr = [self.ip_ldap_attr]
        result = ldap._get_object(dn, search_scope, filter, attr)
        if result['data'] == []:
            msg = 'No reserved IP addresses found in LDAP'
            self.log.debug(msg)
            return True
        # Loop through our result and build a set of allocated addresses
        for item in result['data']:
        # Fetch the value of the IP Address attribute
            entry = item[1][self.ip_ldap_attr][0]
            # Remove the string prefix
            ip = entry.split(' ')[1]           
            # Check if ip address is in our subnet
            if self.subnet.has_key(ip):
                self.aloc_ips.add(ip)
        msg = 'Found %s IP addreses in LDAP' % len(self.aloc_ips)
        self.log.debug(msg)
                
    def _populate_aloc_ips(self, aloc_ips=None):
        """Calculate allocated IPs; populate KV store."""
        self.aloc_ips = set()
        # Add any directly provided allocated IPs
        if aloc_ips:
            for ip in aloc_ips:
                self.aloc_ips.add(ip)
        if self.ip_ldap_enabled == 'yes':
            self._populate_from_ldap()  
            
        if len(self.aloc_ips) == 0:
            return True
        # Write set to KV store
        for ip in self.aloc_ips:
            self.KV.sadd(self.kv_aloc, ip)
        msg = 'Adding %s reserved IP addresses' % len(self.aloc_ips)
        self.log.debug(msg)
        return True
    
    def _populate_free_ips(self):
        """Populate KV store with all free IP within a given subnet."""
        all_ips = set()
        # /8 network takes 1h 9m (2Ghz CPU and 4GB RAM); produces DB of 220MB
        if self.mask < self.max_mask:
            msg = 'Subnets larger than %s must be created manually' % self.mask
            raise error.InputError(msg)
        for ip in self.subnet:
            all_ips.add(str(ip))
        self.free_ips = all_ips - self.aloc_ips
            
        for free_ip in self.free_ips:
            self.KV.sadd(self.kv_free, free_ip)
        # Remove the network and broadcast addresses
        self.KV.srem(self.kv_free, self.subnet.network())
        self.KV.srem(self.kv_free, self.subnet.broadcast())
        msg = 'KV store %s populated with %s free IP addresses' % \
            (self.kv_free, len(self.free_ips))
        self.log.debug(msg)
        return True
    
    def _release_ip(self, ip):
        """Release an IP from the pool of allocated IPs"""
        ip = common.validate_ip_address(ip)
        self.KV.srem(self.kv_aloc, ip)
        self.KV.sadd(self.kv_free, ip)
        return True

    def _reserve_ip(self, number):
        """Reserve an IP from the pool of free IPs"""
        common.is_number(number)
        number = int(number)
        if number > self.KV.scard(self.kv_free):
            msg = 'Fewer than %s free IP addresses in the subnet store %s' % \
            (number, self.kv_free)
            raise error.InsufficientResource(msg)
        offer = []
        for i in range(number):
            ip = self.KV.spop(self.kv_free)
            offer.append(ip)
            self.KV.sadd(self.kv_aloc, ip)
        return offer
    
    def create(self, aloc_ips=None):
        """Create subnet kv stores; populate with IPs; return True."""
        if not (self.network and self.mask):
            msg = 'Please specify ip and mask'
            raise error.InputError(msg)
              
        if self.KV.exists(self.kv_aloc) or self.KV.exists(self.kv_free):
            msg = 'Subnet %s/%s already exists' % (self.kv_name, str(self.mask))
            raise error.AlreadyExists(msg)      
        
        self._populate_aloc_ips(aloc_ips)
        self._populate_free_ips()
        
        msg = 'Created subnet %s/%s with %s free and %s reserved IPs' \
        % (self.kv_name, str(self.mask), len(self.free_ips), len(self.aloc_ips))
        self.log.debug(msg)
        result = self.get()
        if result['exit_code'] == 0 and result['count'] == 1:
            result['msg'] = "Created %s:" % result['type']
            return result
        else:
            msg = 'Create operation returned OK, but unable to find object'
            raise error.NotFound(msg)
        return result
    
    def get(self):
        """Retrieve subnet information; return results list."""
        if not (self.network and self.mask): # Retrive all subnets
            data = self.KV.keys()
            result = common.process_results(data, 'Subnet')
            self.log.debug('Result: %s' % result)
            return result
        data = []
        obj = self.kv_name
        attributes = {}
        attributes['free'] = [self.KV.scard(self.kv_free)]
        attributes['aloc'] = [self.KV.scard(self.kv_aloc)]
        if attributes['free'] == [0] and attributes ['aloc'] == [0]:
            result = common.process_results(data, 'Subnet')
            self.log.debug('Result: %s' % result)
            return result
        try:
            free = attributes['free'][0]
        except KeyError:
            free = 0
        try:
            aloc = attributes['aloc'][0]
        except KeyError:
            aloc = 0
        msg = 'Subnet %s/%s found; %s free and %s pre-allocated IP addresses' % \
                (self.kv_name, str(self.mask), free, aloc)
        self.log.debug(msg)
        item = (obj, attributes)
        data.append(item)
        result = common.process_results(data, 'Subnet')
        self.log.debug('Result: %s' % result)
        return result
            
    def modify(self, reserve=False, release=False):
        """Reserve or release IP address from Subnet"""
        if not (self.network and self.mask):
            msg = 'Please specify ip and mask'
            raise error.InputError(msg)
        if not reserve and not release:
            msg = 'You must specify if you wish to reserve or release an IP'
            raise error.InputError(msg)
        if reserve and release:
            msg = 'You cannot simultaneously reserve and release an IP'
            raise error.InputError(msg)
        if reserve:
            offer = self._reserve_ip(reserve)
            result = common.process_results(offer)
            result['msg'] = 'Reserved ip(s) %s from %s' % (offer, self.kv_name)
            self.log.debug('Result: %s' % result)
            return result
        if release:
            self._release_ip(release)
            result = self.get()
            result['msg'] = 'Returned %s ip(s) to %s' % (release, self.kv_name)
            self.log.debug('Result: %s' % result)
            return result
        
    def delete(self):
        """Delete subnet kv stores; return True."""
        if not (self.network and self.mask):
            msg = 'Please specify ip and mask'
            raise error.InputError(msg)
        if self.get()['data'] == []:
            msg = "cannot delete as already missing"
            raise error.NotFound, msg
        # Delete kv stores
        self.KV.delete(self.kv_aloc)
        self.KV.delete(self.kv_free)
        result = self.get()
        if result['exit_code'] == 3 and result['count'] == 0:
            result['msg'] = "Deleted %s:" % result['type']
            return result
        else:
            msg = 'Delete operation returned OK, but object still there?'
            raise error.SearchError(msg)
