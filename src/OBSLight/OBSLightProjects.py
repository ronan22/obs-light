'''
Created on 17 juin 2011

@author: rmartret
'''

from OBSLightProject import OBSLightProject

import obslighterr


class OBSLightProjects(object): 
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.__listOBSLightProject={}
        
        self.__currentProjectName=None
        
    def getCurrentProjectName(self):
        """
        return the current Project Name
        """
        return self.__currentProjectName
    
    
    def getProject(self,projectName=None):
        """
        return a project
        """
        if projectName!=None:
            if projectName in self.__listOBSLightProject.keys():
                return self.__listOBSLightProject[projectName]
            else:
                return None
        else:
            return None

    
    def addOBSLightProject(self,projectName=None , projectDirectory=None,chrootDirectory=None):
        """
        add a new project 
        """
        if (projectName!=None)&(projectDirectory!=None)&(chrootDirectory!=None):
            
            if projectName in self.__listOBSLightProject.keys():
                raise obslighterr.OBSLightProjectsError("Project all ready  exist in addOBSLightProject")
            
            self.__listOBSLightProject[projectName]=OBSLightProject(projectName=projectName , projectDirectory=projectDirectory,chrootDirectory=chrootDirectory)
            
            return 0
        else:
            raise obslighterr.OBSLightProjectsError("Empty directory in addOBSLightProject")
        
    def getListOBSLightProject(self):
        """
        return the list of projectName
        """
        return self.__listOBSLightProject.keys()
        
         
        