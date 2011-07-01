'''
Created on 21 juin 2011
@author: hellmann
'''

from XML_Parse import XML_Parse
import os

class XML_Filelists(XML_Parse):    
    
    def __init__(self, aFileName=None):
        '''
        Constructor
        '''
        XML_Parse.__init__(self, aFileName)
        self.__FilelistsRootDict={}
        self.__FilelistsNameSpaceDict={}
        self.__FilelistsDicoStorage={}
        
    def getFilelistsDicoStorage(self):
        return self.__FilelistsDicoStorage
        
    def setFilelistsDicoStorage(self,aFilelistsDicoStorage):
        self.__FilelistsDicoStorage=aFilelistsDicoStorage
   
    def getFilelistsNameSpaceDict(self):
        return self.__FilelistsNameSpaceDict
    
    def setFilelistsNameSpaceDict(self,aNameSpaceDict):
        self.__FilelistsNameSpaceDict=aNameSpaceDict
  
def main():
        
    """
        exec the main 
    """
    IN_XML_FILE_NAME = '/home/hellmann/XML_files/input.xml' #The XML input file
    OUT_XML_FILE_NAME = '/home/hellmann/XML_files/output.xml' #The XML output file
    DICT_FILE_NAME = '/home/hellmann/XML_files/output.dict' #The dictionary obtained from the XML file
    
    MyOutFName=OUT_XML_FILE_NAME
    MyTempFName=MyOutFName.replace('.xml','.temp.xml') #The output XML file will be first written into a temp file
      
    aFilelists_cli = XML_Filelists(IN_XML_FILE_NAME)  
    aFilelists_cli.parseXML(IN_XML_FILE_NAME)
    
    #For eventual modifications of the dictionary
    #aFilelists_cli.modifyDict()
    
    aFilelists_cli.setFilelistsNameSpaceDict(aFilelists_cli.getNameSpaceDict()) 
    aFilelists_cli.setFilelistsDicoStorage(aFilelists_cli.getDicoStorage())
    MyFilelistsDict = aFilelists_cli.getFilelistsDicoStorage()
    aFilelists_cli.printObj(DICT_FILE_NAME,MyFilelistsDict)
    aFilelists_cli.dumpXML(MyTempFName)
       
    #The xmllint command will format the output XML file, in particular newlines will be added if necessary    
    MyCommand_1="xmllint --format '" + MyTempFName +  "' > '" + MyOutFName + "'"
    MyCommand_2="rm -rf '" + MyTempFName + "'"
    os.system(MyCommand_1)
    os.system(MyCommand_2)
   
     
if __name__ == '__main__':
    main()
    
