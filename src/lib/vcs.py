"""VCS (Version Control System) management module.

Classes:
SpokeVCS - Creation/deletion/modification/retrieval of VCS account details.
Exceptions:
NotFound - raised on failure to find an object when one is expected.
AlreadyExists -raised on attempts to create an object when one already exists.
InputError - raised on invalid input.
"""

# own modules
import common
import error
import config
import logger
from directory import SpokeLDAP
from user import SpokeUser

# 3rd party modules
import ldap

class SpokeSVN(SpokeLDAP):
    
    """Provide CRUD methods to Subversion account objects."""

    def __init__(self, org_name, user_id):
        """Get config, setup logging and LDAP connection."""
        SpokeLDAP.__init__(self)
        self.config = config.setup()
        self.log = logger.setup(self.__module__)
        self.org_name = org_name
        self.user_id = user_id
        self.user = self._get_user(self.org_name, self.user_id)
        self.user_dn = self.user['data'][0].__getitem__(0)
        self.user_attrs = self.user['data'][0].__getitem__(1)
        self.user_classes = self.user_attrs['objectClass']
        self.svn_class = self.config.get('VCS', 'svn_class', 'aenetSubversion')
        self.svn_repo_attr = self.config.get('VCS', 'svn_repo_attr', 'aenetSubversionRepos')
        self.svn_enable_attr = self.config.get('VCS', 'svn_enable_attr', 'aenetSubversionEnabled')
        self.retrieve_attr = [self.svn_repo_attr, self.svn_enable_attr]
        self.filter = self.svn_repo_attr + '=*'
        self.search_scope = 2 # ldap.SUB
        
    def _get_user(self, org_name, user_id):
        """Retrieve a user object."""
        user = SpokeUser(org_name)
        result = user.get(user_id, unique=True)
        if result['data'] == []:
            msg = "Can't find user %s with org %s" % (user_id, org_name)
            self.log.error(msg)
            raise error.NotFound(msg)          
        return result
    
    def _validate_input(self, entry):
        """Ensure input is a shell-safe string."""
        #entry = common.validate_shell_safe(entry)
        return entry

    def create(self, repo):
        """Enable user access to a repository; return repository info."""
        repo = self._validate_input(repo)
        filter = '%s=%s' % (self.svn_repo_attr, repo)
        scope = self.search_scope
        dn = self.user_dn
        dn_info = []
        try: 
            if repo in self.user_attrs[self.svn_repo_attr]:
                msg = 'Repository %s already enabled for user %s.' % \
                                                        (repo, self.user_dn)
                raise error.AlreadyExists(msg)
            else:
                msg = 'Repository %s not found, creating...' % repo
                raise error.NotFound(msg)
        except (KeyError, error.NotFound):
            if not self.svn_class in self.user_classes:
                # This is our first repository, so add class and enable.
                dn_info.append((ldap.MOD_ADD, 'objectClass', self.svn_class))
                dn_info.append((ldap.MOD_ADD, self.svn_enable_attr, 'TRUE'))
            dn_info.append((ldap.MOD_ADD, self.svn_repo_attr, repo))
            self.log.debug('Adding %s to %s ' % (dn_info, dn))
            result = self._create_object(dn, dn_info)
            self.log.debug('Result: %s' % result)
        return result

    def get(self, repo=None):
        """Find a user's associated repositories; return repository info."""
        dn = self.user_dn
        if repo is None: # Return a list of all repos
            filter = '%s=*' % self.svn_repo_attr
        else:
            filter = '%s=%s' % (self.svn_repo_attr, repo)
        msg = 'Searching at %s with scope %s and filter %s' % \
            (dn, self.search_scope, filter)
        self.log.debug(msg)
        result = self._get_object(dn, self.search_scope, \
                                  filter, attr=self.retrieve_attr)
        self.log.debug('Result: %s' % result)
        return result
 
    def modify(self, enable):
        """Modify a user account's repository access; return True."""
        svn_info = self.get()['data']
        if svn_info == []:
            msg = 'Unable to modify repository access, no repositories found.'
            raise error.NotFound(msg)
        dn = svn_info[0].__getitem__(0)
        old_result = svn_info[0].__getitem__(1)
        old_attrs = {self.svn_enable_attr: old_result[self.svn_enable_attr]}
        if enable == True:
            new_attrs = {self.svn_enable_attr: 'TRUE'}
        elif enable == False:
            new_attrs = {self.svn_enable_attr: 'FALSE'}
        else:
            msg = 'enable can only be one of True or False'
            raise error.InputError(msg)
        self.log.debug('Modifying %s from %s to %s' % (dn, old_attrs, new_attrs))
        result = self._modify_attributes(dn, new_attrs, old_attrs)
        self.log.debug('Result: %s' % result)
        return result
            
    def delete(self, repo):
        """Disable user access to a repository; return True."""        
        repo = self._validate_input(repo)
        filter = '%s=%s' % (self.svn_repo_attr, repo)
        dn = self.user_dn
        dn_info = []
        if self.svn_repo_attr in self.user_attrs:
            dn_info.append((ldap.MOD_DELETE, self.svn_repo_attr, repo))
        if len(self.user_attrs) == 1:
            # This is the last repository, so we can delete the class also.
            dn_info.append((ldap.MOD_DELETE, 'objectClass', self.svn_class))
            
        if dn_info == []:
            msg = 'Repository not enabled for user %s.' % self.user_dn
            raise error.NotFound(msg)
    
        self.log.debug('Deleting %s from %s ' % (dn_info, dn))
        result = self._delete_object(dn, dn_info)
        self.log.debug('Result: %s' % result)
        return result
    