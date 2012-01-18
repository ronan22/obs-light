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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
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
import re

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

    def __init__(self,
                 projectDirectory,
                 fromSave=None):

        '''
        Constructor
        '''
        self.__chrootDirectory = os.path.join(projectDirectory, "aChroot")
        self.__chrootDirTransfert = os.path.join(projectDirectory, "chrootTransfert")
        self.__dirTransfert = "/chrootTransfert"

        self.__mySubprocessCrt = SubprocessCrt()

        if fromSave == None:
            self.__dicoRepos = {}
        else:
            if "dicoRepos" in fromSave.keys():
                self.__dicoRepos = fromSave["dicoRepos"]
        self.initChRoot()

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
        def getmount(path):
            path = os.path.abspath(path)
            while path != os.path.sep:
                if os.path.ismount(path):
                    return path
                path = os.path.abspath(os.path.join(path, os.pardir))
            return path

        def isAclReady(path):
            montOn = getmount(path)
            with open("/etc/mtab", 'r') as f:
                for line in f:
                    listLine = line.split()
                    if montOn in listLine:
                        listOption = listLine[3].split(",")
                        if "acl" in listOption:
                            return True
            return False

        res = ObsLightOsc.getObsLightOsc().createChRoot(chrootDir=self.getDirectory(),
                                                        repos=repos,
                                                        arch=arch,
                                                        apiurl=apiurl,
                                                        project=obsProject,
                                                        )
        if isAclReady(self.getDirectory()):
            self.__subprocess(command="sudo chmod -R o+rwX " + self.getDirectory())
            self.__subprocess(command="sudo setfacl -Rdm o::rwX -m g::rwX " + self.getDirectory())
        else:
            mountPoint = getmount(self.getDirectory())
            raise ObsLightErr.ObsLightChRootError("ACLs not enabled on mount point '" +
                                                  mountPoint + "'. " +
                                                  "Use command 'mount -o remount,acl " +
                                                  mountPoint + "' as root to enable them.")

        if res != 0:
            raise ObsLightErr.ObsLightChRootError("Can't create the chroot")

        self.__subprocess(command="sudo chown root:users " + self.getDirectory())
        self.__subprocess(command="sudo chown root:users " + self.getDirectory() + "/root")
        self.__subprocess(command="sudo chown root:users " + self.getDirectory() + "/etc")
        self.__subprocess(command="sudo chmod g+rwX " + self.getDirectory())
        self.__subprocess(command="sudo chmod g+rwX " + self.getDirectory() + "/root")
        self.__subprocess(command="sudo chmod g+rwX " + self.getDirectory() + "/etc")
        self.__subprocess(command="sudo chown -R root:users " + self.getDirectory() + "/usr/lib/rpm")
        self.__subprocess(command="sudo chmod -R g+rwX " + self.getDirectory() + "/usr/lib/rpm")

        self.initRepos()

        self.prepareChroot(self.getDirectory())

    def __subprocess(self, command=None, waitMess=False):
        '''
        
        '''
        return self.__mySubprocessCrt.execSubprocess(command=command, waitMess=waitMess)

    def __resolveMacro(self, name):
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

    #Old perhaps to del.
    def __findPackageDirectory_bis(self, package=None):
        '''
        Return the directory of where the package were installed.
        '''
        name = package.getMacroDirectoryPackageName()

        if name != None:
            prepDirname = self.__resolveMacro(name)
            if prepDirname == None:
                raise ObsLightErr.ObsLightChRootError(" Can't resolve the macro " + name)

            ObsLightPrintManager.getLogger().debug("for the package " + name + " the prepDirname is: " + str(prepDirname))

            pathBuild = self.getDirectory() + "/" + package.getChrootRpmBuildDirectory() + "/" + "BUILD"
            if not os.path.isdir(pathBuild):
                raise ObsLightErr.ObsLightChRootError("in the chroot path: " + pathBuild + " is not a directory")
            resultPath = package.getChrootRpmBuildDirectory() + "/BUILD/" + prepDirname
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

    def __findPackageDirectory(self, package=None):
        '''
        Return the directory of where the package were installed.
        '''
        pathBuild = self.getDirectory() + "/" + package.getChrootRpmBuildDirectory() + "/" + "BUILD"
        if not os.path.isdir(pathBuild):
            raise ObsLightErr.ObsLightChRootError("The path '" + pathBuild + "' is not a directory")

        listDir = [item for item in os.listdir(pathBuild) if os.path.isdir(pathBuild + "/" + item)]

        if len(listDir) == 0:
            raise ObsLightErr.ObsLightChRootError("No sub-directory in '" + pathBuild + "'." +
                                                  " There should be exactly one.")
        elif len(listDir) == 1:
            prepDirname = listDir[0]
            resultPath = package.getChrootRpmBuildDirectory() + "/BUILD/" + prepDirname
            package.setPrepDirName(prepDirname)
            subDir = os.listdir(pathBuild + "/" + prepDirname)
            if len(subDir) == 0:
                return resultPath
            elif (len(subDir) == 1) and os.path.isdir(pathBuild + "/" + prepDirname + "/" + subDir[0]):
                return resultPath + "/" + subDir[0]
            else:
                return resultPath
        else:
            raise ObsLightErr.ObsLightChRootError("Too many sub-directories in '" + pathBuild + "'")

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
            command.append("mkdir -p " + package.getChrootRpmBuildDirectory() + "/BUILD")
            command.append("mkdir -p " + package.getChrootRpmBuildDirectory() + "/SPECS")
            command.append("mkdir -p " + package.getChrootRpmBuildDirectory() + "/BUILDROOT")
            command.append("mkdir -p " + package.getChrootRpmBuildDirectory() + "/RPMS")
            command.append("mkdir -p " + package.getChrootRpmBuildDirectory() + "/SOURCES")
            command.append("mkdir -p " + package.getChrootRpmBuildDirectory() + "/SRPMS")

            command.append("chown -R root:users " + package.getChrootRpmBuildDirectory())
            command.append("chmod -R g+rwX " + package.getChrootRpmBuildDirectory())

            packageMacroName = package.getMacroPackageName()
            if packageMacroName == None:
                raise ObsLightErr.ObsLightChRootError("Can't find the spec name (%{name}) of '" + packageName + "'.")

            command.append("zypper --non-interactive si --build-deps-only " + packageMacroName)
            #command.append("zypper --non-interactive si " + "--repo " + repo + " " + packageName)
            res = self.execCommand(command=command)

            if res != 0:
                #ObsLightPrintManager.getLogger().error(packageName + " the zypper Script fail to install '" + packageName + "' dependency.")
                #return None
                raise ObsLightErr.ObsLightChRootError("The installation of some dependencies of '" + packageName + "' failed.\nPlease test the command line:\n'zypper si --build-deps-only " + packageMacroName + "'\ninto the chroot.\nMaybe a repository is missing.")

            if os.path.isdir(self.getDirectory() + "/" + package.getChrootRpmBuildDirectory() + "/SPECS/"):
                aspecFile = package.getChrootRpmBuildDirectory() + "/SPECS/" + specFile

                self.__subprocess(command="sudo chown -R root:users " + self.getDirectory() + "/" + package.getChrootRpmBuildDirectory())
                self.__subprocess(command="sudo chmod -R g+rwX " + self.getDirectory() + "/" + package.getChrootRpmBuildDirectory())
                package.saveSpec(self.getDirectory() + "/" + aspecFile)
                #find the directory to watch
                for aFile in package.getListFile():
                    path = self.getDirectory() + "/" + package.getChrootRpmBuildDirectory() + "/SOURCES/" + str(aFile)
                    if os.path.isfile(path):
                        os.unlink(path)
                    shutil.copy2(package.getOscDirectory() + "/" + str(aFile),
                                 path)
                    self.__subprocess(command="sudo chown -R root:users " + path)

                self.prepRpm(specFile=aspecFile, package=package)
                package.initCurrentPatch()
                packageDirectory = self.__findPackageDirectory(package=package)
                ObsLightPrintManager.getLogger().debug("for the package " + packageName + " the packageDirectory is used : " + str(packageDirectory))
                package.setDirectoryBuild(packageDirectory)
                if packageDirectory != None:
                    self.__subprocess(command="sudo chmod -R og+rwX %s"
                                      % (self.getDirectory() + "/" + packageDirectory))
                    self.initGitWatch(path=packageDirectory)
                    self.__buildRpm(specFile=aspecFile, package=package)
                    self.ignoreGitWatch(path=packageDirectory)
                    package.setFirstCommit(tag=self.getCommitTag(path=packageDirectory))
                    package.setChRootStatus("Installed")
                # TODO: write an "else" or check if the "if" is necessary
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
        self.testOwnerChRoot()
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

    def testOwnerChRoot(self):
        '''
        
        '''
        if os.stat(self.getDirectory()).st_uid != 0:
            raise ObsLightErr.ObsLightChRootError("the chroot '" + self.getDirectory() + "' is not owned by root.")

    def addRepo(self, repos=None, alias=None):
        '''
        Add a repository in the chroot's zypper configuration file.
        '''
        if alias in self.__dicoRepos.keys():
            raise ObsLightErr.ObsLightChRootError("can't add '" + alias + "' , already configure in the chroot")
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
        command.append("zypper ar " + repos + " '" + alias + "'")
        command.append("zypper --no-gpg-checks --gpg-auto-import-keys ref")
        self.execCommand(command=command)

    def prepRpm(self, specFile, package):
        '''
        Execute the %prep section of an RPM spec file.
        '''
        #self.__changeTopDir(package.getTopDirRpmBuildDirectory())

        command = []

        command.append("rpmbuild -bp --define '_srcdefattr (-,root,root)' " +
                       "--define '%_topdir %{getenv:HOME}/" +
                       package.getTopDirRpmBuildDirectory() +
                       "' " + specFile + " < /dev/null")
        self.execCommand(command=command)

    def __buildRpm(self, specFile, package):
        '''
        Execute the %build section of an RPM spec file.
        '''
        #self.__changeTopDir(package.getTopDirRpmBuildDirectory())
        command = []
        command.append("rpmbuild -bc --short-circuit --define '_srcdefattr (-,root,root)'" +
                       " --define '%_topdir %{getenv:HOME}/" +
                       package.getTopDirRpmBuildDirectory() +
                       "' " + specFile + " < /dev/null")
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
        if package.getStatus() == "excluded":
            raise ObsLightErr.ObsLightChRootError(package.getName() + " has a excluded status, it can't be install")

        self.commitGit(mess="build", package=package)

        #self.__changeTopDir(package.getTopDirRpmBuildTmpDirectory())
        tmpPath = pathPackage.replace(package.getChrootRpmBuildDirectory() + "/BUILD", "").strip("/")
        tmpPath = tmpPath.strip("/")
        command = []

        command.append("mkdir -p " + package.getChrootRpmBuildTmpDirectory() + "/BUILD")
        command.append("mkdir -p " + package.getChrootRpmBuildTmpDirectory() + "/SPECS")
        command.append("mkdir -p " + package.getChrootRpmBuildTmpDirectory() + "/TMP")

        command.append("ln -sf " + package.getChrootRpmBuildDirectory() + "/BUILDROOT " + package.getChrootRpmBuildTmpDirectory())
        command.append("ln -sf " + package.getChrootRpmBuildDirectory() + "/RPMS " + package.getChrootRpmBuildTmpDirectory())
        command.append("ln -sf " + package.getChrootRpmBuildDirectory() + "/SOURCES " + package.getChrootRpmBuildTmpDirectory())
        command.append("ln -sf " + package.getChrootRpmBuildDirectory() + "/SRPMS " + package.getChrootRpmBuildTmpDirectory())

        command.append("chown -R root:users " + package.getChrootRpmBuildTmpDirectory())
        command.append("chmod -R g+rwX " + package.getChrootRpmBuildTmpDirectory())

        command.append("git --git-dir=" + pathPackage + "/.git --work-tree=" + pathPackage + \
                       " archive --format=tar --prefix=" + tmpPath + "/ HEAD \
                       | (cd " + package.getChrootRpmBuildTmpDirectory() + "/TMP/ && tar xf -)")

        command.append("cd " + package.getChrootRpmBuildTmpDirectory() + "/TMP/")
        command.append("tar -czvf  " + tarFile + " *")
        command.append("mv " + tarFile + " ../SOURCES")
        self.execCommand(command=command)
        pathToSaveSpec = specFile.replace(package.getChrootRpmBuildDirectory(),
                                          package.getChrootRpmBuildTmpDirectory())

        package.saveTmpSpec(path=self.getDirectory() + pathToSaveSpec,
                            archive=tarFile)
        command = []
        command.append("rpmbuild -bc --define '_srcdefattr (-,root,root)'" +
                       " --define '%_topdir %{getenv:HOME}/" +
                       package.getTopDirRpmBuildTmpDirectory() +
                       "' " + pathToSaveSpec + " < /dev/null")
        command.append("cp -fpr  " + package.getChrootRpmBuildTmpDirectory() + "/BUILD/* " + package.getChrootRpmBuildDirectory() + "/BUILD/")
        command.append("rm -r " + package.getChrootRpmBuildTmpDirectory() + "/TMP")
        self.execCommand(command=command)
        #self.__changeTopDir(package.getTopDirRpmBuildDirectory())

    def installRpm(self,
                   package,
                   specFile,
                   pathPackage,
                   tarFile
                   ):
        '''
        Execute the %install section of an RPM spec file.
        '''
        if package.getStatus() == "excluded":
            raise ObsLightErr.ObsLightChRootError(package.getName() + " has a excluded status, it can't be install")

        self.commitGit(mess="install", package=package)

        #self.__changeTopDir(package.getTopDirRpmBuildTmpDirectory())
        tmpPath = pathPackage.replace(package.getChrootRpmBuildDirectory() + "/BUILD", "").strip("/")
        tmpPath = tmpPath.strip("/")
        command = []

        command.append("mkdir -p " + package.getChrootRpmBuildTmpDirectory() + "/BUILD")
        command.append("mkdir -p " + package.getChrootRpmBuildTmpDirectory() + "/SPECS")
        command.append("mkdir -p " + package.getChrootRpmBuildTmpDirectory() + "/TMP")

        command.append("ln -sf " + package.getChrootRpmBuildDirectory() + "/BUILDROOT " + package.getChrootRpmBuildTmpDirectory())
        command.append("ln -sf " + package.getChrootRpmBuildDirectory() + "/RPMS " + package.getChrootRpmBuildTmpDirectory())
        command.append("ln -sf " + package.getChrootRpmBuildDirectory() + "/SOURCES " + package.getChrootRpmBuildTmpDirectory())
        command.append("ln -sf " + package.getChrootRpmBuildDirectory() + "/SRPMS " + package.getChrootRpmBuildTmpDirectory())

        command.append("chown -R root:users " + package.getChrootRpmBuildTmpDirectory())
        command.append("chmod -R g+rwX " + package.getChrootRpmBuildTmpDirectory())

        command.append("git --git-dir=" + pathPackage + "/.git --work-tree=" + pathPackage + \
                       " archive --format=tar --prefix=" + tmpPath + "/ HEAD \
                       | (cd " + package.getChrootRpmBuildTmpDirectory() + "/TMP/ && tar xf -)")

        command.append("cd " + package.getChrootRpmBuildTmpDirectory() + "/TMP/")
        command.append("tar -czvf  " + tarFile + " *")
        command.append("mv " + tarFile + " ../SOURCES")
        self.execCommand(command=command)
        pathToSaveSpec = specFile.replace(package.getChrootRpmBuildDirectory(),
                                          package.getChrootRpmBuildTmpDirectory())

        package.saveTmpSpec(path=self.getDirectory() + pathToSaveSpec,
                            archive=tarFile)
        command = []
        command.append("rpmbuild -bi --define '_srcdefattr (-,root,root)' " +
                       "--define '%_topdir %{getenv:HOME}/" +
                       package.getTopDirRpmBuildTmpDirectory() + "' " +
                       pathToSaveSpec + " < /dev/null")

        command.append("cp -fpr  " + package.getChrootRpmBuildTmpDirectory() + "/BUILD/* " + package.getChrootRpmBuildDirectory() + "/BUILD/")
        command.append("rm -r " + package.getChrootRpmBuildTmpDirectory() + "/TMP")
        self.execCommand(command=command)
        #self.__changeTopDir(package.getTopDirRpmBuildDirectory())

    def packageRpm(self,
                   package,
                   specFile,
                   pathPackage,
                   tarFile
                   ):
        '''
        Execute the package section of an RPM spec file.
        '''
        if package.getStatus() == "excluded":
            raise ObsLightErr.ObsLightChRootError(package.getName() + " has a excluded status, it can't be install")

        self.commitGit(mess="packageRpm", package=package)

        #self.__changeTopDir(package.getTopDirRpmBuildTmpDirectory())
        tmpPath = pathPackage.replace(package.getChrootRpmBuildDirectory() + "/BUILD", "").strip("/")
        tmpPath = tmpPath.strip("/")
        command = []

        command.append("mkdir -p " + package.getChrootRpmBuildTmpDirectory() + "/BUILD")
        command.append("mkdir -p " + package.getChrootRpmBuildTmpDirectory() + "/TMP")
        command.append("mkdir -p " + package.getChrootRpmBuildTmpDirectory() + "/SPECS")

        command.append("ln -sf " + package.getChrootRpmBuildDirectory() + "/BUILDROOT " + package.getChrootRpmBuildTmpDirectory())
        command.append("ln -sf " + package.getChrootRpmBuildDirectory() + "/RPMS " + package.getChrootRpmBuildTmpDirectory())
        command.append("ln -sf " + package.getChrootRpmBuildDirectory() + "/SOURCES " + package.getChrootRpmBuildTmpDirectory())
        command.append("ln -sf " + package.getChrootRpmBuildDirectory() + "/SRPMS " + package.getChrootRpmBuildTmpDirectory())

        command.append("chown -R root:users " + package.getChrootRpmBuildTmpDirectory())
        command.append("chmod -R g+rwX " + package.getChrootRpmBuildTmpDirectory())

        command.append("git --git-dir=" + pathPackage + "/.git --work-tree=" + pathPackage + \
                       " archive --format=tar --prefix=" + tmpPath + "/ HEAD \
                       | (cd " + package.getChrootRpmBuildTmpDirectory() + "/TMP/ && tar xf -)")

        command.append("cd " + package.getChrootRpmBuildTmpDirectory() + "/TMP/")
        command.append("tar -czvf  " + tarFile + " *")
        command.append("mv " + tarFile + " ../SOURCES")
        self.execCommand(command=command)
        pathToSaveSpec = specFile.replace(package.getChrootRpmBuildDirectory(),
                                          package.getChrootRpmBuildTmpDirectory())

        package.saveTmpSpec(path=self.getDirectory() + pathToSaveSpec,
                            archive=tarFile)
        command = []
        command.append("rpmbuild -ba --define '_srcdefattr (-,root,root)' " +
                       "--define '%_topdir %{getenv:HOME}/" +
                       package.getTopDirRpmBuildTmpDirectory() +
                       "' " + pathToSaveSpec + " < /dev/null")
        command.append("cp -fpr  " + package.getChrootRpmBuildTmpDirectory() + "/BUILD/* " + package.getChrootRpmBuildDirectory() + "/BUILD/")
        command.append("rm -r " + package.getChrootRpmBuildTmpDirectory() + "/TMP")

        self.execCommand(command=command)
        #self.__changeTopDir(package.getTopDirRpmBuildDirectory())

#    def __changeTopDir(self, newTopDir):
#        '''
#        
#        '''
#        command = []
#        command.append("chown -R root:users " + "/usr/lib/rpm")
#        command.append("chmod -R g+rw " + "/usr/lib/rpm")
#        self.execCommand(command=command)
#
#        with open(self.getDirectory() + "/usr/lib/rpm/macros", 'r') as cfgFile:
#            content = cfgFile.read()
#        newContent = re.sub(r'(\%_topdir\s*\%{getenv:HOME}/).*', r'\1%s' % newTopDir, content)
#        with open(self.getDirectory() + "/usr/lib/rpm/macros", 'w') as cfgFile:
#            cfgFile.write(newContent)

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
        command.append("git --work-tree=" + path + " --git-dir=" + path + "/.git commit -a -m \"first commit\"")
        self.execCommand(command=command)

    def ignoreGitWatch(self, path=None):
        '''
        Initialize a Git repository in the specified path, and 'git add' everything.
        '''
        if path == None:
            raise ObsLightErr.ObsLightChRootError("path is not defined in initGitWatch.")

        command = []
        command.append("git --work-tree=" + path + " --git-dir=" + path + "/.git status -u -s | sed -e 's/^[ \t]*//' | cut -d' ' -f2 >> " + path + "/.gitignore")
        command.append("echo debugfiles.list >> " + path + "/.gitignore")
        command.append("echo debuglinks.list >> " + path + "/.gitignore")
        command.append("echo debugsources.list >> " + path + "/.gitignore")
        command.append("echo *.in >> " + path + "/.gitignore")
        command.append("git --work-tree=" + path + " --git-dir=" + path + "/.git add " + path + "/.gitignore")
        command.append("git --work-tree=" + path + " --git-dir=" + path + "/.git commit -a -m \"first build commit\"")
        self.execCommand(command=command)

    def getCommitTag(self, path):
        '''
        
        '''
        command = []
        resultFile = "commitTag.log"
        command.append("git --work-tree=" + path + " --git-dir=" + path + "/.git log HEAD --pretty=short -n 1 > " + self.__dirTransfert + "/" + resultFile)
        self.execCommand(command=command)

        result = []
        f = open(self.__chrootDirTransfert + "/" + resultFile, 'r')
        for line in f:
            result.append(line)
        f.close()

        for line in result:
            if line.startswith("commit "):
                res = line.strip("commit ").rstrip("\n")
                return res

    def commitGit(self, mess, package):
        '''
        
        '''

        path = package.getPackageDirectory()
        command = []
        command.append("git --work-tree=" + path + " --git-dir=" + path +
                       "/.git add " + path + "/\*")
        command.append("git --work-tree=" + path + " --git-dir=" + path +
                       "/.git commit -a -m \"" + mess + "\"")
        self.execCommand(command=command)

    def makePatch(self, package=None, patch=None):
        '''
        Create a patch from modifications made in the package directory.
        '''
        if not patch.endswith(".patch"):
            patch += ".patch"
        pathPackage = package.getPackageDirectory()
        pathOscPackage = package.getOscDirectory()

        self.commitGit(mess="makePatch", package=package)

        tag1 = package.getFirstCommit()
        if tag1 == None:
            raise ObsLightErr.ObsLightChRootError("package: '" + package.getName() + "' has no git first tag.")
        tag2 = self.getCommitTag(path=pathPackage)

        command = []
        command.append("git --git-dir=" + pathPackage + "/.git --work-tree=" + pathPackage +
                       " diff -p -a --binary " + tag1 + " " + tag2 + " > " + self.__dirTransfert + "/" + patch)
        self.execCommand(command=command)
        shutil.copy(self.__chrootDirTransfert + "/" + patch, pathOscPackage + "/" + patch)

        package.addPatch(aFile=patch)
        ObsLightOsc.getObsLightOsc().add(path=pathOscPackage, afile=patch)
        package.save()

    def updatePatch(self, package=None):
        '''
        Update a patch from modifications made in the package directory.
        '''
        patch = package.getCurrentPatch()
        pathPackage = package.getPackageDirectory()
        pathOscPackage = package.getOscDirectory()

        self.commitGit(mess="updatePatch", package=package)

        tag1 = package.getFirstCommit()
        if tag1 == None:
            raise ObsLightErr.ObsLightChRootError("package: '" + package.getName() + "' has no git first tag.")
        tag2 = self.getCommitTag(path=pathPackage)

        command = []
        command.append("git --git-dir=" + pathPackage + "/.git --work-tree=" + pathPackage +
                       " diff -p -a --binary " + tag1 + " " + tag2 + " > " + self.__dirTransfert + "/" + patch)
        self.execCommand(command=command)
        shutil.copy(self.__chrootDirTransfert + "/" + patch, pathOscPackage + "/" + patch)
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

