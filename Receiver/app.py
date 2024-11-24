import connexion
import os.path
import json
import datetime
from connexion import NoContent

import requests

import yaml
import logging
import logging.config
import uuid

from pykafka import KafkaClient


logger = logging.getLogger('basicLogger')

# CONFIFUGRATION FILES
import os
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)



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
            strict_validation=True,
            validate_responses=True)
if __name__ == "__main__":
    app.run(port=8080, host='0.0.0.0')
