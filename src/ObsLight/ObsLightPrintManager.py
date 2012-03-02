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
Created on 24 oct. 2011

@author: meego
'''

import logging
import logging.handlers
import ObsLightConfig
QUIET = 0
DEBUG = 0

logger = logging.getLogger('obslight')
streamHandler = logging.StreamHandler()
fileHandler = logging.handlers.RotatingFileHandler(ObsLightConfig.getObsLightLogFilePath(),
                                                   maxBytes=10 * 2 ** 20, backupCount=1)

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
    try:
        intLevel = getattr(logging, str(level))
        logger.setLevel(intLevel)
    except AttributeError:
        # TODO: create custom exception
        raise

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
streamHandler.setFormatter(formatter)
setLoggerLevel(ObsLightConfig.getObslightLoggerLevel())
addHandler(streamHandler)

fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)

def getLogger():
    '''
        
    '''
    return logger
