module MCollective
    module Agent
        class Tftp<RPC::Agent
            action "search" do
                implemented_by "/usr/local/pkg/spoke/libexec/mc_tftp.py"
            end
            action "create" do
                validate :mac, String
                validate :target, String
                implemented_by "/usr/local/pkg/spoke/libexec/mc_tftp.py"
            end
            action "delete" do
                validate :mac, String
                implemented_by "/usr/local/pkg/spoke/libexec/mc_tftp.py"
            end
        end
    end
end
