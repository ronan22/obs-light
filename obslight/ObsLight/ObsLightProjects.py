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
import pickle
from ObsLightProject import ObsLightProject
import ObsLightErr
import ObsLightTools
import collections
import shutil

class ObsLightProjects(object):

    def __init__(self, obsServers, obsLightRepositories, workingDirectory):
        self.__saveconfigProject = None

        self.__dicOBSLightProjects = {}
        self.__dicOBSLightProjects_unload = {}

        self.__obsServers = obsServers
        self.__obsLightRepositories = obsLightRepositories
        self.__currentProjects = None
        self.__workingDirectory = os.path.join(workingDirectory, "ObsProjects")
        self.__pathFile = os.path.join(workingDirectory, "ObsLightProjectsConfig")
        self.__pathFileBackUp = self.__pathFile + ".backup"

    #---------------------------------------------------------------------------
    def getLocalProjectList(self):
        self.__load()
        res = self.__dicOBSLightProjects.keys()
        res.extend(self.__dicOBSLightProjects_unload.keys())
        res.sort()
        return res

    def __load(self, aFile=None):
        if ((len(self.__dicOBSLightProjects.keys()) == 0) and \
           (len(self.__dicOBSLightProjects_unload.keys()) == 0)) or (aFile is not None):
            if aFile is None:
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
                    message = "the file: %s is not a backup" % pathFile
                    raise  ObsLightErr.ObsLightProjectsError(message)
                aFile.close()

                if (not "saveProjects" in self.__saveconfigProject.keys()) or \
                   (not "currentProject" in self.__saveconfigProject.keys()):
                    message = "the file: " + pathFile + "  is not a backup"
                    raise ObsLightErr.ObsLightProjectsError(message)

                for prj in self.__saveconfigProject["saveProjects"].keys():
                    if (prj in self.__dicOBSLightProjects_unload.keys()) or \
                       (prj in self.__dicOBSLightProjects.keys()):
                        message = "Can't import project: '%p' already a obslight project." % prj
                        raise ObsLightErr.ObsLightProjectsError(message)
                    self.__dicOBSLightProjects_unload[prj] = self.__saveconfigProject["saveProjects"][prj]

                self.__currentProjects = self.__saveconfigProject["currentProject"]
            return 0

    def save(self, aFile=None, projectName=None):
        if aFile is None:
            pathFileBackUp = self.__pathFileBackUp
            pathFile = self.__pathFile
            projectName = None
        else:
            pathFileBackUp = aFile + ".backup"
            pathFile = aFile

        saveProject = {}

        if projectName is None:
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
                mesage = "Can't save project '%s' ,it doen't exist." % projectName
                raise ObsLightErr.ObsLightProjectsError(mesage)

        saveconfigProject = {}
        saveconfigProject["saveProjects"] = saveProject
        saveconfigProject["currentProject"] = self.__currentProjects

        if (projectName is not None) or (saveconfigProject != self.__saveconfigProject):

            with open(pathFileBackUp, 'w') as aFile:
                pickle.dump(saveconfigProject, aFile)
                aFile.flush()
                os.fsync(aFile.fileno())

            aFile = open(pathFileBackUp, 'r')
            try:
                if os.path.isfile(pathFileBackUp):
                    _ = pickle.load(aFile)
                    shutil.copyfile(pathFileBackUp, pathFile)
            except:
                message = "the file: %s is not a backup" % pathFileBackUp
                raise  ObsLightErr.ObsLightProjectsError(message)
            finally:
                aFile.close()



            if projectName is None:
                self.__saveconfigProject = saveconfigProject

        return 0

    def getProject(self, project):
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
            message = "the project: '%s'  is not a local project." % project
            raise ObsLightErr.ObsLightProjectsError(message)


    def removeProject(self, projectLocalName=None):
        projetPath = self.getProject(projectLocalName).getDirectory()

        self.getProject(projectLocalName).removeProject()
        if not os.path.isdir(projetPath):
            del self.__dicOBSLightProjects[projectLocalName]
        else:
            message = "Error in removeProject, can't remove project directory."
            raise ObsLightErr.ObsLightProjectsError(message)

        self.__currentProjects = None
        self.save()
        return 0

    def __addProjectFromSave(self, name=None, fromSave=None):
        if not (name in self.__dicOBSLightProjects.keys()):
            project = ObsLightProject(obsServers=self.__obsServers,
                                      obsLightRepositories=self.__obsLightRepositories,
                                    workingDirectory=self.getObsLightWorkingDirectory(),
                                    fromSave=fromSave)
            self.__dicOBSLightProjects[name] = project
        else:
            message = "Can't import: %s, The Project already exists." % name
            raise ObsLightErr.ObsLightProjectsError(message)
        return 0

    def getCurrentProject(self):
        self.__load()
        return self.__currentProjects

    def addProject(self,
                   projectLocalName=None,
                   projectObsName=None,
                   obsServer=None ,
                   projectTarget=None,
                   projectArchitecture=None):
        projectTitle = self.__obsServers.getObsServer(obsServer).getProjectTitle(projectObsName)
        description = self.__obsServers.getObsServer(obsServer).getProjectDescription(projectObsName)

        if (projectLocalName in self.__dicOBSLightProjects_unload.keys()) or\
           (projectLocalName in self.__dicOBSLightProjects.keys()):
            message = "The projectLocalName '%s' all ready exist" % projectLocalName
            raise ObsLightErr.ObsLightProjectsError(message)

        project = ObsLightProject(obsServers=self.__obsServers,
                                  obsLightRepositories=self.__obsLightRepositories,
                                  workingDirectory=self.getObsLightWorkingDirectory(),
                                  projectLocalName=projectLocalName,
                                  projectObsName=projectObsName,
                                  projectTitle=projectTitle,
                                  description=description,
                                  obsServer=obsServer,
                                  projectTarget=projectTarget,
                                  projectArchitecture=projectArchitecture)
        self.__dicOBSLightProjects[projectLocalName] = project
        return 0

    #---------------------------------------------------------------------------

    def getObsLightWorkingDirectory(self):
        '''
        Returns the OBS Light working directory, usually /home/<user>/OBSLight.
        '''
        return self.__workingDirectory

#    def importProject(self, path=None):
#        '''
#        Import a project from a file
#        '''
#        return self.__load(aFile=path)
#
#
#    def exportProject(self, projectLocalName=None, path=None):
#        '''
#        Export a project to a file
#        '''
#        return self.save(aFile=path, projectName=projectLocalName)

    def updatePackage(self, projectLocalName, package, controlFunction=None):
        if (isinstance(package, collections.Iterable) and
            not isinstance(package, str) and
            not isinstance(package, unicode)):
            procedure = self.getProject(projectLocalName).updatePackage
            theBadResult = ObsLightTools.mapProcedureWithThreads(parameterList=package,
                                                                  procedure=procedure,
                                                                  progress=controlFunction)
            if len(theBadResult) > 0:
                return 1
            else:
                return 0
        else:
            return self.getProject(projectLocalName).updatePackage(name=package)

    def refreshPackageDirectoryStatus(self, projectLocalName, package, controlFunction=None):
        if (isinstance(package, collections.Iterable) and
            not isinstance(package, str) and
            not isinstance(package, unicode)):
            procedure = self.getProject(projectLocalName).refreshPackageDirectoryStatus
            theBadResult = ObsLightTools.mapProcedureWithThreads(parameterList=package,
                                                                  procedure=procedure,
                                                                  progress=controlFunction)
            if len(theBadResult) > 0:
                return 1
            else:
                return 0
        else:
            return self.getProject(projectLocalName).refreshPackageDirectoryStatus(package=package)

    def refreshObsStatus(self, projectLocalName, package, controlFunction=None):
        if (isinstance(package, collections.Iterable) and
            not isinstance(package, str) and
            not isinstance(package, unicode)):
            procedure = self.getProject(projectLocalName).refreshObsStatus
            theBadResult = ObsLightTools.mapProcedureWithThreads(parameterList=package,
                                                                  procedure=procedure,
                                                                  progress=controlFunction)
            if len(theBadResult) > 0:
                return 1
            else:
                return 0
        else:
            return self.getProject(projectLocalName).refreshObsStatus(package=package)

    def importPrepBuildPackages(self, projectName, packageNames=None):
        """
        Call `ObsLightProject.importPrepBuildPackages` for all packages
        of `packageNames`. If `packageNames` is None or an empty list,
        call `importPrepBuildPackage` for all packages of `projectName`.

        Returns the list of packages which failed, as tuples of
        (packageName, exception) or (packageName, errorCode) depending
        on the type of failure.

        This function was developed for testing purposes.
        """
        projectObj = self.getProject(projectName)
        return projectObj.importPrepBuildPackages(packageNames)

