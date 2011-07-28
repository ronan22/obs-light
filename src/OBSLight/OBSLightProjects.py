'''
Created on 17 juin 2011

@author: rmartret
'''

from OBSLightProject import OBSLightProject

import obslighterr
import pickle
import os


class OBSLightProjects(object): 
    '''
    classdocs
    '''

    def __init__(self,manager):
        '''
        Constructor
        '''
        self.__manager=manager
        
        self.__pathFile = self.__manager.getManager() +os.sep+"projectConfig"
        
        self.__listOBSLightProject={}
        
        self.__currentProjectName=None
        
        self.__load()

        
        
    def __save(self):
        saveProject={}

        for projectName in self.getListOBSLightProject():
            saveProject[projectName]= self.__listOBSLightProject[projectName].getDic()
            
        file=open(self.__pathFile,'w')
        pickle.dump(saveProject,file)    
        file.close()
        
    def __load(self):
        if os.path.isfile(self.__pathFile):
            file=open(self.__pathFile,'r')

            saveProject=pickle.load(file)
            
            for projetName in saveProject.keys():

                aProjet=saveProject[projetName]
                name=None
                directory=None
                chrootDirectory=None
                target=None
                architecture=None
                keys=aProjet.keys()
                
                if "name" in keys:
                    name=aProjet["name"]
                    
                if "directory" in keys:    
                    directory=aProjet["directory"]
                    
                if "chrootDirectory" in keys:
                    chrootDirectory=aProjet["chrootDirectory"]
                    
                if "target" in keys:    
                    target=aProjet["target"]
                    
                if "architecture" in keys:
                    architecture=aProjet["architecture"]
                
                self.addOBSLightProject(name=name, directory=directory, chrootDirectory=chrootDirectory , target=target , architecture=architecture)
                
            file.close()
        
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

    def addOBSLightProject(self,name=None, directory=None, chrootDirectory=None , target=None , architecture=None):
        """
        add a new project 
        """
        
        
        if (name!=None)&(directory!=None)&(chrootDirectory!=None):
            
            if name in self.__listOBSLightProject.keys():
                raise obslighterr.OBSLightProjectsError("Project all ready  exist in addOBSLightProject")
            
            
            
            self.__listOBSLightProject[name]=OBSLightProject(manager=self.__manager,name=name, directory=directory, chrootDirectory=chrootDirectory , target=target , architecture=architecture)
            
            self.__currentProjectName=name
            
            self.__save()
            
            return 0
        else:
            raise obslighterr.OBSLightProjectsError("Empty directory in addOBSLightProject")
        
    def getListOBSLightProject(self):
        """
        return the list of projectName
        """
        return self.__listOBSLightProject.keys()
        
    def getProjectInfo(self, name=None ):
        return  self.__listOBSLightProject[name].getProjectInfo()
        
        
    def creatChroot(self,name):
        return self.__listOBSLightProject[name].creatChroot()
        
        
    def addRPM(self,project=None, rpm=None, type=None ):
        """
        
        """
        return self.__listOBSLightProject[project].addRPM( rpm=rpm, type=type )
        
    def checkChRoot(self,project=None):
        """
        
        """
        return self.__listOBSLightProject[project].checkChRoot()
        
        
    def getProviderLib(self,project=None,lib=None):
        """
        
        """
        return self.__listOBSLightProject[project].getProviderLib(lib=lib)
        
        
        
        
        
        
        
        
        