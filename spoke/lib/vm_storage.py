'''Virtual machine definition storage management module.
Classes:
SpokeVMStorage - creation/deletion/retrieval of virtual machine definitions.
SpokeVMStorageXen - creation/deletion/retrieval of Xen guest definitions.
SpokeVMStorageKvm - creation/deletion/retrieval of kvm guest definitions.

Exceptions:
NotFound - raised on failure to find an object when one is expected.
InputError - raised on invalid input.
SearchError - raised to indicate unwanted search results were returned.
VMRunning - raised on failed actions due to a VM being in a running state.
ValidationError -raised when an action completes OK but validation fails.
LibvirtError - raised on failed libvirt actions.
'''
# core modules
import sys
import fcntl
import array
import socket
import struct
import logging
import traceback
import xml_helper as xml
from operator import itemgetter

# own modules
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.common as common

# 3rd party libs
try:
    import libvirt
except:
    msg = 'Failed to import libvirt'
    raise error.LibvirtError(msg)


class SpokeVMStorage:
    
    """Provide CRUD methods to Virtual machine definition objects."""
    
    def __init__(self):
        """Get config and setup loggings."""
        self.config = config.setup()
        self.log = logging.getLogger(__name__)
        #This block gets interface and interface type from config file
        self._lookupInterfaces()
        #And this one does the same for disks.
        self._lookupDisks()
        self.search_headers = self.config.get('VM', 'search_headers', 'name,uuid')
        self.headers = self.search_headers.split(',')
        def _error_handler(self, err):
            msg = "Ignoring Libvirt error %s)" % err
            pass
        # Prevent libvirt errors from reaching the console
        libvirt.registerErrorHandler(_error_handler, None)
        
    def create(self, vm_name, vm_uuid, vm_mem, vm_cpu, vm_family, vm_storage_layout,
               vm_network_layout, vm_install=False, vm_disks=None, vm_interfaces=None):
        """Define a new VM and add to hypervisor's store (does not start)."""
        try:
            vm_name = common.validate_hostname(vm_name)
            vm_cpu = common.validate_cpu(vm_cpu)
            vm_mem = common.validate_mem(vm_mem)
            #vm_type = common.validate_host_type(vm_type)
            vm_family = common.validate_host_family(vm_family)
            #vm_extra_opts = common.is_shell_safe(vm_extra_opts)
            vm_uuid = common.validate_uuid(vm_uuid)
        except error.InputError as e:
            self.log.error(e)
            raise e
        
        try:
            self.conn.lookupByName(vm_name)
        except libvirt.libvirtError:
            pass
        else:
            msg = "Domain %s already exists, cannot create." % vm_name
            raise error.AlreadyExists(msg)
        
        # Create a UUID in hypervisor format
        formatted_uuid = self._format_uuid(vm_uuid)
        
        #-1 means XEN will give the right XenID when it starts
        vm_id=-1
        
        #Initial xml structure
        doc = xml.createDoc("doc")
        domain = xml.createElement(doc, "domain", {"type": vm_family})
        #Variable config options
        #xml.createChild(doc, domain, "arch name", None, 'i686')
        xml.createChild(doc, domain, "name", None, vm_name)
        xml.createChild(doc, domain, "memory", None, vm_mem)
        xml.createChild(doc, domain, "currentMemory", None, vm_mem)
        xml.createChild(doc, domain, "vcpu", None, vm_cpu)
        xml.createChild(doc, domain, "uuid", None, formatted_uuid)
        
        #fixed(ish) config options
        os = xml.createChild(doc, domain, "os", None, None)
        #ks - the below is going to have to change for 64bit
        xml.createChild(doc, os, "type", {"arch": "i686"}, "hvm")
        xml.createChild(doc, domain, "clock", {"offset": "utc"}, None)
        xml.createChild(doc, domain, "on_poweroff", None, "destroy")
        xml.createChild(doc, domain, "on_reboot", None, "restart")
        xml.createChild(doc, domain, "on_crash", None, "restart")
        
        devices = xml.createChild(doc, domain, "devices", None, None)
        console = xml.createChild(doc, devices, "console", {"type": "pty"}, None)
        xml.createChild(doc, console, "target", {"type": "xen", "port": "0"}, None)
        #ks
        #xml.createChild(doc, devices, "input", {"type": "mouse", "bus": "xen"}, None)
        # TODO Change the port such that it is associated with the UUID and change listen to internal interface only
        xml.createChild(doc, devices, "graphics", {"type": "vnc", "port": "-1", "autoport": "yes", "listen": "0.0.0.0"}, None)
        xml.createChild(doc, devices, "emulator", None, "/usr/lib/xen/bin/qemu-dm")
        
#        #parse disk info
#        for item in vm_disks:
#            #local1 means hda and vg01
#            if item[0] == "local1":
#                disk = xml.createChild(doc, devices, "disk", {"type": "block", "device": "disk"}, None)
#                xml.createChild(doc, disk, "driver", {"name": "phy"}, None)
#                xml.createChild(doc, disk, "source", {"dev": "/dev/vg01/%s" % vm_name}, None)
#                xml.createChild(doc, disk, "target", {"dev": "hda", "bus": "ide"}, None)
#            #local2 means hdb and vg02
#            if item[0] == "local2":
#                disk = xml.createChild(doc, devices, "disk", {"type": "block", "device": "disk"}, None)
#                xml.createChild(doc, disk, "driver", {"name": "phy"}, None)
#                xml.createChild(doc, disk, "source", {"dev": "/dev/vg01/ko-test-02"}, None)
#                xml.createChild(doc, disk, "target", {"dev": "hdb", "bus": "ide"}, None)                                                      

        if vm_disks is not None:
            for item in vm_disks:
                if item[0] == "local1":
                    disk = xml.createChild(doc, devices, "disk", {"type": "block", "device": "disk"}, None)
                    xml.createChild(doc, disk, "driver", {"name": "phy"}, None)
                    xml.createChild(doc, disk, "source", {"dev": "/dev/vg01/%s" % vm_name}, None)
                    xml.createChild(doc, disk, "target", {"dev": "hda", "bus": "ide"}, None)
                #local2 means hdb and vg02
                if item[0] == "local2":
                    disk = xml.createChild(doc, devices, "disk", {"type": "block", "device": "disk"}, None)
                    xml.createChild(doc, disk, "driver", {"name": "phy"}, None)
                    xml.createChild(doc, disk, "source", {"dev": "/dev/vg02/%s" % vm_name}, None)
                    xml.createChild(doc, disk, "target", {"dev": "hdb", "bus": "ide"}, None)                                                      

        elif vm_storage_layout is not None:
            try:
                disks = self.dtypes[vm_storage_layout]
            except KeyError as e:
                msg = "The disk type %s is not present in config file." % e
                raise error.InputError, msg
            for item in disks:
                item = common.validate_disks_in_conf(self.dnames[item])
                hv_dev = item[0] + "/" + vm_name
                dom_dev = item[1]
                disk = xml.createChild(doc, devices, "disk", {"type": "block", "device": "disk"}, None)
                xml.createChild(doc, disk, "driver", {"name": "phy"}, None)
                xml.createChild(doc, disk, "source", {"dev": hv_dev}, None)
                xml.createChild(doc, disk, "target", {"dev": dom_dev, "bus": "ide"}, None)                                                      

        #parse interface info
        if vm_interfaces is not None:
            for interface in vm_interfaces:
                #get input from interface list
                bridge = int( interface[0].lstrip('breth') )
                mac = interface[1]
                source_interface = interface[2]
                
                interface = xml.createChild(doc, devices, "interface", {"type": "bridge"}, None)
                xml.createChild(doc, interface, "mac", {"address": mac}, None)
                xml.createChild(doc, interface, "source", {"bridge": source_interface}, None)
                xml.createChild(doc, interface, "script", {"path": "vif-bridge"}, None)
                xml.createChild(doc, interface, "target", {"dev": "vif%i.%i" % (vm_id, bridge)}, None)
        elif vm_network_layout is not None:
            try:
                interfaces = self.ifacedef[vm_network_layout]
            except KeyError:
                msg = "The interface type %s is not present in config file." % vm_network_layout
                raise error.InputError(msg)
            
            # Ensure that br0,x is done first as xen cares about order in xml.
            interfaces = sorted(interfaces, key=itemgetter(0))
            for interface in interfaces:
                interface = common.validate_interfaces_in_conf(interface)
                iface_number = int( interface[0].lstrip('breth') )
                if iface_number == 0:
                    boot_mac = common.mac_from_uuid(vm_uuid, iface_number)                   
                    boot_int = interface[1]
                mac = common.mac_from_uuid(vm_uuid, iface_number)
                                   
                source_interface = interface[1]
                # KS enumerate avail interfaces via facter, not remote socket op 
                #if not source_interface in self._all_interfaces():
                #    msg = "%s does not exist on this machine so we cant bridge to it!" % source_interface
                #    raise error.InsufficientResource, msg
                                    
                interface = xml.createChild(doc, devices, "interface", {"type": "bridge"}, None)
                xml.createChild(doc, interface, "mac", {"address": mac}, None)
                xml.createChild(doc, interface, "source", {"bridge": source_interface}, None)
                xml.createChild(doc, interface, "script", {"path": "vif-bridge"}, None)
                xml.createChild(doc, interface, "target", {"dev": "vif%i.%i" % (vm_id, iface_number)}, None)
        
        if vm_install: # Add network boot lines
            xml.createChild(doc, domain, "bootloader", None, "/usr/sbin/pypxeboot" )
            try:
                xml.createChild(doc, domain, "bootloader_args", None, "--udhcpc=/usr/local/pkg/udhcp/sbin/udhcpc --interface=%s mac=%s --label=install-aethernet" % (boot_int, boot_mac) )
            except UnboundLocalError:
                msg = "In config there must be an interface br0 as the provisioning interface!"
                raise error.ConfigError(msg)
        else:
            xml.createChild(doc, domain, "bootloader", None, "/usr/bin/pygrub" )

        try:
            out = self.conn.defineXML(xml.out(doc))
        except Exception, e:
            trace = traceback.format_exc()
            raise error.LibvirtError(e, trace)
        if out == None:
            msg = "Failed to create VM definition for %s" % vm_name
            self.log.error(msg)
            sys.exit(1)
        
        #print xml.out(doc) #useful for debug
        result = self.get(vm_name)
        if result['exit_code'] == 0 and result['count'] == 1:
            result['msg'] = "Created %s:" % result['type']
            self.log.debug('Result: %s' % result)
            return result
        else:
            msg = 'Create operation returned OK, but unable to find object'
            raise error.ValidationError(msg)
        return result
    
    def get(self, vm_name=None):
        """get info on virtual machine(s)"""
        data = []
        #if no vm name get all
        if vm_name == None:
            #get list of all inactive and active
            vm_defined_list = self.conn.listDefinedDomains()
            vm_active_list = self.conn.listDomainsID()
            #iterate over these lists and get some info on each domain
            for vmid in vm_active_list:
                dom = self.conn.lookupByID(vmid)
                data.append(dom.XMLDesc(3))
            for name in vm_defined_list:
                dom = self.conn.lookupByName(name)
                data.append(dom.XMLDesc(3))
        else:
            vm_name = common.validate_hostname(vm_name)
            try:
                dom = self.conn.lookupByName(vm_name)
            except libvirt.libvirtError:
                result = common.process_results(data, 'VM')
                self.log.debug('Result: %s' % result)
                return result
            info = dom.XMLDesc(3)
            data.append(info)
        #self.conn.close() # Connection closing left to calling app - bad?
        result = common.process_results(data, 'VM')
        self.log.debug('Result: %s' % result)
        return result
    
    def delete(self, vm_name):
        '''Remove a definition from store, will fail on xen if machine is running'''
        if vm_name == None:
            msg = "InputError: vm name must be specified with delete."
            raise error.InputError(msg)
        try:
            dom = self.conn.lookupByName(vm_name)
        except libvirt.libvirtError:
            msg = "VM definition for %s doesn't exist, can't delete." % vm_name
            raise error.NotFound(msg)
        try:
            dom.undefine()
        except libvirt.libvirtError:
            msg = "VM %s is running (shutdown first?), can't delete." % vm_name
            raise error.VMRunning(msg)
        #self.conn.close()
        result = self.get(vm_name)
        if result['exit_code'] == 3 and result['count'] == 0:
            result['msg'] = "Deleted %s:" % result['type']
            return result
        else:
            msg = 'Delete operation returned OK, but object still there?'
            raise error.SearchError(msg)
                
    def _lookupState(self, id):
        '''internal, just returns state from state id number'''
        states = {0: "No State", 1: "Running",  2: "Blocked", 3: "Paused",
                   4: "Shutdown", 5: "Powered Off", 6: "Crashed"}
        
        return states[id]
    
    def _lookupInterfaces(self):
        # Gets interface and interface types from the config file
        # and returns them as a dictionary such that 
        # key = val1,val2 returns {'key':[val1, val2]}
        self.interfaces = self.config.items('INTERFACE_LAYOUTS')
        self.interface_types = self.config.items('NETWORK_LAYOUTS')
            
        self.inames = {}
        for item in self.interfaces:            
            self.inames[str(item[0])] = item[1].split(',')
    
        self.ifacedef = {}
        for item in self.interface_types:
            iname_intype = item[1].split(',')
            for iname in iname_intype:
                if iname in self.inames:
                    pass
                else:
                    msg = "%s not found in [INTERFACE_LAYOUTS] section." % iname
                    raise error.InputError, msg
            self.ifacedef[str(item[0])] = item[1].split(',')
        
        for key in self.ifacedef:
            for item in self.ifacedef[key]:
                self.ifacedef[key][self.ifacedef[key].index(item)] = self.inames[item]
                
    def _lookupDisks(self):
        # Gets disk and storage layouts from the config file
        # and returns them as a dictionary such that 
        # key = val1,val2 returns {'key':[val1, val2]}
        self.disks = self.config.items('DISK_LAYOUTS')
        self.disk_types = self.config.items('STORAGE_LAYOUTS')
       
        self.dnames = {}
        for item in self.disks:            
            self.dnames[str(item[0])] = item[1].split(',')
    
        self.dtypes = {}
        for item in self.disk_types:
            dname_intype = item[1].split(',')
            for dname in dname_intype:
                if dname in self.dnames:
                    pass
                else:
                    msg = "%s not found in [DISK_LAYOUTS] section." % dname
                    raise error.InputError, msg
            self.dtypes[str(item[0])] = item[1].split(',')
    
    #Used to check the interfaces on the HV.
    def _all_interfaces(self):
        max_possible = 128  # arbitrary. raise if needed.
        bytes = max_possible * 32
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        names = array.array('B', '\0' * bytes)
        outbytes = struct.unpack('iL', fcntl.ioctl(
            s.fileno(),
            0x8912,  # SIOCGIFCONF
            struct.pack('iL', bytes, names.buffer_info()[0])
        ))[0]
        namestr = names.tostring()
        return [namestr[i:i+32].split('\0', 1)[0] for i in range(0, outbytes, 32)]
    
    def _format_uuid(self, uuid):
        """Takes a single integer uuid and returns a hypervisor uuid string."""
        uuid_format = self.uuid_format
        uuid_list=uuid_format.split("-")
        pad=len(uuid_list[-1])
        last_element=uuid.zfill(pad)
        formatted_uuid=uuid_format.replace(uuid_list[-1], last_element)
        return formatted_uuid 
    
class SpokeVMStorageXen(SpokeVMStorage):
    def __init__(self, hv_uri):
        '''Get some basic config and connect to hypervisor'''
        SpokeVMStorage.__init__(self)
        self.hv_uri = hv_uri     
        self.uuid_format = self.config.get('VM', 'xen_uuid_format', '00000000-0000-0000-0000-XXXXXXXXXXXX')
        try:
            self.conn = libvirt.open(self.hv_uri)
            msg = "Successfully connected to: " + self.hv_uri
            self.log.debug(msg)
        except Exception as e:
            msg = 'Libvirt connection to URI %s failed' % self.hv_uri
            self.log.error('LibvirtError:' + msg)
            self.log.debug('Libvirt exception was: ' + str(e) + '\n' \
+ traceback.format_exc())
            raise error.LibvirtError, msg
        if self.conn == None:
            msg = 'Libvirt connection to URI %s failed' % self.hv_uri
            self.log.error(msg)
            raise error.LibvirtError, msg

    
class SpokeVMStorageKvm(SpokeVMStorage):
    def __init__(self, hv_uri):
        SpokeVMStorage.__init__(self)
        print("USING KVM CLASS")
    
