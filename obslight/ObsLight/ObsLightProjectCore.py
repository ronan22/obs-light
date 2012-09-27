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
import os
import shutil

from ObsLightPackages import ObsLightPackages

import ObsLightErr
from ObsLightSubprocess import SubprocessCrt
from ObsLightObject import ObsLightObject

class ObsLightProjectCore(ObsLightObject):

    def __init__(self,
                 obsLightRepositories,
                 workingDirectory,
                 projectLocalName=None,
                 projectArchitecture=None,
                 fromSave={}):

        ObsLightObject.__init__(self)
        self.__mySubprocessCrt = SubprocessCrt()

        self.__obsLightRepositories = obsLightRepositories
        self.__WorkingDirectory = workingDirectory
        self.__projectType = None
        # package name as key, install/don't install as value
        self.__extraChrootPackages = fromSave.get("extraChrootPackages", {"vim": False,
                                                                          "emacs": False,
                                                                          "strace": False})

        self.__projectLocalName = fromSave.get("projectLocalName", projectLocalName)

        self.__readOnly = False
        self.__projectArchitecture = fromSave.get("projectArchitecture", projectArchitecture)


        if not os.path.isdir(self.getDirectory()):
            os.makedirs(self.getDirectory())

        self.__buildConfigPath = fromSave.get("buildConfigPath", None)

        # Taken from /usr/lib/build/common_functions
        self.__archHierarchyMap = {}
        self.__archHierarchyMap["i686"] = "i686:i586:i486:i386"
        self.__archHierarchyMap["i586"] = "i686:i586:i486:i386"
        self.__archHierarchyMap["i486"] = "i486:i386"
        self.__archHierarchyMap["i386"] = "i386"
        self.__archHierarchyMap["x86_64"] = "x86_64:i686:i586:i486:i386"
        self.__archHierarchyMap["sparc64v"] = "sparc64v:sparc64:sparcv9v:sparcv9:sparcv8:sparc"
        self.__archHierarchyMap["sparc64"] = "sparc64:sparcv9:sparcv8:sparc"
        self.__archHierarchyMap["sparcv9v"] = "sparcv9v:sparcv9:sparcv8:sparc"
        self.__archHierarchyMap["sparcv9"] = "sparcv9:sparcv8:sparc"
        self.__archHierarchyMap["sparcv8"] = "sparcv8:sparc"
        self.__archHierarchyMap["sparc"] = "sparc"

        self.__fromSave = fromSave

    def _initPackage(self):
        self.__packages = ObsLightPackages(self, self.__fromSave.get("packages", {}))

    def _getPackages(self):
        return self.__packages

    def getName(self):
        return self.__projectLocalName

    def getProjectParameter(self, parameter=None):
        '''
        Get the value of a project parameter:
        the valid parameter is :
            projectLocalName
            projectDirectory
            projectArchitecture
        '''
        if parameter == "projectLocalName":
            return self.__projectLocalName
        elif parameter == "projectDirectory":
            return self.getDirectory()
        elif parameter == "projectArchitecture":
            return self.__projectArchitecture

        elif parameter in [ "projectObsName", "projectTarget", "title", "description"]:
            return ""
        else:
            message = "parameter '%s' is not valid for getProjectParameter" % parameter
            raise ObsLightErr.ObsLightProjectsError(message)

    def setProjectParameter(self, parameter=None, value=None):
        '''
        Return the value of a parameter of the project:
        Valid parameters are:
            projectArchitecture
        '''
        if parameter == "projectArchitecture":
            self.__projectArchitecture = value
        else:
            message = "parameter '%s' is not valid for setProjectParameter" % parameter
            raise ObsLightErr.ObsLightProjectsError(message)
        return 0

    def getDic(self):
        aDic = {}
        aDic["projectLocalName"] = self.__projectLocalName
        aDic["projectArchitecture"] = self.__projectArchitecture
        aDic["packages"] = self.__packages.getDic()
        aDic["ro"] = self.__readOnly
        aDic["type"] = self.__projectType
        aDic["buildConfigPath"] = self.__buildConfigPath
        aDic["extraChrootPackages"] = self.__extraChrootPackages
        return aDic

    def getBuildConfigPath(self, fullPath=True):
        if fullPath:
            return self.__buildConfigPath
        else:
            return os.path.basename(self.__buildConfigPath)

    def setBuildConfigPath(self, path):
        self.__buildConfigPath = path

    def getExtraChrootPackagesList(self):
        res = []
        for package in self.__extraChrootPackages.keys():
            if self.__extraChrootPackages[package]:
                res.append(package)
        return res
    #--------------------------------------------------------------------------- util

    def _subprocess(self, command=None, waitMess=False, stdout=False):
        return self.__mySubprocessCrt.execSubprocess(command=command,
                                                     waitMess=waitMess,
                                                     stdout=stdout)

    #--------------------------------------------------------------------------- project
    def getbuildConfigPath(self):
        return self.__buildConfigPath

    def getArchitecture(self):
        return self.__projectArchitecture

    def isReadOnly(self):
        return self.__readOnly

    def setReadOnly(self, value):
        self.__readOnly = value

    def getArchHierarchy(self):
        if self.__projectArchitecture in self.__archHierarchyMap:
            return self.__archHierarchyMap[self.__projectArchitecture]
        else:
            return self.__projectArchitecture

    def getTarget(self):
        """
        Get the 'target' string to be passed to rpmbuild.
        Looks like 'i586-tizen-linux'.
        """
        archs = self.getArchHierarchy()

        buildDir = "/usr/lib/build"
        configdir = buildDir + "/configs"

        configPath = self.getBuildConfigPath()
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

    def getDirectory(self):
        '''
        Return the project directory.
        '''
        return os.path.join(self.__WorkingDirectory, self.__projectLocalName)

    def removeProject(self):
        self.removeLocalRepo()

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

    #--------------------------------------------------------------------------- project Repo
    def removeLocalRepo(self):
        return self.__obsLightRepositories.deleteRepository(self.__projectLocalName)

    def getRepositories(self):
        return self.__obsLightRepositories

    def createRepo(self):
        repo = self.__obsLightRepositories.getRepository(self.__projectLocalName)
        if repo.isOutOfDate():
            return repo.createRepo()
        else:
            return 0

    def getLocalRepository(self):
        return self.__obsLightRepositories.getRepository(self.getName()).getLocalRepository()


    def setProjectType(self, value):
        '''
        Set the type of the project (None,OBS,gbs)
        '''
        self.__projectType = value

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

    def getGitPackagesDefaultDirectory(self):
        '''
        Return the package git directory of the local project.
        '''
        return os.path.join(self.getDirectory(), "gitWorkingTrees")



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
        if onlyInstalled:
            return self.__packages.getPackagesList()
        else:
            return []

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
        res = self.__packages.removePackage(package=package)
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

    def createPackagePath(self, name, isGitPackage=True):
        return os.path.join(self.getGitPackagesDefaultDirectory(), name)



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

#Abstract Funct
    def refreshObsStatus(self, package):
        pass

    def refreshPackageDirectoryStatus(self, package):
        pass

    def updatePackage(self, name):
        pass

    def __refreshObsDescription(self, name):
        pass

    def refreshObsStatus(self, name):
        pass

    def getWebProjectPage(self):
        return ""

    def getReposProject(self):
        return ""
