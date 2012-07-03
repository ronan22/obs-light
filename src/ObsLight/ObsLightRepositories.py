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
Created on 2 Jui. 2012

@author: ronan@fridu.net
'''
import os
import pickle

import urlparse

import ObsLightConfig

from ObsLightSubprocess import SubprocessCrt
from ObsLightRepository import ObsLightRepository

class ObsLightRepositories(object):
    '''
    classdocs
    '''
    def __init__(self, workingDirectory):
        '''
        Constructor
        '''
        self.__repositoriesPath = ObsLightConfig.getRepositriesServerPath()
        self.__workingDirectory = workingDirectory
        pathDir = os.path.expanduser(self.__repositoriesPath)
        if not os.path.isdir(pathDir):
            os.makedirs(pathDir)

        self.__pathFile = os.path.join(self.__workingDirectory, "ObsLightRepositoriesConfig")

        self.__dicOBSLightRepositories = {}

        self.__mySubprocessCrt = SubprocessCrt()

    def __subprocess(self, command=None, waitMess=False, stdout=False):
        return self.__mySubprocessCrt.execSubprocess(command=command,
                                                     waitMess=waitMess,
                                                     stdout=stdout)

    def getRepositoriesList(self, APIName=None):
        '''
        
        '''

        if APIName == None:
            return self.__dicOBSLightRepositories.keys()
        elif APIName in self.__dicOBSLightRepositories.keys():
            return self.__dicOBSLightRepositories[APIName].keys()
        return 1

#    def __load(self, aFile=None):
#        '''
#        
#        '''
#        return 0
#
#    def save(self):
#        '''
#        
#        '''
#        aFile = open(pathFile, 'w')
#        pickle.dump(saveconfigProject, aFile)
#        aFile.close()
#        return 0

    def scanRepository(self):
        for APIName in os.listdir(self.__repositoriesPath):
            APINamePath = os.path.join(self.__repositoriesPath, APIName)
            if os.path.isdir(APINamePath):
                for repo in os.listdir(APINamePath):
                    pathRepo = os.path.join(APINamePath, repo)
                    if os.path.isdir(pathRepo):
                        self.createRepo(APIName, repo)


    def getRepository(self, APIName, projectObsName):
        APIName = str(urlparse.urlparse(APIName)[1])
        pathDir = os.path.join(self.__repositoriesPath, APIName)

        if APIName in self.getRepositoriesList():
            if projectObsName in self.__dicOBSLightRepositories[APIName].keys():
                return self.__dicOBSLightRepositories[APIName][projectObsName]

        self.createRepo(APIName, projectObsName)

        return self.__dicOBSLightRepositories[APIName][projectObsName]

    def createRepository(self, APIName, projectObsName):
        APIName = str(urlparse.urlparse(APIName)[1])
        pathDir = os.path.join(self.__repositoriesPath, APIName)

        if APIName in self.getRepositoriesList():
            if projectObsName in self.__dicOBSLightRepositories[APIName].keys():
                return 0

        self.__dicOBSLightRepositories[APIName] = {}

        repository = ObsLightRepository(pathDir, projectObsName)
        self.__dicOBSLightRepositories[APIName][projectObsName] = repository
        return 0

    def DeleteRepository(self, APIName, projectObsName):
        if APIName in self.getRepositoriesList():
            if projectObsName in self.__dicOBSLightRepositories[APIName].keys():
                self.__dicOBSLightRepositories[APIName][projectObsName].DeleteRepository()
                del self.__dicOBSLightRepositories[APIName][projectObsName]
                if len(self.__dicOBSLightRepositories[APIName]) == 0:
                    pathDir = os.path.join(self.__repositoriesPath, APIName)
                    command = "rm -r %s" % pathDir
                    return self.__subprocess(command=command)
                return 0
        return 0

    def createRepo(self, APIName, projectObsName):
        if APIName in self.getRepositoriesList():
            if projectObsName in self.__dicOBSLightRepositories[APIName].keys():
                return self.__dicOBSLightRepositories[APIName][projectObsName].createRepo()
        return 0


