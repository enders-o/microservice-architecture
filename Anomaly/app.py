import connexion
#from connexion import NoContent

import os.path
import yaml
import logging
import logging.config
import json
import uuid
from datetime import datetime

from pykafka import KafkaClient  
from pykafka import KafkaClient  
from pykafka.common import OffsetType 
from threading import Thread 


import os

# CONFIGURATION
logger = logging.getLogger('basicLogger')
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    logger.info("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    logger.info("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)
logger.info(f'Threshold for account age : ({app_config["threshold"]["find_low"]},{app_config["threshold"]["find_high"]})')
logger.info(f'Threshold for source number friend:  ({app_config["threshold"]["add_low"]},{app_config["threshold"]["add_high"]})')

# GET REQUESTS
def get_find():
    return [], 200


def get_add():
    return [], 200

def store_anomaly(payload: dict, event_type: str, is_high: bool, threshold: int):
    event_id = str(uuid.uuid4())
    logger.debug(f"Detected anomaly {payload['trace_id']}")
    anomaly = {
            "event_id": event_id,
            "trace_id": payload["trace_id"],
            "event_type": event_type,
            "anomaly_type": "Too High" if is_high else "Too Low",
            "description": f"The value is {'too high' if is_high else 'too low'} ({event_type} of {payload['value']} is {'greater' if is_high else 'less'} than threshold of {threshold})",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    try:
        with open(app_config['datastore']['filename'], "r") as infile:
            data = json.load(infile)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    data.append(anomaly)
    with open(app_config['datastore']['filename'], "w") as outfile:
            json.dump(data, outfile, indent=2)
    logger.info(f"Stored anomaly {event_id} for trace {payload['trace_id']}")
    return event_id

# ANOMALY DETECTION
def detect_anomalies():
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                            app_config["events"]["port"])
    logger.info(f"Connecting to Kafka broker at {hostname}")
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                        reset_offset_on_start=False,
                                        auto_offset_reset=OffsetType.LATEST)
    logger.info(f"Connected to Kafka topic: {app_config['events']['topic']}")
    for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            logger.info("Message: %s" % msg)
            payload = msg["payload"]
            if msg["type"] == "join_queue": 
                if payload["account_age_days"] > app_config["threshold"]["find_high"]:
                    store_anomaly(payload, 'find', True,app_config["threshold"]["find_high"])
                if payload["account_age_days"] < app_config["threshold"]["find_low"]:
                    store_anomaly(payload, 'find', False,app_config["threshold"]["find_low"]))
            elif msg["type"] == "add_friend": 
                if payload["source_number_of_friends"] > app_config["threshold"]["add_high"]:
                    store_anomaly(payload, 'add', True, app_config["threshold"]["add_high"]))
                if payload["account_age_days"] < app_config["threshold"]["add_low"]:
                    store_anomaly(payload, 'add', False, app_config["threshold"]["add_low"]))
    consumer.commit_offsets()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            base_path="/anomaly",
            strict_validation=True,
           validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=detect_anomalies)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8120, host="0.0.0.0")
