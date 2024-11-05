import connexion
import json
from connexion import NoContent
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware

import yaml
import logging
import logging.config

from pykafka import KafkaClient

logger = logging.getLogger('basicLogger')

# CONFIFUGRATION FILES

with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

def get_username(index):
    """ Get Username in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
# Here we reset the offset on start so that we retrieve
# messages at the beginning of the message queue.
## 100ms. There is a risk that this loop never stops if the
# index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,consumer_timeout_ms=1000)
    logger.info("Retrieving join queue at index %d" % index)
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
    except:
        logger.error("No more messages found")
        logger.error("Could not find join queue at index %d" % index)
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
    logger.info("Retrieving add friend at index %d" % index)
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
    except:
        logger.error("No more messages found")
        logger.error("Could not find Add friend at index %d" % index)
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
            strict_validation=True,
            validate_responses=True)
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
