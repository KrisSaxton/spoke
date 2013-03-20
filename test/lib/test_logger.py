"""Tests Spoke logger.py module."""
# core modules
import os
import unittest
# own modules
import spoke.lib.config as config
import spoke.lib.log as logger

class SpokeLoggerTest(unittest.TestCase):
    """A Class for testing the Spoke logger.py module."""

    def __init__(self, methodName):
        """Define test config data, write, parse and return config object."""
        unittest.TestCase.__init__(self, methodName)
        self.test_log_filename = '/tmp/spoke-test.log'
        self.log_filename = '/tmp/spoke-test.log'
        self.log_level = 'debug'
      
    def setUP(self): pass
         
    def tearDown(self): pass

    def test_write_read_console_message(self):
        """Write a message to the console; read it back."""
        """How the hell do I read from the console without spawning a child?"""
        pass
        
    def test_write_read_log_message(self):
        """Write message to log file; read it back."""
        logger.gLog = None
        self.log = logger.log_to_file(__name__, level=self.log_level, 
                                      log_file=self.log_filename)
        test_phrase = 'This is a Spoke logger test'
        self.log.debug(test_phrase)
        lf = open(self.test_log_filename, 'r')
        lines = lf.readlines()
        lf.close()
        res = lines[-1].find(test_phrase)
        self.assert_(res > -1)

    def test_zzz_finish(self):
        """Remove test config and log file"""
        os.remove(self.test_log_filename)

if __name__ == "__main__":
    unittest.main()
