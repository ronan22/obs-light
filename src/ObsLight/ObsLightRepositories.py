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
import ObsLightConfig
import os
import pickle

import urlparse

from ObsLightRepository import ObsLightRepository

class ObsLightRepositories(object):
    '''
    classdocs
    '''
    def __init__(self, workingDirectory):
        '''
        Constructor
        '''
        self.__repositoriesPath = ObsLightConfig.getRepositriespath()
        self.__workingDirectory = workingDirectory
        pathDir = os.path.expanduser(self.__repositoriesPath)
        if not os.path.isdir(pathDir):
            os.makedirs(pathDir)

        self.__pathFile = os.path.join(self.__workingDirectory, "ObsLightRepositoriesConfig")

        self.__dicOBSLightRepositories = {}

    def getRepositoriesList(self):
        '''
        
        '''
#        self.__load()
        res = self.__dicOBSLightRepositories.keys()
        return res

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


    def getRepository(self, APIName, projectObsName):
        APIName = str(urlparse.urlparse(APIName)[1])
        pathDir = os.path.join(os.path.expanduser(self.__repositoriesPath), APIName)

        if APIName in self.getRepositoriesList():
            if projectObsName in self.__dicOBSLightRepositories[APIName].keys():
                return self.__dicOBSLightRepositories[APIName][projectObsName]
        else:
            self.__dicOBSLightRepositories[APIName] = {}

        repository = ObsLightRepository(pathDir, projectObsName)
        self.__dicOBSLightRepositories[APIName][projectObsName] = repository
        return repository







