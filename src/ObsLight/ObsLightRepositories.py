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

    def getRepositoriesList(self):
        '''
        
        '''
        return self.__dicOBSLightRepositories.keys()


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
        for projectName in os.listdir(self.__repositoriesPath):
            self.createRepo(projectName)

    def getRepository(self, projectName):
        pathDir = os.path.join(self.__repositoriesPath, self.__repositoriesPath)

        if projectName in self.__dicOBSLightRepositories.keys():
            return self.__dicOBSLightRepositories[projectName]

        self.createRepository(projectName)
        return self.__dicOBSLightRepositories[projectName]

    def createRepository(self, projectName):
        if projectName in self.__dicOBSLightRepositories.keys():
            return 0
        repository = ObsLightRepository(self.__repositoriesPath, projectName)
        self.__dicOBSLightRepositories[projectName] = repository
        return 0

    def DeleteRepository(self, projectName):
        if projectName in self.getRepositoriesList():
            self.__dicOBSLightRepositories[projectName].DeleteRepository()
            del self.__dicOBSLightRepositories[projectName]
            return 0
        return 0

    def createRepo(self, projectName):
        if projectName in self.getRepositoriesList():
            return self.__dicOBSLightRepositories[projectName].createRepo()
        return 0


