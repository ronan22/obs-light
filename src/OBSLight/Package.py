'''
Created on 17 juin 2011

@author: rmartret
'''
from RPMFileObject import RPMFileObject


class Package(object):
    '''
    classdocs
    '''
    

    def __init__(self,packageName=None):
        '''
        Constructor
        '''
        self.__packageName=packageName
        
        self.__rPMFileObject=None
        
        self.__listStatus=["NotBuilt","Built","BuildFailed"]
        
        self.__packageStatus=self.__listStatus[0]
        
        self.__sourceFile={}
        
        self.__rPMName=packageName
        self.__rPMVersion=None
        self.__RPMPackageVersion=None
        
        
    def setRpmFileObject(self,rpmFileName):
        self.__rPMFileObject=RPMFileObject(rpmFileName)
        
        
        
        
        
        