metadata :name        => "Spoke Virtual Machine Power Agent",
                     :description => "Spoke virtual machine power service for MCollective",
                     :author      => "Kris Saxton",
                     :license     => "ALv2",
                     :version     => "1.0",
                     :url         => "http://automationlogic.com/spoke",
                     :timeout     => 10
                     
action "search", :description => "Retrieve a virtual machine's power status" do
    display :always

    input :hostname,
          :prompt      => "Virtual machine name",
          :description => "The name of the virtual machine",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false

    output :data,
           :description => "Virtual machine power info",
           :display_as  => "Virtual machine's power status"
end

action "on", :description => "Power on a virtual machine" do
    display :always
 
    input :hostname,
          :prompt      => "Virtual machine name",
          :description => "The name of the virtual machine",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false
          
    output :data,
           :description => "Virtual machine power info",
           :display_as  => "Powered on virtual machine"
end

action "off", :description => "Power off a virtual machine" do
    display :always
 
    input :hostname,
          :prompt      => "Virtual machine name",
          :description => "The name of the virtual machine",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false
          
    output :data,
           :description => "Virtual machine power info",
           :display_as  => "Powered off virtual machine"
end

action "reboot", :description => "Power cycle a virtual machine" do
    display :always
 
    input :hostname,
          :prompt      => "Virtual machine name",
          :description => "The name of the virtual machine",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false
          
    output :data,
           :description => "Virtual machine power info",
           :display_as  => "Power cycled virtual machine"
end

action "forceoff", :description => "Force power off virtual machine" do
    display :always
 
    input :hostname,
          :prompt      => "Virtual machine name",
          :description => "The name of the virtual machine",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false
          
    output :data,
           :description => "Virtual machine power info",
           :display_as  => "Forced power off of virtual machine"
end