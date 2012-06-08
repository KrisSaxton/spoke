#!/usr/bin/env python
import sys
import config
import logger
import mc_helper as mc

# TODO This only works for Xen until we can hide VM Storage types in the vm_storage module
from vm_power import SpokeVMPowerXen

config_file = '/usr/local/pkg/spoke/etc/spoke.conf'
config = config.setup(config_file)
    
if __name__ == '__main__':
    log = logger.setup('main', verbose=False, quiet=True)
    mc = mc.MCollectiveAction()
    request = mc.request()
    try:
        hv_uri = config.get('VM', 'hv_uri')
        vm_name = request['data']['hostname']
        mc.info('Connecting to hypervisor URI %s' % hv_uri)
        vmp = SpokeVMPowerXen(hv_uri, vm_name)
    except Exception as e:
        mc.fail(e)

    if request['action'] == 'search':
        try:
            mc.info('Retrieving power state for VM %s' % vm_name)
            mc.reply = vmp.get()
        except Exception as e:
            mc.fail(e)
            
    elif request['action'] == 'on':
        try:
            mc.info('Powering on VM %s' % vm_name)
            mc.reply = vmp.create()
        except Exception as e:
            mc.fail(e)
    elif request['action'] == 'off':
        try:
            mc.info('Powering off VM %s' % vm_name)
            mc.reply = vmp.delete()
        except Exception as e:
            mc.fail(e)
    elif request['action'] == 'forceoff':
        try:
            mc.info('Powering off (force) VM %s' % vm_name)
            mc.reply = vmp.delete(force=True)
        except Exception as e:
            mc.fail(e)
    elif request['action'] == 'reboot':
        try:
            mc.info('Power cycling VM %s' % vm_name)
            mc.reply = vmp.modify(vm_power_state='reboot')
        except Exception as e:
            mc.fail(e)
    else:
        msg = "Unknown action: " + request['action']
        mc.fail(msg, 2)
    sys.exit(0)
