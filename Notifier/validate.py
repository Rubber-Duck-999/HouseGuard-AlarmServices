from datetime import datetime
import logging
from exceptions import BadDataError

def validate_temperature(data):
    logging.info('validate_temperature()')
    temp = {}
    try:
        temp = {
            "Humidity": data['humidity'],
            "TimeOfTemperature": datetime.now(),
            "Temperature": data['temp']
        }
    except KeyError as error:
        logging.error('Data was not valid on keys: {}'.format(error))
        raise BadDataError('Error found on JSON Dictionary')
    return temp

def validate_network(data):
    logging.info('validate_speed()')
    speed = {}
    try:
        speed = {
            "Upload": data['up'],
            "Download": data['down'],
            "TimeOfTest": datetime.now(),
        }
    except KeyError as error:
        logging.error('Data was not valid on keys: {}'.format(error))
        raise BadDataError('Error found on JSON Dictionary')
    return speed