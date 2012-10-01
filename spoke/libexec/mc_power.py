#!/usr/bin/env python
# core modules
import sys
# own modules
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.logger as logger
import mc_helper as mc

# TODO This only works for Xen until we can hide VM Storage types in the vm_storage module
from spoke.lib.vm_power import SpokeVMPowerXen

config_file = '/usr/local/pkg/spoke/etc/spoke.conf'
config = config.setup(config_file)
    
if __name__ == '__main__':
    log = logger.setup('main', verbose=False, quiet=True)
    mc = mc.MCollectiveAction()
    request = mc.request()
    try:
        hv_uri = config.get('VM', 'hv_uri')
        vm_name = request['data']['hostname']
        vmp = SpokeVMPowerXen(hv_uri, vm_name)
    except error.SpokeError, e:
        mc.fail(e.msg, e.exit_code)

    if request['action'] == 'search':
        try:
            mc.data = vmp.get()
        except error.SpokeError, e:
            mc.fail(e.msg, e.exit_code)        
    elif request['action'] == 'on':
        try:
            mc.data = vmp.create()
        except error.SpokeError, e:
            mc.fail(e.msg, e.exit_code)
    elif request['action'] == 'off':
        try:
            mc.data = vmp.delete()
        except error.SpokeError, e:
            mc.fail(e.msg, e.exit_code)
    elif request['action'] == 'forceoff':
        try:
            mc.data = vmp.delete(force=True)
        except error.SpokeError, e:
            mc.fail(e.msg, e.exit_code)
    elif request['action'] == 'reboot':
        try:
            mc.data = vmp.modify(vm_power_state='reboot')
        except error.SpokeError, e:
            mc.fail(e.msg, e.exit_code)
    else:
        msg = "Unknown action: " + request['action']
        mc.fail(msg, 2)
    log.info('Result via Mcollective: %s' % mc.data)
    sys.exit(0)
