'''
Created on 17 juin 2011

@author: rmartret
'''
from LocalRepository import LocalRepository


class LocalRepositories(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
        self.__listLocalRepository={}
        
    def getListLocalRepositoryName(self):
        """
        Get a list of RepositoryName
        """
        return self.__listLocalRepository.keys()

    def getLocalRepository(self,name=None):
        """
        Get a Repository
        """
        if name!=None:
            if name in self.__listLocalRepository.keys():
                return self.__listLocalRepository[name]
            else:
                return None
        else:
            return None
        

    def addRepository(self,url,localUrl):
        aLocalRepository=LocalRepository(url,localUrl)
        
        if aLocalRepository.isValideRepository()!=True:
            self.__listLocalRepository[ aLocalRepository.getRepositoryName() ]=aLocalRepository
            
            return 1
        else:
            return 0
        
        
        
        
        
        
        
        
        
        
    
        