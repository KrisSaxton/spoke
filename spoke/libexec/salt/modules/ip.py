'''
Salt module to expose IP management elements of Spoke API
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
    from spoke.lib.ip import SpokeSubnet
    has_ip = True
except ImportError:
    has_ip = False

log = logging.getLogger(__name__)
version = common.version


def __virtual__():
    '''
    Only load this module if the spoke modules imported correctly
    '''
    if has_ip:
        return 'ip'
    return False


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


def search(network, mask):
    try:
        conf = _spoke_config(_salt_config('config'))
        subnet = SpokeSubnet(ip=network, mask=mask, dc=None)
        result = subnet.get()
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def create(network, mask):
    try:
        conf = _spoke_config(_salt_config('config'))
        subnet = SpokeSubnet(ip=network, mask=mask, dc=None)
        result = subnet.create(None)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def delete(network, mask):
    try:
        conf = _spoke_config(_salt_config('config'))
        subnet = SpokeSubnet(ip=network, mask=mask, dc=None)
        result = subnet.delete()
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def reserve(network, mask, qty):
    try:
        conf = _spoke_config(_salt_config('config'))
        subnet = SpokeSubnet(ip=network, mask=mask, dc=None)
        result = subnet.modify(release=None, reserve=qty)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def release(network, mask, ip):
    try:
        conf = _spoke_config(_salt_config('config'))
        subnet = SpokeSubnet(ip=network, mask=mask, dc=None)
        result = subnet.modify(release=ip, reserve=None)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result
