module MCollective
    module Agent
        class Lvm<RPC::Agent
            action "create" do
                validate :vg_name, String
                validate :lv_name, String
                validate :vg_name, String
                implemented_by "/usr/local/pkg/spoke/libexec/mc_lvm.py"
            end
            action "search" do
                validate :vg_name, String
                implemented_by "/usr/local/pkg/spoke/libexec/mc_lvm.py"
            end
            action "delete" do
                validate :vg_name, String
                validate :lv_name, String
                implemented_by "/usr/local/pkg/spoke/libexec/mc_lvm.py"
            end
        end
    end
end
