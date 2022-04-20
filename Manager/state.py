import logging
import pymongo
import utilities
import json
from exceptions import BadDataError

class State:

    def __init__(self):
        '''Constructor for state class'''
        logging.info('# state.__init__()')
        self.client = None
        self.username = ''
        self.password = ''
        self.db       = None
        self.host     = ''

    def get_settings(self):
        '''Get config env var'''
        logging.info('get_settings()')
        try:
            config_name = '/home/{}/sync/config.json'.format(utilities.get_user())
            with open(config_name) as file:
                data = json.load(file)
            self.username = data["db_username"]
            self.password = data["db_password"]
            self.host     = data["db_host"]
        except KeyError:
            logging.info("Variables not set")
        except FileNotFoundError:
            logging.info('File not found')
        except IOError:
            logging.info('Could not read file')

    def connect(self):
        logging.info('# connect()')
        self.get_settings()
        conn_str = 'mongodb://{}:{}@{}:27017/house-guard?authSource=admin'
        conn_str = conn_str.format(self.username, self.password, self.host)
        success = False
        try:
            self.client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)
            self.db = self.client['house-guard']
            success = True
            logging.info('Success on connection')
        except pymongo.errors.OperationFailure as error:
            logging.error('Pymongo failed on auth: {}'.format(error))
        except pymongo.errors.ServerSelectionTimeoutError as error:
            logging.error('Pymongo failed on timeout: {}'.format(error))
        except pymongo.errors.InvalidURI as error:
            logging.error('File was empty')
        return success

    def get(self, collection):
        '''Returns data from the last day'''
        logging.info('# get_alarm()')
        result = {
            "status": 1
        }
        if self.client:
            try:
                for event in collection.find({}, { "_id": 0, "status": 1}):
                    # Temporary id added for records returned in data dict
                    logging.info('Record found: {}'.format(event))
                    if event['status'] == 0:
                        result["status"] = 0
            except pymongo.errors.OperationFailure as error:
                logging.error('Pymongo failed on auth: {}'.format(error))
            except pymongo.errors.ServerSelectionTimeoutError as error:
                logging.error('Pymongo failed on timeout: {}'.format(error))
            except KeyError as error:
                logging.error("Key didn't exist on record")
        else:
            logging.error('No data could be retrieved')
        return result

    def post(self, status, collection):
        '''Adds new data'''
        logging.info('# post()')
        success = False
        if self.client:
            try:
                new_values = { "$set": { "status": status } }
                collection.update_one({},  new_values)
                success = True
            except pymongo.errors.OperationFailure as error:
                logging.error('Pymongo failed on auth: {}'.format(error))
            except BadDataError as error:
                logging.error('Data was invalid')
            except pymongo.errors.ServerSelectionTimeoutError as error:
                logging.error('Pymongo failed on timeout: {}'.format(error))
            except KeyError as error:
                logging.error("Key didn't exist on record")
        else:
            logging.error('No data could be retrieved')
        return success

    def update_alarm(self, request_data):
        '''Updates alarm status'''
        logging.info('# update_alarm()')
        if self.connect():
            collection = self.db.alarm
            status = request_data['status']
            return self.post(status, collection)
        else:
            return False

    def get_alarm(self):
        '''Returns alarm status'''
        logging.info('# get_alarm()')
        if self.connect():
            collection = self.db.alarm
            status = self.get(collection)
            return True, status
        else:
            return False, status

