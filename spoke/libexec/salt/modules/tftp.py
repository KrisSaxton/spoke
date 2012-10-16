# core modules
import sys

# own modules
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.logger as logger
import spoke.lib.common as common

version = common.version

config_file = '/usr/local/pkg/spoke/etc/spoke.conf'

try:
    conf = config.setup(config_file)
except error.ConfigError, e:
    print e.msg
    raise e

log = logger.setup('main', verbose=True, quiet=False)

try:
    tftproot = conf.get("TFTP", "tftp_root")
    from spoke.lib.tftp import SpokeTFTP
    tftp = SpokeTFTP(tftproot) 
except error.SpokeError, e:
    log.error(e.msg)
    if e.traceback:
        log.debug(e.traceback)
    raise e

def _handle_error(e):
    result = {}
    result['msg'] = e.__class__.__name__ + ': ' + e.msg
    result['exit_code'] = e.exit_code
    return result

def search(mac=None, filename=None):
    try:
        result = tftp.search(mac, filename)
    except error.SpokeError as e:
        result = _handle_error(e)
    return result

def create(mac=None, template=None, run_id=None):
    if mac is None or template is None:
        return "mac and template must be specified"
    if run_id is None:
        try:
            result = tftp.create(mac, template)
        except error.SpokeError as e:
            result = _handle_error(e)
    else:
        try:
            result = tftp.create(mac, template, run_id)
        except error.SpokeError as e:
            result = _handle_error(e)
    return result

def delete(mac=None):
    if mac is None:
        return "mac must be specified"
    try:
        result = tftp.delete(mac)
    except error.SpokeError as e:
        result = _handle_error(e)
    return result
