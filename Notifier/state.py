import datetime as dt
from datetime import timedelta
import logging
import pymongo
import utilities
import json
from exceptions import BadDataError
from validate import (validate_temperature,
                      validate_network)

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

    def get(self, collection, field_time, field_one, field_two):
        '''Returns data from the last day'''
        logging.info('# get()')
        data_list = []
        average = [0.0, 0.0]
        if self.client:
            try:
                count = 0
                start = dt.datetime.now() -  timedelta(days=1)
                # Querying mongo collection for data within period
                query = { field_time: {'$lt': dt.datetime.now(), '$gte': start}}
                for event in collection.find(query, { "_id": 0, field_one: 1, field_time: 1, field_two: 1 }):
                    event['Id'] = str(count)
                    average[0] = average[0] + event[field_one]
                    average[1] = average[1] + event[field_two]
                    data_list.append(event)
                    count = count + 1
                average[0] = round(average[0] / count, 2)
                average[1] = round(average[1] / count, 2)
                # Temprorary id added for records returned in data dict
                logging.info('Records found: {}'.format(count))
            except pymongo.errors.OperationFailure as error:
                logging.error('Pymongo failed on auth: {}'.format(error))
            except pymongo.errors.ServerSelectionTimeoutError as error:
                logging.error('Pymongo failed on timeout: {}'.format(error))
            except KeyError as error:
                logging.error("Key didn't exist on record")
        else:
            logging.error('No data could be retrieved')
        return data_list, average

    def post(self, data, collection):
        '''Adds new data'''
        logging.info('# post()')
        success = False
        if self.client:
            try:
                record = collection.insert_one(data)
                logging.info('Record Id: {}'.format(record.inserted_id))
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

    def delete(self, collection, field_time):
        '''Removes data from up to the last 2 days'''
        logging.info('# delete()')
        success = False
        if self.client:
            try:
                start = dt.datetime.now() -  timedelta(days=2)
                # Querying mongo collection for temperature over 2 days
                query = { field_time: {'$lt': start}}
                result = collection.delete_many(query)
                # Temprorary id added for records returned in data dict
                logging.info('Records found: {}'.format(result))
                success = True
            except pymongo.errors.OperationFailure as error:
                logging.error('Pymongo failed on auth: {}'.format(error))
            except pymongo.errors.ServerSelectionTimeoutError as error:
                logging.error('Pymongo failed on timeout: {}'.format(error))
            except KeyError as error:
                logging.error("Key didn't exist on record")
        else:
            logging.error('No data could be retrieved')
        return success

    def add_temperature(self, request_data):
        logging.info('# add_temperature()')
        if self.connect():
            collection = self.db.temperature
            return self.post(validate_temperature(request_data), collection)
        else:
            return False

    def add_speed(self, request_data):
        logging.info('# add_speed()')
        if self.connect():
            collection = self.db.network
            return self.post(validate_network(request_data), collection)
        else:
            return False

    def get_temperature(self):
        '''Returns data from the last day'''
        logging.info('# get_temperature()')
        if self.connect():
            collection = self.db.temperature
            time = "TimeOfTemperature"
            field_one = "Temperature"
            field_two = "Humidity"
            data_list, average = self.get(collection,
                                        time,
                                        field_one,
                                        field_two)
            return True, data_list, average
        else:
            return False, [], [0.0, 0.0]

    def get_speed(self):
        '''Returns data from up to the last 7 days'''
        logging.info('# get_speed()')
        if self.connect():
            collection = self.db.network
            time = "TimeOfTest"
            field_one = "Download"
            field_two = "Upload"
            data_list, average = self.get(collection,
                                        time,
                                        field_one,
                                        field_two)
            return True, data_list, average
        else:
            return False, [], [0.0, 0.0]

    def remove_network(self):
        '''Returns data from up to the last 5 days'''
        logging.info('# remove_network()')
        success = False
        if self.connect():
            collection = self.db.temperature
            success = self.remove(collection, 'TimeOfTemperature')
        return success

    def remove_speed(self):
        '''Returns data from up to the last 5 days'''
        logging.info('# remove_speed()')
        success = False
        if self.connect():
            collection = self.db.network
            success = self.remove(collection, 'TimeOfTest')
        return success
