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


    def __init__(self, projectName=None, projectTitle=None, projectDirectory=None, chrootDirectory=None, obsserver=None ,projectTarget=None, description=None, projectArchitecture=None ,fromSave=None):
        '''
        Constructor
        '''
        if fromSave==None:
            self.__projectName=projectName
            self.__projectDirectory=projectDirectory
            self.__obsserver=obsserver
            self.__projectTarget=projectTarget
            self.__projectArchitecture=projectArchitecture
            self.__projectTitle=projectTitle
            self.__description=description
            
            if chrootDirectory==None:
                chrootDirectory=os.path.join(projectDirectory,"chroot")
            
            self.__chroot=ObsLightChRoot(chrootDirectory)
            self.__packages=ObsLightPackages()
            
        else:
            self.__projectName=fromSave["projectName"]
            self.__projectDirectory=fromSave["projectDirectory"]
            self.__obsserver=fromSave["obsserver"]
            self.__projectTarget=fromSave["projectTarget"]
            self.__projectArchitecture=fromSave["projectArchitecture"]
            self.__projectTitle=fromSave["projectTitle"]
            self.__description=fromSave["description"]
            
            self.__chroot=ObsLightChRoot(fromSave=fromSave["chroot"])
            self.__packages=ObsLightPackages(fromSave["packages"])
            
        if not os.path.isdir(self.__projectDirectory):
            os.makedirs(self.__projectDirectory)
            

    def getDic(self):
        '''
        
        '''
        aDic={}
        aDic["projectName"]=self.__projectName
        aDic["projectDirectory"]=self.__projectDirectory
        aDic["obsserver"]=self.__obsserver
        aDic["projectTarget"]=self.__projectTarget    
        aDic["projectArchitecture"]=self.__projectArchitecture
        aDic["projectTitle"]=self.__projectTitle
        aDic["description"]=self.__description
        
        aDic["packages"]=self.__packages.getDic()
        aDic["chroot"]=self.__chroot.getDic()
        return aDic
        
        
    def getListPackage(self,local=0):
        '''
        
        '''
        if local==0:
            return ObsLightManager.myObsLightManager.getListPackageListFromObsProject(obsserver=self.__obsserver,project=self.__projectName)
        else:
            return self.__packages.getListPackages()
        
    def addPackage(self,name=None):
        '''
        
        '''
        ObsLightManager.myObsLightManager.CheckoutPackage(obsserver=self.__obsserver,project=self.__projectName,package=name,directory=self.__projectDirectory)
        specFile=""
        listFile=[]
        packagePath=os.path.join(self.__projectDirectory,self.__projectName,name)
        for root, dirs, files in os.walk(packagePath):
            for f in files:
                if f.endswith(".spec"):
                    specFile=os.path.join(root,f)
            listFile=files
            break
        
        status=ObsLightManager.getManager().getPackageStatus(obsserver=self.__obsserver,project=self.__projectName,package=name,repos=self.__projectTarget,arch=self.__projectArchitecture)
        
        self.__packages.addPackage(name=name, specFile=specFile, listFile=listFile, status=status)
        
        
    def createChRoot(self):
        '''
         
        '''
        
        for pk in self.__packages.getListPackages():
            #if self.__packages.getPackageStatus(pk)=="succeeded":
            specPath=self.__packages.getSpecFile(pk)
            break
        
        projectDir=os.path.dirname(specPath)
        
        self.__chroot.createChRoot( projectDir=projectDir ,repos=self.__projectTarget,arch=self.__projectArchitecture,specPath=specPath)
        
        repos=os.path.join(ObsLightManager.getManager().getRepos(obsserver=self.__obsserver),self.__projectName.replace(":",":/"),self.__projectTarget)
        
        print "repos",repos
        alias=self.__projectName
        self.__chroot.addRepos(repos=repos  ,alias=alias )

    def goToChRoot(self):
        '''
        
        '''
        self.__chroot.goToChRoot()
        
    def addPackageSourceInChRoot(self,package=None):
        '''
        
        '''
        self.__chroot.addPackageSourceInChRoot(package=package)
        
        #self.__chroot.initGitWatch(self,path=None):
        
        
        