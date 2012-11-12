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
from ObsLightProjectCore import ObsLightProjectCore

import os
import shlex
import subprocess

from ObsLightUtils import getFilteredFileList, isASpecFile, levenshtein

from ObsLightChRoot import ObsLightChRoot
#import ObsLightManager
import ObsLightErr

import ObsLightConfig
import ObsLightTools

EMPTYSPECFILEPATH = os.path.join(os.path.dirname(__file__), "emptySpec", "emptySpec.spec")

class ObsLightProjectChroot(ObsLightProjectCore):

    def __init__(self,
                 obsLightRepositories,
                 workingDirectory,
                 projectLocalName=None,
                 projectArchitecture=None,
                 fromSave={}):
        ObsLightProjectCore.__init__(self,
                                 obsLightRepositories,
                                 workingDirectory,
                                 projectLocalName=projectLocalName,
                                 projectArchitecture=projectArchitecture,
                                 fromSave=fromSave)


        self.__chrootIsInit = fromSave.get("chrootIsInit", False)
        self.__chroot = ObsLightChRoot(projectDirectory=self.getDirectory())

        self.__nbJob = fromSave.get("nbJob", ObsLightTools.cpu_count())
        self.__chroot.setNbJob(self.__nbJob)

        if self.__chrootIsInit :
            if not self.__chroot.isInit():
                self.__chrootIsInit=False
#                        self.__chroot.initRepos()
        else:
            if self.__chroot.isInit():
                self.__chrootIsInit = True

        self._initPackage()
#            self.__extraChrootPackages = fromSave.get("extraChrootPackages", {})

#            if self.__chrootIsInit:
#                for packageName in self.__packages.getPackagesList():
#                    absPackagePath = self.getAbsPackagePath(name=packageName)
#                    if absPackagePath != None:
#                        if not os.path.isdir(absPackagePath) :
#                            self.addPackageSourceInChRoot(package=packageName)

    def getChroot(self):
        return self.__chroot

    def getProjectParameter(self, parameter):
        '''
        Get the value of a project parameter:
        the valid parameter is :
            chrootIsInit
        '''
        if parameter == "chrootIsInit":
            return self.__chrootIsInit
        else:
            return ObsLightProjectCore.getProjectParameter(self, parameter)


    def setProjectParameter(self, parameter, value):
        '''
        Return the value of a parameter of the project:
        Valid parameters are:
            chrootIsInit
        '''
        if parameter == "chrootIsInit":
            self.__chrootIsInit = value
        else:
            return ObsLightProjectCore.setProjectParameter(self, parameter, value)
        return 0

    def getDic(self):
        aDic = ObsLightProjectCore.getDic(self)
        aDic["chrootIsInit"] = self.__chrootIsInit
        aDic["nbJob"] = self.__nbJob
        return aDic

    def createRpmList(self, specFile):
        return None

    def __initChRoot(self):
        specFile = EMPTYSPECFILEPATH
        buildConfig = self.getbuildConfigPath()
        arch = self.getArchitecture()
        extraPackage = self.getExtraChrootPackagesList()

        rpmListFilePath = self.createRpmList(specFile)

        if rpmListFilePath is None:
            message = "Error Can't create chroot jail, no RPM list."
            raise ObsLightErr.ObsLightProjectsError(message)

        retVal = self.__chroot.createChRoot(rpmListFilePath,
                                            buildConfig,
                                            arch,
                                            specFile,
                                            self.getName())
        self.__chrootIsInit = (retVal == 0)
        return retVal


    def execScript(self, aPath):
        '''
        
        '''
        return self.__chroot.execScript(aPath)

    def openTerminal(self, package):
        '''
        Open bash in `package`'s chroot jail working directory.
        '''
        if package != None:
            packagePath = self._getPackages().getPackage(package).getPackageSourceDirectory()
            if packagePath != None:
                pathScript = self.__chroot.getChrootDirTransfert() + "/runMe.sh"
                title = "%s project directory" % package
                f = open(pathScript, 'w')
                f.write("#!/bin/sh\n")
                f.write("# Created by obslight\n")
                f.write("cd " + packagePath + "\n")
                # control code to change window title
                f.write('echo -en "\e]2;%s\a"\n' % title)
                f.write("exec bash\n")
                f.close()
                os.chmod(pathScript, 0755)
                command = ObsLightConfig.getConsole(title) + " " + pathScript

                command = shlex.split(str(command))
                # subprocess.call(command) would wait for the command to finish,
                # which would cause problem with terminal emulators which don't
                # fork themselves
                subprocess.Popen(command)

    def removeChRoot(self):
        '''
        Remove all package from chroot jail and remove it.      
        '''
        for package in self._getPackages().getPackagesList():
            pkgObj = self.getPackage(package)
            if pkgObj.isInstallInChroot():
                pkgObj.delFromChroot()

        res = self.__chroot.removeChRoot()
        self.__chrootIsInit = False
        return res

    def getChRoot(self):
        '''
        return the chroot obj.
        '''
        return self.__chroot

    def getChRootPath(self):
        '''
        Return the path of the chroot jail of a project.
        '''
        return self.__chroot.getDirectory()

    def isChRootInit(self):
        '''
        Return True if the ChRoot is init otherwise False.
        '''
        return self.__chrootIsInit

    def createChRoot(self):
        '''
        Initialize a chroot jail.
        Returns 0 on success. 
        '''
        return self.__initChRoot()

    def goToChRoot(self, package=None, useRootId=False, detach=False):
        if package != None:
            packagePath = self._getPackages().getPackage(package).getPackageChrootDirectory()

            if packagePath != None:
                return self.__chroot.goToChRoot(path=packagePath,
                                                useRootId=useRootId,
                                                detach=detach,
                                                project=self.getName())
            else:
                return self.__chroot.goToChRoot(detach=detach,
                                                project=self.getName(),
                                                useRootId=useRootId)
        else:
            return self.__chroot.goToChRoot(detach=detach,
                                            project=self.getName(),
                                            useRootId=useRootId)

    def removeProject(self):
        res = self.removeChRoot()

        if res == 0:
            ObsLightProjectCore.removeProject(self)
        else:
            message = "Error in removeProject, can't remove project file system"
            raise ObsLightErr.ObsLightProjectsError(message)

    def getChrootUserHome(self, fullPath=True):
        '''
        Return the abs Path of the user home into chroot jail. 
        '''
        return self.__chroot.getChrootUserHome(fullPath)

    def getAbsPackagePath(self, name):
        '''
        return the absolute path of a package install into chroot.
        return None if the package is not install.
        '''
        pkgObj = self._getPackages().getPackage(package)
        if pkgObj.isInstallInChroot():
            packageDirectory = pkgObj.getPackageChrootDirectory()
            if len(packageDirectory) > 0 and packageDirectory.startswith("/"):
                packageDirectory = packageDirectory[1:]
            return os.path.join(self.__chroot.getDirectory() , packageDirectory)
        else:
            return None

    def removePackage(self, package):
        '''
        Remove package into chroot, localy and all publish RPM.
        '''
        ObsLightProjectCore.removePackage(self, package)
        res = self.__chroot.removePackage(package)
        return res


