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
        self.__packageFilter = {}
        self.__packageFilter_unload = {}
        self.__currentListPackageInfo = self.getDefaultListPackageInfo()

        if fromSave == None:
            self.__currentPackage = ""
        elif projectOscPath != None:
            for name in fromSave["savePackages"].keys():
                self.__dicOBSLightPackages[name] = ObsLightPackage(packagePath=os.path.join(projectOscPath, name),
                                                                   fromSave=fromSave["savePackages"][name])
            if "currentPackage" in fromSave.keys():
                self.__currentPackage = fromSave["currentPackage"]
            if "currentListPackageInfo" in fromSave.keys():
                self.__currentListPackageInfo = fromSave["currentListPackageInfo"]
            if "packageFilter" in fromSave.keys():
                self.__packageFilter = fromSave["packageFilter"]
        else:
            raise ObsLightErr.ObsLightPackageErr("Not projectOscPath for the ObsLightPackages init")

#-------------------------------------------------------------------------------
    def getPackage(self, package):
        '''
        
        '''
        if not package in self.__dicOBSLightPackages.keys():
            raise ObsLightErr.ObsLightPackageErr("No such package: " + str(package))

        self.__currentPackage = package

        return self.__dicOBSLightPackages[package]

    def getCurrentPackage(self):
        '''
        
        '''
        return self.__currentPackage

    def getDic(self):
        '''
        
        '''
        aDic = {}
        for pack in self.getListPackages():
            aDic[pack] = self.__dicOBSLightPackages[pack].getDic()

        saveconfigPackages = {}
        saveconfigPackages["savePackages"] = aDic
        saveconfigPackages["currentPackage"] = self.__currentPackage
        saveconfigPackages["currentListPackageInfo"] = self.__currentListPackageInfo
        saveconfigPackages["packageFilter"] = self.__packageFilter
        return saveconfigPackages


    def getListPackages(self):
        '''
        
        '''
        res = self.__dicOBSLightPackages.keys()
        res.sort()
        return res

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


    def delFromChroot(self, package):
        '''
        
        '''
        return self.__dicOBSLightPackages[package].delFromChroot()


    def getSpecFile(self, name=None):
        '''
        
        '''
        return self.__dicOBSLightPackages[name].getSpecFile()

    def getOscDirectory(self, name=None):
        '''
        
        '''
        return self.__dicOBSLightPackages[name].getOscDirectory()

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
    #---------------------------------------------------------------------------

    def getCurrentListPackageInfo(self):
        '''
        
        '''
        return self.__currentListPackageInfo

    def resetCurrentListPackageInfo(self):
        '''
        
        '''
        self.__currentListPackageInfo = self.getDefaultListPackageInfo()

    def getDefaultListPackageInfo(self):
        '''
        
        '''
        return ["obsRev", "oscRev", "status", "oscStatus", "chRootStatus"]

    #---------------------------------------------------------------------------


    def getPackageFilter(self):
        '''
        
        '''
        return self.__packageFilter

    def resetPackageFilter(self):
        '''
        
        '''
        self.__packageFilter = {}

    def removePackageFilter(self, key):
        '''
        
        '''
        if key in self.__packageFilter.keys():
            del self.__packageFilter[key]

    def addPackageFilter(self, key, val):
        '''
        
        '''
        self.__packageFilter[key] = val

    def getListStatus(self):
        '''
        
        '''
        return ["succeeded",
                "failed",
                "unresolvable",
                "broken",
                "blocked",
                "dispatching",
                "scheduled",
                "building",
                "signing",
                "finished",
                "disabled",
                "excluded",
                "Unknown"]

    def getListOscStatus(self):
        '''
        
        '''
        return ["Unknown", "inconsistent state", "Succeeded"]

    def getListChRootStatus(self):
        '''
        
        '''
        return ["Not installed", "No build directory", "Installed"]

    def __isFilterInfo(self, info):
        '''
        
        '''
        for k in self.__packageFilter:
            if k in info.keys():
                if (self.__packageFilter[k] != info[k]):
                    return False
        return True

    def getPackageInfo(self, package=None):
        '''
        
        '''
        res = {}
        if package == None:
            for pk in self.getListPackages():
                info = self.__dicOBSLightPackages[pk].getPackageInfo(self.getCurrentListPackageInfo())
                if self.__isFilterInfo(info):
                    res[pk] = info
        else:
            res[package] = self.__dicOBSLightPackages[package].getPackageInfo(self.getCurrentListPackageInfo())
        return res

    #---------------------------------------------------------------------------

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

    def getChrootRpmBuildDirectory(self, name):
        '''
        
        '''
        return self.__dicOBSLightPackages[name].getChrootRpmBuildDirectory()
