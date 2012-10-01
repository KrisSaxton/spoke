"""DHCP container management module.

Classes:
SpokeDHCPServer - Creation/deletion/retrieval of DHCP server objects.
SpokeDHCPService - Creation/deletion/retrieval of DHCP service objects.
SpokeDHCPSubnets - Creation/deletion/retrieval of DHCP subnet objects.
SpokeDHCPGroup - Creation/deletion/retrieval of DHCP group objects.
SpokeDHCPHost - Creation/deletion/retrieval of DHCP host objects.
SpokeDHCPAttr - Creation/deletion/retrieval of DHCP attribute objects.

Exceptions:
NotFound - raised on failure to find an object when one is expected.
InputError - raised on invalid input.

TODO - create default group when creating service
TODO - set group as optional parameter (defaults to 'default' group).
"""

# own modules
import spoke.lib.common as common
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.logger as logger
from spoke.lib.directory import SpokeLDAP

# 3rd party modules
import ldap

class SpokeDHCPServer(SpokeLDAP):
    
    """Provide CRUD methods to DHCP server objects."""
    
    def __init__(self):
        """Get config, setup logging and LDAP connection."""
        SpokeLDAP.__init__(self)
        self.config = config.setup()
        self.log = logger.setup(__name__)
        self.base_dn = self.config.get('DHCP', 'dhcp_basedn')
        self.search_scope = 2 # ldap.SUB
        self.retrieve_attr = None
        self.dhcp_server_class = 'dhcpServer'
        self.dhcp_conf_suffix = self.config.get('DHCP', 'dhcp_conf_suffix', '-config') 
        
    def create(self, dhcp_server):
        """Create a DHCP server; return a DHCP server object."""
        filter = 'cn=%s' % dhcp_server
        dn = 'cn=%s,%s' % (dhcp_server, self.base_dn)
        service_name = dhcp_server + self.dhcp_conf_suffix
        service_dn = 'cn=%s,%s' % (service_name, self.base_dn)
        dn_attr = {'objectClass': ['top', self.dhcp_server_class],
                   'cn': [dhcp_server],
                   'dhcpServiceDN': [service_dn]}   
        dn_info = [(k, v) for (k, v) in dn_attr.items()]
        self.log.info('Adding DHCP Server: ' + dn)
        result = self._create_object(dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result
        
        return self._validate_exists(dn, filter)
        
    def get(self, dhcp_server):
        """Search for a DHCP server; return a results list."""
        dn = self.base_dn
        filter = 'cn=%s' % dhcp_server
        result = self._get_object(dn, self.search_scope, filter)
        self.log.debug('Result: %s' % result)
        return result
    
    def delete(self, dhcp_server):
        """Delete a DHCP server; return True."""
        dn = 'cn=%s,%s' % (dhcp_server, self.base_dn)
        self.log.debug('Deleting DHCP server entry: ' + dn)
        result = self._delete_object(dn)
        self.log.debug('Result: %s' % result)
        return result
        
class SpokeDHCPService(SpokeLDAP):
    
    """Provide CRUD methods to DHCP service objects."""
    
    def __init__(self):
        """Get config, setup logging and LDAP connection."""
        SpokeLDAP.__init__(self)
        self.config = config.setup()
        self.log = logger.setup(self.__module__)
        self.base_dn = self.config.get('DHCP', 'dhcp_basedn')
        self.search_scope = 2 # ldap.SUB
        self.retrieve_attr = None
        self.dhcp_service_class = 'dhcpService'
        self.dhcp_options_class = 'dhcpOptions'
        self.dhcp_conf_suffix = self.config.get('DHCP', 'dhcp_conf_suffix', '-config')
        
    def create(self, dhcp_server):
        """Create a DHCP service; return DHCP service objects."""
        service_name = dhcp_server + self.dhcp_conf_suffix
        filter = 'cn=%s' % service_name
        dn = 'cn=%s,%s' % (service_name, self.base_dn)
        primary_dn = 'cn=%s,%s' % (dhcp_server, self.base_dn)
        dn_attr = {'objectClass': ['top', self.dhcp_service_class,
                                   self.dhcp_options_class],
                   'cn': [service_name],
                   'dhcpPrimaryDN': [primary_dn]} 
        dn_info = [(k, v) for (k, v) in dn_attr.items()]
        self.log.debug('Adding DHCP Service: ' + dn)
        result = self._create_object(dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result
        
    def get(self, dhcp_server):
        """Search for a DHCP service; return results list."""
        service_name = dhcp_server + self.dhcp_conf_suffix
        filter = 'cn=%s' % service_name
        dn = 'cn=%s,%s' % (service_name, self.base_dn)
        result = self._get_object(dn, self.search_scope, filter)
        self.log.debug('Result: %s' % result)
        return result
          
    def delete(self, dhcp_server):
        """Delete a DHCP service; return True."""
        base_dn = self.base_dn
        service_name = dhcp_server + self.dhcp_conf_suffix
        dn = 'cn=%s,%s' % (service_name, base_dn)
        self.log.info('Deleting DHCP service entry: ' + dn)
        result = self._delete_object(dn)
        self.log.debug('Result: %s' % result)
        return result
    
class SpokeDHCPSubnet(SpokeLDAP):
    
    """Provide CRUD methods to DHCP subnet objects."""
    
    def __init__(self, dhcp_server):
        """Get config, setup logging and LDAP connection."""
        SpokeLDAP.__init__(self)
        self.config = config.setup()
        self.log = logger.setup(self.__module__)
        self.base_dn = self.config.get('DHCP', 'dhcp_basedn')
        self.search_scope = 2 # ldap.SUB
        self.retrieve_attr = None
        self.dhcp_subnet_class = 'dhcpSubnet'
        self.dhcp_conf_suffix = self.config.get('DHCP', 'dhcp_conf_suffix', '-config')
        self.dhcp_server = dhcp_server
        self.dhcp_service_name = self.dhcp_server + self.dhcp_conf_suffix
        self.dhcp_service = self._get_dhcp_service(self.dhcp_server)
        self.dhcp_service_dn = self.dhcp_service['data'][0].__getitem__(0)
        
    def _get_dhcp_service(self, dhcp_server):
        """Retrieve a DHCP service object."""
        service = SpokeDHCPService()
        result = service.get(dhcp_server)
        if result['data'] == []:
            msg = "Can't find DHCP service for %s" % dhcp_server
            raise error.NotFound(msg)          
        return result
    
    def _is_greater_ip_than(self, start_ip, stop_ip):
        """Ensure the last ip is greater than the first."""
        start_ip_list = start_ip.split('.')
        stop_ip_list = stop_ip.split('.')
        index = 0
        while index < len(start_ip_list):
            if start_ip_list[index] != stop_ip_list[index]:
                # Found non match
                if int(start_ip_list[index]) > int(stop_ip_list[index]):
                    msg = '%s is greater than %s' % (start_ip, stop_ip)
                    self.log.error(msg)
                    raise error.InputError(msg)
                    # We only care about the first match
                break
            index = index + 1 
        return start_ip, stop_ip 
        
    def create(self, subnet, mask, start_ip=None, stop_ip=None):
        """Create a DHCP subnet; return DHCP subnet objects."""
        subnet = common.validate_ip_address(subnet)
        filter = 'cn=%s' % subnet
        if not common.is_number(mask):
            msg = 'Subnet mask must be an integer, dotted decimal (or any other\
 notation) is not allowed'
            self.log.error(msg)
            raise error.InputError(msg)
        mask = str(mask)
        if start_ip and not stop_ip:
            msg = 'A range must include a start and stop IP address'
            self.log.error(msg)
            raise error.InputError(msg)
        if start_ip is not None:
            start_ip = common.validate_ip_address(start_ip)
            stop_ip = common.validate_ip_address(stop_ip)
            start_ip, stop_ip = self._is_greater_ip_than(start_ip, stop_ip)
            
        dn = 'cn=%s,%s' % (subnet, self.dhcp_service_dn)
        dn_attr = {'objectClass': ['top', self.dhcp_subnet_class],
                   'cn': [subnet],
                   'dhcpNetMask': [mask]}
        if start_ip is not None:
            dn_attr['dhcpRange'] = start_ip + ' ' + stop_ip
        dn_info = [(k, v) for (k, v) in dn_attr.items()]
        result = self._create_object(dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result
        
    def get(self, subnet):
        """Search for a DHCP subnet; return a results list."""
        subnet = common.validate_ip_address(subnet)
        filter = 'cn=%s' % subnet
        dn = 'cn=%s,%s' % (subnet, self.dhcp_service_dn)
        result = self._get_object(dn, self.search_scope, filter)
        self.log.debug('Result: %s' % result)
        return result
    
    def delete(self, subnet):
        """Delete a DHCP subnet; return True."""
        filter = 'cn=%s' % subnet
        dn = 'cn=%s,%s' % (subnet, self.dhcp_service_dn)
        result = self._delete_object(dn)
        self.log.debug('Result: %s' % result)
        return result
    
class SpokeDHCPGroup(SpokeLDAP):
    
    """Provide CRUD methods to DHCP group objects."""
    
    def __init__(self, dhcp_server):
        """Get config, setup logging and LDAP connection."""
        SpokeLDAP.__init__(self)
        self.config = config.setup()
        self.log = logger.setup(self.__module__)
        self.base_dn = self.config.get('DHCP', 'dhcp_basedn')
        self.search_scope = 2 # ldap.SUB
        self.retrieve_attr = None
        self.dhcp_group_class = 'dhcpGroup'
        self.dhcp_options_class = 'dhcpOptions'
        self.dhcp_conf_suffix = self.config.get('DHCP', 'dhcp_conf_suffix', '-config')
        self.service_name = dhcp_server + self.dhcp_conf_suffix
        self.service_dn = 'cn=%s,%s' % (self.service_name, self.base_dn)
        
    def create(self, group_name):
        """Create DHCP group; return DHCP group objects."""   
        filter = 'cn=%s' % group_name
        dn = 'cn=%s,%s' % (group_name, self.service_dn)
        dn_attr = {'objectClass': ['top', self.dhcp_group_class,
                                   self.dhcp_options_class],
                   'cn': [group_name]}
        dn_info = [(k, v) for (k, v) in dn_attr.items()]
        result = self._create_object(dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result
    
    def get(self, group_name):
        """Search for a DHCP group_name; return a results list."""
        filter = 'cn=%s' % group_name
        dn = 'cn=%s,%s' % (group_name, self.service_dn)
        result = self._get_object(dn, self.search_scope, filter)
        self.log.debug('Result: %s' % result)
        return result
    
    def delete(self, group_name):
        """Delete a DHCP group; return True."""
        filter = 'cn=%s' % group_name
        dn = 'cn=%s,%s' % (group_name, self.service_dn)
        result = self._delete_object(dn)
        self.log.debug('Result: %s' % result)
        return result
    
class SpokeDHCPHost(SpokeLDAP):
    
    """Provide CRUD methods to DHCP host objects."""
    
    def __init__(self, dhcp_server, group_name):
        """Get config, setup logging and LDAP connection."""
        SpokeLDAP.__init__(self)
        self.config = config.setup()
        self.log = logger.setup(self.__module__)
        self.base_dn = self.config.get('DHCP', 'dhcp_basedn')
        self.search_scope = 2 # ldap.SUB
        self.retrieve_attr = None
        self.dhcp_host_class = 'dhcpHost'
        self.dhcp_options_class = 'dhcpOptions'
        self.dhcp_conf_suffix = self.config.get('DHCP', 'dhcp_conf_suffix', '-config')
        self.dhcp_server = dhcp_server
        self.dhcp_group_name = group_name
        group = self._get_dhcp_group(self.dhcp_server, self.dhcp_group_name)
        self.dhcp_group_dn = group['data'][0].__getitem__(0)
        
    def _get_dhcp_service(self, dhcp_server):
        """Retrieve a DHCP service object."""
        service = SpokeDHCPService()
        result = service.get(dhcp_server)
        if result['data'] == []:
            msg = "Can't find DHCP service for %s" % dhcp_server
            raise error.NotFound(msg)          
        return result
        
    def _get_dhcp_group(self, dhcp_server, group_name):
        """Retrieve a DHCP group object."""
        group = SpokeDHCPGroup(dhcp_server)
        result = group.get(group_name)
        if result['data'] == []:
            msg = "Can't find DHCP group for %s" % dhcp_server
            raise error.NotFound(msg)          
        return result
        
    def create(self, host_name):
        """Create DHCP host; return DHCP host objects."""
        filter = 'cn=%s' % host_name
        if self.dhcp_server == host_name:
            msg = 'DHCP hostname %s with same name as DHCP server %s' % \
                                                (host_name, self.dhcp_server)
            self.log.error(msg)
            raise error.InputError(msg) 
        dn = 'cn=%s,%s' % (host_name, self.dhcp_group_dn)
        dn_attr = {'objectClass': ['top', self.dhcp_host_class,
                                   self.dhcp_options_class],
                   'cn': [host_name]}
        dn_info = [(k, v) for (k, v) in dn_attr.items()]
        result = self._create_object(dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result
    
    def get(self, host_name):
        """Search for a DHCP host_name; return a results list."""
        dn = 'cn=%s,%s' % (host_name, self.dhcp_group_dn)
        filter = 'cn=%s' % host_name
        result = self._get_object(dn, self.search_scope, filter)
        self.log.debug('Result: %s' % result)
        return result
    
    def delete(self, host_name):
        """Delete a DHCP host; return True."""
        filter = 'cn=%s' % host_name
        dn = 'cn=%s,%s' % (host_name, self.dhcp_group_dn)
        result = self._delete_object(dn)
        self.log.debug('Result: %s' % result)
        return result
    
class SpokeDHCPAttr(SpokeLDAP):
    
    """Provide CRUD methods to DHCP attributes."""
    
    def __init__(self, dhcp_server, group=None, host=None):
        """Get config, setup logging and LDAP connection."""
        SpokeLDAP.__init__(self)
        self.config = config.setup()
        self.log = logger.setup(self.__module__)
        self.base_dn = self.config.get('DHCP', 'dhcp_basedn')
        self.search_scope = 2 # ldap.SUB
        self.retrieve_attr = None
        self.dhcp_options_class = 'dhcpOptions'
        self.dhcp_service_class = 'dhcpService'
        self.dhcp_option_attr = 'dhcpOption'
        self.dhcp_conf_suffix = self.config.get('DHCP', 'dhcp_conf_suffix', '-config')
        self.dhcp_server = dhcp_server
        self.service_name = self.dhcp_server + self.dhcp_conf_suffix
        self.dhcp_service = self._get_dhcp_service(self.dhcp_server)
        self.dhcp_service_dn = self.dhcp_service['data'][0].__getitem__(0)
        self.target_dn = self.dhcp_service_dn
        if group is not None:
            self.dhcp_group_name = group
            self.dhcp_group = self._get_dhcp_group(self.dhcp_server, \
                                                        self.dhcp_group_name)
            self.dhcp_group_dn = self.dhcp_group['data'][0].__getitem__(0)
            self.target_dn = self.dhcp_group_dn
        if host is not None:
            self.dhcp_host_name = host
            self.dhcp_host = self._get_dhcp_host(self.dhcp_server, \
                                    self.dhcp_group_name, self.dhcp_host_name)
            self.dhcp_host_dn = self.dhcp_host['data'][0].__getitem__(0)
            self.target_dn = self.dhcp_host_dn
    
    def _get_dhcp_service(self, dhcp_server):
        """Retrieve a DHCP service object."""
        service = SpokeDHCPService()
        result = service.get(dhcp_server)
        if result['data'] == []:
            msg = "Can't find DHCP service for %s" % dhcp_server
            raise error.NotFound(msg)          
        return result
    
    def _get_dhcp_group(self, dhcp_server, group_name):
        """Retrieve a DHCP group object."""
        group = SpokeDHCPGroup(dhcp_server)
        result = group.get(group_name)
        if result['data'] == []:
            msg = "Can't find DHCP group for %s" % dhcp_server
            raise error.NotFound(msg)          
        return result
    
    def _get_dhcp_host(self, dhcp_server, group_name, host_name):
        """Retrieve a DHCP host object."""
        host = SpokeDHCPHost(dhcp_server, group_name)
        result = host.get(host_name)
        if result['data'] == []:
            msg = "Can't find DHCP host for %s in group %s" % (dhcp_server, \
                                                                    group_name)
            raise error.NotFound(msg)          
        return result
        
    def create(self, attr_type, attr_value):
        """Create DHCP attribute; return DHCP attribute value."""
        dn = self.target_dn
        dn_info = []
        dn_info.append((ldap.MOD_ADD, attr_type, attr_value))
        #new_attrs = {attr_type: attr_value}
        #self.log.debug('Adding DHCP attribute %s=%s to %s: ' % \
        #              (attr_type, attr_value, dn))
        result = self._create_object(dn, dn_info)
        #result = self._modify_attributes(dn, new_attrs)
        self.log.debug('Result: %s' % result)
        return result
    
    def get(self, attr_type, attr_value=None):
        """Fetch DHCP attribute; return DHCP attribute value."""
        scope = 2 #ldap.SCOPE_SUB
        retrieve_attr = [attr_type]
        
        filter = '%s=*' % attr_type
        if attr_value is not None:
            filter = '%s=%s' % (attr_type, attr_value)
        dn = self.target_dn
        result = self._get_object(dn, scope, filter, attr=retrieve_attr)
        self.log.debug('Result: %s' % result)
        return result
    
    def delete(self, attr_type, attr_value):
        """Delete a DHCP attribute; return True."""
        filter = '%s=%s' % (attr_type, attr_value)
        dn = self.target_dn
        self.log.debug('Deleting DHCP attribute %s %s on %s' % 
                      (attr_type, attr_value, dn))
        dn_info = [(ldap.MOD_DELETE, attr_type, attr_value)]
        result = self._delete_object(dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result
