'''
Created on 24 oct. 2011

@author: meego
'''
import logging

VERBOSE = 0
DEBUG = 0

logger = logging.getLogger('obslight')

def obsLightPrint(text, isDebug=False, isVerbose=False):
    '''
    
    '''
    if ((VERBOSE == 1) and (isVerbose == 1)) or\
       ((DEBUG == 1) and (isDebug == 1)) or\
       (isDebug == False) and (isVerbose == False):
        logger.debug(text)

def setLoggerLevel(level):
    '''
    
    '''
    logger.setLevel(level)

def addHandler(handler):
    '''
    
    '''
    logger.addHandler(handler)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

setLoggerLevel(logging.DEBUG)
addHandler(ch)

def getLogger():
    '''
    
    '''
    return logger
