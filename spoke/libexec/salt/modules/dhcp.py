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


def reservation_search(dhcp_server, dhcp_group, host_name):
    try:
        from spoke.lib.dhcp import SpokeDHCPHost
        host = SpokeDHCPHost(dhcp_server, dhcp_group)
        result = host.get(host_name)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def reservation_create(dhcp_server, dhcp_group, host_name, mac,  ip):
    try:
        from spoke.lib.dhcp import SpokeDHCPHost
        from spoke.lib.dhcp import SpokeDHCPAttr
        host = SpokeDHCPHost(dhcp_server, dhcp_group)
        try:
            host.create(host_name)
        except error.AlreadyExists:
            pass
        attr = SpokeDHCPAttr(dhcp_server, dhcp_group, host_name)
        attr.create("dhcpHWAddress", "ethernet %s" % mac )
        attr.create("dhcpStatements", "fixed-address %s" %ip )
        attr.create("dhcpOption", "host-name \"%s\"" %host_name )
        result = host.get(host_name)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def reservation_delete(dhcp_server, dhcp_group, host_name):
    try:
        from spoke.lib.dhcp import SpokeDHCPHost
        host = SpokeDHCPHost(dhcp_server, dhcp_group)
        result = host.delete(host_name)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def server_create(server):
    try:
        from spoke.lib.dhcp import SpokeDHCPServer
        server = SpokeDHCPServer()
        result = server.create(server)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def server_delete(server):
    try:
        from spoke.lib.dhcp import SpokeDHCPServer
        server = SpokeDHCPServer()
        result = server.delete(server)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def server_search(server):
    try:
        from spoke.lib.dhcp import SpokeDHCPServer
        server = SpokeDHCPServer()
        result = server.get(server)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def service_create(service):
    try:
        from spoke.lib.dhcp import SpokeDHCPService
        service= SpokeDHCPService()
        result = service.create(service)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def service_delete(service):
    try:
        from spoke.lib.dhcp import SpokeDHCPService
        service = SpokeDHCPService()
        result = service.delete(service)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def service_search(service):
    try:
        from spoke.lib.dhcp import SpokeDHCPService
        service = SpokeDHCPService()
        result = service.get(service)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def subnet_create(dhcp_server, subnet, mask, start_ip=None, stop_ip=None):
    try:
        from spoke.lib.dhcp import SpokeDHCPSubnet
        subnet= SpokeDHCPSubnet(dhcp_server)
        result = subnet.create(subnet, mask, start_ip, stop_ip)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def subnet_delete(dhcp_server, subnet):
    try:
        from spoke.lib.dhcp import SpokeDHCPSubnet
        subnet = SpokeDHCPSubnet(dhcp_server)
        result = subnet.delete(subnet)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def subnet_search(dhcp_server, subnet):
    try:
        from spoke.lib.dhcp import SpokeDHCPSubnet
        subnet = SpokeDHCPSubnet(dhcp_server)
        result = subnet.get(subnet)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def group_create(dhcp_server, dhcp_group):
    try:
        from spoke.lib.dhcp import SpokeDHCPGroup
        group = SpokeDHCPGroup(dhcp_server)
        result = group.create(dhcp_group)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def group_delete(dhcp_server, dhcp_group):
    try:
        from spoke.lib.dhcp import SpokeDHCPGroup
        group = SpokeDHCPGroup(dhcp_server)
        result = group.delete(dhcp_group)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def group_search(dhcp_server, dhcp_group):
    try:
        from spoke.lib.dhcp import SpokeDHCPGroup
        group = SpokeDHCPGroup(dhcp_server)
        result = group.get(dhcp_group)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def host_create(dhcp_server, dhcp_group, dhcp_host):
    try:
        from spoke.lib.dhcp import SpokeDHCPHost
        host = SpokeDHCPHost(dhcp_server, dhcp_group)
        result = host.create(dhcp_host)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def host_delete(dhcp_server, dhcp_group, dhcp_host):
    try:
        from spoke.lib.dhcp import SpokeDHCPHost
        host = SpokeDHCPHost(dhcp_server, dhcp_group)
        result = host.delete(dhcp_host)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def host_search(dhcp_server, dhcp_group, dhcp_host):
    try:
        from spoke.lib.dhcp import SpokeDHCPHost
        host = SpokeDHCPHost(dhcp_server, dhcp_group)
        result = host.get(dhcp_host)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def attr_create(dhcp_server, dhcp_group, dhcp_host, attr_type, attr_value):
    try:
        from spoke.lib.dhcp import SpokeDHCPAttr
        attr = SpokeDHCPAttr(dhcp_server, dhcp_group, dhcp_host)
        result = attr.create(attr_type, attr_value)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def attr_delete(dhcp_server, dhcp_group, dhcp_host, attr_type, attr_value):
    try:
        from spoke.lib.dhcp import SpokeDHCPAttr
        attr = SpokeDHCPAttr(dhcp_server, dhcp_group, dhcp_host)
        result = attr.delete(attr_type, attr_value)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def attr_search(dhcp_server, dhcp_group, dhcp_host, attr_type):
    try:
        from spoke.lib.dhcp import SpokeDHCPAttr
        attr = SpokeDHCPAttr(dhcp_server, dhcp_group, dhcp_host)
        result = attr.get(attr_type)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result