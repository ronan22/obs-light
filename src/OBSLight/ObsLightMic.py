'''
Created on 4 oct. 2011

@author: meego
'''

import subprocess
import shlex

class ObsLightMic(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    
    
    def addPackageSourceInChRoot(self,chrootDir=None,package=None):
        '''
        
        '''
        self.initRpmDb(chrootDir)
        command="zypper --non-interactive si "+package
        self.execCommand(chrootDir=chrootDir,command=command)
        
    def addRepos(self,chrootDir=None,repos=None,alias=None):
        '''
        
        '''
        command="zypper ar "+repos+" "+alias
        self.execCommand(chrootDir=chrootDir,command=command)   
        command="zypper --no-gpg-checks --gpg-auto-import-keys ref"
        self.execCommand(chrootDir=chrootDir,command=command) 
        
    def buildRpm(self,chrootDir=None,specFile=None,arch=None):
        '''
        
        '''
        command="rpmbuild -bp --define '_srcdefattr (-,root,root)' "+"/root/rpmbuild/SPECS/"+specFile+"  --target="+arch
        self.execCommand(chrootDir=chrootDir,command=command)
        
    def goToChRoot(self,chrootDir=None):
        '''
        
        '''
        command="sudo mic-chroot "+chrootDir
        command=command.split()
        p=subprocess.call(command)
        
        
        
    def initGitWatch(self,chrootDir=None,path=None):
        '''
        
        '''
        command="cd "+path+"; git init; git add *"
        self.execCommand(chrootDir=chrootDir,command=command)
        
    def makePatch(self,chrootDir=None,path=None,patchFile=None):
        '''
        
        '''
        command="cd "+path+";git diff -p > "+patchFile
        self.execCommand(chrootDir=chrootDir,command=command)
        
    def getAddRemoveFiles(self,chrootDir=None,path=None,resultFile=None):
        '''
        
        '''
        command="cd "+path+";git status -u -s > "+resultFile
        self.execCommand(chrootDir=chrootDir,command=command)
        
    def initRpmDb(self,chrootDir=None):
        '''
        
        '''
        command="rpm --initdb"
        self.execCommand(chrootDir=chrootDir,command=command)
        command="rpm --rebuilddb"
        self.execCommand(chrootDir=chrootDir,command=command)

        
    def execCommand(self,chrootDir=None,command=None):
        '''
        
        '''
        aCommand="sudo mic-chroot "+chrootDir+" --execute=\""+command+"\""
        aCommand= shlex.split(aCommand)
        print "command",aCommand
        p=subprocess.call(aCommand, stdin=open("/dev/null", "r"), close_fds=True)
        
myObsLightMic=ObsLightMic()
        
        
        
