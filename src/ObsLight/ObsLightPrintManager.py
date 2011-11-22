'''
Created on 24 oct. 2011

@author: meego
'''
import logging
import ObsLightConfig
VERBOSE = 0
DEBUG = 0

logger = logging.getLogger('obslight')

def obsLightPrint(text, isDebug=False, isVerbose=False):
    '''
    
    '''
    logger.debug(text)

def setLoggerLevel(level):
    '''
    Set the Level of the logger
    '''
    logger.setLevel(level)

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

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter(ObsLightConfig.getObslightFormatter())
ch.setFormatter(formatter)

setLoggerLevel(logging.DEBUG)
addHandler(ch)

def getLogger():
    '''
    
    '''
    return logger
