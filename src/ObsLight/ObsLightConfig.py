#
# Copyright 2011, Intel Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
'''
Created on 21 nov. 2011

@author: meego
'''
import ConfigParser
import os
import shutil
import re

from ObsLightTools import isNonEmptyString

OBSLIGHTDIRNAME = "OBSLight"
OBSLIGHTCONFIG = "ObslightConfig"

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

def getTemplateConfigPath():
    return os.path.join(os.path.dirname(__file__), "config", OBSLIGHTCONFIG)

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
    '''
    Set the editor/console option in config file to 'consoleCommand',
    with ConfigParser (so comments are removed...).
    '''
    aConfigParser = ConfigParser.ConfigParser()
    with open(CONFIGPATH, 'r') as aConfigFile:
        aConfigParser.readfp(aConfigFile)
    if not aConfigParser.has_section('editor'):
        aConfigParser.add_section('editor')
    aConfigParser.set('editor', 'console', consoleCommand)
    with open(CONFIGPATH, 'w') as aConfigFile:
        aConfigParser.write(aConfigFile)

def setConsole2(consoleCommand):
    '''
    Set the editor/console option in config file to 'consoleCommand',
    with a regular expression.
    '''
    with open(CONFIGPATH, 'r') as cfgFile:
        content = cfgFile.read()
    newContent = re.sub(r'(console\s*[=:]).*', r'\1%s' % consoleCommand, content)
    with open(CONFIGPATH, 'w') as cfgFile:
        cfgFile.write(newContent)

def getOpenFileCommand():
    aConfigParser = ConfigParser.ConfigParser()
    with open(CONFIGPATH, 'r') as aConfigFile:
        aConfigParser.readfp(aConfigFile)
    command = ""
    if (aConfigParser.has_section('editor') and
            aConfigParser.has_option('editor', 'openFile')):
        command = aConfigParser.get('editor', 'openFile')
    if isNonEmptyString(command):
        return command
    else:
        return None

def setOpenFileCommand(command):
    with open(CONFIGPATH, 'r') as cfgFile:
        content = cfgFile.read()
    aConfigParser = ConfigParser.ConfigParser()
    with open(CONFIGPATH, 'r') as aConfigFile:
        aConfigParser.readfp(aConfigFile)
    if not aConfigParser.has_section('editor'):
        content += "\n[editor]\nopenFile=\n"
    newContent = re.sub(r'(openFile\s*[=:]).*', r'\1%s' % command, content)
    with open(CONFIGPATH, 'w') as cfgFile:
        cfgFile.write(newContent)

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

def getObslightLoggerLevel():
    '''
    return the level of the logger
    '''
    aConfigParser = ConfigParser.ConfigParser()
    aConfigFile = open(CONFIGPATH, 'rw')

    aConfigParser.readfp(aConfigFile)
    if ('logger' in aConfigParser.sections()) and ('level' in aConfigParser.options('logger')):
        return aConfigParser.get('logger', 'level', raw=True)
    else:
        return u'INFO'


def configureConsole():
    if os.path.exists(u"/usr/bin/konsole"):
        setConsole2(u"/usr/bin/konsole -e")
    elif os.path.exists(u"/usr/bin/gnome-terminal"):
        setConsole2(u"/usr/bin/gnome-terminal -x")
    #else keep default ("xterm -e")

def configureOpenFile():
    if os.path.exists(u"/usr/bin/xdg-open"):
        setOpenFileCommand(u"/usr/bin/xdg-open")
    elif os.path.exists(u"/usr/bin/kde-open"):
        setOpenFileCommand(u"/usr/bin/kde-open")
    elif os.path.exists(u"/usr/bin/gnome-open"):
        setOpenFileCommand(u"/usr/bin/gnome-open")
    elif os.path.exists(u"/usr/bin/exo-open"):
        setOpenFileCommand(u"/usr/bin/exo-open")


if not os.path.exists(CONFIGPATH):
    shutil.copy2(getTemplateConfigPath(), CONFIGPATH)
    configureConsole()
    configureOpenFile()
