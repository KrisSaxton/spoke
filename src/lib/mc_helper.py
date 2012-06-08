"""Provides marshalling and file handling for mcollective agent integration.

Classes:
SpokeLDAP - extends ldap with several convenience classes.

Exceptions:
ConfigError - raised on invalid configuration data.
SpokeError - raised when action fails for unknown reason.
JSONError - raised on failed JSON actions.
"""

# core modules
import os
import sys
import error
import traceback

try:
    import simplejson as json
except:
    msg = 'Failed to import JSON'
    raise error.SpokeError(msg)

class MCollectiveAction(object):

    _environment_variables = [ 'MCOLLECTIVE_REQUEST_FILE',
                               'MCOLLECTIVE_REPLY_FILE' ]

    def __init__(self):
        self._info  = sys.__stdout__
        self._error = sys.__stderr__ 

        for entry in '_reply', '_request':
            self.__dict__[entry] = {}

        self._arguments = sys.argv[1:]

        if len(self._arguments) < 2:
            try:
                for variable in self._environment_variables:
                    self._arguments.append(os.environ[variable])
            except KeyError:
                raise error.ConfigError("Environment variable `%s' "
                                                 "is not set." % variable)

        self._request_file, self._reply_file = self._arguments

        if len(self._request_file) == 0 or len(self._reply_file) == 0:
            raise error.NotFound("Both request and reply files have to be set.")

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            self.__dict__['_reply'][name] = value

    def __getattr__(self, name):
        if name.startswith('_'):
            return self.__dict__.get(name, None)
        else:
            return self.__dict__['_reply'].get(name, None)

    def __del__(self):
        if self._reply:
            try:
                file = open(self._reply_file, 'w')
                json.dump(self._reply, file)
                file.close()
            except IOError:
                trace = traceback.format_exc()
                msg = "Unable to open reply file: %s" % self._reply_file
                raise error.SpokeError(msg, trace)

    def info(self, message):
        print >> self._info, message
        self._info.flush()

    def error(self, message):
        print >> self._error, message
        self._error.flush()

    def fail(self, message, exit_code=1):
        self.error(message)
        sys.exit(exit_code)

    def reply(self):
        return self._reply

    def request(self):
        if self._request:
            return self._request
        else:
            try:
                file = open(self._request_file, 'r')
                self._request = json.load(file)
                file.close()
            except IOError:
                trace = traceback.format_exc()
                msg = "Unable to open request file: %s" % self._request_file
                raise error.SpokeError(msg, trace)
            except json.JSONDecodeError:
                trace = traceback.format_exc()
                msg = "An error parsing JSON data in file :%s" % self._request_file
                raise error.JSONError(msg, trace)
                file.close()

            return self._request