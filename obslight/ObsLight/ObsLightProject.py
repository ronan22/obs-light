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

class ObsLightProject(ObsLightProjectCore):

    def __init__(self,
                 obsServers,
                 obsLightRepositories,
                 workingDirectory,
                 projectObsName=None,
                 projectLocalName=None,
                 obsServer=None,
                 projectTarget=None,
                 projectArchitecture=None,
                 projectTitle="",
                 description="",
                 fromSave={}):
        ObsLightProjectCore.__init__(self,
                                        obsLightRepositories,
                                        workingDirectory,
                                        projectLocalName=projectLocalName,
                                        projectArchitecture=projectArchitecture,
                                        fromSave=fromSave)

        self.__chrootIsInit = fromSave.get("chrootIsInit", False)
        self.__chroot = ObsLightChRoot(projectDirectory=self.getDirectory())

        if self.__chrootIsInit == True:
            if not self.__chroot.isInit():
                self.__initChRoot()
#                        self.__chroot.initRepos()
        else:
            if self.__chroot.isInit():
                self.__chrootIsInit = True

#            self.__extraChrootPackages = fromSave.get("extraChrootPackages", {})

#            if self.__chrootIsInit:
#                for packageName in self.__packages.getPackagesList():
#                    absPackagePath = self.getAbsPackagePath(name=packageName)
#                    if absPackagePath != None:
#                        if not os.path.isdir(absPackagePath) :
#                            self.addPackageSourceInChRoot(package=packageName)

    def getProjectParameter(self, parameter=None):
        '''
        Get the value of a project parameter:
        the valid parameter is :
            projectLocalName
            projectObsName
            projectDirectory
            obsServer
            projectTarget
            projectArchitecture
            title
            description
        '''
        if parameter == "projectLocalName":
            return self.__projectLocalName
        elif parameter == "projectObsName":
            return self.__projectName
        elif parameter == "projectDirectory":
            return self.getDirectory()
        elif parameter == "obsServer":
            return self.__obsServer
        elif parameter == "projectTarget":
            return self.__projectTarget
        elif parameter == "projectArchitecture":
            return self.__projectArchitecture
        elif parameter == "title":
            return self.__projectTitle
        elif parameter == "description":
            return self.__description
        else:
            message = "parameter value is not valid for getProjectParameter"
            raise ObsLightErr.ObsLightProjectsError(message)

    def setProjectParameter(self, parameter=None, value=None):
        '''
        Return the value of a parameter of the project:
        Valid parameters are:
            projectTarget
            projectArchitecture
            title
            description
        '''
        if parameter == "projectTarget":
            self.__projectTarget = value
        elif parameter == "projectArchitecture":
            self.__projectArchitecture = value
        elif parameter == "title":
            self.__projectTitle = value
        elif parameter == "description":
            self.__description = value
        else:
            message = "parameter '%s' is not valid for setProjectParameter" % parameter
            raise ObsLightErr.ObsLightProjectsError(message)
        return 0

    def getDic(self):
        aDic = ObsLightProjectCore.getDic(self)
        aDic["chrootIsInit"] = self.__chrootIsInit
        return aDic

    def execScript(self, aPath):
        return self.__chroot.execScript(aPath)

    def openTerminal(self, package):
        '''
        Open bash in `package`'s osc working directory.
        '''
        if package != None:
            packagePath = self.__packages.getPackage(package).getPackageChrootDirectory()
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
        for package in self.__packages.getPackagesList():
            pkgObj = self.getPackage(package)
            if pkgObj.isInstallInChroot():
                pkgObj.delFromChroot()

        res = self.__chroot.removeChRoot()
        self.__chrootIsInit = False
        return res

    def getChRoot(self):
        return self.__chroot

    def getChRootPath(self):
        '''
        Return the path of aChRoot of a project
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

    def __initChRoot(self):
        apiurl = self.__obsServers.getObsServer(self.__obsServer).getAPI()
        retVal = self.__chroot.createChRoot(repos=self.__projectTarget,
                                            arch=self.__projectArchitecture,
                                            apiurl=apiurl,
                                            obsProject=self.__projectName)
        self.__chrootIsInit = retVal == 0
        return retVal

    def goToChRoot(self, package=None, useRootId=False, detach=False):
        if package != None:
            packagePath = self.__packages.getPackage(package).getPackageSourceDirectory()
            if packagePath != None:
                return self.__chroot.goToChRoot(path=packagePath,
                                                useRootId=useRootId,
                                                detach=detach,
                                                project=self.__projectLocalName)
            else:
                return self.__chroot.goToChRoot(detach=detach,
                                                project=self.__projectLocalName,
                                                useRootId=useRootId)
        else:
            return self.__chroot.goToChRoot(detach=detach,
                                            project=self.__projectLocalName,
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
        pkgObj = self.__packages.getPackage(package)
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

    def autoDisableExtraChrootPackages(self, packageName, specFileName):
        """Checks if extra packages are available, and enable/disable them accordingly"""
        obsServer = self.__obsServers.getObsServer(self.__obsServer)
        extraPackages = set(self.__extraChrootPackages)
        gotError = True
        while(gotError and len(extraPackages) > 0):
            try:
                buildInfoCli = obsServer.getPackageBuildRequires(self.__projectName,
                                                                 packageName,
                                                                 self.__projectTarget ,
                                                                 self.__projectArchitecture,
                                                                 specFileName,
                                                                 list(extraPackages))
                gotError = False
            except ObsLightErr.ObsLightOscErr as e:
                gotError = True
                toBeRemoved = set()
                for p in extraPackages:
                    if e.msg.find(p) >= 0:
                        toBeRemoved.add(p)

                extraPackages.difference_update(toBeRemoved)
        for p in self.__extraChrootPackages.keys():
            self.__extraChrootPackages[p] = p in extraPackages
