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

@author: Ronan Le Martret
'''

import os

from ObsLightErr import ObsLightObsServers
from ObsLightErr import ObsLightProjectsError
from ObsServers import ObsServers
from ObsLightProjects import ObsLightProjects


def isNonEmptyString(theString):
    return isinstance(theString, basestring) and len(theString) < 1

class ObsLightManager(object):
    '''
    Main interface between clients (command line, GUI) and OBS Light.
    All interactions should be done with this class, no other class should
    be imported in external projects.
    '''

    def __init__(self):
        '''
        Initialize the OBS Light Manager.
        '''

        self.__workingDirectory = os.path.join(os.environ['HOME'], "OBSLight")
        # If not exists, create the obsLight directory for the user.
        if not os.path.isdir(self.__workingDirectory):
            os.makedirs(self.__workingDirectory)

        self.__myObsServers = ObsServers(self)
        self.__myObsLightProjects = ObsLightProjects(self)


    def getObsLightWorkingDirectory(self):
        '''
        Returns the OBS Light working directory, usually /home/<user>/OBSLight.
        '''
        return self.__workingDirectory

    def getObsServerList(self):
        '''
        Returns the list of available OBS servers.
        '''
        return self.__myObsServers.getObsServerList()

    def getObsServerParameter(self, obsServerAlias, parameter):
        # TODO: check valid parameters
        '''
        Get the value of an OBS server parameter.
        Valid parameters are:
            obssOBSConnected
            serverWeb
            serverAPI
            serverRepos
            aliases
            user
            passw
        '''

        if not self.isAnObsServer(obsServerAlias):
            raise ObsLightObsServers(obsServerAlias + " is not an OBS server")
        return self.__myObsServers.getObsServerParameter(obsServerAlias=obsServerAlias,
                                                         parameter=parameter)

    def setObsServerParameter(self, obsServerAlias, parameter, value):
        # TODO: check valid parameters
        '''
        Change the value of an OBS server parameter.
        Valid parameters are:
            obssOBSConnected
            serverWeb
            serverAPI
            serverRepos
            aliases
            user
            passw
        '''

        if not self.isAnObsServer(obsServerAlias):
            raise ObsLightObsServers(obsServerAlias + " is not an OBS server")

        res = self.__myObsServers.setObsServerParameter(obsServer=obsServerAlias,
                                                        parameter=parameter,
                                                        value=value)
        self.__myObsServers.save()
        return res
    
    def getProjectParameter(self, projectLocalName, parameter):
        # TODO: check valid parameters
        '''
        Get the value of a project parameter.
        '''
        if not self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local project")
        return self.__myObsLightProjects.getProjectInfo(projectLocalName, parameter)

    def setProjectParameter(self, projectLocalName, parameter, value):
        # TODO: check valid parameters
        '''
        Get the value of a project parameter.
        '''
        if not self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local project")

        res = self.__myObsLightProjects.setProjectparameter(projectLocalName,
                                                            parameter, value)
        self.__myObsLightProjects.save()
        return res

    def removeProject(self, projectLocalName):
        '''
        Remove a local Project.
        '''
        if not self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local project")

        res = self.__myObsLightProjects.removeProject(projectLocalName=projectLocalName)

        self.__myObsLightProjects.save()
        return res

    def removePackage(self, projectLocalName, package):
        '''
        Remove a package from a local project.
        '''
        if not self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local project")
        elif package == None:
            raise ObsLightObsServers(" no name for the package of the obs server")
        elif not package in self.getLocalProjectPackageList(name=projectLocalName, local=1):
            raise ObsLightObsServers(package + " is not a local package of " + projectLocalName)

        res = self.__myObsLightProjects.removePackage(projectLocalName, package)

        self.__myObsLightProjects.save()
        return res

    def addObsServer(self, serverApi, user, password,
                     alias=None, serverRepo="", serverWeb=""):
        '''
        Add a new OBS server.
        '''
        if self.isAnObsServer(serverApi):
            raise ObsLightObsServers(serverApi + " is already an OBS server")
        elif self.isAnObsServer(alias):
            raise ObsLightObsServers(alias + " is already an OBS alias")
        elif serverApi == None:
            raise ObsLightObsServers("Can't create a OBSServer: no API")
        elif user == None:
            raise ObsLightObsServers("Can't create a OBSServer: no user")
        elif password == None:
            raise ObsLightObsServers("Can't create a OBSServer: no password")

        self.__myObsServers.addObsServer(serverWeb=serverWeb,
                                         serverAPI=serverApi,
                                         serverRepo=serverRepo,
                                         alias=alias,
                                         user=user,
                                         passw=password)
        self.__myObsServers.save()

    # TODO: RLM remove this function ?
    def getObsServer(self, name=None):
        '''
        
        '''
        return self.__myObsServers.getObsServer(name=name)


    def isAnObsServer(self, name):
        '''
        Test if name is already an OBS server name.    
        '''
        if name in self.getObsServerList():
            return True
        else:
            return False

    def addProject(self, obsServer, projectObsName, projectTarget,
                   projectArchitecture, projectTitle=None,
                   projectDirectory=None, chrootDirectory=None,
                   description=None, projectLocalName=None):
        '''
        Create a local project associated with an OBS project.
        '''

        if projectLocalName == None:
            projectLocalName = projectObsName.replace(":", "_")

        if projectDirectory == None:
            projectDirectory = os.path.join(self.__workingDirectory,
                                            projectLocalName)

        if ":" in projectLocalName:
            raise ObsLightProjectsError("You can't use ':' in projectLocalName " + projectLocalName)
        if projectObsName == None:
            raise ObsLightObsServers(" no projectObsName specified")
        elif obsServer == None:
            raise ObsLightObsServers(" no OBS server specified")
        elif projectTarget == None:
            raise ObsLightObsServers(" no projectTarget specified")
        elif projectArchitecture == None:
            raise ObsLightObsServers(" no projectArchitecture specified")
        elif self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is already a local project")
        elif ((projectObsName != None)
              and (not projectObsName in self.getObsServerProjectList(obsServer))):
            raise ObsLightObsServers(projectObsName + " is not a project in the OBS server")
        elif not self.isAnObsServer(obsServer):
            raise ObsLightProjectsError(obsServer + " is not an OBS server")
        elif not projectTarget in self.getTargetList(obsServer, projectObsName):
            raise ObsLightProjectsError(projectTarget + " is not a valid target")
        elif not projectArchitecture in self.getArchitectureList(obsServer=obsServer ,
                                                                 projectObsName=projectObsName,
                                                                 projectTarget=projectTarget):
            raise ObsLightProjectsError(projectArchitecture + " is not a valid architecture")

        self.__myObsLightProjects.addProject(projectLocalName=projectLocalName,
                                             projectObsName=projectObsName,
                                             projectTitle=projectTitle,
                                             projectDirectory=projectDirectory,
                                             chrootDirectory=chrootDirectory,
                                             obsServer=obsServer ,
                                             projectTarget=projectTarget,
                                             description=description,
                                             projectArchitecture=projectArchitecture)
        self.__myObsLightProjects.save()


    def getTargetList(self, obsServer, projectObsName):
        '''
        Return the list of targets of the specified project.
        This method is blocking so you may want to call it from a
        separate thread.
        '''
        if obsServer == None:
            raise ObsLightObsServers(" no obsServer specified")
        elif projectObsName == None:
            raise ObsLightObsServers(" no projectObsName specified")
        elif not self.isAnObsServer(obsServer):
            raise ObsLightProjectsError(obsServer + " is not an OBS server")
        elif not projectObsName in self.getObsServerProjectList(obsServer):
            raise ObsLightObsServers(projectObsName + " is not a valid projectObsName")

        return self.__myObsServers.getTargetList(obsServer=obsServer,
                                                 projectObsName=projectObsName)

    def getArchitectureList(self, obsServer, projectObsName, projectTarget):
        '''
        Return the list of architectures configured on this target
        for the specified project.
        This method is blocking so you may want to call it from a
        separate thread.
        '''
        if obsServer == None:
            raise ObsLightObsServers(" no obsServer specified")
        elif projectObsName == None:
            raise ObsLightObsServers(" no projectObsName specified")
        elif projectTarget == None:
            raise ObsLightObsServers(" no projectTarget specified")
        elif not self.isAnObsServer(obsServer):
            raise ObsLightProjectsError(obsServer + " is not an OBS server")

        return self.__myObsServers.getArchitectureList(obsServer=obsServer ,
                                                       projectObsName=projectObsName,
                                                       projectTarget=projectTarget)


    def isALocalProject(self, name):
        '''
        Test if name is already an OBS Project name.    
        '''
        if name in self.getLocalProjectList():
            return True
        else:
            return False

    def getLocalProjectList(self):
        '''
        Return the list of all local projects.
        '''
        return self.__myObsLightProjects.getLocalProjectList()


    def getLocalProjectPackageList(self, name, local=0):
        '''
        Return the list of packages of a local project.
        If local=1, return the list of locally installed packages.
        If local=0, return the list of packages provided by the OBS server for the project.
        '''
        if not isNonEmptyString(name):
            raise ObsLightProjectsError("Invalid project name specified")
        elif not self.isALocalProject(name):
            raise ObsLightProjectsError(name + " is not a local project")

        return self.__myObsLightProjects.getListPackage(name=name, local=local)


    def getObsProjectPackageList(self, obsServer, projectLocalName):
        '''
        Return the list of packages of a project on an OBS server.
        '''
        if not isNonEmptyString(obsServer):
            raise ObsLightObsServers(" invalid server name provided")
        elif not isNonEmptyString(projectLocalName):
            raise ObsLightObsServers(" invalid project name provided")
        elif not projectLocalName in self.getObsServerProjectList(obsServer):
            raise ObsLightObsServers(projectLocalName + " is not an OBS projectLocalName")

        return self.__myObsServers.getListPackage(obsServer=obsServer,
                                                  projectLocalName=projectLocalName)


    def getObsServerProjectList(self, server):
        '''
        Get the list of projects of an OBS server.
        '''
        if not isNonEmptyString(server):
            raise ObsLightObsServers(" invalid server name specified: " + server)
        elif not self.isAnObsServer(server):
            raise ObsLightObsServers(server + " is not the obs server")

        return self.__myObsServers.getLocalProjectList(server=server)

    def checkoutPackage(self, obsServer=None,
                                projectObsName=None,
                                package=None,
                                directory=None):
        '''
        Check out a package from an OBS server to a local directory.
        '''
        if obsServer == None:
            raise ObsLightObsServers(" no name for the obs server")
        elif projectObsName == None:
            raise ObsLightObsServers(" no name for the projectObsName of the obs server")
        elif package == None:
            raise ObsLightObsServers(" no name for the package of the obs server")
        elif directory == None:
            raise ObsLightProjectsError(" no name for the directory")
        elif not self.isAnObsServer(name=obsServer):
            raise ObsLightObsServers(obsServer + " is not the obs server")
        elif not projectObsName in self.getObsServerProjectList(server=obsServer):
            raise ObsLightObsServers(" no name for the package of the obs server")
        elif not package in self.getObsProjectPackageList(obsServer=obsServer,
                                                              projectObsName=projectObsName):
            raise ObsLightObsServers(" no name for the directory")
        elif not os.path.isdir(directory):
            raise ObsLightProjectsError(directory + " is not a directory")

        self.__myObsServers.checkoutPackage(obsServer=obsServer,
                                            projectObsName=projectObsName,
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
        elif not self.isAnObsServer(name=obsServer):
            raise ObsLightObsServers(obsServer + " is not the obs server")
        elif not project in self.getObsServerProjectList(server=obsServer):
            raise ObsLightObsServers(" no name for the project of the obs server")
        elif not package in self.getObsProjectPackageList(obsServer=obsServer,
                                                              projectLocalName=project):
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
        elif not projectLocalName in self.getLocalProjectList():
            raise ObsLightObsServers(projectLocalName + " not present in the projectLocalName of the obs server")
        elif not package in self.getObsProjectPackageList(obsServer=self.__myObsLightProjects.getObsServer(name=projectLocalName),
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
        elif len(self.getLocalProjectPackageList(name=projectLocalName, local=1)) == 0:
            raise ObsLightProjectsError("no package in " + projectLocalName)

        self.__myObsLightProjects.createChRoot(projectLocalName=projectLocalName)
        self.__myObsLightProjects.save()

    def getRepo(self, obsServer=None):
        '''
        return the name of the repos of the OBS server
        '''
        if obsServer == None:
            raise ObsLightObsServers(" no name for the obs server")
        elif not self.isAnObsServer(name=obsServer):
            raise ObsLightObsServers(obsServer + " is not the obs server")
        return self.__myObsServers.getRepo(obsServer=obsServer)


    def goToChRoot(self, projectLocalName=None, package=None):
        '''
        offer a bash in the chroot for the user
        if package  define, the pwd will be ~/rpmbuild/BUILD/[package]
        '''

        if projectLocalName == None:
            raise ObsLightProjectsError(" no name for the projectLocalName")
        elif not self.isALocalProject(name=projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local projectLocalName")
        elif (package != None) and (not package in self.getLocalProjectPackageList(name=projectLocalName,
                                                                                       local=1)):
            raise ObsLightProjectsError(package + " not in projectLocalName")

        self.__myObsLightProjects.goToChRoot(projectLocalName=projectLocalName,
                                             package=package)

    def addPackageSourceInChRoot(self, projectLocalName=None, package=None):
        '''
        Add a source RPM from the OBS repository into the chroot
        '''
        if projectLocalName == None:
            raise ObsLightProjectsError(" projectLocalName not specified")
        elif package == None:
            raise ObsLightProjectsError(" package name not specified")
        elif not self.isALocalProject(name=projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local project")
        #TODO test if package can be installed

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
        elif not package in self.getLocalProjectPackageList(name=projectLocalName,
                                                                local=1):
            raise ObsLightProjectsError(package + " is not a local package")

        self.__myObsLightProjects.makePatch(projectLocalName=projectLocalName,
                                            package=package,
                                            patch=patch)
        self.__myObsLightProjects.save()


    def addAndCommitChanges(self, projectLocalName=None,
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
        elif not package in self.getLocalProjectPackageList(name=projectLocalName,
                                                                local=1):
            raise ObsLightProjectsError(package + " is not a local package")

        self.__myObsLightProjects.addRemoveFileToTheProject(name=projectLocalName,
                                                            package=package)
        self.__myObsLightProjects.commitToObs(name=projectLocalName,
                                              message=message,
                                              package=package)

        self.__myObsLightProjects.save()

    def addRepo(self, projectLocalName=None,
                        fromProject=None,
                        repos=None,
                        alias=None):
        '''
        
        '''
        if projectLocalName == None:
            raise ObsLightProjectsError(" no name for the projectLocalName")
        elif (fromProject == None) and ((repos == None) or (alias == None)):
            raise ObsLightProjectsError("wrong value for fromProject or (repos, alias)")
        elif (fromProject != None) and (not self.isALocalProject(name=fromProject)):
            raise ObsLightProjectsError(fromProject + " is not a local projectLocalName")
        elif not self.isALocalProject(name=projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local projectLocalName")

        self.__myObsLightProjects.addRepo(projectLocalName=projectLocalName,
                                           fromProject=fromProject,
                                           repos=repos,
                                           alias=alias)

        self.__myObsLightProjects.save()

    def importProject(self,path=None):
        '''
        
        '''
        if not os.path.isfile(path):
            raise ObsLightProjectsError(path+"is not a file, can't importProject")
        self.__myObsLightProjects.importProject(path=path)
        self.__myObsLightProjects.save()
    
    def exportProject(self,projectLocalName=None,path=None):
        '''
        
        '''
        if projectLocalName == None:
            raise ObsLightProjectsError(" no name for the projectLocalName")
        elif not self.isALocalProject(name=projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local projectLocalName")
        
        self.__myObsLightProjects.exportProject(projectLocalName=projectLocalName,path=path)
    

    
        
__myObsLightManager = ObsLightManager()

def getManager():
    '''

    '''
    return __myObsLightManager




















