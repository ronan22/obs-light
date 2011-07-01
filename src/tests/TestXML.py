'''
Created on 30 juin 2011

@author: hellmann
'''

import sys
from OBSLight import XML_Parse
from OBSLight import babysitter

from CTestXML import CTestXML

class TestXML():
    
    def __init__(self,sferr):
        """
        
        """
        self.__sferr=sferr
    
    def loadTrueFile(self ):
        
        print "XML loadTrueFile: ",
        
        cliXML_Parse = CTestXML()
        r = babysitter.run(cliXML_Parse.loadTrueFile)
        if r==0:
            print "SUCCEED"
        else:
            print "FAILED",
            print self.__sferr.getvalue() 
        self.__sferr.seek(0,mode=0) 
      
    def loadNoFile(self ):
        
        print "XML loadNoFile: ",
        
        cliXML_Parse = CTestXML()
        r = babysitter.run(cliXML_Parse.loadNoFile)
        if r==1:
            print "SUCCEED"
        else:
            print "FAILED",
            print self.__sferr.getvalue() 
        self.__sferr.seek(0,mode=0) 
            
    def loadNonEmptyFile(self ):
        
        print "XML loadNonEmptyFile: ",
        
        cliXML_Parse = CTestXML()
        r = babysitter.run(cliXML_Parse.loadNonEmptyFile)
        if r==0:
            print "SUCCEED"
        else:
            print "FAILED",
            print self.__sferr.getvalue() 
        self.__sferr.seek(0,mode=0) 

    def loadEmptyFile(self ):
        
        print "XML loadEmptyFile: ",
        
        cliXML_Parse = CTestXML()
        r = babysitter.run(cliXML_Parse.loadEmptyFile)
        if r==1:
            print "SUCCEED"
        else:
            print "FAILED",
            print self.__sferr.getvalue() 
        self.__sferr.seek(0,mode=0) 
        
    def parseGoodFile(self):
        
        print "XML parseGoodFile: ",
        
        cliXML_Parse = CTestXML()
        r = babysitter.run(cliXML_Parse.parseGoodFile)
        if r==0:
            print "SUCCEED"
        else:
            print "FAILED",
            print self.__sferr.getvalue() 
        self.__sferr.seek(0,mode=0) 
        
    def parseBadFile(self):
        
        print "XML parseBadFile: ",
        
        cliXML_Parse = CTestXML()
        r = babysitter.run(cliXML_Parse.parseBadFile)
        if r==1:
            print "SUCCEED"
        else:
            print "FAILED",
            print self.__sferr.getvalue() 
        self.__sferr.seek(0,mode=0) 
        
   
        
def testRun(sferr):
    
    test=TestXML(sferr)
    test.loadTrueFile()
    test.loadNoFile()
    test.loadNonEmptyFile()
    test.loadEmptyFile()
    test.parseGoodFile()
    test.parseBadFile()

if __name__ == '__main__':
    import StringIO
    sferr = StringIO.StringIO()
    sys.stderr=sferr
    
    testRun(sys.stderr)
    
    