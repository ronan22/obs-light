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

def setConsole(consoleCommand):
    print "setConsole %s" % consoleCommand
    aConfigParser = ConfigParser.ConfigParser()
    with open(CONFIGPATH, 'r') as aConfigFile:
        aConfigParser.readfp(aConfigFile)
    if not aConfigParser.has_section('editor'):
        aConfigParser.add_section('editor')
    aConfigParser.set('editor', 'console', consoleCommand)
    with open(CONFIGPATH, 'w') as aConfigFile:
        aConfigParser.write(aConfigFile)

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


if not os.path.exists(CONFIGPATH):
    shutil.copy2(os.path.join(os.path.dirname(__file__), "config", OBSLIGHTCONFIG), CONFIGPATH)
    if os.path.exists("/usr/bin/konsole"):
        setConsole("/usr/bin/konsole -e")
    elif os.path.exists("/usr/bin/gnome-terminal"):
        setConsole("/usr/bin/gnome-terminal -x")
    #else keep default ("xterm -e")
