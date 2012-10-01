#!/usr/bin/env python
# core modules
import sys
# own modules
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.logger as logger
import spoke.lib.mc_helper as mc
from spoke.lib.host import SpokeHost

config_file = '/usr/local/pkg/spoke/etc/spoke.conf'
config = config.setup(config_file)
    
if __name__ == '__main__':
    log = logger.setup('main', verbose=False, quiet=True)
    mc = mc.MCollectiveAction()
    request = mc.request()
    org_name = request['data']['org']
    try:
        host = SpokeHost(org_name)
    except error.SpokeError, e:
        mc.fail(e.msg, e.exit_code)

    if request['action'] == 'create':
        host_name = request['data']['hostname']
        host_uuid = request['data']['uuid']
        host_mem = request['data']['mem']
        host_cpu = request['data']['cpu']
        host_family = request['data']['family']
        host_type  = request['data']['vm_type']
        host_storage_layout = request['data']['storage_layout']
        host_network_layout = request['data']['network_layout']
        try:
            host_extra_opts = request['data']['extra_opts']
        except KeyError:
            host_extra_opts = None
        try:
            mc.data = host.create(host_name, host_uuid, host_mem, host_cpu, 
                                  host_family, host_type, host_storage_layout,
                                  host_network_layout, host_extra_opts)
        except error.SpokeError, e:
            mc.fail(e.msg, e.exit_code)
    elif request['action'] == 'search':
        try:
            host_name = request['data']['hostname']
        except KeyError:
            host_name = None
        try:
            mc.data = host.get(host_name)
        except error.SpokeError, e:
            mc.fail(e.msg, e.exit_code)
    elif request['action'] == 'delete':
        host_name = request['data']['hostname']
        try:
            mc.data = host.delete(host_name)
        except error.SpokeError, e:
            mc.fail(e.msg, e.exit_code)
    else:
        msg = "Unknown action: " + request['action']
        mc.fail(msg, 2)
    log.info('Result via Mcollective: %s' % mc.data)
    sys.exit(0)
