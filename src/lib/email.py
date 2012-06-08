"""Email account management module.

Classes:
SpokeEmailAccount - Creation/deletion/retrieval of email account objects.
SpokeEmailAddress - Creation/deletion/retrieval of email address objects.
SpokeEmailDomain - Creation/deletion/retrieval of email domain objects.

Exceptions:.
NotFound - raised on failure to find an object when one is expected.
AlreadyExists -raised on attempts to create an object when one already exists.

ldap.MOD_DELETE = 1
ldap.MOD_ADD = 0

TODO: With a primary domain attr on the org, only the uid would be needed.
"""

# own modules
import common
import error
import config
import logger
from directory import SpokeLDAP
from user import SpokeUser
from org import SpokeOrg

class SpokeEmail(SpokeLDAP):
    
    """Superclass for email objects."""

    def __init__(self, org_name, user_id):
        """Get config, setup logging and LDAP connection."""   
        SpokeLDAP.__init__(self)     
        self.config = config.setup()
        self.log = logger.setup(__name__)
        self.base_dn = self.config.get('LDAP', 'basedn')
        self.search_scope = 0 #ldap.SCOPE_BASE
        self.org_attr = self.config.get('ATTR_MAP', 'org_attr', 'o')
        self.org_def_children = self.config.get('ATTR_MAP', \
                                'org_def_children', 'people,groups,dns,hosts')
        self.org_children = self.org_def_children.split(',')
        self.user_login = self.config.get('ATTR_MAP', 'user_login', 'aenetAccountLoginName')
        self.user_id = user_id
        self.user = self._get_user(org_name, self.user_id)
        self.user_dn = self.user['data'][0].__getitem__(0)
        self.user_attrs = self.user['data'][0].__getitem__(1)
        self.user_classes = self.user_attrs['objectClass']
        self.imap_class = self.config.get('ATTR_MAP', 'imap_class', 'aenetCyrus')
        self.imap_enable = self.config.get('ATTR_MAP', 'imap_enable', 'aenetCyrusEnabled')
        self.imap_mailbox = self.config.get('ATTR_MAP', 'imap_mailbox', 'aenetCyrusMailboxName')
        self.imap_domain = self.config.get('ATTR_MAP', 'imap_domain', 'aenetCyrusMailboxDomain')
        self.imap_partition = self.config.get('ATTR_MAP', 'imap_partition', 'aenetCyrusMailboxPartition')
        self.imap_partition_def = self.config.get('ATTR_MAP', \
                                    'imap_partition_def', 'partition-default')
        self.smtp_class = self.config.get('ATTR_MAP', 'smtp_class', 'aenetPostfix')
        self.smtp_address = self.config.get('ATTR_MAP', 'smtp_address', 'aenetPostfixEmailAccept')
        self.smtp_destination = self.config.get('ATTR_MAP', \
                                'smtp_destination', 'aenetPostfixEmailDeliver')
        self.smtp_enable = self.config.get('ATTR_MAP', 'smtp_enable', 'aenetPostfixEnabled')
        self.smtp_pri_address = self.config.get('ATTR_MAP', \
                                'smtp_pri_address', 'aenetPostfixEmailAddress')
    
    def _convert_email_to_mailbox_format(self, email):
        """Derive a Cyrus mailbox name from an email address."""
        email_uid, imap_mbx_domain = email.split('@')
        imap_mbx_name = email_uid.replace('.', '^')
        return imap_mbx_name, imap_mbx_domain 
        
    def _get_user(self, org_name, user_id):
        """Retrieve a user object."""
        user = SpokeUser(org_name)
        result = user.get(user_id, unique=True)
        if result['data'] == []:
            msg = "Can't find user %s in org %s" % (user_id, org_name)
            raise error.NotFound(msg)          
        return result
    
    def _validate_input(self, entry):
        """Ensure input is a valid email account identifier."""
        entry = common.validate_email_address(entry)
        return entry

class SpokeEmailAccount(SpokeEmail):
    
    '''Provide CRUD methods to email account objects.'''
    
    def __init__(self, org_name, user_id):
        '''Specifiy email account attributes.'''
        SpokeEmail.__init__(self, org_name, user_id)
        self.retrieve_attr = [self.imap_enable, self.imap_mailbox,
                              self.imap_domain, self.imap_partition, 
                              self.imap_partition_def, self.smtp_destination,
                              self.smtp_enable, self.smtp_pri_address]
    
    def create(self, email_addr):
        """Create an email account; return a results object."""
        email_addr = self._validate_input(email_addr)
        imap_mbx_name, imap_mbx_domain =\
                             self._convert_email_to_mailbox_format(email_addr)
        dn = self.user_dn
        dn_info = []
        if not self.imap_class in self.user_classes:
            dn_info.append((0, 'objectClass', self.imap_class))
        if not self.smtp_class in self.user_classes:
            dn_info.append((0, 'objectClass', self.smtp_class))
        if not self.imap_mailbox in self.user_attrs:
            dn_info.append((0, self.imap_mailbox, imap_mbx_name))
        if not self.imap_domain in self.user_attrs:
            dn_info.append((0, self.imap_domain, imap_mbx_domain))
        if not self.imap_enable in self.user_attrs:
            dn_info.append((0, self.imap_enable, 'TRUE'))
        if not self.imap_partition in self.user_attrs:
            dn_info.append((0, self.imap_partition, 
                            self.imap_partition_def))
        if not self.smtp_destination in self.user_attrs:
            dn_info.append((0, self.smtp_destination, email_addr))
        if not self.smtp_enable in self.user_attrs:
            dn_info.append((0, self.smtp_enable, 'TRUE'))
        if not self.smtp_pri_address in self.user_attrs:
            dn_info.append((0, self.smtp_pri_address, email_addr))
        
        if dn_info == []:
            msg = 'Attribute dict empty, nothing to add for user %s.' % \
                                                                self.user_dn
            raise error.AlreadyExists(msg)
        self.log.debug('Adding email account %s to user %s ' %
                           (email_addr, self.user_id))
        result = self._create_object(dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result

    def get(self, email_addr):
        """Find an email account; return results object."""
        email_addr = self._validate_input(email_addr)
        imap_mbx_name, imap_mbx_domain =\
                             self._convert_email_to_mailbox_format(email_addr)
        filter = '%s=%s' % (self.imap_mailbox, imap_mbx_name)
        result = self._get_object(self.user_dn, self.search_scope, filter, 
                                  attr=self.retrieve_attr)
        self.log.debug('Result: %s' % result)
        return result
    
    def delete(self, email_addr):
        """Delete an email account; return a results object."""
        email_addr = self._validate_input(email_addr)
        imap_mbx_name, imap_mbx_domain =\
                             self._convert_email_to_mailbox_format(email_addr)
        
        dn_info = []
        if self.imap_class in self.user_classes:
            dn_info.append((1, 'objectClass', self.imap_class))
        if self.smtp_class in self.user_classes:
            dn_info.append((1, 'objectClass', self.smtp_class)) 
        if self.imap_mailbox in self.user_attrs:
            dn_info.append((1, self.imap_mailbox, None))
        if self.imap_domain in self.user_attrs:
            dn_info.append((1, self.imap_domain, None))
        if self.imap_enable in self.user_attrs:
            dn_info.append((1, self.imap_enable, None))
        if self.imap_partition in self.user_attrs:
            dn_info.append((1, self.imap_partition, None))
        if self.smtp_destination in self.user_attrs:
            dn_info.append((1, self.smtp_destination, None))
        if self.smtp_enable in self.user_attrs:
            dn_info.append((1, self.smtp_enable, None))
        if self.smtp_pri_address in self.user_attrs:
            dn_info.append((1, self.smtp_pri_address, None))
        if self.smtp_address in self.user_attrs:
            dn_info.append((1, self.smtp_address, None))
        
        if dn_info == []:
            msg = 'Attribute dict empty, nothing to delete.'
            raise error.NotFound(msg)
        self.log.debug('Deleting email account %s from user %s ' %
                           (email_addr, self.user_id))
        result = self._delete_object(self.user_dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result
    
class SpokeEmailAddress(SpokeEmail):
    
    '''Provide CRUD methods to email address objects.'''
    
    def __init__(self, org_name, user_id):
        '''Specifiy email address attributes.'''
        SpokeEmail.__init__(self, org_name, user_id)
        self.retrieve_attr = [self.smtp_address]
                   
    def create(self, email_addr):
        """Create an email address."""
        email_addr = self._validate_input(email_addr)
        dn = self.base_dn
        filter = '%s=%s' % (self.smtp_address, email_addr)
        # Global search
        result = self._get_object(dn, self.search_scope, filter, unique=True)
        if result['data'] != []:
            self.log.info('Email address %s already exists.' % email_addr)
            raise error.AlreadyExists(result)
        dn_info = [(0, self.smtp_address, email_addr)]
        self.log.debug('Adding email address %s to user %s ' %
                           (email_addr, self.user_id))
        result = self._create_object(self.user_dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result

    def get(self, email_addr=None):
        """Find an email address; return result list."""
        dn = self.user_dn
        if email_addr:
            email_addr = self._validate_input(email_addr)
            filter = '%s=%s' % (self.smtp_address, email_addr)
        else:
            filter = '%s=*' % self.smtp_address
        result = self._get_object(dn, self.search_scope, filter, 
                                  attr=self.retrieve_attr)
        self.log.debug('Result: %s' % result)
        return result
        
    def delete(self, email_addr):
        """Delete an email address."""
        email_addr = self._validate_input(email_addr)
        dn_info = [(1, self.smtp_address, email_addr)]                    
        self.log.debug('Deleting email address %s from user %s ' %
                           (email_addr, self.user_id))
        result = self._delete_object(self.user_dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result

class SpokeEmailDomain(SpokeLDAP):
    
    """Provide CRUD methods to email domain objects."""

    def __init__(self, org_name):
        """Get config, setup logging and LDAP connection."""
        SpokeLDAP.__init__(self)      
        self.config = config.setup()
        self.log = logger.setup(self.__module__)
        self.base_dn = self.config.get('LDAP', 'basedn')
        self.search_scope = 0 #ldap.SCOPE_BASE
        self.org_name = org_name
        self.org = self._get_org(self.org_name)
        self.org_dn = self.org['data'][0].__getitem__(0)
        self.org_attrs = self.org['data'][0].__getitem__(1)
        self.org_classes = self.org_attrs['objectClass']
        self.smtp_class = self.config.get('ATTR_MAP', 'smtp_class', 'aenetPostfix')
        self.smtp_domain = self.config.get('ATTR_MAP', 'smtp_domain', 'aenetPostfixDomain')
        self.retrieve_attr = [self.smtp_domain]
        
    def _get_org(self, org_name):
        """Retrieve our org object."""
        org = SpokeOrg()
        result = org.get(org_name)
        if result['data'] == []:
            msg = "Can't find org %s" % org_name
            raise error.NotFound(msg)          
        return result
            
    def create(self, email_dom):
        """Create an email domain."""
        email_dom = common.validate_domain(email_dom)
        dn = self.base_dn
        filter = '%s=%s' % (self.smtp_domain, email_dom)
        # Global search
        result = self._get_object(dn, self.search_scope, filter, unique=True)
        if result['data'] != []:
            self.log.info('Email domain %s already exists.' % email_dom)
            raise error.AlreadyExists(result)
        dn_info = []
        if not self.smtp_class in self.org_classes:
            dn_info.append((0, 'objectClass', self.smtp_class))
        dn_info.append((0, self.smtp_domain, email_dom))
        self.log.debug('Adding email domain %s to org %s ' %
                          (email_dom, self.org_name))
        result = self._create_object(self.org_dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result

    def get(self, email_dom=None):
        """Find an email domain; return result list."""
        if email_dom:
            email_dom = common.validate_domain(email_dom)
            filter = '%s=%s' % (self.smtp_domain, email_dom)
        else:
            filter = '%s=*' % self.smtp_domain 
        dn = self.org_dn
        result = self._get_object(dn, self.search_scope, filter, 
                                  attr=self.retrieve_attr)
        self.log.debug('Result: %s' % result)
        return result
      
    def delete(self, email_dom):
        """Delete an email domain."""
        filter = '%s=%s' % (self.smtp_domain, email_dom)
        dn_info = []
        #if self.smtp_domain in self.org_attrs:
        dn_info.append((1, self.smtp_domain, email_dom))           
        #if dn_info == []:
        #    self.log.debug('Attribute dict empty, nothing to delete.')
        #else:
        self.log.debug('Deleting email domain %s from org %s ' %
                          (email_dom, self.org_name))
        result = self._delete_object(self.org_dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result