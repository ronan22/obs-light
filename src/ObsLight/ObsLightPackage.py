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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
'''
Created on 30 sept. 2011

@author: ronan
'''
import os

from ObsLightSpec import ObsLightSpec

from ObsLightOsc import ObsLightOsc

class ObsLightPackage(object):
    '''
    classdocs
    '''


    def __init__(self, name="", specFile="", listFile=None, status="", fromSave=None):
        '''
        Constructor
        '''
        if fromSave == None:
            self.__name = name
            if listFile == None:
                self.__listFile = []
            self.__status = status
            self.__specFile = specFile
            self.__packageDirectory = None
        else:
            self.__name = fromSave["name"]
            self.__listFile = fromSave["listFile"]
            self.__status = fromSave["status"]
            self.__specFile = fromSave["specFile"]
            self.__packageDirectory = fromSave["packageDirectory"]
            
        self.__mySpecFile = ObsLightSpec(self.__specFile)
            
    def getName(self):
        '''
        return the name of the package.
        '''
        return self.__name

    def getDic(self):
        '''
        return a description of the object in a dictionary.
        '''
        aDic = {}
        aDic["name"] = self.__name
        aDic["listFile"] = self.__listFile
        aDic["status"] = self.__status
        aDic["specFile"] = self.__specFile
        aDic["packageDirectory"] = self.__packageDirectory
        return aDic
            
    def getStatus(self):
        '''
        return the Status of the package.
        '''
        return self.__status
            
    def getSpecFile(self):
        '''
        return the absolute path of the spec file.
        '''
        return self.__specFile
            
    def getOscDirectory(self):
        '''
        Return the absolute path of the osc directory of the package (base on the directory of the spec file).
        '''
        return os.path.dirname(self.__specFile)
            
    def setDirectoryBuild(self, packageDirectory=None):
        '''
        Set the directory of the package into the chroot.
        '''
        self.__packageDirectory = packageDirectory
        
    def getPackageDirectory(self):
        '''
        Return the directory of the package into the chroot.
        '''
        return self.__packageDirectory
    
    def addPatch(self, aFile=None):
        '''
        add a Patch aFile to package, the patch is automatically add to the spec aFile.
        '''
        self.__mySpecFile.addpatch(aFile)
        self.addFile(aFile)
    
    
    def addFile(self, aFile=None):
        '''
        Add a aFile to the package.
        '''
        self.__listFile.append(aFile)
    
    
    def save(self):
        '''
        Save the Spec file.
        '''
        self.__mySpecFile.save()
        
    
    def addFileToSpec(self, baseFile=None, aFile=None):
        '''
        Add a delete command of a aFile to the spec aFile.
        '''
        return self.__mySpecFile.addFile(baseFile=baseFile, aFile=aFile)
            
    def delFileToSpec(self, aFile=None):
        '''
        Add a delete command of a aFile to the spec aFile.
        '''
        return self.__mySpecFile.delFile(aFile=aFile)
     
    
    def commitToObs(self, message=None):
        '''
        commit the package to the OBS server.
        '''
        ObsLightOsc().commitProject(path=self.getOscDirectory(), message=message)
    
    def addRemoveFileToTheProject(self):
        '''
        add new file and remove file to the project.
        '''
        ObsLightOsc().addremove(path=self.getOscDirectory())

    
    
    
    
    
