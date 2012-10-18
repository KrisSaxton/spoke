'''
Note this will need extending  when we want more than just XEN

'''

import re

import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.common as common

version = common.version

config_file = '/usr/local/pkg/spoke/etc/spoke.conf'

try:
    conf = config.setup(config_file)
except error.ConfigError, e:
    raise

hv_uri = conf.get('VM', 'hv_uri')
try:
    vm_types = conf.get('VM', 'vm_types')
except:
    vm_types = 'test,xen,kvm,vmware'
vm_types_re = vm_types.replace(',','|')
    
family = re.compile('^%s' % vm_types_re)
vm_family = family.match(hv_uri)
try:
    vm_family = vm_family.group(0)
except AttributeError as e:
    msg = "not using valid family in hv_uri, must be one of: %s" % vm_types
    raise error.ConfigError(msg)

def store_create(vm_family, vm_name, vm_uuid, vm_mem, vm_cpu,
                vm_storage_layout, vm_network_layout,
                vm_install=False):
    from spoke.lib.vm_storage import SpokeVMStorageXen
    vms = SpokeVMStorageXen(hv_uri)
    try:
        result = vms.create(vm_name, vm_uuid, vm_mem, vm_cpu, vm_family,
                vm_storage_layout, vm_network_layout,
                vm_install)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def store_search(vm_name=None):
    from spoke.lib.vm_storage import SpokeVMStorageXen
    vms = SpokeVMStorageXen(hv_uri)
    try:
        result = vms.get(vm_name)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def store_delete(vm_name):
    from spoke.lib.vm_storage import SpokeVMStorageXen
    vms = SpokeVMStorageXen(hv_uri)
    try:
        result = vms.delete(vm_name)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def power_search(vm_name):
    from spoke.lib.vm_power import SpokeVMPowerXen
    vmp = SpokeVMPowerXen(hv_uri, vm_name)
    try:
        result = vmp.get()
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result    


def power_create(vm_name):
    from spoke.lib.vm_power import SpokeVMPowerXen
    vmp = SpokeVMPowerXen(hv_uri, vm_name)
    try:
        result = vmp.create()
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result    


def power_delete(vm_name):
    from spoke.lib.vm_power import SpokeVMPowerXen
    vmp = SpokeVMPowerXen(hv_uri, vm_name)
    try:
        result = vmp.delete()
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def power_modify(vm_name, state):
    from spoke.lib.vm_power import SpokeVMPowerXen
    vmp = SpokeVMPowerXen(hv_uri, vm_name)
    try:
        result = vmp.modify(state)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result    