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

class ObsLightProject(object):
    '''
    classdocs
    '''

    def __init__(self,  projectLocalName=None,
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
        if fromSave==None:
            self.__projectLocalName=projectLocalName
            self.__projectObsName=projectObsName
            self.__projectDirectory=projectDirectory
            self.__obsServer=obsServer
            self.__projectTarget=projectTarget
            self.__projectArchitecture=projectArchitecture
            self.__projectTitle=projectTitle
            self.__description=description
            
            if chrootDirectory==None:
                chrootDirectory=os.path.join(projectDirectory,"chroot")
            
            self.__chroot=ObsLightChRoot(chrootDirectory=chrootDirectory,
                                         chrootDirTransfert=projectDirectory+"/chrootTransfert",
                                         dirTransfert="/chrootTransfert" )
            self.__packages=ObsLightPackages()
            
            #perhaps a trusted_prj must be had
            ObsLightManager.myObsLightManager.getObsServer(name=self.__obsServer).initConfigProject(projet=self.__projectObsName,
                                                                                                    repos=self.__projectTarget)

        else:
            self.__projectLocalName=fromSave["projectLocalName"]
            self.__projectObsName=fromSave["projectObsName"]
            self.__projectDirectory=fromSave["projectDirectory"]
            self.__obsServer=fromSave["obsServer"]
            self.__projectTarget=fromSave["projectTarget"]
            self.__projectArchitecture=fromSave["projectArchitecture"]
            self.__projectTitle=fromSave["projectTitle"]
            self.__description=fromSave["description"]
            
            self.__chroot=ObsLightChRoot(fromSave=fromSave["chroot"])
            self.__packages=ObsLightPackages(fromSave["packages"])
            
        if not os.path.isdir(self.__projectDirectory):
            os.makedirs(self.__projectDirectory)
        

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
        aDic={}
        aDic["projectLocalName"]=self.__projectLocalName
        aDic["projectObsName"]=self.__projectObsName
        aDic["projectDirectory"]=self.__projectDirectory
        aDic["obsServer"]=self.__obsServer
        aDic["projectTarget"]=self.__projectTarget    
        aDic["projectArchitecture"]=self.__projectArchitecture
        aDic["projectTitle"]=self.__projectTitle
        aDic["description"]=self.__description
        aDic["packages"]=self.__packages.getDic()
        aDic["chroot"]=self.__chroot.getDic()
        return aDic
        
    def getObsServer(self):
        '''
        
        '''
        return self.__obsServer
        
    def getListPackage(self,local=0):
        '''
        
        '''
        if local==0:
            return ObsLightManager.myObsLightManager.getListPackageFromObsProject(obsServer=self.__obsServer,
                                                                                  projectLocalName=self.__projectObsName)
        else:
            return self.__packages.getListPackages()
        
    def addPackage(self,name=None):
        '''
        add a package to the projectLocalName.
        '''
        ObsLightManager.myObsLightManager.CheckoutPackage(obsServer=self.__obsServer,
                                                          projectLocalName=self.__projectObsName,
                                                          package=name,
                                                          directory=self.__projectDirectory)
        specFile=""
        listFile=[]
        packagePath=os.path.join(self.__projectDirectory,self.__projectObsName,name)
        
        #Find the spec file
        #TO DO can be doing cleaner
        for root, dirs, files in os.walk(packagePath):
            for f in files:
                if f.endswith(".spec"):
                    specFile=os.path.join(root,f)
            listFile=files
            break
        
        #Find the status of the package, Don't use that now
        #status=ObsLightManager.getManager().getPackageStatus(obsserver=self.__obsServer,projectLocalName=self.__projectObsName,package=name,repos=self.__projectTarget,arch=self.__projectArchitecture)
        #self.__packages.addPackage(name=name, specFile=specFile, listFile=listFile, status=status)

        self.__packages.addPackage(name=name, 
                                   specFile=specFile, 
                                   listFile=listFile)
        
    def createChRoot(self):
        '''
         
        '''
        #I hope this will change, because we don't need to build a pakage to creat a chroot. 
        for pk in self.__packages.getListPackages():
            #if self.__packages.getPackageStatus(pk)=="succeeded":
            specPath=self.__packages.getSpecFile(pk)
            projectDir=self.__packages.getOscDirectory(pk)
            break

        self.__chroot.createChRoot( obsApi=self.__obsServer, 
                                    projectDir=projectDir ,
                                    repos=self.__projectTarget,
                                    arch=self.__projectArchitecture,
                                    specPath=specPath)
        self.addRepos()

    def addRepos(self,repos=None  ,alias=None, chroot=None):
        '''
        
        '''
        if chroot==None:
            __aChroot=self.__chroot
        else:
            __aChroot=chroot
        if repos==None:
            __aRepos=self.getReposProject()
        else:
            __aRepos=repos
        if alias==None:
            __anAlias=self.__projectObsName
        else:
            __anAlias=alias
            
        __aChroot.addRepos(repos=__aRepos  ,alias=__anAlias )
        
        
    def getReposProject(self):
        '''
        
        '''
        return os.path.join(ObsLightManager.getManager().getRepos(obsServer=self.__obsServer),self.__projectObsName.replace(":",":/"),self.__projectTarget)

    def goToChRoot(self,package=None):
        '''
        
        '''
        if package!=None:
            self.__chroot.goToChRoot(path=self.__packages.getPackageDirectory(package=package))
        else:
            self.__chroot.goToChRoot()
        
    def addPackageSourceInChRoot(self,package=None):
        '''
        
        '''
        specFile=os.path.basename( self.__packages.getSpecFile(package))
        self.__chroot.addPackageSourceInChRoot(package=self.__packages.getPackage(package),
                                               specFile=specFile,
                                               arch=self.__projectArchitecture)

    def makePatch(self,package=None,patch=None):
        '''
        Create a patch
        '''
        self.__chroot.makePatch(package=self.__packages.getPackage(package),
                                patch=patch)
        

    def commitToObs(self,message=None,package=None):
        '''
        commit the package to the OBS server.
        '''
        
        self.__packages.getPackage(package).commitToObs(message=message)
    
    def addRemoveFileToTheProject(self,package=None):
        '''
        add new file and remove file to the project.
        '''
        self.__packages.getPackage(package).addRemoveFileToTheProject()        
        
        
    def getPackage(self,package=None):
        '''
        
        '''
        return  self.__packages.getPackage(package=package)
        
