#!/usr/bin/env python
import sys
import config
import mc_helper as mc
from lvm import SpokeLVM

config_file = '/usr/local/pkg/spoke/etc/spoke.conf'
config = config.setup(config_file)
    
if __name__ == '__main__':
    mc = mc.MCollectiveAction()
    request = mc.request()
    try:
        vg_name = request['data']['vg_name']
    except KeyError:
        mc.fail("Missing input vg_name", 2)

    if request['action'] == 'create':
        try:
            lv_name = request['data']['lv_name']
            lv_size = request['data']['lv_size']
            mc.reply = SpokeLVM(vg_name).create(lv_name, lv_size)
        except Exception as e:
            msg = type(e).__name__ + ": " + e.msg
            mc.fail(msg, e.exit_code)
    elif request['action'] == 'search':
        try:
            lv_name = request['data']['lv_name']
        except KeyError:
            lv_name = None
        try:
            mc.reply = SpokeLVM(vg_name).get(lv_name)
        except Exception as e:
            msg = type(e).__name__ + ": " + e.msg
            mc.fail(msg, e.exit_code)
    elif request['action'] == 'delete':
        try:
            lv_name = request['data']['lv_name']
        except KeyError:
            mc.fail("Missing input lv_name", 2)
        try:
            mc.reply = SpokeLVM(vg_name).delete(lv_name)
        except Exception as e:
            msg = type(e).__name__ + ": " + e.msg
            mc.fail(msg, e.exit_code)
    else:
        msg = "Unknown action: " + request['action']
        mc.fail(msg, 2)
    sys.exit(0)
