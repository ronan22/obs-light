'''
Created on 24 oct. 2011

@author: meego
'''
import logging
import ObsLightConfig
QUIET = 0
DEBUG = 0

logger = logging.getLogger('obslight')
handler = logging.StreamHandler()


logger.addHandler(handler)

def obsLightPrint(text, isDebug=False, isVerbose=False):
    '''
    
    '''
    if (isDebug == False) or (DEBUG > 0):
        logger.info(text)
    else:
        logger.debug(text)

def setLoggerLevel(level):
    '''
    Set the Level of the logger
    '''
    if level == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    elif level == 'INFO':
        logger.setLevel(logging.INFO)
    elif level == 'WARNING':
        logger.setLevel(logging.WARNING)
    elif level == 'ERROR':
        logger.setLevel(logging.ERROR)
    elif level == 'CRITICAL':
        logger.setLevel(logging.CRITICAL)

def addHandler(handler):
    '''
    Add a Handler to the logger
    '''
    logger.addHandler(handler)

def removeHandler(handler):
    '''
    Remove a Handler to the logger
    '''
    logger.removeHandler(handler)


formatter = logging.Formatter(ObsLightConfig.getObslightFormatter())
handler.setFormatter(formatter)
setLoggerLevel(ObsLightConfig.getObslightLoggerLevel())
addHandler(handler)

def getLogger():
    '''
        
    '''
    return logger
