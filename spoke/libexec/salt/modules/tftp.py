'''
Salt module for querying tftp directory and creating
or deleting tftp configs for specific macs from a
template

REQUIRES:
Spoke: tftp lib, error, config and common
'''

# own modules
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.common as common

version = common.version
config_file = '/usr/local/pkg/spoke/etc/spoke.conf'

try:
    conf = config.setup(config_file)
except error.ConfigError, e:
    raise

try:
    tftproot = conf.get("TFTP", "tftp_root")
    from spoke.lib.tftp import SpokeTFTP
    tftp = SpokeTFTP(tftproot)
except error.SpokeError, e:
    raise


def search(mac=None, template=None):
    '''
    Return dict with list of templates and configs

    CLI Examples::

        salt '*' tftp.search
        salt '*' tftp.search mac='11:22:33:44:55:66'
        salt '*' tftp.search template='test.template'
    '''
    try:
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
        result = tftp.delete(mac)
    except error.SpokeError as e:
        result = common.handle_error(e)
    return result
