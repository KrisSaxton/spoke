"""Tests Spoke logger.py module."""
# core modules
import os
import unittest
# own modules
import spoke.lib.config as config
import spoke.lib.logger as logger

class SpokeLoggerTest(unittest.TestCase):
    """A Class for testing the Spoke logger.py module."""

    def __init__(self, methodName):
        """Define test config data, write, parse and return config object."""
        unittest.TestCase.__init__(self, methodName)
        self.test_log_filename = '/tmp/spoke-test.log'
        test_config = '''
[LOGGING]
log_filename = /tmp/spoke-test.log
log_level = debug
'''
        self.test_config_filename = '/tmp/spoke_test_logger.conf'
        test_config_file = open(self.test_config_filename, 'w')
        test_config_file.write(test_config)
        test_config_file.close()
        self.config = config.setup(self.test_config_filename)
      
    def setUP(self): pass
         
    def tearDown(self): pass
    
    def test_logging_no_config(self):
        """Instantiate without config file; log to the console."""
        test_phrase = 'This is a Spoke logger console test'
        config.gConfig = None
        log = logger.setup(self.__module__)
        log.critical(test_phrase)

    def test_write_read_console_message(self):
        """Write a message to the console; read it back."""
        """How the hell do I read from the console without spawning a child?"""
        pass
        
    def test_write_read_log_message(self):
        """Write message to log file; read it back."""
        logger.gLog = None
        self.config = config.setup(self.test_config_filename)
        self.log = logger.setup(self.__module__)
        test_phrase = 'This is a Spoke logger test'
        self.log.critical(test_phrase)
        lf = open(self.test_log_filename, 'r')
        lines = lf.readlines()
        lf.close()
        res = lines[-1].find(test_phrase)
        self.assert_(res > -1)

    def test_zzz_finish(self):
        """Remove test config and log file"""
        os.remove(self.test_config_filename)
        os.remove(self.test_log_filename)

if __name__ == "__main__":
    unittest.main()
