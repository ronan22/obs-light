'''
Created on 21 juin 2011
@author: hellmann
'''

from XML_Parse import XML_Parse
import os

class XML_Other(XML_Parse):    
    
    def __init__(self, aFileName=None):
        '''
        Constructor
        '''
        XML_Parse.__init__(self, aFileName)
        self.__OtherRootDict={}
        self.__OtherNameSpaceDict={}
        self.__OtherDicoStorage={}
        
    def getOtherDicoStorage(self):
        return self.__OtherDicoStorage
        
    def setOtherDicoStorage(self,aOtherDicoStorage):
        self.__OtherDicoStorage=aOtherDicoStorage
   
    def getOtherNameSpaceDict(self):
        return self.__OtherNameSpaceDict
    
    def setOtherNameSpaceDict(self,aNameSpaceDict):
        self.__OtherNameSpaceDict=aNameSpaceDict
  
def main():
        
    """
        exec the main 
    """
    IN_XML_FILE_NAME = '/home/hellmann/XML_files/input.xml' #The XML input file
    OUT_XML_FILE_NAME = '/home/hellmann/XML_files/output.xml' #The XML output file
    DICT_FILE_NAME = '/home/hellmann/XML_files/output.dict' #The dictionary obtained from the XML file
    
    MyOutFName=OUT_XML_FILE_NAME
    MyTempFName=MyOutFName.replace('.xml','.temp.xml') #The output XML file will be first written into a temp file
      
    aOther_cli = XML_Other(IN_XML_FILE_NAME)  
    aOther_cli.parseXML(IN_XML_FILE_NAME)
    
    #For eventual modifications of the dictionary
    #aOther_cli.modifyDict()
    
    aOther_cli.setOtherNameSpaceDict(aOther_cli.getNameSpaceDict()) 
    aOther_cli.setOtherDicoStorage(aOther_cli.getDicoStorage())
    MyOtherDict = aOther_cli.getOtherDicoStorage()
    aOther_cli.printObj(DICT_FILE_NAME,MyOtherDict)
    aOther_cli.dumpXML(MyTempFName)
       
    #The xmllint command will format the output XML file, in particular newlines will be added if necessary    
    MyCommand_1="xmllint --format '" + MyTempFName +  "' > '" + MyOutFName + "'"
    MyCommand_2="rm -rf '" + MyTempFName + "'"
    os.system(MyCommand_1)
    os.system(MyCommand_2)
   
     
if __name__ == '__main__':
    main()
    
