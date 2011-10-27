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

from ObsServer import ObsServer

class ObsServers(object):
    '''
    classdocs
    '''


    def __init__(self, manager):
        '''
        Constructor
        '''
        self.__dicOBSLightServers = {}
        self.__currentServer = None
        self.__manager = manager
        self.__pathFile = os.path.join(self.__manager.getObsLightWorkingDirectory() , "ObsServersConfig")
        self.__currentOBSServer = None
        self.__load()
        
    def getObsServer(self, name=None):
        '''
        
        '''
        return self.__dicOBSLightServers[name]
        
    def getObsServerList(self):
        '''
        
        '''
        return self.__dicOBSLightServers.keys()
    
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
            
    def __addOBSServerFromSave(self, fromSave=None):
        '''
        
        '''
        aOBSServer = ObsServer(fromSave=fromSave)
        self.__dicOBSLightServers[aOBSServer.getName()] = aOBSServer
        
        
    def addObsServer(self, serverWeb="",
                            serverAPI=None,
                            serverRepos="",
                            aliases=None,
                            user=None,
                            passw=None):
        '''
        
        '''
        aOBSServer = ObsServer(serverWeb=serverWeb,
                               serverAPI=serverAPI,
                               serverRepos=serverRepos,
                               aliases=aliases,
                               user=user,
                               passw=passw)
        self.__dicOBSLightServers[aOBSServer.getName()] = aOBSServer
        
        
    def getLocalProjectList(self, server=None):
        '''
        
        '''
        return self.__dicOBSLightServers[server].getLocalProjectList()
        
        
    def getListPackage(self, obsServer=None,
                            projectLocalName=None):
        '''
        
        '''
        return self.__dicOBSLightServers[obsServer].getListPackage(projectLocalName=projectLocalName)
    
    def checkoutPackage(self, obsServer=None,
                                projectLocalName=None,
                                package=None,
                                directory=None):
        '''
        
        '''
        self.__dicOBSLightServers[obsServer].checkoutPackage(projectLocalName=projectLocalName,
                                                             package=package,
                                                             directory=directory)
         
    def getPackageStatus(self, obsServer=None, project=None, package=None, repos=None, arch=None):
        '''
        
        '''
        return self.__dicOBSLightServers[obsServer].getPackageStatus(project=project,
                                                                     package=package,
                                                                     repos=repos,
                                                                     arch=arch)
        
    def getRepo(self, obsServer=None):
        '''
        
        '''
        return self.__dicOBSLightServers[obsServer].getRepo()

    def getTargetList(self, obsServer=None , projectObsName=None):
        '''
        
        '''
        return self.__dicOBSLightServers[obsServer].getTargetList(projectObsName=projectObsName)
        
    def getArchitectureList(self, obsServer=None ,
                                    projectObsName=None,
                                    projectTarget=None):
        '''
        
        '''
        return self.__dicOBSLightServers[obsServer].getArchitectureList(projectObsName=projectObsName,
                                                                        projectTarget=projectTarget)
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
