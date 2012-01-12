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
import shutil
from ObsLightSubprocess import SubprocessCrt

class ObsLightMicProject(object):
    def __init__(self, workingDirectory, fromSave, importFile, name=None):
        '''
        
        '''
        self.__mySubprocessCrt = SubprocessCrt()

        self.__kickstartPath = None
        self.__architecture = None
        self.__imageType = None
        self.__name = name
        self.__workingDirectory = workingDirectory + "/" + self.__name

        if fromSave != None:
            if "kickstartPath" in fromSave.keys():
                self.__kickstartPath = fromSave["kickstartPath"]
            if "architecture" in fromSave.keys():
                self.__architecture = fromSave["architecture"]
            if "imageType" in fromSave.keys():
                self.__imageType = fromSave["imageType"]
            if "name" in fromSave.keys():
                self.__name = fromSave["name"]
            if "workingDirectory" in fromSave.keys():
                self.__workingDirectory = fromSave["workingDirectory"]

        if not os.path.isdir(self.getProjectDirectory()):
            os.makedirs(self.getProjectDirectory())

    def __subprocess(self, command=None, waitMess=False):
        '''
        
        '''
        return self.__mySubprocessCrt.execSubprocess(command=command,
                                                     waitMess=waitMess)

    def getProjectDirectory(self):
        '''
        
        '''
        return self.__workingDirectory

    def getDic(self):
        '''
        
        '''
        aDic = {}
        aDic["kickstartPath"] = self.__kickstartPath
        aDic["architecture"] = self.__architecture
        aDic["imageType"] = self.__imageType
        aDic["name"] = self.__name
        aDic["workingDirectory"] = self.__workingDirectory
        return aDic


    def addKickstartFile(self, filePath):
        '''
        
        '''
        if os.path.isfile(filePath):
            fileName = os.path.basename(filePath)
            self.__kickstartPath = self.getProjectDirectory() + "/" + fileName
            shutil.copy(filePath, self.__kickstartPath)
        else:
            raise ObsLightErr.ObsLightMicProjectErr("'" + filePath + "' is not a file.")

    def getKickstartFile(self):
        '''
        
        '''
        return self.__kickstartPath

    def delProject(self):
        '''
        
        '''
        shutil.rmtree(self.getProjectDirectory())

    def setMicProjectArchitecture(self, arch):
        '''
        
        '''
        self.__architecture = arch

    def getMicProjectArchitecture(self):
        '''
        
        '''
        return self.__architecture

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
        CMD = "sudo mic create " + self.__imageType + " " + self.__kickstartPath + " --logfile=" + self.__workingDirectory + "/buildLog --cachedir=" + self.__workingDirectory + "/cache --outdir=" + self.__workingDirectory + " --arch=" + self.__architecture + " --release=latest"
        print CMD
        self.__subprocess(command=CMD)

    def getAvailableImageType(self):
        '''
        TODO Add to Manager
        '''
        return ["i686", "armv8" ]

    def getAvailableArchitecture(self):
        '''
        TODO Add to Manager
        '''
        return ["fs", "livecd", "liveusb", "loop" , "raw" ]


    def runQemu(self):
        '''
        
        '''
        #TO TEST
        #"sudo qemu-system-x86_64 -hda meego-netbook-ia32-qemu-1.2.0-raw/meego-netbook-ia32-qemu-1.2.0-sda.raw -boot c -m 2048 -k fr -vnc :1"
        #vncviewer :1



