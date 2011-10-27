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

@author: ronan
'''

import ObsLightOsc
import ObsLightErr

class ObsServer(object):
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
        if fromSave != None:
            self.__isOBSConnected = fromSave["isOBSConnected"]
            self.__serverWeb = fromSave["serverWeb"]
            self.__serverAPI = fromSave["serverAPI"]
            self.__serverRepos = fromSave["serverRepos"]
            self.__aliases = fromSave["alias"]
            self.__user = fromSave["user"]
            self.__passw = fromSave["passw"]
        else:
            self.__isOBSConnected = False
            self.__serverWeb = serverWeb
            self.__serverAPI = serverAPI
            self.__serverRepos = serverRepo
            if alias == None or len(alias) < 1:
                self.__aliases = self.__serverAPI
            else:
                self.__aliases = alias
            self.__user = user
            self.__passw = passw
        
        ObsLightOsc.myObsLightOsc.initConf(api=self.__serverAPI,
                                           user=self.__user,
                                           passw=self.__passw,
                                           alias=self.__aliases)
        
    def getObsServerParameter(self,parameter=None):
        '''
        return the value of the parameter "parameter"
        the valid parameter is:
            obssOBSConnected
            serverWeb
            serverAPI
            serverRepos
            aliases
            user
            passw
        '''
        if parameter=="obssOBSConnected":
            return self.__isOBSConnected
        elif parameter=="serverWeb":
            return self.__serverWeb
        elif parameter=="serverAPI":
            return self.__serverAPI
        elif parameter=="serverRepos":
            return self.__serverRepos
        elif parameter=="aliases":
            return self.__aliases
        elif parameter=="user":
            return self.__user
        elif parameter=="passw":
            return self.__passw
        
    def setObsServerParameter(self,parameter=None,value=None):
        '''
        change the value of the parameter "parameter"
        the valid parameter is:
            obssOBSConnected
            serverWeb
            serverAPI
            serverRepos
            aliases
            user
            passw
        '''
        if value==None:
            raise ObsLightErr.ObsLightObsServers("value is not valid for setObsServerParameter")
        
        if parameter=="obssOBSConnected":
            self.__isOBSConnected=value
        elif parameter=="serverWeb":
            self.__serverWeb=value
        elif parameter=="serverAPI":
            self.__serverAPI=value
        elif parameter=="serverRepos":
            self.__serverRepos=value
        elif parameter=="aliases":
            self.__aliases=value
        elif parameter=="user":
            self.__user=value
        elif parameter=="passw":
            self.__passw=value
        else:
            raise ObsLightErr.ObsLightObsServers("parameter is not valid for setObsServerParameter")
        return None
        
        
        
        
        
        
        
    def initConfigProject(self,
                          projet=None,
                          repos=None):
        '''
        
        '''
        #if the repository is link to a listDepProject
        res = ObsLightOsc.myObsLightOsc.getDepProject(apiurl=self.__serverAPI,
                                                      projet=projet,
                                                      repos=repos)
        #the listDepProject must be trust(add to .oscrc )
        if res != None:
            ObsLightOsc.myObsLightOsc.trustRepos(api=self.__serverAPI,
                                                 listDepProject=res)
        
            
        
    def getDic(self):
        '''
        return a description of the object in a dictionary  
        '''
        aDic = {}
        aDic["isOBSConnected"] = self.__isOBSConnected = False
        aDic["serverWeb"] = self.__serverWeb
        aDic["serverAPI"] = self.__serverAPI
        aDic["serverRepos"] = self.__serverRepos
        aDic["aliases"] = self.__aliases
        aDic["user"] = self.__user
        aDic["passw"] = self.__passw
        return aDic
    
    def getName(self):
        '''
        return the Obs server name.
        '''
        return self.__aliases
    
    def getListPackage(self, projectLocalName=None):
        '''
        
        '''
        return ObsLightOsc.myObsLightOsc.getListPackage(obsServer=self.__serverAPI,
                                                        projectLocalName=projectLocalName)
    
    def checkoutPackage(self, projectLocalName=None, package=None, directory=None):
        '''
        
        '''
        ObsLightOsc.myObsLightOsc.checkoutPackage(obsServer=self.__serverAPI,
                                                  projectLocalName=projectLocalName,
                                                  package=package,
                                                  directory=directory)
        
    def getPackageStatus(self,
                         listDepProject=None,
                         package=None,
                         repos=None,
                         arch=None):
        '''
        
        '''
        return  ObsLightOsc.myObsLightOsc.getPackageStatus(obsServer=self.__serverAPI,
                                                           project=listDepProject,
                                                           package=package,
                                                           repos=repos,
                                                           arch=arch)
    
     
    def getRepo(self):
        '''
        
        '''
        return self.__serverRepos
    
    
    def getLocalProjectList(self):
        '''
        
        '''
        return  ObsLightOsc.myObsLightOsc.getLocalProjectList(obsServer=self.__serverAPI)
    
    def getTargetList(self, projectObsName=None):
        '''
        
        '''
        return ObsLightOsc.myObsLightOsc.getTargetList(obsServer=self.__serverAPI,
                                                       projectObsName=projectObsName)
    
    def getArchitectureList(self,
                            projectObsName=None,
                            projectTarget=None):
        '''
        
        '''
        return ObsLightOsc.myObsLightOsc.getArchitectureList(obsServer=self.__serverAPI ,
                                                              projectObsName=projectObsName,
                                                              projectTarget=projectTarget)
        
    
        
        
    
    
