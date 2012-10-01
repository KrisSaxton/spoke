#!/usr/bin/env python
# core modules
import sys
# own modules
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.logger as logger
import mc_helper as mc

# TODO This only works for Xen until we can hide VM Storage types in the vm_storage module
# TODO Implement access to vm power via vm host modify (e.g. vm.modify(vm_name, power=on).
from spoke.lib.vm_storage import SpokeVMStorageXen

config_file = '/usr/local/pkg/spoke/etc/spoke.conf'
config = config.setup(config_file)
    
if __name__ == '__main__':
    log = logger.setup('main', verbose=False, quiet=True)
    mc = mc.MCollectiveAction()
    request = mc.request()
    try:
        hv_uri = config.get('VM', 'hv_uri')
        mc.info('Connecting to hypervisor URI %s' % hv_uri)
        vm = SpokeVMStorageXen(hv_uri)
    except error.SpokeError, e:
        mc.fail(e.msg, e.exit_code)
            
    if request['action'] == 'create':
        vm_name             = request['data']['hostname']
        vm_uuid             = request['data']['uuid']
        vm_mem              = request['data']['mem']
        vm_cpu              = request['data']['cpu']
        vm_family           = request['data']['family']
        vm_storage_layout   = request['data']['storage_layout']
        vm_network_layout   = request['data']['network_layout']
        try:
            vm_install = request['data']['install']
        except KeyError:
            vm_install = None
        try:
            mc.data = vm.create(vm_name, vm_uuid, vm_mem, vm_cpu, vm_family,
               vm_storage_layout, vm_network_layout, vm_install)
        except error.SpokeError, e:
            mc.fail(e.msg, e.exit_code)
    elif request['action'] == 'search':
        try:
            vm_name = request['data']['hostname']
        except KeyError:
            vm_name = None
        try:
            mc.data = vm.get(vm_name)
        except error.SpokeError, e:
            mc.fail(e.msg, e.exit_code)
    elif request['action'] == 'delete':
        vm_name = request['data']['hostname']
        try:
            mc.data = vm.delete(vm_name)
        except error.SpokeError, e:
            mc.fail(e.msg, e.exit_code)
    else:
        msg = "Unknown action: " + request['action']
        mc.fail(msg, 2)
    log.info('Result via Mcollective: %s' % mc.data)
    sys.exit(0)
