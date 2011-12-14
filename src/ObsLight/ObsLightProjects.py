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
import pickle
from ObsLightProject import ObsLightProject
import ObsLightErr

class ObsLightProjects(object):
    '''
    classdocs
    '''
    def __init__(self, obsServers, workingDirectory):
        '''
        Constructor
        '''
        self.__dicOBSLightProjects = {}
        self.__obsServers = obsServers
        self.__currentProjects = None
        self.__workingDirectory = workingDirectory
        self.__pathFile = os.path.join(self.getObsLightWorkingDirectory() , "ObsLightProjectsConfig")

        self.__load()

    def getObsLightWorkingDirectory(self):
        '''
        Returns the OBS Light working directory, usually /home/<user>/OBSLight.
        '''
        return self.__workingDirectory


    def save(self, aFile=None, ProjectName=None):
        '''
        
        '''
        if aFile == None:
            pathFile = self.__pathFile
        else:
            pathFile = aFile

        saveProject = {}

        if ProjectName == None:
            for ProjectName in self.getLocalProjectList():
                saveProject[ProjectName] = self.__dicOBSLightProjects[ProjectName].getDic()
        else:
            saveProject[ProjectName] = self.__dicOBSLightProjects[ProjectName].getDic()

        saveconfigProject = {}
        saveconfigProject["saveProjects"] = saveProject
        saveconfigProject["currentProject"] = self.__currentProjects
        aFile = open(pathFile, 'w')
        pickle.dump(saveconfigProject, aFile)
        aFile.close()

    def __load(self, aFile=None):
        '''
        
        '''
        if aFile == None:
            pathFile = self.__pathFile
            #If default file load, importFile=False and no update on osc directory.
            importFile = False
        else:
            pathFile = aFile
            importFile = False

        if os.path.isfile(pathFile):
            aFile = open(pathFile, 'r')
            try:
                saveconfigServers = pickle.load(aFile)
            except:
                raise  ObsLightErr.ObsLightProjectsError("the file: " + pathFile + " is not a backup")
            aFile.close()

            if not ("saveProjects" in saveconfigServers.keys()):
                raise ObsLightErr.ObsLightProjectsError("the file: " + pathFile + "  is not a backup")
            saveProjects = saveconfigServers["saveProjects"]

            for projetName in saveProjects.keys():
                aServer = saveProjects[projetName]
                self.__addProjectFromSave(name=projetName, fromSave=aServer, importFile=importFile)
            self.__currentProjects = saveconfigServers["currentProject"]

    def getLocalProjectList(self):
        '''
        
        '''
        return self.__dicOBSLightProjects.keys()


    def addProject(self,
                   projectLocalName=None,
                   projectObsName=None,
                   projectTitle=None,
                   obsServer=None ,
                   projectTarget=None,
                   description=None,
                   projectArchitecture=None):
        '''
        
        '''
        projectTitle = self.__obsServers.getProjectTitle(obsServer=obsServer, projectObsName=projectObsName)
        description = self.__obsServers.getProjectDescription(obsServer=obsServer, projectObsName=projectObsName)

        self.__dicOBSLightProjects[projectLocalName] = ObsLightProject(obsServers=self.__obsServers,
                                                                       workingDirectory=self.getObsLightWorkingDirectory(),
                                                                       projectLocalName=projectLocalName,
                                                                       projectObsName=projectObsName,
                                                                       projectTitle=projectTitle,
                                                                       description=description,
                                                                       obsServer=obsServer,
                                                                       projectTarget=projectTarget,
                                                                       projectArchitecture=projectArchitecture)

    def __addProjectFromSave(self, name=None, fromSave=None, importFile=None):
        '''
        
        '''
        if not (name in self.__dicOBSLightProjects.keys()):
            self.__dicOBSLightProjects[name] = ObsLightProject(obsServers=self.__obsServers,
                                                               workingDirectory=self.getObsLightWorkingDirectory(),
                                                               fromSave=fromSave,
                                                               importFile=importFile)
        else:
            raise ObsLightErr.ObsLightProjectsError("Can't import: " + name + ", The Project already exists.")

    def getListPackage(self, name=None, local=0):
        '''
        
        '''
        return self.__dicOBSLightProjects[name].getListPackage(local=local)


    def addPackage(self, projectLocalName=None  , package=None):
        '''
        
        '''
        return self.__dicOBSLightProjects[projectLocalName].addPackage(name=package)

    def createChRoot(self, projectLocalName=None):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName].createChRoot()


    def goToChRoot(self, projectLocalName=None, package=None, detach=False):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName].goToChRoot(package=package,
                                                                detach=detach)

    def openTerminal(self, projectLocalName, package):
        '''
        
        '''
        return  self.__dicOBSLightProjects[projectLocalName].openTerminal(package=package)

    def getPackageFileInfo(self,
                           projectLocalName,
                           packageName,
                           fileName):
        '''
        
        '''
        return  self.__dicOBSLightProjects[projectLocalName].getPackageFileInfo(packageName,
                                                                                fileName)

    def addPackageSourceInChRoot(self, projectLocalName=None, package=None):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName].addPackageSourceInChRoot(package=package)

    def buildRpm(self, projectLocalName, package):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName].buildRpm(package=package)

    def installRpm(self, projectLocalName, package):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName].installRpm(package=package)

    def packageRpm(self, projectLocalName, package):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName].packageRpm(package=package)

    def makePatch(self,
                  projectLocalName=None,
                  package=None,
                  patch=None):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName].makePatch(package=package,
                                                               patch=patch)

    def updatePatch(self, projectLocalName, package):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName].updatePatch(package=package)

    def getObsServer(self, name=None):
        '''
        Return the OBS server name of a project.
        '''
        return  self.__dicOBSLightProjects[name].getObsServer()

    def commitToObs(self, name=None,
                            message=None,
                            package=None):
        '''
        commit the package to the OBS server.
        '''
        self.__dicOBSLightProjects[name].commitToObs(message=message, package=package)

    def addRemoveFileToTheProject(self, name=None,
                                        package=None):
        '''
        add new file and remove file to the project.
        '''
        self.__dicOBSLightProjects[name].getPackage(package=package).addRemoveFileToTheProject()


    def addRepo(self, projectLocalName=None,
                        fromProject=None,
                        repos=None  ,
                        alias=None):
        '''
        
        '''
        if fromProject != None:
            self.__dicOBSLightProjects[fromProject].addRepo(chroot=self.__dicOBSLightProjects[projectLocalName].getChRoot())
        else:
            self.__dicOBSLightProjects[projectLocalName].addRepo(repos=repos,
                                                                 alias=alias)


    def getProjectObsName(self, projectLocalName=None):
        '''
        
        '''
        return self.__dicOBSLightProjects[projectLocalName].getProjectObsName()

    def getProjectParameter(self, projectLocalName=None, parameter=None):
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
        return self.__dicOBSLightProjects[projectLocalName].getProjectParameter(parameter=parameter)

    def setProjectParameter(self, projectLocalName=None, parameter=None, value=None):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName].setProjectParameter(parameter=parameter,
                                                                         value=value)

    def getPackageParameter(self, projectLocalName, package, parameter=None):
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
        return  self.__dicOBSLightProjects[projectLocalName].getPackageParameter(package=package,
                                                                                 parameter=parameter)

    def setPackageParameter(self, projectLocalName, package, parameter=None, value=None):
        '''
        return the value  of the parameter of the package:
        the valid parameter is :
            specFile
            yamlFile
            packageDirectory
            description
            packageTitle
        '''
        return  self.__dicOBSLightProjects[projectLocalName].setPackageParameter(package=package,
                                                                                 parameter=parameter,
                                                                                 value=value)


    def getPackageDirectory(self, projectLocalName, packageName):
        package = self.__dicOBSLightProjects[projectLocalName].getPackage(packageName)
        return package.getOscDirectory()

    def getPackageDirectoryInChRoot(self, projectLocalName, packageName):
        package = self.__dicOBSLightProjects[projectLocalName].getPackage(packageName)
        return package.getPackageDirectory()

    def setProjectparameter(self, projectLocalName=None, parameter=None, value=None):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName].setProjectparameter(parameter=parameter,
                                                                         value=value)

    def removeProject(self, projectLocalName=None):
        '''
        
        '''
        projetPath = self.__dicOBSLightProjects[projectLocalName].getDirectory()

        self.__dicOBSLightProjects[projectLocalName].removeProject()

        if not os.path.isdir(projetPath):
            del self.__dicOBSLightProjects[projectLocalName]
            return None
        else:
            raise ObsLightErr.ObsLightProjectsError("Error in removeProject, can't remove project directory.")

    def removeChRoot(self, projectLocalName):
        '''
        
        '''
        return self.__dicOBSLightProjects[projectLocalName].removeChRoot()


    def getReposProject(self, projectLocalName):
        '''
        Return the URL of the Repo of the Project
        '''
        return self.__dicOBSLightProjects[projectLocalName].getReposProject()

    def getChRootPath(self, projectLocalName):
        '''
        Return the path of aChRoot of a project
        '''
        return self.__dicOBSLightProjects[projectLocalName].getChRootPath()

    def removePackage(self, projectLocalName=None, package=None):
        '''
        Remove a package from local project.
        '''
        return self.__dicOBSLightProjects[projectLocalName].removePackage(package=package)

    def importProject(self, path=None):
        '''
        Import a project from a file
        '''
        self.__load(aFile=path)


    def exportProject(self, projectLocalName=None, path=None):
        '''
        Export a project to a file
        '''
        self.save(aFile=path, ProjectName=projectLocalName)

    def getWebProjectPage(self, projectLocalName):
        '''
        
        '''
        return self.__dicOBSLightProjects[projectLocalName].getWebProjectPage()

    def getPackageStatus(self, project, package):
        '''
        
        '''
        return self.__dicOBSLightProjects[project].getPackageStatus(package=package)

    def isChRootInit(self, projectLocalName):
        '''
        Return True if the ChRoot is init otherwise False.
        '''
        return self.__dicOBSLightProjects[projectLocalName].isChRootInit()

    def isInstallInChroot(self, projectLocalName, package):
        '''
        Return True if the package is install into the chroot.
        '''
        return self.__dicOBSLightProjects[projectLocalName].isInstallInChroot(package=package)

    def getGetChRootStatus(self, projectLocalName, package):
        '''
        Return the status of the package  into the chroot.
        '''
        return self.__dicOBSLightProjects[projectLocalName].getGetChRootStatus(package=package)

    def getChRootRepositories(self, projectLocalName):
        '''
        
        '''
        return self.__dicOBSLightProjects[projectLocalName].getChRootRepositories()

    def addFileToPackage(self, projectLocalName, package, path):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName].addFileToPackage(package=package,
                                                                      path=path)

    def delFileToPackage(self, projectLocalName, package, name):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName].delFileToPackage(package=package,
                                                                      name=name)

    def updatePackage(self, projectLocalName, package):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName].updatePackage(name=package)

    def deleteRepo(self, projectLocalName, repoAlias):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName].deleteRepo(repoAlias)

    def modifyRepo(self, projectLocalName, repoAlias, newUrl, newAlias):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName].modifyRepo(repoAlias, newUrl, newAlias)

    def getOscPackageStatus(self, project, package):
        '''
        
        '''
        return self.__dicOBSLightProjects[project].getOscPackageStatus(package)

    def refreshOscDirectoryStatus(self, projectLocalName, package=None):
        '''
        
        '''
        return self.__dicOBSLightProjects[projectLocalName].refreshOscDirectoryStatus(package=package)

    def refreshObsStatus(self, projectLocalName, package=None):
        '''
        
        '''
        return self.__dicOBSLightProjects[projectLocalName].refreshObsStatus(package=package)

    def repairOscPackageDirectory(self, projectLocalName, package):
        '''
        
        '''
        return self.__dicOBSLightProjects[projectLocalName].repairOscPackageDirectory(package=package)

    def getOscPackageRev(self,
                          projectLocalName,
                          packageName):
        '''
        
        '''
        return self.__dicOBSLightProjects[projectLocalName].getOscPackageRev(packageName)

    def getObsPackageRev(self,
                          projectLocalName,
                          packageName):
        '''
        
        '''
        return self.__dicOBSLightProjects[projectLocalName].getObsPackageRev(packageName)

    def patchIsInit(self, ProjectName, packageName):
        '''
        
        '''
        return self.__dicOBSLightProjects[ProjectName].patchIsInit(packageName=packageName)









