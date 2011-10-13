'''
Created on 30 sept. 2011

@author: ronan
'''
import os

from ObsLightPackage import ObsLightPackage

class ObsLightPackages(object):
    '''
    classdocs
    '''


    def __init__(self,fromSave=None):
        '''
        Constructor
        '''
        self.__dicOBSLightPackages={}
        if fromSave==None:
            self.__currentPackage=""
        else:

            for name in fromSave["savePackages"].keys():
                self.__dicOBSLightPackages[name]=ObsLightPackage(fromSave=fromSave["savePackages"][name])
            self.__currentPackage=fromSave["currentPackage"]

    def getListPackages(self):
        '''
        
        '''
        return self.__dicOBSLightPackages.keys()
    
    def getDic(self):
        '''
        
        '''
        aDic={}
        for pack in self.getListPackages():
            aDic[pack]=self.__dicOBSLightPackages[pack].getDic()
        
        saveconfigPackages={}    
        saveconfigPackages["savePackages"]  =aDic
        saveconfigPackages["currentPackage"]=self.__currentPackage
        
        
        return saveconfigPackages
        
        
    def addPackage(self,name=None, specFile=None, listFile=[], status=""):
        '''
        
        '''
        self.__currentPackage=name
        
        
        self.__dicOBSLightPackages[name]=ObsLightPackage(name=name, specFile=specFile, listFile=listFile, status=status)
        
        
    def getPackageStatus(self,name=None):
        '''
        
        '''
        return self.__dicOBSLightPackages[name].getStatus()
        
    def getSpecFile(self,name=None):
        '''
        
        '''
        return self.__dicOBSLightPackages[name].getSpecFile()
        
    def getOscDirectory(self,name=None):
        '''
        
        '''
        return self.__dicOBSLightPackages[name].getOscDirectory()
        
        
    def getPackage(self,package=None):
        '''
        
        '''
        return self.__dicOBSLightPackages[package]
    
    def getPackageDirectory(self,package=None):
        '''
        
        '''
        return self.__dicOBSLightPackages[package].getPackageDirectory()
        
        
        
        