'''
Created on 29 sept. 2011

@author: meego
'''

import pickle
import os

from ObsLightErr import ObsLightObsServers
from ObsServer import ObsServer
import ObsLightOsc

class ObsServers(object):
    '''
    classdocs
    '''


    def __init__(self,manager):
        '''
        Constructor
        '''
        self.__dicOBSLightServers={}
        self.__currentServer=None
        self.__manager=manager
        self.__pathFile = os.path.join(self.__manager.getObsLightWorkingDirectory() ,"ObsServersConfig")
        self.__load()
        
        
    def getListOBSServers(self):
        '''
        
        '''
        return self.__dicOBSLightServers.keys()
    
    def save(self):
        '''
        
        '''
        saveServers={}

        for obsserverName in self.getListOBSServers():
            saveServers[obsserverName]= self.__dicOBSLightServers[obsserverName].getDic()
        
        saveconfigServers={}
        saveconfigServers["saveServers"]=saveServers
        saveconfigServers["currentObsServer"]=self.__currentServer    
        file=open(self.__pathFile,'w')
        pickle.dump(saveconfigServers,file)    
        file.close()
        
    def __load(self):
        '''
        
        '''
        if os.path.isfile(self.__pathFile):
            file=open(self.__pathFile,'r')
            saveconfigServers=pickle.load(file)
            file.close()
            saveServers=saveconfigServers["saveServers"]
            for projetName in saveServers.keys():
                aServer=saveServers[projetName]
                self.__addOBSServerFromSave(fromSave=aServer)    
            self.__currentOBSServer= saveconfigServers["currentObsServer"]
            
    def __addOBSServerFromSave(self,fromSave=None):
        '''
        
        '''
        aOBSServer=ObsServer(fromSave=fromSave)
        self.__dicOBSLightServers[aOBSServer.getName()]=aOBSServer
        
        
    def addObsServer(self, serverWeb="", serverAPI=None, serverRepos="", aliases=None, user=None, passw=None):
        '''
        
        '''
        aOBSServer=ObsServer(serverWeb=serverWeb, serverAPI=serverAPI, serverRepos=serverRepos, aliases=aliases, user=user, passw=passw)
        self.__dicOBSLightServers[aOBSServer.getName()]=aOBSServer
        
    def getListPackage(self,obsserver=None,project=None):
        '''
        
        '''
        return self.__dicOBSLightServers[obsserver].getListPackage(project=project)
    
    def CheckoutPackage(self,obsserver=None,project=None,package=None,directory=None):
        '''
        
        '''
        self.__dicOBSLightServers[obsserver].CheckoutPackage(project=project,package=package,directory=directory)
        
    def getPackageStatus(self,obsserver=None,project=None,package=None,repos=None,arch=None):
        '''
        
        '''
        return self.__dicOBSLightServers[obsserver].getPackageStatus(project=project,package=package,repos=repos,arch=arch)
        
    def getRepos(self,obsserver=None):
        '''
        
        '''
        return self.__dicOBSLightServers[obsserver].getRepos()

        
        
        
            