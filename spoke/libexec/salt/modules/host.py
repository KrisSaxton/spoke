
# own modules
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.common as common

version = common.version
config_file = '/usr/local/pkg/spoke/etc/spoke.conf'

try:
    conf = config.setup(config_file)
except error.ConfigError, e:
    raise


# Host commands
def host_search(org_name, host_name=None):
    from spoke.lib.host import SpokeHost
    try:
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
    from spoke.lib.host import SpokeHost
    try:
        host = SpokeHost(org_name)
        result = host.create(host_name, host_uuid, host_mem, host_cpu, 
                                 host_family, host_type, 
                                 host_storage_layout, host_network_layout)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result
    
    
def host_delete(org_name, host_name):
    from spoke.lib.host import SpokeHost
    try:
        host = SpokeHost(org_name)
        result = host.delete(host_name)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result

        
def uuid_create(start_uuid, get_mac=False):
    try:       
        from spoke.lib.host import SpokeHostUUID
        uuid = SpokeHostUUID()
        result = uuid.create(get_mac, uuid_start=start_uuid)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def uuid_search(get_mac=False):

    print get_mac
    print type(get_mac)
    try:
        from spoke.lib.host import SpokeHostUUID
        uuid = SpokeHostUUID()
        result = uuid.get(get_mac)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result  


def uuid_delete():
    try:
        from spoke.lib.host import SpokeHostUUID
        uuid = SpokeHostUUID()
        result = uuid.delete()
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def uuid_reserve(qty, get_mac=False):
    try:
        from spoke.lib.host import SpokeHostUUID
        uuid = SpokeHostUUID()
        result = uuid.modify(get_mac, increment=qty)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result