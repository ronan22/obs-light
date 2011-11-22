'''
Created on 21 nov. 2011

@author: meego
'''
import ConfigParser
import os
import shutil

OBSLIGHTDIRNAME = "OBSLight"
OBSLIGHTCONFIG = "obslightConfig"

WORKINGDIRECTORY = os.path.join(os.environ['HOME'], OBSLIGHTDIRNAME)
# If not exists, create the obsLight directory for the user.
if not os.path.isdir(WORKINGDIRECTORY):
    os.makedirs(WORKINGDIRECTORY)
CONFIGPATH = os.path.join(WORKINGDIRECTORY, OBSLIGHTCONFIG)
if not  os.path.exists(CONFIGPATH):
    shutil.copy2(os.path.join(os.path.dirname(__file__), "config", OBSLIGHTCONFIG), CONFIGPATH)

class ObsLightConfig(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.__configParser = ConfigParser.ConfigParser()
        self.__configFile = open(CONFIGPATH, 'rw')

        self.__configParser.readfp(self.__configFile)

def getConsole():
    '''
    Return the name of the term
    '''
    aConfigParser = ConfigParser.ConfigParser()
    aConfigFile = open(CONFIGPATH, 'rw')

    aConfigParser.readfp(aConfigFile)
    if ('editor' in aConfigParser.sections()) and ('console' in aConfigParser.options('editor')):
        return aConfigParser.get('editor', 'console')
    else:
        return 'xterm -e'

def getObslightFormatter():
    '''
    return the formatter for obslight
    '''
    aConfigParser = ConfigParser.ConfigParser()
    aConfigFile = open(CONFIGPATH, 'rw')

    aConfigParser.readfp(aConfigFile)
    if ('logger' in aConfigParser.sections()) and ('obslight' in aConfigParser.options('logger')):
        return aConfigParser.get('logger', 'obslight', raw=True)
    else:
        return '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

def getObsLightGuiFormatterString():
    '''
    return the formatter for obslightgui
    '''
    aConfigParser = ConfigParser.ConfigParser()
    aConfigFile = open(CONFIGPATH, 'rw')

    aConfigParser.readfp(aConfigFile)
    if ('logger' in aConfigParser.sections()) and ('obslightgui' in aConfigParser.options('logger')):
        return aConfigParser.get('logger', 'obslightgui', raw=True)
    else:
        return u'%(asctime)s - %(name)s - %(levelname)s - %(message)s'



