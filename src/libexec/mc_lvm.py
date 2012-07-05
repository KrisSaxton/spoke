#!/usr/bin/env python
# core modules
import sys
# own modules
import error
import config
import logger
import mc_helper as mc
from lvm import SpokeLVM

config_file = '/usr/local/pkg/spoke/etc/spoke.conf'
config = config.setup(config_file)
    
if __name__ == '__main__':
    mc = mc.MCollectiveAction()
    log = logger.setup('main', verbose=False, quiet=True)
    request = mc.request()
    try:
        vg_name = request['data']['vg_name']
    except KeyError:
        mc.fail("Missing input vg_name", 2)

    if request['action'] == 'create':
        lv_name = request['data']['lv_name']
        lv_size = request['data']['lv_size']
        try:
            mc.data = SpokeLVM(vg_name).create(lv_name, lv_size)
        except error.SpokeError as e:
            mc.fail(e.msg, e.exit_code)
    elif request['action'] == 'search':
        try:
            lv_name = request['data']['lv_name']
        except KeyError:
            lv_name = None
        try:
            mc.data = SpokeLVM(vg_name).get(lv_name)
        except error.SpokeError as e:
            mc.fail(e.msg, e.exit_code)
    elif request['action'] == 'delete':
        try:
            lv_name = request['data']['lv_name']
        except KeyError:
            mc.fail("Missing input lv_name", 2)
        try:
            mc.data = SpokeLVM(vg_name).delete(lv_name)
        except error.SpokeError as e:
            mc.fail(e.msg, e.exit_code)
    else:
        msg = "Unknown action: " + request['action']
        mc.fail(msg, 2)
    log.info('Result via Mcollective: %s' % mc.data)
    sys.exit(0)
