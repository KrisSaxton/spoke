#!/usr/bin/env python
# core modules
import sys

# own modules
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.logger as logger
import mc_helper as mc

from spoke.lib.tftp import SpokeTFTP
        
config_file = '/usr/local/pkg/spoke/etc/spoke.conf'
config = config.setup(config_file)
    
if __name__ == '__main__':
    log = logger.setup('main', verbose=False, quiet=True)
    mc = mc.MCollectiveAction()
    request = mc.request()
    try:
        tftp = SpokeTFTP()
    except Exception as e:
        mc.fail(e)

    if request['action'] == 'search':
        try:
            mac = request['data']['mac']
        except KeyError:
            mac = None
        try:
            target = request['data']['target']
        except KeyError:
            target = None
        try:
            mc.data = tftp.search(mac=mac, target=target)
        except error.SpokeError as e:
            mc.fail(e.msg, e.exit_code)
    elif request['action'] == 'create':
        mac = request['data']['mac']
        target = request['data']['target']
        try:
            mc.data = tftp.create(mac, target)
        except error.SpokeError as e:
            mc.fail(e.msg, e.exit_code)
    elif request['action'] == 'delete':
        mac = request['data']['mac']
        try:
            mc.data = tftp.delete(mac)
        except error.SpokeError as e:
            mc.fail(e.msg, e.exit_code)
    else:
        msg = "Unknown action: " + request['action']
        mc.fail(msg, 2)
    log.info('Result via Mcollective: %s' % mc.data)
    sys.exit(0)
