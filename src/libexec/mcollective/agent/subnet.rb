module MCollective
    module Agent
        class Subnet<RPC::Agent
            action "create" do
                validate :network, ipv4address
                validate :mask, Fixnum
                if request.include?(:dc)
                    validate :dc, String
                end
                implemented_by "/usr/local/pkg/spoke/libexec/mc_subnet.py"
            end
            action "search" do
                validate :network, ipv4address
                validate :mask, Fixnum
                if request.include?(:dc)
                    validate :dc, String
                end
                implemented_by "/usr/local/pkg/spoke/libexec/mc_subnet.py"
            end
            action "delete" do
                validate :network, ipv4address
                validate :mask, Fixnum
                if request.include?(:dc)
                    validate :dc, String
                end
                implemented_by "/usr/local/pkg/spoke/libexec/mc_subnet.py"
            end
            action "reserve" do
                validate :network, ipv4address
                validate :mask, Fixnum
                validate :qty, Fixnum
                if request.include?(:dc)
                    validate :dc, String
                end
                implemented_by "/usr/local/pkg/spoke/libexec/mc_subnet.py"
            end
            action "release" do
                validate :network, ipv4address
                validate :mask, Fixnum
                validate :ip, ipv4address
                if request.include?(:dc)
                    validate :dc, String
                end
                implemented_by "/usr/local/pkg/spoke/libexec/mc_subnet.py"
            end
        end
    end
end
