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
Created on jan 10 2012

@author: ronan@fridu.net
'''

import os
import pickle

import ObsLightErr

from ObsLightMicProject import ObsLightMicProject

class ObsLightMicProjects(object):
    def __init_(self, workingDirectory):
        '''
        Constructor
        '''
        self.__dicOBSLightProjects = {}
        self.__currentProjects = None
        self.__workingDirectory = workingDirectory + "/MicProjects"
        self.__pathFile = os.path.join(self.getObsLightWorkingDirectory() , "ObsLightMicProjectsConfig")

        self.__load()

    def getObsLightWorkingDirectory(self):
        '''
        
        '''
        return self.__workingDirectory

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
        '''
        
        '''
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
        '''
        
        '''
        if not (name in self.__dicOBSLightProjects.keys()):
            self.__dicOBSLightProjects[name] = ObsLightMicProject(workingDirectory=self.getObsLightWorkingDirectory(),
                                                                  fromSave=fromSave,
                                                                  importFile=importFile)
        else:
            raise ObsLightErr.ObsLightProjectsError("Can't import: '" + name + "', The Mic Project already exists.")

    def getMicProjectList(self):
        '''
        
        '''
        res = self.__dicOBSLightProjects.keys()
        res.sort()
        return res


    def addMicProjects(self, projectMicName):
        '''
        
        '''
        self.__addProjectFromSave(name=projectMicName)

    def addKickstartFile(self, projectMicName, filePath):
        '''
        
        '''
        self.__dicOBSLightProjects[projectMicName].addKickstartFile(filePath)

    def getMicProjectArchitecture(self, projectMicName):
        '''
        
        '''
        return self.__dicOBSLightProjects[projectMicName].getMicProjectArchitecture()

    def setMicProjectArchitecture(self, projectMicName, arch):
        '''
        
        '''
        self.__dicOBSLightProjects[projectMicName].setMicProjectArchitecture(arch)

    def setMicProjectImageType(self, projectMicName, imageType):
        '''
        
        '''
        self.__dicOBSLightProjects[projectMicName].setMicProjectImageType(imageType)

    def getMicProjectImageType(self, projectMicName):
        '''
        
        '''
        return self.__dicOBSLightProjects[projectMicName].getMicProjectImageType()

    def createImage(self, projectMicName):
        '''
        
        '''
        return self.__dicOBSLightProjects[projectMicName].createImage()





