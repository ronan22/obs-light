'''
Created on 17 juin 2011

@author: ronan
'''

import os

from ObsLightErr import ObsLightObsServers
from ObsLightErr import OBSLightProjectsError
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
        
    def addObsServer(self, serverWeb="", serverAPI=None, serverRepos="", aliases=None, user=None, passw=None):
        '''
        add new OBS server.    
        '''
        if self.isAnObsServer(serverAPI):
            raise ObsLightObsServers(serverAPI + " is already a obs server")
        elif self.isAnObsServer(aliases):
            raise ObsLightObsServers(aliases + " is already a obs server")
        elif serverAPI == None:
            raise ObsLightObsServers("Can't create a OBSServer No API")
        elif user == None:
            raise ObsLightObsServers("Can't create a OBSServer No user")
        elif passw == None:
            raise ObsLightObsServers("Can't create a OBSServer No passw")
        
        self.__myOBSServers.addObsServer(serverWeb=serverWeb, serverAPI=serverAPI, serverRepos=serverRepos, aliases=aliases, user=user, passw=passw)
        self.__myOBSServers.save()
        
        
    def isAnObsServer(self, name=""):
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
            projectDirectory=os.path.join(self.__workingDirectory,projectName.replace(":","_"))
        
        
        if self.isAnObsProject(projectName):
            raise OBSLightProjectsError(projectName + " is already a obs project")
        elif self.isAnObsProject(projectTitle):
            raise OBSLightProjectsError(projectTitle + " is already a obs project")
        
                
        self.__myObsLightProjects.addProject(projectName=projectName, projectTitle=projectTitle, projectDirectory=projectDirectory, chrootDirectory=chrootDirectory, obsserver=obsserver , projectTarget=projectTarget, description=description, projectArchitecture=projectArchitecture)

        self.__myObsLightProjects.save()

    def isAnObsProject(self,name=""):
        '''
        test if name is already a OBS Project name.    
        '''
        if name in self.getListProject():
            return True
        else:
            return False

    def getListProject(self):
        '''
        return the project list
        '''
        return self.__myObsLightProjects.getListProject()
        
        
    def getListPackageFromLocalProject(self,name=None,local=0):
        '''
        return the list of the package of a project
        if local=1 the list is the list of the package install locally
        if local=0 the list is the list of the package provide by the obs server of the project
        '''
        if name==None:
            raise OBSLightProjectsError("not name for the project")
        elif not self.isAnObsProject(name):
            raise OBSLightProjectsError(name + " is not a obs project")
        
        return self.__myObsLightProjects.getListPackage(name=name,local=local)
        
        
    def getListPackageListFromObsProject(self,obsserver=None,project=None):
        '''
        return the list of the package of a project of a OBS server
        '''
        if obsserver==None:
            raise ObsLightObsServers(" no name for the obs server")
        elif project==None:
            raise ObsLightObsServers(" no name for the project of the obs server")
        elif not project in self.getListProjectInObsServer(server=obsserver):
            raise ObsLightObsServers(project + " is not a obs project")
        
        return self.__myOBSServers.getListPackage(obsserver=obsserver,project=project)
        
        
    def getListProjectInObsServer(self,server=None):
        '''
        return the list of the project of a OBS server
        '''
        if self.isAnObsServer(server):
            raise ObsLightObsServers(" no name for the obs server")
        return self.__myOBSServers.getListProject(server=server)
        
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
        self.__myObsLightProjects.save()
        
    def getRepos(self,obsserver=None):
        '''
        
        '''
        return self.__myOBSServers.getRepos(obsserver=obsserver)
        
        
    def goToChRoot(self,project=None,package=None):
        '''
        
        '''
        self.__myObsLightProjects.goToChRoot(project=project,package=package)
        
    def addPackageSourceInChRoot(self,project=None,package=None):
        '''
        
        '''
        self.__myObsLightProjects.addPackageSourceInChRoot(project=project,package=package)
        self.__myObsLightProjects.save()
        
    def makePatch(self,project=None,package=None,patch=None):
        '''
        
        '''
        self.__myObsLightProjects.makePatch(project=project,package=package,patch=patch)
        self.__myObsLightProjects.save()

        
myObsLightManager=ObsLightManager()

def getManager():
    '''

    '''
    return myObsLightManager
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
