#!/usr/bin/env python
"""Provides application-wide logging

Classes:
SpokeLogger - Sets up logging, based on config file values or defaults.

Exceptions:
OSError - Raised when a filesystem action failes.
"""

# core modules
import os
import logging.handlers

# own modules
import error
import config

gLog = None

def setup(name, verbose=False, quiet=False):
    """Instantiate (once only) and return Log object"""
    global gLog
    if gLog is not None:
        gLog.name = 'spoke.' + name
        pass
    else:
        gLog = SpokeLogger().setup(name, verbose, quiet)
    return gLog

class SpokeLogger:
    
    """Configure logging behaviour, setup a logfile handler.
    Return a logging object."""

    def __init__(self):
        """Get logging config from config object or defaults."""
        try:
            self.config = config.setup()
        except error.ConfigError:
            self.config = None
        self.log_levels = {'debug': logging.DEBUG,
                     'info': logging.INFO,
                     'warning': logging.WARN,
                     'error': logging.ERROR,
                     'critical': logging.CRITICAL}
        self.log_filename = self.config.get('LOGGING', 'log_filename', '/tmp/spoke.log')
        self.log_level = self.config.get('LOGGING', 'log_level', 'info')
        max_size = 1024*1024*5 # 5MBytes
        self.log_max_size = self.config.get('LOGGING', 'log_max_size', max_size)
        self.log_keep = self.config.get('LOGGING', 'log_keep', 5)
        self.log_dir = os.path.split(self.log_filename)[0]
                
    def setup(self, name, verbose=False, quiet=False):
        """Setup logging and return a logging object"""
        log = logging.getLogger('spoke.%s' % name)
        #log.log_filename = self.log_filename #Convenience attr for calling code
        log.setLevel(logging.DEBUG) # Upper ceiling log level, don't change
        log_file_fmt = "%(asctime)s %(name)-16s %(levelname)-5s %(message)s"
        log_console_fmt = "%(message)s"
        # Start with logging to file
        if self.config is not None: # No file logging if no config found.
            if not os.path.exists(self.log_dir):
                try:
                    os.makedirs(os.path.split(self.log_filename)[0])
                except OSError, e:
                    raise e
            for handler in log.handlers:  
                if handler.__class__.__name__ == 'RotatingFileHandler':
                    return self.log # We don't want to add more than one handler
            log_formatter = logging.Formatter(log_file_fmt)
            log_handler = logging.handlers.RotatingFileHandler(self.log_filename,
                                                   maxBytes=self.log_max_size,
                                                   backupCount=self.log_keep)
            log_handler.setLevel(self.log_levels.get(self.log_level, \
                                                     logging.INFO))
            log_handler.setFormatter(log_formatter)
            log.addHandler(log_handler)
        # Log to console if called by a command line wrapper (main) or 
        # if called by unit test (no config).
        if name == 'main' or self.config is None:
            for handler in log.handlers:
                if handler.__class__.__name__ == 'StreamHandler':
                    return log # We don't want to add more than one handler
            console_formatter = logging.Formatter(log_console_fmt)
            console_handler = logging.StreamHandler()
            if verbose:
                console_handler.setLevel(logging.DEBUG)
            elif quiet:
                console_handler.setLevel(logging.CRITICAL)
            else:
                console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(console_formatter)
            log.addHandler(console_handler)       
        return log
    
if __name__ == '__main__':
    pass