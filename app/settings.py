import ujson
import os.path

CONF_FILE_PATH = os.path.join(os.getcwd(), "config.json")

DEFAULTS = {
    'mongo_uri': 'mongodb://mongo',
    'rabbitmq_uri': 'rabbitmq',
    'host': '0.0.0.0',
    'port': 8000,
    'debug': True,
    'workers': 1,
    'mongo_db_name': 'local',
    'mongo_collection_name': 'crud_docs'
}

config = DEFAULTS

try:
    with open(CONF_FILE_PATH, 'r') as conf_file:
        config.update(ujson.load(conf_file))
except OSError:
    print('Config file {0} not present or inaccessible, using '
          'defaults'.format(CONF_FILE_PATH))
except ValueError:
    print('Config file {0} does not contain valid JSON, using '
          'defaults'.format(CONF_FILE_PATH))
else:
    print('Config file {0} loaded'.format(CONF_FILE_PATH))
