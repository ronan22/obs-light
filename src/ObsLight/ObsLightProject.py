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
import os

from ObsLightPackages import ObsLightPackages
from ObsLightChRoot import ObsLightChRoot
import ObsLightManager
import ObsLightErr
from ObsLightSubprocess import SubprocessCrt

class ObsLightProject(object):
    '''
    classdocs
    '''

    def __init__(self, projectLocalName=None,
                        projectObsName=None,
                        projectTitle=None,
                        projectDirectory=None,
                        chrootDirectory=None,
                        obsServer=None ,
                        projectTarget=None,
                        description=None,
                        projectArchitecture=None ,
                        fromSave=None):
        '''
        Constructor
        '''
        self.__mySubprocessCrt = SubprocessCrt()
        
        if fromSave == None:
            self.__projectLocalName = projectLocalName
            self.__projectObsName = projectObsName
            self.__projectDirectory = projectDirectory
            self.__obsServer = obsServer
            self.__projectTarget = projectTarget
            self.__projectArchitecture = projectArchitecture
            self.__projectTitle = projectTitle
            self.__description = description
            
            if chrootDirectory == None:
                chrootDirectory = os.path.join(projectDirectory, "aChroot")
            
            self.__chroot = ObsLightChRoot(chrootDirectory=chrootDirectory,
                                         chrootDirTransfert=projectDirectory + "/chrootTransfert",
                                         dirTransfert="/chrootTransfert")
            self.__packages = ObsLightPackages()
            
            #perhaps a trusted_prj must be had
            ObsLightManager.getManager().getObsServer(name=self.__obsServer).initConfigProject(projet=self.__projectObsName,
                                                                                                    repos=self.__projectTarget)

        else:
            if "projectLocalName" in fromSave.keys():self.__projectLocalName = fromSave["projectLocalName"]
            if "projectObsName" in fromSave.keys():self.__projectObsName = fromSave["projectObsName"]
            if "projectDirectory" in fromSave.keys():self.__projectDirectory = fromSave["projectDirectory"]
            if "obsServer" in fromSave.keys():self.__obsServer = fromSave["obsServer"]
            if "projectTarget" in fromSave.keys():self.__projectTarget = fromSave["projectTarget"]
            if "projectArchitecture" in fromSave.keys():self.__projectArchitecture = fromSave["projectArchitecture"]
            if "projectTitle" in fromSave.keys():self.__projectTitle = fromSave["projectTitle"]
            if "description" in fromSave.keys():self.__description = fromSave["description"]
            
            if "aChroot" in fromSave.keys():self.__chroot = ObsLightChRoot(fromSave=fromSave["aChroot"])
            if "packages" in fromSave.keys():self.__packages = ObsLightPackages(fromSave["packages"])
            
        if not os.path.isdir(self.__projectDirectory):
            os.makedirs(self.__projectDirectory)
        
    def getProjectInfo(self,info=None):
        '''
        return the value  of the info of the project:
        the valide info is :
            projectLocalName
            projectObsName
            projectDirectory
            obsServer
            projectTarget
            "projectArchitecture
            projectTitle
            description
        '''
        if info=="projectLocalName":
            return self.__projectLocalName
        elif info=="projectObsName":
            return self.__projectObsName
        elif info=="projectDirectory":
            return self.__projectDirectory
        elif info=="obsServer":
            return self.__obsServer
        elif info=="projectTarget":
            return self.__projectTarget
        elif info=="projectArchitecture":
            return self.__projectArchitecture
        elif info=="projectTitle":
            return self.__projectTitle
        elif info=="description":
            return self.__description
        else:
            raise ObsLightErr.ObsLightProjectsError("info value is not valide for getProjectInfo")
        
    def setProjectparameter(self,parameter=None,value=None):
        '''
        return the value  of the parameter of the project:
        the valide parameter is :
            projectTarget
            projectArchitecture
            projectTitle
            description
        '''
        if parameter=="projectTarget":
            self.__projectTarget=value
        elif parameter=="projectArchitecture":
            self.__projectArchitecture=value
        elif parameter=="projectTitle":
            self.__projectTitle=value
        elif parameter=="description":
            self.__description=value
        else:
            raise ObsLightErr.ObsLightProjectsError("parameter value is not valide for getProjectInfo")
        
    def __subprocess(self, command=None, waitMess=False):
        '''
        
        '''
        return self.__mySubprocessCrt.execSubprocess(command=command, waitMess=waitMess)
        
    def removeProject(self):
        '''
        
        '''
        
        res=self.__chroot.removeChRoot()
        
        if res ==0:
            return self.__subprocess(command="sudo rm -r  " + self.__projectDirectory)
        else:
            raise ObsLightErr.ObsLightProjectsError("Error in removeProject, can't remove chroot")
        
        return 0

    def getProjectObsName(self):
        '''
        
        '''
        return self.__projectObsName

    def getChRoot(self):
        '''
        
        '''
        return self.__chroot

    def getDic(self):
        '''
        
        '''
        aDic = {}
        aDic["projectLocalName"] = self.__projectLocalName
        aDic["projectObsName"] = self.__projectObsName
        aDic["projectDirectory"] = self.__projectDirectory
        aDic["obsServer"] = self.__obsServer
        aDic["projectTarget"] = self.__projectTarget    
        aDic["projectArchitecture"] = self.__projectArchitecture
        aDic["projectTitle"] = self.__projectTitle
        aDic["description"] = self.__description
        aDic["packages"] = self.__packages.getDic()
        aDic["aChroot"] = self.__chroot.getDic()
        return aDic
        
    def getObsServer(self):
        '''
        
        '''
        return self.__obsServer
        
    def getListPackage(self, local=0):
        '''
        
        '''
        if local == 0:
            return ObsLightManager.getManager().getObsProjectPackageList(obsServer=self.__obsServer,
                                                                                  projectLocalName=self.__projectObsName)
        else:
            return self.__packages.getListPackages()
        
    def addPackage(self, name=None):
        '''
        add a package to the projectLocalName.
        '''
        ObsLightManager.getManager().checkoutPackage(obsServer=self.__obsServer,
                                                          projectLocalName=self.__projectObsName,
                                                          package=name,
                                                          directory=self.__projectDirectory)
        specFile = ""
        packagePath = os.path.join(self.__projectDirectory, self.__projectObsName, name)
        
        #Find the spec file
        listFile = os.listdir(packagePath)
        
        specFile=None
        yamlFile=None
        
        for f in listFile:
            if f.endswith(".spec"):
                specFile = os.path.join(packagePath, f)
            elif f.endswith(".yaml"):
                yamlFile = os.path.join(packagePath, f)
        #Find the status of the package, Don't use that now
        #status=ObsLightManager.getManager().getPackageStatus(obsserver=self.__obsServer,projectLocalName=self.__projectObsName,package=name,repos=self.__projectTarget,arch=self.__projectArchitecture)
        #self.__packages.addPackage(name=name, specFile=specFile, listFile=listFile, status=status)

        self.__packages.addPackage(name=name,
                                   specFile=specFile,
                                   yamlFile=yamlFile,
                                   listFile=listFile)
        
    def createChRoot(self):
        '''
         
        '''
        #I hope this will change, because we don't need to build a pakage to creat a chroot. 
        for pk in self.__packages.getListPackages():
            #if self.__packages.getPackageStatus(pk)=="succeeded":
            specPath = self.__packages.getSpecFile(pk)
            projectDir = self.__packages.getOscDirectory(pk)
            break

        self.__chroot.createChRoot(#obsApi=self.__obsServer,
                                    projectDir=projectDir ,
                                    repos=self.__projectTarget,
                                    arch=self.__projectArchitecture,
                                    specPath=specPath)
        self.addRepo()

    def addRepo(self,
                 repos=None,
                 alias=None,
                 chroot=None):
        '''
        
        '''
        if chroot == None:
            __aChroot = self.__chroot
        else:
            __aChroot = chroot
        if repos == None:
            __aRepos = self.getReposProject()
        else:
            __aRepos = repos
        if alias == None:
            __anAlias = self.__projectObsName
        else:
            __anAlias = alias
            
        __aChroot.addRepo(repos=__aRepos  , alias=__anAlias)
        
        
    def getReposProject(self):
        '''
        
        '''
        return os.path.join(ObsLightManager.getManager().getRepo(obsServer=self.__obsServer), self.__projectObsName.replace(":", ":/"), self.__projectTarget)

    def goToChRoot(self, package=None):
        '''
        
        '''
        if package != None:
            
            pathPackage = self.__packages.getPackageDirectory(package=package)
            if pathPackage != None:
                self.__chroot.goToChRoot(path=pathPackage)
            else:
                self.__chroot.goToChRoot()
        else:
            self.__chroot.goToChRoot()
        
    def addPackageSourceInChRoot(self, package=None):
        '''
         
        '''
        specFile = os.path.basename(self.__packages.getSpecFile(package))
        self.__chroot.addPackageSourceInChRoot(package=self.__packages.getPackage(package),
                                               specFile=specFile,
                                               repo=self.__projectObsName)

    def makePatch(self, package=None, patch=None):
        '''
        Create a patch
        '''
        self.__chroot.makePatch(package=self.__packages.getPackage(package),
                                patch=patch)
        

    def commitToObs(self, message=None, package=None):
        '''
        commit the package to the OBS server.
        '''
        
        self.__packages.getPackage(package).commitToObs(message=message)
    
    def addRemoveFileToTheProject(self, package=None):
        '''
        add new file and remove file to the project.
        '''
        self.__packages.getPackage(package).addRemoveFileToTheProject()        
        
        
    def getPackage(self, package=None):
        '''
        
        '''
        return  self.__packages.getPackage(package=package)
        
    def removePackage(self,package=None):
        '''
        
        '''
        return self.__packages.removePackage(package=package)
        
        
