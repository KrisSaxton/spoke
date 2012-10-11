"""TFTP management module.

Classes:
SpokeTFTP - Creation/deletion/retrieval of TFTP links.
Exceptions:
NotFound - raised on failure to find an object when one is expected.
AlreadyExists -raised on attempts to create an object when one already exists.
InputError - raised on invalid input.
SearchError - raised to indicate unwanted search results were returned.
"""

# core modules
import re
import os
import string

# own modules
import spoke.lib.error as error
import spoke.lib.common as common
import spoke.lib.config as config
import spoke.lib.logger as logger


class SpokeTFTP:


    
    def __init__(self, tftp_root=None):
        self.config = config.setup()
        self.log = logger.setup(__name__)
        self.type = 'TFTP link'
        if not tftp_root:
            tftp_root = self.config.get('TFTP', 'tftp_root')
        self.tftp_root = common.validate_filename(tftp_root)
        self.tftp_conf_dir = self.config.get('TFTP', 'tftp_conf_dir', 'pxelinux.cfg')
        self.tftp_mac_prefix = self.config.get('TFTP', 'tftp_mac_prefix', '01')
        # Add the delimiter (makes life easier when concating strings
        self.tftp_prefix = self.tftp_mac_prefix + '-' 
        #check file exists in the TFTP directory
        self.tftp_dir = self.tftp_root + "/" + self.tftp_conf_dir + "/"
        if not os.path.isdir(self.tftp_dir):
            msg = "TFTP config directory %s not found" % self.tftp_dir
            raise error.NotFound, msg
        
    def _validate_target(self, target):
        target = common.validate_filename(target)
        target_full_path = self.tftp_dir + target
        if not os.path.isfile(target_full_path):
            msg = 'Target %s does not exist' % target
            raise error.NotFound, msg
        return target
    
    def create(self, mac, target, run_id="none"):
        """Creates a symlink mac --> config"""
        mac = common.validate_mac(mac)
        mac = string.replace(mac, ":", "-") #Format for use on tftp filesystem
        target = self._validate_target(target)
        config = self.tftp_dir + target
        config_file = open(config)                
        dst = self.tftp_dir + self.tftp_prefix + mac
        #Check that at least one line has kernel arguments
        kernel_arg_lines = 0
        for line in config_file:
            if 'append' in line:
                kernel_arg_lines += 1
        if kernel_arg_lines < 1:
            msg = "No kernel arguments in specified config. Should be more than one line starting append."
            raise error.InputError, msg
        config_file.close
        config_file = open(config)
        #Check that nothing exists at that mac location before trying to make a file                
        if not os.path.lexists(dst):
            mac_file = open(dst, 'w')
            #Loop file adding run_id at correct line
            for line in config_file:
                if 'append' in line:
                    line = line.rstrip('\n')
                    mac_file.write( line + " run_id=" + str(run_id) + "\n")
                else:
                    mac_file.write(line)
            mac_file.close
        else:
            msg = "Link for mac %s already exists, can't create" % mac
            raise error.AlreadyExists, msg
        result = self.search(mac)
        if result['exit_code'] == 0 and result['count'] == 1:
            result['msg'] = "Created %s:" % result['type']
            return result
        else:
            msg = 'Create operation returned OK, but unable to find object'
            raise error.NotFound(msg)
        return result
              
    def search(self, mac=None, target=None):
        data = []
        if mac is None and target is None:
        # Give me all targets and all their links
            #read the file system
            self.log.debug('Searching for all targets and mac under %s' % \
                           self.tftp_dir)
            file_list = os.listdir(self.tftp_dir)
            if len(file_list) == 0:
                result = common.process_results(data, self.type)
                self.log.debug('Result: %s' % result)
                return result
            item = {}
            for file in file_list:
                item_path = self.tftp_dir + file
                mac_file = os.path.basename(item_path)
                mac_file = mac_file[3:]
                pattern = re.compile('^([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}$')
                valid_mac = pattern.match(mac_file)
                if valid_mac and os.path.isfile(item_path):
                    macs = mac_file
                    try:
                        item[macs]
                    except KeyError:
                        item[macs] = [] # Initialise dict if not exist
                    item[macs].append(file)
                elif os.path.isfile(item_path):
                    try:
                        item[file]
                    except KeyError:
                        item[file] = [] # Initialise dict if not exist
                else:
                    self.log.debug('Unknown file type %s, skipping' % file)
        elif mac is not None and target is None:
            # We're looking for a mac address
            mac = common.validate_mac(mac)
            mac_file = string.replace(mac, ":", "-") #Format for use on filesystem
            mac_link_name = self.tftp_prefix + mac_file           
            mac_link = self.tftp_dir + mac_link_name

            if not os.path.isfile(mac_link):
                result = common.process_results(data, self.type)
                self.log.debug('Result: %s' % result)
                return result
            else:
                item = {}
                item[mac_link_name] = ["Present"]
        elif target is not None and mac is None:
            item = {}
            #Now we just want to check if config exists, no longer maintaining list of links
            target = common.validate_filename(target)
            target = self._validate_target(target)

            item[target] = "Found"
        else:
            msg = "please specify nothing, mac or target (not mac and target)."
            raise error.InputError, msg
        data.append(item)
        result = common.process_results(data, self.type)
        self.log.debug('Result: %s' % result)
        return result
            
    def delete(self, mac):
        """Deletes file self.tftp_root/pxelinux.cfg/01-<mac>"""
        mac = common.validate_mac(mac)
        mac_file = string.replace(mac, ":", "-") #Format for use on tftp filesystem
        dst = self.tftp_dir + self.tftp_prefix + mac_file
        #Make sure the file exists before deleting
        if os.path.lexists(dst):
            self.log.debug('Deleting link to mac %s' % mac)
            os.unlink(dst)
        else:
            msg = "Link to mac %s doesn't exist, can't delete" % mac
            raise error.NotFound, msg
        result = self.search(mac)
        if result['exit_code'] == 3 and result['count'] == 0:
            result['msg'] = "Deleted %s:" % result['type']
            return result
        else:
            msg = 'Delete operation returned OK, but object still there?'
            raise error.SearchError(msg)
