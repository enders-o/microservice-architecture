import connexion
#from connexion import NoContent
# had to pip install apscheduler
from apscheduler.schedulers.background  import BackgroundScheduler

import requests
import json
import os.path
import yaml
import logging
import logging.config
import datetime

logger = logging.getLogger('basicLogger')

with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())
with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

def get_stats():
    logger.info('Request started')
    if os.path.isfile(app_config['datastore']['filename']):
        with open(app_config['datastore']['filename'],"r") as outfile:
            # turn json string into python dict
            current_stats = json.loads(outfile.read())
            current_stats.pop('last_updated')
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
        current_stats['num_add'] +=  len(find)
    current_stats['last_updated'] = current_datetime
    with open(app_config['datastore']['filename'],"w") as outfile:
        outfile.write(json.dumps(current_stats, indent=4,default=str))
    #current_stats['last_updated'] = datetime.datetime.strptime(current_stats['last_updated'], "%Y-%m-%d %H:%M:%S.%f")
    logger.debug(f'Updated values {current_stats}')
    logger.info('End Periodic Processing')

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
if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, host="0.0.0.0")
