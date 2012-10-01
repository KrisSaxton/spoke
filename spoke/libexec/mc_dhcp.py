#!/usr/bin/env python
# core modules
import sys

# own modules
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.logger as logger
import mc_helper as mc
from spoke.lib.dhcp import SpokeDHCPHost, SpokeDHCPAttr
        
config_file = '/usr/local/pkg/spoke/etc/spoke.conf'
config = config.setup(config_file)
    
if __name__ == '__main__':
    log = logger.setup('main', verbose=False, quiet=True)
    mc = mc.MCollectiveAction()
    request = mc.request()
    try:
        server = config.get('DHCP', 'dhcp_def_server')
        group   = config.get('DHCP', 'dhcp_def_group')
        host = SpokeDHCPHost(server, group)
    except Exception as e:
        mc.fail(e)

    if request['action'] != 'search':
        try:
            hostname = request['data']['hostname']
        except KeyError:
            mc.fail("Missing input hostname", 2)
            
    if request['action'] == 'create':
        try:
            mac = request['data']['mac']
            ip = request['data']['ip']
            try:
                mc.info('Creating host %s' % hostname)
                host.create(hostname)
            except error.AlreadyExists:
                mc.info('Host %s already exists' % hostname)
            mc.info('Adding DHCP attributes for host %s' % hostname)
            attr = SpokeDHCPAttr(server, group, hostname)
            attr.create("dhcpHWAddress", "ethernet %s" % mac )
            attr.create("dhcpStatements", "fixed-address %s" %ip )
            attr.create("dhcpOption", "host-name \"%s\"" %hostname )
            mc.data = host.get(hostname)
        except error.SpokeError, e:
            mc.fail(e.msg, e.exit_code)
    elif request['action'] == 'search':
        try:
            hostname = request['data']['hostname']
        except KeyError:
            hostname = None
        try:
            mc.data = host.get(hostname)
            attrs = mc.data['data'][0][1]
            mc.mac = attrs['dhcpHWAddress'][0].split()[1]
            mc.ip = attrs['dhcpStatements'][0].split()[1]
        except error.SpokeError, e:
            mc.fail(e.msg, e.exit_code)
    elif request['action'] == 'delete':
        try:
            mc.data = host.delete(hostname)
        except error.SpokeError, e:
            mc.fail(e.msg, e.exit_code)
    else:
        msg = "Unknown action: " + request['action']
        mc.fail(msg, 2)
    log.info('Result via Mcollective: %s' % mc.data)
    sys.exit(0)
