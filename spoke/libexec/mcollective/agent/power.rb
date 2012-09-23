module MCollective
    module Agent
        class Power<RPC::Agent
            action "search" do
                validate :hostname, String
                implemented_by "/usr/local/pkg/spoke/libexec/mc_power.py"
            end
            action "on" do
                validate :hostname, String
                implemented_by "/usr/local/pkg/spoke/libexec/mc_power.py"
            end
            action "off" do
                validate :hostname, String
                implemented_by "/usr/local/pkg/spoke/libexec/mc_power.py"
            end
            action "reboot" do
                validate :hostname, String
                implemented_by "/usr/local/pkg/spoke/libexec/mc_power.py"
            end
            action "forceoff" do
                validate :hostname, String
                implemented_by "/usr/local/pkg/spoke/libexec/mc_power.py"
            end
        end
    end
end
