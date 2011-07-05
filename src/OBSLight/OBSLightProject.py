'''
Created on 17 juin 2011

@author: rmartret
'''

#from Package import Package
import os
import subprocess


class OBSLightProject(object):
    '''
    classdocs
    '''


    def __init__(self,manager=None,name=None, directory=None, chrootDirectory=None , target=None , architecture=None,imageType=None):
        '''
        
        '''
        self.__manager=manager
        
        self.__projectName=name
        self.__projectDirectory=directory
        self.__chrootDirectory=chrootDirectory
        self.__reposCacheDirectory=None
        
        if not os.path.isdir(self.__projectDirectory):
            os.makedirs(self.__projectDirectory)
            
        if not os.path.isdir(self.__chrootDirectory):    
            os.makedirs(self.__chrootDirectory)
        
        
        self.__listPackages={}
        self.__currentPackage=None
        
        self.__listDependentPackage={}
        
        self.__aProjectTarget=target
        
        self.__listProjectArchitecture=["ia32", "armv7el"]
        if architecture==None:
            self.__ProjectArchitecture=self.__listProjectArchitecture[0]
        else:
            self.__ProjectArchitecture=architecture
        
            
        self.__listImageType=["liveCD","liveUSB","loop","raw/KVM/QEMU","VMWare/vmdk","VirtualBox/vdi","Moorestown/mrstnand","jffs2","nand","ubi"]
        
        if imageType==None:
            self.__imageType= self.__listImageType[0]
        else:
            self.__imageType=imageType
        
        self.__imageName=self.__projectName
        
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
    
    def getDirectory(self,directory=None):
        """
        set the project directory
        """
        return self.__projectDirectory
        
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
        


    def getTarget(self):
        """
        
        """
        return self.__aProjectTarget
    
    def getArchitecture(self):
        """
        
        """
        return self.__ProjectArchitecture
    
    def getProjectInfo(self):
        """
        
        """
        info=[]
        
        info.append("Name: "+str(self.__projectName))
        info.append("Directory: "+str(self.__projectDirectory))
        info.append("Chroot Directory: "+str(self.__chrootDirectory))
        info.append("List Packages: "+str(self.__listPackages.keys()))
        info.append("Dependent Package: "+str(self.__listDependentPackage.keys()))
        info.append("Target: "+str(self.__aProjectTarget))
        info.append("Architecture: "+str(self.__ProjectArchitecture))
        info.append("Image Type: "+str(self.__imageType))
        info.append("Image Name: "+str(self.__imageName))
        
        return info
        
    def __configRPMList(self,filePath):
        """
        
        """
        filePattern=open(filePath,'r')
        
        path=self.__projectDirectory+os.sep+"rpmlist.conf"
        fileProject=open(path,'w')
        
        for line in filePattern:
            
            if line.startswith("preinstall:")|line.startswith("vminstall:")|line.startswith("cbinstall:")|line.startswith("cbpreinstall:")|line.startswith("runscripts:"):
                fileProject.write(line)

            else:
                rpm=line.replace(" \n","")
                rpmPath=self.__manager.getRPMPath(architecture= self.__ProjectArchitecture, target=self.__aProjectTarget,rpm=rpm)
                
                tmpLine=rpm+" "+rpmPath+"\n"

                fileProject.write(tmpLine)
                

        filePattern.close()
        fileProject.close()
        
        return path
         
        
    def creatChroot(self):
        """
        
        """
        if self.__ProjectArchitecture=="ia32":
            arch="i586"
            rpmlist=self.__configRPMList("./OBSLight/installPattern/rpmlistPattern.i586")
        else:
            arch="armv8el"
            rpmlist=self.__configRPMList("./OBSLight/installPattern/rpmlistPattern.armv7hl")
        
        dist="./OBSLight/installPattern/_buildconfig-MeeGo"
        
        
        bashFile="./OBSLight/installPattern/buildOBSLightInit"
        root=self.__chrootDirectory
        
        command=("sudo "+bashFile+" --root="+root+" --rpmlist="+rpmlist+" --dist="+dist+" --arch="+arch)
        print "command",command
        
        command=command.split()
        
        p=subprocess.Popen(command , shell=False,stdout=subprocess.PIPE)
        p.wait()
        
        
        
        #print p.stdout.readlines()
        
    def addRPM( self,rpm=None, type=None ):
        
        if type=="src":
            arch="src"
        else:
            arch=self.__ProjectArchitecture
            
        print self.__manager.getRPMPath(architecture= arch, target=self.__aProjectTarget,rpm=rpm)
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    
        
        