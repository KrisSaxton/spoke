module MCollective
    module Agent
        class Host<RPC::Agent
            action "search" do
                validate :org, String
                implemented_by "/usr/local/pkg/spoke/libexec/mc_host.py"
            end
            action "create" do
                validate :org, String
                validate :hostname, String
                implemented_by "/usr/local/pkg/spoke/libexec/mc_host.py"
            end
            action "delete" do
                validate :org, String
                validate :hostname, String
                implemented_by "/usr/local/pkg/spoke/libexec/mc_host.py"
            end
        end
    end
end
