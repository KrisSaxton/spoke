metadata :name        => "Spoke UUID Agent",
                     :description => "Spoke UUID service for MCollective",
                     :author      => "Kris Saxton",
                     :license     => "ALv2",
                     :version     => "1.0",
                     :url         => "http://automationlogic.com/spoke",
                     :timeout     => 10
                     
action "create", :description => "Sets initial next free UUID value" do
    display :always
    
    input :uuid_start,
          :prompt      => "Start UUID",
          :description => "A value for the initial UUID",
          :type        => :integer,
          :optional    => false
 
    output :data,
           :description => "The next available UUID",
           :display_as  => "Successfuly set next free UUID"
end

action "get", :description => "Retrieve the next free UUID value" do
    display :always
    
    output :data,
           :description => "The next available UUID",
           :display_as  => "Next free UUID"
end

action "reserve", :description => "Reserve $qty UUID(s)" do
    display :always
    
    input :qty,
          :prompt      => "Quantity",
          :description => "Number of UUIDs to reserve (default=1)",
          :type        => :integer,
          :optional    => true
    
    output :data,
           :description => "Reserve $qty UUID(s)",
           :display_as  => "Reserved UUID(s)"
end