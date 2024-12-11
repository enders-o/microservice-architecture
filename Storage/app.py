import os
import yaml
import json
import logging
import logging.config
import datetime
import connexion

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from pykafka import KafkaClient  
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread

from base import Base
from join_queue import JoinQueue
from add_friend import AddFriend

logger = logging.getLogger('basicLogger')
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    logger.info("In Test Environment")
    APP_CONF_FILE = "/config/app_conf.yml"
    LOG_CONF_FILE = "/config/log_conf.yml"
else:
    logger.info("In Dev Environment")
    APP_CONF_FILE = "app_conf.yml"
    LOG_CONF_FILE = "log_conf.yml"
with open(APP_CONF_FILE, 'r') as f:
    app_config = yaml.safe_load(f.read())
# External Logging Configuration
with open(LOG_CONF_FILE, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger.info("App Conf File: %s" % APP_CONF_FILE)
logger.info("Log Conf File: %s" % LOG_CONF_FILE)

logger.info(f"""
            Connecting to DB.
            Hostname: {app_config['datastore']['hostname']}, 
            Port: {app_config['datastore']['port']}
            """)
# https://docs.sqlalchemy.org/en/20/core/pooling.html
DB_ENGINE = create_engine(f"""
                          mysql+pymysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}
                          @{app_config['datastore']['hostname']}:{app_config['datastore']['port']}
                          /{app_config['datastore']['db']}""",
                          pool_size=20,
                          pool_recycle=300,
                          pool_pre_ping=True)
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def get_event_stats():
    try:
        session = DB_SESSION()
        add = session.query(AddFriend).count()
        join =session.query(JoinQueue).count()
        stats = {'num_join_queue': join, 'num_add_friend': add}
        return stats, 200
    except:
        logger.info("No messages found")
    return { "message": "Not Found"}, 404
def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                            app_config["events"]["port"])
    logger.info(f"Connecting to Kafka broker at {hostname}")
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
# Create a consume on a consumer group, that only reads new messages
# (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                        reset_offset_on_start=False,
                                        auto_offset_reset=OffsetType.LATEST)
    logger.info(f"Connected to Kafka topic: {app_config['events']['topic']}")
# This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        if msg["type"] == "join_queue": 
# Store the event1 (i.e., the payload) to the DB
            
            session = DB_SESSION()
            join = JoinQueue(payload['trace_id'],
                             payload['user_id'],
                             payload['username'],
                             payload['game'],
                             payload['account_age_days'])
            session.add(join)
            session.commit()
            session.close()
            logger.debug(f"Stored event join_queue request with a trace id of {payload['trace_id']}")
        elif msg["type"] == "add_friend": # Change this to your event type
            session = DB_SESSION()
            add = AddFriend(payload['trace_id'],
                            payload['source_user_id'],
                            payload['source_number_of_friends'],
                            payload['friend_user_id'],
                            payload['friend_number_of_friends'])
            session.add(add)
            session.commit()
            session.close()
            logger.debug(f"Stored event add_friend request with a trace id of {payload['trace_id']}")
        #logger.info()
        consumer.commit_offsets()
# Store the event2 (i.e., the payload) to the DB
# Commit the new message as being read

# GET REQUESTS
def get_join_queue(start_timestamp,end_timestamp):
    session = DB_SESSION()
    start_timestamp_datetime =datetime.datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S.%f")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S.%f")
    results = session.query(JoinQueue).filter(
        and_(JoinQueue.date_created >= start_timestamp_datetime,
             JoinQueue.date_created < end_timestamp_datetime))
    results_list = []
    for result in results:
        result_dict = {'game': result.game, 'user_id': result.user_id,'username': result.username,'account_age_days': result.account_age_days}
        #print(result_dict)
        results_list.append(result_dict)
    session.close()
    logger.info("Query for JoinQueue after %s returns %d results" %
                (start_timestamp, len(results_list)))
    return results_list, 200

def get_add_friend(start_timestamp,end_timestamp):
    session = DB_SESSION()
    start_timestamp_datetime =datetime.datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S.%f")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S.%f")
    results = session.query(AddFriend).filter(
        and_(AddFriend.date_created >= start_timestamp_datetime,
             AddFriend.date_created < end_timestamp_datetime))
    results_list = []
    for result in results:
        result_dict = {'source_user_id': result.source_user_id,'source_number_of_friends': result.source_number_of_friends,'friend_user_id': result.friend_user_id,'friend_number_of_friends': result.friend_number_of_friends}
        #print(result_dict)
        results_list.append(result_dict)
    session.close()
    logger.info("Query for JoinQueue after %s returns %d results" %
                (start_timestamp, len(results_list)))
    return results_list, 200

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            base_path="/storage",
            strict_validation=True,
           validate_responses=True)
if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090, host="0.0.0.0")
