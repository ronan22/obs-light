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
Created on 21 sept. 2012

@author: Ronan Le Martret 

'''
from ObsLightProjectCore import ObsLightProjectCore

class ObsLightProject(ObsLightProjectCore):

    def __init__(self,
                 obsServers,
                 obsLightRepositories,
                 workingDirectory,
                 projectObsName=None,
                 projectLocalName=None,
                 obsServer=None,
                 projectTarget=None,
                 projectArchitecture=None,
                 projectTitle="",
                 description="",
                 fromSave={}):
        ObsLightProjectCore.__init__(self,
                                     obsServers,
                                     obsLightRepositories,
                                     workingDirectory,
                                     projectObsName=projectObsName,
                                     projectLocalName=projectLocalName,
                                     obsServer=obsServer,
                                     projectTarget=projectTarget,
                                     projectArchitecture=projectArchitecture,
                                     projectTitle=projectTitle,
                                     description=description,
                                     fromSave=fromSave)

    def removeChRoot(self):
        for package in self.__packages.getPackagesList():
            pkgObj = self.getPackage(package)
            if pkgObj.isInstallInChroot():
                pkgObj.delFromChroot()

        res = self.__chroot.removeChRoot()
        self.__chrootIsInit = False
        return res

    def getChRoot(self):
        return self.__chroot

    def getChRootPath(self):
        '''
        Return the path of aChRoot of a project
        '''
        return self.__chroot.getDirectory()

    def isChRootInit(self):
        '''
        Return True if the ChRoot is init otherwise False.
        '''
        return self.__chrootIsInit

    def createChRoot(self):
        '''
        Initialize a chroot jail.
        Returns 0 on success. 
        '''
        return self.__initChRoot()

    def __initChRoot(self):
        apiurl = self.__obsServers.getObsServer(self.__obsServer).getAPI()
        retVal = self.__chroot.createChRoot(repos=self.__projectTarget,
                                            arch=self.__projectArchitecture,
                                            apiurl=apiurl,
                                            obsProject=self.__projectName)
        self.__chrootIsInit = retVal == 0
        return retVal

    def goToChRoot(self, package=None, useRootId=False, detach=False):
        if package != None:
            packagePath = self.__packages.getPackage(package).getPackageSourceDirectory()
            if packagePath != None:
                return self.__chroot.goToChRoot(path=packagePath,
                                                useRootId=useRootId,
                                                detach=detach,
                                                project=self.__projectLocalName)
            else:
                return self.__chroot.goToChRoot(detach=detach,
                                                project=self.__projectLocalName,
                                                useRootId=useRootId)
        else:
            return self.__chroot.goToChRoot(detach=detach,
                                            project=self.__projectLocalName,
                                            useRootId=useRootId)
