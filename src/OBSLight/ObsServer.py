'''
Created on 29 sept. 2011

@author: ronan
'''
import os


import ObsLightOsc


class ObsServer(object):
    '''
    classdocs
    '''


    def __init__(self,serverWeb="",serverAPI=None,serverRepos="",aliases=None,user=None,passw=None,fromSave=None):
        '''
        Create a reference to a OBS server
        ''' 
        if fromSave!=None:
            self.__isOBSConnected=fromSave["isOBSConnected"]
            self.__serverWeb=fromSave["serverWeb"]
            self.__serverAPI=fromSave["serverAPI"]
            self.__serverRepos=fromSave["serverRepos"]
            self.__aliases=fromSave["aliases"]
            self.__user=fromSave["user"]
            self.__passw=fromSave["passw"]
        else:
            self.__isOBSConnected=False
            self.__serverWeb=serverWeb
            self.__serverAPI=serverAPI
            self.__serverRepos=serverRepos
            if (aliases==None):
                self.__aliases=self.__serverAPI
            else:
                self.__aliases=aliases
            self.__user=user
            self.__passw=passw
        
        ObsLightOsc.myObsLightOsc.initConf(api=self.__serverAPI,user=self.__user,passw=self.__passw,aliases=self.__aliases)
        

            
        
    def getDic(self):
        '''
        return a description of the object in a dictionary  
        '''
        aDic={}
        aDic["isOBSConnected"]=self.__isOBSConnected=False
        aDic["serverWeb"]=self.__serverWeb
        aDic["serverAPI"]=self.__serverAPI
        aDic["serverRepos"]=self.__serverRepos
        aDic["aliases"]=self.__aliases
        aDic["user"]=self.__user
        aDic["passw"]=self.__passw
        return aDic
    
    def getName(self):
        '''
        return the Obs server name.
        '''
        return self.__aliases
    
    def getListPackage(self,project=None):
        '''
        
        '''
        return ObsLightOsc.myObsLightOsc.getListPackage(obsServer=self.__serverAPI,project=project)
    
    def CheckoutPackage(self,project=None,package=None,directory=None):
        '''
        
        '''
        ObsLightOsc.myObsLightOsc.CheckoutPackage(obsServer=self.__serverAPI,project=project,package=package,directory=directory)
        
    def getPackageStatus(self,project=None,package=None,repos=None,arch=None):
        '''
        
        '''
        return  ObsLightOsc.myObsLightOsc.getPackageStatus(obsServer=self.__serverAPI,project=project,package=package,repos=repos,arch=arch)
    
    
    def getRepos(self):
        '''
        
        '''
        return self.__serverRepos
    
    
    
    
    
    
    
        
        
    
    