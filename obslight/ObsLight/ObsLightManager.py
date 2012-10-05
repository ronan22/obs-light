#
# Copyright 2011-2012, Intel Inc.
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
'''
Created on 17 juin 2011

@author: Ronan Le Martret
@author: Florent Vennetier
'''

import os
import collections
import time

from ObsLightServers import ObsLightServers
from ObsLightProjects import ObsLightProjects
from ObsLightMicProjects import ObsLightMicProjects
from ObsLightLocalServer import ObsLightLocalServer
from ObsLightRepositories import  ObsLightRepositories

from ObsLightUtils import isNonEmptyString
from ObsLightUtils import isBool

import ObsLightConfig
import ObsLightTools
import ObsLightPrintManager

from ObsLightErr import ObsLightObsServers
from ObsLightErr import ObsLightProjectsError
from ObsLightErr import ArgError

from ObsLightSubprocess import SubprocessCrt
VERSION = "0.9.0-1"

def getVersion():
    '''
    
    '''
    return VERSION

def getConfigPath():
    '''
    Return the path of the config file.
    '''
    return ObsLightConfig.CONFIGPATH

def getWorkingDirectory():
    return ObsLightConfig.WORKINGDIRECTORY

def getProjectManifestDirectory():
    path = os.path.join(getWorkingDirectory() , "projectManifest")
    if not os.path.isdir(path):
        os.makedirs(path)
    return path

def getpidFilePath():
    return os.path.join(getWorkingDirectory(), u"obslight.pid")

##Decorator 
def checkProjectLocalName(position=None):
    def checkProjectLocalName1(f):
        def checkProjectLocalName2(*args, **kwargs):
            mngr = getManager()
            projectLocalName = None
            if (position is not None) and (position < len(args)):
                projectLocalName = args[position]
            elif "projectLocalName" in kwargs :
                projectLocalName = kwargs["projectLocalName"]
            else:
                raise ObsLightProjectsError("checkProjectLocalName Fails")


            if not isNonEmptyString(projectLocalName):
                raise ObsLightObsServers("Invalid project name: '" + str(projectLocalName) + "'")
            elif not mngr.isALocalProject(projectLocalName):
                raise ObsLightProjectsError("'%s' is not a local project"
                                            % str(projectLocalName))
            return f(*args, **kwargs)
        return checkProjectLocalName2
    return checkProjectLocalName1

def checkAvailableProjectLocalName(position=None):
    def checkAvailableProjectLocalName1(f):
        def checkAvailableProjectLocalName2(*args, **kwargs):
            mngr = getManager()
            val = None
            if (position is not None) and (position < len(args)):
                val = args[position]
            elif "projectLocalName" in kwargs :
                val = kwargs["projectLocalName"]
            else:
                raise ObsLightProjectsError("checkProjectLocalName Fails")
            if mngr.isALocalProject(val):
                raise ObsLightProjectsError("'" + str(val) + "' is already a local project")
            return f(*args, **kwargs)
        return checkAvailableProjectLocalName2
    return checkAvailableProjectLocalName1

def checkFilePath(position=None):
    def checkFilePath1(f):
        def checkFilePath2(*args, **kwargs):
            filePath = None
            if (position is not None) and (position < len(args)):
                filePath = args[position]
            elif "filePath" in kwargs :
                filePath = kwargs["filePath"]
            else:
                raise ObsLightProjectsError("checkFilePath Fails")
            if not isNonEmptyString(filePath):
                raise ArgError(u"openFile: invalid path: '%s'" % filePath)
            elif not os.path.isfile(filePath):
                raise ObsLightProjectsError(filePath + "is not a file.")
            return f(*args, **kwargs)
        return checkFilePath2
    return checkFilePath1

def checkNonEmptyStringDirectory(position=None):
    def checkNonEmptyStringDirectory1(f):
        def checkNonEmptyStringDirectory2(*args, **kwargs):
            directory = None
            if (position is not None) and (position < len(args)):
                directory = args[position]
            elif "directory" in kwargs :
                directory = kwargs["directory"]
            else:
                raise ObsLightProjectsError("checkNonEmptyStringDirectory Fails")
            if not isNonEmptyString(directory):
                raise ObsLightObsServers("Invalid Directory name: " + str(directory))
            return f(*args, **kwargs)
        return checkNonEmptyStringDirectory2
    return checkNonEmptyStringDirectory1

def checkNonEmptyStringMessage(position=None):
    def checkNonEmptyStringMessage1(f):
        def checkNonEmptyStringMessage2(*args, **kwargs):
            message = None
            if (position is not None) and (position < len(args)):
                message = args[position]
            elif "message" in kwargs :
                message = kwargs["message"]
            else:
                raise ObsLightProjectsError("checkNonEmptyStringMessage Fails")
            if not isNonEmptyString(message):
                raise ObsLightProjectsError("No commit message")
            return f(*args, **kwargs)
        return checkNonEmptyStringMessage2
    return checkNonEmptyStringMessage1

def checkNonEmptyStringPatch(position=None):
    def checkNonEmptyStringPatch1(f):
        def checkNonEmptyStringPatch2(*args, **kwargs):
            patch = None
            if (position is not None) and (position < len(args)):
                patch = args[position]
            elif "patch" in kwargs :
                patch = kwargs["patch"]
            else:
                raise ObsLightProjectsError("checkNonEmptyStringPatch Fails")
            if not isNonEmptyString(patch):
                raise ObsLightProjectsError("Invalid patch name: " + str(patch))
            return f(*args, **kwargs)
        return checkNonEmptyStringPatch2
    return checkNonEmptyStringPatch1

def checkNonEmptyStringProjectTarget(position=None):
    def checkNonEmptyStringProjectTarget1(f):
        def checkNonEmptyStringProjectTarget2(*args, **kwargs):
            projectTarget = None
            if (position is not None) and (position < len(args)):
                projectTarget = args[position]
            elif "projectTarget" in kwargs :
                projectTarget = kwargs["projectTarget"]
            else:
                raise ObsLightProjectsError("checkNonEmptyStringProjectTarget Fails")
            if not isNonEmptyString(projectTarget):
                raise ObsLightObsServers("No projectTarget specified")
            return f(*args, **kwargs)
        return checkNonEmptyStringProjectTarget2
    return checkNonEmptyStringProjectTarget1

def checkNonEmptyStringProjectArchitecture(position=None):
    def checkNonEmptyStringProjectArchitecture1(f):
        def checkNonEmptyStringProjectArchitecture2(*args, **kwargs):
            projectArchitecture = None
            if (position is not None) and (position < len(args)):
                projectArchitecture = args[position]
            elif "projectArchitecture" in kwargs :
                projectArchitecture = kwargs["projectArchitecture"]
            else:
                raise ObsLightProjectsError("checkNonEmptyStringProjectArchitecture Fails")
            if not isNonEmptyString(projectArchitecture):
                raise ObsLightObsServers("No projectArchitecture specified")
            return f(*args, **kwargs)
        return checkNonEmptyStringProjectArchitecture2
    return checkNonEmptyStringProjectArchitecture1

def checkProjectObsName(position1=None, position2=None):
    def checkAvailableProjectObsName1(f):
        def checkAvailableProjectObsName2(*args, **kwargs):
            mngr = getManager()
            projectObsName = None
            serverApi = None
            if (position1 is not None) and (position1 < len(args)):
                projectObsName = args[position1]
            elif "projectObsName" in kwargs :
                projectObsName = kwargs["projectObsName"]
            else:
                raise ObsLightProjectsError("checkProjectObsName Fails no projectObsName")
            if (position2 is not None) and (position2 < len(args)):
                serverApi = args[position2]
            elif "serverApi" in kwargs :
                serverApi = kwargs["serverApi"]
            else:
                raise ObsLightProjectsError("checkProjectObsName Fails no serverApi")
            if not isNonEmptyString(projectObsName):
                raise ObsLightObsServers("No projectObsName")
            if projectObsName in mngr.getObsServerProjectList(serverApi):
                raise ObsLightObsServers("'%s' is not a project in the OBS server"
                                         % projectObsName)
            return f(*args, **kwargs)
        return checkAvailableProjectObsName2
    return checkAvailableProjectObsName1

#def checkAvailableProjectPackage(position1=None, position2=None, position3=None):
#    def checkAvailableProjectPackage1(f):
#        def checkAvailableProjectPackage2(*args, **kwargs):
#            mngr = getManager()
#            projectObsName = None
#            serverApi = None
#            package = None
#            if (position1 is not None) and (position1 < len(args)):
#                projectObsName = args[position1]
#            elif "projectObsName" in kwargs :
#                projectObsName = kwargs["projectObsName"]
#            else:
#                raise ObsLightProjectsError("checkAvailableProjectPackage Fails no serverApi")
#            if (position2 is not None) and (position2 < len(args)):
#                serverApi = args[position2]
#            elif "serverApi" in kwargs :
#                serverApi = kwargs["serverApi"]
#            else:
#                raise ObsLightProjectsError("checkAvailableProjectPackage Fails no serverApi")
#            if (position3 is not None) and (position3 < len(args)):
#                package = args[position3]
#            elif "package" in kwargs :
#                package = kwargs["package"]
#            else:
#                raise ObsLightProjectsError("checkAvailableProjectPackage Fails no package")
#            if not package in mngr.getObsProjectPackageList(serverApi, projectObsName):
#                raise ObsLightObsServers(" package '" + package + "' is not part of the '"
#                                         + projectObsName + "' project")
#            return f(*args, **kwargs)
#        return checkAvailableProjectPackage2
#    return checkAvailableProjectPackage1

def checkDirectory(position=None):
    def checkDirectory1(f):
        def checkDirectory2(*args, **kwargs):
            directory = None
            if (position is not None) and (position < len(args)):
                directory = args[position]
            elif "directory" in kwargs :
                directory = kwargs["directory"]
            else:
                raise ObsLightProjectsError("checkNonEmptyStringProjectArchitecture Fails")
            if not os.path.isdir(directory):
                raise ObsLightProjectsError(directory + " is not a directory")
            return f(*args, **kwargs)
        return checkDirectory2
    return checkDirectory1

#-------------------------------------------------------------------------------
def checkNonEmptyStringServerApi(serverApi):
    '''
    
    '''
    if not isNonEmptyString(serverApi):
        raise ObsLightObsServers("invalid API:" + str(serverApi))

def checkReachableIsBool(reachable):
    '''
    
    '''
    if not isBool(reachable):
        raise ObsLightObsServers("invalid value for reachable:" + str(reachable))

def checkNonEmptyStringLocalName(projectLocalName):
    if not isNonEmptyString(projectLocalName):
        raise ObsLightObsServers("Invalid projectLocalName name: '" + str(projectLocalName) + "'")
    elif ":" in projectLocalName:
        raise ObsLightProjectsError("':' is forbidden in projectLocalName (%s)"
                                    % str(projectLocalName))

def checkNonEmptyStringPackage(package):
    def test(package):
        if not isNonEmptyString(package):
            raise ObsLightObsServers("Invalid package name: " + str(package))


    if isinstance(package, collections.Iterable) and\
       not isinstance(package, str) and\
       not isinstance(package, unicode) :
        for aVal in package:
            test(aVal)
    else:
        test(package)



#-------------------------------------------------------------------------------

class ObsLightManagerBase(object):

    def __init__(self):
        '''
        Initialize the OBS Light Manager Base.
        '''
        self.__workingDirectory = getWorkingDirectory()

        self._myObsLightMicProjects = ObsLightMicProjects(self.getObsLightWorkingDirectory())

        self._myObsServers = ObsLightServers(self.getObsLightWorkingDirectory())

        self._myObsLightRepositories = ObsLightRepositories(self.getObsLightWorkingDirectory())

        self._myObsLightProjects = ObsLightProjects(self._myObsServers,
                                                    self._myObsLightRepositories,
                                                    self.getObsLightWorkingDirectory())

        self._myObsLightLocalServer = ObsLightLocalServer()

    def getObsLightWorkingDirectory(self):
        '''
        Returns the OBS Light working directory, usually /home/<user>/OBSLight.
        '''
        return self.__workingDirectory

    #---------------------------------------------------------------------------
    def addLoggerHandler(self, handler):
        '''
        Add a Handler object to the logger of obslight.
        '''
        ObsLightPrintManager.addHandler(handler)

    def removeLoggerHandler(self, handler):
        '''
        Remove a Handler object to the logger of obslight.
        '''
        ObsLightPrintManager.removeHandler(handler)

    #---------------------------------------------------------------------------

    def testUrl(self, Url):
        '''
        Return True if Url is reachable, false otherwise.
        '''
        res = ObsLightTools.testUrl(Url)
        return res
    def testHost(self, Url):
        '''
        Return True if the host of the Url is reachable, false otherwise.
        '''
        return ObsLightTools.testHost(Url)

    def testRepo(self, url, name):
        '''
        return url,name
        If url is a repo file (*.repo), the file is download,
        parse and return url and name of the repo directory.
        "%3a" is replace by ":" into the url.
        '''
        return ObsLightTools.testRepo(url=url, name=name)

    def testRepositoryUrl(self, url):
        """
        Return True if `url` is a package repository.
        """
        return ObsLightTools.testRepositoryUrl(url)

    def testUrlRepo(self, url):
        '''
        return True if the url is a repo.
        '''
        return ObsLightTools.testUrlRepo(url=url)

    def getVersion(self):
        '''
        Return the version of obslight
        '''
        return VERSION

    def checkNonEmptyStringUser(self, user):
        if not isNonEmptyString(user):
            raise ObsLightObsServers("Can't create a OBSServer: no user")
        return 0

    def checkNonEmptyStringPassword(self, password):
        if not isNonEmptyString(password):
            raise ObsLightObsServers("Can't create a OBSServer: no password")
        return 0

class ObsLightManagerCore(ObsLightManagerBase):

    def __init__(self):
        '''
        Initialize the OBS Light Manager Core.
        '''
        ObsLightManagerBase.__init__(self)

    #///////////////////////////////////////////////////////////////////////////server
    def testServer(self, obsServer):
        '''
        Return True if obsServer is reachable, false otherwise.
        obsServer may be an OBS server alias or an HTTP(S) URL.
        '''
        return self._myObsServers.testServer(obsServer=obsServer)

    def testApi(self, api, user, passwd):
        '''
        return 0 if the API,user and passwd is OK.
        return 1 if user and passwd  are wrong.
        return 2 if api is wrong.
        '''
        return self._myObsServers.testApi(api=api, user=user, passwd=passwd)

    def getObsServerList(self, reachable=False):
        '''
        Returns the list of available OBS servers.
        if reachable =False :
            return all ObsServer
        else :
            return only the available ObsServer
        '''
        return self._myObsServers.getObsServerList(reachable=reachable)

    def checkObsServerAlias(self, serverApi):
        if not self.isAnObsServer(serverApi):
            raise ObsLightObsServers(serverApi + " is not an OBS server")

    def isAnObsServer(self, name):
        '''
        Test if name is already an OBS server name.    
        '''
        if name in self.getObsServerList():
            return True
        else:
            return False

    def getObsServerParameter(self, obsServerAlias, parameter):
        '''
        Get the value of an OBS server parameter.
        Valid parameters are:
            isOBSConnected
            serverWeb
            serverAPI
            serverRepo
            alias
            user
            passw
        '''
        self.checkObsServerAlias(serverApi=obsServerAlias)
        return self._myObsServers.getObsServer(obsServerAlias).getObsServerParameter(parameter)

    def setObsServerParameter(self, obsServerAlias, parameter, value):
        '''
        Change the value of an OBS server parameter.
        Valid parameters are:
            isOBSConnected
            serverWeb
            serverAPI
            serverRepo
            alias
            user
            passw
        '''
        self.checkObsServerAlias(serverApi=obsServerAlias)
        res = self._myObsServers.getObsServer(obsServerAlias).setObsServerParameter(parameter,
                                                                                    value)
        self._myObsServers.save()
        return res

    def getCurrentObsServer(self):
        '''
        
        '''
        return self._myObsServers.getCurrentServer()

    def checkAvailableAliasOsc(self, serverApi, alias):
        if self._myObsServers.isAnObsServerOscAlias(serverApi, alias):
            raise ObsLightObsServers(alias + " is already an OBS alias define in ~/.oscrc ")
        return 0

    def checkAvailableServerApi(self, serverApi):
        if self.isAnObsServer(serverApi):
            raise ObsLightObsServers(serverApi + " is already an OBS server")
        return 0

    def checkAvailableAlias(self, alias):
        if self.isAnObsServer(alias):
            raise ObsLightObsServers(alias + " is already an OBS server")
        return 0

    def addObsServer(self,
                     serverApi,
                     user,
                     password,
                     alias,
                     serverRepo,
                     serverWeb):
        '''
        Add a new OBS server.
        '''
        checkNonEmptyStringServerApi(serverApi=serverApi)
        self.checkAvailableAlias(alias)
        self.checkAvailableAliasOsc(serverApi, alias)
        self.checkAvailableServerApi(serverApi)
        self.checkNonEmptyStringUser(user)
        self.checkNonEmptyStringPassword(password)
        res = self._myObsServers.addObsServer(serverWeb=serverWeb,
                                             serverAPI=serverApi,
                                             serverRepo=serverRepo,
                                             alias=alias,
                                             user=user,
                                             passw=password)
        self._myObsServers.save()
        return res

    def delObsServer(self, obsServer):
        '''
        Delete an OBS server.
        '''
        checkNonEmptyStringServerApi(serverApi=obsServer)
        self.checkObsServerAlias(serverApi=obsServer)

        self._myObsServers.delObsServer(alias=obsServer)
        self._myObsServers.save()

    #///////////////////////////////////////////////////////////////////////////Local Project
    def getProjectTemplateList(self, local=True):
        if local:
            res = {}
            gbsConfPath = os.path.expanduser("~/.gbs.conf")
            if os.path.isfile(gbsConfPath):
                res["~/.gbs.conf"] = gbsConfPath
            return res
        else:
            res = self.__getProjectFilefList("/usr/share/obslight/projectTemplate")
            return res

    def getProjectConfList(self):
        return self.__getProjectFilefList("/usr/share/obslight/projectConf/")

    def getProjectGbsConfList(self):
        return self.__getProjectFilefList("/usr/share/gbs/")

    def testSshUser(self, cmd):
        aSubProcess = SubprocessCrt()
        res = aSubProcess.execSubprocess(cmd)
        return (res == 127)

    def getProjectManifestList(self):
        return self.__getProjectFilefList(getProjectManifestDirectory())

    def __getProjectFilefList(self, path):
        aDict = {}
        if os.path.isdir(path):
            for  f in os.listdir(path):
                aFilePath = os.path.join(path, f)
                if os.path.isfile(aFilePath) and os.access(aFilePath, os.R_OK):
                    aDict[f] = aFilePath
        return aDict

    def generateUpdatedTizenManifest(self):
        ouputFile = os.path.join(getProjectManifestDirectory(), "tizen-%s.xml")
        ouputFile = ouputFile % (time.strftime("%Y-%m-%d_%Hh%M"))
        cmd = "/usr/bin/generate_default_xml > %s " % ouputFile

        aSubProcess = SubprocessCrt()
        xmlFile = aSubProcess.execSubprocess(cmd, stdout=True)
        with open(ouputFile, 'w') as f:
            f.write(xmlFile)
        return ouputFile

    def getRepoFromGbsProjectConf(self, path):
        return ObsLightTools.getRepoFromGbsProjectConf(path)

    def getBuildConfFromGbsProjectConf(self, selectedProjectRepo, selectedProjectConf):
        return ObsLightTools.getBuildConfFromGbsProjectConf(selectedProjectRepo, selectedProjectConf)

    def getDefaultGbsArch(self):
        return ["i586", "x86_64 ", "armv8el"]

    @checkNonEmptyStringProjectArchitecture(3)
    @checkAvailableProjectLocalName(4)
    def addGbsProject(self, projectConfPath, repoList, arch, alias, autoAddProjectRepo=True):
        checkNonEmptyStringLocalName(alias)
        res = self._myObsLightProjects.addGbsProject(projectConfPath,
                                                     repoList,
                                                     arch,
                                                     alias,
                                                     autoAddProjectRepo)
        self._myObsLightProjects.save()
        return res

    #///////////////////////////////////////////////////////////////////////////obsproject
    @checkNonEmptyStringProjectTarget(3)
    @checkNonEmptyStringProjectArchitecture(4)
    @checkAvailableProjectLocalName(5)
    def addProject(self,
                   serverApi,
                   projectObsName,
                   projectTarget,
                   projectArchitecture,
                   projectLocalName):
        '''
        Create a local project associated with an OBS project.
        '''

        checkNonEmptyStringLocalName(projectLocalName)
        checkNonEmptyStringServerApi(serverApi=serverApi)

        self.checkAvailableProjectObsName(projectObsName=projectObsName, serverApi=serverApi)
        self.checkObsServerAlias(serverApi=serverApi)

        res = self._myObsLightProjects.addOBSProject(projectLocalName=projectLocalName,
                                                     projectObsName=projectObsName,
                                                     obsServer=serverApi,
                                                     projectTarget=projectTarget,
                                                     projectArchitecture=projectArchitecture)
        self._myObsLightProjects.save()
        return res


    def getObsServerProjectList(self,
                                serverApi,
                                maintainer=False,
                                bugowner=False,
                                remoteurl=False,
                                arch=None):
        '''
        Get the list of projects of an OBS server.
        you can also filter the result
        maintainer    False,True
        bugowner      False,True
        remoteurl     False,True
        arch
        '''
        raw = not (maintainer or bugowner or remoteurl)
        checkNonEmptyStringServerApi(serverApi=serverApi)
        self.checkObsServerAlias(serverApi=serverApi)
        server = self._myObsServers.getObsServer(serverApi)
        return server.getLocalProjectList(maintainer=maintainer,
                                          bugowner=bugowner,
                                          remoteurl=remoteurl,
                                          arch=arch,
                                          raw=raw)



    def createObsProject(self, serverApi, projectObsName, title="", description=""):
        checkNonEmptyStringServerApi(serverApi=serverApi)
        self.checkObsServerAlias(serverApi=serverApi)
        server = self._myObsServers.getObsServer(serverApi)
        return server.createObsProject(projectObsName, title, description)

    def checkAvailableProjectObsName(self, projectObsName, serverApi):
        '''
        
        '''
        if not isNonEmptyString(projectObsName):
            raise ObsLightObsServers("No projectObsName")
        if not projectObsName in self.getObsServerProjectList(serverApi):
            raise ObsLightObsServers("'%s' is not a project in the OBS server"
                                     % projectObsName)


        #used by decorator.
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
        return self._myObsLightProjects.getLocalProjectList()

    def getCurrentObsProject(self):
        '''
        
        '''
        return self._myObsLightProjects.getCurrentProject()

    @checkProjectLocalName(1)
    def removeProject(self, projectLocalName):
        '''
        Remove a local Project.
        '''
        res = self._myObsLightProjects.removeProject(projectLocalName=projectLocalName)
        return res

    @checkProjectLocalName(1)
    def getProjectParameter(self, projectLocalName, parameter):
        '''
        Get the value of a project parameter.
        Valid parameter are:
            projectLocalName
            projectObsName
            projectDirectory
            obsServer
            projectTarget
            projectArchitecture
            projectTitle
            description
            isLocalProject
        '''
        if not parameter in ["projectLocalName",
                             "projectObsName",
                             "projectDirectory",
                             "obsServer",
                             "projectTarget",
                             "projectArchitecture",
                             "title",
                             "description",
                             "isLocalProject"]:
            raise ObsLightProjectsError(parameter + " is not a parameter of a local project")

        return self._myObsLightProjects.getProject(projectLocalName).getProjectParameter(parameter)

    def getObsProjectParameter(self, serverApi, obsproject, parameter):
        '''
        Get the value of a project parameter.
        Valid parameter are:
            title
            description
            remoteurl
            maintainer
            bugowner
            repository
            arch
            readonly
        '''

        checkNonEmptyStringServerApi(serverApi=serverApi)
        self.checkObsServerAlias(serverApi=serverApi)
        server = self._myObsServers.getObsServer(serverApi)
        return server.getProjectParameter(obsproject, parameter)

    @checkProjectLocalName(1)
    def getProjectWebPage(self, projectLocalName):
        '''
        Get the project webpage URL.
        '''
        return self._myObsLightProjects.getProject(projectLocalName).getWebProjectPage()

    @checkProjectLocalName(1)
    def getProjectRepository(self, projectLocalName):
        '''
        Return the URL of the repository of the project
        '''
        return self._myObsLightProjects.getProject(projectLocalName).getReposProject()

    @checkProjectLocalName(1)
    def setProjectParameter(self, projectLocalName, parameter, value):
        '''
        Get the value of a project parameter.
        Valid parameters are:
            projectTitle
            description
        '''
        res = self._myObsLightProjects.getProject(projectLocalName).setProjectParameter(parameter,
                                                                                        value)
        self._myObsLightProjects.save()
        return res

#    @checkFilePath(1)
#    def importProject(self, filePath):
#        '''
#        Import a project from a file.
#        '''
#        res = self._myObsLightProjects.importProject(filePath)
#        self._myObsLightProjects.save()
#        return res

#    @checkProjectLocalName(1)
#    def exportProject(self, projectLocalName, path=None):
#        '''
#        Export a project to a file.
#        '''
#        return self._myObsLightProjects.exportProject(projectLocalName, path=path)


    def getDependencyRepositories(self, projectLocalName):
        '''
        Export a project to a file.
        '''
        return self._myObsLightProjects.getProject(projectLocalName).getDependencyRepositories()

    def testBuildPackages(self, projectName, packageNames):
        """
        Call `ObsLightProject.importPrepBuildPackages` for all packages
        of `packageNames`. If `packageNames` is None or an empty list,
        call `importPrepBuildPackage` for all packages of `projectName`.

        Returns the list of packages which failed, as tuples of
        (packageName, exception) or (packageName, errorCode) depending
        on the type of failure.

        This function was developed for testing purposes.
        """

        res = self._myObsLightProjects.importPrepBuildPackages(projectName, packageNames)
        self._myObsLightProjects.save()
        return res

    #///////////////////////////////////////////////////////////////////////////package

    def localCopyPackage(self, projectSrc, projectDst, package):
        print "projectSrc", projectSrc, "projectDst", projectDst, "package", package


    def getLocalProjectPackageList(self, projectLocalName, onlyInstalled=True):
        '''
        Return the list of packages of a local project.
        If onlyInstalled=True, return the list of locally installed packages.
        If onlyInstalled=False, return the list of packages provided by the OBS server for the project.
        '''
        project = self._myObsLightProjects.getProject(projectLocalName)
        return project.getPackageList(onlyInstalled=onlyInstalled)

    @checkProjectLocalName(1)
    def createLocalProjectObsPackage(self, projectLocalName, name, title="", description=""):
        """
        Create an empty package `name` on server in project associated
        with `projectLocalName`, with `title` and `description`.
        Package is not imported automatically,
        you have to call `addPackage(projectLocalName, name)`.
        """
        if name in self.getLocalProjectPackageList(projectLocalName=projectLocalName):
            msg = "'%s' is already a local package of '%s'" % (name, projectLocalName)
            raise ObsLightObsServers(msg)

        project = self._myObsLightProjects.getProject(projectLocalName)
        if self.getProjectParameter(projectLocalName, "isLocalProject"):
            res = project.addPackage(name, project.createPackagePath(name, True))
            self._myObsLightProjects.save()
            return res
        else:
            server = self.getProjectParameter(projectLocalName, "obsServer")
            projectObsName = self.getProjectParameter(projectLocalName, "projectObsName")
            if self.getObsProjectParameter(server, projectObsName, "readonly"):
               res = project.addPackage(name, project.createPackagePath(name, True))
               self._myObsLightProjects.save()
               return res
            else:
                res = self.createObsPackage(server, projectObsName, name, title, description)
                res = self.addPackage(projectLocalName, name)
                self._myObsLightProjects.save()
                return res

    def createObsPackage(self, serverApi, projectObsName, package, title="", description=""):
        checkNonEmptyStringServerApi(serverApi=serverApi)
        self.checkObsServerAlias(serverApi=serverApi)
        server = self._myObsServers.getObsServer(serverApi)
        return server.createObsPackage(projectObsName, package, title, description)


    def checkPackage(self, projectLocalName, package):
        ''' 
        
        '''
        def test(package):
            if not package in self.getLocalProjectPackageList(projectLocalName=projectLocalName):
                msg = "'%s' is not a local package of '%s'" % (package, projectLocalName)
                raise ObsLightObsServers(msg)

        if isinstance(package, collections.Iterable) and\
           not isinstance(package, str) and\
           not isinstance(package, unicode):
            for aVal in package:
                test(aVal)
        else:
            test(package)

    def checkNoPackage(self, projectLocalName, package):
        '''
        
        '''
        def test(package):
            if package in self.getLocalProjectPackageList(projectLocalName=projectLocalName):
                raise ObsLightObsServers("'%s' is already a local package of '%s'"
                                         % (package, projectLocalName))

        if isinstance(package, collections.Iterable) and\
           not isinstance(package, str) and\
           not isinstance(package, unicode):
            for aVal in package:
                test(aVal)
        else:
            test(package)


    @checkProjectLocalName(1)
    def getCurrentPackage(self, projectLocalName):
        '''
        
        '''
        return self._myObsLightProjects.getProject(projectLocalName).getCurrentPackage()

    @checkProjectLocalName(1)
    def importPackage(self,
                      projectLocalName,
                      package,
                      url=None):
        '''
        import a package to a local project. 
        The package should be local or remote git project.
        '''
        if (isinstance(package, collections.Iterable) and
            not isinstance(package, str) and
            not isinstance(package, unicode) and
            len(package) == 2):
            package, url = package

        checkNonEmptyStringPackage(package)
        self.checkNoPackage(projectLocalName=projectLocalName, package=package)

        self._myObsLightProjects.getProject(projectLocalName).addPackage(package, url)

        self._myObsLightProjects.save()

    @checkProjectLocalName(1)
    def addPackage(self, projectLocalName, package):
        '''
        Add a package to a local project. The package must exist on the
        OBS server.
        '''
        checkNonEmptyStringPackage(package)
        self.checkNoPackage(projectLocalName=projectLocalName, package=package)

        server = self._myObsLightProjects.getProject(projectLocalName).getObsServer()
        projectObsName = self._myObsLightProjects.getProject(projectLocalName).getProjectObsName()

        if not package in self.getObsProjectPackageList(server, projectObsName):
            msg = " package '%s' is not part of the '%s' project" % (package, projectObsName)
            raise ObsLightObsServers(msg)

        self._myObsLightProjects.getProject(projectLocalName).addPackage(package)
        self._myObsLightProjects.save()

    def getObsProjectPackageList(self, serverApi, projectObsName):
        '''
        Return the list of packages of a project on an OBS server.
        '''
        checkNonEmptyStringServerApi(serverApi=serverApi)
        self.checkAvailableProjectObsName(projectObsName=projectObsName, serverApi=serverApi)
        server = self._myObsServers.getObsServer(serverApi)
        return server.getPackageList(projectLocalName=projectObsName)

    @checkProjectLocalName(1)
    def removePackage(self, projectLocalName, package):
        '''
        Remove a package from a local project.
        '''
        checkNonEmptyStringPackage(package)
        self.checkPackage(projectLocalName=projectLocalName, package=package)
        res = self._myObsLightProjects.getProject(projectLocalName).removePackage(package)
        self._myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def getPackageParameter(self, projectLocalName, package, parameter):
        '''
        Get the value of a project parameter:
        the valid parameter is :
            name
            listFile
            status
            specFile
            packageChrootDirectory
            packageSourceDirectory
            description
            title
        '''
        checkNonEmptyStringPackage(package)
        self.checkPackage(projectLocalName=projectLocalName, package=package)
        project = self._myObsLightProjects.getProject(projectLocalName)
        return project.getPackageParameter(package=package, parameter=parameter)

    def getObsPackageParameter(self, serverApi, obsproject, package, parameter):
        '''
        Get the value of a project parameter.
        Valid parameter are:
            title
            description
            url
        '''
        checkNonEmptyStringServerApi(serverApi=serverApi)
        self.checkObsServerAlias(serverApi=serverApi)

        return  self._myObsServers.getObsServer(serverApi).getPackageParameter(obsproject,
                                                                               package,
                                                                               parameter)

    @checkProjectLocalName(1)
    def setPackageParameter(self, projectLocalName, package, parameter, value):
        '''
        return the value  of the parameter of the package:
        the valid parameter is :
            specFile
            packageDirectory
            description
            packageTitle
        '''
        checkNonEmptyStringPackage(package)
        self.checkPackage(projectLocalName=projectLocalName, package=package)
        res = self._myObsLightProjects.getProject(projectLocalName).setPackageParameter(package,
                                                                                        parameter,
                                                                                        value)
        self._myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def updatePackage(self, projectLocalName, package, controlFunction=None):
        '''
        
        '''
        checkNonEmptyStringPackage(package)
        self.checkPackage(projectLocalName=projectLocalName, package=package)
        res = self._myObsLightProjects.updatePackage(projectLocalName=projectLocalName,
                                                     package=package,
                                                     controlFunction=controlFunction)
        self._myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    @checkNonEmptyStringMessage(3)
    def addAndCommitChanges(self, projectLocalName, package, message):
        '''
        Add/Remove file in the local directory of a package, and commit change to the OBS.
        '''
        checkNonEmptyStringPackage(package)
        self.checkPackage(projectLocalName=projectLocalName, package=package)

        project = self._myObsLightProjects.getProject(projectLocalName)
        project.getPackage(package=package).addRemoveFileToTheProject()
        res = project.commitPackageChange(message=message, package=package)

        self._myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def repairPackageDirectory(self, projectLocalName, package):
        '''
        Reset a the osc directory.
        '''
        project = self._myObsLightProjects.getProject(projectLocalName)
        res = project.repairPackageDirectory(package=package)
        self._myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def refreshPackageDirectoryStatus(self, projectLocalName, package, controlFunction=None):
        '''
        Refresh the osc status of a package.
        '''
        res = self._myObsLightProjects.refreshPackageDirectoryStatus(projectLocalName,
                                                                 package=package,
                                                                 controlFunction=controlFunction)
        self._myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def refreshObsStatus(self, projectLocalName, package, controlFunction=None):
        '''
        Refresh the OBS status.
        '''
        res = self._myObsLightProjects.refreshObsStatus(projectLocalName=projectLocalName,
                                                        package=package,
                                                        controlFunction=controlFunction)

        self._myObsLightProjects.save()
        return res

#    @checkProjectLocalName(1)
#    @checkNonEmptyStringPackage(2)
#    @checkFilePath(3)
#    def addFileToPackage(self, projectLocalName, package, path):
#        '''
#        Add a file to a package.
#        '''
#        self.checkPackage(projectLocalName=projectLocalName, package=package)
#        project = self._myObsLightProjects.getProject(projectLocalName)
#        res = project.getPackage(package).addFile(path)
#        self._myObsLightProjects.save()
#        return res

#    @checkProjectLocalName(1)
#    @checkNonEmptyStringPackage(2)
#    def deleteFileFromPackage(self, projectLocalName, package, name):
#        '''
#        Delete a file from a package.
#        '''
#        self.checkPackage(projectLocalName=projectLocalName, package=package)
#        if not isNonEmptyString(name):
#            raise ObsLightProjectsError(" invalid path name: " + str(name))
#        self._myObsLightProjects.getProject(projectLocalName).getPackage(package).delFile(name)
#        self._myObsLightProjects.save()

    @checkProjectLocalName(1)
    def getPackageFileInfo(self, projectLocalName, package, fileName):
        '''
        Get a dictionary containing file information:
        - "Status": status returned by osc (one character of " MADC?!")
        - "File name length": just to test
        '''
        checkNonEmptyStringPackage(package)
        project = self._myObsLightProjects.getProject(projectLocalName)
        return project.getPackage(package).getPackageFileInfo(fileName)

    @checkProjectLocalName(1)
    def testConflict(self, projectLocalName, package):
        '''
        Return True if 'package' has conflict else False.
        '''
        project = self._myObsLightProjects.getProject(projectLocalName)
        return project.getPackage(package).testConflict()

    @checkProjectLocalName(1)
    def resolveConflict(self, projectLocalName, package):
        project = self._myObsLightProjects.getProject(projectLocalName)
        return project.getPackage(package).autoResolvedConflict()

    #///////////////////////////////////////////////////////////////////////////filesystem
    @checkProjectLocalName(1)
    def createChRoot(self, projectLocalName):
        '''
        Create a chroot for the project. You need a least one package.
        '''
        res = self._myObsLightProjects.getProject(projectLocalName).createChRoot()
        self._myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def removeChRoot(self, projectLocalName):
        '''
        
        '''
        res = self._myObsLightProjects.getProject(projectLocalName).removeChRoot()
        self._myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def getChRootPath(self, projectLocalName):
        '''
        Return the path of aChRoot of a project
        '''
        return self._myObsLightProjects.getProject(projectLocalName).getChRootPath()

    @checkProjectLocalName(1)
    def isChRootInit(self, projectLocalName):
        '''
        Return True if the ChRoot is init otherwise False.
        '''
        return self._myObsLightProjects.getProject(projectLocalName).isChRootInit()

    @checkProjectLocalName(1)
    def goToChRoot(self, projectLocalName, package=None, useRootId=False, detach=False):
        '''
        offer a bash in the chroot for the user
        if package  define, the pwd will be ~/rpmbuild/BUILD/[package]
        '''
        return self._myObsLightProjects.getProject(projectLocalName).goToChRoot(package,
                                                                                useRootId,
                                                                                detach)

    @checkProjectLocalName(1)
    def execScript(self, projectLocalName, aPath):
        '''
        
        '''
        return self._myObsLightProjects.getProject(projectLocalName).execScript(aPath)
    #/////////////////////////////////////////////////////////////filesystem->Repositories

    @checkProjectLocalName(1)
    def addRepo(self, projectLocalName, fromProject=None, repoUrl=None, alias=None):
        '''
        Add a repository in the chroot's zypper configuration file.
        You can add the repository of another project or use a specific url.
        '''

        if (fromProject == None) and ((repoUrl == None) or (alias == None)):
            raise ObsLightProjectsError("wrong value for fromProject or (repoUrl, alias)")
        elif (fromProject != None) and (not self.isALocalProject(fromProject)):
            raise ObsLightProjectsError("'" + fromProject + "' is not a local project")

        if fromProject != None:
            project1 = self._myObsLightProjects.getProject(fromProject)
            project2 = self._myObsLightProjects.getProject(projectLocalName)
            res = project1.addRepo(chroot=project2.getChRoot())
        else:
            project = self._myObsLightProjects.getProject(projectLocalName)
            res = project.addRepo(repos=repoUrl, alias=alias)

        self._myObsLightProjects.save()
        return res

#    @checkProjectLocalName(1)
#    def getChRootRepositories(self, projectLocalName):
#        '''
#        Return a dictionary of RPM package repositories configured in 
#        the chroot of project 'projectLocalName'. 
#        The dictionary has aliases as keys and URL as values.
#        '''
#        return self._myObsLightProjects.getProject(projectLocalName).getChRootRepositories()

    @checkProjectLocalName(1)
    def deleteRepo(self, projectLocalName, repoAlias):
        '''
        Delete an RPM package repository from the chroot's zypper
        configuration file.
        '''
        res = self._myObsLightProjects.getProject(projectLocalName).deleteRepo(repoAlias)
        self._myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def modifyRepo(self, projectLocalName, repoAlias, newUrl, newAlias):
        res = self._myObsLightProjects.getProject(projectLocalName).modifyRepo(repoAlias,
                                                                               newUrl,
                                                                               newAlias)
        self._myObsLightProjects.save()
        return res

    #///////////////////////////////////////////////////////////////////////////rpmbuild
    @checkProjectLocalName(1)
    def isInstalledInChRoot(self, projectLocalName, package):
        '''
        Return True if the package is installed into the chroot of the project.
        '''
        checkNonEmptyStringPackage(package)
        self.checkPackage(projectLocalName=projectLocalName, package=package)
        project = self._myObsLightProjects.getProject(projectLocalName)
        return project.getPackage(package).isInstallInChroot()

    @checkProjectLocalName(1)
    def buildPrep(self, projectLocalName, package):
        '''
        Add a source RPM from the OBS repository into the chroot.
        '''
        res = self._myObsLightProjects.getProject(projectLocalName).buildPrep(package=package)
        self._myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def buildRpm(self, projectLocalName, package):
        '''
        Execute the %build section of an RPM spec file.
        '''
        res = self._myObsLightProjects.getProject(projectLocalName).buildRpm(package=package)
        self._myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def installRpm(self, projectLocalName, package):
        '''
        Execute the %install section of an RPM spec file.
        '''
        res = self._myObsLightProjects.getProject(projectLocalName).installRpm(package=package)
        self._myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def packageRpm(self, projectLocalName, package):
        '''
        Execute the package section of an RPM spec file.
        '''
        res = self._myObsLightProjects.getProject(projectLocalName).packageRpm(package=package)
        self._myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    @checkNonEmptyStringPatch(3)
    def createPatch(self, projectLocalName, package, patch):
        '''
        Generate patch, and add it to the local OBS package, modify the spec file.
        '''
        checkNonEmptyStringPackage(package)
        self.checkPackage(projectLocalName=projectLocalName, package=package)
        res = self._myObsLightProjects.getProject(projectLocalName).createPatch(package, patch)
        self._myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def updatePatch(self, projectLocalName, package):
        '''
        Generate patch, and add it to the local OBS package, modify the spec file.
        '''
        checkNonEmptyStringPackage(package)
        self.checkPackage(projectLocalName=projectLocalName, package=package)
        res = self._myObsLightProjects.getProject(projectLocalName).updatePatch(package)
        self._myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def patchIsInit(self, projectLocalName, packageName):
        project = self._myObsLightProjects.getProject(projectLocalName)
        return project.getPackage(packageName).patchIsInit()



    #///////////////////////////////////////////////////////////////////////////micproject
    #///////////////////////////////////////////////////////////////////////////qemuproject

class ObsLightManager(ObsLightManagerCore):
    '''
    Application Programming Interface between clients (command line, GUI) and OBS Light.
    All interactions should be done with this class, no other class should
    be imported in external projects.
    '''
    def __init__(self):
        '''
        Initialize the OBS Light Manager.
        '''
        ObsLightManagerCore.__init__(self)

    @checkProjectLocalName(1)
    def getPackageInfo(self, projectLocalName, package=None):
        '''
        Return a dictionary.
        The key is the package name.
        the value is a dictionary.
            The key is the info, ["obsRev", "oscRev", "status", "oscStatus", "chRootStatus"].
            The val is a string. 
                For  ["obsRev", "oscRev"] can be -1,0,1,...
                For ["status", "oscStatus", "chRootStatus"] define in 
                [getListStatus,getListOscStatus,getListChRootStatus]
        If package =None:
            return all the package filtered.
        else:
            return only package.
        '''
        return self._myObsLightProjects.getProject(projectLocalName).getPackageInfo(package)

#    @checkProjectLocalName(1)
#    def getListOscStatus(self, projectLocalName):
#        '''
#        
#        '''
#        return self._myObsLightProjects.getProject(projectLocalName).getListOscStatus()

#    @checkProjectLocalName(1)
#    def getListStatus(self, projectLocalName):
#        '''
#
#        '''
#        return self._myObsLightProjects.getProject(projectLocalName).getListStatus()

#    @checkProjectLocalName(1)
#    def getListChRootStatus(self, projectLocalName):
#        '''
#        
#        '''
#        return self._myObsLightProjects.getProject(projectLocalName).getListChRootStatus()

    @checkProjectLocalName(1)
    def getPackageFilter(self, projectLocalName):
        '''
        Return the dictionary of the PackageFilter.
        the key is the info, "obsRev", "oscRev", "status", "oscStatus", "chRootStatus".
        the value is the value to filter.
        '''
        return self._myObsLightProjects.getProject(projectLocalName).getPackageFilter()

    @checkProjectLocalName(1)
    def removePackageFilter(self, projectLocalName, key):
        '''
        remove a filter from the dictionary of the PackageFilter.
        the key is the info, "obsRev", "oscRev", "status", "oscStatus", "chRootStatus".
        '''
        res = self._myObsLightProjects.getProject(projectLocalName).removePackageFilter(key=key)
        self._myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def addPackageFilter(self, projectLocalName, key, val):
        '''
        Add a filter from the dictionary of the PackageFilter.
        The key is the info, ["obsRev", "oscRev", "status", "oscStatus", "chRootStatus"].
        The val is a string. 
            For  ["obsRev", "oscRev"] can be -1,1,2,...
            For ["status", "oscStatus", "chRootStatus"] define in 
            [getListStatus,getListOscStatus,getListChRootStatus]
        '''
        res = self._myObsLightProjects.getProject(projectLocalName).addPackageFilter(key=key,
                                                                                     val=val)
        self._myObsLightProjects.save()
        return res

#---------------------------------------------------------------------------Package devel
    def getFirstCommit(self, projectLocalName, package):
        pass
    def getSecondCommit(self, projectLocalName, package):
        pass
    def setFirstCommit(self, projectLocalName, package):
        pass
    def setSecondCommit(self, projectLocalName, package):
        pass

    def getListCommitTag(self, projectLocalName, package):
        pass

    def isCurrentGitIsPackageGit(self, projectLocalName, package):
        pass

    def setCurrentGitIsPackageGit(self, projectLocalName, package, val=False):
        pass

    def runGitUI(self, projectLocalName, package):
        pass

    def archiveCurrentGit(self, projectLocalName, package):
        pass

    def initCloneGit(self, projectLocalName, package, gitCommand):
        pass

#---------------------------------------------------------------------------
    @checkProjectLocalName(1)
    def openTerminal(self, projectLocalName, package):
        '''
        open a terminal into the osc directory of a package.
        '''
        return  self._myObsLightProjects.getProject(projectLocalName).openTerminal(package)

    def openFile(self, filePath):
        """
        Open file `filePath` with the default configured program.
        """
        return ObsLightTools.openFileWithDefaultProgram(filePath)

    # TODO: RLM check, called from ObsLightGui.Wizard.ChooseProjectTargetPage
    def getTargetList(self, server, project):
        """
        Get the list of available targets for `project` on `server`.
        Does network calls.
        """
        return self._myObsServers.getObsServer(server).getTargetList(project)

    # TODO: RLM check, called from ObsLightGui.Wizard.ChooseProjectArchPage
    def getArchitectureList(self, server, project, target):
        """
        Get the list of available architectures for `target` on `project` on `server`.
        Does network calls.
        """
        return self._myObsServers.getObsServer(server).getArchitectureList(project, target)
#---------------------------------------------------------------------------

    def getMicProjectList(self):
        """
        Get the list of current MIC projects.
        """
        return self._myObsLightMicProjects.getMicProjectList()

    def addMicProject(self, micProjectName):
        """
        Create new MIC project with name `micProjectName`.
        """
        self._myObsLightMicProjects.addMicProject(micProjectName=micProjectName)
        self._myObsLightMicProjects.save()

    def deleteMicProject(self, micProjectName):
        """
        Delete `micProjectName` project.
        """
        self._myObsLightMicProjects.deleteMicProject(micProjectName)
        self._myObsLightMicProjects.save()

    def setKickstartFile(self, micProjectName, filePath):
        """
        Set the Kickstart file of `micProjectName` project to `filePath`.
        """
        self._myObsLightMicProjects.setKickstartFile(micProjectName=micProjectName,
                                                      filePath=filePath)
        self._myObsLightMicProjects.save()

    def getKickstartFile(self, micProjectName):
        """
        Get the path of the Kickstart file of `micProjectName`.
        """
        return self._myObsLightMicProjects.getKickstartFile(micProjectName=micProjectName)

    def addKickstartRepository(self, micProjectName, baseurl, name, cost=None, **otherParams):
        """
        Add a package repository in the Kickstart file of `micProjectName`.
         baseurl: the URL of the repository
         name:    a name for this repository
         cost:    the cost of this repository, from 0 (highest priority) to 99, or None
        Keyword arguments can be (default value):
        - mirrorlist (""):
        - priority (None):
        - includepkgs ([]):
        - excludepkgs ([]):
        - save (False): keep the repository in the generated image
        - proxy (None):
        - proxy_username (None):
        - proxy_password (None):
        - debuginfo (False):
        - source (False):
        - gpgkey (None): the address of the GPG key of this repository
            on the generated filesystem (ex: file:///etc/pki/rpm-gpg/RPM-GPG-KEY-meego)
        - disable (False): add the repository as disabled
        - ssl_verify ("yes"):
        """
        self._myObsLightMicProjects.addKickstartRepository(micProjectName,
                                                           baseurl,
                                                           name,
                                                           cost,
                                                           **otherParams)

    def removeKickstartRepository(self, micProjectName, repositoryName):
        """
        Remove the `repositoryName` package repository from the
        Kickstart file of `micProjectName`.
        """
        self._myObsLightMicProjects.removeKickstartRepository(micProjectName,
                                                              repositoryName)

    def getKickstartRepositoryDictionaries(self, micProjectName):
        """
        Return the list (unsorted) of `micProjectName` repository dictionaries.
        These dictionaries are compatible for input to `addKickstartRepository`.
        """
        return self._myObsLightMicProjects.getKickstartRepositoryDictionaries(micProjectName)

    def addKickstartPackage(self, micProjectName, packageName, excluded=False):
        """
        Add a package in the Kickstart file of `micProjectName`.
        "excluded" parameter allows to add package as "explicitly excluded"
        (defaults to False).
        """
        self._myObsLightMicProjects.addKickstartPackage(micProjectName, packageName, excluded)

    def removeKickstartPackage(self, micProjectName, packageName):
        """
        Remove a package from the Kickstart file of `micProjectName`.
        """
        self._myObsLightMicProjects.removeKickstartPackage(micProjectName, packageName)

    def getKickstartPackageDictionaries(self, micProjectName):
        """
        Return the list (unsorted) of `micProjectName` package dictionaries.
        Each package dictionary contains:
          "name":     the name of the package
          "excluded": True if package is explicitly excluded, False otherwise
        """
        return self._myObsLightMicProjects.getKickstartPackageDictionaries(micProjectName)

    def addKickstartPackageGroup(self, micProjectName, packageGroupName):
        """
        Add a package group in the Kickstart file of `micProjectName`.
        """
        self._myObsLightMicProjects.addKickstartPackageGroup(micProjectName, packageGroupName)

    def removeKickstartPackageGroup(self, micProjectName, packageGroupName):
        """
        Remove a package group from the Kickstart file of `micProjectName`.
        """
        self._myObsLightMicProjects.removeKickstartPackageGroup(micProjectName, packageGroupName)

    def getKickstartPackageGroupDictionaries(self, micProjectName):
        """
        Get the list of Kickstart package group dictionaries of `micProjectName`.
        Each package dictionary has keys:
          "name": the name of the package group
        More keys will come...
        """
        return self._myObsLightMicProjects.getKickstartPackageGroupDictionaries(micProjectName)

    def addOrChangeKickstartCommand(self, micProjectName, fullText, command=None):
        """
        Add a new command to the Kickstart file of `micProjectName`,
        or modify an existing one.
        To add a new command, just pass the whole commandline in `fullText`.
        To change an existing command, it is preferable to pass the command
        name (or an alias) in `command` so that the old commandline can be
        erased first.
        """
        self._myObsLightMicProjects.addOrChangeKickstartCommand(micProjectName, fullText, command)

    def removeKickstartCommand(self, micProjectName, command):
        """
        Remove `command` from the Kickstart file of `micProjectName`.
        `command` must be a command name or an alias,
        but not the whole commandline.
        """
        self._myObsLightMicProjects.removeKickstartCommand(micProjectName, command)

    def getKickstartCommandDictionaries(self, micProjectName):
        """
        Get the list of Kickstart command dictionaries of `micProjectName`.
        Each dictionary contains:
          "name": the command name
          "in_use": True if the command is used in the current Kickstart file, False otherwise
          "generated_text": the text that is printed in the Kickstart file by this command
          "aliases": a list of command aliases
        """
        return self._myObsLightMicProjects.getKickstartCommandDictionaries(micProjectName)

    def addOrChangeKickstartScript(self, micProjectName, name=None, script="", **kwargs):
        """
        Add a new Kickstart script to `micProjectName`,
        or modify an existing one.
        To add a new script, leave `name` at None.
        To change an existing script, you must pass the script name
        in `name`. `script` and other keyword args are those described
        in `getKickstartScriptDictionaries()`.
        """
        self._myObsLightMicProjects.addOrChangeKickstartScript(micProjectName,
                                                               name,
                                                               script,
                                                               **kwargs)

    def removeKickstartScript(self, micProjectName, scriptName):
        """
        Remove script `scriptName` from the Kickstart file of `micProjectName`.
        """
        self._myObsLightMicProjects.removeKickstartScript(micProjectName, scriptName)

    def getKickstartScriptDictionaries(self, micProjectName):
        """
        Get the list of Kickstart script dictionaries of `micProjectName`.
        Each dictionary contains (default value):
          "name": the name of the script (generated by OBS Light)
          "type": the type of script, one of
               pykickstart.constants.[KS_SCRIPT_PRE, KS_SCRIPT_POST, KS_SCRIPT_TRACEBACK]
          "interp": the interpreter to use to run the script ('/bin/sh')
          "errorOnFail": whether to quit or continue the script if a command fails (False)
          "inChroot": whether to run inside chroot or not (False)
          "logfile": the path where to log the output of the script (None)
          "script": all the lines of the script
        """
        return self._myObsLightMicProjects.getKickstartScriptDictionaries(micProjectName)

    def addKickstartOverlayFile(self, micProjectName, source, destination):
        """
        Add a new overlay file in the target file system of `micProjectName`.
        `source` is the path where the file is currently located,
        `destination` is the path where the file will be copied
        in the target file system.
        """
        return self._myObsLightMicProjects.addKickstartOverlayFile(micProjectName,
                                                                   source,
                                                                   destination)

    def removeKickstartOverlayFile(self, micProjectName, source, destination):
        """
        Remove the overlay file which was to be copied from `source`
        to `destination` in the target file system of `micProjectName`.
        """
        return self._myObsLightMicProjects.removeKickstartOverlayFile(micProjectName,
                                                                      source,
                                                                      destination)

    def getKickstartOverlayFileDictionaries(self, micProjectName):
        """
        Get a list of overlay file dictionaries for project `micProjectName`
        containing:
          "source": the path of the file to be copied
          "destination": the path where the file will be copied
                         in target file system of `micProjectName`
        """
        return self._myObsLightMicProjects.getKickstartOverlayFileDictionaries(micProjectName)

    def saveKickstartFile(self, micProjectName, path=None):
        """
        Save the Kickstart file of `micProjectName` to `path`,
        or to the previous path if None.
        """
        self._myObsLightMicProjects.saveKickstartFile(micProjectName, path)

    def getMicProjectArchitecture(self, micProjectName):
        """
        Get the architecture of `micProjectName` project.
        """
        res = self._myObsLightMicProjects.getMicProjectArchitecture(micProjectName=micProjectName)
        self._myObsLightMicProjects.save()
        return res

    def setMicProjectArchitecture(self, micProjectName, arch):
        """
        Set the architecture of `micProjectName` project.
        """
        self._myObsLightMicProjects.setMicProjectArchitecture(micProjectName=micProjectName,
                                                              arch=arch)
        self._myObsLightMicProjects.save()

    def getAvailableMicProjectArchitectures(self, micProjectName):
        """
        Get a list of available architectures for project `micProjectName`.
        """
        return self._myObsLightMicProjects.getAvailableMicProjectArchitectures(micProjectName)

    def setMicProjectImageType(self, micProjectName, imageType):
        """
        Set the image type of `micProjectName` project.
        `imageType` must be one of those returned by
        `getAvailableMicProjectImageTypes()`.
        """
        self._myObsLightMicProjects.setMicProjectImageType(micProjectName=micProjectName,
                                                           imageType=imageType)
        self._myObsLightMicProjects.save()

    def getMicProjectImageType(self, micProjectName):
        """
        Get the image type of `micProjectName` project.
        """
        return self._myObsLightMicProjects.getMicProjectImageType(micProjectName=micProjectName)

    def getAvailableMicProjectImageTypes(self, micProjectName):
        """
        Get a list of available image types for project `micProjectName`.
        """
        return self._myObsLightMicProjects.getAvailableImageTypes(micProjectName)

    def createImage(self, micProjectName):
        self._myObsLightMicProjects.createImage(micProjectName=micProjectName)
        self._myObsLightMicProjects.save()

#---------------------------------------------------------------------------

    def createRepo(self, projectLocalName=None):
        '''
        Create a Repository
        '''
        res = self._myObsLightProjects.getProject(projectLocalName).createRepo()
        return res

    def DeleteRepository(self, projectLocalName):
        return self._myObsLightRepositories.deleteRepository(projectLocalName)

    def createRepository(self, projectLocalName):
        return self._myObsLightRepositories.createRepository(projectLocalName)

    def scanRepository(self):
        return self._myObsLightRepositories.scanRepository()

    def getRepositoriesList(self):
        return self._myObsLightRepositories.getRepositoriesList()

    def getLocalRepository(self, project):
        return self._myObsLightRepositories.getRepository(project).getLocalRepository()

#---------------------------------------------------------------------------
    def isObsLightServerAvailable(self):
        '''
        return True/False if the OBS Light server (tftp/nfs/http) is available on the local host 
        '''
        return self._myObsLightLocalServer.isObsLightServerAvailable()

    def addDirectoryToServer(self, directory):
        '''
        Add mount a directory into the OBS Light server (tftp/nfs/http) /srv/obslight
        '''
        return self._myObsLightLocalServer.addDirectoryToServer(directory)



__myObsLightManager = None

def getCommandLineManager():
    '''
    Get a reference to the ObsLightManager singleton.
    '''
    global __myObsLightManager
    if __myObsLightManager == None:
        __myObsLightManager = ObsLightManagerCore()

    return __myObsLightManager

def getManager():
    '''
    Get a reference to the ObsLightManager singleton.
    '''
    global __myObsLightManager
    if __myObsLightManager == None:
        __myObsLightManager = ObsLightManager()

    return __myObsLightManager
