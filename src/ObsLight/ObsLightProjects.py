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
import pickle
from ObsLightProject import ObsLightProject
import ObsLightErr
import ObsLightTools
import collections

class ObsLightProjects(object):
    '''
    classdocs
    '''
    def __init__(self, obsServers, workingDirectory):
        '''
        Constructor
        '''
        self.__saveconfigProject = None

        self.__dicOBSLightProjects = {}
        self.__dicOBSLightProjects_unload = {}

        self.__obsServers = obsServers
        self.__currentProjects = None
        self.__workingDirectory = os.path.join(workingDirectory, "ObsProjects")
        self.__pathFile = os.path.join(workingDirectory, "ObsLightProjectsConfig")

    #---------------------------------------------------------------------------
    def getLocalProjectList(self):
        '''
        
        '''
        self.__load()
        res = self.__dicOBSLightProjects.keys()
        res.extend(self.__dicOBSLightProjects_unload.keys())
        res.sort()
        return res

    def __load(self, aFile=None):
        '''
        
        '''
        if ((len(self.__dicOBSLightProjects.keys()) == 0) and (len(self.__dicOBSLightProjects_unload.keys()) == 0)) or (aFile != None):
            if aFile == None:
                pathFile = self.__pathFile
                #If default file load, importFile=False and no update on osc directory.
            else:
                pathFile = aFile

            if os.path.isfile(pathFile):
                aFile = open(pathFile, 'r')
                try:
                    self.__saveconfigProject = pickle.load(aFile)
                except:
                    raise  ObsLightErr.ObsLightProjectsError("the file: " + pathFile + " is not a backup")
                aFile.close()

                if (not "saveProjects" in self.__saveconfigProject.keys()) or (not "currentProject" in self.__saveconfigProject.keys()):
                    raise ObsLightErr.ObsLightProjectsError("the file: " + pathFile + "  is not a backup")

                self.__dicOBSLightProjects_unload = self.__saveconfigProject["saveProjects"]

#                for projetName in saveProjects.keys():
#                    aServer = saveProjects[projetName]
#                    self.__addProjectFromSave(name=projetName, fromSave=aServer)

                self.__currentProjects = self.__saveconfigProject["currentProject"]

    def save(self, aFile=None, projectName=None):
        '''
        
        '''
        if aFile == None:
            pathFile = self.__pathFile
            projectName = None
        else:
            pathFile = aFile

        saveProject = {}

        if projectName == None:
            for aProjectName in self.__dicOBSLightProjects.keys():
                saveProject[aProjectName] = self.__dicOBSLightProjects[aProjectName].getDic()
            for aProjectName in self.__dicOBSLightProjects_unload.keys():
                saveProject[aProjectName] = self.__dicOBSLightProjects_unload[aProjectName]
        else:
            if projectName in self.__dicOBSLightProjects.keys():
                saveProject[projectName] = self.__dicOBSLightProjects[projectName].getDic()
            elif projectName in self.__dicOBSLightProjects_unload.keys():
                saveProject[projectName] = self.__dicOBSLightProjects_unload[projectName]
            else:
                raise ObsLightErr.ObsLightProjectsError("Can't save project '" + projectName + "' ,it doen't exist.")

        saveconfigProject = {}
        saveconfigProject["saveProjects"] = saveProject
        saveconfigProject["currentProject"] = self.__currentProjects

        if (projectName != None) or (saveconfigProject != self.__saveconfigProject):
            aFile = open(pathFile, 'w')
            pickle.dump(saveconfigProject, aFile)
            aFile.close()

        if projectName == None:
            self.__saveconfigProject = saveconfigProject

    def getProject(self, project):
        '''
        
        '''
        self.__load()

        if project in self.__dicOBSLightProjects_unload.keys():
            aServer = self.__dicOBSLightProjects_unload[project]
            self.__addProjectFromSave(name=project, fromSave=aServer)
            del self.__dicOBSLightProjects_unload[project]

        if project in self.__dicOBSLightProjects.keys():
            if self.__currentProjects != project:
                self.__currentProjects = project
                self.save()

            return self.__dicOBSLightProjects[project]
        else:
            raise ObsLightErr.ObsLightProjectsError("the project: '" + project + "'  is not a local project.")


    def removeProject(self, projectLocalName=None):
        '''
        
        '''
        projetPath = self.getProject(projectLocalName).getDirectory()

        self.getProject(projectLocalName).removeProject()
        if not os.path.isdir(projetPath):
            del self.__dicOBSLightProjects[projectLocalName]
        else:
            raise ObsLightErr.ObsLightProjectsError("Error in removeProject, can't remove project directory.")

        self.__currentProjects = None
        self.save()
        return 0

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
        return 0

    def getCurrentProject(self):
        '''
        
        '''
        self.__load()
        return self.__currentProjects

    def addProject(self,
                   projectLocalName=None,
                   projectObsName=None,
                   obsServer=None ,
                   projectTarget=None,
                   projectArchitecture=None):
        '''
        
        '''
        projectTitle = self.__obsServers.getProjectTitle(obsServer=obsServer, projectObsName=projectObsName)
        description = self.__obsServers.getProjectDescription(obsServer=obsServer, projectObsName=projectObsName)

        if (projectLocalName in self.__dicOBSLightProjects_unload.keys()) or\
           (projectLocalName in self.__dicOBSLightProjects.keys()):
            raise ObsLightErr.ObsLightProjectsError("The projectLocalName '" + projectLocalName + "' all ready exist")

        self.__dicOBSLightProjects[projectLocalName] = ObsLightProject(obsServers=self.__obsServers,
                                                                       workingDirectory=self.getObsLightWorkingDirectory(),
                                                                       projectLocalName=projectLocalName,
                                                                       projectObsName=projectObsName,
                                                                       projectTitle=projectTitle,
                                                                       description=description,
                                                                       obsServer=obsServer,
                                                                       projectTarget=projectTarget,
                                                                       projectArchitecture=projectArchitecture)

    #---------------------------------------------------------------------------
    def getPackageStatus(self, project, package):
        '''
        
        '''
        return self.getProject(project).getPackageStatus(package=package)

    def getGetChRootStatus(self, projectLocalName, package):
        '''
        Return the status of the package  into the chroot.
        '''
        return self.getProject(projectLocalName).getGetChRootStatus(package=package)

    def getOscPackageStatus(self, project, package):
        '''
        
        '''
        return self.getProject(project).getOscPackageStatus(package)

    def getOscPackageRev(self,
                         projectLocalName,
                         packageName):
        '''
        
        '''
        return self.getProject(projectLocalName).getOscPackageRev(packageName)

    def getObsPackageRev(self,
                         projectLocalName,
                         packageName):
        '''
        
        '''
        return self.getProject(projectLocalName).getObsPackageRev(packageName)
    #---------------------------------------------------------------------------
    def getPackageFilter(self, projectLocalName):
        return self.getProject(projectLocalName).getPackageFilter()

    def resetPackageFilter(self, projectLocalName):
        return self.getProject[projectLocalName].resetPackageFilter()

    def removePackageFilter(self, projectLocalName, key):
        return self.getProject(projectLocalName).removePackageFilter(key=key)

    def addPackageFilter(self, projectLocalName, key, val):
        return self.getProject(projectLocalName).addPackageFilter(key=key, val=val)

    def getListStatus(self, projectLocalName):
        return self.getProject(projectLocalName).getListStatus()

    def getListOscStatus(self, projectLocalName):
        return self.getProject(projectLocalName).getListOscStatus()

    def getListChRootStatus(self, projectLocalName):
        return self.getProject(projectLocalName).getListChRootStatus()

    def getPackageInfo(self, projectLocalName, package=None):
        return self.getProject(projectLocalName).getPackageInfo(package=package)

    #---------------------------------------------------------------------------

    def getObsLightWorkingDirectory(self):
        '''
        Returns the OBS Light working directory, usually /home/<user>/OBSLight.
        '''
        return self.__workingDirectory

    def openTerminal(self, projectLocalName, package):
        '''
        
        '''
        return  self.getProject(projectLocalName).openTerminal(package=package)

    def getPackageFileInfo(self,
                           projectLocalName,
                           packageName,
                           fileName):
        '''
        
        '''
        return  self.getProject(projectLocalName).getPackageFileInfo(packageName, fileName)

    def addPackageSourceInChRoot(self, projectLocalName=None, package=None):
        '''
        
        '''
        self.getProject(projectLocalName).addPackageSourceInChRoot(package=package)

    def buildRpm(self, projectLocalName, package):
        '''
        
        '''
        self.getProject(projectLocalName).buildRpm(package=package)

    def installRpm(self, projectLocalName, package):
        '''
        
        '''
        self.getProject(projectLocalName).installRpm(package=package)

    def packageRpm(self, projectLocalName, package):
        '''
        
        '''
        self.getProject(projectLocalName).packageRpm(package=package)

    def makePatch(self,
                  projectLocalName=None,
                  package=None,
                  patch=None):
        '''
        
        '''
        self.getProject(projectLocalName).makePatch(package=package,
                                                               patch=patch)

    def updatePatch(self, projectLocalName, package):
        '''
        
        '''
        self.getProject(projectLocalName).updatePatch(package=package)

    def getObsServer(self, name=None):
        '''
        Return the OBS server name of a project.
        '''
        return  self.getProject(name).getObsServer()

    def getPackageFileList(self, projectLocalName, packageName):
        '''
        
        '''
        return self.getProject(projectLocalName).getPackageFileList(packageName)

    def getProjectObsName(self, projectLocalName=None):
        '''
        
        '''
        return self.getProject(projectLocalName).getProjectObsName()

    def getPackageDirectory(self, projectLocalName, packageName):
        package = self.getProject(projectLocalName).getPackage(packageName)
        return package.getOscDirectory()

    def getPackageDirectoryInChRoot(self, projectLocalName, packageName):
        package = self.getProject(projectLocalName).getPackage(packageName)
        return package.getPackageDirectory()

    def setProjectparameter(self, projectLocalName=None, parameter=None, value=None):
        '''
        
        '''
        self.getProject(projectLocalName).setProjectparameter(parameter=parameter,
                                                                         value=value)

    def importProject(self, path=None):
        '''
        Import a project from a file
        '''
        self.__load(aFile=path)


    def exportProject(self, projectLocalName=None, path=None):
        '''
        Export a project to a file
        '''
        self.save(aFile=path, projectName=projectLocalName)

    def isInstallInChroot(self, projectLocalName, package):
        '''
        Return True if the package is install into the chroot.
        '''
        return self.getProject(projectLocalName).isInstallInChroot(package=package)

    def addFileToPackage(self, projectLocalName, package, path):
        '''
        
        '''
        self.getProject(projectLocalName).addFileToPackage(package=package,
                                                                      path=path)

    def delFileToPackage(self, projectLocalName, package, name):
        '''
        
        '''
        self.getProject(projectLocalName).delFileToPackage(package=package,
                                                                      name=name)

    def updatePackage(self, projectLocalName, package, controlFunction=None):
        '''
        
        '''
        if (isinstance(package, collections.Iterable) and
            not isinstance(package, str) and
            not isinstance(package, unicode)):
            theBadResult = ObsLightTools.mapProcedureWithThreads(parameterList=package,
                                                                  procedure=self.getProject(projectLocalName).updatePackage,
                                                                  progress=controlFunction)
            if len(theBadResult) > 0:
                return 1
            else:
                return 0
        else:
            return self.getProject(projectLocalName).updatePackage(name=package)

    def modifyRepo(self, projectLocalName, repoAlias, newUrl, newAlias):
        '''
        
        '''
        self.getProject(projectLocalName).modifyRepo(repoAlias, newUrl, newAlias)


    def refreshOscDirectoryStatus(self, projectLocalName, package, controlFunction=None):
        '''
        
        '''
        if (isinstance(package, collections.Iterable) and
            not isinstance(package, str) and
            not isinstance(package, unicode)):
            theBadResult = ObsLightTools.mapProcedureWithThreads(parameterList=package,
                                                                  procedure=self.getProject(projectLocalName).refreshOscDirectoryStatus,
                                                                  progress=controlFunction)
            if len(theBadResult) > 0:
                return 1
            else:
                return 0
        else:
            return self.getProject(projectLocalName).refreshOscDirectoryStatus(package=package)

    def refreshObsStatus(self, projectLocalName, package, controlFunction=None):
        '''
        
        '''
        if (isinstance(package, collections.Iterable) and
            not isinstance(package, str) and
            not isinstance(package, unicode)):
            theBadResult = ObsLightTools.mapProcedureWithThreads(parameterList=package,
                                                                  procedure=self.getProject(projectLocalName).refreshObsStatus,
                                                                  progress=controlFunction)
            if len(theBadResult) > 0:
                return 1
            else:
                return 0
        else:
            return self.getProject(projectLocalName).refreshObsStatus(package=package)

    def patchIsInit(self, ProjectName, packageName):
        '''
        
        '''
        return self.getProject(ProjectName).patchIsInit(packageName=packageName)


    def testConflict(self, projectLocalName, package):
        '''
        
        '''
        return self.getProject(projectLocalName).testConflict(package)






