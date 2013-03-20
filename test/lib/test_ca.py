"""Tests Spoke ca.py module."""
# core modules
import unittest
import os.path
# own modules
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.log as logger
from spoke.lib.ca import SpokeCA, SpokeCSR, SpokeCACert, SpokeHostCert

class SpokeCATest(unittest.TestCase):

    """A Class for testing the Spoke ca.py module."""
    
    def __init__(self, methodName):
        """Setup config data and redis connection."""
        unittest.TestCase.__init__(self, methodName)
        common_config = '../../contrib/spoke.conf'
        custom_config = '/tmp/spoke.conf'
        config_files = (common_config, custom_config)
        self.config = config.setup(config_files)
        self.log = logger.log_to_console()
        self.ca_name = 'test-ca'
        self.ca_cn = 'Test Certificate Authority'
        self.ca_def_duration = self.config.get('CA', 'ca_def_duration')
        self.ca_base_dir = self.config.get('CA', 'ca_base_dir')
        self.ca_dir = os.path.join(self.ca_base_dir, self.ca_name)
        self.ca_key_rdir = self.config.get('CA', 'ca_key_dir')
        self.ca_cert_rdir = self.config.get('CA', 'ca_cert_dir')
        self.ca_req_rdir = self.config.get('CA', 'ca_req_dir')
        self.ca_cert_name = self.config.get('CA', 'ca_pub_cert')
        self.ca_key_name = self.config.get('CA', 'ca_priv_key')
        self.ca_index_name = self.config.get('CA', 'ca_index')
        self.ca_serial_name = self.config.get('CA', 'ca_serial')
        self.ca_key_dir = os.path.join(self.ca_dir, self.ca_key_rdir)
        self.ca_cert_dir = os.path.join(self.ca_dir, self.ca_cert_rdir)
        self.ca_req_dir = os.path.join(self.ca_dir, self.ca_req_rdir)
        self.ca_tree = [(self.ca_dir, 
                        [self.ca_cert_rdir, self.ca_key_rdir, self.ca_req_rdir], 
                        [self.ca_serial_name]),
                        (self.ca_cert_dir, [], [self.ca_cert_name]),
                        (self.ca_key_dir, [], [self.ca_key_name]),
                        (self.ca_req_dir, [], [])]
        self.ca_key_file = os.path.join(self.ca_key_dir, self.ca_key_name)
        self.ca_cert_file = os.path.join(self.ca_cert_dir, self.ca_cert_name)
        
    # return a list containing os.walk results for "path"
    def get_tree(self, path):
        a = []
        for i in os.walk(path):
            a.append(i)
        return a
        
    def setUp(self): 
        ca = SpokeCA(self.ca_name)
        ca.create(self.ca_cn)

    def tearDown(self):
        ca = SpokeCA(self.ca_name)
        ca.delete()

# CA tests
       
    def test_create_invalid_ca(self):
        """Create a CA with a non shell safe name; raise InputError."""
        ca_name = 'ca;do bad stuff'
        self.assertRaises(error.InputError, SpokeCA, ca_name)
        
    def test_create_invalid_ca_cn(self):
        """Create a CA with a non shell safe cn; raise InputError."""
        ca_name = 'test-invalid-cn-ca'
        ca_cn = 'do naughty; stuff'
        ca = SpokeCA(ca_name)
        self.assertRaises(error.InputError, ca.create, ca_cn)
        
    def test_create_ca_twice(self):
        """Create an existing CA; raise AlreadyExists."""
        ca = SpokeCA(self.ca_name)
        self.assertRaises(error.AlreadyExists, ca.create, self.ca_cn)

    def test_create_ca(self):
        """Create a ca object; return results object."""
        ca_name = 'test-create-ca'
        ca_dir = os.path.join(self.ca_base_dir, ca_name)
        ca_key_dir = os.path.join(ca_dir, self.ca_key_rdir)
        ca_cert_dir = os.path.join(ca_dir, self.ca_cert_rdir)
        ca_key_file = os.path.join(ca_key_dir, self.ca_key_name)
        ca_cert_file = os.path.join(ca_cert_dir, self.ca_cert_name)
        ca = SpokeCA(ca_name)
        expected_result = {'count': 1, 'type': 'CA', 'exit_code': 0, 
                           'msg': 'Created CA:'}
        expected_result['data'] = [{'ca_cn': self.ca_cn,
                            'ca_key': ca_key_file,
                            'ca_def_duration': self.ca_def_duration,
                            'ca_cert_file': ca_cert_file,
                            'ca_cert_as_pem': ''}]
        result = ca.create(self.ca_cn)
        result['data'][0]['ca_cert_as_pem'] = ''
        self.assertEqual(result, expected_result)
        ca.delete()
    
    def test_create_ca_files(self):
        """Create a ca; verify file/directory structure."""
        # CA has already been created at setup
        self.assertEqual(self.ca_tree, self.get_tree(self.ca_dir))
        
    def test_delete_missing_ca(self):
        """Delete missing ca; raise NotFound."""
        ca_name = 'missing-ca'
        ca = SpokeCA(ca_name)
        self.assertRaises(error.NotFound, ca.delete)
    
    def test_delete_ca(self):
        """Delete a ca; return True."""
        ca_name = 'test-delete-ca'
        ca_cn = 'Test Delete Certificate Authority'
        ca = SpokeCA(ca_name)
        ca.create(ca_cn)
        result = ca.delete()
        expected_result = {'count': 0, 'type': 'CA', 'data': [], 'exit_code': 3,
                           'msg': 'Deleted CA:'}
        self.assertEqual(result, expected_result)
    
    def test_delete_ca_files(self):
        """Delete a ca; ensure private key is removed."""
        ca_name = 'test-delete-files-ca'
        ca_cn = 'Test Delete Files Certificate Authority'
        ca_dir = os.path.join(self.ca_base_dir, ca_name)
        ca = SpokeCA(ca_name)
        ca.create(ca_cn)
        ca.delete()
        ca_tree = []
        self.assertEqual(ca_tree, self.get_tree(ca_dir))
    
    def tests_validate_self_signed_root_ca(self):
        """Create a self-signed ca; validate own cert; return True."""
        cert = SpokeCACert(self.ca_cn, self.ca_name)
        self.assertTrue(cert._verify())
    
    def test_create_sub_ca(self):
        """Create a subordinate ca; validate cert with parent ca; return True."""
        sub_ca_name = 'test-sub-ca'
        testsubcn = 'Test Subordinate Authority'
        subca = SpokeCA(sub_ca_name)
        subca.create(testsubcn, self.ca_name)
        cert = SpokeCACert(testsubcn, sub_ca_name, self.ca_name)
        self.assertTrue(cert._verify())
        subca.delete()
        
    def test_create_sub_ca_with_missing_parent(self):
        """Create a subordinate ca with missing parent; raise NotFound."""
        root_ca = 'missing-root-ca'
        sub_ca_name = 'test-sub-ca-missing-parent'
        testsubcn = 'Test Subordinate Authority'
        subca = SpokeCA(sub_ca_name)
        self.assertRaises(error.NotFound, subca.create, testsubcn, root_ca)
        subca.delete()

    def test_get_ca(self):
        """Retrieve a ca; return result object."""
        ca = SpokeCA(self.ca_name)
        expected_result = {'count': 1, 'type': 'CA', 'exit_code': 0, 
                           'msg': 'Found CA:'}
        expected_result['data'] = [{'ca_cn': self.ca_cn,
                            'ca_key': self.ca_key_file,
                            'ca_def_duration': self.ca_def_duration,
                            'ca_cert_file': self.ca_cert_file,
                            'ca_cert_as_pem': ''}]
        result = ca.get()
        result['data'][0]['ca_cert_as_pem'] = ''
        self.assertEqual(result, expected_result)
        
    def test_get_missing_ca(self):
        """Retrieve a missing ca; return an empty result object."""
        ca_name = 'missing-ca'
        ca = SpokeCA(ca_name)
        result = ca.get()
        expected_result = {'count': 0, 'type': 'CA', 'data': [], 'exit_code': 3,
                           'msg': 'No CA(s) found'}
        self.assertEqual(result, expected_result)
    
        
# CSR tests
    
    def test_create_invalid_host_csr(self):
        """Create a host cert request with an invalid name; raise InputError."""
        ca_cn = 'Invalid naughty stuff'
        self.assertRaises(error.InputError, SpokeCSR, ca_cn, self.ca_name)
        
    def test_create_ca_csr_for_missing_ca(self):
        """Create a CA CSR for CA which does not exists; raise NotFound."""
        cn = 'Test Create Missing CA CSR'
        ca_name = 'test-missing-ca'
        self.assertRaises(error.NotFound, SpokeCSR, cn, ca_name, ca=True)
        
    def test_create_ca_csr(self):
        """Create a CA CSR; return result object."""
        ca_cn = 'test-create-ca-csr'
        expected_result = {'count': 1, 'type': 'Request', 'exit_code': 0, 
                           'msg': 'Found Request:'}
        expected_result['data'] = [{'req_cn': ca_cn,
                            'verify': 'success',
                            'req_as_pem': ''}]
        csr = SpokeCSR(ca_cn, self.ca_name, ca=True)
        result = csr.create()
        result['data'][0]['req_as_pem'] = ''
        self.assertEqual(result, expected_result)
        csr.delete(delete_key=True)
        
    def test_create_host_csr(self):
        """Create a host CSR; return result object."""
        cn = 'test.host.csr'
        expected_result = {'count': 1, 'type': 'Request', 'exit_code': 0, 
                           'msg': 'Found Request:'}
        expected_result['data'] = [{'req_cn': cn,
                            'verify': 'success',
                            'req_as_pem': ''}]
        csr = SpokeCSR(cn, self.ca_name)
        result = csr.create()
        result['data'][0]['req_as_pem'] = ''
        self.assertEqual(result, expected_result)
        csr.delete(delete_key=True)
        
    def test_create_host_csr_files(self):
        """Create a host CSR; verify req file created; return True."""
        cn = 'test.host.csr.file'
        csr = SpokeCSR(cn, self.ca_name)
        csr.create()
        self.assertTrue(os.path.exists(csr.req_file))
        csr.delete(delete_key=True)
        
    def test_validate_ca_csr(self):
        """Create a CA CSR; validate CSR; return True."""
        ca_cn = 'test-create-ca-csr'
        csr = SpokeCSR(ca_cn, self.ca_name, ca=True)
        csr.create()
        self.assertTrue(csr._verify())
        csr.delete(delete_key=True)
        
    def test_delete_ca_csr(self):
        """Delete a CA CSR; return True."""
        ca_cn = 'Test Delete CA CSR'
        csr = SpokeCSR(ca_cn, self.ca_name, ca=True)
        csr.create()
        result = csr.delete(delete_key=True)
        expected_result = {'count': 0, 'type': 'Request', 'data': [], 'exit_code': 3,
                           'msg': 'Deleted Request:'}
        self.assertEqual(result, expected_result)
        
    def test_delete_ca_csr_files(self):
        """Delete a CA CSR; return True."""
        ca_cn = 'Test Delete CA CSR'
        csr = SpokeCSR(ca_cn, self.ca_name, ca=True)
        csr.create()
        csr.delete(delete_key=True)
        self.assertFalse(os.path.exists(csr.req_file))
        
    def test_get_a_missing_csr(self):
        """Retrieve a missing CSR; return empty results object."""
        cn = 'missing.foo.com'
        csr = SpokeCSR(cn, self.ca_name)
        result = csr.get()
        expected_result = {'count': 0, 'type': 'Request', 'data': [], 'exit_code': 3,
                           'msg': 'No Request(s) found'}
        self.assertEqual(result, expected_result)
        
    def test_delete_a_missing_csr(self):
        """Delete a missing CSR; raise NotFound."""
        cn = 'missing.foo.com'
        csr = SpokeCSR(cn, self.ca_name)
        self.assertRaises(error.NotFound, csr.delete)
        
# Cert tests

    def test_create_invlaid_host_cert(self):
        """Create a host cert with an invalid name; raise InputError."""
        cn = 'Invalid naughty stuff'
        self.assertRaises(error.InputError, SpokeHostCert, cn, self.ca_name)
        
    def test_create_host_cert_missing_parent(self):
        """Create a host cert with a missing CA; raise NotFound."""
        cn = 'test-missing-ca-cn'
        ca_name = 'test-missing-ca-cert'
        self.assertRaises(error.NotFound, SpokeHostCert, cn, ca_name)
        
    def test_create_host_cert(self):
        """Create a host cert; return True."""
        cn = 'test.foo.com'
        cert = SpokeHostCert(cn, self.ca_name)
        expected_result = {'count': 1, 'type': 'Certificate', 'exit_code': 0, 
                           'msg': 'Found Certificate:'}
        expected_result['data'] = [{'cert_cn': cn,
                            'verify': 'success',
                            'cert_as_pem': ''}]
        result = cert.create()
        result['data'][0]['cert_as_pem'] = ''
        self.assertEqual(result, expected_result)
        cert.delete()
        
    def test_create_host_cert_file(self):
        """Create a host cert; test for cert file; return True."""
        cn = 'test.foo-file.com'
        cert = SpokeHostCert(cn, self.ca_name)
        cert.create()
        self.assertTrue(os.path.exists(cert.cert_file))
        cert.delete()
        
    def test_validate_host_cert(self):
        """Validate a host cert; return True."""
        cn = 'test.valid-cert.com'
        cert = SpokeHostCert(cn, self.ca_name)
        cert.create()
        self.assertTrue(cert._verify())
        cert.delete()
        
    def test_delete_host_cert(self):
        """Delete a host cert; return True."""
        cn = 'test.delete-foo.com'
        cert = SpokeHostCert(cn, self.ca_name)
        cert.create()
        expected_result = {'count': 0, 'type': 'Certificate', 'data': [], 'exit_code': 3,
                           'msg': 'Deleted Certificate:'}
        result = cert.delete()
        self.assertEqual(result, expected_result)
        
    def test_delete_missing_cert(self):
        """Delete a missing host cert; raise NotFound."""
        cn = 'missing-host-cert.com'
        cert = SpokeHostCert(cn, self.ca_name)
        self.assertRaises(error.NotFound, cert.delete)
        
    def test_create_host_alt_name(self):
        """Create a host certificate with an alt name; return True."""
        cn = 'test.foo-alt.com'
        alt_name = 'test.foo-other.com'
        cert = SpokeHostCert(cn, self.ca_name)
        expected_result = {'count': 1, 'type': 'Certificate', 'exit_code': 0, 
                           'msg': 'Found Certificate:'}
        expected_result['data'] = [{'cert_cn': cn,
                            'verify': 'success',
                            'cert_as_pem': ''}]
        result = cert.create(alt_name)
        result['data'][0]['cert_as_pem'] = ''
        self.assertEqual(result, expected_result)
        cert.delete()
        
    def test_create_host_cert_invalid_alt_name(self):
        """Create a host cert with an invalid alt name; raise InputError."""
        cn = 'test.foo-valid.com'
        alt_name = 'test.foo invalid.com'
        cert = SpokeHostCert(cn, self.ca_name)
        self.assertRaises(error.InputError, cert.create, alt_name)
        
    def test_get_host_cert(self):
        """Retrieve a host cert; return a results object."""
        cn = 'test.get.foo.com'
        cert = SpokeHostCert(cn, self.ca_name)
        expected_result = {'count': 1, 'type': 'Certificate', 'exit_code': 0, 
                           'msg': 'Found Certificate:'}
        expected_result['data'] = [{'cert_cn': cn,
                            'verify': 'success',
                            'cert_as_pem': ''}]
        cert.create()
        result = cert.get()
        result['data'][0]['cert_as_pem'] = ''
        self.assertEqual(result, expected_result)
        cert.delete()
        
    def test_get_missing_host_cert(self):
        """Retrieve a missing host cert" return an empty results object."""
        cn = 'test.get-missing-foo.com'
        cert = SpokeHostCert(cn, self.ca_name)
        expected_result = {'count': 0, 'type': 'Certificate', 'data': [], 'exit_code': 3,
                           'msg': 'No Certificate(s) found'}
        result = cert.get()
        self.assertEqual(result, expected_result)
