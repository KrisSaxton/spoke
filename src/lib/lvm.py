"""LVM management module.

Classes:
SpokeLVM - Creation/deletion/modification/retrieval of logical volume details
Exceptions:
NotFound - raised on failure to find an object when one is expected.
AlreadyExists -raised on attempts to create an object when one already exists.
InputError - raised on invalid input.
ConfigError - raised on invalid configuration data.
SearchError - raised to indicate unwanted search results were returned.
SpokeError - raised when action fails for unknown reason.
InsufficientResource - raised on a lack of a required resource.
LVMError - raised on failed LVM actions.
"""

# core modules
import re
import traceback
import subprocess

# own modules
import error
import config
import common
import logger

class SpokeLVM:
    
    def __init__(self, vg_name):
        """Get config, setup logging."""
        self.config = config.setup()
        self.log = logger.setup(__name__)
        self.vg_name = common.is_shell_safe(vg_name)
        try:
            self.lv_units = self.config.get('LVM', 'lv_units')
        except:
            self.lv_units = 'g'
    
    def create(self, lv_name, lv_size):
        """Create logical volume; return True"""
        lv_size = str(lv_size) + self.lv_units
        lv_name = common.validate_hostname(lv_name) # LV names are always hostnames
        lv_size = common.validate_storage_format(lv_size)
        
        args = ['lvcreate', '-n', lv_name, '-L', lv_size, self.vg_name]
        str_args = " ".join(args)
        msg = "Running " + str_args
        self.log.debug(msg)
        try:
            result = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        except Exception:
            msg = 'Running command %s failed' % str_args
            trace = traceback.format_exec()
            raise error.SpokeError(msg, trace)

        data = result.communicate()
        stdout = data[0]
        stderr = data[1]
        msg = "Command stdout was: %s, stderr was: %s" % (stdout, stderr)
        self.log.debug(msg)
        
        # Errors we know about
        if "Volume group \"%s\" not found" % self.vg_name in stderr:
            msg = "volume group '%s' was not found." % self.vg_name 
            raise error.NotFound(msg)
        elif "Insufficient free extents" in stderr:
            msg = "Not enough free space to create LV"
            raise error.InsufficientResource(msg)
        elif "Logical volume \"%s\" already exists in volume group \"%s\"" % (lv_name, self.vg_name) in stderr:
            msg = "Logical volume '%s' already exists in volume group '%s'" % (lv_name, self.vg_name)
            raise error.AlreadyExists(msg)
        # Catch unexpected errors
        if result.returncode != 0:
            msg = "Create command returned non-zero: %s stdout was: %s, stderr was: %s" % \
                                                        (result.returncode, stdout, stderr)
            raise error.LVMError(msg)

        result = self.get(lv_name)
        if result['exit_code'] == 0 and result['count'] == 1:
            result['msg'] = "Created %s:" % result['type']
            return result
        else:
            msg = 'Create operation returned OK, but unable to find object'
            raise error.NotFound(msg)
        return result
    
    def get(self, lv_name=None):
        """Get logical volume; return list of volume attributes."""
        if lv_name is not None:
            lv_name = common.validate_hostname(lv_name) # LV names are always hostnames
            args = ['lvs', '--noheadings', '--units', self.lv_units, '-o', 'lv_name,lv_size', '--separator', ':', '/dev/%s/%s' % (self.vg_name, lv_name)]
        else:
            args = ['lvs', '--noheadings', '--units', self.lv_units, '-o', 'lv_name,lv_size', '--separator', ':', '/dev/%s' % self.vg_name]
        str_args = " ".join(args)
        msg = "Running " + str_args
        self.log.debug(msg)
        try:
            result = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        except Exception, e:
            msg = 'Running command %s failed' % str_args
            trace = traceback.format_exec()
            raise error.SpokeError(msg, trace)
            
        out = result.communicate()
        (stdout, stderr) = (out[0], out[1])
        msg = "Command stdout was: %s, stderr was: %s" % (stdout, stderr)
        self.log.debug(msg)

        data = []
        # Errors we know about
        if "Volume group \"%s\" not found" % self.vg_name in stderr:
            msg = "Volume group '%s' was not found." % self.vg_name 
            raise error.NotFound(msg)
        elif "logical volume(s) not found" in stderr:
            result = common.process_results(data)
            self.log.debug('Result: %s' % result)
            return result
        elif stderr == "" and stdout == "":
            result = common.process_results(data)
            self.log.debug('Result: %s' % result)
            return result
        # Catch unexpected errors
        if result.returncode != 0:
            msg = "Search command returned non-zero: %s stdout was: %s, stderr was: %s" % \
                                                        (result.returncode, stdout, stderr)
            raise error.LVMError(msg)
        output = stdout.strip()
        output = re.compile('\n').split(output)
        for item in output:
            item = item.strip()
            dic = {}
            name, size = item.split(':')
            dic['lv_size'] = size
            dic['lv_name'] = name
            data.append(dic)
        result = common.process_results(data)
        self.log.debug('Result: %s' % result)
        return result
        
    def delete(self, lv_name):
        """Delete logical volume; return True."""
        lv_name = common.validate_hostname(lv_name) # LV names are always hostnames

        args = ['lvremove', '-f', '%s/%s' % (self.vg_name, lv_name)]
        str_args = " ".join(args)
        msg = "Running " + str_args
        self.log.debug(msg)
        try:
            result = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        except Exception, e:
            msg = 'Running command %s failed' % str_args
            trace = traceback.format_exec()
            raise error.SpokeError(msg, trace)

        data = result.communicate()
        stdout = data[0]
        stderr = data[1]
        msg = "Command stdout was: %s, stderr was: %s" % (stdout, stderr)
        self.log.debug(msg)

        if "Volume group \"%s\" not found" % self.vg_name in stderr:
            msg = "volume group '%s' was not found." % self.vg_name 
            raise error.NotFound(msg)
        elif "logical volume(s) not found" in stderr:
            msg = "logical volume '%s' not found." % lv_name
            raise error.NotFound(msg)
        
        # Catch non-specific errors
        if result.returncode != 0:
            msg = "Delete command returned non-zero: %s stdout was: %s, stderr was: %s" % \
                                                        (result.returncode, stdout, stderr)
            raise error.LVMError(msg)

        result = self.get(lv_name)
        if result['exit_code'] == 3 and result['count'] == 0:
            result['msg'] = "Deleted %s:" % result['type']
            return result
        else:
            msg = 'Delete operation returned OK, but object still there?'
            raise error.SearchError(msg)
