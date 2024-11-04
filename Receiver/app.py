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

with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

# POST REQUESTS
def join_queue(body):
    trace_id = uuid.uuid4()
    body['trace_id'] = str(trace_id)
    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
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
    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
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
    app.run(port=8080)
