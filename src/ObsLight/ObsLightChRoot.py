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
Created on 30 sept. 2011

@author: meego
'''

import os
import time
import platform
import shlex
import shutil
import subprocess

import ObsLightOsc
import ObsLightMic 

import ObsLightErr

class ObsLightChRoot(object):
    '''
    classdocs
    '''


    def __init__(self,  chrootDirectory=None,
                        chrootDirTransfert=None,
                        dirTransfert=None,
                        fromSave=None):

        '''
        Constructor
        '''
        if fromSave == None:
            self.__chrootDirectory = chrootDirectory
            self.__chrootrpmbuildDirectory = "/root/rpmbuild"
            self.__chrootDirTransfert = chrootDirTransfert
            self.__dirTransfert = dirTransfert
        else:
            self.__chrootDirectory = fromSave["chrootDirectory"]
            self.__chrootrpmbuildDirectory = fromSave["rpmbuildDirectory"]
            self.__chrootDirTransfert = fromSave["chrootDirTransfert"]
            self.__dirTransfert = fromSave["dirTransfert"]
        self.initChRoot()
        
    def initChRoot(self):
        '''
        
        '''
#        if not os.path.isdir(self.__chrootDirectory):
#            os.makedirs(self.__chrootDirectory)
#            command="sudo chown root:root "+self.__chrootDirectory
#            
#            command=command.split()
#            subprocess.call(command,stdin=open("/dev/null", "r"), close_fds=True)
            
        if not os.path.isdir(self.__chrootDirTransfert):
            os.makedirs(self.__chrootDirTransfert)


    def getDic(self):
        '''
        
        '''
        saveconfigPackages = {}    
        saveconfigPackages["chrootDirectory"] = self.__chrootDirectory
        saveconfigPackages["rpmbuildDirectory"] = self.__chrootrpmbuildDirectory
        saveconfigPackages["chrootDirTransfert"] = self.__chrootDirTransfert
        saveconfigPackages["dirTransfert"] = self.__dirTransfert
        return saveconfigPackages
    

    def createChRoot(self,  obsApi=None,
                            projectDir=None ,
                            repos=None,
                            arch=None,
                            specPath=None):
        '''
        
        '''
        ObsLightOsc.myObsLightOsc.createChRoot(obsApi=obsApi, 
                                               chrootDir=self.__chrootDirectory,
                                               projectDir=projectDir ,
                                               repos=repos,
                                               arch=arch,
                                               specPath=specPath)
        
        subprocess.call(["sudo","chown","root:users",self.__chrootDirectory])
        subprocess.call(["sudo","chown","root:users",self.__chrootDirectory+"/root"])
        subprocess.call(["sudo","chown","root:users",self.__chrootDirectory+"/etc"])
        subprocess.call(["sudo","chmod","g+rw",self.__chrootDirectory])
        subprocess.call(["sudo","chmod","g+r",self.__chrootDirectory+"/root"])
        subprocess.call(["sudo","chmod","g+rw",self.__chrootDirectory+"/etc"])

                
        self.prepareChroot(self.__chrootDirectory)

    def __findPackageDirectory(self, package=None):
        '''
        
        '''
        pathBuild = self.__chrootDirectory + "/" + self.__chrootrpmbuildDirectory + "/" + "BUILD"
        #Find the Package Directory
        for  packageDirectory in os.listdir(pathBuild):
            res = packageDirectory
            if "-" in packageDirectory:
                packageDirectory = packageDirectory[:packageDirectory.rindex("-")]
                
            
            if package == packageDirectory:
                return self.__chrootrpmbuildDirectory + "/BUILD/" + res
        return None


    def addPackageSourceInChRoot(self,  package=None,
                                        specFile=None,
                                        arch=None):

        '''
        
        '''
        packageName = package.getName()
        command = []
        command.append("zypper --non-interactive si " + packageName)
        self.execCommand(command=command)

        if os.path.isdir(self.__chrootDirectory+"/"+self.__chrootrpmbuildDirectory+"/SPECS/"):
            aspecFile=self.__chrootrpmbuildDirectory+"/SPECS/"+specFile
            
            self.buildPrepRpm(chrootDir=self.__chrootDirectory,
                              specFile=aspecFile,
                              arch=arch)
            
            #find the directory to watch
            packageDirectory = self.__findPackageDirectory(package=packageName)
            package.setDirectoryBuild(packageDirectory)
            self.initGitWatch(path=packageDirectory)
        else:
            raise ObsLightErr.ObsLightChRootError(packageName + " source is not intall in " + self.__chrootDirectory)
            
            
    def execCommand(self, command=None):
        '''
        
        '''
        if not ObsLightMic.myObsLightMic.isInit():
            ObsLightMic.myObsLightMic.initChroot(chrootDirectory=self.__chrootDirectory,
                                                 chrootTransfertDirectory=self.__chrootDirTransfert,
                                                 transfertDirectory=self.__dirTransfert)    
        
        timeString = time.strftime("%Y%m%d%H%M%S")
        scriptName = "runMe-" + timeString + ".sh"    
        scriptPath = self.__chrootDirTransfert + "/" + scriptName

        f = open(scriptPath, 'w')
        f.write("#!/bin/sh\n")
        f.write("# Created by obslight\n")
        
        for c in command:
            f.write(c + "\n") 
        f.close()
        
        os.chmod(scriptPath, 0654)
        
        aCommand = "sudo chroot " + self.__chrootDirectory + " " + self.__dirTransfert + "/"+ scriptName
        
        if platform.machine() == 'x86_64':
            aCommand = "linux32 " + aCommand
        
        aCommand = shlex.split(aCommand)
        subprocess.call(aCommand, stdin=open(os.devnull, 'rw'))

    def addRepos(self, repos=None, alias=None):
        '''
        
        '''
        command = []
        command.append("zypper ar " + repos + " " + alias)
        command.append("zypper --no-gpg-checks --gpg-auto-import-keys ref")
        self.execCommand(command=command) 
        

    def buildPrepRpm(self,  chrootDir=None,
                            specFile=None,
                            arch=None):

        '''
        
        '''
        command = []
        command.append("rpmbuild -bp --define '_srcdefattr (-,root,root)' " + specFile + "  --target=" + arch + " < /dev/null")
        self.execCommand(command=command)
        
    def goToChRoot(self, chrootDir=None, path=None):
        '''
        
        '''
        if  not ObsLightMic.myObsLightMic.isInit():
            ObsLightMic.myObsLightMic.initChroot(chrootDirectory=self.__chrootDirectory,
                                                 chrootTransfertDirectory=self.__chrootDirTransfert,
                                                 transfertDirectory=self.__dirTransfert)

        
        pathScript = self.__chrootDirTransfert + "/runMe.sh"
        f = open(pathScript, 'w')
        f.write("#!/bin/sh\n")
        f.write("# Created by obslight\n")
        if path != None:
            f.write("cd " + path + "\n")
        f.write("exec bash\n") 
        f.close()
        
        os.chmod(pathScript, 0654)
        
        command = "sudo chroot " + self.__chrootDirectory + " " + self.__dirTransfert + "/runMe.sh"
        if platform.machine() == 'x86_64':
            command = "linux32 " + command
        
        command = shlex.split(command)
        
        subprocess.call(command)
        
    def initGitWatch(self, path=None):
        '''
        
        '''
        command = []
        command.append("git init " + path)
        command.append("git --work-tree=" + path + " --git-dir=" + path + "/.git add " + path + "/\*")
        command.append("git --git-dir=" + path + "/.git commit -m \"first commit\"")
        self.execCommand(command=command)
        

    def makePatch(self, package=None,
                        patch=None):
        '''
        
        '''
        patchFile=patch
        pathPackage=package.getPackageDirectory()
        pathOscPackage=package.getOscDirectory()
        command=[]
        command.append("git --git-dir="+pathPackage+"/.git --work-tree="+pathPackage+" diff -p > "+self.__dirTransfert+"/"+patchFile)
                
        self.execCommand(command=command)
        shutil.copy(self.__chrootDirTransfert + "/" + patchFile, pathOscPackage + "/" + patch)
        package.addPatch(file=patch)
        self.__getAddRemoveFiles(chrootDir=None, package=package)
        package.save()
        
    def __getAddRemoveFiles(self, chrootDir=None, package=None):
        '''
        
        '''
        resultFile = "resultGitStatus" + package.getName() + ".log"
        pathPackage = package.getPackageDirectory()
        pathOscPackage = package.getOscDirectory()
        command = []
        command.append("git --git-dir=" + pathPackage + "/.git --work-tree=" + pathPackage + " status -u -s > " + self.__dirTransfert + "/" + resultFile)
        self.execCommand(command=command)
        
        result = []
        f = open(self.__chrootDirTransfert + "/" + resultFile, 'r')
        for line in f:
            result.append(line)
        f.close()
        
        filesToAdd = []
        filesToDel = []
        
        for res in result:
            if " " in res:
                if res[0] == " ":
                    res = res[1:]
                
                if " " in res:
                    index = res.index(" ")
                    tag = res[:index]
                    file = res[index + 1:-1]
                    if tag == "??":
                        filesToAdd.append(file)
                    elif tag == "D":
                        filesToDel.append(file)
        
        command = []
        repoListFilesToAdd = []
        for file in filesToAdd:
            baseFile = os.path.basename(file)
            command.append("cp " + os.path.join(pathPackage, file) + " " + self.__dirTransfert)
            repoListFilesToAdd.append([file, baseFile])
            
        if command!=[]:    
            self.execCommand(command=command)
        
            for fileDef in repoListFilesToAdd:
                [file,baseFile]=fileDef
                shutil.copy(self.__chrootDirTransfert+"/"+baseFile, pathOscPackage+"/"+baseFile)
                package.addFileToSpec(baseFile=baseFile,file=file)
            
            
        for fileDef in filesToDel:
            package.delFileToSpec(file=fileDef)
        
        package.save()
        
        
        
    def prepareChroot(self, chrootDir):
        '''
        Prepares the chroot :
        - replaces some binaries by their ARM equivalent (in case chroot is ARM)
        - configures zypper and rpm for ARM
        - rebuilds rpm database
        '''
        command = []

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
        command.append('echo "alias ll=\"ls -lh\"\nalias la=\"ls -Alh\"" >> /etc/profile.d/alias.sh')
        self.execCommand(command=command)


        
        


