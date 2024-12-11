import connexion
#from connexion import NoContent
# had to pip install apscheduler
from apscheduler.schedulers.background  import BackgroundScheduler
import requests
from requests.exceptions import Timeout, ConnectionError
import json
import os.path
import yaml
import logging
import logging.config

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
# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

RECEIVER_URL = app_config['services']['receiver']
STORAGE_URL = app_config['services']['storage']
PROCESSING_URL = app_config['services']['processing']
ANALYZER_URL = app_config['services']['analyzer']
TIMEOUT =app_config['timeout']['period_sec']

def check_services():
    """ Called periodically """
    receiver_status = "Unavailable"
    try:
        response = requests.get(RECEIVER_URL, timeout=TIMEOUT)
        if response.status_code == 200:
            receiver_status = "Healthy"
            logger.info("Receiver is Healthly")
        else:
            logger.info("Receiver returning non-200 response")
    except (Timeout, ConnectionError):
        logger.info("Receiver is Not Available")

    storage_status = "Unavailable"
    try:
        response = requests.get(STORAGE_URL, timeout=TIMEOUT)
        if response.status_code == 200:
            storage_json = response.json()
            storage_status = f"Storage has {storage_json['num_join_queue']} BP and {storage_json['num_add_friend']} HR events"
            logger.info("Storage is Healthy")
        else:
            logger.info("Storage returning non-200 response")
    except (Timeout, ConnectionError):
        logger.info("Storage is Not Available")

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(check_services,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            base_path="/check",
            strict_validation=True,
           validate_responses=True)
if "TARGET_ENV" in os.environ or os.environ["TARGET_ENV"] == "test":
    app.add_middleware(
            CORSMiddleware,
            position=MiddlewarePosition.BEFORE_EXCEPTION,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            )

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8130, host="0.0.0.0")
