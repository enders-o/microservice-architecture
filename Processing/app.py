import connexion
#from connexion import NoContent
# had to pip install apscheduler
from apscheduler.schedulers.background  import BackgroundScheduler
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware

import requests
import json
import os.path
import yaml
import logging
import logging.config
import datetime


import os
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

def get_stats():
    logger.info('Request started')
    if os.path.isfile(app_config['datastore']['filename']):
        with open(app_config['datastore']['filename'],"r") as outfile:
            # turn json string into python dict
            current_stats = json.loads(outfile.read())
            #current_stats.pop('last_updated')
    else:
        logger.error('Statistics does not exist')
        return 404
    logger.debug(f'Statistics: {current_stats}')
    logger.info('Request completed')
    return current_stats, 200

def query(url) -> list:
    result = requests.get(url)
    if result.status_code == 200:
        logger.info(f'{len(result.json())} events received at {url}')
        return result.json()
    else:
        logger.error('Error, request failed')
        raise Exception

def populate_stats():
    """ Periodically update stats """
    try:
        logger.info("Start Periodic Processing")
        if os.path.isfile(app_config['datastore']['filename']):
            with open(app_config['datastore']['filename'],"r") as outfile:
                # turn json string into python dict
                current_stats = json.loads(outfile.read())
        else:
            current_stats = {
                    "num_joinq": 0,
                    "num_add": 0,
                    "max_age": 0,
                    "min_age": 9999,
                    "last_updated": "1970-01-01 00:00:00.000"
                    }
        logger.info(current_stats)
        current_datetime = datetime.datetime.now()
        find = query(f"{app_config['eventstore']['url']}/party/find?start_timestamp={current_stats['last_updated']}&end_timestamp={current_datetime}")
        add  = query(f"{app_config['eventstore']['url']}/party/add?start_timestamp={current_stats['last_updated']}&end_timestamp={current_datetime}")
        if find:
            current_stats['num_joinq'] +=  len(find)
            if current_stats['max_age'] < max(find,key = lambda x:x['account_age_days'])['account_age_days']:
                current_stats['max_age'] = max(find,key = lambda x:x['account_age_days'])['account_age_days']
            if current_stats['min_age'] > min(find,key = lambda x:x['account_age_days'])['account_age_days']:
                current_stats['min_age'] = min(find,key = lambda x:x['account_age_days'])['account_age_days']
        if add:
            current_stats['num_add'] +=  len(add)
        current_stats['last_updated'] = current_datetime
        #current_stats['last_updated'] = datetime.datetime.strptime(current_stats['last_updated'], "%Y-%m-%d %H:%M:%S.%f")
        with open(app_config['datastore']['filename'],"w") as outfile:
            outfile.write(json.dumps(current_stats, indent=4,default=str))
        logger.debug(f'Updated values {current_stats}')
        logger.info('End Periodic Processing')

    except Exception as e:
        logger.error(f"Error in populate_stats: {str(e)}", exc_info=True)

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()

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
    init_scheduler()
    app.run(port=8100, host="0.0.0.0")
