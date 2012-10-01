#!/usr/bin/env ruby
# Currently this just does single VMs

require 'mcollective'

include MCollective::RPC

options = rpcoptions do |parser, options|
    parser.define_head "Server Provisioning Client"
    parser.banner = "Usage: uuid [options] [filters] --hostname HOSTNAME"
 
    parser.on('', '--hostname HOSTNAME', 'Server hostname') do |v|
        options[:hostname] = v
    end
    parser.on('', '--customer CUSTOMER', 'Customer requesting server') do |v|
        options[:customer] = v
    end
end
 
unless options.include?(:hostname)
    puts("You need to specify a hostname with --hostname")
    exit! 1
end

unless options.include?(:customer)
    puts("You need to specify a customer with --customer")
    exit! 1
end

default_config='/usr/local/etc/mco.cfg'
options[:config] = default_config

# Static data that should eventually be externalised 
# either in an external service or a discoverable attribute
hostname = options[:'hostname']
network='10.0.16.0'
mask='24'
org = options[:customer]
vg_name = 'vg01'

# Find IP
mc = rpcclient("dhcp", :options => options)
mc.reset_filter
mc.progress = false
resp = mc.search(:hostname => hostname)[0]
ip = resp[:data][:'ip']
mac = resp[:data][:'mac']
printf("%-20s: Found IP reservation %s for hostname: %s\n", resp[:sender], ip, hostname)

# Release IP
mc = rpcclient("subnet", :options => options)
mc.reset_filter
mc.progress = false
resp = mc.release(:network => network, :mask => mask, :ip => ip)[0]
printf("%-20s: Released IP: %s\n", resp[:sender], ip)

# Remove DHCP entry
mc = rpcclient("dhcp", :options => options)
mc.reset_filter
mc.progress = false
resp = mc.delete(:hostname => hostname)[0]
printf("%-20s: Deleted DHCP entry for: %s\n", resp[:sender], hostname)

# Remove TFTP link
mc = rpcclient("tftp", :options => options)
mc.reset_filter
mc.progress = false
resp = mc.delete(:mac => mac)[0]
printf("%-20s: Removed TFTP link for hostname: %s (%s)\n", resp[:sender], hostname, mac)

# Delete Logical Volume
lv_name = hostname
mc = rpcclient("lvm", :options => options)
mc.reset_filter
mc.progress = false
resp = mc.delete(:vg_name => vg_name, :lv_name => lv_name)[0]
printf("%-20s: Deleted Logical Volume %s\n", resp[:sender], lv_name)

# Delete Server LDAP record 
mc = rpcclient("host", :options => options)
mc.reset_filter
mc.progress = false
resp = mc.delete(:org => org, :hostname => hostname)[0]
printf("%-20s: Deleted Server Record: %s\n", resp[:sender], hostname)

# Power off Virtual Machine
mc = rpcclient("power", :options => options)
mc.reset_filter
mc.progress = false
resp = mc.search(:hostname => hostname)[0]
printf("%-20s: Powered off Virtual Machine: %s\n", resp[:sender], hostname)

# Delete Virtual Machine
mc = rpcclient("vm", :options => options)
mc.reset_filter
mc.progress = false
resp = mc.delete(:hostname => hostname)[0]
printf("%-20s: Deleted Virtual Machine: %s\n", resp[:sender], hostname)
