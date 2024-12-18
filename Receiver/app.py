import os
import os.path
import datetime
import uuid
import json
import logging
import logging.config
import connexion
from connexion import NoContent

import yaml

from pykafka import KafkaClient



# CONFIFUGRATION FILES
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

logger.info("App Conf File: %s " % APP_CONF_FILE)
logger.info("Log Conf File: %s " % LOG_CONF_FILE)

# KAFKA CLIENT STARTUP
client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
topic = client.topics[str.encode(app_config['events']['topic'])]
producer = topic.get_sync_producer()
# GET REQUESTS
def get_check():
    logger.info('Get check')
    return NoContent, 200

# POST REQUESTS
def join_queue(body):
    """
    Adds a request to the queue with a unique trace ID and timestamp.

    This function takes a request body, generates a UUID trace ID, wraps the data in a
    standardized message format, and publishes it to a message queue. The message includes
    the request type, timestamp, and the original payload enriched with a trace ID.

    Args:
        body (dict): The request payload to be queued.

    Returns:
        tuple: A tuple containing (NoContent, 201) indicating successful queuing.
            - NoContent: Represents an empty response body
            - 201: HTTP status code for "Created"
    """
    trace_id = uuid.uuid4()
    body['trace_id'] = str(trace_id)
    msg = { "type": "join_queue",
            "datetime" : datetime.datetime.now().strftime( "%Y-%m-%dT%H:%M:%S"),
            "payload": body
           }
    msg_str = json.dumps(msg)
    logger.info("Sending event: %s "% msg_str)
    producer.produce(msg_str.encode('utf-8'))
    return NoContent, 201

def add_friend(body):
    """
    Publishes a friend request event to the message queue with tracking metadata.

    This function processes a friend request by creating a message with a unique trace ID
    and timestamp, then publishes it to the message queue for asynchronous processing.
    The original request body is preserved within the message payload.

    Args:
        body (dict): The friend request details. Can include fields such as 
            requester_id, friend_id, or other relevant friendship metadata.

    Returns:
        tuple: A tuple containing (NoContent, 201) indicating successful queuing.
            - NoContent: Represents an empty response body
            - 201: HTTP status code for "Created"
    """
    trace_id = uuid.uuid4()
    body['trace_id'] = str(trace_id)
    msg = { "type": "add_friend",
            "datetime" :datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": body
            }
    msg_str = json.dumps(msg)
    logger.info("Sending event: %s "% msg_str)
    producer.produce(msg_str.encode('utf-8'))
    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            base_path="/receiver",
            strict_validation=True,
            validate_responses=True)
if __name__ == "__main__":
    app.run(port=8080, host='0.0.0.0')
