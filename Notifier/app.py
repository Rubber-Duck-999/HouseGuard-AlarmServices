#!/usr/bin/python3
'''Python script to send emails on server'''
from datetime import datetime
import logging
import logging.handlers
import os
import utilities
from state import State
from flask import Flask, request, jsonify

app = Flask(__name__)


filename = '/home/{}/sync/notifier.log'

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
        self.route('/admin', methods=['GET'])(self.get_admin)
        self.route('/admin', methods=['POST'])(self.set_admin)
        self.route('/host', methods=['POST'])(self.set_host)
        self.route('/host', methods=['GET'])(self.get_host)
        self.state = State()
        self.request_result = False

    def get_list(self):
        data = {
            "admin": [
                "GET",
                "POST"
            ],
            "host": [
                "GET",
                "POST"
            ]
        }
        return jsonify(data)

    def result(self, results=None):
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

    def get_host(self):
        logging.info('# get_host()')
        # Ensure wrong days are not entered
        self.request_result, results = self.state.get_temperature()
        data = self.result(results)
        return jsonify(data)

    def set_host(self):
        logging.info('# set_host()')
        request_data = request.get_json()
        if request_data:
            self.request_result = self.state.add_temperature(request_data)
        data = self.result()
        return jsonify(data)


if __name__ == "__main__":
    logging.info("Starting program")
    server = Server(__name__)
    server.run(debug=True, host='0.0.0.0')
	