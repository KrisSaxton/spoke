"""Certificate Authority management module.

Classes:
SpokeCA - Creation/deletion/modification/retrieval of CA details.
SpokeCSR- Creation/deletion/modification/retrieval of CSR details.
SpokeCert - Super class for management of certificates.
SpokeCACert- Creation/deletion/modification/retrieval of CA cert details.
SpokeHostCert- Creation/deletion/modification/retrieval of Host cert details.
Exceptions:
NotFound - raised on failure to find an object when one is expected.
AlreadyExists -raised on attempts to create an object when one already exists.
InputError - raised on invalid input.
ValidationError - raised when an action completes OK but validation fails.
SpokeError - raised when action fails for unknown reason.

TODO Support different key algorithms
TODO Support for creation/use of CRLs (i.e. revocation)
TODO Support for Authority Key Identifier (currently bust in M2Crypto)
"""

# core modules
import traceback
import hashlib
import os.path

# own modules
import error
import config
import logger
import common

# 3rd party modules
try:
    from M2Crypto import X509, RSA, m2, EVP
except:
    msg = 'Failed to import M2Crypto'
    raise error.SpokeError(msg)

class SpokeCA():
    
    """Provide CRUD methods to Certificate Authority objects."""
    
    def __init__(self, ca_name):    
        """Get config, setup logging."""
        self.config = config.setup()
        self.log = logger.setup(__name__)
        self.ca_name = common.is_shell_safe(ca_name)
        self.ca_base_dir = self.config.get('CA', 'ca_base_dir')
        self.ca_dir = os.path.join(self.ca_base_dir, self.ca_name) 
        self.ca_key_rdir = self.config.get('CA', 'ca_key_dir', 'private')
        self.ca_cert_rdir = self.config.get('CA', 'ca_cert_dir', 'certs')
        self.ca_req_rdir = self.config.get('CA', 'ca_req_dir', 'reqs')
        self.ca_cert_name = self.config.get('CA', 'ca_pub_cert', 'ca-cert.pem')
        self.ca_bundle_name = self.config.get('CA', 'ca_bundle', 'ca-bundle.pem')
        self.ca_req_name = self.config.get('CA', 'ca_req', 'ca-req.pem')
        self.ca_key_name = self.config.get('CA', 'ca_priv_key', 'ca-key.pem')
        self.ca_index_name = self.config.get('CA', 'ca_index', 'index')
        self.ca_serial_name = self.config.get('CA', 'ca_serial', 'serial')
        self.ca_cert_dir = os.path.join(self.ca_dir, self.ca_cert_rdir)
        self.ca_key_dir = os.path.join(self.ca_dir, self.ca_key_rdir)
        self.ca_req_dir = os.path.join(self.ca_dir, self.ca_req_rdir)
        self.ca_cert_file = os.path.join(self.ca_cert_dir, self.ca_cert_name)
        self.ca_bundle_file = os.path.join(self.ca_base_dir, 
                                           self.ca_bundle_name)
        
        self.ca_key_file = os.path.join(self.ca_key_dir, self.ca_key_name)
        self.ca_req_file = os.path.join(self.ca_req_dir, self.ca_req_name)
        self.ca_index_file = os.path.join(self.ca_cert_dir, self.ca_index_name)
        self.ca_serial_file = os.path.join(self.ca_dir, self.ca_serial_name)
            
        self.ca_key = os.path.join(self.ca_key_dir, self.ca_key_file)
        self.ca_cert = os.path.join(self.ca_cert_dir, self.ca_cert_file)
        self.req_dirs = [ self.ca_base_dir, self.ca_dir, self.ca_key_dir, 
                         self.ca_req_dir, self.ca_cert_dir ]
        self.req_files = [ self.ca_index_file, self.ca_serial_file,
                          self.ca_key_file, self.ca_cert_file ]
        try:
            ca_cert = X509.load_cert(self.ca_cert_file, format=1)
            self.ca_cn = ca_cert.get_subject().CN
            self.ca_cert_as_pem = ca_cert.as_pem()
        except:
            msg = 'CA cert file %s does not exist' % self.ca_cert_file
            self.log.debug(msg)      
        self.ca_country = self.config.get('CA', 'ca_country', 'GB')
        try:
            self.ca_state = self.config.get('CA', 'ca_state')
        except:
            self.ca_state = None
        self.ca_locality = self.config.get('CA', 'ca_locality', 'London')
        self.ca_org = self.config.get('CA', 'ca_org', 'Acme Ltd')
        self.ca_ou = self.config.get('CA', 'ca_ou', 'Certificate Services')
        self.ca_email = self.config.get('CA', 'ca_email', 'ca@acme.co.uk')
        self.ca_def_duration = self.config.get('CA', 'ca_def_duration', 1095)
        self.ca_keypass = self.config.get('CA', 'ca_keypass', '')
        # Try to get some more info from req/cert files if they are present
        self.ca_info = self._get_ca_info()
        try:
            self.ca_cn = self.ca_info['ca_cn']
        except:pass
        try:
            self.ca_cert_as_pem = self.ca_info['ca_cert_as_pem']
        except:pass
            
    def __str__(self):
        return self.ca_cert_as_pem

    def _pass_callback(self, v):
        return self.ca_keypass
    
    def _get_serial(self):
        """Retreives current serial number from CA serial file"""
        try:
            f = open(self.ca_serial_file, 'r')
            serialno = f.readline()
            f.close
        except:
            # Initialise serial file
            serialno = 0
        return int(serialno)           

    def _increment_serial(self):
        """Fetches current serial number and increments file to next number"""       
        serialno = self._get_serial()
        nextno = serialno + 1
        nextno = str(nextno)
        f = open(self.ca_serial_file, 'w')
        f.write(nextno)
        f.write('\n')
        f.flush() # Not sure if this has any effect with file I/O
        f.close()
        return serialno
    
    def _gen_x509_name(self, cn):
        """Generate an X509 name object; populate and return it."""   
        name = X509.X509_Name()
        name.CN = cn
        name.C = self.ca_country
        name.S = self.ca_state
        name.L = self.ca_locality
        name.O = self.ca_org
        name.OU = self.ca_ou
        name.Email = self.ca_email
        return name
    
    def _get_ca_info(self):
        ca_info = {}
        try:
            ca_cert = X509.load_cert(self.ca_cert_file, format=1)
            ca_info['ca_cn'] = ca_cert.get_subject().CN
            ca_info['ca_cert_as_pem'] = ca_cert.as_pem()
            msg = 'Retrieved CN and pem from CA cert file %s' % self.ca_cert_file
            self.log.debug(msg)
        except:
            msg = 'CA cert file %s does not exist' % self.ca_cert_file
            self.log.debug(msg)
            try:
                ca_req = X509.load_request(self.ca_req_file)
                ca_info['ca_cn'] = ca_req.get_subject().CN
                msg = 'Retrieved CN from CA req file %s' % self.ca_req_file
                self.log.debug(msg)
            except:
                msg = 'CA req file %s does not exist' % self.ca_req_file
                self.log.debug(msg)
        return ca_info
        
    def create(self, cn, signer=None):
        """Create a CA with default file structure and configuration files."""
        # If signer is set, this CA cert will be signed by the signer, 
        # otherwise a self-signed certificate will be produced.
        self.ca_cn = common.is_shell_safe(cn)
        if signer:
            signer = common.is_shell_safe(signer)
        if os.path.exists(self.ca_key_file) or \
        os.path.exists(self.ca_cert_file):
            msg = 'CA %s exists, delete first to continue' % self.ca_name   
            raise error.AlreadyExists(msg)
        self.req_dirs.sort()
        for directory in self.req_dirs:
            if not (os.path.exists(directory)):
                try:
                    self.log.debug('Creating directory %s' % directory)
                    os.makedirs(directory)
                except Exception as e:
                    raise e
        
        msg = 'Creating CSR with cn=%s and requester=%s' % (cn,self.ca_name)
        self.log.debug(msg)
        csr = SpokeCSR(cn, self.ca_name, ca=True)
        csr.create()
        msg = 'Creating Cert with cn=%s, requester=%s and signer=%s' % \
                                                    (cn, self.ca_name, signer)
        self.log.debug(msg)
        cert = SpokeCACert(cn, self.ca_name, signer)
        cert.create()
        result = self.get()
        if result['exit_code'] == 0 and result['count'] == 1:
            result['msg'] = "Created %s:" % result['type']
            return result
        else:
            msg = 'Create operation returned OK, but unable to find object'
            raise error.ValidationError(msg)
        return result
    
    def get(self):
        """Search for a CA; return a result object containing CA attributes."""
        data = []
        item = {}
        for directory in self.req_dirs:
            if not (os.path.exists(directory)):
                self.log.debug('Cannot find %s' % directory)
                result = common.process_results(data, 'CA')
                self.log.debug('Result: %s' % result)
                return result
        ca_info = self._get_ca_info()
        item.update(ca_info)
        item['ca_key'] = self.ca_key_file
        item['ca_cert_file'] = self.ca_cert_file
        item['ca_def_duration'] = self.ca_def_duration
        data.append(item)
        result = common.process_results(data, 'CA')
        self.log.debug('Result: %s' % result)
        return result
        
    def delete(self):
        """Delete a CA's file structure and configuration files."""
        # NB This will fail if you've been storing certs or reqs
        if self.get()['data'] == []:
            msg = '%s does not exist, cannot delete' % self.ca_name
            raise error.NotFound(msg)
        self.req_files.append(self.ca_req_file)
        for req_file in self.req_files:
            if (os.path.exists(req_file)):
                os.remove(req_file)
        self.req_dirs.sort(reverse=True)
        for directory in self.req_dirs:
            if (os.path.exists(directory)):
                try:
                    os.removedirs(directory)
                except Exception as e:
                    msg = 'Unable to delete directory %s: %s' % (directory, e)
                    self.log.debug(msg)
        result = self.get()
        if result['exit_code'] == 3 and result['count'] == 0:
            result['msg'] = "Deleted %s:" % result['type']
            return result
        else:
            msg = 'Delete operation returned OK, but object still there?'
            raise error.ValidationError(msg)
    
class SpokeCSR():
    
    """Provide CRUD methods to Certificate Request objects."""
    
    def __init__(self, cn, requester=None, ca=None):    
        """Get config, setup logging."""
        self.config = config.setup()
        self.log = logger.setup(self.__module__)
        if not requester:
            requester = self.config.get('CA', 'ca_default_ca')
        requester = common.is_shell_safe(requester)
        self.is_a_ca = ca
        self.reqca = SpokeCA(requester)
        if not self.reqca.get()['data']:
            msg = 'CA %s does not exist; please create' % requester
            raise error.NotFound(msg)
        if self.is_a_ca:
            self.cn = common.is_shell_safe(cn)
            self.req_file = self.reqca.ca_req_file
            self.key_file = self.reqca.ca_key_file
        else: # We're dealing with a host CSR
            self.cn = common.validate_domain(cn)
            key_name = '%s.key.pem' % cn
            req_name = '%s.req' % cn
            self.key_file = os.path.join(self.reqca.ca_dir, key_name)
            self.req_file = os.path.join(self.reqca.ca_dir, req_name)
        
    def _genkey_callback(self):
        pass
            
    def _gen_rsq_key(self):
        return RSA.gen_key(2048, m2.RSA_F4, callback=self._genkey_callback)
    
    def _gen_and_save_key(self, keyfile):
        """Generate a private key, save and return it."""
        try:
            rsa = self._gen_rsq_key()
            rsa.save_key(keyfile, None)      
            pkey = EVP.PKey()
            pkey.assign_rsa(rsa, 1)
        except Exception as e:
            raise e
        return pkey
    
    def _gen_x509_name(self, cn):
        """Generate an X509 name object; populate and return it."""   
        name = X509.X509_Name()
        name.CN = cn
        name.C = self.reqca.ca_country
        name.S = self.reqca.ca_state
        name.L = self.reqca.ca_locality
        name.O = self.reqca.ca_org
        name.OU = self.reqca.ca_ou
        name.Email = self.reqca.ca_email
        return name
    
    def _verify(self):
        """Verify a certificate request; return True (0) or False (1)"""
        try:
            req = X509.load_request(self.req_file)
        except:
            msg = 'Certificate request file %s not found' % self.req_file
            raise error.NotFound(msg)
        pkey = req.get_pubkey()
        return req.verify(pkey)
    
    def get(self):
        """Retrieve a certificate request; return results object."""
        # TODO Put this in a dir walk loop so it supports multiple reqs
        data = []
        item = {}
        try:
            req = X509.load_request(self.req_file)
        except IOError:
            result = common.process_results(data, 'Request')
            return result
        item['req_cn'] = req.get_subject().CN
        item['req_as_pem'] = req.as_pem()
        pkey = req.get_pubkey()
        if req.verify(pkey):
            item['verify'] = 'success'
        data.append(item)
        result = common.process_results(data, 'Request')
        return result
        
    def create(self):
        """Create certificate request; return certificate request file."""   
        try:
            pkey = self._gen_and_save_key(self.key_file)
        except IOError:
            msg = 'Failed to open key file: ' + self.key_file
            raise error.NotFound(msg)
        name = self._gen_x509_name(self.cn)
        req = X509.Request()
        req.set_version(3)
        req.set_pubkey(pkey)
        req.set_subject_name(name)
        req.sign(pkey, 'sha1')
        req.save(self.req_file)
        result = self.get()
        return result
    
    def delete(self, delete_key=True):
        """Delete a certificate request; return True"""
        try: 
            os.remove(self.req_file)
            if delete_key:
                os.remove(self.key_file)
        except (OSError, IOError):
            msg = 'Failed to delete request %s and/or key %s' \
                                            % (self.req_file, self.key_file)
            raise error.NotFound(msg)
        except Exception as e:
            raise e
        result = self.get()
        if result['exit_code'] == 3 and result['count'] == 0:
            result['msg'] = "Deleted %s:" % result['type']
            return result
        else:
            msg = 'Delete operation returned OK, but object still there?'
            raise error.ValidationError(msg)
    
class SpokeCert():
    
    """Provide CRUD methods to X509 certificate objects."""
    
    def __init__(self, cn, requester, signer=None):    
        """Get config, setup logging."""
        self.config = config.setup()
        self.log = logger.setup(__name__)
        self.reqca = self._get_ca(requester)
        if signer:
            self.signca = self._get_ca(signer)
        else:
            self.signca = self.reqca
        
    def _get_ca(self, ca_name):
        ca_name = common.is_shell_safe(ca_name)
        ca = SpokeCA(ca_name)
        if not ca.get()['data']:
            msg = "Can't find CA %s" % ca_name
            raise error.NotFound(msg)
        return ca
        
    def _gen_pubkey_fingerprint(self, pkey):
        try:
            self.pkey = pkey
            h = hashlib.new('sha1')
            h.update(self.pkey.as_der())
            client_serial = h.hexdigest().upper()
            client_serial_hex = ''
        
            for byte in xrange(20):
                client_serial_hex += client_serial[byte*2] + client_serial[byte*2+1]
                if byte < 19:
                    client_serial_hex += ':'
        except Exception,e:
            raise e
        return client_serial_hex
    
    def _set_duration(self, cert):
        """Set certificate duration; return certificate object."""
        notBefore = m2.x509_get_not_before(cert.x509)
        notAfter = m2.x509_get_not_after(cert.x509)
        days = self.signca.ca_def_duration
        common.is_number(days)
        m2.x509_gmtime_adj(notBefore, 0)
        m2.x509_gmtime_adj(notAfter, 60*60*24*int(days))
        return cert
    
    def _add_extensions(self, cert, pubkey_fprint):
        """Stub method to add cert extensions, override in your sub class."""
        return cert
    
    def _save_cert(self, cert):
        """Save a certificate file; return True."""
        cert.save(self.cert_file)
        try:
            os.remove(self.req_file)
        except:
            msg = 'Unable to remove %s' % self.req_file
            self.log.debug(msg)
        return True
    
    def _do_req(self):
        """Stub method to create cert requests, override in your sub class."""
        pass
    
    def _verify(self):
        """Verify a host certificate; return True (0) or False (1) """        
        cacert = X509.load_cert(self.signca.ca_cert_file)
        capubkey = cacert.get_pubkey()
        cert = X509.load_cert(self.cert_file)
        return cert.verify(capubkey)
    
    def create(self, alt_name=None):
        """Sign a certificate request; return a certificate."""
        if alt_name:
            self.alt_name = common.validate_domain(alt_name)
        req = self._do_req()
        issuer = self.signca._gen_x509_name(self.signca.ca_cn)
        cert = X509.X509()
        cert.set_version(2)
        serialnumber = self.signca._increment_serial()
        cert.set_serial_number(serialnumber)
        cert.set_issuer_name(issuer)
        cert.set_subject(req.get_subject())
        certpubkey = req.get_pubkey()
        cert.set_pubkey(certpubkey)
        pubkey_fprint = self._gen_pubkey_fingerprint(certpubkey)
        cert = self._set_duration(cert)
        # Create and add certificate extensions
        cert = self._add_extensions(cert, pubkey_fprint)          
        # Sign the cert with the CA key
        cakey = RSA.load_key(self.signca.ca_key_file, 
                                 callback = self.signca._pass_callback)
        capkey = EVP.PKey()
        capkey.assign_rsa(cakey, 1)
        cert.sign(capkey, 'sha1')   
        self._save_cert(cert)
        result = self.get()
        return result
    
    def get(self):
        """Retrieve a certificate; return results object."""
        # TODO Put this in a dir walk loop so it supports multiple reqs
        data = []
        item = {}
        try:
            cert = X509.load_cert(self.cert_file)
        except IOError:
            result = common.process_results(data, 'Certificate')
            self.log.debug('Result: %s' % result)
            return result
        item['cert_cn'] = cert.get_subject().CN
        item['cert_as_pem'] = cert.as_pem()
        item['verify'] = 'failure'
        if self._verify():
            item['verify'] = 'success'
        data.append(item)
        result = common.process_results(data, 'Certificate')
        self.log.debug('Result: %s' % result)
        return result
    
    def delete(self):
        """Delete a certificate and its associated key."""
        # NB This will fail if you've been storing certs or reqs
        for file in (self.key_file, self.cert_file):
            try:
                os.remove(file)
            except (OSError, IOError):
                msg = 'Unable to delete file %s' % file
                raise error.NotFound(msg)
        result = self.get()
        if result['exit_code'] == 3 and result['count'] == 0:
            result['msg'] = "Deleted %s:" % result['type']
            return result
        else:
            msg = 'Delete operation returned OK, but object still there?'
            raise error.ValidationError(msg)
    
class SpokeHostCert(SpokeCert):
    
    """Subclass of SpokeCert specialised for creating host certs."""
    
    def __init__(self, cn, requester):
        self.cn = common.validate_domain(cn)
        SpokeCert.__init__(self, cn, requester)
        self.key_file = os.path.join(self.signca.ca_dir, '%s.key.pem' % self.cn)
        self.req_file = os.path.join(self.signca.ca_dir, '%s.req' % self.cn)
        self.cert_file = os.path.join(self.signca.ca_dir, '%s.cert.pem' % self.cn)
        
    def _add_extensions(self, cert, pubkey_fprint, alt_name=None):
        """Add host-specific extensions to cert; return cert."""
        ext_ski = X509.new_extension('subjectKeyIdentifier', pubkey_fprint)
        ext_usage = X509.new_extension('keyUsage', 'Digital Signature, Non Repudiation, Key Encipherment, Data Encipherment')
        ext_const = X509.new_extension('basicConstraints', 'CA:FALSE')
        ext_comment = X509.new_extension('nsComment', 'OpenSSL Generated Certificate')
        if alt_name:
            ext_alt = X509.new_extension('subjectAltName', "DNS:%s" % self.alt_name)
        # adding Authority Key Identifier currently broken in M2Crypto (python seg faults)
        #cacert = X509.load_cert(self.ca.cert)
        #authkeyid = cacert.get_ext('authorityKeyIdentifier')
        #ext_aki = X509.new_extension('authorityKeyIdentifier', authkeyid.get_value())                      
        cert.add_ext(ext_ski)
        #cert.add_ext(ext_aki)       
        cert.add_ext(ext_const) 
        cert.add_ext(ext_usage)               
        cert.add_ext(ext_comment)
        if alt_name:
            cert.add_ext(ext_alt)
        return cert
    
    def _do_req(self):
        """Create a certificate request; return a certificate request object."""
        csr = SpokeCSR(self.cn, self.reqca.ca_name)
        csr.create()
        req = X509.load_request(self.req_file, format=1)
        return req
    
class SpokeCACert(SpokeCert):
    
    """Subclass of SpokeCert specialised for creating CA certs."""
    
    def __init__(self, cn, requester, signer=None):
        self.cn = common.is_shell_safe(cn)
        SpokeCert.__init__(self, cn, requester, signer)
        if not signer:
            # We're dealing with self-signed CA cert
            self.log.debug('No signer given, self-signing')
            self.self_signed = True
        else:
            # We're dealing with a CA signed by another
            signer = common.is_shell_safe(signer)
            self.self_signed = False
        self.log.debug('Issuer cn is %s' % self.signca.ca_cn)
        self.req_file = self.reqca.ca_req_file
        self.key_file = self.reqca.ca_key_file
        self.cert_file = self.reqca.ca_cert_file
        
    def _add_extensions(self, cert, pubkey_fprint):
        """Add CA-specific extensions to cert; return cert."""
        ext_ski = X509.new_extension('subjectKeyIdentifier', pubkey_fprint)
        ext_usage = X509.new_extension('keyUsage', 'Certificate Sign, CRL Sign')
        ext_usage.set_critical(1)
        ext_const = X509.new_extension('basicConstraints', 'CA:TRUE')
        # adding Authority Key Identifier currently broken see Header Notes   
        cert.add_ext(ext_ski)       
        cert.add_ext(ext_const) 
        cert.add_ext(ext_usage)
        return cert
    
    def _save_cert(self, cert):
        try:
            os.remove(self.req_file)
        except:
            msg = 'Unable to remove %s' % self.req_file
            self.log.debug(msg)
        if not self.self_signed:
            # Successful verification relies on the signing CA's cert
            # being the first in the file!  So don't change the order.
            cert_bundle = open(self.cert_file, 'w')
            cert_bundle.write(cert.as_pem())
            cert_bundle.write(self.signca.ca_cert_as_pem)
            cert_bundle.close()
        else:
            cert.save(self.cert_file)
        return True
    
    def _do_req(self):
        """Create a certificate request; return a certificate request object."""
        req = X509.load_request(self.req_file, format=1)
        return req