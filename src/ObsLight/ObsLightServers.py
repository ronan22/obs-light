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
Created on 29 sept. 2011

@author: ronan
'''

import pickle
import os
import ObsLightOsc
from ObsLightServer import ObsLightServer
from ObsLightErr import ObsLightObsServers
import ObsLightTools

class ObsLightServers(object):
    '''
    classdocs
    '''

    def __init__(self, workingDirectory):
        '''
        Constructor
        '''
        self.__saveconfigServers = None

        self.__dicOBSLightServers = {}
        self.__dicOBSLightServers_unLoad = {}
        #
        self.__blackList = {}
        self.__currentServer = None
        self.__pathFile = os.path.join(workingDirectory , "ObsServersConfig")
        self.__initServersFromOsc()

        self.resultLocalProjectList = {}
        self.resultListPackage = {}
        self.resultTargetList = {}
        self.resultArchitectureList = {}

    def __initServersFromOsc(self):
        '''
        
        '''
        self.__blackList = ObsLightOsc.getObsLightOsc().getServersFromOsc()

    def __load(self):
        '''
        
        '''
        if (len(self.__dicOBSLightServers.keys()) == 0) and (len(self.__dicOBSLightServers_unLoad.keys()) == 0):
            if os.path.isfile(self.__pathFile):
                aFile = open(self.__pathFile, 'r')
                self.__saveconfigServers = pickle.load(aFile)
                aFile.close()
                saveServers = self.__saveconfigServers["saveServers"]
                for projetName in saveServers.keys():
                    aServer = saveServers[projetName]
                    self.__addOBSServerFromSave(fromSave=aServer)
                self.__currentServer = self.__saveconfigServers["currentObsServer"]

    def __addOBSServerFromSave(self, fromSave=None):
        '''
        
        '''
        if "alias" in fromSave.keys():
            self.__dicOBSLightServers_unLoad[fromSave["alias"]] = fromSave
            #aOBSServer = ObsLightServer(fromSave=fromSave)
            #self.__dicOBSLightServers[aOBSServer.getName()] = aOBSServer
        else:
            raise ObsLightObsServers("can't load a project from fromSave")

    def save(self):
        '''
        
        '''
        if (len(self.__dicOBSLightServers.keys()) > 0) or (len(self.__dicOBSLightServers_unLoad.keys()) > 0):
            saveServers = {}

            for obsserverName in self.__dicOBSLightServers.keys():
                saveServers[obsserverName] = self.__dicOBSLightServers[obsserverName].getDic()
            for obsserverName in self.__dicOBSLightServers_unLoad.keys():
                saveServers[obsserverName] = self.__dicOBSLightServers_unLoad[obsserverName]

            saveconfigServers = {}
            saveconfigServers["saveServers"] = saveServers
            saveconfigServers["currentObsServer"] = self.__currentServer

            if saveconfigServers != self.__saveconfigServers:
                aFile = open(self.__pathFile, 'w')
                pickle.dump(saveconfigServers, aFile)
                aFile.close()
                self.__saveconfigServers = saveconfigServers

#-------------------------------------------------------------------------------
    def getCurrentServer(self):
        '''
        
        '''
        self.__load()
        return self.__currentServer

    def getObsServerList(self, reachable=False):
        '''
        
        '''
        self.__load()
        res = self.__dicOBSLightServers.keys()
        res.extend(self.__dicOBSLightServers_unLoad.keys())
        if reachable == False:
            return res
        else:
            reachableRes = []
            for serverName in res:
                aObsServer = self.getObsServer(serverName)
                if aObsServer == None:
                    raise ObsLightObsServers("serverName '" + serverName + "'doesn't exist")
                elif aObsServer.isReachable():
                    reachableRes.append(serverName)
            return reachableRes

    def getObsServer(self, name=None):
        '''
        
        '''
        self.__load()
        if name in self.__dicOBSLightServers.keys():
            self.__currentServer = name
            return self.__dicOBSLightServers[name]
        elif name in self.__dicOBSLightServers_unLoad.keys():
            fromSave = self.__dicOBSLightServers_unLoad[name]
            aOBSServer = ObsLightServer(fromSave=fromSave)
            self.__dicOBSLightServers[aOBSServer.getName()] = aOBSServer
            del self.__dicOBSLightServers_unLoad[name]
            self.__currentServer = name
            return self.__dicOBSLightServers[name]
        else:
            return None

    def testServer(self, obsServer):
        '''
        
        '''
        if obsServer in self.getObsServerList():
            return self.getObsServer(obsServer).testServer()
        else:
            return ObsLightTools.testHost(obsServer)

    def testApi(self, api, user, passwd):
        '''
        return 0 if the API,user and passwd is OK.
        return 1 if user and passwd  are wrong.
        return 2 if api is wrong.
        '''
        return ObsLightOsc.getObsLightOsc().testApi(api=api, user=user, passwd=passwd)
#-------------------------------------------------------------------------------
    def isAnObsServerOscAlias(self, api, alias):
        '''
        
        '''
        for aApi in self.__blackList.keys():
            for aAlias in self.__blackList[aApi]['aliases']:
                if (alias == aAlias) and (api != aApi):
                    return True
        return False

    def addObsServer(self,
                     serverWeb="",
                     serverAPI=None,
                     serverRepo="",
                     alias=None,
                     user=None,
                     passw=None):
        '''
        
        '''
        aOBSServer = ObsLightServer(serverWeb=serverWeb,
                               serverAPI=serverAPI,
                               serverRepo=serverRepo,
                               alias=alias,
                               user=user,
                               passw=passw)
        ObsLightTools.importCert(serverAPI)
        self.__dicOBSLightServers[aOBSServer.getName()] = aOBSServer

    def delObsServer(self, alias):
        '''
        
        '''
        if alias in self.__dicOBSLightServers.keys():
            del self.__dicOBSLightServers[alias]
        elif alias in self.__dicOBSLightServers_unLoad.keys():
            del self.__dicOBSLightServers_unLoad[alias]
        else:
            raise ObsLightObsServers("'" + alias + "' can't be deleted, it's not an OBS Server")

    def getLocalProjectList(self,
                            server=None,
                            maintainer=False,
                            bugowner=False,
                            arch=None,
                            remoteurl=False):
        '''
        
        '''
        return self.getObsServer(server).getLocalProjectList(maintainer=maintainer,
                                                             bugowner=bugowner,
                                                             arch=arch,
                                                             remoteurl=remoteurl)

    def getListPackage(self, obsServer=None, projectLocalName=None):
        '''
        
        '''
        if obsServer in self.resultListPackage.keys():
            if projectLocalName in self.resultListPackage[obsServer].keys():
                return self.resultListPackage[obsServer][projectLocalName]
            else:
                res = self.getObsServer(obsServer).getListPackage(projectLocalName=projectLocalName)
                if res != None:
                    self.resultListPackage[obsServer][projectLocalName] = res
                return res
        else:
            res = self.getObsServer(obsServer).getListPackage(projectLocalName=projectLocalName)
            if res != None:
                self.resultListPackage[obsServer] = {}
                self.resultListPackage[obsServer][projectLocalName] = res
            return res

    def checkoutPackage(self,
                        obsServer=None,
                        projectObsName=None,
                        package=None,
                        directory=None):
        '''
        
        '''
        self.getObsServer(obsServer).checkoutPackage(projectObsName=projectObsName,
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
        return self.getObsServer(obsServer).getPackageStatus(project=project,
                                                                     package=package,
                                                                     repo=repo,
                                                                     arch=arch)

    def getRepo(self, obsServer=None):
        '''
        
        '''
        return self.getObsServer(obsServer).getRepo()

    def getTargetList(self, obsServer=None, projectObsName=None):
        '''
        
        '''
        if obsServer in self.resultTargetList.keys():
            if projectObsName in self.resultTargetList[obsServer].keys():
                return self.resultTargetList[obsServer][projectObsName]
            else:
                res = self.getObsServer(obsServer).getTargetList(projectObsName=projectObsName)
                if res != None:
                    self.resultTargetList[obsServer][projectObsName] = res
                return res
        else:
            res = self.getObsServer(obsServer).getTargetList(projectObsName=projectObsName)
            if res != None:
                self.resultTargetList[obsServer] = {}
                self.resultTargetList[obsServer][projectObsName] = res
            return res

    def getArchitectureList(self, obsServer=None,
                            projectObsName=None,
                            projectTarget=None):
        '''
        
        '''
        if obsServer in self.resultArchitectureList.keys():
            if projectObsName in self.resultArchitectureList[obsServer].keys():
                if projectTarget in self.resultArchitectureList[obsServer][projectObsName].keys():
                    return self.resultArchitectureList[obsServer][projectObsName][projectTarget]
                else:
                    res = self.getObsServer(obsServer).getArchitectureList(projectObsName=projectObsName,
                                                                        projectTarget=projectTarget)
                    if res != None:
                        self.resultArchitectureList[obsServer][projectObsName][projectTarget] = res
                    return res
            else:
                res = self.getObsServer(obsServer).getArchitectureList(projectObsName=projectObsName,
                                                                        projectTarget=projectTarget)
                if res != None:
                    self.resultArchitectureList[obsServer][projectObsName] = {}
                    self.resultArchitectureList[obsServer][projectObsName][projectTarget] = res
                return res
        else:
            res = self.getObsServer(obsServer).getArchitectureList(projectObsName=projectObsName,
                                                                        projectTarget=projectTarget)
            if res != None:
                self.resultArchitectureList[obsServer] = {}
                self.resultArchitectureList[obsServer][projectObsName] = {}
                self.resultArchitectureList[obsServer][projectObsName][projectTarget] = res
            return res

    def getObsServerParameter(self, obsServerAlias=None, parameter=None):
        '''
        
        '''
        return self.getObsServer(obsServerAlias).getObsServerParameter(parameter=parameter)

    def setObsServerParameter(self, obsServer=None, parameter=None, value=None):
        '''
        
        '''
        return self.getObsServer(obsServer).setObsServerParameter(parameter=parameter,
                                                                          value=value)

    def getProjectTitle(self, obsServer, projectObsName):
        '''
        
        '''
        return self.getObsServer(obsServer).getProjectTitle(projectObsName=projectObsName)

    def getProjectDescription(self, obsServer, projectObsName):
        '''
        
        '''
        return self.getObsServer(obsServer).getProjectDescription(projectObsName=projectObsName)

    def getPackageTitle(self, obsServer, projectObsName, package):
        '''
        
        '''
        return self.getObsServer(obsServer).getPackageTitle(projectObsName=projectObsName,
                                                                    package=package)

    def getPackageDescription(self, obsServer, projectObsName, package):
        '''
        
        '''
        return self.getObsServer(obsServer).getPackageDescription(projectObsName=projectObsName,
                                                                          package=package)


    def getObsProjectPackageList(self, obsServer, projectObsName):
        """
        
        """
        return self.getObsServer(obsServer).getObsProjectPackageList()

    def getObsPackageRev(self,
                         obsServer,
                         projectObsName,
                         package):
        """
        
        """
        return self.getObsServer(obsServer).getObsPackageRev(projectObsName=projectObsName,
                                                                     package=package)






