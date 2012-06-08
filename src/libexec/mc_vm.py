#!/usr/bin/env python
import sys

import config
import logger
import mc_helper as mc

# TODO This only works for Xen until we can hide VM Storage types in the vm_storage module
# TODO Implement access to vm power via vm host modify (e.g. vm.modify(vm_name, power=on).
from vm_storage import SpokeVMStorageXen

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
    except Exception as e:
        mc.fail(e)

    if request['action'] != 'search':
        try:
            vm_name = request['data']['hostname']
        except KeyError:
            mc.fail("Missing input hostname", 2)
            
    if request['action'] == 'create':
        try:
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
            mc.info('Creating VM %s' % vm_name)
            mc.reply = vm.create(vm_name, vm_uuid, vm_mem, vm_cpu, vm_family,
               vm_storage_layout, vm_network_layout, vm_install)
        except Exception as e:
            mc.fail(e)
    elif request['action'] == 'search':
        try:
            vm_name = request['data']['hostname']
        except KeyError:
            vm_name = None
        try:
            mc.info('Searching for VM %s' % vm_name)
            mc.reply = vm.get(vm_name)
        except Exception as e:
            mc.fail(e)
    elif request['action'] == 'delete':
        try:
            mc.info('Deleting VM %s' % vm_name)
            mc.reply = vm.delete(vm_name)
        except Exception as e:
            mc.fail(e)
    else:
        msg = "Unknown action: " + request['action']
        mc.fail(msg, 2)
    sys.exit(0)
