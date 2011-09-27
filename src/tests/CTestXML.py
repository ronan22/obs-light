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
        url="./XMLFileTest/NonXML.xml"
        aXML_Parse=XML_Parse.XML_Parse()
        return aXML_Parse.StructureXMLVerif(url)
    
    def convertGoodDictToXML(self):
        
        GoodDict={'CATALOG': {'CD': [{'ARTIST': 'Bob Dylan',
                                     'attr_My_attr1': 'My_attr1_test',
                                     'Test_liste' :
                                     [{'_text': 'My_text1_test'},
                                     {'_text': 'My_text2_test'}],
                                     'COMPANY': 'Columbia',
                                     'COUNTRY': 'USA',
                                     'PRICE': '10.90',
                                     'TITLE': 'Empire Burlesque',
                                     'YEAR': '1985'},
                                    {'ARTIST': 'Bonnie Tyler',
                                     'COMPANY': 'CBS Records',
                                     'COUNTRY': 'UK',
                                     'PRICE': '9.90',
                                     'TITLE': 'Hide your heart',
                                     'YEAR': '1988'}]}}       
       
        XMLOutFile="./XMLFileTest/OutpForGoodDict.xml"
        aXML_Parse=XML_Parse.XML_Parse()
        return aXML_Parse.ConvertDictToXMLVerif(GoodDict,XMLOutFile)
    
    def convertBadDictToXML(self):
        # In BadDict when compared to GoodDict the "{" bracket before 'ARTIST' is missing
        
        #alternatively: BadDict=5
        BadDict={}
        XMLOutFile="./XMLFileTest/OutpForBadDict.xml"
        aXML_Parse=XML_Parse.XML_Parse()
        return aXML_Parse.ConvertDictToXMLVerif(BadDict,XMLOutFile)
    
    def modifyCorrectlyDict(self):
        
        MyDict = {'CATALOG': {'CD': [{'ARTIST': 'Bob Dylan',
                                   'attr_My_attr1': 'My_attr1_test',
                                   'Test_liste' :
                                   [{'_text': 'My_text1_test'},
                                   {'_text': 'My_text2_test'}],
                                    'COMPANY': 'Columbia',
                                    'COUNTRY': 'USA',
                                    'PRICE': '10.90',
                                    'TITLE': 'Empire Burlesque',
                                    'YEAR': '1985'},
                                   {'ARTIST': 'Bonnie Tyler',
                                    'COMPANY': 'CBS Records',
                                    'COUNTRY': 'UK',
                                    'PRICE': '9.90',
                                    'TITLE': 'Hide your heart',
                                    'YEAR': '1988'}]}}       
        
        CorrectDictList = ['CATALOG', 'CD', 0, 'ARTIST']
        
        XMLOutDict = "./XMLFileTest/ModifyGoodDict"       
        XMLOutFile = "./XMLFileTest/ModifyGoodDict.xml"
        aXML_Parse=XML_Parse.XML_Parse()
        return aXML_Parse.ModifDictVerif(MyDict,'ToryAmos',CorrectDictList)
            
    def modifyWronglyDict(self):
        
        MyDict = {'CATALOG': {'CD': [{'ARTIST': 'Bob Dylan',
                                   'attr_My_attr1': 'My_attr1_test',
                                   'Test_liste' :
                                   [{'_text': 'My_text1_test'},
                                   {'_text': 'My_text2_test'}],
                                    'COMPANY': 'Columbia',
                                    'COUNTRY': 'USA',
                                    'PRICE': '10.90',
                                    'TITLE': 'Empire Burlesque',
                                    'YEAR': '1985'},
                                   {'ARTIST': 'Bonnie Tyler',
                                    'COMPANY': 'CBS Records',
                                    'COUNTRY': 'UK',
                                    'PRICE': '9.90',
                                    'TITLE': 'Hide your heart',
                                    'YEAR': '1988'}]}}       
        
        WrongDictList = ['CATALOG', 'CD', 'ARTIST']
        XMLOutDict = "./XMLFileTest/ModifyGoodDict"       
        XMLOutFile = "./XMLFileTest/ModifyGoodDict.xml"
        aXML_Parse=XML_Parse.XML_Parse()
        return aXML_Parse.ModifDictVerif(MyDict,'ToryAmos',WrongDictList)
        
    
       
    
