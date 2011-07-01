'''
Created on 30 juin 2011

@author: hellmann
'''

import sys
from OBSLight import XML_Parse
from OBSLight import babysitter

 

class CTestXML():
    
    def __init__(self):
        """
        
        """
        
    def loadTrueFile(self):
        url="./XMLFileTest/input1.xml"
        aXML_Parse=XML_Parse.XML_Parse()
        return aXML_Parse.ExistsXMLVerif(url)
        
    def loadNoFile(self):
        url="./XMLFileTest/NONE.xml"
        aXML_Parse=XML_Parse.XML_Parse()
        return aXML_Parse.ExistsXMLVerif(url)

    def loadNonEmptyFile(self):
        url="./XMLFileTest/Empty.xml"
        aXML_Parse=XML_Parse.XML_Parse()
        return aXML_Parse.EmptyXMLVerif(url)
    
    def loadEmptyFile(self):
        url="./XMLFileTest/Empty.xml"
        aXML_Parse=XML_Parse.XML_Parse()
        return aXML_Parse.EmptyXMLVerif(url)
    
    def parseGoodFile(self):
        url="./XMLFileTest/input.xml"
        aXML_Parse=XML_Parse.XML_Parse()
        return aXML_Parse.StructureXMLVerif(url)
    
    def parseBadFile(self):
        url="./XMLFileTest/pourri.xml"
        aXML_Parse=XML_Parse.XML_Parse()
        return aXML_Parse.StructureXMLVerif(url)
    
    
    
    
    
    
    
