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
        self.run_id=6738
        
    def _validate_target(self, target):
        target = common.validate_filename(target)
        target_full_path = self.tftp_dir + target
        if not os.path.isfile(target_full_path):
            msg = 'Target %s does not exist' % target
            raise error.NotFound, msg
        return target
    
    def create(self, mac, target):
        """Creates a symlink mac --> config"""
        mac = common.validate_mac(mac)
        mac = string.replace(mac, ":", "-") #Format for use on tftp filesystem
        target = self._validate_target(target)
        config = target
        config_file = open(config)                
        dst = self.tftp_dir + self.tftp_prefix + mac
        #Check that at least one line has kernel arguments
        for line in config_file:
            if line.contains('append'):
                kernel_arg_lines += 1
        if kernel_arg_lines < 1:
            msg = "No kernel arguments in specified config. Should be more than one line starting append."
            raise error.InputError, msg
        #Check that nothing exists at that mac location before trying to make a file                
        if not os.path.lexists(dst):
            mac_file = open(dst, w)
                #Loop file adding run_id at correct line
                for line in config_file:
                    if line.contains('append'):
                        mac_file.write( line.append(" run_id=" + str(run_id)) )
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
                mac_file = os.path.basename(itempath)
                mac_file = mac_file[3:]
                if common.validate_mac(mac_file) && os.path.isfile(item_path):
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
            self.log.debug('Searching for target for mac link %s' % mac_link)
            #check if the symlink exists for that mac and return target
            if not os.path.islink(mac_link):
                result = common.process_results(data, self.type)
                self.log.debug('Result: %s' % result)
                return result
            else:
                item = {}
                target = os.path.basename(os.path.realpath(mac_link))
                item[mac_link_name] = [target]
        elif target is not None and mac is None:
            target = self._validate_target(target)
            # We're looking for all mac address associated with the target file
            target = common.validate_filename(target)
            self.log.debug('Searching for links to target %s' % target)          
            link_list = os.listdir(self.tftp_dir)
            #count = 0
            mac_list = []
            for item in link_list:
                item_path = self.tftp_dir + item
                #this regex checks for the mac address with 01 on beginning
                pattern = re.compile('^([0-9a-fA-F]{2}[:\-]){6}[0-9a-fA-F]{2}$')
                valid_mac = pattern.match(item)
                #if the item is a symlink and a long mac addr strip the 01
                #and print which config it points to.
                if (os.path.islink(item_path)) and (valid_mac):
                    #mac = item[3:]
                    config = os.path.basename(os.path.realpath(item_path))
                    #check that this association points to the target we want
                    if (config == target):
                        mac_list.append(item)
                        #count += 1          
            if len(mac_list) == 0:
                msg = "Target %s has no associated MACs" % target
                self.log.debug(msg)
                result = common.process_results(data, self.type)
                self.log.debug('Result: %s' % result)
                return result
            #else:
            item = {}
            item[target] = mac_list  
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
