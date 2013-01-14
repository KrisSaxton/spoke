'''
Salt module to expose DHCP management elements of Spoke API
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
    has_dhcp = True
except (ImportError, error.SpokeError) as e:
    has_dhcp = False

log = logging.getLogger(__name__)
version = common.version


def __virtual__():
    '''
    Only load this module if the spoke modules imported correctly
    '''
    if has_dhcp:
        return 'dhcp'
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


def reservation_search(host_name, dhcp_server=None, dhcp_group=None):
    try:
        conf = _spoke_config(_salt_config('config'))
        if not dhcp_server:
            dhcp_server = conf.get('DHCP', 'dhcp_def_server')
        if not dhcp_group:
            dhcp_group = conf.get('DHCP', 'dhcp_def_group')
        from spoke.lib.dhcp import SpokeDHCPHost
        host = SpokeDHCPHost(dhcp_server, dhcp_group)
        result = host.get(host_name)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def reservation_create(host_name, mac, ip, dhcp_server=None, dhcp_group=None):
    try:
        conf = _spoke_config(_salt_config('config'))
        if not dhcp_server:
            dhcp_server = conf.get('DHCP', 'dhcp_def_server')
        if not dhcp_group:
            dhcp_group = conf.get('DHCP', 'dhcp_def_group')
        from spoke.lib.dhcp import SpokeDHCPHost
        from spoke.lib.dhcp import SpokeDHCPAttr
        host = SpokeDHCPHost(dhcp_server, dhcp_group)
        try:
            host.create(host_name)
        except error.AlreadyExists:
            pass
        attr = SpokeDHCPAttr(dhcp_server, dhcp_group, host_name)
        attr.create("dhcpHWAddress", "ethernet %s" % mac)
        attr.create("dhcpStatements", "fixed-address %s" % ip)
        attr.create("dhcpOption", "host-name \"%s\"" % host_name)
        result = host.get(host_name)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def reservation_delete(host_name, dhcp_server=None, dhcp_group=None):
    try:
        conf = _spoke_config(_salt_config('config'))
        if not dhcp_server:
            dhcp_server = conf.get('DHCP', 'dhcp_def_server')
        if not dhcp_group:
            dhcp_group = conf.get('DHCP', 'dhcp_def_group')
        from spoke.lib.dhcp import SpokeDHCPHost
        host = SpokeDHCPHost(dhcp_server, dhcp_group)
        result = host.delete(host_name)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def group_create(dhcp_server=None, dhcp_group=None):
    try:
        conf = _spoke_config(_salt_config('config'))
        if not dhcp_server:
            dhcp_server = conf.get('DHCP', 'dhcp_def_server')
        if not dhcp_group:
            dhcp_group = conf.get('DHCP', 'dhcp_def_group')
        from spoke.lib.dhcp import SpokeDHCPGroup
        group = SpokeDHCPGroup(dhcp_server)
        result = group.create(dhcp_group)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def group_delete(dhcp_server=None, dhcp_group=None):
    try:
        conf = _spoke_config(_salt_config('config'))
        if not dhcp_server:
            dhcp_server = conf.get('DHCP', 'dhcp_def_server')
        if not dhcp_group:
            dhcp_group = conf.get('DHCP', 'dhcp_def_group')
        from spoke.lib.dhcp import SpokeDHCPGroup
        group = SpokeDHCPGroup(dhcp_server)
        result = group.delete(dhcp_group)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def group_search(dhcp_server=None, dhcp_group=None):
    try:
        conf = _spoke_config(_salt_config('config'))
        if not dhcp_server:
            dhcp_server = conf.get('DHCP', 'dhcp_def_server')
        if not dhcp_group:
            dhcp_group = conf.get('DHCP', 'dhcp_def_group')
        from spoke.lib.dhcp import SpokeDHCPGroup
        group = SpokeDHCPGroup(dhcp_server)
        result = group.get(dhcp_group)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def host_create(dhcp_host, dhcp_server=None, dhcp_group=None):
    try:
        conf = _spoke_config(_salt_config('config'))
        if not dhcp_server:
            dhcp_server = conf.get('DHCP', 'dhcp_def_server')
        if not dhcp_group:
            dhcp_group = conf.get('DHCP', 'dhcp_def_group')
        from spoke.lib.dhcp import SpokeDHCPHost
        host = SpokeDHCPHost(dhcp_server, dhcp_group)
        result = host.create(dhcp_host)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def host_delete(dhcp_host, dhcp_server=None, dhcp_group=None):
    try:
        conf = _spoke_config(_salt_config('config'))
        if not dhcp_server:
            dhcp_server = conf.get('DHCP', 'dhcp_def_server')
        if not dhcp_group:
            dhcp_group = conf.get('DHCP', 'dhcp_def_group')
        from spoke.lib.dhcp import SpokeDHCPHost
        host = SpokeDHCPHost(dhcp_server, dhcp_group)
        result = host.delete(dhcp_host)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def host_search(dhcp_host, dhcp_server=None, dhcp_group=None):
    try:
        conf = _spoke_config(_salt_config('config'))
        if not dhcp_server:
            dhcp_server = conf.get('DHCP', 'dhcp_def_server')
        if not dhcp_group:
            dhcp_group = conf.get('DHCP', 'dhcp_def_group')
        from spoke.lib.dhcp import SpokeDHCPHost
        host = SpokeDHCPHost(dhcp_server, dhcp_group)
        result = host.get(dhcp_host)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result
