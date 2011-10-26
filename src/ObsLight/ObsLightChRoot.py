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

@author: Ronan Le Martret
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

from ObsLightSubprocess import SubprocessCrt

class ObsLightChRoot(object):
    '''
    classdocs
    '''


    def __init__(self, chrootDirectory=None,
                        chrootDirTransfert=None,
                        dirTransfert=None,
                        fromSave=None):

        '''
        Constructor
        '''
        self.__mySubprocessCrt = SubprocessCrt()
        
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
    

    def createChRoot(self, #obsApi=None,
                            projectDir=None ,
                            repos=None,
                            arch=None,
                            specPath=None):
        '''
        
        '''
        ObsLightOsc.myObsLightOsc.createChRoot(#obsApi=obsApi,
                                               chrootDir=self.__chrootDirectory,
                                               projectDir=projectDir ,
                                               repos=repos,
                                               arch=arch,
                                               specPath=specPath)
        
        
        self.__subprocess(command="sudo chown root:users " + self.__chrootDirectory)
        self.__subprocess(command="sudo chown root:users " + self.__chrootDirectory + "/root")
        self.__subprocess(command="sudo chown root:users " + self.__chrootDirectory + "/etc")
        self.__subprocess(command="sudo chmod g+rw " + self.__chrootDirectory)
        self.__subprocess(command="sudo chmod g+r " + self.__chrootDirectory + "/root")
        self.__subprocess(command="sudo chmod g+rw " + self.__chrootDirectory + "/etc")
                
        self.prepareChroot(self.__chrootDirectory)

    def __subprocess(self, command=None, waitMess=False):
        '''
        
        '''
        return self.__mySubprocessCrt.execSubprocess(command=command, waitMess=waitMess)
        

    def __findPackageDirectory(self, package=None):
        '''
        Return the directory of where the package were installed.
        '''
        pathBuild = self.__chrootDirectory + "/" + self.__chrootrpmbuildDirectory + "/" + "BUILD"
        #Find the Package Directory
        
        if package == None:
            raise ObsLightErr.ObsLightChRootError("in __findPackageDirectory path is not def ")
        elif not os.path.isdir(pathBuild):
            raise ObsLightErr.ObsLightChRootError("in the chroot path: " + pathBuild + " is not a directory")
        
        for  packageDirectory in os.listdir(pathBuild):
            res = packageDirectory
            if "-" in packageDirectory:
                packageDirectory = packageDirectory[:packageDirectory.rindex("-")]
                
            if package == packageDirectory:
                resultPath= self.__chrootrpmbuildDirectory + "/BUILD/" + res
                
                subDir=os.listdir(pathBuild+ "/" + res)
                if len(subDir)==0:
                    return resultPath
                elif len(subDir)==1:
                    return resultPath+"/"+subDir[0]
                else:
                    return resultPath
                
        return None


    def addPackageSourceInChRoot(self, package=None,
                                        specFile=None,
                                        repo=None):

        '''
        
        '''
        packageName = package.getName()
        command = []
        command.append("zypper --non-interactive si --build-deps-only " + packageName)
        command.append("zypper --non-interactive si " + "--repo " + repo + " " + packageName)
        self.execCommand(command=command)

        if os.path.isdir(self.__chrootDirectory + "/" + self.__chrootrpmbuildDirectory + "/SPECS/"):
            aspecFile = self.__chrootrpmbuildDirectory + "/SPECS/" + specFile
            
            self.buildPrepRpm(specFile=aspecFile)
            
            #find the directory to watch
            packageDirectory = self.__findPackageDirectory(package=packageName)
            package.setDirectoryBuild(packageDirectory)
            self.initGitWatch(path=packageDirectory)
        else:
            raise ObsLightErr.ObsLightChRootError(packageName + " source is not installed in " + self.__chrootDirectory)
            
            
    def execCommand(self, command=None):
        '''
        Execute a list of commands in the chroot.
        '''
        if command == None:
            return
        
        if not ObsLightMic.myObsLightMic.isInit():
            ObsLightMic.myObsLightMic.initChroot(chrootDirectory=self.__chrootDirectory,
                                                 chrootTransfertDirectory=self.__chrootDirTransfert,
                                                 transfertDirectory=self.__dirTransfert)    
        
        timeString = time.strftime("%Y-%m-%d_%Hh%Mm%S")
        scriptName = "runMe_" + timeString + ".sh"    
        scriptPath = self.__chrootDirTransfert + "/" + scriptName

        f = open(scriptPath, 'w')
        f.write("#!/bin/sh\n")
        f.write("# Created by obslight\n")
        
        for c in command:
            f.write(c + "\n") 
        f.close()
        
        os.chmod(scriptPath, 0654)
        
        aCommand = "sudo -H chroot " + self.__chrootDirectory + " " + self.__dirTransfert + "/" + scriptName
        
        if platform.machine() == 'x86_64':
            aCommand = "linux32 " + aCommand
        
        self.__subprocess(command=aCommand, waitMess=True)


    def addRepo(self, repos=None, alias=None):
        '''
        Add a repository in the chroot's zypper configuration file.
        '''
        command = []
        command.append("zypper ar " + repos + " " + alias)
        command.append("zypper --no-gpg-checks --gpg-auto-import-keys ref")
        self.execCommand(command=command) 
        

    def buildPrepRpm(self, specFile=None):
        '''
        Execute the %prep section of an RPM spec file.
        '''
        command = []
        command.append("rpmbuild -bp --define '_srcdefattr (-,root,root)' " + specFile + " < /dev/null")
        self.execCommand(command=command)
        
    def goToChRoot(self, path=None):
        '''
        Go to the chroot.
        Open a Bash in the chroot.
        '''
        if not os.path.isdir(self.__chrootDirectory):
            raise ObsLightErr.ObsLightChRootError("goToChRoot: chroot is not initialized, use createChRoot")
        elif not os.path.isdir(self.__chrootDirectory):
            raise 
        
        ObsLightErr.ObsLightChRootError("goToChRoot: the path: " + self.__chrootDirectory + " is not a directory")
        
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
        
        command = "sudo -H chroot " + self.__chrootDirectory + " " + self.__dirTransfert + "/runMe.sh"
        if platform.machine() == 'x86_64':
            command = "linux32 " + command
            
        command = shlex.split(command)
        subprocess.call(command)
 
        
    def initGitWatch(self, path=None):
        '''
        Initialize a Git repository in the specified path, and 'git add' everything.
        '''
        if path == None:
            raise ObsLightErr.ObsLightChRootError("path is not defined in initGitWatch.")
        
        command = []
        command.append("git init " + path)
        command.append("git --work-tree=" + path + " --git-dir=" + path + "/.git add " + path + "/\*")
        command.append("git --git-dir=" + path + "/.git commit -m \"first commit\"")
        self.execCommand(command=command)
        

    def makePatch(self, package=None, patch=None):
        '''
        Create a patch from modifications made in the package directory.
        '''
        patchFile = patch
        pathPackage = package.getPackageDirectory()
        pathOscPackage = package.getOscDirectory()
        command = []
        command.append("git --git-dir=" + pathPackage + "/.git --work-tree=" + pathPackage + " diff -p > " + self.__dirTransfert + "/" + patchFile)
        
        self.execCommand(command=command)
        shutil.copy(self.__chrootDirTransfert + "/" + patchFile, pathOscPackage + "/" + patch)
        package.addPatch(aFile=patch)
        self.__getAddRemoveFiles(package=package)
        package.save()
        
    def __getAddRemoveFiles(self, package=None):
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
                    aFile = res[index + 1:-1]
                    if tag == "??":
                        filesToAdd.append(aFile)
                    elif tag == "D":
                        filesToDel.append(aFile)
        
        command = []
        repoListFilesToAdd = []
        for aFile in filesToAdd:
            baseFile = os.path.basename(aFile)
            command.append("cp " + os.path.join(pathPackage, aFile) + " " + self.__dirTransfert)
            repoListFilesToAdd.append([aFile, baseFile])
            
        if command != []:    
            self.execCommand(command=command)
        
            for fileDef in repoListFilesToAdd:
                [aFile, baseFile] = fileDef
                shutil.copy(self.__chrootDirTransfert + "/" + baseFile, pathOscPackage + "/" + baseFile)
                package.addFileToSpec(baseFile=baseFile, aFile=aFile)
            
            
        for fileDef in filesToDel:
            package.delFileToSpec(aFile=fileDef)
        
        package.save()
        
        
        
    def prepareChroot(self, chrootDir):
        '''
        Prepare the chroot :
        - replaces some binaries by their ARM equivalent (in case chroot is ARM)
        - configures zypper and rpm for ARM
        - rebuilds rpm database
        '''
        command = []

        if ObsLightMic.myObsLightMic.isArmArch(chrootDir):
            # If rpm and rpmbuild binaries are not ARM, replace them by ARM versions
            command.append('[ -z "$(file /bin/rpm | grep ARM)" -a -f /bin/rpm.orig-arm ]'
                + ' && cp /bin/rpm /bin/rpm.x86 && cp /bin/rpm.orig-arm /bin/rpm')
            command.append('[ -z "$(file /usr/bin/rpmbuild | grep ARM)" -a -f /usr/bin/rpmbuild.orig-arm ]'
                + ' && cp /usr/bin/rpmbuild /usr/bin/rpmbuild.x86 && cp /usr/bin/rpmbuild.orig-arm /usr/bin/rpmbuild')
            # Remove the old (broken ?) RPM database
            command.append('rm -f /var/lib/rpm/__db*')
            # Force zypper and rpm to use armv7hl architecture
            command.append("echo 'arch = armv7hl' >> /etc/zypp/zypp.conf")
            command.append("echo -n 'armv7hl-meego-linux' > /etc/rpm/platform")
            
        
        command.append("rpm --initdb")
        command.append("rpm --rebuilddb")
        command.append('echo "alias ll=\"ls -lh\"\nalias la=\"ls -Alh\"" >> /etc/profile.d/alias.sh')
        self.execCommand(command=command)
