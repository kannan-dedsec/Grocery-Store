import logging
import ConfigurationConstants
import uuid as random
import base64 as encoder
from ConfigurationConstants import LOG_FILE


logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format=ConfigurationConstants.LOGGER_FORMAT)

def getLogger():
    logger = logging.getLogger()
    return logger

def getRole(roleName):
    if roleName == "store":
        return 1
    else:
        return 2

def generateRandomID():
    return str(random.uuid4())

def encode(string):
    return encoder.b64encode(string.encode('utf-8')).decode('utf-8')

def decode(string):
    return encoder.b64decode(string.encode('utf-8')).decode('utf-8')
