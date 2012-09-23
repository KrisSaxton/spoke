module MCollective
    module Agent
        class Lvm<RPC::Agent
            action "create" do
                implemented_by "/usr/local/pkg/spoke/libexec/mc_lvm.py"
            end
            action "search" do
                implemented_by "/usr/local/pkg/spoke/libexec/mc_lvm.py"
            end
            action "delete" do
                implemented_by "/usr/local/pkg/spoke/libexec/mc_lvm.py"
            end
        end
    end
end
