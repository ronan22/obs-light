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

class ObsLightPackage(object):
    '''
    classdocs
    '''


    def __init__(self,name="", specFile="", listFile=[], status="", fromSave=None):
        '''
        Constructor
        '''
        if fromSave==None:
            self.__name=name
            self.__listFile=listFile
            self.__status=status
            self.__specFile=specFile
            self.__packageDirectory=None
        else:
            self.__name=fromSave["name"]
            self.__listFile=fromSave["listFile"]
            self.__status=fromSave["status"]
            self.__specFile=fromSave["specFile"]
            self.__packageDirectory=fromSave["packageDirectory"]
            
        self.__mySpecFile=ObsLightSpec(self.__specFile)
            
    def getName(self):
        '''
        
        '''
        return self.__name

    def getDic(self):
        '''
        
        '''
        aDic={}
        aDic["name"]=self.__name
        aDic["listFile"]=self.__listFile
        aDic["status"]=self.__status
        aDic["specFile"]=self.__specFile
        aDic["packageDirectory"]=self.__packageDirectory
        return aDic
            
    def getStatus(self):
        '''
        
        '''
        return self.__status
            
    def getSpecFile(self):
        '''
        
        '''
        return self.__specFile
            
    def getOscDirectory(self):
        '''
        
        '''
        return os.path.dirname(self.__specFile)
            
    def setDirectoryBuild(self,packageDirectory=None):
        '''
        
        '''
        self.__packageDirectory=packageDirectory
        
    def getPackageDirectory(self):
        '''
        
        '''
        return self.__packageDirectory
    
    def addPatch(self,file=None):
        '''
    
        '''
        self.__mySpecFile.addpatch(file)
        self.addFile(file)
    
    
    def addFile(self,file=None):
        '''
    
        '''
        self.__listFile.append(file)
    
    
    def save(self):
        '''
        
        '''
        self.__mySpecFile.save()
        
    
    def addFileToSpec(self,baseFile=None,file=None):
        '''
        
        '''
        return self.__mySpecFile.addFile(baseFile=baseFile,file=file)
            
    def delFileToSpec(self,file=None):
        '''
        
        '''    
        return self.__mySpecFile.delFile(file=file)
    
    
    