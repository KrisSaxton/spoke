'''
Note this will need extending  when we want more than just XEN

'''

import re

import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.common as common

version = common.version

config_file = '/usr/local/pkg/spoke/etc/spoke.conf'

try:
    conf = config.setup(config_file)
except error.ConfigError, e:
    raise


def search(vg_name, lv_name=None):
    from spoke.lib.lvm import SpokeLVM
    lv = SpokeLVM(vg_name)
    try:
        result = lv.get(lv_name)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def create(vg_name, lv_name, lv_size):
    from spoke.lib.lvm import SpokeLVM
    lv = SpokeLVM(vg_name)
    try:
        result = lv.create(lv_name, lv_size)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def delete(vg_name, lv_name, force=False):
    from spoke.lib.lvm import SpokeLVM
    lv = SpokeLVM(vg_name)
    if force is True:
        try:
            result = lv.delete(lv_name)
        except error.SpokeError as e:
            result = common.handle_error(e)
    else:
        result = "Set force=True to delete %s from group %s" % (lv_name, vg_name)
    return result

    