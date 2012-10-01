"""Provides Key-Value store access and management.

Classes:
SpokeKV - extends redis with several convenience classes.

Exceptions:
RedisError - raised on failed Redis actions.
"""
# core modules
import traceback

# own modules
import spoke.lib.error as error
import spoke.lib.config as config
import spoke.lib.logger as logger

# 3rd party modules
try:
    import redis
except:
    msg = 'Failed to import redis'
    raise error.RedisError(msg)

kvLDAP = None

def setup():
    """Instantiate (once only) and return Redis connection object"""
    global kvLDAP
    if kvLDAP is not None:
        pass
    else:
        kvLDAP = SpokeKVConn()  
    return kvLDAP

class SpokeKVConn:
    
    """Class representing Redis server connection."""
    
    def __init__(self):
        """Bind to Redis server, return an redis connection object."""
        self.config = config.setup()
        self.log = logger.setup(__name__)
        self.kv_host = self.config.get('KV', 'kv_host')
        self.kv_port = int(self.config.get('KV', 'kv_port', 6379))
        self.kv_db = self.config.get('KV', 'kv_db', '0')
        try:
            self.KV = redis.StrictRedis(host=self.kv_host, port=self.kv_port,
                                         db=self.kv_db)
            # We have to query something to know if the connection is good
            self.KV.keys()
        except redis.exceptions.ConnectionError:
            msg = 'Connection to Redis server %s:%s as %s failed' % \
                (self.kv_host, self.kv_port, self.kv_db)
            trace = traceback.format_exc()
            raise error.RedisError(msg, trace)

class SpokeKV:
    
    """Extend redis class with convenience methods."""
    
    def __init__(self):
        """Parse configuration, setup logging; 
        bind to Redis server and return a Redis connection object."""
        self.config = config.setup()
        self.log = logger.setup(__name__)
        self.KV = setup().KV
