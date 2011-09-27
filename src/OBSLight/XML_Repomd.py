'''
Created on 21 juin 2011
@author: hellmann
'''

from XML_Parse import XML_Parse
import os

class XML_Repomd(XML_Parse):    
    
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
  
def main():
        
    """
        exec the main 
    """
    IN_XML_FILE_NAME = '/home/hellmann/XML_files/input.xml' #The XML input file
    OUT_XML_FILE_NAME = '/home/hellmann/XML_files/output.xml' #The XML output file
    DICT_FILE_NAME = '/home/hellmann/XML_files/output.dict' #The dictionary obtained from the XML file
    
    MyOutFName=OUT_XML_FILE_NAME
    aRepomd_cli = XML_Repomd(IN_XML_FILE_NAME)  
    aRepomd_cli.parseXML(IN_XML_FILE_NAME)
    #For eventual modifications of the dictionary
    #aRepomd_cli.modifyDict()
    aRepomd_cli.setRepomdNameSpaceDict(aRepomd_cli.getNameSpaceDict()) 
    aRepomd_cli.setRepomdDicoStorage(aRepomd_cli.getDicoStorage())
    MyRepomdDict = aRepomd_cli.getRepomdDicoStorage()
    aRepomd_cli.printObj(DICT_FILE_NAME,MyRepomdDict)
    aRepomd_cli.dumpXML(MyOutFName)
    aRepomd_cli.lintXML(MyOutFName,MyOutFName)
       
        
if __name__ == '__main__':
    main()
    
