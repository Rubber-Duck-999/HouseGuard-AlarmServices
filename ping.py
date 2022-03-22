import os
import logging
import json

file = ''
try:
    user = os.getlogin()
    file = '/{}/sync/ping.log'.format(user)
    os.remove(file)
except OSError as error:
    pass

# Add the log message handler to the logger
logging.basicConfig(filename=file,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logging.info("Starting program")

def get_settings():
    '''Get config env var'''
    logging.info('get_settings()')
    addresses = []
    try:
        username = os.getlogin()
        config_name = '/{}/sync/config.json'.format(username)
        with open(config_name) as file:
            data = json.load(file)
        addresses = data["ip_addresses"]
    except KeyError:
        logging.info("Variables not set")
    except FileNotFoundError:
        logging.info('File not found')
    except IOError:
        logging.info('Could not read file')
    return addresses

def ping_check(host):
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

if __name__ == "__main__":
    addresses = get_settings()
    for address in addresses:
        success = ping_check(address)
        logging.info('Attempted ping: {}'.format(success))