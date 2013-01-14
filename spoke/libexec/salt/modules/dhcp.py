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


def reservation_create(dhcp_server, dhcp_group, host_name, mac,  ip):
    try:
        conf = _spoke_config(_salt_config('config'))
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


def reservation_delete(dhcp_server, dhcp_group, host_name):
    try:
        conf = _spoke_config(_salt_config('config'))
        from spoke.lib.dhcp import SpokeDHCPHost
        host = SpokeDHCPHost(dhcp_server, dhcp_group)
        result = host.delete(host_name)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def server_create(server):
    try:
        conf = _spoke_config(_salt_config('config'))
        from spoke.lib.dhcp import SpokeDHCPServer
        server = SpokeDHCPServer()
        result = server.create(server)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def server_delete(server):
    try:
        conf = _spoke_config(_salt_config('config'))
        from spoke.lib.dhcp import SpokeDHCPServer
        server = SpokeDHCPServer()
        result = server.delete(server)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def server_search(server):
    try:
        conf = _spoke_config(_salt_config('config'))
        from spoke.lib.dhcp import SpokeDHCPServer
        server = SpokeDHCPServer()
        result = server.get(server)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def service_create(service):
    try:
        conf = _spoke_config(_salt_config('config'))
        from spoke.lib.dhcp import SpokeDHCPService
        service = SpokeDHCPService()
        result = service.create(service)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def service_delete(service):
    try:
        conf = _spoke_config(_salt_config('config'))
        from spoke.lib.dhcp import SpokeDHCPService
        service = SpokeDHCPService()
        result = service.delete(service)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def service_search(service):
    try:
        conf = _spoke_config(_salt_config('config'))
        from spoke.lib.dhcp import SpokeDHCPService
        service = SpokeDHCPService()
        result = service.get(service)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def subnet_create(dhcp_server, subnet, mask, start_ip=None, stop_ip=None):
    try:
        conf = _spoke_config(_salt_config('config'))
        from spoke.lib.dhcp import SpokeDHCPSubnet
        subnet = SpokeDHCPSubnet(dhcp_server)
        result = subnet.create(subnet, mask, start_ip, stop_ip)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def subnet_delete(dhcp_server, subnet):
    try:
        conf = _spoke_config(_salt_config('config'))
        from spoke.lib.dhcp import SpokeDHCPSubnet
        subnet = SpokeDHCPSubnet(dhcp_server)
        result = subnet.delete(subnet)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def subnet_search(dhcp_server, subnet):
    try:
        conf = _spoke_config(_salt_config('config'))
        from spoke.lib.dhcp import SpokeDHCPSubnet
        subnet = SpokeDHCPSubnet(dhcp_server)
        result = subnet.get(subnet)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def group_create(dhcp_server, dhcp_group):
    try:
        conf = _spoke_config(_salt_config('config'))
        from spoke.lib.dhcp import SpokeDHCPGroup
        group = SpokeDHCPGroup(dhcp_server)
        result = group.create(dhcp_group)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def group_delete(dhcp_server, dhcp_group):
    try:
        conf = _spoke_config(_salt_config('config'))
        from spoke.lib.dhcp import SpokeDHCPGroup
        group = SpokeDHCPGroup(dhcp_server)
        result = group.delete(dhcp_group)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def group_search(dhcp_server, dhcp_group):
    try:
        conf = _spoke_config(_salt_config('config'))
        from spoke.lib.dhcp import SpokeDHCPGroup
        group = SpokeDHCPGroup(dhcp_server)
        result = group.get(dhcp_group)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def host_create(dhcp_server, dhcp_group, dhcp_host):
    try:
        conf = _spoke_config(_salt_config('config'))
        from spoke.lib.dhcp import SpokeDHCPHost
        host = SpokeDHCPHost(dhcp_server, dhcp_group)
        result = host.create(dhcp_host)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def host_delete(dhcp_server, dhcp_group, dhcp_host):
    try:
        conf = _spoke_config(_salt_config('config'))
        from spoke.lib.dhcp import SpokeDHCPHost
        host = SpokeDHCPHost(dhcp_server, dhcp_group)
        result = host.delete(dhcp_host)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def host_search(dhcp_server, dhcp_group, dhcp_host):
    try:
        conf = _spoke_config(_salt_config('config'))
        from spoke.lib.dhcp import SpokeDHCPHost
        host = SpokeDHCPHost(dhcp_server, dhcp_group)
        result = host.get(dhcp_host)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def attr_create(dhcp_server, dhcp_group, dhcp_host, attr_type, attr_value):
    try:
        conf = _spoke_config(_salt_config('config'))
        from spoke.lib.dhcp import SpokeDHCPAttr
        attr = SpokeDHCPAttr(dhcp_server, dhcp_group, dhcp_host)
        result = attr.create(attr_type, attr_value)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def attr_delete(dhcp_server, dhcp_group, dhcp_host, attr_type, attr_value):
    try:
        conf = _spoke_config(_salt_config('config'))
        from spoke.lib.dhcp import SpokeDHCPAttr
        attr = SpokeDHCPAttr(dhcp_server, dhcp_group, dhcp_host)
        result = attr.delete(attr_type, attr_value)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def attr_search(dhcp_server, dhcp_group, dhcp_host, attr_type):
    try:
        conf = _spoke_config(_salt_config('config'))
        from spoke.lib.dhcp import SpokeDHCPAttr
        attr = SpokeDHCPAttr(dhcp_server, dhcp_group, dhcp_host)
        result = attr.get(attr_type)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result
