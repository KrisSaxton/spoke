"""Wrapper module to run all unit tests"""

import unittest

import test_spoke_ldap
import test_config
import test_dhcp
import test_dns
import test_email
import test_host
import test_ip
import test_list
import test_logger
import test_org
import test_password
import test_user
import test_vcs
import test_vm

if __name__ == '__main__':
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite([
                            test_loader.loadTestsFromModule(test_spoke_ldap),
                            test_loader.loadTestsFromModule(test_vcs),
                            test_loader.loadTestsFromModule(test_password),
                            test_loader.loadTestsFromModule(test_dns),
                            test_loader.loadTestsFromModule(test_dhcp),
                            test_loader.loadTestsFromModule(test_email),
                            test_loader.loadTestsFromModule(test_user),
                            
                            test_loader.loadTestsFromModule(test_org),
                            test_loader.loadTestsFromModule(test_logger),
                            test_loader.loadTestsFromModule(test_config)
                            ])
    unittest.TextTestRunner(verbosity=1).run(test_suite)