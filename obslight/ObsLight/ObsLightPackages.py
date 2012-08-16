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
Created on 30 sept. 2011

@author: ronan
'''
from ObsLight import ObsLightErr

import os


NOT_INSTALLED = "Not installed"
NO_BUILD_DIRECTORY = "No build directory"
NO_BUILD_SECTION = "No build section"
MANY_BUILD_DIRECTORIES = "Many BUILD directories"
PREPARED = "Prepared"
BUILD = "Built"
BUILD_INSTALLED = "Build Installed"
BUILD_PACKAGED = "Build Packaged"

from ObsLightPackage import ObsLightPackage


class ObsLightPackages(object):
    '''
    classdocs
    '''

    def __init__(self, chrootUserHome=None, projectOscPath=None, fromSave=None):
        '''
        Constructor
        '''
        self.__dicOBSLightPackages = {}
        self.__packageFilter = {}
        self.__packageFilter_unload = {}
        self.__currentListPackageInfo = self.getDefaultListPackageInfo()

        if fromSave == None:
            self.__currentPackage = ""
        elif (projectOscPath != None):
            for name in fromSave["savePackages"].keys():
                package = ObsLightPackage(packagePath=os.path.join(projectOscPath, name),
                                          chrootUserHome=chrootUserHome,
                                          fromSave=fromSave["savePackages"][name])
                self.__dicOBSLightPackages[name] = package
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

    def addPackage(self,
                   name,
                   packagePath,
                   description,
                   chrootUserHome,
                   packageTitle,
                   specFile=None,
                   listFile=None,
                   status="",
                   existsOnServer=True):
        '''
        
        '''
        listFile = listFile or []
        self.__currentPackage = name
        if listFile == None:
            listFile = []

        if not name in  self.__dicOBSLightPackages.keys():
            self.__dicOBSLightPackages[name] = ObsLightPackage(name=name,
                                                               packagePath=packagePath,
                                                               chrootUserHome=chrootUserHome,
                                                               specFile=specFile,
                                                               description=description,
                                                               packageTitle=packageTitle,
                                                               listFile=listFile,
                                                               status=status,
                                                               existsOnServer=existsOnServer)
        else:
            message = "Can't add package '" + name + "' ,already exist in project."
            raise ObsLightErr.ObsLightPackageErr(message)

    def removePackage(self, package=None):
        '''
        
        '''
        self.getPackage(package).destroy()
        del self.__dicOBSLightPackages[package]
        if self.__currentPackage == package:
            self.__currentPackage = None
        return 0

#-------------------------------------------------------------------------------


    def removePackageFilter(self, key):
        '''
        
        '''
        if key in self.__packageFilter.keys():
            del self.__packageFilter[key]


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

#    def isInstallInChroot(self, name):
#        '''
#        Return True if the package is install into the chroot.
#        '''
#        return self.getPackage(name).isInstallInChroot()

    def delFromChroot(self, package):
        '''
        
        '''
        return self.getPackage(package).delFromChroot()

    def getSpecFile(self, name=None):
        '''
        
        '''
        return self.getPackage(name).getSpecFile()

    def getOscDirectory(self, name=None):
        '''
        
        '''
        return self.getPackage(name).getOscDirectory()

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
        return [NOT_INSTALLED,
                NO_BUILD_DIRECTORY,
                NO_BUILD_SECTION,
                MANY_BUILD_DIRECTORIES,
                PREPARED,
                BUILD,
                BUILD_INSTALLED,
                BUILD_PACKAGED]

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
                info = self.getPackage(pk).getPackageInfo(self.getCurrentListPackageInfo())
                if self.__isFilterInfo(info):
                    res[pk] = info
        else:
            res[package] = self.getPackage(package).getPackageInfo(self.getCurrentListPackageInfo())
        return res

    #---------------------------------------------------------------------------

    def updatePackage(self, name, status=None):
        '''
        
        '''
        self.getPackage(name).update(status=status)


    def getChrootRpmBuildDirectory(self, name):
        '''
        
        '''
        return self.getPackage(name).getChrootRpmBuildDirectory()
