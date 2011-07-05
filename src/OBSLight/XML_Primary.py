'''
Created on 21 juin 2011
@author: hellmann
'''

from XML_Parse import XML_Parse
import os

class XML_Primary(XML_Parse):    
    
    def __init__(self, aFileName=None):
        '''
        Constructor
        '''
        XML_Parse.__init__(self, aFileName)
        self.__PrimaryRootDict={}
        self.__PrimaryNameSpaceDict={}
        self.__PrimaryDicoStorage={}
        
    def getPrimaryDicoStorage(self):
        return self.__PrimaryDicoStorage
        
    def setPrimaryDicoStorage(self,aPrimaryDicoStorage):
        self.__PrimaryDicoStorage=aPrimaryDicoStorage
   
    def getPrimaryNameSpaceDict(self):
        return self.__PrimaryNameSpaceDict
    
    def setPrimaryNameSpaceDict(self,aNameSpaceDict):
        self.__PrimaryNameSpaceDict=aNameSpaceDict
  
def main():
        
    """
        exec the main 
    """
    IN_XML_FILE_NAME = '/home/hellmann/XML_files/input.xml' #The XML input file
    OUT_XML_FILE_NAME = '/home/hellmann/XML_files/output.xml' #The XML output file
    DICT_FILE_NAME = '/home/hellmann/XML_files/output.dict' #The dictionary obtained from the XML file
    
    MyOutFName=OUT_XML_FILE_NAME
    aPrimary_cli = XML_Primary(IN_XML_FILE_NAME)  
    aPrimary_cli.parseXML(IN_XML_FILE_NAME)
    #For eventual modifications of the dictionary
    #aPrimary_cli.modifyDict()
    aPrimary_cli.setPrimaryNameSpaceDict(aPrimary_cli.getNameSpaceDict()) 
    aPrimary_cli.setPrimaryDicoStorage(aPrimary_cli.getDicoStorage())
    MyPrimaryDict = aPrimary_cli.getPrimaryDicoStorage()
    aPrimary_cli.printObj(DICT_FILE_NAME,MyPrimaryDict)
    aPrimary_cli.dumpXML(MyOutFName)
    aPrimary_cli.lintXML(MyOutFName,MyOutFName)
     
    
if __name__ == '__main__':
    main()
    
