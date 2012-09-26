#
# Copyright 2011-2012, Intel Inc.
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
Created on 21 sept. 2012

@author: Ronan Le Martret 

'''
from ObsLightProjectChroot import ObsLightProjectChroot

import os

from ObsLightUtils import getFilteredFileList, isASpecFile, levenshtein
from ObsLightPackages import ObsLightPackages
from ObsLightChRoot import ObsLightChRoot
#import ObsLightManager
import ObsLightErr

from ObsLightObject import ObsLightObject

import ObsLightConfig

import ObsLightGitManager


class ObsLightBuilderProject(ObsLightProjectChroot):

    def __init__(self,
                 obsLightRepositories,
                 workingDirectory,
                 projectLocalName=None,
                 projectArchitecture=None,
                 fromSave={}):
        ObsLightProjectChroot.__init__(self,
                                       obsLightRepositories,
                                       workingDirectory,
                                       projectLocalName=projectLocalName,
                                       projectArchitecture=projectArchitecture,
                                       fromSave=fromSave)

    #--------------------------------------------------------------------------- build package
    def getProjectParameter(self, parameter=None):
        '''
        Get the value of a project parameter:
        the valid parameter is :

        '''
        return ObsLightProjectChroot.getProjectParameter(self, parameter)

    def setProjectParameter(self, parameter, value):
        '''
        Return the value of a parameter of the project:
        Valid parameters are:

        '''
        return ObsLightProjectChroot.setProjectParameter(self, parameter, value)

    def getDic(self):
        aDic = ObsLightProjectChroot.getDic(self)
        return aDic

    def __prepareChroot(self, section, pkgObj, specFileName):
        # First install the BuildRequires of the spec file.
        # The BuildRequires come from OBS.
        # We need a spec file parser to be OBS free.

        buildConfig = self.getbuildConfigPath()
        target = self.getArchHierarchy()
        extraPackage = self.getExtraChrootPackagesList()
        packageName = pkgObj.getName()

        rpmListFilePath = self.createRpmList(specFileName)

        res = self.getChroot().installBuildRequires(rpmListFilePath, target, buildConfig)

        if res != 0:
            raise ObsLightErr.ObsLightProjectsError("Can't install " + packageName)

        if section == "prep":
            res = self.getChroot().addPackageSourceInChRoot(pkgObj)
        return 0

    def __execRpmSection(self, packageName, section):
        """
        Execute `section` of the spec file of `packageName`
        into the chroot jail.
        """
        sectionMap = {"prep":  self.getChroot().prepRpm,
                      "build": self.getChroot().buildRpm,
                      "install": self.getChroot().installRpm,
                      "files": self.getChroot().packageRpm}

        pkgObj = self._getPackages().getPackage(packageName)

        specFileObj = pkgObj.getSpecObj()
        if specFileObj is None:
            raise ObsLightErr.ObsLightPackageErr("Package '%s' has no Spec file!" % packageName)
        specFileObj.parseFile()
        specFileName = pkgObj.getSpecFile()

        self.__prepareChroot(section, pkgObj, pkgObj.getSpecFile(fullPath=True))

        if pkgObj.getPackageParameter("patchMode") and section != "prep":
            _ = self.getChroot().prepGhostRpmbuild(pkgObj)

        archs = self.getArchHierarchy()
        buildDir = "/usr/lib/build"
        configdir = buildDir + "/configs"
        configPath = self.getBuildConfigPath()

        target = self.getTarget()
        specFilePath = self.getChroot().addPackageSpecInChRoot(pkgObj,
                                                               specFileName,
                                                               section,
                                                               configPath,
                                                               archs,
                                                               configdir,
                                                               buildDir)

        # If we don't remove default ACLs, some files created by the
        # Makefile of package may have wrong rights, and make the build fail.
        # (Was detected with "e2fsprogs")
        self.getChroot().forbidPackageAccessToObslightGroup(pkgObj)
        retVal = sectionMap[section](package=pkgObj,
                                     specFile=specFilePath,
                                     arch=target)
        self.getChroot().allowPackageAccessToObslightGroup(pkgObj)
        #publish RPM builded.
        if (section == "files") and pkgObj.isPackaged():
            buildRootpath = os.path.join(pkgObj.getChrootRpmBuildDirectory(), "RPMS")
            self.publishRPM(pkgObj, buildRootpath)

        return retVal

    def publishRPM(self, pkgObj, path):
        absBuildRootpath = self.getChroot().getDirectory() + path
        listRPM = []

        for arch in os.listdir(absBuildRootpath):
            for rpm in os.listdir(os.path.join(absBuildRootpath, arch)):
                listRPM.append(os.path.join(arch, rpm))

        repo = self.getRepositories().getRepository(self.getName())
        if len(listRPM) > 0:
            repo.removeRPM(pkgObj.getRPMPublished())
            pkgObj.setRPMPublished(listRPM)
            repo.addRPM(absBuildRootpath, listRPM)
            repo.createRepo()
        return 0

    def buildPrep(self, package):
        return self.__execRpmSection(package, "prep")

    def buildRpm(self, package):
        return self.__execRpmSection(package, "build")

    def installRpm(self, package):
        return self.__execRpmSection(package, "install")

    def packageRpm(self, package):
        return self.__execRpmSection(package, "files")

    #--------------------------------------------------------------------------- test build
    def importPrepBuildPackage(self, packageName):
        """
        Import the package in OBS Light, import it in chroot jail,
        execute %prep, then build RPMs.
        Returns 0 on success, != 0 or exception on failure.

        This function was developed for testing purposes.
        """
        if not self.isChRootInit():
            # Maybe we can create chroot jail in the calling function?
            self.logger.info("Creating chroot jail of project '%s'" % self.__projectLocalName)
            retVal = self.createChRoot()
            if retVal != 0:
                return retVal

        self.logger.info("Importing package '%s'" % packageName)
        # Does not return anything, will raise exception on error
        self.addPackage(packageName)

        self.logger.info("Preparing package '%s' in chroot jail" % packageName)
        retVal = self.buildPrep(packageName)
        if retVal != 0:
            return retVal

        self.logger.info("Building RPMs for '%s' in chroot jail" % packageName)
        retVal = self.packageRpm(packageName)
        if retVal != 0:
            return retVal
        self.logger.info("Deleting package '%s' as it builds correctly" % packageName)
        retVal = self.removePackage(packageName)
        return retVal

    def importPrepBuildPackages(self, packageNames=None):
        """
        Call `importPrepBuildPackage` for all packages of `packageNames`.
        If `packageNames` is None or an empty list, call `importPrepBuildPackage`
        for all packages of the project.

        Returns the list of packages which failed, as tuples of
        (packageName, exception) or (packageName, errorCode) depending
        on the type of failure.

        This function was developed for testing purposes.
        """
        failedPackages = list()
        if packageNames is None or len(packageNames) < 1:
            packageNames = self.getPackageList(False)
        for packageName in packageNames:
            try:
                retVal = self.importPrepBuildPackage(packageName)
                if retVal != 0:
                    failedPackages.append((packageName, retVal))
            except BaseException as be:
                failedPackages.append((packageName, be))
        return failedPackages

    #--------------------------------------------------------------------------- chroot jail
    def createPatch(self, package, patch):
        '''
        Create a patch
        '''
        return self.getChroot().createPatch(package=self._getPackages().getPackage(package),
                                         patch=patch)

    def updatePatch(self, package):
        '''
        Update a patch
        '''
        return  self.getChroot().updatePatch(package=self._getPackages().getPackage(package))


