import os
import requests
import logging

class Api:
    
    def __init__(self, server):
        '''Constructor for API'''
        self.server = server

    def check_alarm(self):
        '''Check alarm status'''
        status = True
        try:
            response = requests.get(self.server.format('alarm'), timeout=5)
            if response.status_code == 200:
                logging.info("Requests successful")
                data = response.json()
                val_status = data['data']['status']
                if val_status == 0:
                    status = False
            else:
                logging.error('Requests unsuccessful')
        except requests.ConnectionError as error:
            logging.error("Connection error: {}".format(error))
        except requests.Timeout as error:
            logging.error("Timeout on server: {}".format(error))
        except KeyError as error:
            logging.error("Key error on data: {}".format(error))
        return status


    def publish_data(self, filename):
        '''Send data to server if asked'''
        try:
            data = {
                'image': filename
            }
            response = requests.post(self.server.format('motion'), json=data, timeout=5)
            if response.status_code == 200:
                logging.info("Requests successful")
                logging.info('Response: {}'.format(response))
                os.remove(filename)
            else:
                logging.error('Requests unsuccessful')
        except requests.ConnectionError as error:
            logging.error("Connection error: {}".format(error))
        except requests.Timeout as error:
            logging.error("Timeout on server: {}".format(error))
        except OSError:
            logging.error("File couldn't be removed")