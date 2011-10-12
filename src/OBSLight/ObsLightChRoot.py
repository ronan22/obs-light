'''
Created on 30 sept. 2011

@author: meego
'''

import os

import ObsLightOsc
import ObsLightMic 
import subprocess
import shlex


class ObsLightChRoot(object):
    '''
    classdocs
    '''


    def __init__(self,chrootDirectory=None,fromSave=None):
        '''
        Constructor
        '''
        if fromSave==None:
            self.__chrootDirectory=chrootDirectory
        else:
            self.__chrootDirectory=fromSave["chrootDirectory"]
        
        self.initChRoot()
        
    def initChRoot(self):
        '''
        
        '''
        if not os.path.isdir(self.__chrootDirectory):
            os.makedirs(self.__chrootDirectory)
                    
            command="sudo chown root:root "+self.__chrootDirectory
            command=command.split()
            subprocess.call(command, stdin=open("/dev/null", "r"), close_fds=True)

        
            
    def getDic(self):
        '''
        
        '''
        saveconfigPackages={}    
        saveconfigPackages["chrootDirectory"]=self.__chrootDirectory
        
        return saveconfigPackages
    
    def addProjectSource(self):
        '''
        
        '''
        
    
    
    def createChRoot(self, projectDir=None ,repos=None,arch=None,specPath=None):
        '''
        
        '''
        ObsLightOsc.myObsLightOsc.createChRoot( chrootDir=self.__chrootDirectory,projectDir=projectDir ,repos=repos,arch=arch,specPath=specPath)
        ObsLightMic.myObsLightMic.initRpmDb(chrootDir=self.__chrootDirectory)
        
        
    def addRepos(self,repos=None,alias=None):
        '''
        
        '''
        ObsLightMic.myObsLightMic.addRepos(chrootDir=self.__chrootDirectory,repos=repos,alias=alias)
        
    def initGitWatch(self,path=None):
        '''
        
        '''
        ObsLightMic.myObsLightMic.initGitWatch(self,chrootDir=self.__chrootDirectory,path=path)
    
    def goToChRoot(self):
        '''
        
        '''
        ObsLightMic.myObsLightMic.goToChRoot(chrootDir=self.__chrootDirectory)
    
    def addPackageSourceInChRoot(self,package=None):
        '''
        
        '''
        print "chrootDir=",self.__chrootDirectory,"package=",package
        ObsLightMic.myObsLightMic.addPackageSourceInChRoot(chrootDir=self.__chrootDirectory,package=package)
    
    
    
    
