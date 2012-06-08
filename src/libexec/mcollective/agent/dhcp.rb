module MCollective
    module Agent
        class Dhcp<RPC::Agent
            action "search" do
                validate :hostname, String
                implemented_by "/usr/local/pkg/spoke/libexec/mc_dhcp.py"
            end
            action "create" do
                validate :hostname, String
                validate :mac, String
                validate :ip, String
                implemented_by "/usr/local/pkg/spoke/libexec/mc_dhcp.py"
            end
            action "delete" do
                validate :hostname, String
                implemented_by "/usr/local/pkg/spoke/libexec/mc_dhcp.py"
            end
        end
    end
end
