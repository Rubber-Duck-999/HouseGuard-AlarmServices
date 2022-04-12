#!/usr/bin/python3
import os
import logging
import json
import time
import utilities
from emailer import Emailer

filename = '/home/{}/sync/ping.log'

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
logging.info("Starting program")

class Ping:

    def __init__(self):
        self.hosts = [
            {
                "IP": "192.168.0.1",
                "State": False
            },
            {
                "IP": "192.168.0.11",
                "State": False
            },
            {
                "IP": "192.168.0.14",
                "State": False
            },
            {
                "IP": "192.168.0.15",
                "State": False
            },
            {
                "IP": "192.168.0.21",
                "State": False
            },
            {
                "IP": "192.168.0.38",
                "State": False
            },
            {
                "IP": "192.168.0.42",
                "State": False
            }
        ]
        self.admin = {
            "IP": "192.168.0.48",
            "State": False
        }

    def ping_check(self, host):
        success = False
        try:
            response = os.system("ping -qc 3 {}".format(host))
            # and then check the response...
            if response == 0:
                logging.info('Success on checks')
                success = True
        except OSError as error:
            logging.error('Check failed on {}'.format(error))
        return success

    def loop(self):
        '''Loop through sensor and publish'''
        while True:
            admin_state_change = False
            for host in self.hosts:
                host["State"] = self.ping_check(host["IP"])
                logging.info('Address: {}, Attempted ping: {}'.format(host["IP"], host["State"]))
            state = self.ping_check(self.admin["IP"])
            if state != self.admin["State"]:
                admin_state_change = True
            logging.info('Address: {}, Attempted ping: {}'.format(self.admin["IP"], self.admin["State"]))
            self.admin["State"] = state
            if admin_state_change:
                email = Emailer(self.admin["IP"], self.admin["State"], self.hosts)
                email.get_config()
                email.send()
            admin_state_change = False
            time.sleep(60 * 15)


if __name__ == "__main__":
    ping = Ping()
    ping.loop()
