'''
Created on 21 nov. 2011

@author: meego
'''
import ObsLightManager
import ConfigParser

class ObsLightConfig(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.__configParser = ConfigParser.ConfigParser()
        self.__configFile = open(ObsLightManager.getConfigPath(), 'rw')

        self.__configParser.readfp(self.__configFile)

def getConsole():
    '''
    Return the name of the term
    '''
    aConfigParser = ConfigParser.ConfigParser()
    aConfigFile = open(ObsLightManager.getConfigPath(), 'rw')

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
    aConfigFile = open(ObsLightManager.getConfigPath(), 'rw')

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
    aConfigFile = open(ObsLightManager.getConfigPath(), 'rw')

    aConfigParser.readfp(aConfigFile)
    if ('logger' in aConfigParser.sections()) and ('obslightgui' in aConfigParser.options('logger')):
        return aConfigParser.get('logger', 'obslightgui', raw=True)
    else:
        return u'%(asctime)s - %(name)s - %(levelname)s - %(message)s'



