'''
Salt module to expose TFTP management elements of Spoke API
'''

# Import core libs
import re
import logging

# Import salt modules
from salt.exceptions import SaltInvocationError

# Import spoke libs
try:
    import spoke.lib.error as error
    import spoke.lib.config as config
    import spoke.lib.common as common
    from spoke.lib.vm_storage import SpokeVMStorageXen
    from spoke.lib.vm_power import SpokeVMPowerXen
    has_vm = True
except ImportError:
    has_vm = False

log = logging.getLogger(__name__)
version = common.version


def __virtual__():
    '''
    Only load this module if the spoke modules imported correctly
    '''
    if has_vm:
        return 'vm'
    return False


def _salt_config(name):
    value = __opts__['SPOKE.{0}'.format(name)]
    if not value:
        msg = 'missing SPOKE.{0} in config'.format(name)
        raise SaltInvocationError(msg)
    return value


def _spoke_config(config_file):
    try:
        conf = config.setup(config_file)
    except error.ConfigError, e:
        msg = 'Error reading config file {0}'.format(config_file)
        raise SaltInvocationError(msg)
    return conf


#try:
#    vm_types = conf.get('VM', 'vm_types')
#except:
#    vm_types = 'test,xen,kvm,vmware'
#
#vm_types_re = vm_types.replace(',', '|')
#
#family = re.compile('^%s' % vm_types_re)
#vm_family = family.match(hv_uri)
#
#try:
#    vm_family = vm_family.group(0)
#except AttributeError as e:
#    msg = "not using valid family in hv_uri, must be one of: %s" % vm_types
#    raise error.ConfigError(msg)
def store_create(vm_family, vm_name, vm_uuid, vm_mem, vm_cpu,
                 vm_storage_layout, vm_network_layout, vm_install=False):
    try:
        conf = _spoke_config(_salt_config('config'))
        hv_uri = conf.get('VM', 'hv_uri')
        vms = SpokeVMStorageXen(hv_uri)
        result = vms.create(vm_name, vm_uuid, vm_mem, vm_cpu, vm_family,
                            vm_storage_layout, vm_network_layout, vm_install)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def store_search(vm_name=None):
    try:
        conf = _spoke_config(_salt_config('config'))
        hv_uri = conf.get('VM', 'hv_uri')
        vms = SpokeVMStorageXen(hv_uri)
        result = vms.get(vm_name)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def store_delete(vm_name):
    try:
        conf = _spoke_config(_salt_config('config'))
        hv_uri = conf.get('VM', 'hv_uri')
        vms = SpokeVMStorageXen(hv_uri)
        result = vms.delete(vm_name)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def power_search(vm_name):
    try:
        conf = _spoke_config(_salt_config('config'))
        hv_uri = conf.get('VM', 'hv_uri')
        vmp = SpokeVMPowerXen(hv_uri, vm_name)
        result = vmp.get()
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def power_create(vm_name):
    try:
        conf = _spoke_config(_salt_config('config'))
        hv_uri = conf.get('VM', 'hv_uri')
        vmp = SpokeVMPowerXen(hv_uri, vm_name)
        result = vmp.create()
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def power_delete(vm_name):
    try:
        conf = _spoke_config(_salt_config('config'))
        hv_uri = conf.get('VM', 'hv_uri')
        vmp = SpokeVMPowerXen(hv_uri, vm_name)
        result = vmp.delete()
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def power_modify(vm_name, state):
    try:
        conf = _spoke_config(_salt_config('config'))
        hv_uri = conf.get('VM', 'hv_uri')
        vmp = SpokeVMPowerXen(hv_uri, vm_name)
        result = vmp.modify(state)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result
