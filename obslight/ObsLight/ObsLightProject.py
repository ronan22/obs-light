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
Created on 29 sept. 2011

@author: ronan
@author: Florent Vennetier
'''
import os
import shlex
import shutil
import subprocess
import urllib

from ObsLightUtils import getFilteredFileList, isASpecFile, levenshtein
from ObsLightPackages import ObsLightPackages
from ObsLightChRoot import ObsLightChRoot
#import ObsLightManager
import ObsLightErr
from ObsLightSubprocess import SubprocessCrt
from ObsLightObject import ObsLightObject
import ObsLightOsc

import ObsLightConfig

import ObsLightGitManager
from ObsLightSpec import getSpecTagValue

class ObsLightProject(ObsLightObject):

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
        ObsLightObject.__init__(self)
        self.__mySubprocessCrt = SubprocessCrt()

        self.__obsServers = obsServers
        self.__obsLightRepositories = obsLightRepositories
        self.__chrootIsInit = fromSave.get("chrootIsInit", False)
        self.__WorkingDirectory = workingDirectory
        self.__projectTitle = fromSave.get("title", "")

        # package name as key, install/don't install as value
        self.__extraChrootPackages = {"vim": False, "emacs": False, "strace": False}

        self.__projectLocalName = fromSave.get("projectLocalName", projectLocalName)
        self.__chroot = ObsLightChRoot(projectDirectory=self.getDirectory())

        self.__projectName = fromSave.get("projectObsName", projectObsName)

        self.__obsServer = fromSave.get("obsServer", obsServer)

        self.__projectTarget = fromSave.get("projectTarget", projectTarget)

        if not (self.__obsServer in self.__obsServers.getObsServerList()):
                    message = "WARNING: '%s' is not a defined OBS server " % self.__obsServer
                    self.logger.warn(message)
        #perhaps a trusted_prj must be had
        else:
            obsServer = self.__obsServers.getObsServer(name=self.__obsServer)
            obsServer.initConfigProject(projet=self.__projectName, repos=self.__projectTarget)


        self.__projectArchitecture = fromSave.get("projectArchitecture", projectArchitecture)
        self.__description = fromSave.get("description", description)

        self.__packages = ObsLightPackages(self, fromSave.get("packages", {}))

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

        if not os.path.isdir(self.getDirectory()):
            os.makedirs(self.getDirectory())

        self.__configPath = None

        # Taken from /usr/lib/build/common_functions
        self.__archHierarchyMap = {}
        self.__archHierarchyMap["i686"] = "i686:i586:i486:i386"
        self.__archHierarchyMap["i586"] = "i586:i486:i386"
        self.__archHierarchyMap["i486"] = "i486:i386"
        self.__archHierarchyMap["i386"] = "i386"
        self.__archHierarchyMap["x86_64"] = "x86_64:i686:i586:i486:i386"
        self.__archHierarchyMap["sparc64v"] = "sparc64v:sparc64:sparcv9v:sparcv9:sparcv8:sparc"
        self.__archHierarchyMap["sparc64"] = "sparc64:sparcv9:sparcv8:sparc"
        self.__archHierarchyMap["sparcv9v"] = "sparcv9v:sparcv9:sparcv8:sparc"
        self.__archHierarchyMap["sparcv9"] = "sparcv9:sparcv8:sparc"
        self.__archHierarchyMap["sparcv8"] = "sparcv8:sparc"
        self.__archHierarchyMap["sparc"] = "sparc"


    #--------------------------------------------------------------------------- util

    def _subprocess(self, command=None, waitMess=False, stdout=False):
        return self.__mySubprocessCrt.execSubprocess(command=command,
                                                     waitMess=waitMess,
                                                     stdout=stdout)

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

    #--------------------------------------------------------------------------- project
    def __getArchHierarchy(self):
        if self.__projectArchitecture in self.__archHierarchyMap:
            return self.__archHierarchyMap[self.__projectArchitecture]
        else:
            return self.__projectArchitecture

    def __getConfigPath(self):
        if self.__configPath is None:
            obsServer = self.__obsServers.getObsServer(self.__obsServer)
            self.__configPath = obsServer.saveProjectConfig(self.__projectName,
                                                            self.__projectTarget)

        return self.__configPath

    def getChrootUserHome(self, fullPath=True):
        '''
        Return the abs Path of the user home into chroot jail. 
        '''
        return self.__chroot.getChrootUserHome(fullPath)

    def __getTarget(self):
        """
        Get the 'target' string to be passed to rpmbuild.
        Looks like 'i586-tizen-linux'.
        """
        archs = self.__getArchHierarchy()

        buildDir = "/usr/lib/build"
        configdir = buildDir + "/configs"

        configPath = self.__getConfigPath()
        command = '%s/getchangetarget --dist "%s" --configdir "%s" --archpath "%s"'
        command = command % (buildDir, configPath, configdir, archs)

        target = self._subprocess(command, stdout=True)
        self.logger.debug("Target found by getchangetarget: '%s'" % target)

        endline = "\n"
        if target.endswith("\n"):
            target = target[:-len(endline)]

        return target

    def addRemoveFileToTheProject(self, package=None):
        '''
        add new file and remove file to the project.
        '''
        self.__packages.getPackage(package).addRemoveFileToTheProject()


    def getWebProjectPage(self):
        serverWeb = self.__obsServers.getObsServer(name=self.__obsServer).getUrlServerWeb()

        if serverWeb in (None, "None", ""):
            raise ObsLightErr.ObsLightProjectsError("No Web Server")
        res = urllib.basejoin(serverWeb , "project/show?project=" + self.__projectName)
        return res


    def getDirectory(self):
        '''
        Return the project directory.
        '''
        return os.path.join(self.__WorkingDirectory, self.__projectLocalName)

    def removeProject(self):
        self.removeLocalRepo()
        res = self.removeChRoot()

        if res == 0:
            drctr = self.getDirectory()
            if os.path.isdir(drctr):
                try:
                    return shutil.rmtree(drctr)
                except:
                    message = "Error in removeProject, can't remove directory, '%s'" % drctr
                    raise ObsLightErr.ObsLightProjectsError(message)
            else:
                self.logger.warn("'%s' is not a directory" % drctr)
                return 0
        else:
            message = "Error in removeProject, can't remove project file system"
            raise ObsLightErr.ObsLightProjectsError(message)


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
        aDic = {}
        aDic["projectLocalName"] = self.__projectLocalName
        aDic["projectObsName"] = self.__projectName
        aDic["obsServer"] = self.__obsServer
        aDic["projectTarget"] = self.__projectTarget
        aDic["projectArchitecture"] = self.__projectArchitecture
        aDic["title"] = self.__projectTitle
        aDic["description"] = self.__description
        aDic["packages"] = self.__packages.getDic()
        aDic["chrootIsInit"] = self.__chrootIsInit
#        aDic["extraChrootPackages"] = self.__extraChrootPackages
        return aDic

#    def updateProject(self):
#        server = self.__obsServers.getObsServer(self.__obsServer)
#        for name in self.__packages.getPackagesList():
#            status = server.getPackageStatus(project=self.__projectName,
#                                             package=name,
#                                             repo=self.__projectTarget,
#                                             arch=self.__projectArchitecture)
#            self.__packages.updatePackage(name=name, status=status)

    #---------------------------------------------------------------------------package status
    def getPackageInfo(self, package=None):
        return self.__packages.getPackageInfo(package=package)

    def getPackageFilter(self):
        return self.__packages.getPackageFilter()

    def resetPackageFilter(self):
        return self.__packages.resetPackageFilter()

    def removePackageFilter(self, key):
        return self.__packages.removePackageFilter(key=key)

    def addPackageFilter(self, key, val):
        return self.__packages.addPackageFilter(key=key, val=val)

#    def getListOscStatus(self):
#        return self.__packages.getListOscStatus()

#    def getListStatus(self):
#        return self.__packages.getListStatus()

#    def getListChRootStatus(self):
#        return self.__packages.getListChRootStatus()

    def refreshPackageDirectoryStatus(self, package=None):
        def doUpDatePackage(package):
            self.updatePackage(name=package)
#            self.refreshPackageDirectoryStatus(package)
#            self.__packages.getPackage(package).initPackageFileInfo()
#            self.__refreshOscPackageLocalRev(package)

        if package != None:
            doUpDatePackage(package)
        else:
            for pkg in self.getPackageList():
                doUpDatePackage(pkg)
        return 0

#    def __refreshOscPackageLocalRev(self, package):
#        '''
#        Get the local rev of the "package".
#        rev come from an OBS Server and mean nothing for a git package.
#        '''
#        packageObj = self.__packages.getPackage(package)
#
#        if not packageObj.isGitPackage:
#            obsServer = self.__obsServers.getObsServer(self.__obsServer)
#            oscDirectory = packageObj.getPackageSourceDirectory()
#            rev = obsServer.getOscPackageRev(workingdir=oscDirectory)
#
#            if rev != None:
#                packageObj.setOscPackageRev(rev)
#            else:
#                packageObj.setOscPackageRev("-1")

#    def checkOscDirectoryStatus(self, package):
#        obsServer = self.__obsServers.getObsServer(self.__obsServer)
#        dicoListFile = obsServer.getFilesListPackage(projectObsName=self.__projectName,
#                                                     package=package)
#        if dicoListFile != None:
#            packageCli = self.__packages.getPackage(package)
#            listOscFile = packageCli.getPackageParameter(parameter="listFile")
#
#            for obsFile in dicoListFile.keys():
#                if (not obsFile in listOscFile) and (obsFile != "_link"):
#                    self.__packages.getPackage(package).setOscStatus("inconsistent state")
#                    return None
#            self.__packages.getPackage(package).setOscStatus("Succeeded")
#
#        return None

    #--------------------------------------------------------------------------- package 
    def commitPackageChange(self, message=None, package=None):
        '''
        commit the package to the OBS server or git.
        '''
        # test if package is a RW OBS package.
        pkgObj = self.__packages.getPackage(package)

        if not pkgObj.isGitPackage:
            server = self.__obsServers.getObsServer(self.__obsServer)
            if server.getProjectParameter(self.__projectName, "readonly"):
                message = "Can't commit project you are not maintainer on project."
                raise ObsLightErr.ObsLightProjectsError(message)

        #Do a package commit
        pkgObj.commitPackageChange(message=message)

        if not pkgObj.isGitPackage:
            #check 
#            self.checkOscDirectoryStatus(package=package)
#            self.__refreshOscPackageLocalRev(package=package)
            self.refreshObsStatus(package=package)

        return 0

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

    def __getGitPackagesDefaultDirectory(self):
        '''
        Return the package git directory of the local project.
        '''
        return os.path.join(self.getDirectory(), "gitWorkingTrees")

    def __getOscPackagesDefaultDirectory(self):
        '''
        Return the package Osc directory of the local project.
        '''
        return os.path.join(self.getDirectory(), self.__projectName)

#    def __addPackagesFromSave(self, fromSave):
#        '''
#        check and add a package from a save.
#        '''
#        for packageName in fromSave["savePackages"].keys():
#            packageFromSave = fromSave["savePackages"][packageName]
#            if "name" in packageFromSave.keys():
#                name = packageFromSave["name"]
#            packagePath = self.__getPackagePath(name)
#            if not os.path.isdir(packagePath):
#                packagePath, specFile = self.checkoutPackage(package=name)
#                packageFromSave["specFile"] = specFile
#                packageFromSave["listFile"] = listFile
#
#            if importFile == True:
#                toUpDate = False
#                if "listFile" in packageFromSave.keys():
#                    listFile = packageFromSave["listFile"]
#                for aFile in listFile:
#                    if not os.path.isfile(os.path.join(packagePath, aFile)):
#                        toUpDate = True
#                if "specFile" in packageFromSave.keys():
#                    specFilePath = packageFromSave["specFile"]
#                    if specFilePath is not None and not os.path.isfile(specFilePath):
#                        toUpDate = True
#                        
#                if toUpDate == True:
#                    ObsLightOsc.getObsLightOsc().updatePackage(packagePath=packagePath)
#
#            fromSave["savePackages"][packageName] = packageFromSave
#        return ObsLightPackages(fromSave=fromSave)

    def getPackageParameter(self, package, parameter=None):
        '''
        Get the value of a project parameter:
        the valid parameter is :
            name
            status
            specFile
            packageDirectory
            description
            title
        '''
        return self.__packages.getPackage(package).getPackageParameter(parameter=parameter)

    def setPackageParameter(self, package, parameter=None, value=None):
        '''
        return the value  of the parameter of the package:
        the valid parameter is :
            specFile
            packageDirectory
            description
            title
        '''
        return self.__packages.getPackage(package).setPackageParameter(parameter=parameter,
                                                                       value=value)

    def getCurrentPackage(self):
        return self.__packages.getCurrentPackage()

    def getPackageList(self, onlyInstalled=True):
        '''
        Get the list of packages of this project.
        If `onlyInstalled` is True, get only those which have been imported locally.
        '''
        if not onlyInstalled :
            if self.__obsServer in self.__obsServers.getObsServerList():
                obsServer = self.__obsServers.getObsServer(self.__obsServer)
                res1 = set(obsServer.getObsProjectPackageList(projectObsName=self.__projectName))
                res2 = set(self.__packages.getPackagesList())
                res = list(res1.difference(res2))
                res.sort()
                return res
            else:
                return  None
        else:
            res = self.__packages.getPackagesList()
            return res

    def getPackage(self, package=None):
        '''
        Return a package object.
        '''
        return  self.__packages.getPackage(package=package)

    def removePackage(self, package):
        '''
        Remove package into chroot, localy and all publish RPM.
        '''
        repo = self.__obsLightRepositories.getRepository(self.__projectLocalName)
        repo.removeRPM(self.getPackage(package).getRPMPublished())
        repo.createRepo()
        _ = self.__packages.removePackage(package=package)

        res = self.__chroot.removePackage(package)
        return res
#    def __createPackageFilesFromGit(self, gitTreePath, packagePath):
#        """
#        Create/update files of package at `packagePath` from a git tree
#        """
#
#        packagingDir = os.path.join(gitTreePath, "packaging")
#
#        # Create/clean package directory
#        if os.path.exists(packagePath):
#            # Remove all files except ".osc"
#            packageCurrentFiles = os.listdir(packagePath)
#            for f in packageCurrentFiles:
#                if f != ".osc":
#                    os.remove(os.path.join(packagePath, f))
#        else:
#            os.makedirs(packagePath)
#
#        # test if the packaging directory exist.
#        if os.path.isdir(packagingDir):
#            packagingDirFileList = os.listdir(packagingDir)
#
#            # Copy files from packaging/ to package directory
#            for f in packagingDirFileList:
#                shutil.copy(os.path.join(packagingDir, f), os.path.join(packagePath, f))

    def addPackage(self, name=None, packageGitPath=None):
        '''
        add a package to the projectLocalName.
        if url is given, package will be a git package.
        if package come from OBS status, rev on OBS are set,
        and Osc local package rev is set.
        '''

        #test if package "name" is already localy install.
        if name in self.getPackageList():
            return None

        packagePath = self.createPackagePath(name, packageGitPath is not None)

        self.__packages.addPackage(name=name,
                                   packagePath=packagePath,
                                   packageGitPath=packageGitPath,
                                   )
        pkgObj = self.__packages.getPackage(name)

        if not pkgObj.isGitPackage:
            self.__refreshObsDescription(name)
#            self.__refreshOscPackageLocalRev(name)
            self.refreshObsStatus(name)

    def createPackagePath(self, name, isGitPackage):
        if isGitPackage:
           return os.path.join(self.__getGitPackagesDefaultDirectory(), name)
        else:
            return os.path.join(self.__getOscPackagesDefaultDirectory(), name)


    def repairPackageDirectory(self, package):
        pkgObj = self.__packages.getPackage(name)

        if not pkgObj.isGitPackage:
            if package != None:
                return  self.getPackage(package).repairPackageDirectory()
            else:
                return None

    def updatePackage(self, name):
        '''
        update a package of the projectLocalName.
        '''
        self.__refreshObsDescription(name)

        pkgObj = self.__packages.getPackage(name)
#        pkgObj.updatePackage()
        if not pkgObj.isGitPackage:
            server = self.__obsServers.getObsServer(self.__obsServer)
            self.refreshObsStatus(name)

    #        self.checkOscDirectoryStatus(package=name)
#            self.__refreshOscPackageLocalRev(name)

#            self.getPackage(name).initPackageFileInfo()
        return 0

    #--------------------------------------------------------------------------- project Repo
    def removeLocalRepo(self):
        return self.__obsLightRepositories.deleteRepository(self.__projectLocalName)

    def createRepo(self):
        repo = self.__obsLightRepositories.getRepository(self.__projectLocalName)
        if repo.isOutOfDate():
            return repo.createRepo()
        else:
            return 0

    #--------------------------------------------------------------------------- chroot jail
    def createPatch(self, package, patch):
        '''
        Create a patch
        '''
        return self.__chroot.createPatch(package=self.__packages.getPackage(package),
                                         patch=patch)

    def updatePatch(self, package):
        '''
        Update a patch
        '''
        return  self.__chroot.updatePatch(package=self.__packages.getPackage(package))

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

    #--------------------------------------------------------------------------- OBS server
    def getProjectObsName(self):
        return self.__projectName

    def getObsServer(self):
        return self.__obsServer

    def __refreshObsPackageRev(self, package):
        pkgObj = self.getPackage(package)
        if not pkgObj.isGitPackage:
            obsServer = self.__obsServers.getObsServer(self.__obsServer)
            rev = obsServer.getObsPackageRev(self.__projectName, package)
            if rev is not None:
                pkgObj.setPackageParameter("obsRev", rev)
            else:
                pkgObj.setPackageParameter("obsRev", "-1")
            return 0

    def refreshObsStatus(self, package=None):
        '''
        refresh the package status and rev with the state on OBS Server.
        '''
        def doRefreshObsStatus(obsServer, package):
            status = obsServer.getPackageStatus(project=self.__projectName,
                                                package=package,
                                                repo=self.__projectTarget,
                                                arch=self.__projectArchitecture)
            if status != None:
                self.__packages.getPackage(package).setPackageParameter(parameter="status",
                                                                        value=status)
            return self.__refreshObsPackageRev(package=package)


        pkgObj = self.getPackage(package)
        if not pkgObj.isGitPackage:

            obsServer = self.__obsServers.getObsServer(self.__obsServer)

            if package is not None:
                return doRefreshObsStatus(obsServer, package)

            else:
                for pk in self.getPackageList():
                    doRefreshObsStatus(obsServer, pk)
                return 0
        else:
            return 0

#    def getChRootRepositories(self):
#        return self.__chroot.getChRootRepositories()

    def getDependencyRepositories(self):
        obsServer = self.__obsServers.getObsServer(self.__obsServer)
        return obsServer.getDependencyRepositories(self.__projectName,
                                                   self.__projectTarget,
                                                   self.__projectArchitecture)



    def getReposProject(self):
        '''
        Return the URL of the Repo of the Project
        '''
        return os.path.join(self.__obsServers.getObsServer(self.__obsServer).getRepo(),
                            self.__projectName.replace(":", ":/"),
                            self.__projectTarget)

    def __refreshObsDescription(self, name):
        """
        refrech package OBS Title and description
        """
        pkgObj = self.__packages.getPackage(name)

        #No Title or description for git package.
        if not pkgObj.isGitPackage:
            obsServer = self.__obsServers.getObsServer(self.__obsServer)
            packageTitle = obsServer.getPackageParameter(self.__projectName, name, "title")
            description = obsServer.getPackageParameter(self.__projectName, name, "description")

            pkgObj.setPackageParameter(parameter="title", value=packageTitle)
            pkgObj.setPackageParameter(parameter="description", value=description)

    #--------------------------------------------------------------------------- build package

    def __prepareChroot(self, section, pkgObj, specFileName):
        # First install the BuildRequires of the spec file.
        # The BuildRequires come from OBS.
        # We need a spec file parser to be OBS free.
        packageName = pkgObj.getName()

        obsServer = self.__obsServers.getObsServer(self.__obsServer)
        extraPkg = [x for x in self.__extraChrootPackages.keys() if self.__extraChrootPackages[x]]
        buildInfoCli = obsServer.getPackageBuildRequires(self.__projectName,
                                                         packageName,
                                                         self.__projectTarget ,
                                                         self.__projectArchitecture,
                                                         specFileName,
                                                         extraPkg,
                                                         not pkgObj.isGitPackage)
        res = -1

        if len(buildInfoCli.deps) > 0:
            target = self.__getArchHierarchy()
            configPath = self.__getConfigPath()
            res = self.__chroot.installBuildRequires(buildInfoCli, target, configPath)

        if res != 0:
            raise ObsLightErr.ObsLightProjectsError("Can't install " + packageName)

        if section == "prep":
            res = self.__chroot.addPackageSourceInChRoot(pkgObj)
        return 0

    def __execRpmSection(self, packageName, section):
        """
        Execute `section` of the spec file of `packageName`
        into the chroot jail.
        """
        sectionMap = {"prep":  self.__chroot.prepRpm,
                      "build": self.__chroot.buildRpm,
                      "install": self.__chroot.installRpm,
                      "files": self.__chroot.packageRpm}

        pkgObj = self.__packages.getPackage(packageName)

        specFileObj = pkgObj.getSpecObj()
        if specFileObj is None:
            raise ObsLightErr.ObsLightPackageErr("Package '%s' has no Spec file!" % packageName)
        specFileObj.parseFile()
        specFileName = pkgObj.getSpecFile()

        self.__prepareChroot(section, pkgObj, pkgObj.getSpecFile(fullPath=True))

        if pkgObj.getPackageParameter("patchMode") and section != "prep":
            _ = self.__chroot.prepGhostRpmbuild(pkgObj)

        archs = self.__getArchHierarchy()
        buildDir = "/usr/lib/build"
        configdir = buildDir + "/configs"
        configPath = self.__getConfigPath()

        target = self.__getTarget()
        specFilePath = self.__chroot.addPackageSpecInChRoot(pkgObj,
                                                            specFileName,
                                                            section,
                                                            configPath,
                                                            archs,
                                                            configdir,
                                                            buildDir)

        # If we don't remove default ACLs, some files created by the
        # Makefile of package may have wrong rights, and make the build fail.
        # (Was detected with "e2fsprogs")
        self.__chroot.forbidPackageAccessToObslightGroup(pkgObj)
        retVal = sectionMap[section](package=pkgObj,
                                     specFile=specFilePath,
                                     arch=target)
        self.__chroot.allowPackageAccessToObslightGroup(pkgObj)
        #publish RPM builded.
        if (section == "files") and pkgObj.isPackaged():
            buildRootpath = os.path.join(pkgObj.getChrootRpmBuildDirectory(), "RPMS")
            self.publishRPM(pkgObj, buildRootpath)

        return retVal

    def publishRPM(self, pkgObj, path):
        absBuildRootpath = self.__chroot.getDirectory() + path
        listRPM = []

        for arch in os.listdir(absBuildRootpath):
            for rpm in os.listdir(os.path.join(absBuildRootpath, arch)):
                listRPM.append(os.path.join(arch, rpm))

        repo = self.__obsLightRepositories.getRepository(self.__projectLocalName)
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

#Manage the repository into the chroot jail
#_____________________________________________________________________________
#    def deleteRepo(self, repoAlias):
#        return self.__chroot.deleteRepo(repoAlias)
#
#    def modifyRepo(self, repoAlias, newUrl, newAlias):
#        return self.__chroot.modifyRepo(repoAlias, newUrl, newAlias)
#
#    def addRepo(self, repos=None,
#                      alias=None,
#                      chroot=None):
#        if chroot is None:
#            __aChroot = self.__chroot
#        else:
#            __aChroot = chroot
#
#        if repos is None:
#            __aRepos = self.getReposProject()
#        else:
#            __aRepos = repos
#
#        if alias is None:
#            __anAlias = self.__projectName
#        else:
#            __anAlias = alias
#
#        if not __aChroot.isAlreadyAReposAlias(__anAlias):
#            return __aChroot.addRepo(repos=__aRepos  , alias=__anAlias)
#        else:
#            message = __anAlias + " is already installed in the project file system"
#            self.logger.info(message)
#            return 0

    #--------------------------------------------------------------------------- test build
    def importPrepBuildPackage(self, packageName):
        """
        Import the package in OBS Light, import it in chroot jail,
        execute %prep, then build RPMs.
        Returns 0 on success, != 0 or exception on failure.

        This function was developed for testing purposes.
        """
        if not self.__chrootIsInit:
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
