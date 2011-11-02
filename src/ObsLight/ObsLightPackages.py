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
from ObsLightPackage import ObsLightPackage

class ObsLightPackages(object):
    '''
    classdocs
    '''


    def __init__(self, fromSave=None):
        '''
        Constructor
        '''
        self.__dicOBSLightPackages = {}
        
        
        if fromSave == None:
            self.__currentPackage = ""
        else:

            for name in fromSave["savePackages"].keys():
                self.__dicOBSLightPackages[name] = ObsLightPackage(fromSave=fromSave["savePackages"][name])
            self.__currentPackage = fromSave["currentPackage"]

    def getListPackages(self):
        '''
        
        '''
        return self.__dicOBSLightPackages.keys()
    
    def getDic(self):
        '''
        
        '''
        aDic = {}
        for pack in self.getListPackages():
            aDic[pack] = self.__dicOBSLightPackages[pack].getDic()
        
        saveconfigPackages = {}    
        saveconfigPackages["savePackages"] = aDic
        saveconfigPackages["currentPackage"] = self.__currentPackage
        
        
        return saveconfigPackages
        
        
    def addPackage(self,
                   name=None,
                   specFile=None,
                   yamlFile=None,
                   listFile=None,
                   status=""):
        '''
        
        '''
        self.__currentPackage = name
        if listFile == None:
            listFile = []
        
        self.__dicOBSLightPackages[name] = ObsLightPackage(name=name,
                                                           specFile=specFile,
                                                           yamlFile=yamlFile,
                                                           listFile=listFile,
                                                           status=status)
        
        
    def getPackageStatus(self, name=None):
        '''
        
        '''
        return self.__dicOBSLightPackages[name].getStatus()
        
    def getSpecFile(self, name=None):
        '''
        
        '''
        return self.__dicOBSLightPackages[name].getSpecFile()
        
    def getOscDirectory(self, name=None):
        '''
        
        '''
        return self.__dicOBSLightPackages[name].getOscDirectory()
        
        
    def getPackage(self, package=None):
        '''
        
        '''
        return self.__dicOBSLightPackages[package]
    
    def getPackageDirectory(self, package=None):
        '''
        
        '''
        return self.__dicOBSLightPackages[package].getPackageDirectory()
        
    def removePackage(self,package=None):
        '''
        
        '''
        self.__dicOBSLightPackages[package].destroy()
        del self.__dicOBSLightPackages[package]
        return 0
        
         
        
