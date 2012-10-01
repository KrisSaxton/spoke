#!/usr/bin/env ruby
# Currently this just does single VMs

require 'mcollective'

include MCollective::RPC

options = rpcoptions do |parser, options|
    parser.define_head "Server Provisioning Client"
    parser.banner = "Usage: uuid [options] [filters] --customer CUSTOMER --size SMALL|MEDIUM|LARGE"
 
    parser.on('', '--customer CUSTOMER', 'Customer requesting server') do |v|
        options[:customer] = v
    end
    parser.on('', '--size SIZE', 'VM size (SMALL, MEDIUM OR LARGE)') do |v|
        options[:size] = v
    end
    parser.on('', '--hostname HOSTNAME', 'Server hostname') do |v|
        options[:hostname] = v
    end
end
 
unless options.include?(:customer)
    puts("You need to specify a customer with --customer")
    exit! 1
end

unless options.include?(:size)
    puts("You need to specify a VM size with --size SMALL|MEDIUM|LARGE")
    exit! 1
end

if options.include?(:hostname)
    hostname_prefix = options[:hostname]
else
    hostname_prefix = options[:customer]
end

default_config='/usr/local/etc/mco.cfg'
options[:config] = default_config

def get_vm_conf(options)
    # VM size mappings (this would normally be provided by a service catalogue)
    case options[:size]
    when "SMALL"
        vm_config={'mem' => 512, 'cpu' => 1, 'family' => 'xen', 'vm_type' => 'para', 'network_layout' => 'with_internet', 'storage_layout' => 'basic', 'lv_size' => '20', 'target' => 'xendomu.conf'}
    when "MEDIUM"
        vm_config={'mem' => 1024, 'cpu' => 1, 'family' => 'xen', 'vm_type' => 'para', 'network_layout' => 'with_internet', 'storage_layout' => 'basic', 'lv_size' => '40', 'target' => 'xendomu.conf'}
    when "LARGE"
        vm_config={'mem' => 2048, 'cpu' => 2, 'family' => 'xen', 'vm_type' => 'para', 'network_layout' => 'with_internet', 'storage_layout' => 'basic', 'lv_size' => '60', 'target' => 'xendomu.conf'}
    else
        puts("You need to specify a valid VM size with --size SMALL|MEDIUM|LARGE")
        exit! 1
    end
end

org = options[:customer]
vm_conf = get_vm_conf(options)

# Discover and select hypervisor with suitable attributes
mc = rpcclient("rpcutil", :options => options)
mc.progress = false
mc.fact_filter "virtual", "xen0"
mc.fact_filter "spoke_prov_net_exists", "true"
network = mc.get_fact(:fact => 'spoke_prov_net_subnet')[0][:data][:value]
resp = mc.get_fact(:fact => 'spoke_prov_net_mask')[0]
hypervisor = resp[:sender]
mask = resp[:data][:value]
printf("%-20s: Discovered and selected suitable hypervisor\n", resp[:sender])
printf("%-20s: Retrieved provisioning subnet and mask: %s/%s\n", resp[:sender], network, mask)

# Get next free UUID
mc = rpcclient("uuid", :options => options)
mc.reset_filter
mc.progress = false
resp = mc.reserve()[0]
uuid = resp[:data][:data][0]
printf("%-20s: Retrieved next free UUID: %s\n", resp[:sender], uuid)

# Generate hostname
hostname = hostname_prefix + '-' + uuid.to_s
printf("%-20s: Generated hostname: %s\n", 'localhost', hostname)

# Generate MAC address
uuid_long = "%06d" % uuid
mac_part = uuid_long[0,2] + ":" + uuid_long[2,2] + ":" + uuid_long[4,5]
mac = "02:" + mac_part + ":00:00"
printf("%-20s: Generated MAC address: %s\n", 'localhost', mac)

# Create Server LDAP record 
mc = rpcclient("host", :options => options)
mc.reset_filter
mc.progress = false
resp = mc.create(:org => org, :hostname => hostname, :uuid => uuid, :mem => vm_conf['mem'], :cpu => vm_conf['cpu'], :family => vm_conf['family'], :vm_type => vm_conf['vm_type'], :storage_layout => vm_conf['storage_layout'], :network_layout => vm_conf['network_layout'])[0]
printf("%-20s: Created Server Record: %s\n", resp[:sender], hostname)

# Reserve IP
mc = rpcclient("subnet", :options => options)
mc.reset_filter
mc.progress = false
resp = mc.reserve(:network => network, :mask => mask)[0]
ip = resp[:data][:data][0]
printf("%-20s: Reserved IP: %s\n", resp[:sender], ip)

# Create DHCP reservation
mc = rpcclient("dhcp", :options => options)
mc.reset_filter
mc.progress = false
resp = mc.create(:hostname => hostname, :mac => mac, :ip => ip)[0]
printf("%-20s: Created DHCP entry for: %s\n", resp[:sender], hostname)

# Create TFTP link
mc = rpcclient("tftp", :options => options)
mc.reset_filter
mc.progress = false
resp = mc.create(:target => vm_conf['target'], :mac => mac)[0]
printf("%-20s: Created TFTP link for hostname: %s (%s)\n", resp[:sender], hostname, mac)

# Create Logical Volume
lv_name = hostname
printf("%-20s: Generated Logical Volume Name: %s\n", 'localhost', lv_name)
mc = rpcclient("lvm", :options => options)
mc.reset_filter
mc.progress = false
resp = mc.create(:lv_name => lv_name, :lv_size => vm_conf['lv_size'])[0]
printf("%-20s: Created Logical Volume: %s\n", resp[:sender], lv_name)

# Create Virtual Machine
mc = rpcclient("vm", :options => options)
mc.reset_filter
mc.identity_filter hypervisor
mc.progress = false
resp = mc.create(:hostname => hostname, :uuid => uuid, :mem => vm_conf['mem'], :cpu => vm_conf['cpu'], :family => vm_conf['family'], :storage_layout => vm_conf['storage_layout'], :network_layout => vm_conf['network_layout'], :install => true)[0]
printf("%-20s: Created Virtual Machine: %s\n", resp[:sender], hostname)

# Power on Virtual Machine
mc = rpcclient("power", :options => options)
mc.reset_filter
mc.identity_filter hypervisor
mc.progress = false
resp = mc.search(:hostname => hostname)[0]
printf("%-20s: Powered on Virtual Machine: %s\n", resp[:sender], hostname)
