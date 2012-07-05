metadata :name        => "Spoke TFTP Agent",
                     :description => "Spoke TFTP service for MCollective",
                     :author      => "Kris Saxton",
                     :license     => "ALv2",
                     :version     => "1.0",
                     :url         => "http://automationlogic.com/spoke",
                     :timeout     => 10
                     
action "search", :description => "Search for TFTP target and MAC info" do
    display :always

    input :target,
          :prompt      => "TFTP target config file",
          :description => "The target TFTP config file",
          :type        => :string,
          :validation  => '^[a-zA-Z\.\-_\d]+$',
          :maxlength   => 20,
          :optional    => true
 
    input :mac,
          :prompt      => "MAC address",
          :description => "The MAC address associated with the target",
          :type        => :string,
          :validation  => '^([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}$',
          :maxlength   => 20,
          :optional    => true

    output :data,
           :description => "The TFTP target or link info",
           :display_as  => "Found TFTP info"
end

action "create", :description => "Create a TFTP target => MAC association" do
    display :always
    
    input :target,
          :prompt      => "TFTP target config file",
          :description => "The filename for the target TFTP config file",
          :type        => :string,
          :validation  => '^[a-zA-Z\.\-_\d]+$',
          :maxlength   => 20,
          :optional    => false
 
    input :mac,
          :prompt      => "MAC address",
          :description => "The MAC address associated with the target",
          :type        => :string,
          :validation  => '^([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}$',
          :maxlength   => 20,
          :optional    => false

    output :data,
           :description => "Created TFTP target => MAC association",
           :display_as  => "Created TFTP traget => MAC association"
end

action "delete", :description => "Delete a TFTP target => MAC association" do
    display :always

    input :mac,
          :prompt      => "MAC address",
          :description => "The MAC address associated with the target",
          :type        => :string,
          :validation  => '^([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}$',
          :maxlength   => 20,
          :optional    => false
 
    output :data,
           :description => "Deleted TFTP target => MAC association",
           :display_as  => "Deleted TFTP target => MAC association"
end