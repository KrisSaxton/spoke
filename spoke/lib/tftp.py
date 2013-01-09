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
        self.type = 'TFTP config'
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
        
    def _validate_template(self, template):
        template = common.validate_filename(template)
        template_full_path = self.tftp_dir + template
        if not os.path.isfile(template_full_path):
            msg = 'Template %s does not exist' % template
            raise error.NotFound, msg
        if not '.template' in template:
            msg = 'Template %s must have .template extension' % template
            raise error.InputError, msg
        return template
    
    def create(self, mac, template, run_id=None):
        """Creates a config at mac using template"""
        mac = common.validate_mac(mac)
        if run_id is not None:
            run_id = common.is_shell_safe(run_id)
        mac = string.replace(mac, ":", "-") #Format for use on tftp filesystem
        template = self._validate_template(template)
        template_path = self.tftp_dir + template
        template_file = open(template_path)                
        dst = self.tftp_dir + self.tftp_prefix + mac
        #Check that at least one line has kernel arguments
        kernel_arg_lines = 0
        for line in template_file:
            if 'append' in line:
                kernel_arg_lines += 1
        if kernel_arg_lines < 1 and run_id is not None:
            msg = "No kernel arguments in specified template. Should be more than one line starting append."
            raise error.InputError, msg
        template_file.close
        template_file = open(template_path)
        #Check that nothing exists at that mac location before trying to make a file                
        if not os.path.lexists(dst):
            mac_file = open(dst, 'w')
            #Loop file adding run_id at correct line
            for line in template_file:
                if 'append' in line and run_id:
                    #remove the line break and add run_id at end of kernel args
                    line = line.rstrip('\n')
                    mac_file.write( line + " run_id=" + str(run_id) + "\n")
                else:
                    mac_file.write(line)
            mac_file.close
        else:
            msg = "Config for mac %s already exists, can't create" % mac
            raise error.AlreadyExists, msg
        result = self.search(mac)
        if result['exit_code'] == 0 and result['count'] == 1:
            result['msg'] = "Created %s:" % result['type']
            return result
        else:
            msg = 'Create operation returned OK, but unable to find object'
            raise error.NotFound(msg)
        return result
              
    def search(self, mac=None, template=None):
        data = []
        if mac is None and template is None:
            # Give me all macs and all templates
            #read the file system
            self.log.debug('Searching for all templates and macs under %s' % \
                           self.tftp_dir)
            file_list = os.listdir(self.tftp_dir)
            if len(file_list) == 0:
                result = common.process_results(data, self.type)
                self.log.debug('Result: %s' % result)
                return result
            item = {}
            for file in file_list:
                valid_template = False
                item_path = self.tftp_dir + file
                file_name = os.path.basename(item_path)
                if ".template" in file_name:
                    valid_template = True 
                file_name = file_name[3:]
                #use a regex to see if the file is a mac config
                pattern = re.compile('^([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}$')
                valid_mac = pattern.match(file_name)
                #if it's a mac add to list of macs
                if valid_mac and os.path.isfile(item_path):
                    macs = file_name
                    try:
                        item["configs"]
                    except KeyError:
                        item["configs"] = [] # Initialise dict if not exist
                    item["configs"].append(macs)
                elif valid_template and os.path.isfile(item_path):
                    try:
                        item["templates"]
                    except KeyError:
                        item["templates"] = [] # Initialise dict if not exist
                    item["templates"].append(file)
                else:
                    self.log.debug('Unknown file type %s, skipping' % file)
        elif mac is not None and template is None:
            # We're looking for a mac address
            mac = common.validate_mac(mac)
            mac_file = string.replace(mac, ":", "-") #Format for use on filesystem
            mac_file_name = self.tftp_prefix + mac_file           
            mac_link = self.tftp_dir + mac_file_name

            if not os.path.isfile(mac_link):
                result = common.process_results(data, self.type)
                self.log.debug('Result: %s' % result)
                return result
            else:
                item = [mac_file_name]
                #item[mac_file_name] = "Found"
        elif template is not None and mac is None:

            #Now we just want to check if template exists, no longer maintaining list of links
            template = common.validate_filename(template)
            template = self._validate_template(template)

            item = [template]
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
            result['msg'] = "Deleted %s" % result['type']
            return result
        else:
            msg = 'Delete operation returned OK, but object still there?'
            raise error.SearchError(msg)
