module MCollective
    module Agent
        class Uuid<RPC::Agent
            metadata :name        => "Spoke UUID Agent",
                     :description => "Spoke UUID service for MCollective",
                     :author      => "Kris Saxton",
                     :license     => "ALv2",
                     :version     => "1.0",
                     :url         => "http://automationlogic.com/spoke",
                     :timeout     => 10
            action "create" do
                implemented_by "/usr/local/pkg/spoke/libexec/mc_uuid.py"
            end
            action "get" do
                implemented_by "/usr/local/pkg/spoke/libexec/mc_uuid.py"
            end
            action "delete" do
                implemented_by "/usr/local/pkg/spoke/libexec/mc_uuid.py"
            end
            action "reserve" do
                implemented_by "/usr/local/pkg/spoke/libexec/mc_uuid.py"
            end
        end
    end
end