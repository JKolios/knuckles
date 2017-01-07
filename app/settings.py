import ujson
from sanic.log import log

CONF_FILE_PATH = "config.json"

DEFAULTS = {
    'mongo_connection_string': 'mongodb://mongo',
    'host': '0.0.0.0',
    'port': 8000,
    'debug': True,
    'workers': 1
}

config = DEFAULTS

try:
    with open(CONF_FILE_PATH, 'r') as conf_file:
        config.update(ujson.load(conf_file))
except OSError:
    log.debug('Config file %s not present or inaccessible, using '
              'defaults', CONF_FILE_PATH)
except ValueError:
    log.debug('Config file %s does not contain valid JSON, using '
              'defaults', CONF_FILE_PATH)
else:
    log.debug('Config file {0} loaded', CONF_FILE_PATH)