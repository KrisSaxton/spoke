metadata :name        => "Spoke Host Agent",
                     :description => "Spoke Host service for MCollective",
                     :author      => "Kris Saxton",
                     :license     => "ALv2",
                     :version     => "1.0",
                     :url         => "http://automationlogic.com/spoke",
                     :timeout     => 10
                     
action "search", :description => "Search for Host entry" do
    display :always

    input :org,
          :prompt      => "Organisation",
          :description => "The organisation to whom the host belongs",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false
 
    input :hostname,
          :prompt      => "Hostname",
          :description => "The hostname of the host entry",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => true

    output :data,
           :description => "Host info",
           :display_as  => "Found host(s)"
end

action "create", :description => "Create a Host entry" do
    display :always
    
    input :org,
          :prompt      => "Organisation",
          :description => "The organisation to whom the host belongs",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false
 
    input :hostname,
          :prompt      => "Hostname",
          :description => "The hostname of the host entry",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false
          
    input :uuid,
          :prompt      => "UUID",
          :description => "The host's UUID",
          :type        => :integer,
          :optional    => false
          
    input :mem,
          :prompt      => "Memory",
          :description => "The host's memory in MB",
          :type        => :integer,
          :optional    => false

    input :cpu,
          :prompt      => "CPU",
          :description => "The number of CPU units available to the host",
          :type        => :integer,
          :optional    => false

    input :family,
          :prompt      => "Hypervisor Type",
          :description => "The hosting hypervisor",
          :type        => :string,
          :validation  => '^(test|xen|kvm|vmware)$',
          :maxlength   => 10,
          :optional    => false

    input :vm_type,
          :prompt      => "Virtual Machine Type",
          :description => "The type of virtualisation used",
          :type        => :string,
          :validation  => '^(phys|full|para)$',
          :maxlength   => 10,
          :optional    => false
          
    input :storage_layout,
          :prompt      => "Storage Layout",
          :description => "The nickname for the host's storage layout",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false          
          
    input :network_layout,
          :prompt      => "Network Layout",
          :description => "The nickname for the host's network layout",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false 

    input :extra_opts,
          :prompt      => "Extra Options",
          :description => "Extra options to pass to the hypervisor",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => true
          
    output :data,
           :description => "Host info",
           :display_as  => "Created host"
end

action "delete", :description => "Delete a Host entry" do
    display :always

    input :org,
          :prompt      => "Organisation",
          :description => "The organisation to whom the host belongs",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false
 
    input :hostname,
          :prompt      => "Hostname",
          :description => "The hostname of the host entry",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false

    output :data,
           :description => "Deleted host",
           :display_as  => "Deleted host"
end