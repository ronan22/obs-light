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
import ObsLightConfig
from ObsLightSubprocess import SubprocessCrt

import ObsLightPrintManager

class ObsLightChRoot(object):
    '''
    classdocs
    '''

    def __init__(self, projectDirectory,
                        fromSave=None):

        '''
        Constructor
        '''
        self.__chrootDirectory = os.path.join(projectDirectory, "aChroot")
        self.__chrootDirTransfert = os.path.join(projectDirectory, "chrootTransfert")
        self.__dirTransfert = "/chrootTransfert"
        self.__chrootRpmBuildDirectory = "/root/rpmbuild"
        self.__chrootRpmBuildTmpDirectory = "/root/obslightbuild"
        self.__mySubprocessCrt = SubprocessCrt()

        if fromSave == None:
            self.__dicoRepos = {}
        else:
            if "dicoRepos" in fromSave.keys():
                self.__dicoRepos = fromSave["dicoRepos"]
        self.initChRoot()

    def getChrootRpmBuildDirectory(self):
        '''
        
        '''
        return self.__chrootRpmBuildDirectory

    def getChrootDirTransfert(self):
        '''
        
        '''
        return self.__chrootDirTransfert

    def getDirectory(self):
        '''
        Return the path of aChRoot of a project
        '''
        return self.__chrootDirectory

    def removeChRoot(self):
        '''
        
        '''
        if  ObsLightMic.getObsLightMic(name=self.getDirectory()).isInit():
            ObsLightMic.destroy(name=self.getDirectory())

        if os.path.isdir(self.getDirectory()):
            return self.__subprocess(command="sudo rm -r  " + self.getDirectory())

        return 0

    def isInit(self):
        '''
        
        '''
        res = os.path.isdir(self.getDirectory())

        if res and os.path.isfile(os.path.join(self.getDirectory(), ".chroot.lock")):
            if not ObsLightMic.isInit(name=self.getDirectory()):
                ObsLightMic.getObsLightMic(name=self.getDirectory()).initChroot(chrootDirectory=self.getDirectory(),
                                                                                chrootTransfertDirectory=self.__chrootDirTransfert,
                                                                                transfertDirectory=self.__dirTransfert)
        return res

    def initChRoot(self):
        '''
        
        '''
        if not os.path.isdir(self.__chrootDirTransfert):
            os.makedirs(self.__chrootDirTransfert)

    def getDic(self):
        '''
        
        '''
        saveconfigPackages = {}
        saveconfigPackages["dicoRepos"] = self.__dicoRepos
        return saveconfigPackages


    def createChRoot(self, repos,
                           arch,
                           apiurl,
                           obsProject):
        '''
        
        '''
        res = ObsLightOsc.getObsLightOsc().createChRoot(chrootDir=self.getDirectory(),
                                                        repos=repos,
                                                        arch=arch,
                                                        apiurl=apiurl,
                                                        project=obsProject,
                                                        )

        if res != 0:
            raise ObsLightErr.ObsLightChRootError("Can't create the chroot")

        self.__subprocess(command="sudo chown root:users " + self.getDirectory())
        self.__subprocess(command="sudo chown root:users " + self.getDirectory() + "/root")
        self.__subprocess(command="sudo chown root:users " + self.getDirectory() + "/etc")
        self.__subprocess(command="sudo chmod g+rw " + self.getDirectory())
        self.__subprocess(command="sudo chmod g+r " + self.getDirectory() + "/root")
        self.__subprocess(command="sudo chmod g+rw " + self.getDirectory() + "/etc")

        self.initRepos()

        self.prepareChroot(self.getDirectory())

    def __subprocess(self, command=None, waitMess=False):
        '''
        
        '''
        return self.__mySubprocessCrt.execSubprocess(command=command, waitMess=waitMess)

    def resolveMacro(self, name):
        '''

        '''
        if not os.path.isdir(self.getDirectory()):
            raise ObsLightErr.ObsLightChRootError("goToChRoot: chroot is not initialized, use createChRoot")
        elif not os.path.isdir(self.getDirectory()):
            raise ObsLightErr.ObsLightChRootError("goToChRoot: the path: " + self.getDirectory() + " is not a directory")

        if  not ObsLightMic.getObsLightMic(name=self.getDirectory()).isInit():
            ObsLightMic.getObsLightMic(name=self.getDirectory()).initChroot(chrootDirectory=self.getDirectory(),
                                                                               chrootTransfertDirectory=self.__chrootDirTransfert,
                                                                               transfertDirectory=self.__dirTransfert)

        command = "rpm --eval " + name + " > /chrootTransfert/resultRpmQ.log"

        pathScript = self.__chrootDirTransfert + "/runMe.sh"
        f = open(pathScript, 'w')
        f.write("#!/bin/sh\n")
        f.write("# Created by obslight\n")
        f.write(command)
        f.close()

        os.chmod(pathScript, 0654)

        command = "sudo -H chroot " + self.getDirectory() + " " + self.__dirTransfert + "/runMe.sh"

        if platform.machine() == 'x86_64':
            command = "linux32 " + command

        command = shlex.split(str(command))
        p = subprocess.Popen(command, stdout=None)
        p.wait()
        f = open(self.__chrootDirTransfert + "/resultRpmQ.log", 'r')
        name = f.read().replace("\n", "")
        f.close()
        return name

    def __findPackageDirectory(self, package=None):
        '''
        Return the directory of where the package were installed.
        '''

        name = package.getMacroDirectoryPackageName()

        if name != None:
            prepDirname = self.resolveMacro(name)
            if prepDirname == None:
                raise ObsLightErr.ObsLightChRootError(" Can't resolve the macro " + name)

            ObsLightPrintManager.getLogger().debug("for the package " + name + " the prepDirname is: " + str(prepDirname))

            pathBuild = self.getDirectory() + "/" + self.__chrootRpmBuildDirectory + "/" + "BUILD"
            if not os.path.isdir(pathBuild):
                raise ObsLightErr.ObsLightChRootError("in the chroot path: " + pathBuild + " is not a directory")

            resultPath = self.__chrootRpmBuildDirectory + "/BUILD/" + prepDirname

            subDir = os.listdir(pathBuild + "/" + prepDirname)
            if len(subDir) == 0:
                return resultPath
            elif (len(subDir) == 1) and os.path.isdir(pathBuild + "/" + prepDirname + "/" + subDir[0]):
                return resultPath + "/" + subDir[0]
            else:
                return resultPath
        else:
            package.setChRootStatus("No build directory")
        return None

    def getChRootRepositories(self):
        '''
        
        '''
        return self.__dicoRepos

    def addPackageSourceInChRoot(self, package,
                                       specFile,
                                       repo):
        '''
        
        '''
        if package.getStatus() == "excluded":
            raise ObsLightErr.ObsLightChRootError(package.getName() + " has a excluded status, it can't be install")
        elif specFile == None:
            raise ObsLightErr.ObsLightChRootError(package.getName() + " has no spec file")
        else:
            packageName = package.getName()

            command = []
            command.append("zypper --non-interactive si --build-deps-only " + packageName)
            command.append("zypper --non-interactive si " + "--repo " + repo + " " + packageName)
            res = self.execCommand(command=command)

            if res != 0:
                ObsLightPrintManager.getLogger().error(packageName + " the zypper Script fail")
                return None
                #raise ObsLightErr.ObsLightChRootError(packageName + " the zypper Script fail")

            if os.path.isdir(self.getDirectory() + "/" + self.__chrootRpmBuildDirectory + "/SPECS/"):
                aspecFile = self.__chrootRpmBuildDirectory + "/SPECS/" + specFile
                self.prepRpm(specFile=aspecFile)
                #find the directory to watch
                packageDirectory = self.__findPackageDirectory(package=package)
                ObsLightPrintManager.getLogger().debug("for the package " + packageName + " the packageDirectory is used : " + str(packageDirectory))
                package.setDirectoryBuild(packageDirectory)
                if packageDirectory != None:
                    self.initGitWatch(path=packageDirectory)
                    self.__buildRpm(aspecFile)
                    self.ignoreGitWatch(path=packageDirectory)
                    package.setChRootStatus("Installed")
            else:
                raise ObsLightErr.ObsLightChRootError(packageName + " source is not installed in " + self.getDirectory())

    def execCommand(self, command=None):
        '''
        Execute a list of commands in the chroot.
        '''
        if command == None:
            return
        if not ObsLightMic.getObsLightMic(name=self.getDirectory()).isInit():
            ObsLightMic.getObsLightMic(name=self.getDirectory()).initChroot(chrootDirectory=self.getDirectory(),
                                                                            chrootTransfertDirectory=self.__chrootDirTransfert,
                                                                            transfertDirectory=self.__dirTransfert)
        #Need more then second %S
        timeString = time.strftime("%Y-%m-%d_%Hh%Mm") + str(time.time() % 1).split(".")[1]
        scriptName = "runMe_" + timeString + ".sh"
        scriptPath = self.__chrootDirTransfert + "/" + scriptName

        f = open(scriptPath, 'w')
        f.write("#!/bin/sh\n")
        f.write("# Created by obslight\n")
        for c in command:
            f.write(c + "\n")
        f.close()

        os.chmod(scriptPath, 0654)

        aCommand = "sudo -H chroot " + self.getDirectory() + " " + self.__dirTransfert + "/" + scriptName
        if platform.machine() == 'x86_64':
            aCommand = "linux32 " + aCommand

        return self.__subprocess(command=aCommand, waitMess=True)


    def addRepo(self, repos=None, alias=None):
        '''
        Add a repository in the chroot's zypper configuration file.
        '''
        if alias in self.__dicoRepos.keys():
            raise ObsLightErr.ObsLightChRootError("can't add " + alias + " , already configure in the chroot")
        else:
            self.__dicoRepos[alias] = repos

        self.__addRepo(repos=repos, alias=alias)

    def initRepos(self):
        '''
        init all the repos in the chroot.
        '''
        for alias in self.__dicoRepos.keys():
            self.__addRepo(repos=self.__dicoRepos[alias], alias=alias)

    def isAlreadyAReposAlias(self, alias):
        '''
        
        '''
        if alias in self.__dicoRepos.keys():
            return True
        else:
            return False

    def __addRepo(self, repos=None, alias=None):
        '''
        
        '''
        command = []
        command.append("zypper ar " + repos + " " + alias)
        command.append("zypper --no-gpg-checks --gpg-auto-import-keys ref")
        self.execCommand(command=command)

    def prepRpm(self, specFile=None):
        '''
        Execute the %prep section of an RPM spec file.
        '''
        command = []
        command.append("rpmbuild -bp --define '_srcdefattr (-,root,root)' " + specFile + " < /dev/null")
        self.execCommand(command=command)

    def __buildRpm(self, specFile=None):
        '''
        Execute the %prep section of an RPM spec file.
        '''
        command = []
        command.append("rpmbuild -bc --short-circuit --define '_srcdefattr (-,root,root)' " + specFile + " < /dev/null")
        self.execCommand(command=command)


    def buildRpm(self,
                   package,
                   specFile,
                   pathPackage,
                   tarFile
                   ):
        '''
        Execute the %build section of an RPM spec file.
        '''
        tmpPath = pathPackage.replace(self.__chrootRpmBuildDirectory + "/BUILD", "").strip("/")
        tmpPath = tmpPath.strip("/")
        command = []
        command.append("rm -r " + self.__chrootRpmBuildTmpDirectory)
        command.append("rm -r " + self.__chrootRpmBuildDirectory + "/BUILDROOT/*")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/BUILD")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/BUILDROOT")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/RPMS")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/SOURCES")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/SPECS")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/SRPMS")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/TMP")
        command.append("chown -R root:users " + self.__chrootRpmBuildTmpDirectory)
        command.append("chmod -R g+rw " + self.__chrootRpmBuildTmpDirectory)

        command.append("git --git-dir=" + pathPackage + "/.git --work-tree=" + pathPackage + \
                       " archive --format=tar --prefix=" + tmpPath + "/ HEAD \
                       | (cd " + self.__chrootRpmBuildTmpDirectory + "/TMP/ && tar xf -)")

        command.append("cd " + self.__chrootRpmBuildTmpDirectory + "/TMP/")
        command.append("tar -czvf  " + tarFile + " *")
        command.append("mv " + tarFile + " ../SOURCES")
        self.execCommand(command=command)
        pathToSaveSpec = specFile.replace(self.__chrootRpmBuildDirectory,
                                          self.__chrootRpmBuildTmpDirectory)

        package.saveTmpSpec(path=self.getDirectory() + pathToSaveSpec,
                            topdir=self.__chrootRpmBuildTmpDirectory,
                            archive=tarFile)
        command = []
        command = []
        command.append("rpmbuild -bc --define '_srcdefattr (-,root,root)' " + pathToSaveSpec + " < /dev/null")
        command.append("cp -fprv  " + self.__chrootRpmBuildTmpDirectory + "/BUILD/* " + self.__chrootRpmBuildDirectory + "/BUILD/")
        command.append("rm -r " + self.__chrootRpmBuildTmpDirectory)
        self.execCommand(command=command)

    def installRpm(self,
                   package,
                   specFile,
                   pathPackage,
                   tarFile
                   ):
        '''
        Execute the %install section of an RPM spec file.
        '''
        tmpPath = pathPackage.replace(self.__chrootRpmBuildDirectory + "/BUILD", "").strip("/")
        tmpPath = tmpPath.strip("/")
        command = []
        command.append("rm -r " + self.__chrootRpmBuildTmpDirectory)
        command.append("rm -r " + self.__chrootRpmBuildDirectory + "/BUILDROOT/*")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/BUILD")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/BUILDROOT")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/RPMS")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/SOURCES")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/SPECS")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/SRPMS")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/TMP")
        command.append("chown -R root:users " + self.__chrootRpmBuildTmpDirectory)
        command.append("chmod -R g+rw " + self.__chrootRpmBuildTmpDirectory)

        command.append("git --git-dir=" + pathPackage + "/.git --work-tree=" + pathPackage + \
                       " archive --format=tar --prefix=" + tmpPath + "/ HEAD \
                       | (cd " + self.__chrootRpmBuildTmpDirectory + "/TMP/ && tar xf -)")

        command.append("cd " + self.__chrootRpmBuildTmpDirectory + "/TMP/")
        command.append("tar -czvf  " + tarFile + " *")
        command.append("mv " + tarFile + " ../SOURCES")
        self.execCommand(command=command)
        pathToSaveSpec = specFile.replace(self.__chrootRpmBuildDirectory,
                                          self.__chrootRpmBuildTmpDirectory)

        package.saveTmpSpec(path=self.getDirectory() + pathToSaveSpec,
                            topdir=self.__chrootRpmBuildTmpDirectory,
                            archive=tarFile)
        command = []
        command.append("rpmbuild -bi --define '_srcdefattr (-,root,root)' " + pathToSaveSpec + " < /dev/null")
        command.append("cp -fprv  " + self.__chrootRpmBuildTmpDirectory + "/BUILD/* " + self.__chrootRpmBuildDirectory + "/BUILD/")
        command.append("cp -fprv  " + self.__chrootRpmBuildTmpDirectory + "/BUILDROOT/* " + self.__chrootRpmBuildDirectory + "/BUILDROOT/")
        command.append("rm -r " + self.__chrootRpmBuildTmpDirectory)
        self.execCommand(command=command)

    def packageRpm(self,
                   package,
                   specFile,
                   pathPackage,
                   tarFile
                   ):
        '''
        Execute the package section of an RPM spec file.
        '''
        tmpPath = pathPackage.replace(self.__chrootRpmBuildDirectory + "/BUILD", "").strip("/")
        tmpPath = tmpPath.strip("/")
        command = []
        command.append("rm -r " + self.__chrootRpmBuildTmpDirectory)
        command.append("rm -r " + self.__chrootRpmBuildDirectory + "/BUILDROOT/*")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/BUILD")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/BUILDROOT")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/RPMS")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/SOURCES")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/SPECS")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/SRPMS")
        command.append("mkdir -p " + self.__chrootRpmBuildTmpDirectory + "/TMP")
        command.append("chown -R root:users " + self.__chrootRpmBuildTmpDirectory)
        command.append("chmod -R g+rw " + self.__chrootRpmBuildTmpDirectory)

        command.append("git --git-dir=" + pathPackage + "/.git --work-tree=" + pathPackage + \
                       " archive --format=tar --prefix=" + tmpPath + "/ HEAD \
                       | (cd " + self.__chrootRpmBuildTmpDirectory + "/TMP/ && tar xf -)")

        command.append("cd " + self.__chrootRpmBuildTmpDirectory + "/TMP/")
        command.append("tar -czvf  " + tarFile + " *")
        command.append("mv " + tarFile + " ../SOURCES")
        self.execCommand(command=command)
        pathToSaveSpec = specFile.replace(self.__chrootRpmBuildDirectory,
                                          self.__chrootRpmBuildTmpDirectory)

        package.saveTmpSpec(path=self.getDirectory() + pathToSaveSpec,
                            topdir=self.__chrootRpmBuildTmpDirectory,
                            archive=tarFile)
        command = []
        command.append("rpmbuild -ba --define '_srcdefattr (-,root,root)' " + pathToSaveSpec + " < /dev/null")
        command.append("cp -fprv  " + self.__chrootRpmBuildTmpDirectory + "/RPMS/* " + self.__chrootRpmBuildDirectory + "/RPMS/")
        command.append("cp -fprv  " + self.__chrootRpmBuildTmpDirectory + "/SRPMS/* " + self.__chrootRpmBuildDirectory + "/SRPMS/")
        command.append("cp -fprv  " + self.__chrootRpmBuildTmpDirectory + "/BUILD/* " + self.__chrootRpmBuildDirectory + "/BUILD/")
        command.append("cp -fprv  " + self.__chrootRpmBuildTmpDirectory + "/BUILDROOT/* " + self.__chrootRpmBuildDirectory + "/BUILDROOT/")
        command.append("rm -r " + self.__chrootRpmBuildTmpDirectory)
        self.execCommand(command=command)

    def goToChRoot(self, path=None, detach=False):
        '''
        Go to the chroot.
        Open a Bash in the chroot.
        '''
        if not os.path.isdir(self.getDirectory()):
            raise ObsLightErr.ObsLightChRootError("goToChRoot: chroot is not initialized, use createChRoot")
        elif not os.path.isdir(self.getDirectory()):
            raise ObsLightErr.ObsLightChRootError("goToChRoot: the path: " + self.getDirectory() + " is not a directory")

        if  not ObsLightMic.getObsLightMic(name=self.getDirectory()).isInit():
            ObsLightMic.getObsLightMic(name=self.getDirectory()).initChroot(chrootDirectory=self.getDirectory(),
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

        command = "sudo -H chroot " + self.getDirectory() + " " + self.__dirTransfert + "/runMe.sh"
        if detach is True:
            command = ObsLightConfig.getConsole() + " " + command
        if platform.machine() == 'x86_64':
            command = "linux32 " + command

        # TODO: find why it does not work without str()
        command = shlex.split(str(command))
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

    def ignoreGitWatch(self, path=None):
        '''
        Initialize a Git repository in the specified path, and 'git add' everything.
        '''
        if path == None:
            raise ObsLightErr.ObsLightChRootError("path is not defined in initGitWatch.")

        command = []
        command.append("git --work-tree=" + path + " --git-dir=" + path + "/.git status -u -s | cut -d' ' -f2 >> " + path + "/.gitignore")
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

        if ObsLightMic.getObsLightMic(name=self.getDirectory()).isArmArch(chrootDir):
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
        command.append('echo "alias ll=\\"ls -lh\\"" >> ~/.bashrc')
        command.append('echo "alias la=\\"ls -Alh\\"" >> ~/.bashrc')
        command.append('echo "alias vi=\\"vim\\"" >> ~/.bashrc')
        self.execCommand(command=command)

    def deleteRepo(self, repoAlias):
        '''
        
        '''
        if repoAlias in self.__dicoRepos.keys():
            command = []
            command.append("zypper rr " + repoAlias)
            command.append("zypper --no-gpg-checks --gpg-auto-import-keys ref")
            self.execCommand(command=command)
            del self.__dicoRepos[repoAlias]
        else:
            raise ObsLightErr.ObsLightChRootError("Can't delete the repo", repoAlias)

    def modifyRepo(self, repoAlias, newUrl, newAlias):
        '''
        
        '''
        self.deleteRepo(repoAlias)
        self.__addRepo(newUrl, newAlias)

