'''
Created on 17 juin 2011

@author: rmartret
'''

class LocalRepository(object):
    '''
    classdocs
    '''


    def __init__(self,url=None):
        '''
        TO DO
        '''
        
        self.__repositoryName=None
        self.__creationDate=None
        self.__BaseReposUrl=None
        self.__reposID=None
        self.__reposVersion=None
        self.__repositoryStatus=None
        
        self.__listRPM={}
        self.__listGroupRPM={}
        
        self.__valideRepository=False
        
    def getRepositoryName(self):
        """
        Return the name of the repository.
        """
        return self.__repositoryName
    
    def isValideRepository(self):
        """
        Return if the repository is a valide repository.
        """
        return self.__valideRepository
    
    
    
    
    
    