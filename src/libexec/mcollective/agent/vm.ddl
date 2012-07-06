metadata :name        => "Spoke Virtual Machine Agent",
                     :description => "Spoke Virtual Machine service for MCollective",
                     :author      => "Kris Saxton",
                     :license     => "ALv2",
                     :version     => "1.0",
                     :url         => "http://automationlogic.com/spoke",
                     :timeout     => 10
                     
action "search", :description => "Search for a virtual machine" do
    display :always

    input :hostname,
          :prompt      => "Virtual machine name",
          :description => "The name of the virtual machine",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => true

    output :data,
           :description => "Virtual machine info",
           :display_as  => "Found virtual machine(s)"
end

action "create", :description => "Create a virtual machine" do
    display :always
 
    input :hostname,
          :prompt      => "Virtual machine name",
          :description => "The hostname of the virtual machine",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false
          
    input :uuid,
          :prompt      => "UUID",
          :description => "The vm's UUID",
          :type        => :integer,
          :optional    => false
          
    input :mem,
          :prompt      => "Memory",
          :description => "The vm's memory in MB",
          :type        => :integer,
          :optional    => false

    input :cpu,
          :prompt      => "CPU",
          :description => "The number of CPU units available to the vm",
          :type        => :integer,
          :optional    => false

    input :family,
          :prompt      => "Hypervisor Type",
          :description => "The hosting hypervisor",
          :type        => :string,
          :validation  => '^(test|xen|kvm|vmware)$',
          :maxlength   => 10,
          :optional    => false
          
    input :storage_layout,
          :prompt      => "Storage Layout",
          :description => "The nickname for the vm's storage layout",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false          
          
    input :network_layout,
          :prompt      => "Network Layout",
          :description => "The nickname for the vm's network layout",
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
           :description => "New virtual machine info",
           :display_as  => "Created virtual machine"
end

action "delete", :description => "Delete a virtual machine" do
    display :always
 
    input :hostname,
          :prompt      => "Virtual machine name",
          :description => "The hostname of the virtual machine",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false

    output :data,
           :description => "Deleted virtual machine",
           :display_as  => "Deleted virtual machine"
end