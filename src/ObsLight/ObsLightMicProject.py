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
Created on jan 10 2012

@author: ronan@fridu.net
'''
import os
import ObsLightErr

class ObsLightMicProject(object):
    def __init_(self, workingDirectory, fromSave, importFile):
        '''
        
        '''
        self.__kickstartPath = None
        self.__architecture = None
        self.__imageType = None

    def getDic(self):
        '''
        
        '''
        return {}


    def addKickstartFile(self, filePath):
        '''
        
        '''
        if os.path.isfile(filePath):
            self.__kickstartPath = filePath
        else:
            raise ObsLightErr.ObsLightMicProjectErr("'" + filePath + "' is not a file.")

    def getKickstartFile(self, filePath):
        '''
        
        '''
        return self.__kickstartPath

    def getMicProjectArchitecture(self):
        '''
        
        '''
        return self.__architecture

    def setMicProjectArchitecture(self, arch):
        '''
        
        '''
        self.__architecture = arch

    def setMicProjectImageType(self, imageType):
        '''
        
        '''
        self.__imageType = imageType

    def getMicProjectImageType(self):
        '''
        
        '''
        return self.__imageType

    def createImage(self):
        '''
        
        '''
        pass
