module MCollective
    module Agent
        class Uuid<RPC::Agent
            action "create" do
                validate :uuid_start, String
                implemented_by "/usr/local/pkg/spoke/libexec/mc_uuid.py"
            end
            action "get" do
                implemented_by "/usr/local/pkg/spoke/libexec/mc_uuid.py"
            end
            action "delete" do
                implemented_by "/usr/local/pkg/spoke/libexec/mc_uuid.py"
            end
            action "reserve" do
                validate :qty, String
                implemented_by "/usr/local/pkg/spoke/libexec/mc_uuid.py"
            end
        end
    end
end