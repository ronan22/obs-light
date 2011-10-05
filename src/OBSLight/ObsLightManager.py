'''
Created on 17 juin 2011

@author: ronan
'''

import os

from ObsLightErr import ObsLightObsServers
from ObsServers import ObsServers
from ObsLightProjects import ObsLightProjects 

class ObsLightManager(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        init the OBS Light Manager
        '''
        
        self.__workingDirectory = os.path.join(os.environ['HOME'], "OBSLight")
        #if not exist creat the obsLight directory for the user.
        if not os.path.isdir(self.__workingDirectory):
            os.makedirs(self.__workingDirectory)
            
        self.__myOBSServers = ObsServers(self)
        self.__myObsLightProjects = ObsLightProjects(self)
        
        
    def getObsLightWorkingDirectory(self):
        '''
        
        '''
        return self.__workingDirectory
        
    def getListOBSServers(self):
        '''
        return the list of the OBS servers available
        '''
        return self.__myOBSServers.getListOBSServers()
        
    def addOBSServer(self, serverWeb="", serverAPI=None, serverRepos="", aliases=None, user=None, passw=None):
        '''
        add new OBS server.    
        '''
        if self.isAlreadyInOBSServer(serverAPI):
            raise ObsLightObsServers(serverAPI + " is already a obs server")
        elif self.isAlreadyInOBSServer(aliases):
            raise ObsLightObsServers(aliases + " is already a obs server")
        elif serverAPI == None:
            raise ObsLightObsServers("Can't create a OBSServer No API")
        elif user == None:
            raise ObsLightObsServers("Can't create a OBSServer No user")
        elif passw == None:
            raise ObsLightObsServers("Can't create a OBSServer No passw")
        
        self.__myOBSServers.addOBSServer(serverWeb=serverWeb, serverAPI=serverAPI, serverRepos=serverRepos, aliases=aliases, user=user, passw=passw)
        self.__myOBSServers.save()
        
        
    def isAlreadyInOBSServer(self, name=""):
        '''
        test if name is already a OBS server name.    
        '''
        if name in self.getListOBSServers():
            return True
        else:
            return False
        
    def addProject(self, projectName=None, projectTitle=None, projectDirectory=None, chrootDirectory=None, obsserver=None , projectTarget=None, description=None, projectArchitecture=None):
        '''
        
        '''
        if projectDirectory==None:
            projectDirectory=os.path.join(self.__workingDirectory,projectName)
        
        self.__myObsLightProjects.addProject(projectName=projectName, projectTitle=projectTitle, projectDirectory=projectDirectory, chrootDirectory=chrootDirectory, obsserver=obsserver , projectTarget=projectTarget, description=description, projectArchitecture=projectArchitecture)

        self.__myObsLightProjects.save()

    def getListProject(self):
        '''
        return the project list
        '''
        return self.__myObsLightProjects.getListProject()
        
        
    def getListPackageFromLocalProject(self,name=None,local=0):
        '''
        
        '''
        return self.__myObsLightProjects.getListPackage(name=name,local=local)
        
        
    def getListPackageListFromObsProject(self,obsserver=None,project=None):
        '''
        
        '''
        return self.__myOBSServers.getListPackage(obsserver=obsserver,project=project)
        
    def CheckoutPackage(self,obsserver=None,project=None,package=None,directory=None):
        '''
        
        '''
        self.__myOBSServers.CheckoutPackage(obsserver=obsserver,project=project,package=package,directory=directory)
    
    def getPackageStatus(self,obsserver=None,project=None,package=None,repos=None,arch=None):
        '''
        
        '''
        return self.__myOBSServers.getPackageStatus(obsserver=obsserver,project=project,package=package,repos=repos,arch=arch)
        
    def addPackage(self, project=None  ,package=None):
        '''
        
        '''
        self.__myObsLightProjects.addPackage( project=project  ,package=package)
        
        self.__myObsLightProjects.save()
        
    def createChRoot(self, project=None ):
        '''
        
        '''
        self.__myObsLightProjects.createChRoot( project=project )
        
    def getRepos(self,obsserver=None):
        '''
        
        '''
        return self.__myOBSServers.getRepos(obsserver=obsserver)
        
        
    def goToChRoot(self,project=None):
        '''
        
        '''
        self.__myObsLightProjects.goToChRoot(project=project)
        
    def addPackageSourceInChRoot(self,project=None,package=None):
        '''
        
        '''
        self.__myObsLightProjects.addPackageSourceInChRoot(project=project,package=package)
        
        
        
myObsLightManager=ObsLightManager()

def getManager():
    '''

    '''
    return myObsLightManager
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
