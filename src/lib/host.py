"""Host container management module.

Classes:
SpokeHost - create/modify/get/delete SpokeHost objects.
SpokeUUID - create/modify/get/delete SpokeUUID objects.

Exceptions:
NotFound - raised on failure to find an object when one is expected.
AlreadyExists -raised on attempts to create an object when one already exists.
InputError - raised on invalid input.
ConfigError - raised when a configuration problem is found.
IncrementError - raised on a failure to increment a resource.

ldap.MOD_DELETE = 1
ldap.MOD_ADD = 0
"""
# core modules
import ConfigParser

# own modules
import error
import config
import common
import logger
from directory import SpokeLDAP
from org import SpokeOrg

class SpokeHost(SpokeLDAP):
    
    def __init__(self, org_name):    
        """Get config, setup logging and LDAP connection."""
        SpokeLDAP.__init__(self)
        self.config = config.setup()
        self.log = logger.setup(__name__)
        self.search_scope = 2 # ldap.SUB
        self.retrieve_attr = None
        self.org_name = org_name
        self.org = self._get_org(self.org_name)
        self.org_dn = self.org['data'][0].__getitem__(0)
        self.org_attrs = self.org['data'][0].__getitem__(1)
        self.org_classes = self.org_attrs['objectClass']
        self.container_attr = self.config.get('ATTR_MAP', 'container_attr', 'ou')
        self.host_container = self.config.get('HOST', 'host_container', 'hosts')
        self.host_container_dn = '%s=%s,%s' % (self.container_attr, \
                                            self.host_container, self.org_dn)
        self.host_class = self.config.get('HOST', 'host_class', 'aenetHost')
        self.host_key = self.config.get('HOST', 'host_key', 'cn')
        self.host_uuid_attr = self.config.get('HOST', 'host_uuid_attr', 'aenetHostUUID')
        self.host_name_attr = self.config.get('HOST', 'host_name_attr', 'aenetHostName')
        self.host_cpu_attr = self.config.get('HOST', 'host_cpu_attr', 'aenetHostCPU')
        self.host_mem_attr = self.config.get('HOST', 'host_mem_attr', 'aenetHostMem')
        self.host_extra_opts_attr = self.config.get('HOST', 
                                'host_extra_opts_attr', 'aenetHostExtraOpts')
        self.host_family_attr = self.config.get('HOST', 'host_family_attr', 'aenetHostFamily')
        self.host_network_layout_attr = self.config.get('HOST', 
                        'host_network_layout_attr', 'aenetHostNetworkLayout')
        self.host_storage_layout_attr = self.config.get('HOST', 
                        'host_storage_layout_attr', 'aenetHostStorageLayout')
        self.host_type_attr = self.config.get('HOST', 'host_type_attr', 'aenetHostType')
    
    def _get_org(self, org_name):
        """Retrieve our org object."""
        org = SpokeOrg()
        result = org.get(org_name)
        if result['data'] == []:
            msg = "Can't find org %s" % org_name
            raise error.NotFound(msg)          
        return result

    def create(self, host_name, host_uuid, host_mem, host_cpu, host_family, 
               host_type, host_storage_layout, host_network_layout, 
               host_extra_opts=None):
        """Create a VM Host; return a VM Host search result."""
        host_name = common.validate_hostname(host_name)
        host_uuid = common.validate_uuid(host_uuid)
        host_mem = common.validate_mem(host_mem)
        host_cpu = common.validate_cpu(host_cpu)
        host_family = common.validate_host_family(host_family)
        # Verifies that the interfaces referenced in the storage layout
        # exist in the configuration file
        host_storage_layout = self._validate_storage_layout(host_storage_layout)
        # and for network layouts.
        host_network_layout = self._validate_network_layout(host_network_layout)
        host_type = common.validate_host_type(host_type)
        host_extra_opts = common.is_shell_safe(host_extra_opts)
            
        filter = '%s=%s' % (self.host_key, host_name)
        dn = '%s=%s,%s' % (self.host_key, host_name, self.host_container_dn)
        dn_attr = {'objectClass': ['top', self.host_class],
                   self.host_key: [host_name],
                   self.host_cpu_attr: [str(host_cpu)],
                   self.host_mem_attr: [str(host_mem)],
                   self.host_family_attr: [host_family],
                   self.host_name_attr: [host_name],
                   self.host_network_layout_attr: [host_network_layout],
                   self.host_storage_layout_attr: [host_storage_layout],
                   self.host_type_attr: [host_type],
                   self.host_uuid_attr: [host_uuid],
                   }
        if host_extra_opts is not None:
            dn_attr[self.host_extra_opts_attr] = [host_extra_opts]
            
        dn_info = [(k, v) for (k, v) in dn_attr.items()]
        
        msg = 'Creating %s with attributes %s' % (dn, dn_info)
        self.log.debug(msg)
        result = self._create_object(dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result
    
    def get(self, host_name=None):
        """Search for a Host entry; return a search result."""
        dn = self.host_container_dn
        if host_name is None:
            filter = '%s=*' % self.host_key
        else:
            host_name = common.validate_hostname(host_name)
            filter = '%s=%s' % (self.host_key, host_name)
        msg = 'Searching at %s with scope %s and filter %s' % \
            (dn, self.search_scope, filter)
        self.log.debug(msg)
        result = self._get_object(dn, self.search_scope, filter)
        self.log.debug('Result: %s' % result)
        return result
        
    def delete(self, host_name):
        """Delete a Host entry; return an empty search result."""
        host_name = common.validate_hostname(host_name)
        dn = '%s=%s,%s' % (self.host_key, host_name, self.host_container_dn)
        msg = 'Deleting %s' % dn
        self.log.debug(msg)
        result = self._delete_object(dn)
        self.log.debug('Result: %s' % result)
        return result
    
    def _validate_network_layout(self, host_network_layout):
        """Verify that network layout exists in config file and that all
        interfaces referenced in the layout are present as interface layouts."""
        try:
            interfaces_raw = self.config.get('NETWORK_LAYOUTS', 
                                             host_network_layout)
            interfaces = interfaces_raw.split(',')
        except error.ConfigError as e:
            msg = "the network layout %s is not present in config file." % e
            raise error.InputError, msg
        
        try:
            interface_layouts_raw = self.config.items('INTERFACE_LAYOUTS')
            # Let's change this horrid list of tuples into a nice dictionary
            interface_layouts = {}
            for l in interface_layouts_raw:
                interface_layouts[l[0]] = l[1]
            # Check that all interface layouts in our network layout 
            # exist in our dictionary of interface layouts
            for i in interfaces:
                if i in interface_layouts:
                    pass
                else:
                    msg = "%s not found in [INTERFACE_LAYOUTS] section." % i
                    raise error.ConfigError, msg
        except ConfigParser.NoSectionError:
            msg = "[INTERFACE_LAYOUTS] section missing."
            raise error.ConfigError, msg
        return host_network_layout
        
    def _validate_storage_layout(self, host_storage_layout):
        """Verify that storage layout exists in config file and that all
        devices referenced in the layout are present as device layouts."""
        try:
            disks_raw = self.config.get('STORAGE_LAYOUTS', 
                                             host_storage_layout)
            disks = disks_raw.split(',')
        except error.ConfigError as e:
            msg = "the storage layout %s is not present in config file." % e
            raise error.InputError, msg
        
        try:
            disk_layouts_raw = self.config.items('DISK_LAYOUTS')
            # Let's change this horrid list of tuples into a nice dictionary
            disk_layouts = {}
            for d in disk_layouts_raw:
                disk_layouts[d[0]] = d[1]
            # Check that all disk layouts in our storage layout 
            # exist in our dictionary of disk layouts
            for s in disks:
                if s in disk_layouts:
                    pass
                else:
                    msg = "%s not found in [DISKS_LAYOUTS] section." % s
                    raise error.ConfigError, msg
        except ConfigParser.NoSectionError:
            msg = "[DISKS_LAYOUTS] section missing."
            raise error.ConfigError, msg
        return host_storage_layout
    
class SpokeHostUUID(SpokeLDAP):
    def __init__(self):    
        """Get config, setup logging and LDAP connection."""
        SpokeLDAP.__init__(self)
        self.config = config.setup()
        self.log = logger.setup(__name__)
        self.search_scope = 0 #ldap.SCOPE_BASE
        self.next_uuid_attr = self.config.get('ATTR_MAP','next_uuid_attr', 'aenetHostUUID')
        self.next_uuid_dn = self.config.get('LDAP','basedn')
        self.next_uuid_dn = self.config.get('ATTR_MAP','next_uuid_dn', self.next_uuid_dn)
        self.next_uuid_class = self.config.get('ATTR_MAP','next_uuid_class', 'aenetNextUUID')
        self.next_uuid_start = self.config.get('ATTR_MAP','next_uuid_start', 1)   
        self.next_uuid = self._get_next_uuid_dn()['data']
        self.next_uuid_attrs = self.next_uuid[0].__getitem__(1)
        self.next_uuid_classes = self.next_uuid_attrs['objectClass']
        self.retrieve_attr = [self.next_uuid_attr]
        self.filter = '%s=*' % self.next_uuid_attr
        
    def _get_next_uuid_dn(self):
        """Retrive UUID dn object."""
        dn = self.next_uuid_dn
        result = self._get_object(dn, self.search_scope)
        if result['data'] == []:
            msg = "Cannot locate %s; check your config?" % dn
            raise error.NotFound, msg
        return result

    def create(self, uuid_start=None):
        """Create initial UUID object; return True."""
        if uuid_start:
            self.next_uuid_start = uuid_start
        if not common.is_number(self.next_uuid_start):
            msg = 'next_uuid_start must be an integer'
            raise error.InputError(msg)
        # Now we know it's an integer, make it a string for LDAP's sake
        self.next_uuid_start = str(self.next_uuid_start)
        dn = self.next_uuid_dn
        dn_info = []
        if not self.next_uuid_class in self.next_uuid_classes:
            dn_info.append((0, 'objectClass', self.next_uuid_class))
        if not self.next_uuid_attr in self.next_uuid_attrs:
            dn_info.append((0, self.next_uuid_attr, 
                            self.next_uuid_start))
            
        if dn_info == []:
            msg = 'UUID entry already set on %s.' % dn
            raise error.AlreadyExists(msg)
        self.log.debug('Adding %s to %s ' % (dn_info, dn))     
        result = self._create_object(dn, dn_info)
        result['data'] = [int(result['data'][0][1][self.next_uuid_attr][0])]
        result['msg'] = 'Created UUID:'
        self.log.debug('Result: %s' % result)
        return result
        
    def get(self):
        """Retrieve the next free UUID object; return UUID as integer."""
        dn = self.next_uuid_dn
        filter = '%s=*' % self.next_uuid_attr
        msg = 'Searching at %s with scope %s and filter %s' % \
            (dn, self.search_scope, filter)
        self.log.debug(msg)
        result = self._get_object(dn, self.search_scope, filter, 
                                  self.retrieve_attr)
        if result['data'] == []:
            msg = "Cannot locate a UUID; maybe you need to run create?"
            raise error.NotFound(msg)
        result['data'] = [int(result['data'][0][1][self.next_uuid_attr][0])]
        result['msg'] = 'Found UUID:'
        self.log.debug('Result: %s' % result)
        return result
    
    def modify(self, increment=1):
        """Increment initial UUID object; return list of UUIDs."""
        if not common.is_number(increment):
            msg = 'increment input must be an Integer'
            raise error.InputError, msg
        dn = self.next_uuid_dn
        filter = '%s=*' % self.next_uuid_attr
        
        result = self._get_object(dn, 0, filter, self.retrieve_attr, 
                                  attrs_only=True)
        if result['data'] == []:
            msg = "Cannot locate a UUID; maybe you need to run create?"
            raise error.NotFound(msg)
        
        uuid = int(result['data'][0][1][self.next_uuid_attr][0])
        new_uuid = int(uuid) + int(increment)
        old_attrs = result['data'][0][1]
        new_attrs = old_attrs.copy()
        new_attrs[self.next_uuid_attr] = [str(new_uuid)]
        self.log.debug('Modifying %s from %s to %s' % (dn, old_attrs, new_attrs))
        try:
            result = self._modify_attributes(dn, new_attrs, old_attrs)
        except:
            msg = 'Update of next free UUID to %d failed' % new_uuid
            raise error.IncrementError, msg
        result['data'] = range(uuid, (new_uuid))
        result['msg'] = "Reserved UUIDs: " + str(result['data'])
        self.log.debug('Result: %s' % result)
        return result
               
    def delete(self):
        """Delete UUID object; return True."""
        dn = self.next_uuid_dn
        dn_info = []
        if self.next_uuid_class in self.next_uuid_classes:
            dn_info.append((1, 'objectClass', self.next_uuid_class))
        if self.next_uuid_attr in self.next_uuid_attrs:
            dn_info.append((1, self.next_uuid_attr, None))
            
        if dn_info == []:
            msg = 'No UUID found, nothing to delete.'
            raise error.NotFound(msg)
        self.log.debug('Deleting %s from %s ' % (dn_info, dn))
        result = self._delete_object(dn, dn_info)
        result['msg'] = 'Deleted UUID:'
        self.log.debug('Result: %s' % result)
        return result
      
class SpokeHostXen(SpokeHost):
#    def __init__(self, hv_uri):
#        '''Get some basic config and connect to hypervisor'''
#        self.hv_uri = hv_uri
#        self.conn = libvirt.open(self.hv_uri)
#        if self.conn == None:
#            print 'Failed to open connection to the hypervisor'
#        self.config = config.setup('/usr/local/data/spoke/etc/spoke.conf')
    pass
    
class SpokeHostKvm(SpokeHost):
    def __init__(self, hv_uri):
        print("USING KVM CLASS")
    
