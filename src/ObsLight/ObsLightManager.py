#
# Copyright 2011, Intel Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
'''
Created on 17 juin 2011

@author: ronan
'''

import os

from ObsLightErr import ObsLightObsServers
from ObsLightErr import ObsLightProjectsError
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
            
        self.__myObsServers = ObsServers(self)
        self.__myObsLightProjects = ObsLightProjects(self)
        
        
    def getObsLightWorkingDirectory(self):
        '''
        
        '''
        return self.__workingDirectory
        
    def getListObsServers(self):
        '''
        return the list of the OBS servers available
        '''
        return self.__myObsServers.getListObsServers()
        
    def addObsServer(self, serverWeb="",
                            serverAPI=None,
                            serverRepos="",
                            aliases=None,
                            user=None,
                            passw=None):
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
        
        self.__myObsServers.addObsServer(serverWeb=serverWeb, serverAPI=serverAPI, serverRepos=serverRepos, aliases=aliases, user=user, passw=passw)
        self.__myObsServers.save()
        
        
    def getObsServer(self, name=None):
        '''
        
        '''
        return self.__myObsServers.getObsServer(name=name)
        
        
    def isAObsServer(self, name=""):
        '''
        test if name is already a OBS server name.    
        '''
        if name in self.getListObsServers():
            return True
        else:
            return False
        
    def addProject(self, projectLocalName=None,
                        projectObsName=None,
                        projectTitle=None,
                        projectDirectory=None,
                        chrootDirectory=None,
                        obsServer=None,
                        projectTarget=None,
                        description=None,
                        projectArchitecture=None):
        '''
        add a project from a obs to a local project
        '''
        
        if projectLocalName == None:
            projectLocalName = projectObsName.replace(":", "_")
            
        if projectDirectory == None:
            projectDirectory = os.path.join(self.__workingDirectory, projectLocalName)
        
        if ":" in projectLocalName:
            raise ObsLightProjectsError("You can't have ':' in the projectLocalName " + projectLocalName)
        if projectObsName == None:
            raise ObsLightObsServers(" no projectObsName for the obs server")
        elif obsServer == None:
            raise ObsLightObsServers(" no OBS server for the project")
        elif projectTarget == None:
            raise ObsLightObsServers(" no projectTarget for the project in obs server")
        elif projectArchitecture == None:
            raise ObsLightObsServers(" no projectArchitecture for the project in obs server")
        elif self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is already a local project")
        elif (projectObsName != None) and (not projectObsName in self.getListProjectInObsServer(server=obsServer)):
            raise ObsLightObsServers(projectObsName + " is not a project in the obs server")
        elif not self.isAObsServer(obsServer):
            raise ObsLightProjectsError(obsServer + " is not  already a obs server")
        elif not projectTarget in self.getListTarget(obsServer=obsServer , project=projectObsName):
            raise ObsLightProjectsError(projectTarget + " is not a target obs server")
        elif not projectArchitecture in self.getListArchitecture(obsServer=obsServer , project=projectObsName, projectTarget=projectTarget):
            raise ObsLightProjectsError(projectArchitecture + " is not already a obs server")
              
        self.__myObsLightProjects.addProject(projectLocalName=projectLocalName, projectObsName=projectObsName, projectTitle=projectTitle, projectDirectory=projectDirectory, chrootDirectory=chrootDirectory, obsServer=obsServer , projectTarget=projectTarget, description=description, projectArchitecture=projectArchitecture)
        self.__myObsLightProjects.save()


    def getListTarget(self, obsServer=None , project=None):
        '''
        return the list of the target of a obs server
        '''
        if obsServer == None:
            raise ObsLightObsServers(" no obsServer for the project")
        elif project == None:
            raise ObsLightObsServers(" no project for the project in obs server")
        elif not self.isAObsServer(obsServer):
            raise ObsLightProjectsError(obsServer + " is not  already a obs server")
        elif not project in self.getListProjectInObsServer(server=obsServer):
            raise ObsLightObsServers(project + " is not a project in the obs server")
                
        return self.__myObsServers.getListTarget(obsServer=obsServer , project=project) 
        
    def getListArchitecture(self, obsServer=None , project=None, projectTarget=None):
        '''
        return the list of the 
        '''
        if obsServer == None:
            raise ObsLightObsServers(" no obsServer for the project")
        elif project == None:
            raise ObsLightObsServers(" no project in the  obs server")
        elif projectTarget == None:
            raise ObsLightObsServers(" no projectTarget for the project in obs server")
        elif not self.isAObsServer(obsServer):
            raise ObsLightProjectsError(obsServer + " is not  already a obs server")
        
        return self.__myObsServers.getListArchitecture(obsServer=obsServer ,
                                                       project=project,
                                                       projectTarget=projectTarget)



    def isALocalProject(self, name=""):
        '''
        test if name is already a OBS Project name.    
        '''
        if name in self.getListLocalProject():
            return True
        else:
            return False

    def getListLocalProject(self):
        '''
        return the project list
        '''
        return self.__myObsLightProjects.getListLocalProject()
        
        
    def getListPackageFromLocalProject(self, name=None, local=0):
        '''
        return the list of the package of a project
        if local=1 the list is the list of the package install locally
        if local=0 the list is the list of the package provide by the obs server of the project
        '''
        if name == None:
            raise ObsLightProjectsError("not name for the project")
        elif not self.isALocalProject(name):
            raise ObsLightProjectsError(name + " is not a local project")
        
        return self.__myObsLightProjects.getListPackage(name=name, local=local)
        
        
    def getListPackageFromObsProject(self, obsServer=None, projectLocalName=None):
        '''
        return the list of the package of a projectLocalName of a OBS server
        '''
        if obsServer == None:
            raise ObsLightObsServers(" no name for the obs server")
        elif projectLocalName == None:
            raise ObsLightObsServers(" no name for the projectLocalName of the obs server")
        elif not projectLocalName in self.getListProjectInObsServer(server=obsServer):
            raise ObsLightObsServers(projectLocalName + " is not a obs projectLocalName")
        
        return self.__myObsServers.getListPackage(obsServer=obsServer, projectLocalName=projectLocalName)
        
        
    def getListProjectInObsServer(self, server=None):
        '''
        return the list of the project of a OBS server
        '''
        if server == None:
            raise ObsLightObsServers(" no name for the obs server")
        elif not self.isAObsServer(server):
            raise ObsLightObsServers(server + " is not the obs server")

        return self.__myObsServers.getListLocalProject(server=server)
        
    def CheckoutPackage(self, obsServer=None,
                                projectLocalName=None,
                                package=None,
                                directory=None):
        '''
        Check out a package from a obs server to a local directory
        '''
        if obsServer == None:
            raise ObsLightObsServers(" no name for the obs server")
        elif projectLocalName == None:
            raise ObsLightObsServers(" no name for the projectLocalName of the obs server")
        elif package == None:
            raise ObsLightObsServers(" no name for the package of the obs server")
        elif directory == None:
            raise ObsLightProjectsError(" no name for the directory")
        elif not self.isAObsServer(name=obsServer):
            raise ObsLightObsServers(obsServer + " is not the obs server")
        elif not projectLocalName in self.getListProjectInObsServer(server=obsServer):
            raise ObsLightObsServers(" no name for the package of the obs server")
        elif not package in self.getListPackageFromObsProject(obsServer=obsServer,
                                                              projectLocalName=projectLocalName):
            raise ObsLightObsServers(" no name for the directory")
        elif not os.path.isdir(directory):
            raise ObsLightProjectsError(directory + " is not a directory")

        self.__myObsServers.CheckoutPackage(obsServer=obsServer,
                                            projectLocalName=projectLocalName,
                                            package=package,
                                            directory=directory)
        self.__myObsLightProjects.save()
    
    def getPackageStatus(self, obsServer=None,
                                project=None,
                                package=None,
                                repos=None,
                                arch=None):
        '''
        return the status, from a OBS serve,r of a package for the repos and arch
        '''
        if obsServer == None:
            raise ObsLightObsServers(" no name for the obs server")
        elif project == None:
            raise ObsLightObsServers(" no name for the project of the obs server")
        elif package == None:
            raise ObsLightObsServers(" no name for the package of the obs server")
        elif not self.isAObsServer(name=obsServer):
            raise ObsLightObsServers(obsServer + " is not the obs server")
        elif not project in self.getListProjectInObsServer(server=obsServer):
            raise ObsLightObsServers(" no name for the package of the obs server")
        elif not package in self.getListPackageFromObsProject(obsServer=obsServer, projectLocalName=project):
            raise ObsLightObsServers(" no name for the directory")
        
        return self.__myObsServers.getPackageStatus(obsServer=obsServer,
                                                    project=project,
                                                    package=package,
                                                    repos=repos,
                                                    arch=arch)
        
    def addPackage(self, projectLocalName=None  , package=None):
        '''
        add a package to the local projectLocalName from the obs server
        '''
        if projectLocalName == None:
            raise ObsLightProjectsError(" no name for the projectLocalName")
        elif package == None:
            raise ObsLightProjectsError(" no name for the package")
        elif not self.isALocalProject(name=projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local projectLocalName")
        elif not projectLocalName in self.getListLocalProject():
            raise ObsLightObsServers(projectLocalName + " not present in the projectLocalName of the obs server")
        elif not package in self.getListPackageFromObsProject(obsServer=self.__myObsLightProjects.getObsServer(name=projectLocalName),
                                                                projectLocalName=self.__myObsLightProjects.getProjectObsName(projectLocalName=projectLocalName)):
            raise ObsLightObsServers(package + " not present in the projectLocalName of the obs server")

        self.__myObsLightProjects.addPackage(projectLocalName=projectLocalName  , package=package)
        
        self.__myObsLightProjects.save()
        
    def createChRoot(self, projectLocalName=None):
        '''
        create a chroot inside the projectLocalName, you need a least one package.
        '''        
        if projectLocalName == None:
            raise ObsLightProjectsError(" no name for the projectLocalName")
        elif not self.isALocalProject(name=projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local projectLocalName")
        elif len(self.getListPackageFromLocalProject(name=projectLocalName, local=1)) == 0:
            raise ObsLightProjectsError("no package in " + projectLocalName)
        
        self.__myObsLightProjects.createChRoot(projectLocalName=projectLocalName)
        self.__myObsLightProjects.save()
        
    def getRepos(self, obsServer=None):
        '''
        return the name of the repos of the OBS server
        '''
        if obsServer == None:
            raise ObsLightObsServers(" no name for the obs server")
        elif not self.isAObsServer(name=obsServer):
            raise ObsLightObsServers(obsServer + " is not the obs server")
        return self.__myObsServers.getRepos(obsServer=obsServer)
        
        
    def goToChRoot(self, projectLocalName=None, package=None):
        '''
        offer a bash in the chroot for the user
        if package  define, the pwd will be ~/rpmbuild/BUILD/[package]
        '''
        
        if projectLocalName == None:
            raise ObsLightProjectsError(" no name for the projectLocalName")
        
        elif (package != None) and (not package in self.getListPackageFromLocalProject(name=projectLocalName, local=1)):
            raise ObsLightProjectsError(package + " not in projectLocalName")
        
        self.__myObsLightProjects.goToChRoot(projectLocalName=projectLocalName, package=package)
        
    def addPackageSourceInChRoot(self, projectLocalName=None, package=None):
        '''
        add a rpm source from the obs repos into the chroot
        '''
        if projectLocalName == None:
            raise ObsLightProjectsError(" no name for the projectLocalName")
        elif package == None:
            raise ObsLightProjectsError(" no name for the package")
        elif not self.isALocalProject(name=projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local projectLocalName")
        #TODO test if package can be install
        
        self.__myObsLightProjects.addPackageSourceInChRoot(projectLocalName=projectLocalName,
                                                           package=package)
        self.__myObsLightProjects.save()
        
    def makePatch(self, projectLocalName=None,
                        package=None,
                        patch=None):
        '''
        generate patch, and add it to the local obs package, modifi the spec file.
        '''
        if projectLocalName == None:
            raise ObsLightProjectsError(" no name for the projectLocalName")
        elif package == None:
            raise ObsLightProjectsError(" no name for the package")
        elif patch == None:
            raise ObsLightProjectsError(" no name for the patch")
        elif not self.isALocalProject(name=projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local projectLocalName")
        elif not package in self.getListPackageFromLocalProject(name=projectLocalName,
                                                                local=1):
            raise ObsLightProjectsError(package + " is not a local package")
        
        self.__myObsLightProjects.makePatch(projectLocalName=projectLocalName,
                                            package=package,
                                            patch=patch)
        self.__myObsLightProjects.save()

        
    def addAndCommitChange(self, projectLocalName=None,
                                package=None,
                                message=None):
        '''
        Add/Remove file in the local directory of a package, and commit change to the OBS.
        '''
        if projectLocalName == None:
            raise ObsLightProjectsError(" no name for the projectLocalName")
        elif package == None:
            raise ObsLightProjectsError(" no name for the package")
        elif message == None:
            raise ObsLightProjectsError(" no message for the commit")
        elif not self.isALocalProject(name=projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local projectLocalName")
        elif not package in self.getListPackageFromLocalProject(name=projectLocalName,
                                                                local=1):
            raise ObsLightProjectsError(package + " is not a local package")
        
        self.__myObsLightProjects.addRemoveFileToTheProject(name=projectLocalName,
                                                            package=package)
        self.__myObsLightProjects.commitToObs(name=projectLocalName,
                                              message=message,
                                              package=package)

        self.__myObsLightProjects.save()
        
    def addRepos(self, projectLocalName=None,
                        fromProject=None,
                        repos=None,
                        alias=None):
        '''
        
        '''
        print "projectLocalName", projectLocalName, "fromProject", fromProject, "repos", repos  , "alias", alias
        if projectLocalName == None:
            raise ObsLightProjectsError(" no name for the projectLocalName")
        elif (fromProject == None)and((repos == None)and(alias == None)):
            raise ObsLightProjectsError("wrong value for fromProject or (repos, alias)")
        elif (fromProject != None) and (not self.isALocalProject(name=projectLocalName)):
            raise ObsLightProjectsError(fromProject + " is not a local projectLocalName")          
                                
        self.__myObsLightProjects.addRepos(projectLocalName=projectLocalName,
                                           fromProject=fromProject,
                                           repos=repos,
                                           alias=alias)
        
        self.__myObsLightProjects.save()
        
        
myObsLightManager = ObsLightManager()

def getManager():
    '''

    '''
    return myObsLightManager
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        