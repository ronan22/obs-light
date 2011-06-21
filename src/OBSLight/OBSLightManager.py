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
        
        self.__localRepositories=LocalRepositories()
        
        self.__workingDirectory="/home/OBSLight"
        
        self.__isOBSConnected=False
        
        self.__oBSLightProjects=OBSLightProjects()
        
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
        
    def addProject(self,projectName=None , projectDirectory=None, chrootDirectory=None):
            if projectName==None:
                raise obslighterr.ManagerError("Can't create a project with no name")
            
            if (projectDirectory==None):
                projectDirectory=self.__workingDirectory+SEP+"Project"+SEP+projectName
                
            if (chrootDirectory==None):
                chrootDirectory=projectDirectory+SEP+"chroot"
                
            return self.__oBSLightProjects.addOBSLightProject(projectName=projectName, projectDirectory=projectDirectory, chrootDirectory=chrootDirectory)
    
    
    def getListOBSLightProject(self):
        return self.__oBSLightProjects.getListOBSLightProject()
        
        
        
        
        
        
        
        
        
        
        
        