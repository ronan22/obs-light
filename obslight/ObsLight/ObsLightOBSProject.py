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
from ObsLightBuilderProject import ObsLightBuilderProject

import os
import shlex
import shutil
import subprocess
import urllib

from ObsLightUtils import getFilteredFileList, isASpecFile, levenshtein
from ObsLightPackages import ObsLightPackages
from ObsLightChRoot import ObsLightChRoot
#import ObsLightManager
import ObsLightErr
from ObsLightSubprocess import SubprocessCrt
from ObsLightObject import ObsLightObject
import ObsLightOsc

import ObsLightConfig

import ObsLightGitManager
from ObsLightSpec import getSpecTagValue

class ObsLightOBSProject(ObsLightBuilderProject):

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
        ObsLightBuilderProject.__init__(self,
                                        obsLightRepositories,
                                        workingDirectory,
                                        projectLocalName=projectLocalName,
                                        projectArchitecture=projectArchitecture,
                                        fromSave=fromSave)

        self.__obsServers = obsServers


        self.__projectTitle = fromSave.get("title", "")
        self.__description = fromSave.get("description", description)

        self.__projectName = fromSave.get("projectObsName", projectObsName)


        self.__projectTarget = fromSave.get("projectTarget", projectTarget)

        self.__obsServer = fromSave.get("obsServer", obsServer)
        if not (self.__obsServer in self.__obsServers.getObsServerList()):
                    message = "WARNING: '%s' is not a defined OBS server " % self.__obsServer
                    self.logger.warn(message)
        #perhaps a trusted_prj must be had
        else:
            obsServer = self.__obsServers.getObsServer(name=self.__obsServer)
            obsServer.initConfigProject(projet=self.__projectName, repos=self.__projectTarget)

        self.__readOnly = fromSave.get("ro", obsServer.getProjectParameter(self.__projectName,
                                                                           "readonly"))

    def getProjectParameter(self, parameter=None):
        '''
        Get the value of a project parameter:
        the valid parameter is :
            projectLocalName
            projectObsName
            projectDirectory
            obsServer
            projectTarget
            projectArchitecture
            title
            description
        '''
        if parameter == "projectLocalName":
            return self.__projectLocalName
        elif parameter == "projectObsName":
            return self.__projectName
        elif parameter == "projectDirectory":
            return self.getDirectory()
        elif parameter == "obsServer":
            return self.__obsServer
        elif parameter == "projectTarget":
            return self.__projectTarget
        elif parameter == "projectArchitecture":
            return self.__projectArchitecture
        elif parameter == "title":
            return self.__projectTitle
        elif parameter == "description":
            return self.__description
        else:
            message = "parameter value is not valid for getProjectParameter"
            raise ObsLightErr.ObsLightProjectsError(message)

    def setProjectParameter(self, parameter=None, value=None):
        '''
        Return the value of a parameter of the project:
        Valid parameters are:
            projectTarget
            projectArchitecture
            title
            description
        '''
        if parameter == "projectTarget":
            self.__projectTarget = value
        elif parameter == "projectArchitecture":
            self.__projectArchitecture = value
        elif parameter == "title":
            self.__projectTitle = value
        elif parameter == "description":
            self.__description = value
        else:
            message = "parameter '%s' is not valid for setProjectParameter" % parameter
            raise ObsLightErr.ObsLightProjectsError(message)
        return 0

    def getDic(self):
        aDic = {}
        aDic["projectLocalName"] = self.__projectLocalName
        aDic["projectObsName"] = self.__projectName
        aDic["obsServer"] = self.__obsServer
        aDic["projectTarget"] = self.__projectTarget
        aDic["projectArchitecture"] = self.__projectArchitecture
        aDic["title"] = self.__projectTitle
        aDic["description"] = self.__description
        aDic["packages"] = self.__packages.getDic()
        aDic["chrootIsInit"] = self.__chrootIsInit
        aDic["ro"] = self.__readOnly
#        aDic["extraChrootPackages"] = self.__extraChrootPackages
        return aDic

    #--------------------------------------------------------------------------- OBS server
    def __getConfigPath(self):
        if self.__configPath is None:
            obsServer = self.__obsServers.getObsServer(self.__obsServer)
            self.__configPath = obsServer.saveProjectConfig(self.__projectName,
                                                            self.__projectTarget)

        return self.__configPath

    def getProjectObsName(self):
        return self.__projectName

    def getObsServer(self):
        return self.__obsServer

    def __refreshObsPackageRev(self, package):
        pkgObj = self.getPackage(package)
        if not pkgObj.isGitPackage:
            obsServer = self.__obsServers.getObsServer(self.__obsServer)
            rev = obsServer.getObsPackageRev(self.__projectName, package)
            if rev is not None:
                pkgObj.setPackageParameter("obsRev", rev)
            else:
                pkgObj.setPackageParameter("obsRev", "-1")
            return 0

    def refreshObsStatus(self, package=None):
        '''
        refresh the package status and rev with the state on OBS Server.
        '''
        def doRefreshObsStatus(obsServer, package):
            status = obsServer.getPackageStatus(project=self.__projectName,
                                                package=package,
                                                repo=self.__projectTarget,
                                                arch=self.__projectArchitecture)
            if status != None:
                self.__packages.getPackage(package).setPackageParameter(parameter="status",
                                                                        value=status)
            return self.__refreshObsPackageRev(package=package)


        pkgObj = self.getPackage(package)
        if not pkgObj.isGitPackage:

            obsServer = self.__obsServers.getObsServer(self.__obsServer)

            if package is not None:
                return doRefreshObsStatus(obsServer, package)

            else:
                for pk in self.getPackageList():
                    doRefreshObsStatus(obsServer, pk)
                return 0
        else:
            return 0

#    def getChRootRepositories(self):
#        return self.__chroot.getChRootRepositories()

    def getDependencyRepositories(self):
        obsServer = self.__obsServers.getObsServer(self.__obsServer)
        return obsServer.getDependencyRepositories(self.__projectName,
                                                   self.__projectTarget,
                                                   self.__projectArchitecture)


    def getReposProject(self):
        '''
        Return the URL of the Repo of the Project
        '''
        return os.path.join(self.__obsServers.getObsServer(self.__obsServer).getRepo(),
                            self.__projectName.replace(":", ":/"),
                            self.__projectTarget)

    def __refreshObsDescription(self, name):
        """
        refrech package OBS Title and description
        """
        pkgObj = self.__packages.getPackage(name)

        #No Title or description for git package.
        if not pkgObj.isGitPackage:
            obsServer = self.__obsServers.getObsServer(self.__obsServer)
            packageTitle = obsServer.getPackageParameter(self.__projectName, name, "title")
            description = obsServer.getPackageParameter(self.__projectName, name, "description")

            pkgObj.setPackageParameter(parameter="title", value=packageTitle)
            pkgObj.setPackageParameter(parameter="description", value=description)

    def repairPackageDirectory(self, package):
        pkgObj = self.__packages.getPackage(name)

        if not pkgObj.isGitPackage:
            if package != None:
                return  self.getPackage(package).repairPackageDirectory()
            else:
                return None

    def getWebProjectPage(self):
        serverWeb = self.__obsServers.getObsServer(name=self.__obsServer).getUrlServerWeb()

        if serverWeb in (None, "None", ""):
            raise ObsLightErr.ObsLightProjectsError("No Web Server")
        res = urllib.basejoin(serverWeb , "project/show?project=" + self.__projectName)
        return res


    def getPackageList(self, onlyInstalled=True):
        '''
        Get the list of packages of this project.
        If `onlyInstalled` is True, get only those which have been imported locally.
        '''
        if not onlyInstalled :
            if self.__obsServer in self.__obsServers.getObsServerList():
                obsServer = self.__obsServers.getObsServer(self.__obsServer)
                res1 = set(obsServer.getObsProjectPackageList(projectObsName=self.__projectName))
                res2 = set(self.__packages.getPackagesList())
                res = list(res1.difference(res2))
                res.sort()
                return res
            else:
                return  None
        else:
            res = self.__packages.getPackagesList()
            return res


    def updatePackage(self, name):
        '''
        update a package of the projectLocalName.
        '''
        ObsLightProjectCore.updatePackage(name)

        pkgObj = self.__packages.getPackage(name)
        if not pkgObj.isGitPackage:
            server = self.__obsServers.getObsServer(self.__obsServer)
            self.refreshObsStatus(name)

        return 0
