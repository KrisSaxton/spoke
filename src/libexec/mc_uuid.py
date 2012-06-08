#!/usr/bin/env python
import sys
import config
import mc_helper as mc
from host import SpokeHostUUID

config_file = '/usr/local/pkg/spoke/etc/spoke.conf'
config = config.setup(config_file)
    
if __name__ == '__main__':
    mc = mc.MCollectiveAction()
    request = mc.request()
    try:
        uuid_start = request['data']['uuid_start']
    except KeyError:
        uuid_start = None
    try:
        qty = request['data']['qty']
    except KeyError:
        qty = None
    msg = "Calling SpokeHostUUID from mco"
    #log.debug(msg)
    if request['action'] == 'create':
        try:
            mc.reply = SpokeHostUUID().create(uuid_start)
        except Exception as e:
            msg = type(e).__name__ + ": " + e.msg
            mc.fail(msg, e.exit_code)
    elif request['action'] == 'get':
        try:
            mc.reply = SpokeHostUUID().get()
        except Exception as e:
            msg = type(e).__name__ + ": " + e.msg
            mc.fail(msg, e.exit_code)
    elif request['action'] == 'delete':
        try:
            mc.reply = SpokeHostUUID().delete()
        except Exception as e:
            msg = type(e).__name__ + ": " + e.msg
            mc.fail(msg, e.exit_code)
    elif request['action'] == 'reserve':
        try:
            mc.reply = SpokeHostUUID().modify(increment=qty)
        except Exception as e:
            msg = type(e).__name__ + ": " + e.msg
            mc.fail(msg, e.exit_code)
    else:
        msg = "Unknown action: " + request['action']
        mc.fail(msg, 2)
    sys.exit(0)