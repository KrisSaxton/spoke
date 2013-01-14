'''
Salt module to expose TFTP management elements of Spoke API
'''

# Import core libs
import re
import logging

# Import salt modules
from salt.exceptions import SaltInvocationError

# Import spoke libs
try:
    import spoke.lib.error as error
    import spoke.lib.config as config
    import spoke.lib.common as common
    from spoke.lib.tftp import SpokeTFTP
    has_tftp = True
except ImportError:
    has_tftp = False

log = logging.getLogger(__name__)
version = common.version


def __virtual__():
    '''
    Only load this module if the spoke modules imported correctly
    '''
    if has_tftp:
        return 'tftp'
    return False


def _salt_config(name):
    value = __salt__['config.option']('SPOKE.{0}'.format(name))
    if not value:
        msg = 'missing SPOKE.{0} in config'.format(name)
        raise SaltInvocationError(msg)
    return value


def _spoke_config(config_file):
    try:
        conf = config.setup(config_file)
    except error.ConfigError, e:
        msg = 'Error reading config file {0}'.format(config_file)
        raise SaltInvocationError(msg)
    return conf


def search(mac=None, template=None):
    '''
    Return dict with list of templates and configs

    CLI Examples::

        salt '*' tftp.search
        salt '*' tftp.search mac='11:22:33:44:55:66'
        salt '*' tftp.search template='test.template'
    '''
    try:
        conf = _spoke_config(_salt_config('config'))
        tftproot = conf.get("TFTP", "tftp_root")
        tftp = SpokeTFTP(tftproot)
        result = tftp.search(mac, template)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result


def create(mac=None, template=None, run_id=None):
    '''
    Create a config for a specific MAC from a template
    run_id is optional

    CLI Examples::

        salt '*' tftp.create template='test.template' mac='11:22:33:44:55:66'
        salt '*' tftp.create template='test.template' mac='11:22:33:44:55:66'\\
        run_id=2590
    '''
    if mac is None or template is None:
        return "mac and template must be specified"
    conf = _spoke_config(_salt_config('config'))
    tftproot = conf.get("TFTP", "tftp_root")
    tftp = SpokeTFTP(tftproot)
    if run_id is None:
        try:
            result = tftp.create(mac, template)
        except error.SpokeError as e:
            result = common.handle_error(e)
    else:
        try:
            result = tftp.create(mac, template, run_id)
        except error.SpokeError as e:
            result = common.handle_error(e)
    return result


def delete(mac=None):
    '''
    Delete a config for a specific MAC

    CLI Examples::

        salt '*' tftp.delete mac='11:22:33:44:55:66'
    '''
    if mac is None:
        return "mac must be specified"
    try:
        conf = _spoke_config(_salt_config('config'))
        tftproot = conf.get("TFTP", "tftp_root")
        tftp = SpokeTFTP(tftproot)
        result = tftp.delete(mac)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result
