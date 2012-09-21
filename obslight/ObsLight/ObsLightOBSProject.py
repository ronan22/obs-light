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

    #--------------------------------------------------------------------------- OBS server
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

