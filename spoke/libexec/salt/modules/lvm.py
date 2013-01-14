'''
Salt module to expose TFTP management elements of Spoke API
'''

# Import core libs
import re
import logging

# Import salt modules
from salt.exceptions import SaltInvocationError

# Import spoke libs
try:
    import spoke.lib.error as error
    import spoke.lib.config as config
    import spoke.lib.common as common
    from spoke.lib.lvm import SpokeLVM
    has_spoke = True
except ImportError:
    has_spoke = False

log = logging.getLogger(__name__)
version = common.version


def _salt_config(name):
    value = __salt__['config.option']('SPOKE.{0}'.format(name))
    if not value:
        msg = 'missing SPOKE.{0} in config'.format(name)
        raise SaltInvocationError(msg)
    return value


def _spoke_config(config_file):
    try:
        conf = config.setup(config_file)
    except error.ConfigError, e:
        msg = 'Error reading config file {0}'.format(config_file)
        raise SaltInvocationError(msg)
    return conf

def search(lv_name=None, vg_name=None):
    try:
        conf = _spoke_config(_salt_config('config'))
        if not vg_name:
            vg_name = conf.get('LVM', 'lv_def_vg_name')
        lv = SpokeLVM(vg_name)
        result = lv.get(lv_name)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def create(lv_name, lv_size, vg_name=None):
    try:
        conf = _spoke_config(_salt_config('config'))
        if not vg_name:
            vg_name = conf.get('LVM', 'lv_def_vg_name')
        lv = SpokeLVM(vg_name)
        result = lv.create(lv_name, lv_size)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def delete(lv_name, force=False, vg_name=None):
    conf = _spoke_config(_salt_config('config'))
    if not vg_name:
        vg_name = conf.get('LVM', 'lv_def_vg_name')
    if force is True:
        try:
            lv = SpokeLVM(vg_name)
            result = lv.delete(lv_name)
        except error.SpokeError as e:
            result = common.handle_error(e)
    else:
        result = "Set force=True to delete %s from group %s" %\
            (lv_name, vg_name)
    return result
