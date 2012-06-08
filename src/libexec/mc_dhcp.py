#!/usr/bin/env python
import sys

import error
import config
import logger
import mc_helper as mc

from dhcp import SpokeDHCPHost, SpokeDHCPAttr
        
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
            mac             = request['data']['mac']
            ip              = request['data']['ip']
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
            mc.reply = True
        except Exception as e:
            mc.fail(e)
    elif request['action'] == 'search':
        try:
            hostname = request['data']['hostname']
        except KeyError:
            hostname = None
        try:
            mc.info('Searching for host %s' % hostname)
            mc.reply = host.get(hostname)
        except Exception as e:
            msg = type(e).__name__ + ": " + e.msg
            mc.fail(msg, e.exit_code)
    elif request['action'] == 'delete':
        try:
            mc.info('Deleting host %s' % hostname)
            mc.reply = host.delete(hostname)
        except Exception as e:
            msg = type(e).__name__ + ": " + e.msg
            mc.fail(msg, e.exit_code)
    else:
        msg = "Unknown action: " + request['action']
        mc.fail(msg, 2)
    sys.exit(0)
