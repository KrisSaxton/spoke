'''Virtual machine power management module.
Classes:
SpokeVMPower - manipulation of virtual machine power statuses.
SpokeVMPowerXen - manipulation of Xen virtual machine power statuses.
SpokeVMPowerKvm - manipulation of Kvm virtual machine power statuses.

Exceptions:
NotFound - raised on failure to find an object when one is expected.
InputError - raised on invalid input.
SearchError - raised to indicate unwanted search results were returned.
SpokeError - raised when action fails for unknown reason.
VMRunning - raised on failed actions due to a VM being in a running state.
VMStopped - raised on failed actions due to a VM being in a stopped state.
ValidationError -raised when an action completes OK but validation fails.
LibvirtError - raised on failed libvirt actions.
'''

# core modules
import time
import traceback

# own modules
import spoke.lib.error as error
import spoke.lib.common as common
import spoke.lib.config as config
import spoke.lib.logger as logger

# 3rd party modules
try:
    import libvirt
except:
    msg = 'Failed to import libvirt'
    raise error.LibvirtError(msg)

class SpokeVMPower:    
    
    """Provide CRUD methods to Virtual machine power objects."""
    
    def __init__(self, vm_name):
        """Get config and setup logging."""
        self.config = config.setup()
        self.log = logger.setup(self.__module__)
        def _error_handler(self, err):
            msg = "Ignoring Libvirt error %s)" % err
            pass
        # Prevent libvirt errors from reaching the console
        libvirt.registerErrorHandler(_error_handler, None)
 
    def get(self):
        '''get the power state of a given vm'''
        data = []
        item = {}
        state = self._lookupState(self.dom.info()[0])
        item['vm_name'] = self.vm_name
        item['state'] = state
        data.append(item)
        self.log.debug(data)
        result = common.process_results(data, 'VM')
        #out = xml.xml_to_text(info, self.headers)
        #self.log.info(out)
        self.log.debug('Result: %s' % result)
        return result
    
    def modify(self, vm_power_state):
        '''Change the power state of a vm'''
        if vm_power_state == "on":
            result = self.create()
        elif vm_power_state == "off":
            result = self.delete()           
        elif vm_power_state == "reboot":
            try:
                result = self.dom.reboot(0)
                msg = "Power cycled %s" % self.vm_name
                self.log.debug(msg)
            except libvirt.libvirtError:
                msg = "Failed to power cycle %s" % self.vm_name
                raise error.LibvirtError(msg)
            if result != 0:
                msg = 'Unknown error rebooting VM, libvirt returned %s' % result
                raise error.LibvirtError(msg)
        elif vm_power_state == "forceoff":
            result = self.delete(force=True)            
        else:
            msg = "Invalid state, must be one of: on|off|reboot|forceoff"
            raise error.InputError, msg
        #self.conn.close()
        result = self.get()
        if result['exit_code'] == 0 and result['count'] == 1:
            result['msg'] = "Modified %s:" % result['type']
            return result
        else:
            msg = 'Power operation returned OK, but unable to find object'
            raise error.NotFound(msg)
        return result
            
    def create(self):
        '''Power on a VM'''
        try:
            self.dom.create()
        except libvirt.libvirtError:
            msg = "VM %s is already powered on." % self.vm_name
            raise error.VMRunning, msg  
        #self.conn.close()      
        result = self.get()
        if result['exit_code'] == 0 and result['count'] == 1:
            result['msg'] = "Powered on %s:" % result['type']
            return result
        else:
            msg = 'Power operation returned OK, but unable to find object'
            raise error.NotFound(msg)
        return result
        
    def delete(self, force=False):
        '''Power off a VM'''
        if force: # Hard shutdown
            try:
                result = self.dom.destroy()
                msg = "Forced powered off %s" % self.vm_name
                self.log.debug(msg)
            except libvirt.libvirtError:
                msg = "VM % is already powered off." % self.vm_name
                raise error.VMStopped, msg
        else: # Regular shutdown
            try:
                result = self.dom.shutdown()
                msg = "Shutting down %s" % self.vm_name
                self.log.debug(msg)
            except libvirt.libvirtError:
                msg = "VM %s is already powered off" % self.vm_name
                raise error.VMStopped, msg
        if result != 0:
            msg = 'Unknown error shutting down VM, libvirt returned %s' % result
            raise error.LibvirtError(msg)
        result = self.get()
        # For regular power off requests we have to wait for the OS to shutdown
        # so we retry a few times
        # persistent VMs should return 'Off' when shutdown
        # transient VMs should return 'No State' (as the VM is done)
        tries = 1
        wait = 3
        retries = self.config.get('VM', 'status_retries', 5)
        while tries < retries:
            state = result['data'][0]['state']
            if result['exit_code'] == 0 and (state == 'Off' or \
                                             state == 'No State'):
                result['msg'] = "Powered off %s:" % result['type']
                return result
            time.sleep(wait)
            result = self.get()
            wait += 3
            tries += 1
        # if we get here, VM state never returned Off 
        msg = 'Power operation returned OK, but %s state is %s' % \
                (self.vm_name, result['data'][0]['state'])
        raise error.ValidationError(msg)
    
    def _lookupState(self, id):
        '''internal, just returns state from state id number'''
        states = {0: "No State", 1: "On",  2: "On", 3: "Paused",
                   4: "Shutdown", 5: "Off", 6: "Crashed"}
        
        return states[id]

    
class SpokeVMPowerXen(SpokeVMPower):
    def __init__(self, hv_uri, vm_name):
        '''Get some basic config and connect to hypervisor'''
        SpokeVMPower.__init__(self, vm_name)
        self.hv_uri = hv_uri
        self.vm_name = common.validate_hostname(vm_name)
        self.conn = None
        try:
            self.conn = libvirt.open(self.hv_uri)
            msg = "Successfully connected to: " + self.hv_uri
            self.log.debug(msg)
        except libvirt.libvirtError:
            trace = traceback.format_exc()
            msg = 'Libvirt connection to URI %s failed' % self.hv_uri
            raise error.LibvirtError(msg, trace)
        except Exception:
            trace = traceback.format_exc()
            msg = 'Unknown error'
            raise error.SpokeError(msg, trace)
        finally:
            if self.conn == None:
                msg = 'Libvirt connection to URI %s failed' % self.hv_uri
                raise error.LibvirtError(msg)
            try:
                self.dom = self.conn.lookupByName(self.vm_name)
            except libvirt.libvirtError:
                msg = "VM %s not found." % self.vm_name
                raise error.NotFound(msg)   
    
class SpokeVMPowerKvm(SpokeVMPower):
    def __init__(self, hv_uri):
        SpokeVMPower.__init__(self)
        print("USING KVM CLASS")
    
