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
        self.__configFile = open(ObsLightManager.getManager().getConfigPath(), 'rw')

        self.__configParser.readfp(self.__configFile)

def getConsole():
    '''
    
    '''
    aConfigParser = ConfigParser.ConfigParser()
    aConfigFile = open(ObsLightManager.getManager().getConfigPath(), 'rw')

    aConfigParser.readfp(aConfigFile)
    if 'editor' in aConfigParser.sections():
        return aConfigParser.get('editor', 'console')
    else:
        return 'xterm -e'


