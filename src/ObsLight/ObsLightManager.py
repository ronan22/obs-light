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
@author: Florent Vennetier
'''

import os, urllib2

from ObsLightErr import ObsLightObsServers
from ObsLightErr import ObsLightProjectsError
from ObsServers import ObsServers
from ObsLightProjects import ObsLightProjects


def isNonEmptyString(theString):
    return isinstance(theString, basestring) and len(theString) > 0

class ObsLightManager(object):
    '''
    Application Programming Interface between clients (command line, GUI) and OBS Light.
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

        self.__myObsServers = ObsServers(workingDirectory=self.__workingDirectory)
        self.__myObsLightProjects = ObsLightProjects(obsServers=self.__myObsServers, workingDirectory=self.__workingDirectory)


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
        '''
        Get the value of a project parameter:
        the valide info is :
            projectLocalName
            projectObsName
            projectDirectory
            obsServer
            projectTarget
            projectArchitecture
            projectTitle
            description
        '''
        if not self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local project")
        if not parameter in ["projectLocalName",
                             "projectObsName",
                             "projectDirectory",
                             "obsServer",
                             "projectTarget",
                             "projectArchitecture",
                             "projectTitle",
                             "description"]:
            raise ObsLightProjectsError(parameter + " is not a parameter of a local project ")

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
        elif not isNonEmptyString(package):
            raise ObsLightObsServers(" invalid package name: " + str(package))
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
        if not isNonEmptyString(serverApi):
            raise ObsLightObsServers("Can't create a OBSServer: invalid API:" + str(serverApi))
        elif self.isAnObsServer(serverApi):
            raise ObsLightObsServers(serverApi + " is already an OBS server")
        elif self.isAnObsServer(alias):
            raise ObsLightObsServers(alias + " is already an OBS alias")
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
            raise ObsLightObsServers("'" + projectLocalName + "' is not an OBS project")

        return self.__myObsServers.getListPackage(obsServer=obsServer,
                                                  projectLocalName=projectLocalName)

    def getObsServerProjectList(self, server):
        '''
        Get the list of projects of an OBS server.
        '''
        if not isNonEmptyString(server):
            raise ObsLightObsServers(" invalid server name specified: " + str(server))
        elif not self.isAnObsServer(server):
            raise ObsLightObsServers(server + " is not the obs server")

        return self.__myObsServers.getLocalProjectList(server)


    def checkoutPackage(self, obsServer, projectObsName, package, directory):
        '''
        Check out a package from an OBS server to a local directory.
        '''
        if isNonEmptyString(obsServer):
            raise ObsLightObsServers(" invalid OBS server: " + str(obsServer))
        elif isNonEmptyString(projectObsName):
            raise ObsLightObsServers(" invalid projectObsName: " + str(projectObsName))
        elif isNonEmptyString(package):
            raise ObsLightObsServers(" invalid package name: " + str(package))
        elif isNonEmptyString(directory):
            raise ObsLightProjectsError(" invalid directory: " + str(directory))
        elif not self.isAnObsServer(obsServer):
            raise ObsLightObsServers(obsServer + " is not an OBS server")
        elif not projectObsName in self.getObsServerProjectList(obsServer):
            raise ObsLightObsServers(" unknown project: " + projectObsName)
        elif not package in self.getObsProjectPackageList(obsServer, projectObsName):
            raise ObsLightObsServers(" package '" + package + "' is not part of the '"
                                     + projectObsName + "' project")
        elif not os.path.isdir(directory):
            raise ObsLightProjectsError(directory + " is not a directory")

        self.__myObsServers.checkoutPackage(obsServer=obsServer,
                                            projectObsName=projectObsName,
                                            package=package,
                                            directory=directory)
        self.__myObsLightProjects.save()

    #def getPackageStatus(self, obsServer, project, package, target, arch):
    def getPackageStatus(self, project, package):
        '''
        Return the status of package on the OBS server.
        '''
        if not isNonEmptyString(project):
            raise ObsLightObsServers(" invalid project: " + str(project))
        elif not isNonEmptyString(package):
            raise ObsLightObsServers(" invalid package: " + str(package))

        #try:

        return self.__myObsLightProjects.getPackageStatus(project=project,
                                                    package=package)
        #except urllib2.URLError:
        #    return "unknown (connection problem)"

    def getPackageDirectory(self, projectLocalName, packageName):
        '''
        Return the directory where the package files live.
        '''
        if not isNonEmptyString(projectLocalName):
            raise ObsLightObsServers(" invalid project name provided")
        if not isNonEmptyString(packageName):
            raise ObsLightObsServers(" invalid package: " + str(packageName))
        if not self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local project")
        return self.__myObsLightProjects.getPackageDirectory(projectLocalName, packageName)

    def getPackageDirectoryInChRoot(self, projectLocalName, packageName):
        '''
        Return the directory in the chroot where the uncompressed package files live.
        '''
        if not isNonEmptyString(projectLocalName):
            raise ObsLightObsServers(" invalid project name provided")
        if not isNonEmptyString(packageName):
            raise ObsLightObsServers(" invalid package: " + str(packageName))
        if not self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local project")
        if not self.isChRootInit(projectLocalName):
            raise ObsLightProjectsError("The project '" + projectLocalName
                                        + "' has not chroot at the moment")
        return self.__myObsLightProjects.getPackageDirectoryInChRoot(projectLocalName, packageName)

    def addPackage(self, projectLocalName, package):
        '''
        Add a package to a local project. The package must exist on the
        OBS server.
        '''
        if not isNonEmptyString(projectLocalName):
            raise ObsLightProjectsError(" invalid projectLocalName: " + str(projectLocalName))
        elif not isNonEmptyString(package):
            raise ObsLightProjectsError(" invalid package name: " + str(package))
        elif not self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local project")
        server = self.__myObsLightProjects.getObsServer(projectLocalName)
        projectObsName = self.__myObsLightProjects.getProjectObsName(projectLocalName)
        if not package in self.getObsProjectPackageList(server, projectObsName):
            raise ObsLightObsServers(" package '" + package + "' is not part of the '"
                                     + projectObsName + "' project")

        self.__myObsLightProjects.addPackage(projectLocalName, package)
        self.__myObsLightProjects.save()

    def createChRoot(self, projectLocalName):
        '''
        Create a chroot for the project. You need a least one package.
        '''
        if not isNonEmptyString(projectLocalName):
            raise ObsLightProjectsError(" invalid project name: " + str(projectLocalName))
        elif not self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local project")
        elif len(self.getLocalProjectPackageList(projectLocalName, local=1)) == 0:
            raise ObsLightProjectsError("No package in " + projectLocalName + ". At least one"
                                        + " package is needed to build the chroot.")

        self.__myObsLightProjects.createChRoot(projectLocalName=projectLocalName)
        self.__myObsLightProjects.save()

    def getRepo(self, obsServer):
        '''
        Return the URL of the OBS server package repository.
        '''
        if not isNonEmptyString(obsServer):
            raise ObsLightObsServers(" invalid OBS server name: " + str(obsServer))
        elif not self.isAnObsServer(obsServer):
            raise ObsLightObsServers(obsServer + " is not an OBS server")
        return self.__myObsServers.getRepo(obsServer=obsServer)


    def goToChRoot(self, projectLocalName, package=None, detach=False):
        '''
        offer a bash in the chroot for the user
        if package  define, the pwd will be ~/rpmbuild/BUILD/[package]
        '''

        if not isNonEmptyString(projectLocalName):
            raise ObsLightProjectsError(" invalid project name: " + str(projectLocalName))
        elif not self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local project")
        elif ((package != None)
              and (not package in self.getLocalProjectPackageList(projectLocalName, local=1))):
            raise ObsLightProjectsError(" package '" + package + "' is not part of the '"
                                        + projectLocalName + "' project")

        self.__myObsLightProjects.goToChRoot(projectLocalName, package, detach)

    def getChRootPath(self, projectLocalName):
        '''
        Return the path of aChRoot of a project
        '''

        if not isNonEmptyString(projectLocalName):
            raise ObsLightProjectsError(" invalid project name: " + str(projectLocalName))
        elif not self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local project")

        return self.__myObsLightProjects.getChRootPath(projectLocalName)

    def isChRootInit(self, projectLocalName):
        '''
        Return True if the ChRoot is init otherwise False.
        '''
        if not isNonEmptyString(projectLocalName):
            raise ObsLightProjectsError(" invalid project name: " + str(projectLocalName))
        elif not self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local project")


        return self.__myObsLightProjects.isChRootInit(projectLocalName=projectLocalName)

    def isInstalledInChRoot(self, projectLocalName, package):
        '''
        Return True if the package is installed into the chroot of the project.
        '''

        if not isNonEmptyString(projectLocalName):
            raise ObsLightProjectsError(" invalid project name: " + str(projectLocalName))
        elif not self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local project")
        elif not isNonEmptyString(package):
            raise ObsLightProjectsError(" invalid package name: " + str(package))
        elif not package in self.getLocalProjectPackageList(projectLocalName, local=1):
            raise ObsLightProjectsError(package + " is not a local package")


        return self.__myObsLightProjects.isInstallInChroot(projectLocalName=projectLocalName,
                                                           package=package)

    def addPackageSourceInChRoot(self, projectLocalName, package):
        '''
        Add a source RPM from the OBS repository into the chroot.
        '''
        if not isNonEmptyString(projectLocalName):
            raise ObsLightProjectsError(" invalid project name: " + str(projectLocalName))
        elif not isNonEmptyString(package):
            raise ObsLightProjectsError(" invalid package name: " + str(package))
        elif not self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local project")
        # TODO: test if package can be installed

        self.__myObsLightProjects.addPackageSourceInChRoot(projectLocalName=projectLocalName,
                                                           package=package)
        self.__myObsLightProjects.save()

    def makePatch(self, projectLocalName, package, patch):
        '''
        Generate patch, and add it to the local OBS package, modify the spec file.
        '''
        if not isNonEmptyString(projectLocalName):
            raise ObsLightProjectsError(" invalid project name: " + str(projectLocalName))
        elif not isNonEmptyString(package):
            raise ObsLightProjectsError(" invalid package name: " + str(package))
        elif not isNonEmptyString(patch):
            raise ObsLightProjectsError(" invalid patch name: " + str(patch))
        elif not self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local project")
        elif not package in self.getLocalProjectPackageList(projectLocalName, local=1):
            raise ObsLightProjectsError(package + " is not a local package")

        self.__myObsLightProjects.makePatch(projectLocalName, package, patch)
        self.__myObsLightProjects.save()


    def addAndCommitChanges(self, projectLocalName, package, message):
        '''
        Add/Remove file in the local directory of a package, and commit change to the OBS.
        '''
        if not isNonEmptyString(projectLocalName):
            raise ObsLightProjectsError(" invalid project name: " + str(projectLocalName))
        elif not isNonEmptyString(package):
            raise ObsLightProjectsError(" invalid package name: " + str(package))
        elif isNonEmptyString(message):
            raise ObsLightProjectsError(" no commit message")
        elif not self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local project")
        elif not package in self.getLocalProjectPackageList(projectLocalName, local=1):
            raise ObsLightProjectsError(package + " is not a local package")

        self.__myObsLightProjects.addRemoveFileToTheProject(projectLocalName, package)
        self.__myObsLightProjects.commitToObs(name=projectLocalName,
                                              message=message,
                                              package=package)

        self.__myObsLightProjects.save()

    def addRepo(self, projectLocalName, fromProject=None, repoUrl=None, alias=None):
        '''
        Add a repository in the chroot's zypper configuration file.
        You can add the repository of another project or use a specific
        url.
        '''
        if not isNonEmptyString(projectLocalName):
            raise ObsLightProjectsError(" invalid project name: " + str(projectLocalName))
        elif (fromProject == None) and ((repoUrl == None) or (alias == None)):
            raise ObsLightProjectsError("wrong value for fromProject or (repoUrl, alias)")
        elif (fromProject != None) and (not self.isALocalProject(fromProject)):
            raise ObsLightProjectsError(fromProject + " is not a local project")
        elif not self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local project")

        self.__myObsLightProjects.addRepo(projectLocalName=projectLocalName,
                                           fromProject=fromProject,
                                           repos=repoUrl,
                                           alias=alias)

        self.__myObsLightProjects.save()

    def importProject(self, path):
        '''
        Import a project from a file.
        '''
        if not os.path.isfile(path):
            raise ObsLightProjectsError(path + "is not a file, can't import project")
        self.__myObsLightProjects.importProject(path)
        self.__myObsLightProjects.save()

    def exportProject(self, projectLocalName, path=None):
        '''
        Export a project to a file.
        '''
        if not isNonEmptyString(projectLocalName):
            raise ObsLightProjectsError(" invalid project name: " + str(projectLocalName))
        elif not self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local projectLocalName")

        self.__myObsLightProjects.exportProject(projectLocalName, path=path)

    def getProjectWebPage(self, projectLocalName):
        '''
        Get the project webpage URL.
        '''
        if not isNonEmptyString(projectLocalName):
            raise ObsLightProjectsError(" invalid project name: " + str(projectLocalName))
        elif not self.isALocalProject(projectLocalName):
            raise ObsLightProjectsError(projectLocalName + " is not a local project")

        return self.__myObsLightProjects.getWebProjectPage(projectLocalName)

__myObsLightManager = None

def getManager():
    '''
    Get a reference to the ObsLightManager singleton.
    '''
    global __myObsLightManager
    if __myObsLightManager == None:
        __myObsLightManager = ObsLightManager()

    return __myObsLightManager




