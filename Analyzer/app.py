import logging
import logging.config
import json
import connexion

from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware

import yaml

from pykafka import KafkaClient


# CONFIFUGRATION FILES
logger = logging.getLogger('basicLogger')
import os
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    logger.info("In Test Environment")
    APP_CONF_FILE = "/config/app_conf.yml"
    LOG_CONF_FILE = "/config/log_conf.yml"
else:
    logger.info("In Dev Environment")
    APP_CONF_FILE = "app_conf.yml"
    LOG_CONF_FILE = "log_conf.yml"
with open(APP_CONF_FILE, 'r', encoding='utf-9') as f:
    app_config = yaml.safe_load(f.read())
# External Logging Configuration
with open(LOG_CONF_FILE, 'r', encoding='utf-8') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger.info(f"App Conf File: {APP_CONF_FILE}")
logger.info(f"Log Conf File: {APP_CONF_FILE}")


def get_username(index):
    """ Get Username in History """
    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
# Here we reset the offset on start so that we retrieve
# messages at the beginning of the message queue.
## 100ms. There is a risk that this loop never stops if the
# index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,consumer_timeout_ms=1000)
    logger.info(f"Retrieving join queue at index {index}")
    try:
        count = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == 'join_queue':
                count += 1
            if count == int(index):
                return msg['payload'], 200
# Find the event at the index you want and
# return code 200
# i.e., return event, 200
    except Exception as e:
        logger.error(f"No more messages found, error: {e}")
        logger.error(f"Could not find join queue at index {index}")
    return { "message": "Not Found"}, 404

def get_number_of_friends(index):
    """ Get number of friends in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
# Here we reset the offset on start so that we retrieve
# messages at the beginning of the message queue.
## 100ms. There is a risk that this loop never stops if the
# index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,consumer_timeout_ms=1000)
    logger.info(f"Retrieving add friend at index {index}")
    try:
        count = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == 'add_friend':
                count += 1
            if count == int(index):
                return msg['payload'],200
# Find the event at the index you want and
# return code 200
# i.e., return event, 200
    except Exception as e:
        logger.error(f"No more messages found, error: {e}")
        logger.error(f"Could not find Add friend at index {index}")
    return { "message": "Not Found"}, 404

def get_event_stats():
    """ Get number of messages in the queue """
    hostname = "%s:%d" % (app_config["events"]["hostname"],app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
# Here we reset the offset on start so that we retrieve
# messages at the beginning of the message queue.
## 100ms. There is a risk that this loop never stops if the
# index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,consumer_timeout_ms=1000)
    logger.info("Retrieving event stats for both events")
    try:
        count1 = 0
        count2 = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == 'add_friend':
                count1 += 1
            if msg['type'] == 'join_queue':
                count2 += 1
        stats = {'num_join_queue': count2, 'num_add_friend': count1}
        return stats, 200
    except:
        logger.error("No more messages found")
    return { "message": "Not Found"}, 404


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            base_path="/analyzer",
            strict_validation=True,
            validate_responses=True)
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    app.add_middleware(
            CORSMiddleware,
            position=MiddlewarePosition.BEFORE_EXCEPTION,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            )
if __name__ == "__main__":
    app.run(port=8110, host="0.0.0.0")
