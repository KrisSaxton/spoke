module MCollective
    module Agent
        class Vm<RPC::Agent
            action "search" do
                implemented_by "/usr/local/pkg/spoke/libexec/mc_vm.py"
            end
            action "create" do
                validate :hostname, String
                validate :uuid, String
                validate :mem, String
                validate :cpu, String
                validate :family, String
                validate :storage_layout, String
                validate :network_layout, String
                if request.include?(:install)
                    validate :install, String
                end
                implemented_by "/usr/local/pkg/spoke/libexec/mc_vm.py"
            end
            action "delete" do
                validate :hostname, String
                implemented_by "/usr/local/pkg/spoke/libexec/mc_vm.py"
            end
        end
    end
end
