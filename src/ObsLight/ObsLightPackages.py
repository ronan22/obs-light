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
from ObsLight import ObsLightErr
'''
Created on 30 sept. 2011

@author: ronan
'''
import os

from ObsLightPackage import ObsLightPackage

class ObsLightPackages(object):
    '''
    classdocs
    '''

    def __init__(self, projectOscPath=None, fromSave=None):
        '''
        Constructor
        '''
        self.__dicOBSLightPackages = {}


        if fromSave == None:
            self.__currentPackage = ""
        elif projectOscPath != None:
            for name in fromSave["savePackages"].keys():
                self.__dicOBSLightPackages[name] = ObsLightPackage(packagePath=os.path.join(projectOscPath, name),
                                                                   fromSave=fromSave["savePackages"][name])
            self.__currentPackage = fromSave["currentPackage"]
        else:
            raise ObsLightErr.ObsLightPackageErr("Not projectOscPath for the ObsLightPackages init")

    def getListPackages(self):
        '''
        
        '''
        res = self.__dicOBSLightPackages.keys()
        res.sort()
        return res

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
                   name,
                   packagePath,
                   description,
                   packageTitle,
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
                                                           packagePath=packagePath,
                                                           specFile=specFile,
                                                           description=description,
                                                           packageTitle=packageTitle,
                                                           yamlFile=yamlFile,
                                                           listFile=listFile,
                                                           status=status)

    def isInstallInChroot(self, name):
        '''
        Return True if the package is install into the chroot.
        '''
        return self.__dicOBSLightPackages[name].isInstallInChroot()

    def getGetChRootStatus(self, name):
        '''
        Return the status of the package  into the chroot.
        '''
        return self.__dicOBSLightPackages[name].getGetChRootStatus()

    def delFromChroot(self, package):
        '''
        
        '''
        return self.__dicOBSLightPackages[package].delFromChroot()

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


    def getPackage(self, package):
        '''
        
        '''
        if not package in self.__dicOBSLightPackages:
            raise ObsLightErr.ObsLightPackageErr("No such package: " + str(package))
        return self.__dicOBSLightPackages[package]

    def getPackageDirectory(self, package=None):
        '''
        
        '''
        return self.__dicOBSLightPackages[package].getPackageDirectory()

    def getPackageParameter(self, package, parameter=None):
        '''
        Get the value of a project parameter:
        the valid parameter is :
            name
            listFile
            status
            specFile
            yamlFile
            packageDirectory
            description
            packageTitle
        '''
        return self.__dicOBSLightPackages[package].getPackageParameter(parameter=parameter)

    def setPackageParameter(self, package, parameter, value):
        '''
        return the value  of the parameter of the package:
        the valid parameter is :
            specFile
            yamlFile
            packageDirectory
            description
            packageTitle
        '''
        return self.__dicOBSLightPackages[package].setPackageParameter(parameter=parameter, value=value)

    def removePackage(self, package=None):
        '''
        
        '''
        self.__dicOBSLightPackages[package].destroy()
        del self.__dicOBSLightPackages[package]
        return 0

    def updatePackage(self, name, status=None):
        '''
        
        '''
        self.__dicOBSLightPackages[name].update(status=status)


    def addFile(self, package, path):
        '''
        
        '''
        self.__dicOBSLightPackages[package].addFile(path)
    def delFile(self, package, name):
        '''
        
        '''
        self.__dicOBSLightPackages[package].delFile(name)


