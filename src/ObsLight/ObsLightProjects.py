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
import ObsLightPrintManager

class ObsLightProjects(object):
    '''
    classdocs
    '''
    def __init__(self, obsServers,workingDirectory):
        '''
        Constructor
        '''
        self.__dicOBSLightProjects = {}
        self.__obsServers = obsServers
        self.__currentProjects = None
        
        self.__pathFile = os.path.join(workingDirectory , "ObsLightProjectsConfig")
        
        self.__load()
        
        
    def save(self,aFile=None,ProjectName=None):
        '''
        
        '''
        if aFile==None:
            pathFile=self.__pathFile
        else:
            pathFile=aFile
        
        saveProject = {}

        if ProjectName==None:
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
        
    def __load(self,aFile=None):
        '''
        
        '''
        if aFile==None:
            pathFile=self.__pathFile
            importFile=True
        else:
            pathFile=aFile
            importFile=False
            
        if os.path.isfile(pathFile):
            aFile = open(pathFile, 'r')
            try:
                saveconfigServers = pickle.load(aFile)
            except:
                raise  ObsLightErr.ObsLightProjectsError("the file: "+pathFile+" is not a backup")
            aFile.close()
            
            if not ("saveProjects" in saveconfigServers.keys()):
                raise ObsLightErr.ObsLightProjectsError("the file: "+pathFile+"  is not a backup")
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
                   projectDirectory=None,
                   chrootDirectory=None,
                   obsServer=None ,
                   projectTarget=None,
                   description=None,
                   projectArchitecture=None):
        '''
        
        '''
        self.__dicOBSLightProjects[projectLocalName] = ObsLightProject(obsServers=self.__obsServers,
                                                                       projectLocalName=projectLocalName,
                                                                       projectObsName=projectObsName,
                                                                       projectTitle=projectTitle,
                                                                       projectDirectory=projectDirectory,
                                                                       chrootDirectory=chrootDirectory,
                                                                       obsServer=obsServer,
                                                                       projectTarget=projectTarget,
                                                                       description=description,
                                                                       projectArchitecture=projectArchitecture)
        
    def __addProjectFromSave(self, name=None, fromSave=None,importFile=None):
        '''
        
        '''
        if not (name in self.__dicOBSLightProjects.keys() ):
            self.__dicOBSLightProjects[name] = ObsLightProject(obsServers=self.__obsServers,fromSave=fromSave,importFile=importFile)
        else:
            ObsLightPrintManager.obsLightPrint("Can't import: "+name+", The Project already exist.")
        
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
        projetPath=self.__dicOBSLightProjects[projectLocalName].getDirectory()
        
        self.__dicOBSLightProjects[projectLocalName].removeProject()
        
        if not os.path.isdir(projetPath):
            del self.__dicOBSLightProjects[projectLocalName]
            return None
        else:
            raise ObsLightErr.ObsLightProjectsError("Error in removeProject, can't remove project directory.")
        
        
    def removePackage(self,projectLocalName=None,package=None):
        '''
        Remove a package from local project.
        '''
        return self.__dicOBSLightProjects[projectLocalName].removePackage(package=package)
        
    def importProject(self,path=None):
        '''
        Import a project from a file
        '''
        self.__load(aFile=path)
        
    
    def exportProject(self,projectLocalName=None,path=None):
        '''
        Export a project to a file
        '''
        self.save(aFile=path,ProjectName=projectLocalName)
        
    def getWebProjectPage(self,projectLocalName):
        '''
        
        '''
        return self.__dicOBSLightProjects[projectLocalName].getWebProjectPage()
        
        
        
