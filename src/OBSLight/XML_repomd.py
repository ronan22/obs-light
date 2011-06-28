'''
Created on 21 juin 2011
@author: hellmann
'''

from XML_parse import XML_Parse

class Repomd(XML_Parse):    
    
    def __init__(self, aFileName=None):
        '''
        Constructor
        '''
        XML_Parse.__init__(self, aFileName)
        self.__RepomdRootDict={}
        self.__RepomdNameSpaceDict={}
        self.__RepomdDicoStorage={}
        
    def getRepomdDicoStorage(self):
        return self.__RepomdDicoStorage
        
    def setRepomdDicoStorage(self,aRepomdDicoStorage):
        self.__RepomdDicoStorage=aRepomdDicoStorage
   
    def getRepomdNameSpaceDict(self):
        return self.__RepomdNameSpaceDict
    
    def setRepomdNameSpaceDict(self,aNameSpaceDict):
        self.__RepomdNameSpaceDict=aNameSpaceDict
  
   
