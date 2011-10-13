'''
Created on 30 sept. 2011

@author: meego
'''

import os

import ObsLightOsc
import ObsLightMic 
import subprocess
import shlex

import shutil

class ObsLightChRoot(object):
    '''
    classdocs
    '''


    def __init__(self,chrootDirectory=None,chrootDirTransfert=None,dirTransfert=None,fromSave=None):
        '''
        Constructor
        '''
        if fromSave==None:
            self.__chrootDirectory=chrootDirectory
            self.__chrootrpmbuildDirectory="/root/rpmbuild"
            self.__chrootDirTransfert=chrootDirTransfert
            self.__dirTransfert=dirTransfert
        else:
            self.__chrootDirectory=fromSave["chrootDirectory"]
            self.__chrootrpmbuildDirectory=fromSave["rpmbuildDirectory"]
            self.__chrootDirTransfert=fromSave["chrootDirTransfert"]
            self.__dirTransfert=fromSave["dirTransfert"]
        self.initChRoot()
        
    def initChRoot(self):
        '''
        
        '''
        if not os.path.isdir(self.__chrootDirectory):
            os.makedirs(self.__chrootDirectory)
            command="sudo chown root:root "+self.__chrootDirectory
            command=command.split()
            subprocess.call(command,stdin=open("/dev/null", "r"), close_fds=True)
            
        if not os.path.isdir(self.__chrootDirTransfert):
            os.makedirs(self.__chrootDirTransfert)


    def getDic(self):
        '''
        
        '''
        saveconfigPackages={}    
        saveconfigPackages["chrootDirectory"]=self.__chrootDirectory
        saveconfigPackages["rpmbuildDirectory"]=self.__chrootrpmbuildDirectory
        saveconfigPackages["chrootDirTransfert"]=self.__chrootDirTransfert
        saveconfigPackages["dirTransfert"]=self.__dirTransfert
        return saveconfigPackages
    
    
    def createChRoot(self, projectDir=None ,repos=None,arch=None,specPath=None):
        '''
        
        '''
        ObsLightOsc.myObsLightOsc.createChRoot( chrootDir=self.__chrootDirectory,projectDir=projectDir ,repos=repos,arch=arch,specPath=specPath)

        subprocess.call(["sudo","chown","root:users",self.__chrootDirectory])
        subprocess.call(["sudo","chown","root:users",self.__chrootDirectory+"/root"])
        subprocess.call(["sudo","chown","root:users",self.__chrootDirectory+"/etc"])
        subprocess.call(["sudo","chmod","g+rw",self.__chrootDirectory])
        subprocess.call(["sudo","chmod","g+r",self.__chrootDirectory+"/root"])
        subprocess.call(["sudo","chmod","g+rw",self.__chrootDirectory+"/etc"])
                
        self.prepareChroot(self.__chrootDirectory)

        
    
    def __findPackageDirectory(self,package=None):
        '''
        
        '''
        pathBuild=self.__chrootDirectory+"/"+ self.__chrootrpmbuildDirectory+"/"+ "BUILD"
        #Find the Package Directory
        for  packageDirectory in os.listdir(pathBuild):
            res=packageDirectory
            if "-" in packageDirectory:
                packageDirectory=packageDirectory[:packageDirectory.rindex("-")]
                
            
            if package==packageDirectory:
                return self.__chrootrpmbuildDirectory+"/BUILD/"+res
        return None

        
    
    def addPackageSourceInChRoot(self,package=None,specFile=None,arch=None):
        '''
        
        '''
        packageName=package.getName()
        command=[]
        command.append("zypper --non-interactive si "+packageName)
        
        self.execCommand(command=command)
        
        aspecFile=self.__chrootrpmbuildDirectory+"/SPECS/"+specFile
        self.buildPrepRpm(chrootDir=self.__chrootDirectory,specFile=aspecFile,arch=arch)
        
        #find the directory to watch
        packageDirectory=self.__findPackageDirectory(package=packageName)
        package.setDirectoryBuild(packageDirectory)
        self.initGitWatch(path=packageDirectory)
        


    def execCommand(self,command=None):
        '''
        
        '''
        if  not ObsLightMic.myObsLightMic.isInit():
            ObsLightMic.myObsLightMic.initChroot(chrootDirectory=self.__chrootDirectory,chrootTransfertDirectory=self.__chrootDirTransfert,transfertDirectory=self.__dirTransfert)    
            
        pathScript=self.__chrootDirTransfert+"/runMe.sh"
        f=open(pathScript,'w')
        f.write("#!/bin/sh\n")
        f.write("# Created by obslight\n")
        for c in command:
            f.write(c+"\n") 
        f.close()
        
        os.chmod(pathScript, 0654)
        
        aCommand="sudo chroot "+self.__chrootDirectory+" "+self.__dirTransfert+"/runMe.sh"
        aCommand= shlex.split(aCommand)
        print "aCommand",aCommand
        subprocess.call(aCommand,stdin=open(os.devnull, 'rw') )

    def addRepos(self,repos=None,alias=None):
        '''
        
        '''
        command=[]
        command.append("zypper ar "+repos+" "+alias)
        command.append("zypper --no-gpg-checks --gpg-auto-import-keys ref")
        self.execCommand(command=command) 
        
    def buildPrepRpm(self,chrootDir=None,specFile=None,arch=None):
        '''
        
        '''
        command=[]
        command.append("rpmbuild -bp --define '_srcdefattr (-,root,root)' "+specFile+"  --target="+arch+" < /dev/null")
        self.execCommand(command=command)
        
    def goToChRoot(self,chrootDir=None,path=None):
        '''
        
        '''
        if  not ObsLightMic.myObsLightMic.isInit():
            ObsLightMic.myObsLightMic.initChroot(chrootDirectory=self.__chrootDirectory,chrootTransfertDirectory=self.__chrootDirTransfert,transfertDirectory=self.__dirTransfert)
        
        pathScript=self.__chrootDirTransfert+"/runMe.sh"
        f=open(pathScript,'w')
        f.write("#!/bin/sh\n")
        f.write("#Write by obslight\n")
        if path!=None:
            f.write("cd "+path+"\n")
        f.write("exec bash\n") 
        f.close()
        
        os.chmod(pathScript, 0654)
        
        command="sudo chroot "+self.__chrootDirectory+" "+self.__dirTransfert+"/runMe.sh"
        command= shlex.split(command)
        
        print "command",command
        subprocess.call(command )
        
        
    def initGitWatch(self,path=None):
        '''
        
        '''
        command=[]
        command.append("git init "+path)
        command.append("git --work-tree="+path+" --git-dir="+path+"/.git add "+path+"/\*")
        command.append("git --git-dir="+path+"/.git commit -m \"first commit\"")
        self.execCommand(command=command)
        
        
    def makePatch(self,package=None,patch=None):
        '''
        
        '''
        patchFile=patch
        pathPackage=package.getPackageDirectory()
        pathOscPackage=package.getOscDirectory()
        command=[]
        command.append("git --git-dir="+pathPackage+"/.git --work-tree="+pathPackage+"diff -p > "+self.__dirTransfert+"/"+patchFile)
        self.execCommand(command=command)
        shutil.copy(self.__chrootDirTransfert+"/"+patchFile, pathOscPackage+"/"+patch)
        package.addPatch(file=patch)
        
        
        
        
    def getAddRemoveFiles(self,chrootDir=None,path=None,resultFile=None):
        '''
        
        '''

        command=[]
        command.append("git --git-dir="+path+"/.git status -u -s > "+resultFile)
        self.execCommand(command=command)
        
    def prepareChroot(self, chrootDir):
        '''
        Prepares the chroot :
        - replaces some binaries by their ARM equivalent (in case chroot is ARM)
        - configures zypper and rpm for ARM
        - rebuilds rpm database
        '''
        command=[]

        if ObsLightMic.myObsLightMic.isArmArch(chrootDir):
            # If rpm and rpmbuild binaries are not ARM, replace by ARM versions
            command.append('[ -z "$(file /bin/rpm | grep ARM)" -a -f /bin/rpm.orig-arm ]'
                + ' && cp /bin/rpm /bin/rpm.x86 && cp /bin/rpm.orig-arm /bin/rpm')
            command.append('[ -z "$(file /bin/rpmbuild | grep ARM)" -a -f /bin/rpmbuild.orig-arm ]'
                + ' && cp /bin/rpm /bin/rpmbuild.x86 && cp /bin/rpmbuild.orig-arm /bin/rpm')
            # Remove the old (broken ?) rpm database
            command.append('rm -f /var/lib/rpm/__db*')
            # Force zypper and rpm to use armv7hl architecture
            command.append("echo 'arch = armv7hl' >> /etc/zypp/zypp.conf")
            command.append("echo -n 'armv7hl-meego-linux' > /etc/rpm/platform")
            
        
        command.append("rpm --initdb") 
        command.append("rpm --rebuilddb")   
        self.execCommand(command=command)


        
        


