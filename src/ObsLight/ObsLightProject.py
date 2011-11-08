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

class ObsLightProject(object):
    '''
    classdocs
    '''

    def __init__(self, obsServers,
                       projectLocalName=None,
                       projectObsName=None,
                       projectTitle=None,
                       projectDirectory=None,
                       chrootDirectory=None,
                       obsServer=None ,
                       projectTarget=None,
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

        if fromSave == None:
            self.__projectLocalName = projectLocalName
            self.__projectObsName = projectObsName
            self.__projectDirectory = projectDirectory
            self.__obsServer = obsServer
            self.__projectTarget = projectTarget
            self.__projectArchitecture = projectArchitecture
            self.__projectTitle = projectTitle
            self.__description = description

            if chrootDirectory == None:
                chrootDirectory = os.path.join(projectDirectory, "aChroot")

            self.__chroot = ObsLightChRoot(chrootDirectory=chrootDirectory,
                                         chrootDirTransfert=projectDirectory + "/chrootTransfert",
                                         dirTransfert="/chrootTransfert")
            self.__packages = ObsLightPackages()

            #perhaps a trusted_prj must be had
            self.__obsServers.getObsServer(name=self.__obsServer).initConfigProject(projet=self.__projectObsName,
                                                                                                    repos=self.__projectTarget)
        else:
            if "projectLocalName" in fromSave.keys():
                self.__projectLocalName = fromSave["projectLocalName"]
            if "projectObsName" in fromSave.keys():
                self.__projectObsName = fromSave["projectObsName"]
            if "projectDirectory" in fromSave.keys():
                self.__projectDirectory = fromSave["projectDirectory"]
            if "obsServer" in fromSave.keys():
                self.__obsServer = fromSave["obsServer"]
            if "projectTarget" in fromSave.keys():
                self.__projectTarget = fromSave["projectTarget"]
            if "projectArchitecture" in fromSave.keys():
                self.__projectArchitecture = fromSave["projectArchitecture"]
            if "projectTitle" in fromSave.keys():
                self.__projectTitle = fromSave["projectTitle"]
            if "description" in fromSave.keys():
                self.__description = fromSave["description"]

            if "aChroot" in fromSave.keys():
                self.__chroot = ObsLightChRoot(fromSave=fromSave["aChroot"])
            else:
                raise ObsLightErr.ObsLightProjectsError("aChroot is not ")

            if "packages" in fromSave.keys():
                self.__packages = self.__addPackagesFromSave(fromSave=fromSave["packages"], importFile=importFile)

            if "chrootIsInit" in fromSave.keys():
                self.__chrootIsInit = fromSave["chrootIsInit"]
                if self.__chrootIsInit == True:
                    if not os.path.isdir(self.__chroot.getDirectory()):
                        self.createChRoot()
                else:
                    if os.path.isdir(self.__chroot.getDirectory()):
                        self.__chrootIsInit = True


            if self.__chrootIsInit:
                for packageName in self.__packages.getListPackages():
                    if self.__packages.isInstallInChroot(packageName):
                        absPackagePath = os.path.join(self.__chroot.getDirectory() , self.__packages.getPackageDirectory(packageName))
                        if not os.path.isdir(absPackagePath) :
                            self.addPackageSourceInChRoot(package=packageName)


        if not os.path.isdir(self.__projectDirectory):
            os.makedirs(self.__projectDirectory)



    def getDirectory(self):
        '''
        Return the project directory.
        '''
        return self.__projectDirectory

    def __addPackagesFromSave(self, fromSave, importFile):
        '''
        check and add a package from a save.
        '''
        for packageName in fromSave["savePackages"].keys():
            packageFromSave = fromSave["savePackages"][packageName]
            if "name" in packageFromSave.keys(): name = packageFromSave["name"]
            packagePath = self.__getPackagePath(name)
            if not os.path.isdir(self.__getPackagePath(name)):
                specFile, yamlFile, listFile = self.checkoutPackage(package=name)
                packageFromSave["specFile"] = specFile
                packageFromSave["yamlFile"] = yamlFile
                packageFromSave["listFile"] = listFile

            toUpDate = False
            if "listFile" in packageFromSave.keys():listFile = packageFromSave["listFile"]
            for aFile in listFile:
                if not os.path.isfile(os.path.join(packagePath, aFile)):
                    toUpDate = True

            if "specFile" in packageFromSave.keys():
                specFilePath = packageFromSave["specFile"]
                if not os.path.isfile(specFilePath):
                    toUpDate = True
            if "yamlFile" in packageFromSave.keys() and packageFromSave["yamlFile"] is not None:
                yamlFilePath = packageFromSave["yamlFile"]
                if not os.path.isfile(yamlFilePath):
                    toUpDate = True

            if importFile == True:
                toUpDate = False
                if "listFile" in packageFromSave.keys():listFile = packageFromSave["listFile"]
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

        return ObsLightPackages(fromSave)

    def getProjectInfo(self, info=None):
        '''
        return the value  of the info of the project:
        the valide info is :
            projectLocalName
            projectObsName
            projectDirectory
            obsServer
            projectTarget
            "projectArchitecture
            projectTitle
            description
        '''
        if info == "projectLocalName":
            return self.__projectLocalName
        elif info == "projectObsName":
            return self.__projectObsName
        elif info == "projectDirectory":
            return self.__projectDirectory
        elif info == "obsServer":
            return self.__obsServer
        elif info == "projectTarget":
            return self.__projectTarget
        elif info == "projectArchitecture":
            return self.__projectArchitecture
        elif info == "projectTitle":
            return self.__projectTitle
        elif info == "description":
            return self.__description
        else:
            raise ObsLightErr.ObsLightProjectsError("info value is not valide for getProjectInfo")

    def setProjectparameter(self, parameter=None, value=None):
        '''
        return the value  of the parameter of the project:
        the valide parameter is :
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
            raise ObsLightErr.ObsLightProjectsError("parameter value is not valide for getProjectInfo")

    def __subprocess(self, command=None, waitMess=False):
        '''
        
        '''
        return self.__mySubprocessCrt.execSubprocess(command=command, waitMess=waitMess)

    def removeProject(self):
        '''
        
        '''
        res = self.__chroot.removeChRoot()
        self.__chrootIsInit = False

        if res == 0:
            return shutil.rmtree(self.__projectDirectory)
        else:
            raise ObsLightErr.ObsLightProjectsError("Error in removeProject, can't remove chroot")

        return 0

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
        aDic["projectDirectory"] = self.__projectDirectory
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
            return self.__obsServers.getObsProjectPackageList(obsServer=self.__obsServer,
                                                                                  projectLocalName=self.__projectObsName)
        else:
            return self.__packages.getListPackages()

    def __getPackagePath(self, package):
        '''
        
        '''
        return os.path.join(self.__projectDirectory, self.__projectObsName, package)

    def checkoutPackage(self, package=None):
        '''
        
        '''
        ObsLightOsc.getObsLightOsc().checkoutPackage(obsServer=self.__obsServer,
                                                    projectObsName=self.__projectObsName,
                                                    package=package,
                                                    directory=self.__projectDirectory)

        packagePath = self.__getPackagePath(package)

        #Find the spec file
        listFile = os.listdir(packagePath)

        specFile = None
        yamlFile = None

        for f in listFile:
            if f.endswith(".spec"):
                specFile = os.path.join(packagePath, f)
            elif f.endswith(".yaml"):
                yamlFile = os.path.join(packagePath, f)

        return specFile, yamlFile, listFile

    def getPackageStatus(self, package=None):
        '''
        
        '''
        return self.__packages.getPackageStatus(name=package)

    def addPackage(self, name=None):
        '''
        add a package to the projectLocalName.
        '''
        specFile, yamlFile, listFile = self.checkoutPackage(package=name)
        status = self.__obsServers.getPackageStatus(obsServer=self.__obsServer, project=self.__projectObsName, package=name, repo=self.__projectTarget, arch=self.__projectArchitecture)
        self.__packages.addPackage(name=name,
                                   specFile=specFile,
                                   yamlFile=yamlFile,
                                   listFile=listFile,
                                   status=status)

    def isInstallInChroot(self, package):
        '''
        Return True if the package is install into the chroot.
        '''

        return self.__packages.isInstallInChroot(name=package)

    def updateProject(self):
        '''
        
        '''
        for name in self.__packages.getListPackages():
            status = self.__obsServers.getPackageStatus(obsServer=self.__obsServer, project=self.__projectObsName, package=name, repo=self.__projectTarget, arch=self.__projectArchitecture)

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
        
        '''
        #I hope this will change, because we don't need to build a pakage to creat a chroot. 
        for pk in self.__packages.getListPackages():
            #if self.__packages.getPackageStatus(pk)=="succeeded":
            specPath = self.__packages.getSpecFile(pk)
            projectDir = self.__packages.getOscDirectory(pk)
            break


        self.__chroot.createChRoot(#obsApi=self.__obsServer,
                                    projectDir=projectDir ,
                                    repos=self.__projectTarget,
                                    arch=self.__projectArchitecture,
                                    specPath=specPath)
        self.__chrootIsInit = True
        self.addRepo()

    def addRepo(self,
                 repos=None,
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

        __aChroot.addRepo(repos=__aRepos  , alias=__anAlias)


    def getReposProject(self):
        '''
        
        '''
        return os.path.join(self.__obsServers.getRepo(obsServer=self.__obsServer), self.__projectObsName.replace(":", ":/"), self.__projectTarget)

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
        specFile = os.path.basename(self.__packages.getSpecFile(package))
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
        serverWeb = self.__obsServers.getObsServer(name=self.__obsServer).getUrlServerWeb()

        if serverWeb in (None, "None", ""):
            raise ObsLightErr.ObsLightProjectsError("No Web Server")
        return urllib.basejoin(serverWeb , "project/show?project=" + self.__projectObsName)


