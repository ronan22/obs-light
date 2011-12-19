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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
'''
Created on 17 juin 2011

@author: Ronan Le Martret
@author: Florent Vennetier
'''

import os
import sys

from ObsLightServers import ObsLightServers
from ObsLightProjects import ObsLightProjects
from ObsLightTools import isNonEmptyString
import ObsLightConfig
import ObsLightTools
import ObsLightPrintManager
import inspect

from ObsLightErr import ObsLightObsServers
from ObsLightErr import ObsLightProjectsError
from ObsLightErr import ArgError

VERSION = "0.4.8-1"

if os.getegid() == 0:
    print "Sorry, Can't run OBS Light as root."
    sys.exit(0)

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
                raise ObsLightProjectsError("'" + str(projectLocalName) + "' is not a local project")
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
                raise ObsLightProjectsError("'" + str(val) + "' is not a local project")
            return f(*args, **kwargs)
        return checkAvailableProjectLocalName2
    return checkAvailableProjectLocalName1

def checkNonEmptyStringLocalName(position=None):
    def checkNonEmptyStringLocalName1(f):
        def checkNonEmptyStringLocalName2(*args, **kwargs):
            projectLocalName = None
            if (position is not None) and (position < len(args)):
                projectLocalName = args[position]
            elif "projectLocalName" in kwargs :
                projectLocalName = kwargs["projectLocalName"]
            else:
                raise ObsLightProjectsError("checkNonEmptyStringLocalName Fails")
            if not isNonEmptyString(projectLocalName):
                raise ObsLightObsServers("Invalid projectLocalName name: '" + str(projectLocalName) + "'")
            elif ":" in projectLocalName:
                raise ObsLightProjectsError("You can't use ':' in projectLocalName '" + str(projectLocalName) + "'")
            return f(*args, **kwargs)
        return checkNonEmptyStringLocalName2
    return checkNonEmptyStringLocalName1

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

def checkObsServerAlias(position=None):
    def checkObsServerAlias1(f):
        def checkObsServerAlias2(*args, **kwargs):
            mngr = getManager()
            val = None
            if (position is not None) and (position < len(args)):
                val = args[position]
            elif "obsServerAlias" in kwargs :
                val = kwargs["obsServerAlias"]
            else:
                raise ObsLightProjectsError("checkObsServerAlias Fails")
            if not mngr.isAnObsServer(val):
                raise ObsLightObsServers(val + " is not an OBS server")
            return f(*args, **kwargs)
        return checkObsServerAlias2
    return checkObsServerAlias1

def checkNonEmptyStringPackage(position=None):
    def checkNonEmptyStringPackage1(f):
        def checkNonEmptyStringPackage2(*args, **kwargs):
            val = None
            if (position is not None) and (position < len(args)):
                val = args[position]
            elif "package" in kwargs :
                val = kwargs["package"]
            else:
                raise ObsLightProjectsError("checkNonEmptyStringPackage Fails")
            if not isNonEmptyString(val):
                raise ObsLightObsServers("Invalid package name: " + str(val))
            return f(*args, **kwargs)
        return checkNonEmptyStringPackage2
    return checkNonEmptyStringPackage1

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

def checkPackage(position1=None, position2=None):
    def checkPackage1(f):
        def checkPackage2(*args, **kwargs):
            mngr = getManager()
            projectLocalName = None
            package = None
            if (position1 is not None) and (position1 < len(args)):
                projectLocalName = args[position1]
            elif "projectLocalName" in kwargs :
                projectLocalName = kwargs["projectLocalName"]
            else:
                raise ObsLightProjectsError("checkPackage Fails no projectLocalName")
            if (position2 is not None) and (position2 < len(args)):
                package = args[position2]
            elif "package" in kwargs :
                package = kwargs["package"]
            else:
                raise ObsLightProjectsError("checkPackage Fails no package")
            if not package in mngr.getLocalProjectPackageList(projectLocalName=projectLocalName, local=1):
                raise ObsLightObsServers("'" + package + "' is not a local package of '" + projectLocalName + "'")
            return f(*args, **kwargs)
        return checkPackage2
    return checkPackage1

def checkNonEmptyStringServerApi(position=None):
    def checkNonEmptyStringServerApi1(f):
        def checkNonEmptyStringServerApi2(*args, **kwargs):
            serverApi = None
            if (position is not None) and (position < len(args)):
                serverApi = args[position]
            elif "package" in kwargs :
                serverApi = kwargs["package"]
            else:
                raise ObsLightProjectsError("checkNonEmptyStringServerApi Fails")
            if not isNonEmptyString(serverApi):
                raise ObsLightObsServers("Can't create a OBSServer: invalid API:" + str(serverApi))
            return f(*args, **kwargs)
        return checkNonEmptyStringServerApi2
    return checkNonEmptyStringServerApi1

def checkAvailableServerApi(position=None):
    def checkAvailableServerApi1(f):
        def checkAvailableServerApi2(*args, **kwargs):
            mngr = getManager()
            serverApi = None
            if (position is not None) and (position < len(args)):
                serverApi = args[position]
            elif "serverApi" in kwargs :
                serverApi = kwargs["serverApi"]
            else:
                raise ObsLightProjectsError("checkAvailableServerApi Fails")
            if mngr.isAnObsServer(serverApi):
                raise ObsLightObsServers(serverApi + " is already an OBS server")
            return f(*args, **kwargs)
        return checkAvailableServerApi2
    return checkAvailableServerApi1

def checkServerApi(position=None):
    def checkServerApi1(f):
        def checkServerApi2(*args, **kwargs):
            mngr = getManager()
            serverApi = None
            if (position is not None) and (position < len(args)):
                serverApi = args[position]
            elif "serverApi" in kwargs :
                serverApi = kwargs["serverApi"]
            else:
                raise ObsLightProjectsError("checkServerApi Fails")
            if not mngr.isAnObsServer(serverApi):
                raise ObsLightObsServers(serverApi + " is not an OBS server")
            return f(*args, **kwargs)
        return checkServerApi2
    return checkServerApi1

def checkAvailableAlias(position=None):
    def checkAvailableAlias1(f):
        def checkAvailableAlias2(*args, **kwargs):
            mngr = getManager()
            alias = None
            if (position is not None) and (position < len(args)):
                serverApi = args[position]
            elif "alias" in kwargs :
                serverApi = kwargs["alias"]
            else:
                raise ObsLightProjectsError("checkAvailableAlias Fails")
            if mngr.isAnObsServer(serverApi):
                raise ObsLightObsServers(serverApi + " is already an OBS server")
            return f(*args, **kwargs)
        return checkAvailableAlias2
    return checkAvailableAlias1

def checkAvailableAliasOsc(position1=None, position2=None):
    def checkAvailableAliasOsc1(f):
        def checkAvailableAliasOsc2(*args, **kwargs):
            mngr = getManager()
            serverApi = None
            alias = None
            if (position1 is not None) and (position1 < len(args)):
                serverApi = args[position1]
            elif "serverApi" in kwargs :
                serverApi = kwargs["serverApi"]
            else:
                raise ObsLightProjectsError("checkPackage Fails no serverApi")
            if (position2 is not None) and (position2 < len(args)):
                alias = args[position2]
            elif "alias" in kwargs :
                alias = kwargs["alias"]
            else:
                raise ObsLightProjectsError("checkPackage Fails no alias")
            if mngr.isAnObsServerOscAlias(serverApi, alias):
                raise ObsLightObsServers(alias + " is already an OBS alias define in ~/.oscrc ")
            return f(*args, **kwargs)
        return checkAvailableAliasOsc2
    return checkAvailableAliasOsc1

def checkNonEmptyStringUser(position=None):
    def checkNonEmptyStringUser1(f):
        def checkNonEmptyStringUser2(*args, **kwargs):
            user = None
            if (position is not None) and (position < len(args)):
                user = args[position]
            elif "user" in kwargs :
                user = kwargs["user"]
            else:
                raise ObsLightProjectsError("checkAvailableAlias Fails")
            if not isNonEmptyString(user):
                raise ObsLightObsServers("Can't create a OBSServer: no user")
            return f(*args, **kwargs)
        return checkNonEmptyStringUser2
    return checkNonEmptyStringUser1

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

def checkNonEmptyStringPassword(position=None):
    def checkNonEmptyStringPassword1(f):
        def checkNonEmptyStringPassword2(*args, **kwargs):
            password = None
            if (position is not None) and (position < len(args)):
                password = args[position]
            elif "password" in kwargs :
                password = kwargs["password"]
            else:
                raise ObsLightProjectsError("checkAvailableAlias Fails")
            if not isNonEmptyString(password):
                raise ObsLightObsServers("no password")
            return f(*args, **kwargs)
        return checkNonEmptyStringPassword2
    return checkNonEmptyStringPassword1

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

def checkAvailableProjectObsName(position1=None, position2=None):
    def checkAvailableProjectObsName1(f):
        def checkAvailableProjectObsName2(*args, **kwargs):
            mngr = getManager()
            projectObsName = None
            obsServer = None
            if (position1 is not None) and (position1 < len(args)):
                projectObsName = args[position1]
            elif "projectObsName" in kwargs :
                projectObsName = kwargs["projectObsName"]
            else:
                raise ObsLightProjectsError("checkAvailableProjectObsName Fails no serverApi")
            if (position2 is not None) and (position2 < len(args)):
                obsServer = args[position2]
            elif "obsServer" in kwargs :
                obsServer = kwargs["obsServer"]
            else:
                raise ObsLightProjectsError("checkAvailableProjectObsName Fails no obsServer")
            if isNonEmptyString(projectObsName):
                raise ObsLightObsServers("No projectObsName")
            if not projectObsName in mngr.getObsServerProjectList(obsServer):
                raise ObsLightObsServers("'" + projectObsName + "' is not a project in the OBS server")
            return f(*args, **kwargs)
        return checkAvailableProjectObsName2
    return checkAvailableProjectObsName1

def checkProjectObsName(position1=None, position2=None):
    def checkAvailableProjectObsName1(f):
        def checkAvailableProjectObsName2(*args, **kwargs):
            mngr = getManager()
            projectObsName = None
            obsServer = None
            if (position1 is not None) and (position1 < len(args)):
                projectObsName = args[position1]
            elif "projectObsName" in kwargs :
                projectObsName = kwargs["projectObsName"]
            else:
                raise ObsLightProjectsError("checkAvailableProjectObsName Fails no serverApi")
            if (position2 is not None) and (position2 < len(args)):
                obsServer = args[position2]
            elif "obsServer" in kwargs :
                obsServer = kwargs["obsServer"]
            else:
                raise ObsLightProjectsError("checkAvailableProjectObsName Fails no obsServer")
            if isNonEmptyString(projectObsName):
                raise ObsLightObsServers("No projectObsName")
            if projectObsName in mngr.getObsServerProjectList(obsServer):
                raise ObsLightObsServers("'" + projectObsName + "' is not a project in the OBS server")
            return f(*args, **kwargs)
        return checkAvailableProjectObsName2
    return checkAvailableProjectObsName1

def checkAvailableProjectTarget(position1=None, position2=None, position3=None):
    def checkAvailableProjectTarget1(f):
        def checkAvailableProjectTarget2(*args, **kwargs):
            mngr = getManager()
            projectObsName = None
            obsServer = None
            projectTarget = None
            if (position1 is not None) and (position1 < len(args)):
                projectObsName = args[position1]
            elif "projectObsName" in kwargs :
                projectObsName = kwargs["projectObsName"]
            else:
                raise ObsLightProjectsError("checkAvailableProjectTarget Fails no serverApi")
            if (position2 is not None) and (position2 < len(args)):
                obsServer = args[position2]
            elif "obsServer" in kwargs :
                obsServer = kwargs["obsServer"]
            else:
                raise ObsLightProjectsError("checkAvailableProjectTarget Fails no obsServer")
            if (position3 is not None) and (position3 < len(args)):
                projectTarget = args[position3]
            elif "projectTarget" in kwargs :
                projectTarget = kwargs["projectTarget"]
            else:
                raise ObsLightProjectsError("checkAvailableProjectTarget Fails no projectTarget")
            if not projectTarget in mngr.getTargetList(obsServer, projectObsName):
                raise ObsLightProjectsError(projectTarget + " is not a valid target")
            return f(*args, **kwargs)
        return checkAvailableProjectTarget2
    return checkAvailableProjectTarget1

def checkAvailableProjectArchitecture(position1=None, position2=None, position3=None, position4=None):
    def checkAvailableProjectArchitecture1(f):
        def checkAvailableProjectArchitecture2(*args, **kwargs):
            mngr = getManager()
            projectObsName = None
            obsServer = None
            projectTarget = None
            projectArchitecture = None
            if (position1 is not None) and (position1 < len(args)):
                projectObsName = args[position1]
            elif "projectObsName" in kwargs :
                projectObsName = kwargs["projectObsName"]
            else:
                raise ObsLightProjectsError("checkAvailableProjectArchitecture Fails no serverApi")
            if (position2 is not None) and (position2 < len(args)):
                obsServer = args[position2]
            elif "obsServer" in kwargs :
                obsServer = kwargs["obsServer"]
            else:
                raise ObsLightProjectsError("checkAvailableProjectArchitecture Fails no obsServer")
            if (position3 is not None) and (position3 < len(args)):
                projectTarget = args[position3]
            elif "projectTarget" in kwargs :
                projectTarget = kwargs["projectTarget"]
            else:
                raise ObsLightProjectsError("checkAvailableProjectArchitecture Fails no projectTarget")
            if (position4 is not None) and (position4 < len(args)):
                projectArchitecture = args[position4]
            elif "projectArchitecture" in kwargs :
                projectArchitecture = kwargs["projectArchitecture"]
            else:
                raise ObsLightProjectsError("checkAvailableProjectArchitecture Fails no projectArchitecture")
            if not projectArchitecture in mngr.getArchitectureList(obsServer=obsServer,
                                                               projectObsName=projectObsName,
                                                               projectTarget=projectTarget):
                raise ObsLightProjectsError(projectArchitecture + " is not a valid architecture")
            return f(*args, **kwargs)
        return checkAvailableProjectArchitecture2
    return checkAvailableProjectArchitecture1

def checkAvailableProjectPackage(position1=None, position2=None, position3=None):
    def checkAvailableProjectPackage1(f):
        def checkAvailableProjectPackage2(*args, **kwargs):
            mngr = getManager()
            projectObsName = None
            obsServer = None
            package = None
            if (position1 is not None) and (position1 < len(args)):
                projectObsName = args[position1]
            elif "projectObsName" in kwargs :
                projectObsName = kwargs["projectObsName"]
            else:
                raise ObsLightProjectsError("checkAvailableProjectPackage Fails no serverApi")
            if (position2 is not None) and (position2 < len(args)):
                obsServer = args[position2]
            elif "obsServer" in kwargs :
                obsServer = kwargs["obsServer"]
            else:
                raise ObsLightProjectsError("checkAvailableProjectPackage Fails no obsServer")
            if (position3 is not None) and (position3 < len(args)):
                package = args[position3]
            elif "package" in kwargs :
                package = kwargs["package"]
            else:
                raise ObsLightProjectsError("checkAvailableProjectPackage Fails no package")
            if not package in mngr.getObsProjectPackageList(obsServer, projectObsName):
                raise ObsLightObsServers(" package '" + package + "' is not part of the '"
                                         + projectObsName + "' project")
            return f(*args, **kwargs)
        return checkAvailableProjectPackage2
    return checkAvailableProjectPackage1

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

        self.__workingDirectory = ObsLightConfig.WORKINGDIRECTORY

        self.__myObsServers = ObsLightServers(workingDirectory=self.getObsLightWorkingDirectory())
        self.__myObsLightProjects = ObsLightProjects(obsServers=self.__myObsServers,
                                                     workingDirectory=self.getObsLightWorkingDirectory())
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

    def getObsLightWorkingDirectory(self):
        '''
        Returns the OBS Light working directory, usually /home/<user>/OBSLight.
        '''
        return self.__workingDirectory

    def testServer(self, obsServer):
        '''
        Return True if obsServer is reachable, false otherwise.
        obsServer may be an OBS server alias or an HTTP(S) URL.
        '''
        return self.__myObsServers.testServer(obsServer=obsServer)

    def testUrl(self, Url):
        '''
        Return True if Url is reachable, false otherwise.
        '''
        return ObsLightTools.testUrl(Url)

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

    def testUrlRepo(self, url):
        '''
        return True if the url is a repo.
        '''
        return ObsLightTools.testUrlRepo(url=url)

    def testApi(self, api, user, passwd):
        '''
        return 0 if the API,user and passwd is OK.
        return 1 if user and passwd  are wrong.
        return 2 if api is wrong.
        '''
        return ObsLightTools.testApi(api=api, user=user, passwd=passwd)

    def getVersion(self):
        '''
        Return the version of obslight
        '''
        return VERSION
    #---------------------------------------------------------------------------
    #used by decorator.
    def isALocalProject(self, name):
        '''
        Test if name is already an OBS Project name.    
        '''
        if name in self.getLocalProjectList():
            return True
        else:
            return False

    def isAnObsServer(self, name):
        '''
        Test if name is already an OBS server name.    
        '''
        if name in self.getObsServerList():
            return True
        else:
            return False

    def isAnObsServerOscAlias(self, api, alias):
        '''
        Test if alias is define in the ~/.oscrc
        '''
        return self.__myObsServers.isAnObsServerOscAlias(api, alias)

    @checkProjectLocalName(1)
    def getLocalProjectPackageList(self, projectLocalName, local=0):
        '''
        Return the list of packages of a local project.
        If local=1, return the list of locally installed packages.
        If local=0, return the list of packages provided by the OBS server for the project.
        '''
        return self.__myObsLightProjects.getListPackage(name=projectLocalName, local=local)

    @checkNonEmptyStringServerApi(1)
    @checkServerApi(1)
    def getObsServerProjectList(self, server):
        '''
        Get the list of projects of an OBS server.
        '''
        return self.__myObsServers.getLocalProjectList(server)

    @checkNonEmptyStringServerApi(1)
    @checkNonEmptyStringLocalName(2)
    @checkObsServerAlias(1)
    @checkAvailableProjectObsName(2, 1)
    def getTargetList(self, obsServer, projectObsName):
        '''
        Return the list of targets of the specified project.
        This method is blocking so you may want to call it from a
        separate thread.
        '''
        return self.__myObsServers.getTargetList(obsServer=obsServer,
                                                 projectObsName=projectObsName)

    @checkNonEmptyStringServerApi(1)
    @checkNonEmptyStringLocalName(2)
    @checkNonEmptyStringProjectTarget(3)
    @checkObsServerAlias(1)
    def getArchitectureList(self, obsServer, projectObsName, projectTarget):
        '''
        Return the list of architectures configured on this target
        for the specified project.
        This method is blocking so you may want to call it from a
        separate thread.
        '''
        return self.__myObsServers.getArchitectureList(obsServer=obsServer ,
                                                       projectObsName=projectObsName,
                                                       projectTarget=projectTarget)

    @checkNonEmptyStringServerApi(1)
    @checkAvailableProjectObsName(2, 1)
    def getObsProjectPackageList(self, obsServer, projectObsName):
        '''
        Return the list of packages of a project on an OBS server.
        '''
        return self.__myObsServers.getListPackage(obsServer=obsServer,
                                                  projectLocalName=projectObsName)

    #---------------------------------------------------------------------------

    def getObsServerList(self, reachable=False):
        '''
        Returns the list of available OBS servers.
        if reachable =False :
            return all ObsServer
        else :
            return only the available ObsServer
        '''
        return self.__myObsServers.getObsServerList(reachable=reachable)

    @checkObsServerAlias(1)
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
        return self.__myObsServers.getObsServerParameter(obsServerAlias=obsServerAlias,
                                                         parameter=parameter)

    @checkObsServerAlias(1)
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
        res = self.__myObsServers.setObsServerParameter(obsServer=obsServerAlias,
                                                        parameter=parameter,
                                                        value=value)
        self.__myObsServers.save()
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
        '''
        if not parameter in ["projectLocalName",
                             "projectObsName",
                             "projectDirectory",
                             "obsServer",
                             "projectTarget",
                             "projectArchitecture",
                             "projectTitle",
                             "description"]:
            raise ObsLightProjectsError(parameter + " is not a parameter of a local project ")

        return self.__myObsLightProjects.getProjectParameter(projectLocalName, parameter)

    @checkProjectLocalName(1)
    def setProjectParameter(self, projectLocalName, parameter, value):
        '''
        Get the value of a project parameter.
        Valid parameters are:
            projectTarget
            projectArchitecture
            projectTitle
            description
        '''
        res = self.__myObsLightProjects.setProjectParameter(projectLocalName,
                                                            parameter,
                                                            value)
        self.__myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def removeProject(self, projectLocalName):
        '''
        Remove a local Project.
        '''
        res = self.__myObsLightProjects.removeProject(projectLocalName=projectLocalName)

        self.__myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def removeChRoot(self, projectLocalName):
        '''
        
        '''
        self.__myObsLightProjects.removeChRoot(projectLocalName)
        self.__myObsLightProjects.save()

    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(1)
    @checkPackage(1, 2)
    def removePackage(self, projectLocalName, package):
        '''
        Remove a package from a local project.
        '''
        res = self.__myObsLightProjects.removePackage(projectLocalName, package)
        self.__myObsLightProjects.save()
        return res

    @checkNonEmptyStringServerApi(1)
    @checkAvailableServerApi(1)
    @checkAvailableAlias(4)
    @checkAvailableAliasOsc(1, 4)
    @checkNonEmptyStringUser(2)
    @checkNonEmptyStringPassword(3)
    def addObsServer(self,
                     serverApi,
                     user,
                     password,
                     alias,
                     serverRepo="",
                     serverWeb=""):
        '''
        Add a new OBS server.
        '''
        self.__myObsServers.addObsServer(serverWeb=serverWeb,
                                         serverAPI=serverApi,
                                         serverRepo=serverRepo,
                                         alias=alias,
                                         user=user,
                                         passw=password)
        self.__myObsServers.save()

    @checkNonEmptyStringServerApi(1)
    @checkServerApi(1)
    def delObsServer(self, alias):
        '''
        Delete an OBS server.
        '''
        self.__myObsServers.delObsServer(alias=alias)
        self.__myObsServers.save()

    @checkNonEmptyStringServerApi(1)
    @checkNonEmptyStringLocalName(7)
    @checkNonEmptyStringProjectTarget(3)
    @checkNonEmptyStringProjectArchitecture(4)
    @checkAvailableProjectLocalName(7)
    @checkAvailableProjectObsName(2, 1)
    @checkObsServerAlias(1)
    @checkAvailableProjectTarget(2, 1, 3)
    @checkAvailableProjectArchitecture(2, 1, 3, 4)
    def addProject(self,
                   obsServer,
                   projectObsName,
                   projectTarget,
                   projectArchitecture,
                   projectTitle=None,
                   description=None,
                   projectLocalName=None):
        '''
        Create a local project associated with an OBS project.
        '''
        self.__myObsLightProjects.addProject(projectLocalName=projectLocalName,
                                             projectObsName=projectObsName,
                                             projectTitle=projectTitle,
                                             obsServer=obsServer,
                                             projectTarget=projectTarget,
                                             description=description,
                                             projectArchitecture=projectArchitecture)
        self.__myObsLightProjects.save()

    def getLocalProjectList(self):
        '''
        Return the list of all local projects.
        '''
        return self.__myObsLightProjects.getLocalProjectList()

    @checkNonEmptyStringServerApi(1)
    @checkNonEmptyStringLocalName(2)
    @checkNonEmptyStringPackage(3)
    @checkNonEmptyStringDirectory(4)
    @checkObsServerAlias(1)
    @checkAvailableProjectObsName(2, 1)
    @checkAvailableProjectPackage(2, 1, 3)
    @checkDirectory(4)
    def checkoutPackage(self, obsServer, projectObsName, package, directory):
        '''
        Check out a package from an OBS server to a local directory.
        '''
        self.__myObsServers.checkoutPackage(obsServer=obsServer,
                                            projectObsName=projectObsName,
                                            package=package,
                                            directory=directory)
        self.__myObsLightProjects.save()

    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(2)
    def getPackageStatus(self, projectLocalName, package):
        '''
        Return the status of package on the OBS server.
        '''
        return self.__myObsLightProjects.getPackageStatus(project=projectLocalName,
                                                    package=package)

    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(2)
    def getOscPackageStatus(self, projectLocalName, package):
        '''
        Return the status of osc in the package directory.
        '''
        if not isNonEmptyString(package):
            raise ObsLightObsServers(" invalid package: " + str(package))

        return self.__myObsLightProjects.getOscPackageStatus(project=projectLocalName,
                                                             package=package)

    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(2)
    def getOscPackageRev(self, projectLocalName, packageName):
        """
        Return the local revision of the package.
        """
        return self.__myObsLightProjects.getOscPackageRev(projectLocalName=projectLocalName,
                                                          packageName=packageName)


    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(2)
    def getObsPackageRev(self, projectLocalName, packageName):
        """
        Return the revision of the package on server.
        """

        return self.__myObsLightProjects.getObsPackageRev(projectLocalName=projectLocalName,
                                                          packageName=packageName)

    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(2)
    def getPackageDirectory(self, projectLocalName, packageName):
        '''
        Return the directory where the package files live.
        '''
        return self.__myObsLightProjects.getPackageDirectory(projectLocalName, packageName)

    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(2)
    def getPackageFileList(self, projectLocalName, packageName):
        '''
        
        '''
        return self.__myObsLightProjects.getPackageFileList(projectLocalName, packageName)

    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(2)
    def getPackageDirectoryInChRoot(self, projectLocalName, packageName):
        '''
        Return the directory in the chroot where the uncompressed package files live.
        '''
        if not self.isChRootInit(projectLocalName):
            raise ObsLightProjectsError("The project '" + projectLocalName
                                        + "' has no chroot at the moment")
        return self.__myObsLightProjects.getPackageDirectoryInChRoot(projectLocalName, packageName)

    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(2)
    def getPackageFileInfo(self, projectLocalName, packageName, fileName):
        '''
        Get a dictionary containing file information:
        - "Status": status returned by osc (one character of " MADC?!")
        - "File name length": just to test
        '''
        return self.__myObsLightProjects.getPackageFileInfo(projectLocalName,
                                                            packageName,
                                                            fileName)

        #status = [u'A', u'D', u' ', u'M', u'?', u'!', u'C']
        #return {u'Status': status[len(fileName) % len(status)],
        #        u"File name length": len(fileName)}

    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(2)
    def addPackage(self, projectLocalName, package):
        '''
        Add a package to a local project. The package must exist on the
        OBS server.
        '''
        server = self.__myObsLightProjects.getObsServer(projectLocalName)
        projectObsName = self.__myObsLightProjects.getProjectObsName(projectLocalName)
        if not package in self.getObsProjectPackageList(server, projectObsName):
            raise ObsLightObsServers(" package '" + package + "' is not part of the '"
                                     + projectObsName + "' project")

        self.__myObsLightProjects.addPackage(projectLocalName, package)
        self.__myObsLightProjects.save()

    @checkProjectLocalName(1)
    def createChRoot(self, projectLocalName):
        '''
        Create a chroot for the project. You need a least one package.
        '''
        self.__myObsLightProjects.createChRoot(projectLocalName=projectLocalName)
        self.__myObsLightProjects.save()

    @checkNonEmptyStringServerApi(1)
    @checkServerApi(1)
    def getRepo(self, obsServer):
        '''
        Return the URL of the OBS server package repository.
        '''
        return self.__myObsServers.getRepo(obsServer=obsServer)

    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(1)
    @checkPackage(1, 2)
    def goToChRoot(self, projectLocalName, package=None, detach=False):
        '''
        offer a bash in the chroot for the user
        if package  define, the pwd will be ~/rpmbuild/BUILD/[package]
        '''
        self.__myObsLightProjects.goToChRoot(projectLocalName, package, detach)

    @checkProjectLocalName(1)
    def openTerminal(self, projectLocalName, package):
        '''
        open a terminal into the osc directory of a package.
        '''
        return  self.__myObsLightProjects.openTerminal(projectLocalName=projectLocalName,
                                                       package=package)

    @checkFilePath(1)
    def openFile(self, filePath):
        return ObsLightTools.openFileWithDefaultProgram(filePath)

    @checkProjectLocalName(1)
    def getChRootPath(self, projectLocalName):
        '''
        Return the path of aChRoot of a project
        '''
        return self.__myObsLightProjects.getChRootPath(projectLocalName)

    @checkProjectLocalName(1)
    def isChRootInit(self, projectLocalName):
        '''
        Return True if the ChRoot is init otherwise False.
        '''
        return self.__myObsLightProjects.isChRootInit(projectLocalName=projectLocalName)

    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(2)
    @checkPackage(1, 2)
    def isInstalledInChRoot(self, projectLocalName, package):
        '''
        Return True if the package is installed into the chroot of the project.
        '''
        return self.__myObsLightProjects.isInstallInChroot(projectLocalName=projectLocalName,
                                                           package=package)
    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(2)
    @checkPackage(1, 2)
    def getGetChRootStatus(self, projectLocalName, package):
        '''
        Return the status of the package  into the chroot.
        '''
        return self.__myObsLightProjects.getGetChRootStatus(projectLocalName=projectLocalName,
                                                            package=package)

    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(2)
    def addPackageSourceInChRoot(self, projectLocalName, package):
        '''
        Add a source RPM from the OBS repository into the chroot.
        '''
        self.__myObsLightProjects.addPackageSourceInChRoot(projectLocalName=projectLocalName,
                                                           package=package)
        self.__myObsLightProjects.save()

    @checkProjectLocalName(1)
    def buildRpm(self, projectLocalName, package):
        '''
        Execute the %build section of an RPM spec file.
        '''
        self.__myObsLightProjects.buildRpm(projectLocalName=projectLocalName,
                                           package=package)
        self.__myObsLightProjects.save()

    @checkProjectLocalName(1)
    def installRpm(self, projectLocalName, package):
        '''
        Execute the %install section of an RPM spec file.
        '''
        self.__myObsLightProjects.installRpm(projectLocalName=projectLocalName,
                                                                package=package)
        self.__myObsLightProjects.save()

    @checkProjectLocalName(1)
    def packageRpm(self, projectLocalName, package):
        '''
        Execute the package section of an RPM spec file.
        '''
        self.__myObsLightProjects.packageRpm(projectLocalName=projectLocalName,
                                                                package=package)
        self.__myObsLightProjects.save()

    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(2)
    @checkPackage(1, 2)
    @checkNonEmptyStringPatch(3)
    def makePatch(self, projectLocalName, package, patch):
        '''
        Generate patch, and add it to the local OBS package, modify the spec file.
        '''
        self.__myObsLightProjects.makePatch(projectLocalName, package, patch)
        self.__myObsLightProjects.save()

    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(2)
    @checkPackage(1, 2)
    def updatePatch(self, projectLocalName, package):
        '''
        Generate patch, and add it to the local OBS package, modify the spec file.
        '''
        self.__myObsLightProjects.updatePatch(projectLocalName, package)
        self.__myObsLightProjects.save()

    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(2)
    @checkPackage(1, 2)
    @checkNonEmptyStringMessage(3)
    def addAndCommitChanges(self, projectLocalName, package, message):
        '''
        Add/Remove file in the local directory of a package, and commit change to the OBS.
        '''
        self.__myObsLightProjects.addRemoveFileToTheProject(projectLocalName, package)
        self.__myObsLightProjects.commitToObs(name=projectLocalName,
                                              message=message,
                                              package=package)
        self.__myObsLightProjects.save()

    @checkProjectLocalName(1)
    def patchIsInit(self, ProjectName, packageName):
        '''
        
        '''
        return self.__myObsLightProjects.patchIsInit(ProjectName=ProjectName,
                                                     packageName=packageName)

    @checkProjectLocalName(1)
    def addRepo(self, projectLocalName, fromProject=None, repoUrl=None, alias=None):
        '''
        Add a repository in the chroot's zypper configuration file.
        You can add the repository of another project or use a specific
        url.
        '''
        if (fromProject == None) and ((repoUrl == None) or (alias == None)):
            raise ObsLightProjectsError("wrong value for fromProject or (repoUrl, alias)")
        elif (fromProject != None) and (not self.isALocalProject(fromProject)):
            raise ObsLightProjectsError(fromProject + " is not a local project")

        self.__myObsLightProjects.addRepo(projectLocalName=projectLocalName,
                                           fromProject=fromProject,
                                           repos=repoUrl,
                                           alias=alias)
        self.__myObsLightProjects.save()

    @checkProjectLocalName(1)
    def deleteRepo(self, projectLocalName, repoAlias):
        '''
        Delete an RPM package repository from the chroot's zypper
        configuration file.
        '''
        res = self.__myObsLightProjects.deleteRepo(projectLocalName, repoAlias)
        self.__myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def modifyRepo(self, projectLocalName, repoAlias, newUrl, newAlias):
        res = self.__myObsLightProjects.modifyRepo(projectLocalName, repoAlias, newUrl, newAlias)
        self.__myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def getChRootRepositories(self, projectLocalName):
        '''
        Return a dictionary of RPM package repositories configured in the
        chroot of project 'projectLocalName'. The dictionary has aliases
        as keys and URL as values.
        '''
        return self.__myObsLightProjects.getChRootRepositories(projectLocalName=projectLocalName)

    @checkFilePath(1)
    def importProject(self, filePath):
        '''
        Import a project from a file.
        '''
        self.__myObsLightProjects.importProject(filePath)
        self.__myObsLightProjects.save()

    @checkProjectLocalName(1)
    def exportProject(self, projectLocalName, path=None):
        '''
        Export a project to a file.
        '''
        self.__myObsLightProjects.exportProject(projectLocalName, path=path)

    @checkProjectLocalName(1)
    def getProjectWebPage(self, projectLocalName):
        '''
        Get the project webpage URL.
        '''
        return self.__myObsLightProjects.getWebProjectPage(projectLocalName)

    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(2)
    @checkPackage(1, 2)
    def getPackageParameter(self, projectLocalName, package, parameter):
        '''
        Get the value of a project parameter:
        the valid parameter is :
            name
            listFile
            status
            specFile
            yamlFile
            packageDirectory
            description
            packageTitle
        '''
        return  self.__myObsLightProjects.getPackageParameter(projectLocalName=projectLocalName,
                                                              package=package,
                                                              parameter=parameter)

    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(2)
    @checkPackage(1, 2)
    def setPackageParameter(self, projectLocalName, package, parameter=None, value=None):
        '''
        return the value  of the parameter of the package:
        the valid parameter is :
            specFile
            yamlFile
            packageDirectory
            description
            packageTitle
        '''
        res = self.__myObsLightProjects.setPackageParameter(projectLocalName=projectLocalName,
                                                              package=package,
                                                              parameter=parameter,
                                                              value=value)
        self.__myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(2)
    @checkPackage(1, 2)
    def updatePackage(self, projectLocalName, package):
        '''
        
        '''
        self.__myObsLightProjects.updatePackage(projectLocalName=projectLocalName,
                                                package=package)
        self.__myObsLightProjects.save()

    @checkProjectLocalName(1)
    def getProjectRepository(self, projectLocalName):
        '''
        Return the URL of the repository of the project
        '''
        return self.__myObsLightProjects.getReposProject(projectLocalName=projectLocalName)

    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(2)
    @checkPackage(1, 2)
    @checkFilePath(3)
    def addFileToPackage(self, projectLocalName, package, path):
        '''
        Add a file to a package.
        '''
        self.__myObsLightProjects.addFileToPackage(projectLocalName=projectLocalName, package=package, path=path)
        self.__myObsLightProjects.save()

    @checkProjectLocalName(1)
    @checkNonEmptyStringPackage(2)
    @checkPackage(1, 2)
    def deleteFileFromPackage(self, projectLocalName, package, name):
        '''
        Delete a file from a package.
        '''
        if not isNonEmptyString(name):
            raise ObsLightProjectsError(" invalid path name: " + str(name))
        self.__myObsLightProjects.delFileToPackage(projectLocalName=projectLocalName, package=package, name=name)
        self.__myObsLightProjects.save()

    @checkProjectLocalName(1)
    def refreshOscDirectoryStatus(self, projectLocalName, package=None):
        '''
        Refresh the osc status of a package.
        '''
        res = self.__myObsLightProjects.refreshOscDirectoryStatus(projectLocalName, package=package)
        self.__myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def refreshObsStatus(self, projectLocalName, package=None):
        '''
        Refresh the OBS status.
        '''
        res = self.__myObsLightProjects.refreshObsStatus(projectLocalName=projectLocalName, package=package)
        self.__myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def repairOscPackageDirectory(self, projectLocalName, package):
        '''
        Reset a the osc directory.
        '''
        res = self.__myObsLightProjects.repairOscPackageDirectory(projectLocalName=projectLocalName, package=package)
        self.__myObsLightProjects.save()
        return res

    @checkProjectLocalName(1)
    def testConflict(self, projectLocalName, package):
        '''
        Return True if 'package' has conflict else False.
        '''
        return self.__myObsLightProjects.testConflict(projectLocalName, package)

__myObsLightManager = None

def getManager():
    '''
    Get a reference to the ObsLightManager singleton.
    '''
    global __myObsLightManager
    if __myObsLightManager == None:
        __myObsLightManager = ObsLightManager()

    return __myObsLightManager


















