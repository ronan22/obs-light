'''
Created on 17 juin 2011

@author: rmartret
'''

from OBSLightTools.LocalRepositories import LocalRepositories

from OBSLightTools.OBSLightProjects import OBSLightProjects 

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
        
        
        