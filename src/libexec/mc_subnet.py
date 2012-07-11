#!/usr/bin/env python
# core modules
import sys

# own modules
import config
import logger
import mc_helper as mc
from ip import SpokeSubnet

config_file = '/usr/local/pkg/spoke/etc/spoke.conf'
config = config.setup(config_file)

if __name__ == '__main__':
    mc = mc.MCollectiveAction()
    log = logger.setup('main', verbose=False, quiet=True)
    request = mc.request()
    network = request['data']['network']
    mask = request['data']['mask']
    try:
        dc = request['data']['dc']
    except KeyError:
        dc = None
    try:
        qty = request['data']['qty']
    except KeyError:
        qty = 1
    try:
        ip = request['data']['ip']
    except KeyError:
        ip = None
    if request['action'] == 'search':
        try:
            mc.data = SpokeSubnet(network, mask, dc).get()['data']
        except Exception as e:
            mc.fail(e.msg, e.exit_code)
    elif request['action'] == 'reserve':
        try:
            mc.data = SpokeSubnet(network, mask, dc).modify(reserve=qty)['data']
        except Exception as e:
            mc.fail(e.msg, e.exit_code)
    elif request['action'] == 'release':
        try:
            mc.data = SpokeSubnet(network, mask, dc).modify(release=ip)['data']
        except Exception as e:
            mc.fail(e.msg, e.exit_code)
    else:
        msg = "Unknown action: " + request['action']
        mc.fail(msg, 2)
    log.info('Result via Mcollective: %s' % mc.data)
    sys.exit(0)