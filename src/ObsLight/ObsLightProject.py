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
Created on 29 sept. 2011

@author: ronan
'''
import os
import shutil

from ObsLightPackages import ObsLightPackages
from ObsLightChRoot import ObsLightChRoot
#import ObsLightManager
import ObsLightErr
from ObsLightSubprocess import SubprocessCrt
import ObsLightOsc
import urllib

import ObsLightPrintManager

import ObsLightConfig

import shlex
import subprocess

class ObsLightProject(object):
    '''
    classdocs
    '''

    def __init__(self,
                 obsServers,
                 workingDirectory,
                 projectObsName=None,
                 projectLocalName=None,
                 obsServer=None,
                 projectTarget=None,
                 projectArchitecture=None,
                 projectTitle="",
                 description="",
                 fromSave=None,
                 importFile=False):
        '''
        Constructor
        '''
        self.__mySubprocessCrt = SubprocessCrt()

        self.__obsServers = obsServers

        self.__chrootIsInit = False
        self.__WorkingDirectory = workingDirectory
        self.__projectTitle = projectTitle

        if fromSave is None:
            self.__projectLocalName = projectLocalName
            self.__projectObsName = projectObsName
            self.__obsServer = obsServer
            self.__projectTarget = projectTarget
            self.__projectArchitecture = projectArchitecture
            self.__description = description
            self.__packages = ObsLightPackages()
            self.__chroot = ObsLightChRoot(projectDirectory=self.getDirectory())

            #perhaps a trusted_prj must be had
            obsServer = self.__obsServers.getObsServer(name=self.__obsServer)
            obsServer.initConfigProject(projet=self.__projectObsName, repos=self.__projectTarget)
        else:
            if "projectLocalName" in fromSave.keys():
                self.__projectLocalName = fromSave["projectLocalName"]
            if "projectObsName" in fromSave.keys():
                self.__projectObsName = fromSave["projectObsName"]
            if "obsServer" in fromSave.keys():
                self.__obsServer = fromSave["obsServer"]
                if not (self.__obsServer in self.__obsServers.getObsServerList()):
                    message = "WARNING: '" + self.__obsServer + "' is not a defined OBS server "
                    ObsLightPrintManager.obsLightPrint(message)
            if "projectTarget" in fromSave.keys():
                self.__projectTarget = fromSave["projectTarget"]
            if "projectArchitecture" in fromSave.keys():
                self.__projectArchitecture = fromSave["projectArchitecture"]
            if "title" in fromSave.keys():
                self.__projectTitle = fromSave["title"]
                if self.__projectTitle is None:
                    self.__projectTitle = ""
            if "description" in fromSave.keys():
                self.__description = fromSave["description"]
                if self.__description is None:
                    self.__description = ""

            if "aChroot" in fromSave.keys():
                self.__chroot = ObsLightChRoot(projectDirectory=self.getDirectory(),
                                               fromSave=fromSave["aChroot"])
            else:
                raise ObsLightErr.ObsLightProjectsError("aChroot is not ")
            #perhaps a trusted_prj must be had
            if self.__obsServer in self.__obsServers.getObsServerList():
                obsServer = self.__obsServers.getObsServer(name=self.__obsServer)
                obsServer.initConfigProject(projet=self.__projectObsName,
                                            repos=self.__projectTarget)

            if "packages" in fromSave.keys():
                self.__packages = self.__addPackagesFromSave(fromSave=fromSave["packages"],
                                                             importFile=importFile)

            if "chrootIsInit" in fromSave.keys():
                self.__chrootIsInit = fromSave["chrootIsInit"]
                if self.__chrootIsInit == True:
                    if not self.__chroot.isInit():
                        self.__initChRoot()
#                        self.__chroot.initRepos()
                else:
                    if self.__chroot.isInit():
                        self.__chrootIsInit = True

#            if self.__chrootIsInit:
#                for packageName in self.__packages.getListPackages():
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


    def getDirectory(self):
        '''
        Return the project directory.
        '''
        return os.path.join(self.__WorkingDirectory, self.__projectLocalName)

    def getAbsPackagePath(self, name):
        '''
        return the absolute path of a package install into chroot.
        return None if the package is not install.
        '''

        if self.getPackage(name).isInstallInChroot():
            packageDirectory = self.__packages.getPackage(name).getPackageDirectory()
            absPackagePath = self.__chroot.getDirectory() + packageDirectory
            return absPackagePath
        else:
            return None

    def __addPackagesFromSave(self, fromSave, importFile):
        '''
        check and add a package from a save.
        '''
        for packageName in fromSave["savePackages"].keys():
            packageFromSave = fromSave["savePackages"][packageName]
            if "name" in packageFromSave.keys():
                name = packageFromSave["name"]
            packagePath = self.__getPackagePath(name)
            if not os.path.isdir(self.__getPackagePath(name)):
                packagePath, specFile, yamlFile, listFile = self.checkoutPackage(package=name)

                packageFromSave["specFile"] = specFile
                packageFromSave["yamlFile"] = yamlFile
                packageFromSave["listFile"] = listFile

            if importFile == True:
                toUpDate = False
                if "listFile" in packageFromSave.keys():
                    listFile = packageFromSave["listFile"]
                for aFile in listFile:
                    if not os.path.isfile(os.path.join(packagePath, aFile)):
                        toUpDate = True
                if "specFile" in packageFromSave.keys():
                    specFilePath = packageFromSave["specFile"]
                    if specFilePath is not None and not os.path.isfile(specFilePath):
                        toUpDate = True
                if "yamlFile" in packageFromSave.keys():
                    yamlFilePath = packageFromSave["yamlFile"]
                    if yamlFilePath is not None and not os.path.isfile(yamlFilePath):
                        toUpDate = True
                if toUpDate == True:
                    ObsLightOsc.getObsLightOsc().updatePackage(packagePath=packagePath)

            fromSave["savePackages"][packageName] = packageFromSave

        return ObsLightPackages(projectOscPath=self.__getProjectOscPath(),
                                fromSave=fromSave)

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
            return self.__projectObsName
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
            message = "parameter '" + parameter + "' is not valid for setProjectParameter"
            raise ObsLightErr.ObsLightProjectsError(message)
        return 0

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
            title
        '''
        return self.__packages.getPackage(package).getPackageParameter(parameter=parameter)

    def setPackageParameter(self, package, parameter=None, value=None):
        '''
        return the value  of the parameter of the package:
        the valid parameter is :
            specFile
            yamlFile
            packageDirectory
            description
            title
        '''
        return self.__packages.getPackage(package).setPackageParameter(parameter=parameter,
                                                                       value=value)

    #---------------------------------------------------------------------------package
    def getCurrentPackage(self):
        return self.__packages.getCurrentPackage()

    #---------------------------------------------------------------------------

    def __subprocess(self, command=None, waitMess=False, stdout=False):
        return self.__mySubprocessCrt.execSubprocess(command=command,
                                                     waitMess=waitMess,
                                                     stdout=stdout)

    def removeProject(self):
        res = self.removeChRoot()

        if res == 0:
            drctr = self.getDirectory()
            if os.path.isdir(drctr):
                try:
                    return shutil.rmtree(drctr)
                except:
                    message = "Error in removeProject, can't remove directory, '" + drctr + "'"
                    raise ObsLightErr.ObsLightProjectsError(message)
            else:
                ObsLightPrintManager.obsLightPrint("WARNING: '" + drctr + "' is not a directory.")
                return 0
        else:
            message = "Error in removeProject, can't remove project file system"
            raise ObsLightErr.ObsLightProjectsError(message)

        return 0

    def removeChRoot(self):
        '''
        
        '''
        for package in self.__packages.getListPackages():
            if self.getPackage(package).isInstallInChroot():
                self.__packages.delFromChroot(package)

        res = self.__chroot.removeChRoot()
        self.__chrootIsInit = False
        return res

    def getProjectObsName(self):
        '''
        
        '''
        return self.__projectObsName

    def getChRoot(self):
        '''
         
        '''
        return self.__chroot

    def getDic(self):
        '''
        
        '''
        aDic = {}
        aDic["projectLocalName"] = self.__projectLocalName
        aDic["projectObsName"] = self.__projectObsName
        aDic["obsServer"] = self.__obsServer
        aDic["projectTarget"] = self.__projectTarget
        aDic["projectArchitecture"] = self.__projectArchitecture
        aDic["title"] = self.__projectTitle
        aDic["description"] = self.__description
        aDic["packages"] = self.__packages.getDic()
        aDic["aChroot"] = self.__chroot.getDic()
        aDic["chrootIsInit"] = self.__chrootIsInit
        return aDic

    def getObsServer(self):
        '''
        
        '''
        return self.__obsServer

    def getListPackage(self, onlyInstalled=True):
        '''
        
        '''
        if not onlyInstalled :
            if self.__obsServer in self.__obsServers.getObsServerList():
                obsServer = self.__obsServers.getObsServer(self.__obsServer)
                res1 = set(obsServer.getObsProjectPackageList(projectObsName=self.__projectObsName))
                res2 = set(self.__packages.getListPackages())
                res = list(res1.difference(res2))
                res.sort()
                return res
            else:
                return  None
        else:
            return self.__packages.getListPackages()

    def __getPackagePath(self, package):
        '''
        
        '''
        return os.path.join(self.getDirectory(), self.__projectObsName, package)

    def __getProjectOscPath(self):
        '''
        
        '''
        return os.path.join(self.getDirectory(), self.__projectObsName)

    def checkoutPackage(self, package=None):
        '''
        
        '''
        ObsLightOsc.getObsLightOsc().checkoutPackage(obsServer=self.__obsServer,
                                                     projectObsName=self.__projectObsName,
                                                     package=package,
                                                     directory=self.getDirectory())

        packagePath = self.__getPackagePath(package)

        return self.checkoutFilePackage(packagePath)

    def  checkoutFilePackage(self, packagePath):
        #Find the spec file
        if os.path.isdir(packagePath):
            tmplistFile = os.listdir(packagePath)
        else:
            message = "Can't do checkoutFilePackage, the path:'" + packagePath + "' do not exist."
            raise ObsLightErr.ObsLightProjectsError(message)

        listFile = []
        for aFile in tmplistFile:
            if os.path.isfile(packagePath + "/" + aFile) and\
               not (aFile.startswith(".")) and\
               not (aFile.endswith("~")):
                listFile.append(aFile)

        listSpecFile = []
        yamlFile = None
        specFile = None

        for f in listFile:
            if self.__isASpecfile(f):
                listSpecFile.append(f)
            elif self.__isAyamlfile(f):
                pass
            #disable the yaml file management.
#                yamlFile = f

        if len(listSpecFile) > 1:
            specFile = None
            packageName = os.path.basename(packagePath)

            for spec in listSpecFile:
                if str(spec[:-5]) == str(packageName):
                    specFile = spec
                    break
                elif spec.startswith(packageName):
                    specFile = spec

        elif len(listSpecFile) == 1:
            specFile = listSpecFile[0]

        return packagePath, specFile, yamlFile, listFile

    def __updatePackage(self, package, noOscUpdate=False):
        '''
        
        '''
        packagePath = self.__getPackagePath(package)
        if noOscUpdate == False:
            ObsLightOsc.getObsLightOsc().updatePackage(packagePath)

        return self.checkoutFilePackage(packagePath)

    def __isASpecfile(self, aFile):
        '''
        
        '''
        return aFile.endswith(".spec")

    def __isAyamlfile(self, aFile):
        '''
        
        '''
        return aFile.endswith(".yaml")


    def addPackage(self, name=None):
        '''
        add a package to the projectLocalName.
        '''
        if name in self.getListPackage():
            return None

        packagePath, specFile, yamlFile, listFile = self.checkoutPackage(package=name)

        obsServer = self.__obsServers.getObsServer(self.__obsServer)
        status = obsServer.getPackageStatus(project=self.__projectObsName,
                                            package=name,
                                            repo=self.__projectTarget,
                                            arch=self.__projectArchitecture)
        packageTitle = obsServer.getPackageParameter(self.__projectObsName, name, "title")
        description = obsServer.getPackageParameter(self.__projectObsName, name, "description")

        self.__packages.addPackage(name=name,
                                   packagePath=packagePath,
                                   description=description,
                                   packageTitle=packageTitle,
                                   specFile=specFile,
                                   yamlFile=yamlFile,
                                   listFile=listFile,
                                   status=status)
        self.checkOscDirectoryStatus(package=name)
        self.checkOscPackageStatus(package=name)
        self.checkObsPackageStatus(package=name)

    def checkObsPackageStatus(self, package):
        '''
        
        '''
        obsServer = self.__obsServers.getObsServer(self.__obsServer)
        rev = obsServer.getObsPackageRev(self.__projectObsName, package)
        if rev is not None:
            self.__packages.getPackage(package).setPackageParameter("obsRev", rev)
        return 0

    def refreshOscDirectoryStatus(self, package=None):
        '''
        
        '''
        if package != None:
            self.updatePackage(name=package, noOscUpdate=True)
            self.checkOscDirectoryStatus(package)
            self.__packages.getPackage(package).initPackageFileInfo()
            self.checkOscPackageStatus(package)
        else:
            for pk in self.getListPackage():
                self.updatePackage(name=pk, noOscUpdate=True)
                self.checkOscDirectoryStatus(pk)
                self.__packages.getPackage(pk).initPackageFileInfo()
                self.checkOscPackageStatus(package)
        return 0

    def repairOscPackageDirectory(self, package):
        '''
        
        '''
        if package != None:
            path = self.__getPackagePath(package)
            ObsLightOsc.getObsLightOsc().repairOscPackageDirectory(path=path)
            return self.updatePackage(name=package)
        else:
            return None

    def refreshObsStatus(self, package=None):
        '''
        
        '''
        if package != None:
            obsServer = self.__obsServers.getObsServer(self.__obsServer)
            status = obsServer.getPackageStatus(project=self.__projectObsName,
                                                package=package,
                                                repo=self.__projectTarget,
                                                arch=self.__projectArchitecture)
            if status != None:
                self.__packages.getPackage(package).setPackageParameter(parameter="status",
                                                                        value=status)
            return self.checkObsPackageStatus(package=package)

        else:
            for pk in self.getListPackage():
                obsServer = self.__obsServers.getObsServer(self.__obsServer)
                status = obsServer.getPackageStatus(project=self.__projectObsName,
                                                    package=pk,
                                                    repo=self.__projectTarget,
                                                    arch=self.__projectArchitecture)

                return self.__packages.getPackage(pk).setPackageParameter(parameter="status",
                                                                          value=status)

    def checkOscPackageStatus(self, package):
        '''
        
        '''
        obsServer = self.__obsServers.getObsServer(self.__obsServer)
        oscDirectory = self.__packages.getPackage(package).getOscDirectory()
        rev = obsServer.getOscPackageRev(workingdir=oscDirectory)

        if rev != None:
            self.__packages.getPackage(package).setOscPackageRev(rev)
        else:
            self.__packages.getPackage(package).setOscPackageRev("-1")

    def checkOscDirectoryStatus(self, package):
        '''
        
        '''
        obsServer = self.__obsServers.getObsServer(self.__obsServer)
        dicoListFile = obsServer.getFilesListPackage(projectObsName=self.__projectObsName,
                                                     package=package)
        if dicoListFile != None:
            packageCli = self.__packages.getPackage(package)
            listOscFile = packageCli.getPackageParameter(parameter="listFile")

            for obsFile in dicoListFile.keys():
                if (not obsFile in listOscFile) and (obsFile != "_link"):
                    self.__packages.getPackage(package).setOscStatus("inconsistent state")
                    return None
            self.__packages.getPackage(package).setOscStatus("Succeeded")

        return None

    def updatePackage(self, name, noOscUpdate=False):
        '''
        update a package of the projectLocalName.
        '''
        result = self.__updatePackage(package=name, noOscUpdate=noOscUpdate)

        specFile = result[1]
        yamlFile = result[2]
        listFile = result[3]

        server = self.__obsServers.getObsServer(self.__obsServer)
        status = server.getPackageStatus(project=self.__projectObsName,
                                         package=name,
                                         repo=self.__projectTarget,
                                         arch=self.__projectArchitecture)

        packageTitle = server.getPackageParameter(self.__projectObsName,
                                                  package=name,
                                                  parameter="title")

        description = server.getPackageParameter(self.__projectObsName,
                                                  package=name,
                                                  parameter="description")

        packageCli = self.__packages.getPackage(name)
        packageCli.setPackageParameter(parameter="specFile", value=specFile)
        packageCli.setPackageParameter(parameter="yamlFile", value=yamlFile)
        packageCli.setPackageParameter(parameter="listFile", value=listFile)
        packageCli.setPackageParameter(parameter="status", value=status)
        packageCli.setPackageParameter(parameter="title", value=packageTitle)
        packageCli.setPackageParameter(parameter="description", value=description)

        self.refreshObsStatus(package=name)

        self.checkOscDirectoryStatus(package=name)
        if noOscUpdate == False:
            self.checkOscPackageStatus(package=name)

        self.__packages.getPackage(name).initPackageFileInfo()
        return 0

    def getChRootRepositories(self):
        '''
        
        '''
        return self.__chroot.getChRootRepositories()

    def updateProject(self):
        '''
        
        '''
        for name in self.__packages.getListPackages():
            server = self.__obsServers.getObsServer(self.__obsServer)
            status = server.getPackageStatus(project=self.__projectObsName,
                                             package=name,
                                             repo=self.__projectTarget,
                                             arch=self.__projectArchitecture)
            self.__packages.updatePackage(name=name, status=status)

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
        Init a chroot and add the project repository. 
        '''
#        repos = self.getDependencyRepositories()

        self.__initChRoot()
#        res = self.addRepo()
#
#        for alias in repos.keys():
#            res = self.addRepo(repos=repos[alias], alias=alias)

        return 0

    def __initChRoot(self):
        '''
        Init a chroot.
        '''
        apiurl = self.__obsServers.getObsServer(self.__obsServer).getAPI()
        self.__chroot.createChRoot(repos=self.__projectTarget,
                                   arch=self.__projectArchitecture,
                                   apiurl=apiurl,
                                   obsProject=self.__projectObsName)
        self.__chrootIsInit = True

    def getReposProject(self):
        '''
        Return the URL of the Repo of the Project
        '''
        return os.path.join(self.__obsServers.getObsServer(self.__obsServer).getRepo(),
                            self.__projectObsName.replace(":", ":/"),
                            self.__projectTarget)

    def goToChRoot(self, package=None, detach=False):
        if package != None:
            packagePath = self.__packages.getPackage(package).getPackageDirectory()
            if packagePath != None:
                return self.__chroot.goToChRoot(path=packagePath, detach=detach,
                                                project=self.__projectLocalName)
            else:
                return self.__chroot.goToChRoot(detach=detach, project=self.__projectLocalName)
        else:
            return self.__chroot.goToChRoot(detach=detach, project=self.__projectLocalName)

    def execScript(self, aPath):
        return self.__chroot.execScript(aPath)

    def openTerminal(self, package):
        '''
        Open bash in `package`'s osc working directory.
        '''
        if package != None:
            packagePath = self.__packages.getOscDirectory(name=package)
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

    def __prepareChroot(self, section, pkgObj, specFileName):
        # First install the BuildRequires of the spec file.
        # The BuildRequires come from OBS.
        # We need a spec file parser to be OBS free.
        packageName = pkgObj.getName()

        obsServer = self.__obsServers.getObsServer(self.__obsServer)
        buildInfoCli = obsServer.getPackageBuildRequires(self.__projectObsName,
                                                                packageName,
                                                                self.__projectTarget ,
                                                                self.__projectArchitecture,
                                                                specFileName)

        if len(buildInfoCli.deps) > 0:
            res = self.__chroot.installBuildRequires(buildInfoCli)
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

        pkgObj.getSpecFileObj().parseFile()
        specFileName = pkgObj.getSpecFile()

        self.__prepareChroot(section, pkgObj, pkgObj.getSpecFilePath())

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

        retVal = sectionMap[section](package=pkgObj,
                                     specFile=specFilePath,
                                     arch=target)
        return retVal

    def buildPrep(self, package):
        return self.__execRpmSection(package, "prep")

    def buildRpm(self, package):
        return self.__execRpmSection(package, "build")

    def installRpm(self, package):
        return self.__execRpmSection(package, "install")

    def packageRpm(self, package):
        return self.__execRpmSection(package, "files")

    def __getArchHierarchy(self):
        if self.__projectArchitecture in self.__archHierarchyMap:
            return self.__archHierarchyMap[self.__projectArchitecture]
        else:
            return self.__projectArchitecture

    def __getConfigPath(self):
        if self.__configPath is None:
            obsServer = self.__obsServers.getObsServer(self.__obsServer)
            self.__configPath = obsServer.saveProjectConfig(self.__projectObsName,
                                                            self.__projectTarget)

        return self.__configPath

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

        target = self.__subprocess(command, stdout=True)
        ObsLightPrintManager.getLogger().debug("Target found by getchangetarget: '%s'" % target)

        endline = "\n"
        if target.endswith("\n"):
            target = target[:-len(endline)]

        return target

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

    def commitToObs(self, message=None, package=None):
        '''
        commit the package to the OBS server.
        '''
        obsRev = self.__packages.getPackage(package).getObsPackageRev()
        oscRev = self.__packages.getPackage(package).getOscPackageRev()
        if obsRev != oscRev:
            message = "Can't Commit \"%s\"\n"
            message += "because local osc rev \"%s\" and OBS rev \"%s\" do not match.\n"
            message += "Please update the package."
            message = message % (package, oscRev, obsRev)

            raise ObsLightErr.ObsLightProjectsError(message)

        self.__packages.getPackage(package).commitToObs(message=message)
        self.checkOscDirectoryStatus(package=package)
        self.checkOscPackageStatus(package=package)
        self.refreshObsStatus(package=package)
        return 0

    def addRemoveFileToTheProject(self, package=None):
        '''
        add new file and remove file to the project.
        '''
        self.__packages.getPackage(package).addRemoveFileToTheProject()

    def getPackage(self, package=None):
        return  self.__packages.getPackage(package=package)

    def removePackage(self, package=None):
        return self.__packages.removePackage(package=package)

    def getWebProjectPage(self):
        serverWeb = self.__obsServers.getObsServer(name=self.__obsServer).getUrlServerWeb()

        if serverWeb in (None, "None", ""):
            raise ObsLightErr.ObsLightProjectsError("No Web Server")
        res = urllib.basejoin(serverWeb , "project/show?project=" + self.__projectObsName)
        return res

    def getPackageInfo(self, package=None):
        return self.__packages.getPackageInfo(package=package)

    def getListOscStatus(self):
        return self.__packages.getListOscStatus()

    def getPackageFilter(self):
        return self.__packages.getPackageFilter()

    def resetPackageFilter(self):
        return self.__packages.resetPackageFilter()

    def removePackageFilter(self, key):
        return self.__packages.removePackageFilter(key=key)

    def addPackageFilter(self, key, val):
        return self.__packages.addPackageFilter(key=key, val=val)

    def getListStatus(self):
        return self.__packages.getListStatus()

    def getListChRootStatus(self):
        return self.__packages.getListChRootStatus()


    def getDependencyRepositories(self):
        obsServer = self.__obsServers.getObsServer(self.__obsServer)
        return obsServer.getDependencyRepositories(self.__projectObsName,
                                                   self.__projectTarget,
                                                   self.__projectArchitecture)

#Manage the repository into the chroot jail
#_____________________________________________________________________________
    def deleteRepo(self, repoAlias):
        return self.__chroot.deleteRepo(repoAlias)

    def modifyRepo(self, repoAlias, newUrl, newAlias):
        return self.__chroot.modifyRepo(repoAlias, newUrl, newAlias)

    def addRepo(self, repos=None,
                      alias=None,
                      chroot=None):
        if chroot is None:
            __aChroot = self.__chroot
        else:
            __aChroot = chroot

        if repos is None:
            __aRepos = self.getReposProject()
        else:
            __aRepos = repos

        if alias is None:
            __anAlias = self.__projectObsName
        else:
            __anAlias = alias

        if not __aChroot.isAlreadyAReposAlias(__anAlias):
            return __aChroot.addRepo(repos=__aRepos  , alias=__anAlias)
        else:
            message = __anAlias + " is already installed in the project file system"
            ObsLightPrintManager.getLogger().info(message)
            return 0

#_____________________________________________________________________________
