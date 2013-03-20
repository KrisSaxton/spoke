"""Tests Spoke email.py module.
TODO: Test that '.'s in uids get subbed for '^' in Cyrus mailbox names 
TODO: Test that user's org has domain entry for email address being added
TODO: Test that email address doesn't exist anywhere in the org
"""
# core modules
import unittest
# own modules
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.log as logger
from spoke.lib.org import SpokeOrg
from spoke.lib.user import SpokeUser
from spoke.lib.email import SpokeEmailAccount
from spoke.lib.email import SpokeEmailDomain
from spoke.lib.email import SpokeEmailAddress


class SpokeEmailTest(unittest.TestCase):

    """A Class for testing the Spoke email.py module."""
    
    def __init__(self, methodName):
        """Setup config data and LDAP connection."""
        unittest.TestCase.__init__(self, methodName)
        common_config = '../../contrib/spoke.conf'
        custom_config = '/tmp/spoke.conf'
        config_files = (common_config, custom_config)
        self.config = config.setup(config_files)
        self.log = logger.log_to_console()
        self.base_dn = self.config.get('LDAP', 'basedn')
        self.search_scope = 2 # ldap.SCOPE_SUBTREE
        self.retrieve_attr = None
        self.org_name = 'SpokeEmailTest'
        self.org_attr = self.config.get('ATTR_MAP', 'org_attr')
        self.org_def_children = self.config.get('ATTR_MAP', 'org_def_children')
        self.org_children = self.org_def_children.split(',')
        self.container_attr = self.config.get('ATTR_MAP', 'container_attr')
        self.user_container = self.config.get('ATTR_MAP', 'user_container')
        self.user_key = self.config.get('ATTR_MAP', 'user_key')
        self.first = 'timmy'
        self.last = 'test'
        self.user_id = self.first + self.last
        self.user_class = self.config.get('ATTR_MAP', 'user_class')
        self.email_dom = 'test.email.loc'
        self.email_addr = self.user_id + '@' + self.email_dom
        self.imap_class = self.config.get('ATTR_MAP', 'imap_class')
        self.imap_enable = self.config.get('ATTR_MAP', 'imap_enable')
        self.imap_mailbox = self.config.get('ATTR_MAP', 'imap_mailbox')
        self.imap_domain = self.config.get('ATTR_MAP', 'imap_domain')
        self.imap_partition = self.config.get('ATTR_MAP', 'imap_partition')
        self.imap_partition_def = self.config.get('ATTR_MAP', \
                                                'imap_partition_def')
        self.smtp_class = self.config.get('ATTR_MAP', 'smtp_class')
        self.smtp_domain = self.config.get('ATTR_MAP', 'smtp_domain')
        self.smtp_address = self.config.get('ATTR_MAP', 'smtp_address')
        self.smtp_destination = self.config.get('ATTR_MAP', 'smtp_destination')
        self.smtp_enable = self.config.get('ATTR_MAP', 'smtp_enable')
        self.smtp_pri_address = self.config.get('ATTR_MAP', 'smtp_pri_address')
        
    def setUp(self):
        """Create test organisation, user and email domain."""
        org = SpokeOrg()
        org.create(self.org_name)
        dom = SpokeEmailDomain(self.org_name)
        dom.create(self.email_dom)
        user = SpokeUser(self.org_name)
        user.create(self.email_addr, self.first, self.last)
        acc = SpokeEmailAccount(self.org_name, self.user_id)
        acc.create(self.email_addr)

    def tearDown(self):
        """Delete test organisation, user and email domain."""
        acc = SpokeEmailAccount(self.org_name, self.user_id)
        acc.delete(self.email_addr)
        user = SpokeUser(self.org_name)
        user.delete(self.first, self.last)
        dom = SpokeEmailDomain(self.org_name)
        dom.delete(self.email_dom)
        org = SpokeOrg()
        org.delete(self.org_name, self.org_children)
        
# Email account tests

    def test_email_account_operation_with_missing_org(self):
        """Create email account in a missing org; raise MissingParent."""
        org_name = 'TestMissingOrg'
        self.assertRaises(error.NotFound, \
                          SpokeEmailAccount, org_name, self.user_id)
        
    def test_email_account_operation_with_missing_user(self):
        """Instantiate email account with a missing user; raise NotFound."""
        user_id = 'missinguser'
        self.assertRaises(error.NotFound, \
                          SpokeEmailAccount, self.org_name, user_id)
        
    def test_create_email_account(self):
        """Create email account; return email account object."""
        first = 'create_email'
        last = 'account_test'
        user_id = first + last
        email_addr = first + last + '@' + self.email_dom
        user = SpokeUser(self.org_name)
        user.create(email_addr, first, last)
        
        org = '%s=%s' % (self.org_attr, self.org_name)
        people = '%s=%s' % (self.container_attr, self.user_container)
        uid = '%s=%s' % (self.user_key, user_id)
        dn = '%s,%s,%s,%s' % (uid, people, org, self.base_dn)
        dn_info = {'objectClass': ['top', 'inetOrgPerson', self.user_class,
                                    self.imap_class, self.smtp_class],
                   self.imap_enable: ['TRUE'],
                   self.imap_mailbox: [user_id],
                   self.imap_domain: [self.email_dom],
                   self.imap_partition: [self.imap_partition_def],
                   self.smtp_destination: [email_addr],
                   self.smtp_enable: ['TRUE'],
                   self.smtp_pri_address: [email_addr]
                   }
        expected_result = [(dn, dn_info)]        
        acc = SpokeEmailAccount(self.org_name, user_id)
        result = acc.create(email_addr)['data']
        self.assertEqual(result, expected_result)
        user.delete(first, last)
    
    def test_create_email_account_twice(self):
        """Create an email account twice; raise AlreadyExists."""
        email_addr = 'testcreatetwins@' + self.email_dom
        acc = SpokeEmailAccount(self.org_name, self.user_id)
        self.assertRaises(error.AlreadyExists, acc.create, email_addr)
        
    def test_get_email_account(self):
        """Retrieve an email account; return an email account object."""
        email_addr = self.user_id + '@' + self.email_dom
        org = '%s=%s' % (self.org_attr, self.org_name)
        people = '%s=%s' % (self.container_attr, self.user_container)
        uid = '%s=%s' % (self.user_key, self.user_id)
        dn = '%s,%s,%s,%s' % (uid, people, org, self.base_dn)
        dn_info = {self.imap_enable: ['TRUE'],
                   self.imap_mailbox: [self.user_id],
                   self.imap_domain: [self.email_dom],
                   self.imap_partition: [self.imap_partition_def],
                   self.smtp_destination: [email_addr],
                   self.smtp_enable: ['TRUE'],
                   self.smtp_pri_address: [email_addr]
                   }
        expected_result = [(dn, dn_info)]        
        acc = SpokeEmailAccount(self.org_name, self.user_id)
        result = acc.get(self.email_addr)['data']
        self.assertEqual(result, expected_result)
        
    def test_get_missing_email_account(self):
        """Retrieve a missing email account; return empty list."""
        acc = SpokeEmailAccount(self.org_name, self.user_id)
        email_addr = 'missing@' + self.email_dom
        result = acc.get(email_addr)['data']
        expected_result = []
        self.assertEqual(result, expected_result)

    def test_delete_email_account(self):
        """Delete an email account; return empty results object."""
        first = 'delete_email'
        last = 'account_test'
        user_id = first + last
        email_addr = first + last + '@' + self.email_dom
        user = SpokeUser(self.org_name)
        user.create(email_addr, first, last)
        acc = SpokeEmailAccount(self.org_name, user_id)
        acc.create(email_addr)
        newacc = SpokeEmailAccount(self.org_name, user_id)
        self.assertTrue(newacc.delete(email_addr))
        user.delete(first, last)
        
    def test_delete_missing_email_account(self):
        """Delete a missing email account; raise NotFound."""
        email_addr = 'deletemissing@' + self.email_dom
        first = 'test'
        last = 'missing'
        user_id = first + last
        user = SpokeUser(self.org_name)
        user.create(email_addr, first, last)
        acc = SpokeEmailAccount(self.org_name, user_id)
        self.assertRaises(error.NotFound, acc.delete, email_addr)
        user.delete(first, last)
        
    def test_invalid_email_account_input(self):
        """Input invalid email account; raise InputError."""
        acc = SpokeEmailAccount(self.org_name, self.user_id)
        email_addr = '*@domain.loc'
        self.assertRaises(error.InputError, acc.get, email_addr)
        
# Email address tests
        
    def test_create_email_address(self):
        """Create email address; return result."""
        email_addr = 'testcreate@' + self.email_dom
        org = 'o=%s' % (self.org_name)
        people = '%s=%s' % (self.container_attr, self.user_container)
        uid = '%s=%s' % (self.user_key, self.user_id)
        dn = '%s,%s,%s,%s' % (uid, people, org, self.base_dn)
        dn_info = {self.smtp_address: [email_addr]}
        expected_result = [(dn, dn_info)]        
        addr = SpokeEmailAddress(self.org_name, self.user_id)
        result = addr.create(email_addr)['data']
        self.assertEqual(result, expected_result)
    
    def test_create_email_address_twice(self):
        """Create an email address twice; raise AlreadyExists."""
        email_addr = 'testcreatetwins@' + self.email_dom
        addr = SpokeEmailAddress(self.org_name, self.user_id)
        addr.create(email_addr)
        self.assertRaises(error.AlreadyExists, addr.create, email_addr)
        
    def test_email_address_operation_with_missing_org(self):
        """Create an email address in a missing org; raise NotFound."""
        org_name = 'TestMissingOrg'
        self.assertRaises(error.NotFound, SpokeEmailAddress, org_name, 
                          self.user_id)
        
    def test_email_address_operation_with_missing_user(self):
        """Create an email address on a missing user; raise NotFound."""
        user_id = 'missinguser'
        self.assertRaises(error.NotFound, SpokeEmailAddress, self.org_name, 
                          user_id)
        
    def test_get_email_address(self):
        """Retrieve an email address; return an email address object."""
        email_addr = 'test_get_email_addr' + '@' + self.email_dom
        org = 'o=%s' % (self.org_name)
        people = '%s=%s' % (self.container_attr, self.user_container)
        uid = '%s=%s' % (self.user_key, self.user_id)
        dn = '%s,%s,%s,%s' % (uid, people, org, self.base_dn)
        dn_info = {self.smtp_address: [email_addr]}
        expected_result = [(dn, dn_info)]        
        addr = SpokeEmailAddress(self.org_name, self.user_id)
        addr.create(email_addr)
        result = addr.get(email_addr)['data']
        self.assertEqual(result, expected_result)

    def test_get_all_email_address(self):
        """Retrieve all email addresss; return an email address object."""
        email_addr = 'test_get_email_addr' + '@' + self.email_dom
        email_addr2 = 'test_get_all_email_addr' + '@' + self.email_dom
        org = 'o=%s' % (self.org_name)
        people = '%s=%s' % (self.container_attr, self.user_container)
        uid = '%s=%s' % (self.user_key, self.user_id)
        dn = '%s,%s,%s,%s' % (uid, people, org, self.base_dn)
        dn_info = {self.smtp_address: [email_addr, email_addr2]}
        expected_result = [(dn, dn_info)]        
        addr = SpokeEmailAddress(self.org_name, self.user_id)
        addr.create(email_addr)
        addr.create(email_addr2)
        result = addr.get()['data']
        self.assertEqual(result, expected_result)
        
    def test_get_missing_email_address(self):
        """Retrieve a missing email address; return empty results object."""
        addr = SpokeEmailAddress(self.org_name, self.user_id)
        email_addr = 'missing@' + self.email_dom
        result = addr.get(email_addr)['data']
        expected_result = []
        self.assertEqual(result, expected_result)

    def test_delete_email_address(self):
        """Delete an email address; return True."""
        email_addr = 'delete@' + self.email_dom
        addr = SpokeEmailAddress(self.org_name, self.user_id)
        addr.create(email_addr)
        self.assertTrue(addr.delete(email_addr))
        
    def test_delete_missing_email_address(self):
        """Delete a missing email address; raise NotFound."""
        email_addr = 'deletemissing@' + self.email_dom
        addr = SpokeEmailAddress(self.org_name, self.user_id)
        self.assertRaises(error.NotFound, addr.delete, email_addr)
        
    def test_invalid_email_address_input(self):
        """Input invalid email address; raise InputError."""
        email_addr = '*@domain.loc'
        addr = SpokeEmailAddress(self.org_name, self.user_id)
        self.assertRaises(error.InputError, addr.get, email_addr)
 
# Email domain tests.
       
    def test_create_email_domain(self):
        """Create email domain; return results object."""
        email_dom = 'create.domain.loc'
        org = 'o=%s' % (self.org_name)
        dn = '%s,%s' % (org, self.base_dn)
        dn_info = {self.smtp_domain: [self.email_dom, email_dom]}
        expected_result = [(dn, dn_info)]
        domain = SpokeEmailDomain(self.org_name)
        result = domain.create(email_dom)['data']
        self.assertEqual(result, expected_result)
        
    def test_create_email_domain_twice(self):
        """Create email domain twice; raise AlreadyExists."""
        email_dom = 'twins.domain.loc'
        domain = SpokeEmailDomain(self.org_name)
        domain.create(email_dom)
        self.assertRaises(error.AlreadyExists, domain.create, email_dom)
        domain.delete(email_dom)
        
    def test_instantiate_email_domain_with_missing_org(self):
        """Instantiate an email domain with no org; raise NotFound."""
        org_name = 'SpokeMissingOrg'
        self.assertRaises(error.NotFound, SpokeEmailDomain, org_name)
        
    def test_get_email_domain(self):
        """Retrieve an email domain; return a domain object."""
        org = 'o=%s' % (self.org_name)
        dn = '%s,%s' % (org, self.base_dn)
        dn_info = {'aenetPostfixDomain': [self.email_dom]}
        expected_result = [(dn, dn_info)]        
        domain = SpokeEmailDomain(self.org_name)
        result = domain.get(self.email_dom)['data']
        self.assertEqual(result, expected_result)
        
    def test_get_all_email_domains(self):
        """Retrieve all email domain; return a domain object."""
        email_dom2 = 'testgetall.com'
        org = 'o=%s' % (self.org_name)
        dn = '%s,%s' % (org, self.base_dn)
        dn_info = {'aenetPostfixDomain': [self.email_dom, email_dom2]}
        expected_result = [(dn, dn_info)]        
        domain = SpokeEmailDomain(self.org_name)
        domain.create(email_dom2)
        result = domain.get()['data']
        self.assertEqual(result, expected_result)
        
    def test_get_missing_email_domain(self):
        """Retrieve a missing email domain; return empty results object."""
        domain = SpokeEmailDomain(self.org_name)
        email_dom = 'missing.domain.loc'
        result = domain.get(email_dom)['data']
        expected_result = []
        self.assertEqual(result, expected_result)
        
    def test_delete_email_domain(self):
        """Delete an email domain; return True."""
        email_dom = 'delete.domain.loc'
        domain = SpokeEmailDomain(self.org_name)
        domain.create(email_dom)
        self.assertTrue(domain.delete(email_dom))
        
    def test_delete_missing_email_domain(self):
        """Delete a missing email domain; raise NotFound."""
        email_dom = 'missing.domain.loc'
        domain = SpokeEmailDomain(self.org_name)
        self.assertRaises(error.NotFound, domain.delete, email_dom)
        
    def test_invalid_email_domain_input(self):
        """Input invalid domain name; raise InputError."""
        email_dom = '*.domain.loc'
        domain = SpokeEmailDomain(self.org_name)
        self.assertRaises(error.InputError, domain.create, email_dom)
