'''
Created on 7 juil. 2011

@author: hellmann
'''

import sys
from OBSLight import LocalRepository
from OBSLight import babysitter
from CTestRepo import CTestRepo


class TestRepo(object):
    
    def __init__(self,sferr):
        
        """
        
        """
        self.__sferr=sferr
    
    def UpDateCorrectlyRepository(self):
        
        print "Update correctly a Repository ",
        
        cliRepo_Oper = CTestRepo()
        r = babysitter.run(cliRepo_Oper.UpDateCorrectlyRepository)
        if r==0:
            print "SUCCEED"
        else:
            print "FAILED",
            print self.__sferr.getvalue() 
        self.__sferr.seek(0,mode=0) 
  
    def UpDateWronglyRepository(self):
        
        print "Update wrongly a Repository ",
        
        cliRepo_Oper = CTestRepo()
        r = babysitter.run(cliRepo_Oper.UpDateWronglyRepository)
        if r==1:
            print "SUCCEED"
        else:
            print "FAILED",
            print self.__sferr.getvalue() 
        self.__sferr.seek(0,mode=0) 

def testRun(sferr):
    
    test=TestRepo(sferr)
    test.UpDateCorrectlyRepository()
    test.UpDateWronglyRepository()
   
if __name__ == '__main__':
    import StringIO
    sferr = StringIO.StringIO()
    sys.stderr=sferr
    
    testRun(sys.stderr)
    
   
    