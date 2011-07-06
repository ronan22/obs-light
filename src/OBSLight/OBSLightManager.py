'''
Created on 17 juin 2011

@author: rmartret
'''

from LocalRepositories import LocalRepositories

from OBSLightProjects import OBSLightProjects 

import os

SEP=os.sep

import obslighterr


class OBSLightManager(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
        
        
        self.__workingDirectory=os.environ['HOME']+os.sep+"OBSLight"
        
        if not os.path.isdir(self.__workingDirectory):
            os.makedirs(self.__workingDirectory)
            
        self.__localRepositories=LocalRepositories(self)
        
        self.__isOBSConnected=False
        
        self.__oBSLightProjects=OBSLightProjects(self)
        
        
    def getManager(self):
        """
        
        """
        return self.__workingDirectory
    
    def getWorkingDirectory(self):
        """
        
        """
        return  self.__workingDirectory   
        
    def getListLocalRepositoryName(self):
        """
        
        """
        return self.__localRepositories.getListLocalRepositoryName()
        
    def __loadConfiguration(self):
        """
        TO DO
        """
        pass
    
    def __upDateConfiguration(self):
        """
        TO DO
        """
        pass
        

    def addProject(self,name=None, directory=None, chrootDirectory=None , target=None , architecture=None  ):
        
        if name==None:
            raise obslighterr.ManagerError("Can't create a project with no name")
            
        if (directory==None):
            directory=self.__workingDirectory+SEP+"Project"+SEP+name
                
        if (chrootDirectory==None):
            chrootDirectory=directory+SEP+"chroot"
                
        return self.__oBSLightProjects.addOBSLightProject(name=name, directory=directory, chrootDirectory=chrootDirectory , target=target , architecture=architecture  )
 

    def getListOBSLightProject(self):
        return self.__oBSLightProjects.getListOBSLightProject()
        
        
    def addRepository(self,path=None,url=None,name=None):

        self.__localRepositories.addRepository(path=path,url=url,name=name)
        
    def getRepositoryInfo( self,name=None ):
        """
        
        """
        return self.__localRepositories.getRepositoryInfo( name=name )
        
    def getProjectInfo(self, name=None  ):
        return self.__oBSLightProjects.getProjectInfo( name=name )
        
        
    def setUrlToRepositoty(self,name=None,url=None):
        return self.__localRepositories.setUrlToRepositoty( name=name, url=url)
        
        
    def setPathToRepositoty(self,name=None,path=None):
        return self.__localRepositories.setPathToRepositoty( name=name, path=path)
    
    
    def check(self,name=None):
        return self.__localRepositories.check(name=name)
    
    def creatChroot(self, name=None  ):
        return self.__oBSLightProjects.creatChroot(name)
        
    def getRPMPath(self,architecture=None, target=None,rpm=None):
        """
        
        """
        return  self.__localRepositories.getRPMPath(architecture=architecture, target=target,rpm=rpm)
    
    def getDependence(self,architecture=None, target=None,rpm=None):
        """
        
        """
        return  self.__localRepositories.getDependence(architecture=architecture, target=target,rpm=rpm)
        
    
    def addRPM(self,project=None, rpm=None, type=None ):
        """
        
        """
        return self.__oBSLightProjects.addRPM(project=project, rpm=rpm, type=type )
    
    
    
    def upDateRepository(self,name=None ):
        """
        
        """
        return self.__localRepositories.upDateRepository(name=name )
    
    def checkChRoot(self,project=None):
        """
        
        """
        return self.__oBSLightProjects.checkChRoot(project=project)
        
    def getReposRPMFile(self,target=None,arch=None):
        """
        
        """
        return self.__localRepositories.getReposRPMFile(target=target,arch=arch)
    
    
    def getProviderLib(self,project=None,lib=None):
        """
        
        """
        return self.__oBSLightProjects.getProviderLib(project=project,lib=lib)
    
    def getRepository(self,name=None):
        """
        
        """
        return  self.__localRepositories.getLocalRepository(name)
    
    
    
    
    
    
    
    
    
    
    
    
        