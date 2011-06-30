'''
Created on the 21 june 2011

This is the main file for the conversion of a XML file to a dictionary and 
for the conversion of a dictionary back to a XML file after eventual modifications.

@author: hellmann
'''

from XML_repomd import Repomd
from XML_parse import XML_Parse
from XML_parse import XmlDictObject 
from pprint import pprint
import os, time


def main():
    '''
    The main function
    '''
    IN_XML_FILE_NAME = '/home/hellmann/XML_files/input.xml' #The XML input file
    OUT_XML_FILE_NAME = '/home/hellmann/XML_files/output.xml' #The XML output file
    DICT_FILE_NAME = '/home/hellmann/XML_files/output.dict' #The dictionary obtained from the XML file
    
    MyOutFName=OUT_XML_FILE_NAME
    MyTempFName=MyOutFName.replace('.xml','.temp.xml') #The output XML file will be first written into a temp file
      
    aRepomd_cli = Repomd(IN_XML_FILE_NAME)  
    aRepomd_cli.parseXML(IN_XML_FILE_NAME)
    
    #For eventual modifications of the dictionary
    #aRepomd_cli.modifyDict()
    
    aRepomd_cli.setRepomdNameSpaceDict(aRepomd_cli.getNameSpaceDict()) 
    aRepomd_cli.setRepomdDicoStorage(aRepomd_cli.getDicoStorage())
    MyRepomdDict = aRepomd_cli.getRepomdDicoStorage()
    aRepomd_cli.printObj(DICT_FILE_NAME,MyRepomdDict)
    aRepomd_cli.dumpXML(MyTempFName)
        
    #The xmllint command will format the output XML file, in particular newlines will be added if necessary    
    MyCommand_1="xmllint --format '" + MyTempFName +  "' > '" + MyOutFName + "'"
    MyCommand_2="rm -rf '" + MyTempFName + "'"
    os.system(MyCommand_1)
    os.system(MyCommand_2)
    
      
if __name__ == '__main__':
    main()
    