module MCollective
    module Agent
        class Vm<RPC::Agent
            action "search" do
                implemented_by "/usr/local/pkg/spoke/libexec/mc_vm.py"
            end
            action "create" do
                implemented_by "/usr/local/pkg/spoke/libexec/mc_vm.py"
            end
            action "delete" do
                implemented_by "/usr/local/pkg/spoke/libexec/mc_vm.py"
            end
        end
    end
end
