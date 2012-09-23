metadata :name        => "Spoke DHCP Agent",
                     :description => "Spoke DHCP service for MCollective",
                     :author      => "Kris Saxton",
                     :license     => "ALv2",
                     :version     => "1.0",
                     :url         => "http://automationlogic.com/spoke",
                     :timeout     => 10
                     
action "search", :description => "Find and return DHCP host details" do
    display :always

    input :hostname,
          :prompt      => "DHCP hostname",
          :description => "A hostname for identifying the dhcp entry",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false
 
    output :data,
           :description => "The DHCP host info",
           :display_as  => "Found DHCP host"
end

action "create", :description => "Create a DHCP host entry" do
    display :always
    
    input :hostname,
          :prompt      => "DHCP hostname",
          :description => "A hostname for identifying the dhcp entry",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false

    input :mac,
          :prompt      => "Host MAC address",
          :description => "The network interface MAC address for the host",
          :type        => :string,
          :validation  => '^([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}$',
          :maxlength   => 17,
          :optional    => false

    input :ip,
          :prompt      => "Host IP address",
          :description => "The reserved IP addresse for the host",
          :type        => :ipv4address,
          :optional    => false
    
    output :data,
           :description => "Reserved IP addresses",
           :display_as  => "Reserved IP(s)"
end

action "delete", :description => "Delete a DHCP host entry" do
    display :always

    input :hostname,
          :prompt      => "DHCP hostname",
          :description => "A hostname for identifying the dhcp entry",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false
 
    output :data,
           :description => "Deleted DHCP host confirmation",
           :display_as  => "Deleted DHCP host"
end