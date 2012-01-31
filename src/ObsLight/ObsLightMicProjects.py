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
Created on jan 10 2012

@author: ronan@fridu.net
'''

import os
import pickle

import ObsLightErr

from ObsLightMicProject import ObsLightMicProject

class ObsLightMicProjects:
    def __init__(self, workingDirectory):
        '''
        Constructor
        '''
        self.__dicOBSLightProjects = {}
        self.__currentProjects = None
        self.__workingDirectory = workingDirectory + "/MicProjects"
        self.__pathFile = os.path.join(workingDirectory , "ObsLightMicProjectsConfig")

        if not os.path.isdir(self.getObsLightMicDirectory()):
            os.makedirs(self.getObsLightMicDirectory())
        self.__load()

    def getObsLightMicDirectory(self):
        return self.__workingDirectory

    def __load(self, aFile=None):
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
                raise  ObsLightErr.ObsLightMicProjectErr("the file: '" + pathFile + "' is not a backup file.")
            aFile.close()

            if not ("saveProjects" in saveconfigServers.keys()):
                raise ObsLightErr.ObsLightMicProjectErr("the file: '" + pathFile + "'  is not a valid backup.")
            saveProjects = saveconfigServers["saveProjects"]

            for projetName in saveProjects.keys():
                aServer = saveProjects[projetName]
                self.__addProjectFromSave(name=projetName, fromSave=aServer, importFile=importFile)
            self.__currentProjects = saveconfigServers["currentProject"]

    def save(self, aFile=None, ProjectName=None):
        if aFile == None:
            pathFile = self.__pathFile
        else:
            pathFile = aFile

        saveProject = {}

        if ProjectName == None:
            for ProjectName in self.getMicProjectList():
                saveProject[ProjectName] = self.__dicOBSLightProjects[ProjectName].getDic()
        else:
            saveProject[ProjectName] = self.__dicOBSLightProjects[ProjectName].getDic()

        saveconfigProject = {}
        saveconfigProject["saveProjects"] = saveProject
        saveconfigProject["currentProject"] = self.__currentProjects
        aFile = open(pathFile, 'w')
        pickle.dump(saveconfigProject, aFile)
        aFile.close()

    def __addProjectFromSave(self, name=None, fromSave=None, importFile=None):
        if not (name in self.__dicOBSLightProjects.keys()):
            self.__dicOBSLightProjects[name] = ObsLightMicProject(workingDirectory=self.getObsLightMicDirectory(),
                                                                  fromSave=fromSave,
                                                                  importFile=importFile,
                                                                  name=name)
        else:
            raise ObsLightErr.ObsLightProjectsError("Can't import: '" + name + "', The Mic Project already exists.")

    def getMicProjectList(self):
        """
        Get the list of available Mic projects.
        """
        res = self.__dicOBSLightProjects.keys()
        res.sort()
        return res

    def isAMicProject(self, projectName):
        """
        Test if `projectName` is a Mic project.
        """
        return projectName in self.getMicProjectList()

    def _checkMicProjectName(self, projectName):
        """
        Raise an exception if `projectName` is not a Mic project.
        """
        if not self.isAMicProject(projectName):
            message = "'%s' project does not exist"
            raise ObsLightErr.ObsLightProjectsError(message)

    def addMicProjects(self, micProjectName):
        self._checkMicProjectName(micProjectName)
        self.__addProjectFromSave(name=micProjectName)

    def delMicProjects(self, micProjectName):
        self._checkMicProjectName(micProjectName)
        self.__dicOBSLightProjects[micProjectName].deleteProjectDirectory()
        del self.__dicOBSLightProjects[micProjectName]

    def setKickstartFile(self, micProjectName, filePath):
        self._checkMicProjectName(micProjectName)
        self.__dicOBSLightProjects[micProjectName].setKickstartFile(filePath)

    def getKickstartFile(self, micProjectName):
        self._checkMicProjectName(micProjectName)
        return self.__dicOBSLightProjects[micProjectName].getKickstartFile()

    def getMicProjectArchitecture(self, micProjectName):
        self._checkMicProjectName(micProjectName)
        return self.__dicOBSLightProjects[micProjectName].getArchitecture()

    def setMicProjectArchitecture(self, micProjectName, arch):
        self._checkMicProjectName(micProjectName)
        self.__dicOBSLightProjects[micProjectName].setArchitecture(arch)

    def setMicProjectImageType(self, micProjectName, imageType):
        self._checkMicProjectName(micProjectName)
        self.__dicOBSLightProjects[micProjectName].setImageType(imageType)

    def getMicProjectImageType(self, micProjectName):
        self._checkMicProjectName(micProjectName)
        return self.__dicOBSLightProjects[micProjectName].getImageType()

    def createImage(self, micProjectName):
        self._checkMicProjectName(micProjectName)
        return self.__dicOBSLightProjects[micProjectName].createImage()
