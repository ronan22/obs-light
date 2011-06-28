'''
Created on 21 juin 2011
@author: hellmann
'''

from xml.etree import ElementTree
from XML_DICT_Conversion import XmlDictObject 
from XML_DICT_Conversion import ConvertDictToXml, _ConvertDictToXmlRecurse
from XML_DICT_Conversion import ConvertXmlToDict, _ConvertXmlToDictRecurse
from pprint import pprint
import sys, string, time

class XML_Parse(object):
    
    def __init__(self, aFileName=None):
        '''
        Constructor
        '''
        self.__FileName=aFileName #Name of the XML file to be parsed
        self.__DicoStorage={} #The dictionary created from the XML file 
        self.__NameSpaceDict={} #The auxiliary dictionary containing namespaces 
        self.__Tree=None
                
    def getDicoStorage(self):
        return self.__DicoStorage
    
    def setDicoStorage(self,aDicoStorage):
        self.__DicoStorage=aDicoStorage
    
    def getNameSpaceDict(self):
        return self.__NameSpaceDict
    
    def setNameSpaceDict(self,aNameSpaceDict):
        self.__NameSpaceDict=aNameSpaceDict
     
    # Prints with the pprint command an object like dictionary to a file  
    def printObj(self,aFileName=None,aObj=None):

        MyFName = aFileName
        MyStdout = sys.stdout
        MyFDescr = open(MyFName, mode='at')
        sys.stdout = MyFDescr
        pprint(aObj)
        sys.stdout = MyStdout
        MyFDescr.close()
          
    # Dumps the dictionary to a XML file with the help of the ElementTree.write function      
    def dumpXML(self,aFileName=None):
        
        MyFName_1=aFileName
        root = ConvertDictToXml(self.__DicoStorage)
        tree = ElementTree.ElementTree(root)
        tree.write(MyFName_1)
               
    # Parses the XML file and creates a dictionary            
    def parseXML(self, aFileName=None):
        
        MyFName = aFileName
        '''
        # Begin namespace treatment included
        MyFNameNmsp = MyFName.replace('.xml','.nmsp.xml')
        replaceString(MyFName, MyFNameNmsp,'xmlns=', 'xmlns:my=')
        self.__DicoStorage = ConvertXmlToDict(MyFNameNmsp)
        # End namespace treatment included
        '''
        self.__DicoStorage = ConvertXmlToDict(MyFName)      
    
    # Allows the modification of the dictionary   
    def modifyDict(self):
  
        #       
        # 1.possibility: self.__DicoStorage['comps']['group']['packagelist']['packagereq']['_text'] = 'red'
        # 2.possibility: self.__DicoStorage.comps.group[0].packagelist.packagereq[0]._text = 'red'
        
        return self.__DicoStorage


def replaceString(aInpFileName,aOutFileName,aInStr,aOutStr):
        '''
        This function allows the replacement of all occurrences 
        of a given string in a file via another string. The new 
        content is subsequently stored in a file. The name of the 
        output file can be the same as that of the input file.
        ''' 
        MyInpFileName = aInpFileName
        MyOutFileName = aOutFileName
        MyInpFDescr = open(MyInpFileName,'r')
        content = MyInpFDescr.read()              # read the entire input file into memory
        MyInpFDescr.close()
        MyOutFDescr = open(MyOutFileName, 'w')             
        MyOutFDescr.write(content.replace(aInStr, aOutStr))  # write the file with the text substitution
        MyOutFDescr.close()




    