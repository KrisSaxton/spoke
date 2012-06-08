#!/usr/bin/env python
"""Provides application-wide exception handling

Classes:
Error - Base class.

Exit Codes:
0 - OK
1 - Error. The action failed due to an unclassified error. SpokeError
2 - Invalid input. The action could not be completed due to invalid input data. InputError, ConfigError
3 - No results.  The action completed successfully but returned no data.
4 - Already exists.  The action could not be completed because the target object already exists. AlreadyExists
5 - Not found.  The action could not be completed because a dependent object is missing. NotFound
6 - OK, failed.  The action completed successfully but the validation failed. ValidationError
7 - 3rd party library error. The action could not be completed due to an error in a 3rd party library.
"""

class SpokeError(Exception):
    """Base class for exceptions in this module"""
    def __init__(self, msg, traceback=None):
        Exception.__init__(self, msg)
        self.exit_code = self._set_exit_code()
        self.msg = msg
        self.info = 'for more information on Spoke errors: visit http://<tbc>/'
        self.traceback = traceback
            
    def _set_exit_code(self):
        return 1

# InputError
class InputError(SpokeError):
    """Raised on invalid input."""
    def _set_exit_code(self):
        return 2
    
class ConfigError(InputError):
    """Raised when a configuration problem is found."""
    def _set_exit_code(self):
        return 2

# NotFound errors
class NotFound(SpokeError):
    """Raised when an operation fails to find an object when one is expected."""
    def _set_exit_code(self):
        return 3

# AlreadyExists error
class AlreadyExists(SpokeError):
    """Raised when an operation returns an object when none is expected."""
    def _set_exit_code(self):
        return 4

class SaveTheBabies(AlreadyExists):
    """Raised on attempts to delete a parent container that still has kids."""
    pass

# Search Errors
class SearchError(SpokeError):
    """Raised to indicate unwanted search results were returned."""
    pass

class SearchUniqueError(SpokeError):
    """Raised to indicate multiple results found when only one was wanted."""
    pass

# Validation Errors
class ValidationError(SpokeError):
    """Raised when an action completes successfully but validation fails."""
    def _set_exit_code(self):
        return 6

# 3rd party library errors
class Spoke3rdPartyError(SpokeError):
    """Raised on failures in dependent libraries."""
    def _set_exit_code(self):
        return 7
    
class SpokeLDAPError(Spoke3rdPartyError):
    """Raised on failures in LDAP operations"""
    pass

class RedisError(Spoke3rdPartyError):
    """Raised on failures in Redis operations"""
    pass

class LibvirtError(Spoke3rdPartyError):
    """Raised on failures in Libvirt operations"""
    pass

class JSONError(Spoke3rdPartyError):
    """Raised on failures in JSON operations."""
    pass

class SpokeIMAPError(Spoke3rdPartyError):
    """Raised on exceptions during IMAP operations."""
    pass

class LVMError(Spoke3rdPartyError):
    """Raised on errors with logical volume actions."""
    pass

# Other Errors
class IncrementError(SpokeError):
    """Raised on a failure to increment some resource"""
    pass

class InsufficientResource(SpokeError):
    """Raised on a lack of some resource"""
    pass

class AuthError(SpokeError):
    """Raised on failed authentication."""
    pass

class VMRunning(SpokeError):
    """Raised if an operation cannot be completed because a vm is running"""
    pass

class VMStopped(SpokeError):
    """Raised if an operation cannot be completed because a vm is not running"""
    pass

