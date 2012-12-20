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


def search(network, mask):
    try:
        from spoke.lib.ip import SpokeSubnet
        subnet = SpokeSubnet(ip=network, mask=mask, dc=None)
        result = subnet.get()
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def create(network, mask):
    try:
        from spoke.lib.ip import SpokeSubnet
        subnet = SpokeSubnet(ip=network, mask=mask, dc=None)
        result = subnet.create(None)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def delete(network, mask):
    try:
        from spoke.lib.ip import SpokeSubnet
        subnet = SpokeSubnet(ip=network, mask=mask, dc=None)
        result = subnet.delete()
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def reserve(network, mask, qty):
    try:
        from spoke.lib.ip import SpokeSubnet
        subnet = SpokeSubnet(ip=network, mask=mask, dc=None)
        result = subnet.modify(release=None, reserve=qty)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def release(network, mask, ip):
    try:
        from spoke.lib.ip import SpokeSubnet
        subnet = SpokeSubnet(ip=network, mask=mask, dc=None)
        result = subnet.modify(release=ip, reserve=None)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result
