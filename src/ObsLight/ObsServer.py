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
        self.__alias = None
        self.__serverRepo=None
        
        if fromSave != None:
            if "isOBSConnected" in fromSave.keys():self.__isOBSConnected = fromSave["isOBSConnected"]
            if "serverWeb" in fromSave.keys():self.__serverWeb = fromSave["serverWeb"]
            if "serverAPI" in fromSave.keys():self.__serverAPI = fromSave["serverAPI"]
            if "serverRepo" in fromSave.keys():self.__serverRepo = fromSave["serverRepo"]
            if "alias" in fromSave.keys():self.__alias = fromSave["alias"]
            if "user" in fromSave.keys():self.__user = fromSave["user"]
            if "passw" in fromSave.keys():self.__passw = fromSave["passw"]

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
        

    def getObsServerParameter(self,parameter=None):
        '''
        return the value of the parameter "parameter"
        the valid parameter is:
            obssOBSConnected
            serverWeb
            serverAPI
            serverRepo
            alias
            user
            passw
        '''

        if parameter=="obssOBSConnected":
            return self.__isOBSConnected
        elif parameter=="serverWeb":
            return self.__serverWeb
        elif parameter=="serverAPI":
            return self.__serverAPI
        elif parameter=="serverRepo":
            return self.__serverRepo
        elif parameter=="aliases":
            return self.__alias
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
            serverRepo
            alias
            user
            passw
        '''
        if value==None:
            raise ObsLightErr.ObsLightObsServers("value is not valid for setObsServerParameter")

        if parameter=="isOBSConnected":
            self.__isOBSConnected=value
        elif parameter=="serverWeb":
            self.__serverWeb=value
        elif parameter=="serverAPI":
            self.__serverAPI=value
        elif parameter=="serverRepo":
            self.__serverRepo=value
        elif parameter=="alias":
            self.__alias=value
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
        res = ObsLightOsc.getObsLightOsc().getDepProject(apiurl=self.__serverAPI,
                                                      projet=projet,
                                                      repos=repos)
        #the listDepProject must be trust(add to .oscrc )
        if res != None:
            ObsLightOsc.getObsLightOsc().trustRepos(api=self.__serverAPI,
                                                 listDepProject=res)
        
            
        
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
        return ObsLightOsc.getObsLightOsc().getListPackage(obsServer=self.__serverAPI,
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
                         repos=None,
                         arch=None):
        '''
        
        '''
        return  ObsLightOsc.getObsLightOsc().getPackageStatus(obsServer=self.__serverAPI,
                                                           project=project,
                                                           package=package,
                                                           repos=repos,
                                                           arch=arch)
    
     
    def getRepo(self):
        '''
        
        '''
        if self.__serverRepo!=None:
            return self.__serverRepo
        else:
            raise ObsLightErr.ObsLightObsServers("In "+self.__alias+" there is no repo")
    
    
    def getLocalProjectList(self):
        '''
        
        '''
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
    
