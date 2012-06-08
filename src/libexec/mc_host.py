#!/usr/bin/env python
import sys
import config
import logger
import mc_helper as mc
from host import SpokeHost

config_file = '/usr/local/pkg/spoke/etc/spoke.conf'
config = config.setup(config_file)
    
if __name__ == '__main__':
    log = logger.setup('main', verbose=False, quiet=True)
    mc = mc.MCollectiveAction()
    request = mc.request()
    try:
        org_name = request['data']['org']
    except KeyError:
        mc.fail("Missing input org", 2)

    try:
        host = SpokeHost(org_name)
    except Exception as e:
        msg = type(e).__name__ + ": " + e.msg
        mc.fail(msg, e.exit_code)

    if request['action'] == 'create':
        try:
            host_name = request['data']['hostname']
            host_uuid = request['data']['uuid']
            host_mem = request['data']['mem']
            host_cpu = request['data']['cpu']
            host_family = request['data']['family']
            host_storage_layout = request['data']['storage_layout']
            host_network_layout = request['data']['network_layout']
            host_type  = request['data']['type']
            try:
                host_extra_opts = request['data']['extra_opts']
            except KeyError:
                host_extra_opts = None
            mc.info('Creating host %s' % host_name)
            mc.reply = host.create(host_name, host_uuid, host_mem, host_cpu, host_family, 
               host_storage_layout, host_network_layout, host_type, 
               host_extra_opts)
        except Exception as e:
            msg = type(e).__name__ + ": " + e.msg
            mc.fail(msg, e.exit_code)
    elif request['action'] == 'search':
        try:
            host_name = request['data']['hostname']
        except KeyError:
            host_name = None
        try:
            mc.info('Searching for host %s' % host_name)
            mc.reply = host.get(host_name)
        except Exception as e:
            msg = type(e).__name__ + ": " + e.msg
            mc.fail(msg, e.exit_code)
    elif request['action'] == 'delete':
        try:
            host_name = request['data']['hostname']
        except KeyError:
            host_name = None
        try:
            mc.info('Deleting host %s' % host_name)
            mc.reply = host.delete(host_name)
        except Exception as e:
            msg = type(e).__name__ + ": " + e.msg
            mc.fail(msg, e.exit_code)
    else:
        msg = "Unknown action: " + request['action']
        mc.fail(msg, 2)
    sys.exit(0)
