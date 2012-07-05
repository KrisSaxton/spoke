metadata :name        => "Spoke Subnet Agent",
                     :description => "Spoke Subnet service for MCollective",
                     :author      => "Kris Saxton",
                     :license     => "ALv2",
                     :version     => "1.0",
                     :url         => "http://automationlogic.com/spoke",
                     :timeout     => 10
                     
action "search", :description => "Find and return subnet details" do
    display :always

    input :network,
          :prompt      => "Network number or IP address",
          :description => "A network number or member IP address identifying the subnet",
          :type        => :ipv4address,
          :optional    => false
 
    input :mask,
          :prompt      => "Subnet mask",
          :description => "The subnet mask or prefix (integer format)",
          :type        => :integer,
          :optional    => false

    input :dc,
          :prompt      => "Datacentre tag",
          :description => "A datacentre ID to uniquely identify the subnet",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 6,
          :optional    => true

    output :data,
           :description => "The Subnet's name, free and allocated IP addresses",
           :display_as  => "Found subnet"
end

action "reserve", :description => "Reserve $qty IP(s)" do
    display :always
    
    input :qty,
          :prompt      => "Quantity",
          :description => "Number of IP addresses to reserve (default=1)",
          :type        => :integer,
          :optional    => true
    
    output :data,
           :description => "Reserved IP addresses",
           :display_as  => "Reserved IP(s)"
end

action "release", :description => "Release IP address" do
    display :always
    
    input :ip,
          :prompt      => "IP address",
          :description => "IP addresses to return to subnet",
          :type        => :ipv4address,
          :optional    => false
    
    output :data,
           :description => "Returned IP address",
           :display_as  => "Returned IP address"
end