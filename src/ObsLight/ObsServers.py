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
Created on 29 sept. 2011

@author: meego
'''

import pickle
import os
import ObsLightOsc
from ObsServer import ObsServer
from ObsLightErr import ObsLightObsServers
import ObsLightTools

class ObsServers(object):
    '''
    classdocs
    '''

    def __init__(self, workingDirectory):
        '''
        Constructor
        '''
        self.__dicOBSLightServers = {}
        self.__blackList = {}
        self.__currentServer = None
        self.__pathFile = os.path.join(workingDirectory , "ObsServersConfig")
        self.__currentOBSServer = None
        self.__initServersFromOsc()
        self.__load()

    def __initServersFromOsc(self):
        '''
        
        '''
        self.__blackList = ObsLightOsc.getObsLightOsc().getServersFromOsc()

    def isAnObsServerOscAlias(self, api, alias):
        '''
        
        '''
        for aApi in self.__blackList.keys():
            for aAlias in self.__blackList[aApi]['aliases']:
                if (alias == aAlias) and (api != aApi):
                    return True
        return False

    def __load(self):
        '''
        
        '''
        if os.path.isfile(self.__pathFile):
            aFile = open(self.__pathFile, 'r')
            saveconfigServers = pickle.load(aFile)
            aFile.close()
            saveServers = saveconfigServers["saveServers"]
            for projetName in saveServers.keys():
                aServer = saveServers[projetName]
                self.__addOBSServerFromSave(fromSave=aServer)
            self.__currentOBSServer = saveconfigServers["currentObsServer"]

    def getObsServer(self, name=None):
        '''
        
        '''
        if name in self.getObsServerList():
            return self.__dicOBSLightServers[name]
        else:
            return None

    def getObsServerList(self, reachable=False):
        '''
        
        '''
        if reachable == False:
            return self.__dicOBSLightServers.keys()
        else:
            res = []
            for serverName in self.__dicOBSLightServers.keys():
                if self.getObsServer(serverName).isReachable():
                    res.append(serverName)
            return res

    def save(self):
        '''
        
        '''
        saveServers = {}

        for obsserverName in self.getObsServerList():
            saveServers[obsserverName] = self.__dicOBSLightServers[obsserverName].getDic()

        saveconfigServers = {}
        saveconfigServers["saveServers"] = saveServers
        saveconfigServers["currentObsServer"] = self.__currentServer
        aFile = open(self.__pathFile, 'w')
        pickle.dump(saveconfigServers, aFile)
        aFile.close()

    def __addOBSServerFromSave(self, fromSave=None):
        '''
        
        '''
        aOBSServer = ObsServer(fromSave=fromSave)
        self.__dicOBSLightServers[aOBSServer.getName()] = aOBSServer


    def addObsServer(self,
                     serverWeb="",
                     serverAPI=None,
                     serverRepo="",
                     alias=None,
                     user=None,
                     passw=None):
        '''
        
        '''
        aOBSServer = ObsServer(serverWeb=serverWeb,
                               serverAPI=serverAPI,
                               serverRepo=serverRepo,
                               alias=alias,
                               user=user,
                               passw=passw)
        self.__dicOBSLightServers[aOBSServer.getName()] = aOBSServer

    def delObsServer(self, alias):
        '''
        
        '''
        if alias in self.getObsServerList():
            del self.__dicOBSLightServers[alias]
        else:
            raise ObsLightObsServers("'" + alias + "' can't be deleted, it's not an OBS Server")

    def getLocalProjectList(self, server=None):
        '''
        
        '''
        return self.__dicOBSLightServers[server].getLocalProjectList()


    def getListPackage(self, obsServer=None, projectLocalName=None):
        '''
        
        '''
        return self.__dicOBSLightServers[obsServer].getListPackage(projectLocalName=projectLocalName)

    def checkoutPackage(self,
                        obsServer=None,
                        projectObsName=None,
                        package=None,
                        directory=None):
        '''
        
        '''
        self.__dicOBSLightServers[obsServer].checkoutPackage(projectObsName=projectObsName,
                                                             package=package,
                                                             directory=directory)

    def getPackageStatus(self,
                         obsServer=None,
                         project=None,
                         package=None,
                         repo=None,
                         arch=None):
        '''
        
        '''
        return self.__dicOBSLightServers[obsServer].getPackageStatus(project=project,
                                                                     package=package,
                                                                     repo=repo,
                                                                     arch=arch)

    def getRepo(self, obsServer=None):
        '''
        
        '''
        return self.__dicOBSLightServers[obsServer].getRepo()

    def getTargetList(self, obsServer=None, projectObsName=None):
        '''
        
        '''
        return self.__dicOBSLightServers[obsServer].getTargetList(projectObsName=projectObsName)

    def getArchitectureList(self, obsServer=None,
                            projectObsName=None,
                            projectTarget=None):
        '''
        
        '''
        return self.__dicOBSLightServers[obsServer].getArchitectureList(projectObsName=projectObsName,
                                                                        projectTarget=projectTarget)


    def getObsServerParameter(self, obsServerAlias=None, parameter=None):
        '''
        
        '''
        return self.__dicOBSLightServers[obsServerAlias].getObsServerParameter(parameter=parameter)

    def setObsServerParameter(self, obsServer=None, parameter=None, value=None):
        '''
        
        '''
        return self.__dicOBSLightServers[obsServer].setObsServerParameter(parameter=parameter,
                                                                          value=value)


    def getProjectTitle(self, obsServer, projectObsName):
        '''
        
        '''
        return self.__dicOBSLightServers[obsServer].getProjectTitle(projectObsName=projectObsName)

    def getProjectDescription(self, obsServer, projectObsName):
        '''
        
        '''
        return self.__dicOBSLightServers[obsServer].getProjectDescription(projectObsName=projectObsName)

    def getPackageTitle(self, obsServer, projectObsName, package):
        '''
        
        '''
        return self.__dicOBSLightServers[obsServer].getPackageTitle(projectObsName=projectObsName,
                                                                    package=package)

    def getPackageDescription(self, obsServer, projectObsName, package):
        '''
        
        '''
        return self.__dicOBSLightServers[obsServer].getPackageDescription(projectObsName=projectObsName,
                                                                          package=package)

    def testServer(self, obsServer):
        '''
        
        '''
        if obsServer in self.getObsServerList():
            return self.__dicOBSLightServers[obsServer].testServer()
        else:
            return ObsLightTools.testHost(obsServer)

    def getObsProjectPackageList(self, obsServer, projectObsName):
        """
        
        """
        return self.__dicOBSLightServers[obsServer].getObsProjectPackageList()









