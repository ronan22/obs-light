'''
Created on 17 juin 2011

@author: rmartret
'''
from LocalRepository import LocalRepository

import os

import pickle

class LocalRepositories(object):
    '''
    classdocs
    '''
    
    
    def __init__(self,manager):
        '''
        Constructor
        '''
        self.__manager=manager
        
        self.__pathFile = self.__manager.getManager() +os.sep+"reposConfig"
        self.__listLocalRepository={}
        
        self.__load()

        
        
    def __save(self):
        """
        
        """
        saveRepository={}

        for repName in self.getListLocalRepositoryName():
            
            saveRepository[repName]= self.getLocalRepository(repName).getDic() 
            
        file=open(self.__pathFile,'w')
        pickle.dump(saveRepository,file) 
        file.close()   
        
        
    def __load(self):
        """
        
        """
        if os.path.isfile(self.__pathFile):
            file=open(self.__pathFile,'r')
            saveRepository=pickle.load(file)
            
            for repName in saveRepository.keys():
                rep=saveRepository[repName]
                path=None
                url=None
                name=None
                listRPM=None
                keys=rep.keys()
                if "url" in keys:
                    url=rep["url"]
                if "path" in keys:    
                    path=rep["path"]
                
                self.addRepository(path=path,url=url,name=repName)
                
            file.close()
            
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
        

    def addRepository(self,path=None,url=None,name=None):
        """
        
        """
        aLocalRepository=LocalRepository(path=path,url=url,name=name)
        
        if aLocalRepository.isValideRepository()!=True:
            self.__listLocalRepository[ aLocalRepository.getRepositoryName() ]=aLocalRepository
            self.__save()
            return 0
        else:
            return 1
        
    def getRepositoryInfo(self, name=None ):
        """
        
        """
        if name in self.getListLocalRepositoryName():
            return self.getLocalRepository(name).getRepositoryInfo( )
        return [] 
            

            
            
    def setUrlToRepositoty(self,name=None,url=None):
        """
        
        """
        if self.getLocalRepository(name).setUrlToRepositoty(url=url)==0:
            self.__save()
            return 0
        else:
            return 1 
        
    def setPathToRepositoty(self,name=None,path=None):
        """
        
        """
        if self.getLocalRepository(name).setPathToRepositoty(path=path)==0:
            self.__save()
            return 0
        else:
            return 1 
        
        
    def check(self,name=None):
        """
        
        """
        if self.getLocalRepository(name).check()==0:
            self.__save()
            return 0
        else:
            return 1 
        
    def getRPMPath(self,architecture=None, target=None,rpm=None):
        """
        
        """
        return  self.getLocalRepository(target).getRPMPath(architecture=architecture,rpm=rpm)
        
    def getDependence(self,architecture=None, target=None,rpm=None):
        """
        
        """
        return  self.getLocalRepository(target).getDependence(architecture=architecture,rpm=rpm)
        
        
    def upDateRepository(self,name=None ):
        """
        
        """
        return  self.getLocalRepository(name).upDateRepository()
    
    def getReposRPMFile(self,target=None,arch=None):
        """
        
        """
        return  self.getLocalRepository(target).getReposRPMFile(arch=arch)
        
        
        
        
        
        