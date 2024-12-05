import os.path
import json
import logging
import logging.config
import connexion
import datetime
from connexion import NoContent

import yaml
import uuid

from pykafka import KafkaClient



# CONFIFUGRATION FILES
import os
logger = logging.getLogger('basicLogger')
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    logger.info("In Test Environment")
    APP_CONF_FILE = "/config/app_conf.yml"
    LOG_CONF_FILE = "/config/log_conf.yml"
else:
    logger.info("In Dev Environment")
    APP_CONF_FILE = "app_conf.yml"
    LOG_CONF_FILE = "log_conf.yml"

with open(APP_CONF_FILE, 'r', encoding='utf-8') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open(LOG_CONF_FILE, 'r', encoding='utf-8') as f:
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)

logger.info("App Conf File: %s" % APP_CONF_FILE)
logger.info("Log Conf File: %s" % LOG_CONF_FILE)



# KAFKA CLIENT STARTUP
client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
topic = client.topics[str.encode(app_config['events']['topic'])]
producer = topic.get_sync_producer()

# POST REQUESTS
def join_queue(body):
    trace_id = uuid.uuid4()
    body['trace_id'] = str(trace_id)
    msg = { "type": "join_queue",
            "datetime" : datetime.datetime.now().strftime( "%Y-%m-%dT%H:%M:%S"),
            "payload": body
           }
    msg_str = json.dumps(msg)
    logger.info(f'Sending event: {msg_str}')
    producer.produce(msg_str.encode('utf-8'))
    return NoContent, 201

def add_friend(body):
    trace_id = uuid.uuid4()
    body['trace_id'] = str(trace_id)
    msg = { "type": "add_friend",
            "datetime" :datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": body
            }
    msg_str = json.dumps(msg)
    logger.info(f'Sending event: {msg_str}')
    producer.produce(msg_str.encode('utf-8'))
    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            base_path="/receiver",
            strict_validation=True,
            validate_responses=True)
if __name__ == "__main__":
    app.run(port=8080, host='0.0.0.0')
