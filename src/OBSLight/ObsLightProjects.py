'''
Created on 29 sept. 2011

@author: ronan
'''
import os
import pickle
from ObsLightProject import ObsLightProject

class ObsLightProjects(object):
    '''
    classdocs
    '''


    def __init__(self,manager):
        '''
        Constructor
        '''
        self.__dicOBSLightProjects={}
        self.__manager=manager
        self.__currentProjects=""
        
        self.__pathFile = os.path.join(self.__manager.getObsLightWorkingDirectory() ,"ObsLightProjectsConfig")
        
        self.__load()
        
        
    def save(self):
        '''
        
        '''
        saveProject={}

        for ProjectName in self.getListProject():
            saveProject[ProjectName]= self.__dicOBSLightProjects[ProjectName].getDic()
        
        saveconfigProject={}
        saveconfigProject["saveProjects"]=saveProject
        saveconfigProject["currentProject"]=self.__currentProjects    
        file=open(self.__pathFile,'w')
        pickle.dump(saveconfigProject,file)    
        file.close()
        
    def __load(self):
        '''
        
        '''
        if os.path.isfile(self.__pathFile):
            file=open(self.__pathFile,'r')
            saveconfigServers=pickle.load(file)
            file.close()
            saveProjects=saveconfigServers["saveProjects"]
            for projetName in saveProjects.keys():
                aServer=saveProjects[projetName]
                self.__addProjectFromSave(name=projetName, fromSave=aServer)    
            self.__currentProjects= saveconfigServers["currentProject"]
        
        
    def getListProject(self):
        '''
        
        '''
        return self.__dicOBSLightProjects.keys()
        
        
    def addProject(self, projectName=None, projectTitle=None, projectDirectory=None, chrootDirectory=None, obsserver=None ,projectTarget=None, description=None, projectArchitecture=None):
        '''
        
        '''
        self.__dicOBSLightProjects[projectName]=ObsLightProject( projectName=projectName, projectTitle=projectTitle, projectDirectory=projectDirectory, chrootDirectory=chrootDirectory, obsserver=obsserver ,projectTarget=projectTarget, description=description, projectArchitecture=projectArchitecture)
        
    def __addProjectFromSave(self,name=None,fromSave=None ):
        '''
        
        '''
        self.__dicOBSLightProjects[name]=ObsLightProject( fromSave=fromSave)
        
        
    def getListPackage(self,name=None,local=0):
        '''
        
        '''
        return self.__dicOBSLightProjects[name].getListPackage(local=local)
        
        
    def addPackage(self, project=None  ,package=None):
        '''
        
        '''
        return self.__dicOBSLightProjects[project].addPackage(name=package)
        
    def createChRoot(self, project=None ):
        '''
        
        '''
        self.__dicOBSLightProjects[project].createChRoot()
        
        
        
    def goToChRoot(self,project=None,package=None):
        '''
        
        '''
        self.__dicOBSLightProjects[project].goToChRoot(package=package)
        
    def addPackageSourceInChRoot(self,project=None,package=None):
        '''
        
        '''
        self.__dicOBSLightProjects[project].addPackageSourceInChRoot(package=package)
        
    def makePatch(self,project=None,package=None,patch=None):
        '''
        
        '''
        self.__dicOBSLightProjects[project].makePatch(package=package,patch=patch)
        
        
        
        
        
        
        
        
        