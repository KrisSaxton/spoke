"""Spoke common libraries.

Classes:
None
Exceptions:
ConfigError - raised when a configuration problem is found.
InputError - raised on invalid input.
"""
# core modules
import re
import string

# own modules
import spoke.lib.error as error

version = '1.0'

def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def is_integer(string):
    try:
        int(string)
        return True
    except ValueError:
        return False
    
def is_shell_safe(string):
    """Ensure input contains no dangerous characters."""
    string = str(string)
    pattern = re.compile('^[-_A-Za-z0-9 \.]+$')
    valid = pattern.match(string)
    if not valid:
        msg = '%s contains illegal characters' % string
        raise error.InputError(msg)
    return string

def validate_filename(filename):
    """Check filename or directory is valid format"""
    pattern = re.compile('^[A-Za-z0-9-_./]')
    valid_file = pattern.search(filename)
    if not valid_file:
        msg = "%s is not a valid filename" % filename
        raise error.InputError, msg
    return filename 

def mac_from_uuid(uuid, iface_num):
    """returns the appropriate mac from a UUID and interface number."""
    #uuid = uuid[24:]
    uuid = int(uuid)
    iface_num = int(iface_num)
    if iface_num < 0 or iface_num > 99:
        msg = "iface_num should be 0-99"
        raise error.InputError, msg
    uuid = "%06d" % uuid
    uuid = uuid[:2] + ":" + uuid[2:4] + ":" + uuid[4:6]
    mac = "02:%s:%02d:00" % (uuid, iface_num)
    return mac

def validate_ip_address(ip):
    """Ensure input is a valid IP address."""
    ip = str(ip)
    pattern = re.compile(r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")
    valid = pattern.match(ip)
    if not valid:
        msg = '%s is not a valid IP address' % ip
        raise error.InputError(msg)
    return ip

def validate_mac(mac):
    """Check MAC address is valid format (matches MAC and TFTP link format)."""
    pattern = re.compile('^([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}$')
    valid_mac = pattern.match(mac)
    if not valid_mac:
        msg = "%s is not a valid MAC Address" % mac
        raise error.InputError, msg
    mac = string.lower(mac)
    return mac

def validate_email_address(email_addr):
    """Ensure input is a valid email address format."""
    email_addr = email_addr.lower()
    pattern = re.compile(r"^[-a-z0-9_.]+@[-a-z0-9]+\.+[a-z]{2,6}")
    valid_email = pattern.match(email_addr)
    if not valid_email:
        msg = '%s is not a valid email address' % email_addr
        raise error.InputError(msg)
    return email_addr

def validate_domain(domain_name):
    msg = '%s is not a valid domain name' % domain_name
    if domain_name is None:
        raise error.InputError(msg)
    domain_name = domain_name.lower()
    if domain_name[-1:] == ".":
        domain_name = domain_name[:-1] # strip dot from the right
    if len(domain_name) > 255:
        raise error.InputError(msg)
    pattern = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    for x in domain_name.split("."):
        valid = pattern.match(x)
        if not valid:
            raise error.InputError(msg)
    return domain_name

def validate_hostname(name):
    if name is None:
        msg = "Please specify a hostname"
        raise error.InputError, msg
    pattern = re.compile('^[-_A-Za-z0-9]+$')
    valid_name = pattern.match(name)
    if not valid_name:
        msg = "%s is not a valid hostname" % name
        raise error.InputError, msg
    return name

def validate_name(name):
    pattern = re.compile('^[-_A-Za-z0-9]+$')
    valid_name = pattern.match(name)
    if not valid_name:
        msg = "%s is not a valid name" % name
        raise error.InputError, msg
    return name

def validate_storage_format(size):
    """Ensure input is a valid storage value."""
    size = str(size)
    pattern = re.compile('^[0-9]{1,3}[kKmMgG]$')
    valid = pattern.match(size)
    if not valid:
        msg = '%s is not a valid storage format' % size
        raise error.InputError(msg)
    return size

def validate_uuid(uuid):
    if uuid is None:
        msg = "Please specify host UUID"
        raise error.InputError, msg
    uuid = str(uuid)
    pattern = re.compile('^[0-9]{1,12}$')
    valid_uuid = pattern.match(uuid)
    if not valid_uuid:
        msg = "%s is not a valid uuid, must be a number between 0 and 999999999999" % uuid
        raise error.InputError, msg
    return uuid

def validate_mem(mem):
    if mem is None:
        msg = "Please specify host memory"
        raise error.InputError, msg
    '''validates memory but also CONVERTS TO KILOBYTES so must be called!'''
    mem = str(mem)
    pattern = re.compile('^[0-9]{2,4}$')
    valid_mem = pattern.match(mem)
    if not valid_mem:
        msg = "%s is not a valid memory size; must be between 10 and 9999" % mem
        raise error.InputError, msg
    return str(int(mem)*1024)

def validate_cpu(cpu):
    if cpu is None:
        msg = "Please specify host cpu"
        raise error.InputError, msg
    cpu = str(cpu)
    pattern = re.compile('^[1|2]$')
    valid_cpu = pattern.match(cpu)
    if not valid_cpu:
        msg = "%s is not a valid cpu size; must be 1 or 2" % cpu
        raise error.InputError, msg
    return cpu

def validate_host_family(family):
    if family is None:
        msg = "Please specify host family; must be xen or kvm or vmware."
        raise error.InputError, msg
    pattern = re.compile('^(test|xen|kvm|vmware)$')
    valid_family = pattern.match(family)
    if not valid_family:
        msg = "%s is not a valid host family; must be xen, kvm or vmware" % family
        raise error.InputError(msg)
    return family

def validate_host_type(type):
    if type is None:
        msg = "Please specify host type; must be phys, full or para."
        raise error.InputError, msg
    pattern = re.compile('^(phys|full|para)$')
    valid_type = pattern.match(type)
    if not valid_type:
        msg = "%s is not a valid host type; must be phys, full or para." % type
        raise error.InputError, msg
    return type

def validate_disks(disks):
    '''validate disks, makes sure we have good list format and contents'''
    if type(disks).__name__ != 'list':
        msg = "Disk input wasn't successfully input as list."
        raise error.InputError, msg
    for item in disks:
        if len(item) != 2:
            msg = "Each Disk must have type and size."
            raise error.InputError, msg
        dsk_type = re.compile('^(local1|local2)$')
        if dsk_type.match(item[0]) == None:
            msg = "Each Disk type must be local1 or local2."
            raise error.InputError, msg
        dsk_size = re.compile('^[0-9]{2}$')
        if dsk_size.match(item[1]) == None:
            msg = "Each Disk size must be 10 to 99."
            raise error.InputError, msg
    return disks
    
def validate_interfaces(interfaces):
    '''validate interfaces, makes sure we have good list format and contents'''
    if type(interfaces).__name__ != 'list':
        msg = "Interface input wasn't successfully input as list."
        raise error.InputError, msg
    for item in interfaces:
        if len(item) != 3:
            msg = "Each Interface must have bridge, mac and source."
            raise error.InputError, msg
        bridge = re.compile('^eth|br[0-9]$')
        if bridge.match(item[0]) == None:
            msg = "Interface bridge %s must be like brX or ethX." % item[0]
            raise error.InputError, msg
        mac = re.compile('^([0-9a-f]{2}[:]){5}[0-9a-f]{2}$')
        if mac.match(item[1]) == None:
            msg = "Interface mac should be lower case hex, colon as seperator."
            raise error.InputError, msg
        source = re.compile('^eth[0-9]$')
        if source.match(item[2]) == None:
            msg = "Interface source must be like eth0"
            raise error.InputError, msg
    return interfaces
    
def validate_interfaces_in_conf(interfaces):
    '''validate interfaces, makes sure we have good list format and contents'''
    if type(interfaces).__name__ != 'list':
        msg = "Interface input wasn't successfully input as list."
        raise error.ConfigError, msg
    if len(interfaces) != 4:
        msg = "Each Interface must have bridge, source, network and netmask."
        raise error.ConfigError, msg
    bridge = re.compile('^eth|br[0-9]$')
    if bridge.match(interfaces[0]) == None:
        msg = "Interface bridge %s must be like brX or ethX." % interfaces[0]
        raise error.ConfigError, msg
    source = re.compile('^eth[0-9]$')
    if source.match(interfaces[1]) == None:
        msg = "Interface source must be like eth0"
        raise error.ConfigError, msg
    # Validate network number
    validate_ip_address(interfaces[2])
    # Validate network mask
    is_number(interfaces[3])
    return interfaces

def validate_disks_in_conf(disks):
    '''validate disks, makes sure we have good list format and contents'''
    if type(disks).__name__ != 'list':
        msg = "Disk input wasn't successfully input as list."
        raise error.ConfigError, msg
    if len(disks) != 2:
        msg = "Each disk must have hv location and dom location."
        raise error.ConfigError, msg
    bridge = re.compile('^/dev/+')
    if bridge.match(disks[0]) == None:
        msg = "Disk hv location must be like /dev/*."
        raise error.ConfigError, msg
    source = re.compile('^hd[a-z]$')
    if source.match(disks[1]) == None:
        msg = "Disk dom location must be like hda"
        raise error.ConfigError, msg
    return disks

def process_results(data, name=None):
    '''Take result data; return full result dictionary object.'''
    result = {}
    result['data'] = data
    if not name:
        thing = 'object'
    else:
        thing = is_shell_safe(name)
    result['type'] = thing
    count = len(data)
    result['count'] = count 
    if count == 0:
        result['exit_code'] = 3    
        result['msg'] = 'No ' + thing + '(s) found'
    else:
        result['exit_code'] = 0
        if count == 1:
            result['msg'] = "Found %s:" % thing
        else:
            result['msg'] = 'Found ' + str(count) + ' ' + thing + 's:'
    return result
