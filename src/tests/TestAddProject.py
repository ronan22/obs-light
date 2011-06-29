'''
Created on 21 juin 2011

@author: rmartret
'''




from OBSLight import commandline
from OBSLight import babysitter

import sys

class TestAddProject():
    def __init__(self,sferr):
        """
        
        """
        self.__sferr=sferr
        
    def argSimpleProject(self):
        return ["addProject","projectName","test1"]

    def argMissPara(self):
        return ["addProject","projectName"]


    def testSimple(self ):
        """add one project"""
        print "add one project:",
        
        obslightcli = commandline.OBSLight()
        obslightcli.setListArgv( self.argSimpleProject() )
        r = babysitter.run( obslightcli.main )
        if r==0:
            print "SUCCEED"
        else:
            print "FAILED",
            print self.__sferr.getvalue() 
            self.__sferr.seek( 0, mode=0)

    def testMissParameter(self):
        """add one project miss parameter"""
        print "add one project miss parameter:",
        
        obslightcli = commandline.OBSLight()
        obslightcli.setListArgv( self.argMissPara() )
        
        r = babysitter.run(obslightcli.main)
        if r==1:
            print "SUCCEED"
        else:
            print "FAILED",
            print self.__sferr.getvalue() 
            self.__sferr.seek(0, mode=0)
        
        

def testRun(sferr):
    test=TestAddProject(sferr)
    test.testSimple()
    test.testMissParameter()


if __name__ == '__main__':
    
    testRun(sys.stderr)
