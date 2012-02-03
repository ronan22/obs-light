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

import ObsLightOsc
import ObsLightErr
import ObsLightTools

class ObsLightServer(object):
    '''
    classdocs
    '''

    def __init__(self,
                 serverWeb="",
                 serverAPI=None,
                 serverRepo="",
                 alias=None,
                 user=None,
                 passw=None,
                 fromSave=None):
        '''
        Create a reference to a OBS server
        '''
        self.__alias = None
        self.__serverRepo = None
        self.__isReachable = None

        if fromSave != None:
            if "isOBSConnected" in fromSave.keys():
                self.__isOBSConnected = fromSave["isOBSConnected"]
            if "serverWeb" in fromSave.keys():
                self.__serverWeb = fromSave["serverWeb"]
            if "serverAPI" in fromSave.keys():
                self.__serverAPI = fromSave["serverAPI"]
            if "serverRepo" in fromSave.keys():
                self.__serverRepo = fromSave["serverRepo"]
            if "alias" in fromSave.keys():
                self.__alias = fromSave["alias"]
            if "user" in fromSave.keys():
                self.__user = fromSave["user"]
            if "passw" in fromSave.keys():
                self.__passw = fromSave["passw"]
        else:
            self.__isOBSConnected = False
            self.__serverWeb = serverWeb
            self.__serverAPI = serverAPI
            self.__serverRepo = serverRepo

            self.__alias = alias

            self.__user = user
            self.__passw = passw

        if (self.__alias == None) or (len(self.__alias) < 1):
            self.__alias = self.__serverAPI

        ObsLightOsc.getObsLightOsc().initConf(api=self.__serverAPI,
                                              user=self.__user,
                                              passw=self.__passw,
                                              alias=self.__alias)

    def testServer(self):
        '''
        
        '''

        self.__isReachable = (self.testServerAPI() and
                             self.testServerRepo() and
                             self.testServerWeb())
        return self.__isReachable

    def testServerAPI(self):
        '''
        
        '''
        return ObsLightTools.testHost(host=self.__serverAPI)

    def testServerRepo(self):
        '''
        
        '''
        return ObsLightTools.testHost(host=self.__serverRepo)

    def testServerWeb(self):
        '''
        
        '''
        return ObsLightTools.testHost(host=self.__serverWeb)

    def isReachable(self):
        '''
        
        '''
        if self.__isReachable == None:
            self.__isReachable = self.testServer()
        return self.__isReachable

    def getObsProjectPackageList(self, projectObsName):
        '''
        
        '''

        return ObsLightOsc.getObsLightOsc().getListPackage(apiurl=self.__serverAPI,
                                                           projectLocalName=projectObsName)

    def getFilesListPackage(self,
                            projectObsName,
                            package):
        '''
         
        '''
        return ObsLightOsc.getObsLightOsc().getFilesListPackage(apiurl=self.__serverAPI,
                                                                projectObsName=projectObsName,
                                                                package=package)

    def getObsServerParameter(self, parameter=None):
        '''
        return the value of the parameter "parameter"
        the valid parameter is:
            isOBSConnected
            serverWeb
            serverAPI
            serverRepo
            alias
            user
            passw
        '''

        if parameter == "isOBSConnected":
            return self.__isOBSConnected
        elif parameter == "serverWeb":
            return self.__serverWeb
        elif parameter == "serverAPI":
            return self.__serverAPI
        elif parameter == "serverRepo":
            return self.__serverRepo
        elif parameter == "alias":
            return self.__alias
        elif parameter == "user":
            return self.__user
        elif parameter == "passw":
            return self.__passw

    def getProjectParameter(self, project, parameter):
        '''
        Get the value of a project parameter.
        Valid parameter are:
            title
            description
            remoteurl
            maintainer
            bugowner
            arch
            repository            
        '''
        if not parameter in ["title",
                             "description",
                             "remoteurl",
                             "maintainer",
                             "bugowner",
                             "arch",
                             "repository"]:
            raise ObsLightErr.ObsLightObsServers(parameter + " is not a parameter of a OBS project")

        if not project in self.getLocalProjectList(raw=True):
            raise ObsLightErr.ObsLightObsServers("Can't return the project parameter,\n '" + project + "' is not a project on obs '" + self.__serverAPI + "'")

        return ObsLightOsc.getObsLightOsc().getProjectParameter(projectObsName=project,
                                                                apiurl=self.__serverAPI,
                                                                parameter=parameter)

    def getPackageParameter(self, project, package, parameter):
        '''
        Get the value of a package parameter.
        Valid parameter are:
            title
            description
            url
            status       
            listFile    
        '''
        print "parameter", parameter

        if not parameter in ["title",
                             "description",
                             "url",
                             "status",
                             "listFile"]:
            raise ObsLightErr.ObsLightObsServers(parameter + " is not a parameter of a OBS package")

        if not project in self.getLocalProjectList(raw=True):
            raise ObsLightErr.ObsLightObsServers("Can't return the package parameter,\n '" + project + "' is not a project on obs '" + self.__serverAPI + "'")

        if not package in self.getObsProjectPackageList(projectObsName=project):
            raise ObsLightErr.ObsLightObsServers("Can't return the package parameter,\n '" + project + "' is not a package of project '" + project + "' on obs '" + self.__serverAPI + "'")

        if parameter in ["title",
                         "description",
                         "url"]:
            return ObsLightOsc.getObsLightOsc().getPackageMetaParameter(projectObsName=project,
                                                                package=package,
                                                                apiurl=self.__serverAPI,
                                                                parameter=parameter)
        elif parameter in ["listFile"]:
            return ObsLightOsc.getObsLightOsc().getPackageParameter(projectObsName=project,
                                                                    package=package,
                                                                    apiurl=self.__serverAPI,
                                                                    parameter=parameter)


    def getObsPackageRev(self,
                         projectObsName,
                         package):
        '''
        
        '''
        return ObsLightOsc.getObsLightOsc().getObsPackageRev(apiurl=self.__serverAPI,
                                                             projectObsName=projectObsName,
                                                             package=package)

    def getOscPackageRev(self, workingdir):
        '''
        
        '''
        return ObsLightOsc.getObsLightOsc().getOscPackageRev(workingdir=workingdir)

    def setObsServerParameter(self, parameter=None, value=None):
        '''
        change the value of the parameter "parameter"
        the valid parameter is:
            obssOBSConnected
            serverWeb
            serverAPI
            serverRepo
            alias
            user
            passw
        '''
        if value == None:
            raise ObsLightErr.ObsLightObsServers("value is not valid for setObsServerParameter")
        if parameter == "isOBSConnected":
            self.__isOBSConnected = value
        elif parameter == "serverWeb":
            self.__serverWeb = value
        elif parameter == "serverAPI":
            ObsLightOsc.getObsLightOsc().changeAPI(api=self.__serverAPI,
                                                   newApi=value)
            self.__serverAPI = value
        elif parameter == "serverRepo":
            self.__serverRepo = value
        elif parameter == "alias":
            self.__alias = value
        elif parameter == "user":
            ObsLightOsc.getObsLightOsc().changeUser(api=self.__serverAPI,
                                                    user=value)
            self.__user = value
        elif parameter == "passw":
            ObsLightOsc.getObsLightOsc().changePassw(api=self.__serverAPI,
                                                     passw=value)
            self.__passw = value
        else:
            raise ObsLightErr.ObsLightObsServers("parameter is not valid for setObsServerParameter")
        return None

    def initConfigProject(self, projet, repos):
        '''
        
        '''
        #if the repository is link to a listDepProject
        res = ObsLightOsc.getObsLightOsc().getDepProject(apiurl=self.__serverAPI,
                                                         projet=projet,
                                                         repos=repos)
        #the listDepProject must be trust(add to .oscrc )
        if res != None:
            ObsLightOsc.getObsLightOsc().trustRepos(api=self.__serverAPI,
                                                    listDepProject=res)
            for aprojet in res.keys():
                if (aprojet != projet) or (res[aprojet] != repos):
                    self.initConfigProject(projet=aprojet,
                                           repos=res[aprojet])

    def getDic(self):
        '''
        return a description of the object in a dictionary  
        '''
        aDic = {}
        aDic["isOBSConnected"] = self.__isOBSConnected = False
        aDic["serverWeb"] = self.__serverWeb
        aDic["serverAPI"] = self.__serverAPI
        aDic["serverRepo"] = self.__serverRepo
        aDic["alias"] = self.__alias
        aDic["user"] = self.__user
        aDic["passw"] = self.__passw
        return aDic

    def getName(self):
        '''
        return the OBS server name.
        '''
        return self.__alias

    def getListPackage(self, projectLocalName=None):
        '''
        
        '''
        return ObsLightOsc.getObsLightOsc().getListPackage(apiurl=self.__serverAPI,
                                                        projectLocalName=projectLocalName)

    def checkoutPackage(self, projectObsName=None, package=None, directory=None):
        '''
        
        '''
        ObsLightOsc.getObsLightOsc().checkoutPackage(obsServer=self.__serverAPI,
                                                  projectObsName=projectObsName,
                                                  package=package,
                                                  directory=directory)

    def getPackageStatus(self,
                         project=None,
                         package=None,
                         repo=None,
                         arch=None):
        '''
        
        '''
        return  ObsLightOsc.getObsLightOsc().getPackageStatus(obsServer=self.__serverAPI,
                                                           project=project,
                                                           package=package,
                                                           repo=repo,
                                                           arch=arch)


    def getRepo(self):
        '''
        
        '''
        if self.__serverRepo != None:
            return self.__serverRepo
        else:
            raise ObsLightErr.ObsLightObsServers("In " + self.__alias + " there is no repo")


    def getLocalProjectList(self,
                            maintainer=False,
                            bugowner=False,
                            arch=None,
                            remoteurl=False,
                            raw=False):
        '''
        
        '''
        if raw == False:
            aBugowner = None
            if bugowner == True:
                aBugowner = self.__user

            aMaintainer = None
            if maintainer == True:
                aMaintainer = self.__user

            return  ObsLightOsc.getObsLightOsc().getLocalProjectListFilter(obsServer=self.__serverAPI,
                                                                             maintainer=aMaintainer,
                                                                             bugowner=aBugowner,
                                                                             arch=arch,
                                                                             remoteurl=remoteurl)
        else:
            return  ObsLightOsc.getObsLightOsc().getLocalProjectList(obsServer=self.__serverAPI)

    def getTargetList(self, projectObsName=None):
        '''
        
        '''
        return ObsLightOsc.getObsLightOsc().getTargetList(obsServer=self.__serverAPI,
                                                       projectObsName=projectObsName)

    def getArchitectureList(self,
                            projectObsName=None,
                            projectTarget=None):
        '''
        
        '''
        return ObsLightOsc.getObsLightOsc().getArchitectureList(obsServer=self.__serverAPI ,
                                                             projectObsName=projectObsName,
                                                             projectTarget=projectTarget)



    def getUrlServerWeb(self):
        '''
        
        '''
        return self.__serverWeb

    def getProjectTitle(self, projectObsName):
        '''
        
        '''
        return ObsLightOsc.getObsLightOsc().getProjectParameter(projectObsName=projectObsName,
                                                                apiurl=self.__serverAPI,
                                                                parameter="title")

    def getProjectDescription(self, projectObsName):
        '''
        
        '''
        return ObsLightOsc.getObsLightOsc().getProjectParameter(projectObsName=projectObsName,
                                                                apiurl=self.__serverAPI,
                                                                parameter="description")

    def getPackageTitle(self, projectObsName, package):
        '''
        
        '''
        return ObsLightOsc.getObsLightOsc().getPackageParameter(projectObsName=projectObsName,
                                                                package=package,
                                                                apiurl=self.__serverAPI,
                                                                parameter="title")

    def getPackageDescription(self, projectObsName, package):
        '''
        
        '''
        return ObsLightOsc.getObsLightOsc().getPackageParameter(projectObsName=projectObsName,
                                                                package=package,
                                                                apiurl=self.__serverAPI,
                                                                parameter="description")


