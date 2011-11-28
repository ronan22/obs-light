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

class ObsLightProject(object):
    '''
    classdocs
    '''

    def __init__(self, obsServers,
                       workingDirectory,
                       projectObsName=None,
                       projectLocalName=None,
                       obsServer=None ,
                       projectTarget=None,
                       projectTitle=None,
                       description=None,
                       projectArchitecture=None,
                       fromSave=None,
                       importFile=False):
        '''
        Constructor
        '''
        self.__mySubprocessCrt = SubprocessCrt()

        self.__obsServers = obsServers

        self.__chrootIsInit = False
        self.__WorkingDirectory = workingDirectory


        if fromSave == None:
            self.__projectLocalName = projectLocalName
            self.__projectObsName = projectObsName
            self.__obsServer = obsServer
            self.__projectTarget = projectTarget
            self.__projectArchitecture = projectArchitecture
            self.__projectTitle = projectTitle
            self.__description = description

            self.__chroot = ObsLightChRoot(projectDirectory=self.getDirectory())
            self.__packages = ObsLightPackages()

            #perhaps a trusted_prj must be had
            self.__obsServers.getObsServer(name=self.__obsServer).initConfigProject(projet=self.__projectObsName,
                                                                                    repos=self.__projectTarget)
        else:
            if "projectLocalName" in fromSave.keys():
                self.__projectLocalName = fromSave["projectLocalName"]
            if "projectObsName" in fromSave.keys():
                self.__projectObsName = fromSave["projectObsName"]
            if "obsServer" in fromSave.keys():
                self.__obsServer = fromSave["obsServer"]
                if not (self.__obsServer in self.__obsServers.getObsServerList()):
                    ObsLightPrintManager.obsLightPrint("WARNING: '" + self.__obsServer + "' is not a defined OBS server ")
            if "projectTarget" in fromSave.keys():
                self.__projectTarget = fromSave["projectTarget"]
            if "projectArchitecture" in fromSave.keys():
                self.__projectArchitecture = fromSave["projectArchitecture"]
            if "projectTitle" in fromSave.keys():
                self.__projectTitle = fromSave["projectTitle"]
            if "description" in fromSave.keys():
                self.__description = fromSave["description"]
            if "aChroot" in fromSave.keys():
                self.__chroot = ObsLightChRoot(projectDirectory=self.getDirectory(),
                                               fromSave=fromSave["aChroot"])
            else:
                raise ObsLightErr.ObsLightProjectsError("aChroot is not ")
            #perhaps a trusted_prj must be had
            if self.__obsServer in self.__obsServers.getObsServerList():
                self.__obsServers.getObsServer(name=self.__obsServer).initConfigProject(projet=self.__projectObsName,
                                                                                        repos=self.__projectTarget)
            if "packages" in fromSave.keys():
                self.__packages = self.__addPackagesFromSave(fromSave=fromSave["packages"],
                                                             importFile=importFile)

            if "chrootIsInit" in fromSave.keys():
                self.__chrootIsInit = fromSave["chrootIsInit"]
                if self.__chrootIsInit == True:
                    if not self.__chroot.isInit():
                        self.__initChRoot()
                        self.__chroot.initRepos()
                else:
                    if self.__chroot.isInit():
                        self.__chrootIsInit = True

            if self.__chrootIsInit:
                for packageName in self.__packages.getListPackages():
                    absPackagePath = self.getAbsPackagePath(name=packageName)
                    if absPackagePath != None:
                        if not os.path.isdir(absPackagePath) :
                            self.addPackageSourceInChRoot(package=packageName)

        if not os.path.isdir(self.getDirectory()):
            os.makedirs(self.getDirectory())

        print "init self.__projectLocalName", self.__projectLocalName

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

        if self.__packages.isInstallInChroot(name):
            absPackagePath = self.__chroot.getDirectory() + self.__packages.getPackageDirectory(name)
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
            projectTitle
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
        elif parameter == "projectTitle":
            return self.__projectTitle
        elif parameter == "description":
            return self.__description
        else:
            raise ObsLightErr.ObsLightProjectsError("parameter value is not valid for getProjectParameter")

    def setProjectParameter(self, parameter=None, value=None):
        '''
        Return the value of a parameter of the project:
        Valid parameters are:
            projectTarget
            projectArchitecture
            projectTitle
            description
        '''
        if parameter == "projectTarget":
            self.__projectTarget = value
        elif parameter == "projectArchitecture":
            self.__projectArchitecture = value
        elif parameter == "projectTitle":
            self.__projectTitle = value
        elif parameter == "description":
            self.__description = value
        else:
            raise ObsLightErr.ObsLightProjectsError("parameter value is not valid for setProjectParameter")

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
        return self.__packages.getPackageParameter(package=package,
                                                   parameter=parameter)

    def setPackageParameter(self, package, parameter=None, value=None):
        '''
        return the value  of the parameter of the package:
        the valid parameter is :
            specFile
            yamlFile
            packageDirectory
            description
            packageTitle
        '''
        return self.__packages.setPackageParameter(package=package,
                                                   parameter=parameter,
                                                   value=value)


    def __subprocess(self, command=None, waitMess=False):
        '''
        
        '''
        return self.__mySubprocessCrt.execSubprocess(command=command,
                                                     waitMess=waitMess)

    def removeProject(self):
        '''
        
        '''
        res = self.removeChRoot()

        if res == 0:
            return shutil.rmtree(self.getDirectory())
        else:
            raise ObsLightErr.ObsLightProjectsError("Error in removeProject, can't remove chroot")

        return 0

    def removeChRoot(self):
        '''
        
        '''
        for package in self.__packages.getListPackages():
            if self.__packages.isInstallInChroot(package):
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
        aDic["projectTitle"] = self.__projectTitle
        aDic["description"] = self.__description
        aDic["packages"] = self.__packages.getDic()
        aDic["aChroot"] = self.__chroot.getDic()
        aDic["chrootIsInit"] = self.__chrootIsInit
        return aDic

    def getObsServer(self):
        '''
        
        '''
        return self.__obsServer

    def getListPackage(self, local=0):
        '''
        
        '''
        if local == 0:
            if self.__obsServer in self.__obsServers.getObsServerList():
                return self.__obsServers.getObsProjectPackageList(obsServer=self.__obsServer,
                                                                  projectObsName=self.__projectObsName)
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

        #Find the spec file
        listFile = os.listdir(packagePath)

        specFile = None
        yamlFile = None

        for f in listFile:
            if self.__isASpecfile(f):
                specFile = f
            elif self.__isAyamlfile(f):
                yamlFile = f

        return packagePath, specFile, yamlFile, listFile

    def __isASpecfile(self, file):
        '''
        
        '''
        return file.endswith(".spec")

    def __isAyamlfile(self, file):
        '''
        
        '''
        return file.endswith(".yaml")

    def getPackageStatus(self, package=None):
        '''
        
        '''
        return self.__packages.getPackageStatus(name=package)

    def addPackage(self, name=None):
        '''
        add a package to the projectLocalName.
        '''
        packagePath, specFile, yamlFile, listFile = self.checkoutPackage(package=name)

        status = self.__obsServers.getPackageStatus(obsServer=self.__obsServer,
                                                    project=self.__projectObsName,
                                                    package=name, repo=self.__projectTarget,
                                                    arch=self.__projectArchitecture)

        packageTitle = self.__obsServers.getPackageTitle(obsServer=self.__obsServer,
                                                         projectObsName=self.__projectObsName,
                                                         package=name)

        description = self.__obsServers.getPackageDescription(obsServer=self.__obsServer,
                                                              projectObsName=self.__projectObsName,
                                                              package=name)

        self.__packages.addPackage(name=name,
                                   packagePath=packagePath,
                                   description=description,
                                   packageTitle=packageTitle,
                                   specFile=specFile,
                                   yamlFile=yamlFile,
                                   listFile=listFile,
                                   status=status)

    def isInstallInChroot(self, package):
        '''
        Return True if the package is install into the chroot.
        '''

        return self.__packages.isInstallInChroot(name=package)

    def getGetChRootStatus(self, package):
        '''
        Return the status of the package  into the chroot.
        '''
        return self.__packages.getGetChRootStatus(name=package)

    def getChRootRepositories(self):
        '''
        
        '''
        return self.__chroot.getChRootRepositories()

    def updateProject(self):
        '''
        
        '''
        for name in self.__packages.getListPackages():
            status = self.__obsServers.getPackageStatus(obsServer=self.__obsServer,
                                                        project=self.__projectObsName,
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
        self.__initChRoot()
        self.addRepo()

    def __initChRoot(self):
        '''
        Init a chroot.
        '''
        self.__chroot.createChRoot(repos=self.__projectTarget,
                                   arch=self.__projectArchitecture,
                                   apiurl=self.__obsServer,
                                   obsProject=self.__projectObsName)
        self.__chrootIsInit = True

    def addRepo(self, repos=None,
                      alias=None,
                      chroot=None):
        '''
        
        '''
        if chroot == None:
            __aChroot = self.__chroot
        else:
            __aChroot = chroot
        if repos == None:
            __aRepos = self.getReposProject()
        else:
            __aRepos = repos
        if alias == None:
            __anAlias = self.__projectObsName
        else:
            __anAlias = alias

        if not __aChroot.isAlreadyAReposAlias(__anAlias):
            __aChroot.addRepo(repos=__aRepos  , alias=__anAlias)
        else:
            ObsLightPrintManager.getLogger().info(__anAlias + " is already installed in the chroot")

    def getReposProject(self):
        '''
        Return the URL of the Repo of the Project
        '''
        return os.path.join(self.__obsServers.getRepo(obsServer=self.__obsServer),
                            self.__projectObsName.replace(":", ":/"),
                            self.__projectTarget)

    def goToChRoot(self, package=None, detach=False):
        '''
        
        '''
        if package != None:

            pathPackage = self.__packages.getPackageDirectory(package=package)
            if pathPackage != None:
                self.__chroot.goToChRoot(path=pathPackage, detach=detach)
            else:
                self.__chroot.goToChRoot(detach=detach)
        else:
            self.__chroot.goToChRoot(detach=detach)

    def addPackageSourceInChRoot(self, package=None):
        '''
         
        '''
        specFile = self.__packages.getSpecFile(package)

        self.__chroot.addPackageSourceInChRoot(package=self.__packages.getPackage(package),
                                               specFile=specFile,
                                               repo=self.__projectObsName)

    def makePatch(self, package=None, patch=None):
        '''
        Create a patch
        '''
        self.__chroot.makePatch(package=self.__packages.getPackage(package),
                                patch=patch)

    def commitToObs(self, message=None, package=None):
        '''
        commit the package to the OBS server.
        '''

        self.__packages.getPackage(package).commitToObs(message=message)

    def addRemoveFileToTheProject(self, package=None):
        '''
        add new file and remove file to the project.
        '''
        self.__packages.getPackage(package).addRemoveFileToTheProject()

    def getPackage(self, package=None):
        '''
        
        '''
        return  self.__packages.getPackage(package=package)

    def removePackage(self, package=None):
        '''
        
        '''
        return self.__packages.removePackage(package=package)

    def getWebProjectPage(self):
        '''
        
        '''
        obsServer = self.__obsServers.getObsServer(name=self.__obsServer)

        if obsServer == None:
            return ""
        serverWeb = obsServer.getUrlServerWeb()

        if serverWeb in (None, "None", ""):
            raise ObsLightErr.ObsLightProjectsError("No Web Server")
        res = urllib.basejoin(serverWeb , "project/show?project=" + self.__projectObsName)
        return res

    def addFileToPackage(self, package, path):
        '''
        
        '''

        self.__packages.addFile(package=package, path=path)


    def delFileToPackage(self, package, name):
        '''
        
        '''
        self.__packages.delFile(package=package, name=name)
