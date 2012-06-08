#!/usr/bin/env python
import sys

import error
import config
import logger
import mc_helper as mc

from tftp import SpokeTFTP
        
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
        mc.info('Searching for TFTP links')
        mc.reply = tftp.search(mac=mac, target=target)
    elif request['action'] == 'create':
        mac = request['data']['mac']
        target = request['data']['target']
        try:
            mc.info('Creating TFTP link between %s and %s' % (mac, target))
            mc.reply = tftp.create(mac, target)
        except Exception as e:
            mc.fail(e)
    elif request['action'] == 'delete':
        mac = request['data']['mac']
        try:
            mc.info('Deleting TFTP link for %s' % mac)
            mc.reply = tftp.delete(mac)
        except Exception as e:
            mc.fail(e)
    else:
        msg = "Unknown action: " + request['action']
        mc.fail(msg, 2)
    sys.exit(0)
