#!/usr/bin/env python
import sys
import config
import mc_helper as mc
from ip import SpokeSubnet

config_file = '/usr/local/pkg/spoke/etc/spoke.conf'
config = config.setup(config_file)

if __name__ == '__main__':
    mc = mc.MCollectiveAction()
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
        qty = None
    try:
        ip = request['data']['ip']
    except KeyError:
        ip = None
    msg = "Calling SpokeSubnet from mco with args network=%s, mask=%s and dc=%s" % (network, mask, dc)
    #log.debug(msg)
    if request['action'] == 'create':
        try:
            mc.reply = SpokeSubnet(network, mask, dc).create()
        except Exception as e:
            msg = type(e).__name__ + ": " + e.msg
            mc.fail(msg, e.exit_code)
    elif request['action'] == 'search':
        try:
            mc.reply = SpokeSubnet(network, mask, dc).get()
        except Exception as e:
            msg = type(e).__name__ + ": " + e.msg
            mc.fail(msg, e.exit_code)
    elif request['action'] == 'delete':
        try:
            mc.reply = SpokeSubnet(network, mask, dc).delete()
        except Exception as e:
            msg = type(e).__name__ + ": " + e.msg
            mc.fail(msg, e.exit_code)
    elif request['action'] == 'reserve':
        try:
            mc.reply = SpokeSubnet(network, mask, dc).modify(reserve=qty)
        except Exception as e:
            msg = type(e).__name__ + ": " + e.msg
            mc.fail(msg, e.exit_code)
    elif request['action'] == 'release':
        try:
            mc.reply = SpokeSubnet(network, mask, dc).modify(release=ip)
        except Exception as e:
            msg = type(e).__name__ + ": " + e.msg
            mc.fail(msg, e.exit_code)
    else:
        msg = "Unknown action: " + request['action']
        mc.fail(msg, 2)
    sys.exit(0)