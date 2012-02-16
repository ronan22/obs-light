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
                self.__dicOBSLightProjects_unload = {}
                self.__dicOBSLightProjects = {}
                #If default file load, importFile=False and no update on osc directory.
            else:
                self.__load()
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

                for p in self.__saveconfigProject["saveProjects"].keys():
                    if (p in self.__dicOBSLightProjects_unload.keys()) or (p in self.__dicOBSLightProjects.keys()):
                        raise ObsLightErr.ObsLightProjectsError("Can't import project: '" + p + "' already a obslight project.")
                    self.__dicOBSLightProjects_unload[p] = self.__saveconfigProject["saveProjects"][p]

                self.__currentProjects = self.__saveconfigProject["currentProject"]
            return 0

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

        return 0

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
        projectTitle = self.__obsServers.getObsServer(obsServer).getProjectTitle(projectObsName)
        description = self.__obsServers.getObsServer(obsServer).getProjectDescription(projectObsName)

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
        return 0

    #---------------------------------------------------------------------------

    def getObsLightWorkingDirectory(self):
        '''
        Returns the OBS Light working directory, usually /home/<user>/OBSLight.
        '''
        return self.__workingDirectory

    def importProject(self, path=None):
        '''
        Import a project from a file
        '''
        return self.__load(aFile=path)


    def exportProject(self, projectLocalName=None, path=None):
        '''
        Export a project to a file
        '''
        return self.save(aFile=path, projectName=projectLocalName)

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








