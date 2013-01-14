'''
Salt module to expose Host management elements of Spoke API
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
    from spoke.lib.host import SpokeHost
    from spoke.lib.host import SpokeHostUUID
    has_host = True
except (ImportError, error.SpokeError) as e:
    has_host = False

log = logging.getLogger(__name__)
version = common.version


def __virtual__():
    '''
    Only load this module if the spoke modules imported correctly
    '''
    if has_host:
        return 'host'
    return False


def _salt_config(name):
    value = __opts__['SPOKE.{0}'.format(name)]
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


def host_search(org_name, host_name=None):
    try:
        conf = _spoke_config(_salt_config('config'))
        host = SpokeHost(org_name)
        if host_name is None:
            result = host.get()
        else:
            result = host.get(host_name)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def host_create(org_name, host_name, host_uuid, host_mem, host_cpu,
                host_family, host_type,
                host_storage_layout, host_network_layout):
    try:
        conf = _spoke_config(_salt_config('config'))
        host = SpokeHost(org_name)
        result = host.create(host_name, host_uuid, host_mem, host_cpu,
                             host_family, host_type,
                             host_storage_layout, host_network_layout)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def host_delete(org_name, host_name):
    try:
        conf = _spoke_config(_salt_config('config'))
        host = SpokeHost(org_name)
        result = host.delete(host_name)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def uuid_create(start_uuid=None, get_mac=False):
    try:
        conf = _spoke_config(_salt_config('config'))
        uuid = SpokeHostUUID()
        result = uuid.create(start_uuid, get_mac)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def uuid_search(get_mac=False):
    try:
        conf = _spoke_config(_salt_config('config'))
        uuid = SpokeHostUUID()
        print 'My Get_mac is {0}'.format(get_mac)
        result = uuid.get(get_mac=get_mac)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def uuid_delete():
    try:
        conf = _spoke_config(_salt_config('config'))
        uuid = SpokeHostUUID()
        result = uuid.delete()
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def uuid_reserve(qty=1, get_mac=False):
    try:
        conf = _spoke_config(_salt_config('config'))
        uuid = SpokeHostUUID()
        result = uuid.modify(qty, get_mac)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result
