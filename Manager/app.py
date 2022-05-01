#!/usr/bin/python3
'''Python script to send emails on server'''
from emailer import Emailer
import logging
import logging.handlers
import os
import utilities
from state import State
from flask import Flask, request, jsonify

app = Flask(__name__)


filename = '/home/{}/sync/manager.log'

try:
    name = utilities.get_user()
    filename = filename.format(name)
    os.remove(filename)
except OSError as error:
    pass

# Add the log message handler to the logger
logging.basicConfig(filename=filename,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

class Server(Flask):

    def __init__(self, import_name):
        '''Constructor for flask API methods'''
        super(Server, self).__init__(import_name)
        self.route('/', methods=['GET'])(self.get_list)
        self.route('/alarm', methods=['POST'])(self.set_alarm)
        self.route('/alarm', methods=['GET'])(self.get_alarm)
        self.route('/motion', methods=['POST'])(self.add_motion)
        self.state = State()
        self.request_result = False

    def get_list(self):
        data = {
            "alarm": [
                "GET",
                "POST"
            ],
            "motion": [
                "POST"
            ]
        }
        return jsonify(data)

    def result(self, results={}):
        '''Converts bool to string'''
        logging.info('# result()')
        data = {
            "result": "Failure"
        }
        if self.request_result is True:
            data = {
                "result": "Success",
                "data": results
            }
        return data

    def set_alarm(self):
        logging.info('# set_alarm()')
        # Ensure wrong days are not entered
        request_data = request.get_json()
        if request_data:
            self.request_result = self.state.update_alarm(request_data)
        data = self.result()
        return jsonify(data)

    def get_alarm(self):
        logging.info('# get_alarm()')
        # Ensure wrong days are not entered
        self.request_result, results = self.state.get_alarm()
        data = self.result(results)
        return jsonify(data)

    def add_motion(self):
        logging.info('# add_motion()')
        request_data = request.get_json()
        try:
            result = self.state.get_alarm()
            status = result['status']
            logging.info(status)
        except KeyError as error:
            logging.error('Key error on result')
        except TypeError as error:
            logging.error('Type error on result')
        '''
        if result['status'] == 1:
            if request_data:
                emailer = Emailer()
                #self.request_result = emailer.send(request_data['image'])
        else:
            logging.info('Alarm is Off')'''
        data = self.result()
        return jsonify(data)

if __name__ == "__main__":
    logging.info("Starting program")
    server = Server(__name__)
    server.run(debug=True, host='0.0.0.0')
	