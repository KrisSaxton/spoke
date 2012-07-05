metadata :name        => "Spoke LVM2 Agent",
                     :description => "Spoke LVM2 service for MCollective",
                     :author      => "Kris Saxton",
                     :license     => "ALv2",
                     :version     => "1.0",
                     :url         => "http://automationlogic.com/spoke",
                     :timeout     => 10
                     
action "search", :description => "Search for Logical Volumes" do
    display :always

    input :vg_name,
          :prompt      => "Logical Volume Group",
          :description => "The Logical Volume Group",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false
 
    input :lv_name,
          :prompt      => "Logical Volume Name",
          :description => "The Logical Volume Name",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => true

    output :data,
           :description => "Logical Volume info",
           :display_as  => "Found Logical Volume(s)"
end

action "create", :description => "Create a Logical Volume" do
    display :always
    
     input :vg_name,
          :prompt      => "Logical Volume Group",
          :description => "The Logical Volume Group",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false
 
    input :lv_name,
          :prompt      => "Logical Volume Name",
          :description => "The Logical Volume Name",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false

    output :data,
           :description => "New Logical Volume info",
           :display_as  => "Created Logical Volume"
end

action "delete", :description => "Delete a Logical Volume" do
    display :always

    input :vg_name,
          :prompt      => "Logical Volume Group",
          :description => "The Logical Volume Group",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false
 
    input :lv_name,
          :prompt      => "Logical Volume Name",
          :description => "The Logical Volume Name",
          :type        => :string,
          :validation  => '^[a-zA-Z\-_\d]+$',
          :maxlength   => 20,
          :optional    => false

    output :data,
           :description => "Deleted Logical Volume",
           :display_as  => "Deleted Logical Volume"
end