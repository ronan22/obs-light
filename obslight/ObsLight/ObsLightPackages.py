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

from ObsLightPackage import ObsLightPackage
from ObsLightPackageStatus import getPackageListID

class ObsLightPackages(object):

    def __init__(self, project, fromSave={}):
        self.__dicOBSLightPackages = {}
        self.__packageFilter_unload = {}

        self.__project = project
        self.__currentPackage = fromSave.get("currentPackage", "")

        for name in fromSave.get("savePackages", {}).keys():
            packageSave = fromSave["savePackages"][name]
            package = ObsLightPackage(self.__project,
                                      fromSave=packageSave)

            self.__dicOBSLightPackages[name] = package

        self.__currentListPackageInfo = self.getDefaultListPackageInfo()

#        self.__packageFilter = fromSave.get("packageFilter", {})
        self.__packageFilter = {}

#-------------------------------------------------------------------------------
    def getPackage(self, package):
        if not package in self.__dicOBSLightPackages.keys():
            raise ObsLightErr.ObsLightPackageErr("No such package: " + str(package))

        self.__currentPackage = package

        return self.__dicOBSLightPackages[package]

    def addPackage(self,
                   name,
                   packagePath,
                   packageGitPath,
                   ):

        if not name in  self.__dicOBSLightPackages.keys():
            self.__dicOBSLightPackages[name] = ObsLightPackage(self.__project,
                                                               name=name,
                                                               packagePath=packagePath,
                                                               packageGitPath=packageGitPath,
                                                               )
            self.__currentPackage = name
        else:
            message = "Can't add package '%s' ,already exist in project." % name
            raise ObsLightErr.ObsLightPackageErr(message)

    def removePackage(self, package=None):
        self.getPackage(package).destroy()
        del self.__dicOBSLightPackages[package]
        if self.__currentPackage == package:
            self.__currentPackage = None
        return 0

#-------------------------------------------------------------------------------
    def removePackageFilter(self, key):
        if key in self.__packageFilter.keys():
            del self.__packageFilter[key]

    def getCurrentPackage(self):
        return self.__currentPackage

    def getDic(self):
        aDic = {}
        for pack in self.getPackagesList():
            aDic[pack] = self.__dicOBSLightPackages[pack].getDic()

        saveconfigPackages = {}
        saveconfigPackages["savePackages"] = aDic
        saveconfigPackages["currentPackage"] = self.__currentPackage
        saveconfigPackages["currentListPackageInfo"] = self.__currentListPackageInfo
        saveconfigPackages["packageFilter"] = self.__packageFilter
        return saveconfigPackages

    def getPackagesList(self):
        res = self.__dicOBSLightPackages.keys()
        res.sort()
        return res

#    def isInstallInChroot(self, name):
#        '''
#        Return True if the package is install into the chroot.
#        '''
#        return self.getPackage(name).isInstallInChroot()

    #--------------------------------------------------------------------------- package status

    def getCurrentListPackageInfo(self):
        return self.__currentListPackageInfo

    def resetCurrentListPackageInfo(self):
        self.__currentListPackageInfo = self.getDefaultListPackageInfo()

    def getDefaultListPackageInfo(self):
        return getPackageListID()

    def getPackageFilter(self):
        return self.__packageFilter

    def resetPackageFilter(self):
        self.__packageFilter = {}

    def addPackageFilter(self, key, val):
        self.__packageFilter[key] = val

#    def getStatusList(self):
#        return OBS_SERVER_STATUS

#    def getOscStatusList(self):
#        return LOCAL_STATUS


#    def getListChRootStatus(self):
#        return listChRootStatus

    def __isFilterInfo(self, info):
        for k in self.__packageFilter:
            if k in info.keys():
                if (self.__packageFilter[k] != info[k]):
                    return False
        return True

    def getPackageInfo(self, package=None):
        res = {}
        if package == None:
            for pk in self.getPackagesList():
                info = self.getPackage(pk).getPackageInfo(self.getCurrentListPackageInfo())
                if self.__isFilterInfo(info):
                    res[pk] = info
        else:
            res[package] = self.getPackage(package).getPackageInfo(self.getCurrentListPackageInfo())
        return res

    #---------------------------------------------------------------------------
#    def updatePackage(self, name, status=None):
#        self.getPackage(name).update(status=status)

