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
        if self.isAObsServer(serverAPI):
            raise ObsLightObsServers(serverAPI + " is already a obs server")
        elif self.isAObsServer(aliases):
            raise ObsLightObsServers(aliases + " is already a obs server")
        elif serverAPI == None:
            raise ObsLightObsServers("Can't create a OBSServer No API")
        elif user == None:
            raise ObsLightObsServers("Can't create a OBSServer No user")
        elif passw == None:
            raise ObsLightObsServers("Can't create a OBSServer No passw")
        
        self.__myOBSServers.addObsServer(serverWeb=serverWeb, serverAPI=serverAPI, serverRepos=serverRepos, aliases=aliases, user=user, passw=passw)
        self.__myOBSServers.save()
        
        
    def isAObsServer(self, name=""):
        '''
        test if name is already a OBS server name.    
        '''
        if name in self.getListOBSServers():
            return True
        else:
            return False
        
    def addProject(self, projectName=None, projectTitle=None, projectDirectory=None, chrootDirectory=None, obsserver=None , projectTarget=None, description=None, projectArchitecture=None):
        '''
        add a project from a obs to a local project
        '''
        
        if projectDirectory==None:
            projectDirectory=os.path.join(self.__workingDirectory,projectName.replace(":","_"))
            
        if projectTitle==None:
            projectTitle=projectName
            
        if projectName==None:
            raise ObsLightObsServers(" no projectName for the obs server")
        elif obsserver==None:
            raise ObsLightObsServers(" no obsserver for the project")
        elif projectTarget==None:
            raise ObsLightObsServers(" no projectTarget for the project in obs server")
        elif projectArchitecture==None:
            raise ObsLightObsServers(" no projectArchitecture for the project in obs server")
        elif (projectTitle!=None) and self.isALocalProject(projectTitle):
            raise OBSLightProjectsError(projectTitle + " is already a obs project")
        elif (projectTitle!=None) and (not projectTitle in self.getListProjectInObsServer(server=obsserver)):
            raise ObsLightObsServers(projectTitle +" is not a project in the obs server")
        elif not self.isAObsServer(obsserver):
            raise OBSLightProjectsError(obsserver + " is not  already a obs server")
        elif not projectTarget in self.getListTarget(obsserver=obsserver ,project=projectName):
            raise OBSLightProjectsError(projectTarget + " is not a target obs server")
        elif not projectArchitecture in self.getListArchitecture(obsserver=obsserver ,project=projectName,projectTarget=projectTarget):
            raise OBSLightProjectsError(projectArchitecture + " is not already a obs server")
              
        self.__myObsLightProjects.addProject(projectName=projectName, projectTitle=projectTitle, projectDirectory=projectDirectory, chrootDirectory=chrootDirectory, obsserver=obsserver , projectTarget=projectTarget, description=description, projectArchitecture=projectArchitecture)
        self.__myObsLightProjects.save()


    def getListTarget(self,obsserver=None ,project=None):
        '''
        return the list of the target of a obs server
        '''
        if obsserver==None:
            raise ObsLightObsServers(" no obsserver for the project")
        elif project==None:
            raise ObsLightObsServers(" no project for the project in obs server")
        elif not self.isAObsServer(obsserver):
            raise OBSLightProjectsError(obsserver + " is not  already a obs server")
        elif not project in self.getListProjectInObsServer(server=obsserver):
            raise ObsLightObsServers(project +" is not a project in the obs server")
                
        return self.__myOBSServers.getListTarget(obsserver=obsserver ,project=project) 
        
    def getListArchitecture(self,obsserver=None ,project=None,projectTarget=None):
        '''
        return the list of the 
        '''
        if obsserver==None:
            raise ObsLightObsServers(" no obsserver for the project")
        elif project==None:
            raise ObsLightObsServers(" no project in the  obs server")
        elif projectTarget==None:
            raise ObsLightObsServers(" no projectTarget for the project in obs server")
        elif not self.isAObsServer(obsserver):
            raise OBSLightProjectsError(obsserver + " is not  already a obs server")
        
        return self.__myOBSServers.getListArchitecture(obsserver=obsserver ,project=project,projectTarget=projectTarget)



    def isALocalProject(self,name=""):
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
        elif not self.isALocalProject(name):
            raise OBSLightProjectsError(name + " is not a local project")
        
        return self.__myObsLightProjects.getListPackage(name=name,local=local)
        
        
    def getListPackageFromObsProject(self,obsserver=None,project=None):
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
        if server==None:
            raise ObsLightObsServers(" no name for the obs server")
        elif not self.isAObsServer(server):
            raise ObsLightObsServers(server+" is not the obs server")

        return self.__myOBSServers.getListProject(server=server)
        
    def CheckoutPackage(self,obsserver=None,project=None,package=None,directory=None):
        '''
        Check out a package from a obs server to a local directory
        '''
        if obsserver==None:
            raise ObsLightObsServers(" no name for the obs server")
        elif project==None:
            raise ObsLightObsServers(" no name for the project of the obs server")
        elif package==None:
            raise ObsLightObsServers(" no name for the package of the obs server")
        elif directory==None:
            raise OBSLightProjectsError(" no name for the directory")
        elif not self.isAObsServer(name=obsserver):
            raise ObsLightObsServers(obsserver+" is not the obs server")
        elif not project in self.getListProjectInObsServer(server=obsserver):
            raise ObsLightObsServers(" no name for the package of the obs server")
        elif not package in self.getListPackageFromObsProject(obsserver=obsserver,project=project):
            raise ObsLightObsServers(" no name for the directory")
        elif not os.path.isdir(directory):
            raise OBSLightProjectsError(directory+" is not a directory")

        self.__myOBSServers.CheckoutPackage(obsserver=obsserver,project=project,package=package,directory=directory)
        self.__myObsLightProjects.save()
    
    def getPackageStatus(self,obsserver=None,project=None,package=None,repos=None,arch=None):
        '''
        return the status, from a OBS serve,r of a package for the repos and arch
        '''
        if obsserver==None:
            raise ObsLightObsServers(" no name for the obs server")
        elif project==None:
            raise ObsLightObsServers(" no name for the project of the obs server")
        elif package==None:
            raise ObsLightObsServers(" no name for the package of the obs server")
        elif not self.isAObsServer(name=obsserver):
            raise ObsLightObsServers(obsserver+" is not the obs server")
        elif not project in self.getListProjectInObsServer(server=obsserver):
            raise ObsLightObsServers(" no name for the package of the obs server")
        elif not package in self.getListPackageFromObsProject(obsserver=obsserver,project=project):
            raise ObsLightObsServers(" no name for the directory")
        
        return self.__myOBSServers.getPackageStatus(obsserver=obsserver,project=project,package=package,repos=repos,arch=arch)
        
    def addPackage(self, project=None  ,package=None):
        '''
        add a package to the local project from the obs server
        '''
        if project==None:
            raise OBSLightProjectsError(" no name for the project")
        elif package==None:
            raise OBSLightProjectsError(" no name for the package")
        elif not self.isALocalProject(name=project):
            raise OBSLightProjectsError(project+" is not a local project")
        elif not project in self.getListProjectInObsServer(server=self.__myObsLightProjects.getObsServer(name=project)):
            raise ObsLightObsServers(package+" not present in the project of the obs server")
        elif not package in self.getListPackageFromObsProject(obsserver=self.__myObsLightProjects.getObsServer(name=project),project=project):
            raise ObsLightObsServers(package+" not present in the project of the obs server")

        self.__myObsLightProjects.addPackage( project=project  ,package=package)
        
        self.__myObsLightProjects.save()
        
    def createChRoot(self, project=None ):
        '''
        create a chroot inside the project, you need a least one package.
        '''        
        if project==None:
            raise OBSLightProjectsError(" no name for the project")
        elif not self.isALocalProject(name=project):
            raise OBSLightProjectsError(project+" is not a local project")
        elif len( self.getListPackageFromLocalProject(name=project, local=1))==0:
            raise OBSLightProjectsError("no package in "+project)
        
        self.__myObsLightProjects.createChRoot( project=project )
        self.__myObsLightProjects.save()
        
    def getRepos(self,obsserver=None):
        '''
        return the name of the repos of the OBS server
        '''
        if obsserver==None:
            raise ObsLightObsServers(" no name for the obs server")
        elif not self.isAObsServer(name=obsserver):
            raise ObsLightObsServers(obsserver+" is not the obs server")
        return self.__myOBSServers.getRepos(obsserver=obsserver)
        
        
    def goToChRoot(self,project=None,package=None):
        '''
        offer a bash in the chroot for the user
        if package  define, the pwd will be ~/rpmbuild/BUILD/[package]
        '''
        
        if project==None:
            raise OBSLightProjectsError(" no name for the project")
        
        elif (package!=None) and (not package in self.getListPackageFromLocalProject(name=project, local=1)):
            raise OBSLightProjectsError(package+" not in project")
        
        self.__myObsLightProjects.goToChRoot(project=project,package=package)
        
    def addPackageSourceInChRoot(self,project=None,package=None):
        '''
        add a rpm source from the obs repos into the chroot
        '''
        if project==None:
            raise OBSLightProjectsError(" no name for the project")
        elif package==None:
            raise OBSLightProjectsError(" no name for the package")
        elif not self.isALocalProject(name=project):
            raise OBSLightProjectsError(project+" is not a local project")
        #TODO test if package can be install
        
        self.__myObsLightProjects.addPackageSourceInChRoot(project=project,package=package)
        self.__myObsLightProjects.save()
        
    def makePatch(self,project=None,package=None,patch=None):
        '''
        generate patch, and add it to the local obs package, modifi the spec file.
        '''
        if project==None:
            raise OBSLightProjectsError(" no name for the project")
        elif package==None:
            raise OBSLightProjectsError(" no name for the package")
        elif patch==None:
            raise OBSLightProjectsError(" no name for the patch")
        elif not self.isALocalProject(name=project):
            raise OBSLightProjectsError(project+" is not a local project")
        elif not package in self.getListPackageFromLocalProject(name=project, local=1):
            raise OBSLightProjectsError(package+" is not a local package")
        
        self.__myObsLightProjects.makePatch(project=project,package=package,patch=patch)
        self.__myObsLightProjects.save()

        
myObsLightManager=ObsLightManager()

def getManager():
    '''

    '''
    return myObsLightManager
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
