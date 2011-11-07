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
from ObsLightYaml import ObsLightYaml
from ObsLightOsc import ObsLightOsc

import ObsLightPrintManager
from ObsLightSubprocess import SubprocessCrt

from ObsLightErr import ObsLightPackageErr

class ObsLightPackage(object):
    '''
    classdocs
    '''


    def __init__(self,
                 name="",
                 specFile=None,
                 yamlFile=None,
                 listFile=None,
                 status="Unknown",
                 fromSave=None):
        '''
        Constructor
        '''
        self.__mySubprocessCrt = SubprocessCrt()
        self.__yamlFile=None
        self.__specFile = None
        
        if fromSave == None:
            self.__name = name
            if listFile == None:
                self.__listFile = []
            else:
                self.__listFile = listFile
            self.__status = status
            self.__specFile = specFile
            self.__yamlFile = yamlFile
            self.__packageDirectory = None
        else:
            if "name" in fromSave.keys():
                self.__name = fromSave["name"]
            if "listFile" in fromSave.keys():
                self.__listFile = fromSave["listFile"]
            if "status" in fromSave.keys():
                self.__status = fromSave["status"]
            if "specFile" in fromSave.keys():
                self.__specFile = fromSave["specFile"]
            if "yamlFile" in fromSave.keys():
                self.__yamlFile = fromSave["yamlFile"]
            if "packageDirectory" in fromSave.keys():
                self.__packageDirectory = fromSave["packageDirectory"]
            if self.__status in [None,"None",""]:
                self.__status="Unknown"
            
        
        if not self.__yamlFile in (None,'None',""):
            self.__myYamlFile = ObsLightYaml(path=self.__yamlFile,specPath=self.__specFile)
            self.__mySpecFile = None
            if self.__specFile in (None,'None',""):
                self.__specFile = self.__myYamlFile.getSpecFile()
        else:
            self.__myYamlFile = None
            if not self.__specFile in (None,'None',""):    
                self.__mySpecFile = ObsLightSpec(self.__specFile)
            else:
                self.__mySpecFile = None
            
    def update(self,status=None):
        '''
        
        '''
        if status not in [None,"","None"]:
            self.__status=status
            
    def __subprocess(self, command=None, waitMess=False):
        '''
        
        '''
        return self.__mySubprocessCrt.execSubprocess(command=command, waitMess=waitMess)
            
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
        aDic["yamlFile"] = self.__yamlFile
        aDic["packageDirectory"] = self.__packageDirectory
        return aDic
            
    def getStatus(self):
        '''
        return the Status of the package.
        '''
        return self.__status
            
    def getSpecFile(self):
        '''
        return the absolute path of the spec file or yaml.
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
        if self.__myYamlFile!=None:
            if self.__myYamlFile.addpatch(aFile) == 1:
                ObsLightPrintManager.obsLightPrint("WARNING: Patch already exist the yaml file will not be changed.")
        elif self.__mySpecFile!=None:
            if self.__mySpecFile.addpatch(aFile) == 1:
                ObsLightPrintManager.obsLightPrint("WARNING: Patch already exist the spec file will not be changed.")
        else:
            raise ObsLightPackageErr("No Spec or Yaml in the package")
          
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
        if self.__myYamlFile!=None:
            self.__myYamlFile.save()
        elif self.__mySpecFile!=None:
            self.__mySpecFile.save()
        else:
            raise ObsLightPackageErr("No Spec or Yaml in the package")
        

    def addFileToSpec(self, baseFile=None, aFile=None):
        '''
        Add a delete command of a aFile to the spec aFile.
        '''
        if self.__myYamlFile!=None:
            return self.__myYamlFile.addFile(baseFile=baseFile, aFile=aFile)
        elif self.__mySpecFile!=None:
            return self.__mySpecFile.addFile(baseFile=baseFile, aFile=aFile)
        else:
            raise ObsLightPackageErr("No Spec or Yaml in the package") 
            
    def delFileToSpec(self, aFile=None):
        '''
        Add a delete command of a aFile to the spec aFile.
        '''
        if self.__myYamlFile!=None:
            return self.__myYamlFile.delFile(aFile=aFile)
        elif self.__mySpecFile!=None:
            return self.__mySpecFile.delFile(aFile=aFile)
        else:
            raise ObsLightPackageErr("No Spec or Yaml in the package") 
    
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

    def destroy(self):
        '''
        
        '''
        return self.__subprocess(command="rm -r  " + self.getOscDirectory())
    
    
    
    
