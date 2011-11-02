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


    def __init__(self, manager):
        '''
        Constructor
        '''
        self.__dicOBSLightProjects = {}
        self.__manager = manager
        self.__currentProjects = ""
        
        self.__pathFile = os.path.join(self.__manager.getObsLightWorkingDirectory() , "ObsLightProjectsConfig")
        
        self.__load()
        
        
    def save(self):
        '''
        
        '''
        saveProject = {}

        for ProjectName in self.getLocalProjectList():
            saveProject[ProjectName] = self.__dicOBSLightProjects[ProjectName].getDic()
        
        saveconfigProject = {}
        saveconfigProject["saveProjects"] = saveProject
        saveconfigProject["currentProject"] = self.__currentProjects    
        aFile = open(self.__pathFile, 'w')
        pickle.dump(saveconfigProject, aFile)    
        aFile.close()
        
    def __load(self):
        '''
        
        '''
        if os.path.isfile(self.__pathFile):
            aFile = open(self.__pathFile, 'r')
            saveconfigServers = pickle.load(aFile)
            aFile.close()
            saveProjects = saveconfigServers["saveProjects"]
            for projetName in saveProjects.keys():
                aServer = saveProjects[projetName]
                self.__addProjectFromSave(name=projetName, fromSave=aServer)    
            self.__currentProjects = saveconfigServers["currentProject"]
        
        
    def getLocalProjectList(self):
        '''
        
        '''
        return self.__dicOBSLightProjects.keys()
        
        
    def addProject(self,
                   projectLocalName=None,
                   projectObsName=None,
                   projectTitle=None,
                   projectDirectory=None,
                   chrootDirectory=None,
                   obsServer=None ,
                   projectTarget=None,
                   description=None,
                   projectArchitecture=None):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName] = ObsLightProject(projectLocalName=projectLocalName,
                                                                       projectObsName=projectObsName,
                                                                       projectTitle=projectTitle,
                                                                       projectDirectory=projectDirectory,
                                                                       chrootDirectory=chrootDirectory,
                                                                       obsServer=obsServer,
                                                                       projectTarget=projectTarget,
                                                                       description=description,
                                                                       projectArchitecture=projectArchitecture)
        
    def __addProjectFromSave(self, name=None, fromSave=None):
        '''
        
        '''
        self.__dicOBSLightProjects[name] = ObsLightProject(fromSave=fromSave)
        
        
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
        
        
    def goToChRoot(self, projectLocalName=None, package=None):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName].goToChRoot(package=package)
        
    def addPackageSourceInChRoot(self, projectLocalName=None, package=None):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName].addPackageSourceInChRoot(package=package)
        
    def makePatch(self,
                  projectLocalName=None,
                  package=None,
                  patch=None):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName].makePatch(package=package,
                                                               patch=patch)
        
        
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
        self.__dicOBSLightProjects[name].getPackage(package=package).commitToObs(message=message)
    
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
            self.__dicOBSLightProjects[projectLocalName].addRepo(repos=repos, alias=alias)
        
        
    def getProjectObsName(self, projectLocalName=None):
        '''
        
        '''
        return self.__dicOBSLightProjects[projectLocalName].getProjectObsName()
        
    def getProjectInfo(self,projectLocalName=None,info=None):
        '''
        
        '''
        return self.__dicOBSLightProjects[projectLocalName].getProjectInfo(info=info)
        
    def setProjectparameter(self,projectLocalName=None,parameter=None,value=None):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName].setProjectparameter(parameter=parameter,value=value)

    def removeProject(self,projectLocalName=None):
        '''
        
        '''
        res=self.__dicOBSLightProjects[projectLocalName].removeProject()
        if res==0:
            del self.__dicOBSLightProjects[projectLocalName]
            return None
        else:
            raise ObsLightErr.ObsLightProjectsError("Error in removeProject, can't remove project directory.")
