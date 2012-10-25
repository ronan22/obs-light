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
from ObsLightProjectCore import ObsLightProjectCore

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

import tempfile

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

        self.__projectName = fromSave.get("projectObsName", projectObsName)

        ObsLightBuilderProject.__init__(self,
                                        obsLightRepositories,
                                        workingDirectory,
                                        projectLocalName=projectLocalName,
                                        projectArchitecture=projectArchitecture,
                                        fromSave=fromSave)

        self.setProjectType('OBS')
        self.__obsServers = obsServers

        self.__projectTitle = fromSave.get("title", "")
        self.__description = fromSave.get("description", description)

        self.__projectTarget = fromSave.get("projectTarget", projectTarget)

        self.__obsServer = fromSave.get("obsServer", obsServer)
        if not (self.__obsServer in self.__obsServers.getObsServerList()):
            message = "WARNING: '%s' is not a defined OBS server " % self.__obsServer
            self.logger.warn(message)
        #perhaps a trusted_prj must be had
        else:
            obsServer = self.__obsServers.getObsServer(name=self.__obsServer)
            obsServer.initConfigProject(projet=self.__projectName, repos=self.__projectTarget)

        if self.isReadOnly():
            self.setReadOnly(fromSave.get("ro", obsServer.getProjectParameter(self.__projectName,
                                                                              "readonly")))


    def getProjectParameter(self, parameter=None):
        '''
        Get the value of a project parameter:
        the valid parameter is :
            projectObsName
            obsServer
            projectTarget
            title
            description
        '''
        if parameter == "projectObsName":
            return self.__projectName
        if parameter == "obsServer":
            return self.__obsServer
        elif parameter == "projectTarget":
            return self.__projectTarget
        if parameter == "title":
            return self.__projectTitle
        elif parameter == "description":
            return self.__description
        else:
            return ObsLightBuilderProject.getProjectParameter(self, parameter)

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
            ObsLightBuilderProject.setProjectParameter(self, parameter, value)
        return 0

    def getDic(self):
        aDic = ObsLightBuilderProject.getDic(self)
        aDic["projectObsName"] = self.__projectName
        aDic["obsServer"] = self.__obsServer
        aDic["projectTarget"] = self.__projectTarget
        aDic["title"] = self.__projectTitle
        aDic["description"] = self.__description
#        aDic["extraChrootPackages"] = self.__extraChrootPackages
        return aDic

    #--------------------------------------------------------------------------- OBS server
    def getBuildConfigPath(self):
        if ObsLightBuilderProject.getBuildConfigPath(self) is None:
            obsServer = self.__obsServers.getObsServer(self.__obsServer)
            self.setBuildConfigPath(obsServer.saveProjectConfig(self.__projectName,
                                                                 self.__projectTarget))

        return ObsLightBuilderProject.getBuildConfigPath(self)

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
        return 0
#        def doRefreshObsStatus(obsServer, package):
#            status = obsServer.getPackageStatus(project=self.__projectName,
#                                                package=package,
#                                                repo=self.__projectTarget,
#                                                arch=self.getArchitecture())
##            if status != None:
##                self._getPackages().getPackage(package).setPackageParameter(parameter="status",
##                                                                            value=status)
#            return self.__refreshObsPackageRev(package=package)
#
#
#        pkgObj = self.getPackage(package)
#        if not pkgObj.isGitPackage:
#
#            obsServer = self.__obsServers.getObsServer(self.__obsServer)
#
#            if package is not None:
#                return doRefreshObsStatus(obsServer, package)
#
#            else:
#                for pk in self.getPackageList():
#                    doRefreshObsStatus(obsServer, pk)
#                return 0
#        else:
#            return 0

#    def getChRootRepositories(self):
#        return self.__chroot.getChRootRepositories()

    def getDependencyRepositories(self):
        obsServer = self.__obsServers.getObsServer(self.__obsServer)
        return obsServer.getDependencyRepositories(self.__projectName,
                                                   self.__projectTarget,
                                                   self.getArchitecture())


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
        pkgObj = self._getPackages().getPackage(name)

        #No Title or description for git package.
        if not pkgObj.isGitPackage:
            obsServer = self.__obsServers.getObsServer(self.__obsServer)
            packageTitle = obsServer.getPackageParameter(self.__projectName, name, "title")
            description = obsServer.getPackageParameter(self.__projectName, name, "description")

            pkgObj.setPackageParameter(parameter="title", value=packageTitle)
            pkgObj.setPackageParameter(parameter="description", value=description)

    def repairPackageDirectory(self, package):
        pkgObj = self._getPackages().getPackage(name)

        if not pkgObj.isGitPackage:
            if package != None:
                return  self.getPackage(package).repairPackageDirectory()
            else:
                return None

    def getServerWeb(self):
        return self.__obsServers.getObsServer(name=self.__obsServer).getUrlServerWeb()

    def getWebProjectPage(self):
        serverWeb = self.getServerWeb()

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
                res2 = set(self._getPackages().getPackagesList())
                res = list(res1.difference(res2))
                res.sort()
                return res
            else:
                return  None
        else:
            res = self._getPackages().getPackagesList()
            return res


    def updatePackage(self, name):
        '''
        update a package of the projectLocalName.
        '''
        ObsLightProjectCore.updatePackage(self, name)

        pkgObj = self._getPackages().getPackage(name)

        if not pkgObj.isGitPackage:
            server = self.__obsServers.getObsServer(self.__obsServer)
            self.refreshObsStatus(name)

        return 0

    def autoDisableExtraChrootPackages(self, packageName, specFileName):
        """Checks if extra packages are available, and enable/disable them accordingly"""
        obsServer = self.__obsServers.getObsServer(self.__obsServer)
        extraPackages = set(self.__extraChrootPackages)
        gotError = True
        while(gotError and len(extraPackages) > 0):
            try:
                buildInfoCli = obsServer.getPackageBuildRequires(self.__projectName,
                                                                 self.__projectTarget ,
                                                                 self.getArchitecture(),
                                                                 specFileName,
                                                                 list(extraPackages))
                gotError = False
            except ObsLightErr.ObsLightOscErr as e:
                gotError = True
                toBeRemoved = set()
                for p in extraPackages:
                    if e.msg.find(p) >= 0:
                        toBeRemoved.add(p)

                extraPackages.difference_update(toBeRemoved)
        for p in self.__extraChrootPackages.keys():
            self.__extraChrootPackages[p] = p in extraPackages

    def createRpmList(self, specFile):
        """
        Create a rpmlist file and return the path.
        """

        obsServer = self.__obsServers.getObsServer(self.__obsServer)
        extraPkg = self.getExtraChrootPackagesList()
        buildInfoCli = obsServer.getPackageBuildRequires(self.__projectName,
                                                         self.__projectTarget ,
                                                         self.getArchitecture(),
                                                         specFile,
                                                         extraPkg)


        res, dicoRpmName = self.__reOrderRpm(buildInfoCli, self.getTarget(), self.getBuildConfigPath())

        preinstall_list = buildInfoCli.preinstall_list
        vminstall_list = buildInfoCli.vminstall_list
        cbinstall_list = buildInfoCli.cbinstall_list
        cbpreinstall_list = buildInfoCli.cbpreinstall_list
        runscripts_list = buildInfoCli.runscripts_list

#        dicoRpmName = ObsLightCacheManager.checkCacheFile(dicoRpmName)

        rpmListFilePath = tempfile.mkstemp()
        f = open(rpmListFilePath[1], 'w')

#        print "rpmListFilePath[1]", rpmListFilePath[1]

        for package in res:
#            print "package", package, " dicoRpmName[package]", dicoRpmName[package]
            f.write(package + " " + dicoRpmName[package] + "\n")

        f.write("preinstall: " + " ".join(preinstall_list) + "\n")
        f.write("vminstall: " + " ".join(vminstall_list) + "\n")
        f.write("cbinstall: " + " ".join(cbinstall_list) + "\n")
        f.write("cbpreinstall: " + " ".join(cbpreinstall_list) + "\n")
        f.write("runscripts: " + " ".join(runscripts_list) + "\n")

        f.close()

        return rpmListFilePath[1]

    def __reOrderRpm(self, buildInfoCli, target, configPath):
        command = []
        cacheDir = "/tmp/reOrderDir"
        cacheRpmList = cacheDir + "/rpmList"
        cacheRpmLink = cacheDir + "/rpmLink"

        self._subprocess(command="rm -rf " + cacheRpmLink)
        self._subprocess(command="mkdir -p " + cacheRpmLink)

        f = open(cacheRpmList, 'w')
        listInput = []
        dicoRpmName = {}
        for i in buildInfoCli.deps:
            if not ((i in buildInfoCli.preinstall_list) or (i in buildInfoCli.vminstall_list)) :
                absPath = i.fullfilename
                pkgName = os.path.basename(absPath)
                if pkgName.endswith(".rpm"):
                    pkgName = pkgName[:-4]

                pkgName = pkgName[:pkgName.rfind("-")]
                pkgName = pkgName[:pkgName.rfind("-")]
                dicoRpmName[pkgName] = absPath
#                dicoRpmName[pkgName] = i
                f.write(pkgName + "\n")
                listInput.append(pkgName)
                command = "ln -sf " + absPath + " " + cacheRpmLink + "/" + pkgName + ".rpm"
                self._subprocess(command=command)
        # flush() does not necessarily write the file's data to disk. 
        # Use os.fsync(f.fileno()) to ensure this behavior.
        f.flush()
        os.fsync(f.fileno())
        f.close()
        dicopara = {}
        dicopara["buildDir"] = "/usr/lib/build"
        dicopara["cfgPth"] = configPath
        dicopara["tgt"] = target
        dicopara["RpmList"] = cacheRpmList
        dicopara["cacheRpmLink"] = cacheRpmLink
        command = "%(buildDir)s/order --dist %(cfgPth)s --archpath  %(tgt)s "
        command += "--configdir %(buildDir)s/configs --manifest %(RpmList)s  %(cacheRpmLink)s"
        command = command % dicopara

        listOrdered = self._subprocess(command=command, stdout=True)

        result = listOrdered.split()

#        # Build a dict of package -> path of RPM
#        for i in wantedPkgList:
#            absPath = i.fullfilename
#            pkgName = os.path.basename(absPath)
#            if pkgName.endswith(".rpm"):
#                pkgName = pkgName[:-4]
#            absPathDict[pkgName] = absPath

        return result, dicoRpmName

    def __getOscPackagesDefaultDirectory(self):
        '''
        Return the package Osc directory of the local project.
        '''
        return os.path.join(self.getDirectory(), self.__projectName)

    def createPackagePath(self, name, isGitPackage):
        if isGitPackage:
           return os.path.join(self.getGitPackagesDefaultDirectory(), name)
        else:
            return os.path.join(self.__getOscPackagesDefaultDirectory(), name)

    def commitPackageChange(self, message=None, package=None):
        '''
        commit the package to the OBS server or git.
        '''
        # test if package is a RW OBS package.
        pkgObj = self._getPackages().getPackage(package)

        if not pkgObj.isGitPackage:
            server = self.__obsServers.getObsServer(self.__obsServer)
            if server.getProjectParameter(self.__projectName, "readonly"):
                message = "Can't commit project you are not maintainer on project."
                raise ObsLightErr.ObsLightProjectsError(message)

        #Do a package commit
        pkgObj.commitPackageChange(message=message)

        if not pkgObj.isGitPackage:
            #check 
#            self.checkOscDirectoryStatus(package=package)
#            self.__refreshOscPackageLocalRev(package=package)
            self.refreshObsStatus(package=package)

        return 0
