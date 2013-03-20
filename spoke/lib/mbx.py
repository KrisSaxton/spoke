"""Mailbox management module

Classes:
SpokeMbx - Easy creation/deletion/retrieval of mailboxes.

Exceptions:
InputError - raised on invalid input.
SearchError - raised to indicate unwanted search results were returned.
SpokeIMAPError - Raised if the IMAP server reports a failure.

TODO raises exceptions for mailbox already exists or not found.
"""
# core modules
import re
import logging
import imaplib
import traceback

# own modules
import spoke.lib.error as error
import spoke.lib.config as config

class SpokeMbx():
    
    """Provide CRUD methods to Cyrus IMAP mailboxes"""

    def __init__(self):
        """Get config, setup logging and cyrus connection."""
        self.config = config.setup()
        self.log = logging.getLogger(__name__)
        server = self.config.get('IMAP', 'server')
        port = int(self.config.get('IMAP', 'port', 143))
        self.user = self.config.get('IMAP', 'user')
        password = self.config.get('IMAP', 'password')
        self.mailbox_group = self.config.get('IMAP', 'mailbox_group', 'user')
        self.sep = '/'
        try:
            self.imap = imaplib.IMAP4(server, port)
        except imaplib.socket.error:
            trace = traceback.format_exec()
            msg = '%s: %s' % ('IMAP connection error')
            raise error.SpokeIMAPError(msg, trace)
        self.imap.login(self.user, password)
    
    def _validate_mailbox_name(self, mailbox_name):
        """Ensure input is a valid email address format."""
        mailbox_name = mailbox_name.lower()
        pattern = re.compile(r"^[-a-z0-9_.]+@[-a-z0-9]+\.+[a-z]{2,6}")
        valid_mailbox = pattern.match(mailbox_name)
        if not valid_mailbox:            
            msg = '%s is not a valid mailbox name' % mailbox_name
            raise error.InputError(msg)
        return mailbox_name

    def get(self, mailbox_name, unique=False):
        """Find a mailbox; return result (list of tuples)."""
        mailbox_name = self._validate_mailbox_name(mailbox_name)
        mailbox = self.sep.join([self.mailbox_group, mailbox_name])
        self.log.debug('Searching for mailbox %s' % mailbox)
        res, data = self.imap.list(pattern=mailbox)
        self.log.debug(data)
        if res != 'OK':
            raise error.SpokeIMAPError(data)
        if data == [None]:
            self.log.debug('Mailbox %s not found' % mailbox)
            return []
        if unique is True and len(data) > 1:
            self.log.error('Multiple results when uniqueness requested.')
            raise error.SearchUniqueError(data)
        pattern = re.compile\
            (r'\((?P<flags>.*)\) "(?P<sep>.*)" ".*/(?P<mbx>.*)"')
        result = []
        for line in data:
            flags, sep, mbx = pattern.match(line).groups()
            result.append((mbx, sep, flags))
        self.log.debug(result)
        return result
    
    def create(self, mailbox_name):
        """Create a mailbox; return True."""
        mailbox_name = self._validate_mailbox_name(mailbox_name)
        mailbox = self.sep.join([self.mailbox_group, mailbox_name])
        self.log.debug('Creating mailbox %s' % mailbox)
        res, msg = self.imap.create(mailbox)
        msg = msg[0]
        if res != 'OK':
            raise error.SpokeIMAPError(msg)
        self.imap.setacl(mailbox, self.user, 'c') # Grant admin user delete
        self.log.debug(msg)
        return True
        
    def delete(self, mailbox_name, confirm=False):
        """Delete a mailbox; return True."""
        mailbox_name = self._validate_mailbox_name(mailbox_name)
        mailbox = self.sep.join([self.mailbox_group, mailbox_name])
        self.log.debug('Deleting mailbox %s' % mailbox)
        res, msg = self.imap.delete(mailbox)
        msg = msg[0]
        if res != 'OK':
            raise error.SpokeIMAPError(msg)
        self.log.debug(msg)
        return True
