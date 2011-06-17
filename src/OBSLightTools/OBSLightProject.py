'''
Created on 17 juin 2011

@author: rmartret
'''

#from Package import Package

class OBSLightProject(object):
    '''
    classdocs
    '''


    def __init__(self,projectName=None , projectDirectory=None,chrootDirectory=None,reposCacheDirectory=None):
        '''
        
        '''
        self.__projectName=projectName
        self.__projectDirectory=projectDirectory
        self.__chrootDirectory=chrootDirectory
        self.__reposCacheDirectory=reposCacheDirectory
        
        self.__listPackages={}
        self.__currentPackage=None
        
        self.__listDependentPackage={}
        
        self.__listProjectArchitecture=["i586", "armv7el"]
        self.__ProjectArchitecture=self.__listProjectArchitecture[0]
        
        self.__listImageType=["liveCD","liveUSB","loop","raw/KVM/QEMU","VMWare/vmdk","VirtualBox/vdi","Moorestown/mrstnand","jffs2","nand","ubi"]
        self.__imageType= self.__listImageType[0]
        
        self.__imageName=projectName
        
        self.__listOfSelectedRPM={}
        
        
    def getProjectName(self):
        """
        return the project name
        """
        return self.__projectName
    
    def setProjectName(self,name=None):
        """
        set the project name
        """
        self.__projectName=name
        
    def getProjectDirectory(self):
        """
        return the project directory
        """
        return self.__projectDirectory
    
    def setProjectDirectory(self,directory=None):
        """
        set the project directory
        """
        self.__projectDirectory=directory
        
    def getChrootDirectory(self):
        """
        return the chroot directory
        """
        return self.__chrootDirectory
    
    def setChrootDirectory(self,directory=None):
        """
        set  the chroot directory
        """
        self.__chrootDirectory=directory
        
    def getReposCacheDirectory(self):
        """
        return the Repos Cache Directory
        """
        return self.__reposCacheDirectory
    
    def setReposCacheDirectory(self,directory=None):
        """
        set the Repos Cache Directory
        """
        self.__reposCacheDirectory=directory
        
    def getListPackages(self):
        """
        return the list of packages
        """
        return self.__listPackages
        
    def addPackages(self,package):
        """
        add a packages
        """
        self.__listPackages.append(package)
        self.__currentPackage=None
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    
        
        