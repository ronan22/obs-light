#
# Copyright 2011-2012, Intel Inc.
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
@author: Florent Vennetier
'''

import os
import time
import platform
import shlex
import shutil
import subprocess
import urllib

import ObsLightOsc
import ObsLightMic

import ObsLightErr
import ObsLightConfig
from ObsLightSubprocess import SubprocessCrt
from ObsLightTools import isUserInGroup

import ObsLightPrintManager
import copy

class ObsLightChRoot(object):
    '''
    chroot-related operations of an OBS project.
    '''

    ObsLightUserGroup = "users"

    def __init__(self,
                 projectDirectory,
                 fromSave=None):

        '''
        Constructor
        '''
        self.__projectDirectory = projectDirectory
        self.__chrootDirectory = os.path.join(projectDirectory, "aChroot")
        self.__chrootDirTransfert = os.path.join(projectDirectory, "chrootTransfert")
        self.__dirTransfert = "/chrootTransfert"

        self.__mySubprocessCrt = SubprocessCrt()
        self.hostArch = platform.machine()

        if fromSave == None:
            self.__dicoRepos = {}
        else:
            if "dicoRepos" in fromSave.keys():
                self.__dicoRepos = copy.copy(fromSave["dicoRepos"])
        self.initChRoot()


    @property
    def projectDirectory(self):
        return self.__projectDirectory

    @staticmethod
    def prepareGitCommand(workTree, subcommand, gitDir="../.git_obslight"):
        """
        Construct a Git command-line, setting its working tree to `workTree`,
        and then appends `subcommand`.
        Output example:
          git --git-dir=<workTree>/[gitDir] --work-tree=<workTree> <subcommand>
        """
        command = "git --git-dir=%s/%s --work-tree=%s " % (workTree,
                                                           gitDir,
                                                           workTree)
        command += subcommand
        return command

    @staticmethod
    def makeArchiveGitSubcommand(outputFilePath, prefix, revision=u"HEAD"):
        """
        Construct a Git 'archive' subcommand with tar format,
        piped on gzip to produce a .tar.gz file.
        """
        command = "archive --format=tar --prefix=%s/ %s | gzip > %s"
        command = command % (prefix, revision, outputFilePath)
        return command

    def getChrootDirTransfert(self):
        return self.__chrootDirTransfert

    def getDirectory(self):
        ''' 
        Return the path of aChRoot of a project
        '''
        return self.__chrootDirectory

    def failIfAclsNotReady(self):
        """
        Raise an exception if ACLs are not enabled on the filesystem
        where the current project is located.
        """
        def getmount(path):
            """Get the mount point of the filesystem where `path` is located."""
            path = os.path.abspath(path)
            while path != os.path.sep:
                if os.path.ismount(path):
                    return path
                path = os.path.abspath(os.path.join(path, os.pardir))
            return path

        def areAclsReady(path):
            """Check if ACLs are enabled on filesystem where `path` is located."""
            # chacl will fail with return code 1 if it can't get ACLs
            retCode = self.__subprocess("chacl -l %s" % path)
            return retCode == 0

        if not areAclsReady(self.projectDirectory):
            mountPoint = getmount(self.projectDirectory)
            message = "ACLs are not enabled on mount point '%s'. "
            message += "Use the following command as root to enable them:\n\n"
            message += "  mount -o remount,acl %s"
            raise ObsLightErr.ObsLightChRootError(message % (mountPoint, mountPoint))

    def failIfUserNotInUserGroup(self):
        """
        Raise an exception if the user running this program is not member
        of the user group defined by OBS Light (self.ObsLightUserGroup).
        This is required for the custom sudo rules to apply.
        """
        if not isUserInGroup(self.ObsLightUserGroup):
            message = "You are not in the '%s' group. " % self.ObsLightUserGroup
            message += "Please add yourself in this group:\n"
            message += "  sudo usermod -a -G %s `whoami`\n" % self.ObsLightUserGroup
            message += "then logout and login again."
            raise ObsLightErr.ObsLightChRootError(message)

    def removeChRoot(self):
        if  ObsLightMic.getObsLightMic(name=self.getDirectory()).isInit():
            ObsLightMic.destroy(name=self.getDirectory())

        self.failIfUserNotInUserGroup()

        if os.path.isdir(self.getDirectory()):
            return self.__subprocess(command="sudo rm -r  " + self.getDirectory())

        return 0

    def isInit(self):
        res = os.path.isdir(self.getDirectory())

        if res and os.path.isfile(os.path.join(self.getDirectory(), ".chroot.lock")):
            if not ObsLightMic.isInit(name=self.getDirectory()):
                ObsLightMic.getObsLightMic(name=self.getDirectory()).initChroot(chrootDirectory=self.getDirectory(),
                                                                                chrootTransfertDirectory=self.__chrootDirTransfert,
                                                                                transfertDirectory=self.__dirTransfert)
        return res

    def initChRoot(self):
        if not os.path.isdir(self.__chrootDirTransfert):
            os.makedirs(self.__chrootDirTransfert)

    def getDic(self):
        saveconfigPackages = {}
        saveconfigPackages["dicoRepos"] = self.__dicoRepos
        return saveconfigPackages

    def fixFsRights(self):
        errorMessage = "Failed to configure project filesystem access rights. "
        errorMessage += "Commandline was:\n %s"

        def raiseErrorIfNonZero(command):
            """
            Run `command` in subprocess and raise an error if return code
            differs from zero.
            """
            retCode = self.__subprocess(command)
            if retCode != 0:
                raise ObsLightErr.ObsLightChRootError(errorMessage % command)

        # The path of the root of the project filesystem
        fsPath = self.getDirectory()

        self.__subprocess("sudo chmod -R o+rwX %s" % fsPath)
        # This command often returns 1 for broken symlinks, but we don't care
        self.__subprocess("sudo setfacl -Rdm o::rwX -m g::rwX -m u::rwX %s" % fsPath)

        cmdList = ["sudo chown root:users %s" % fsPath,
                   "sudo chown root:users %s" % os.path.join(fsPath, "root"),
                   "sudo chown root:users %s" % os.path.join(fsPath, "etc"),
                   "sudo chmod g+rwX %s" % fsPath,
                   "sudo chmod g+rwX %s" % os.path.join(fsPath, "root"),
                   "sudo chmod g+rwX %s" % os.path.join(fsPath, "etc"),
                   "sudo chown -R root:users %s" % os.path.join(fsPath, "usr", "lib", "rpm"),
                   "sudo chmod -R g+rwX %s" % os.path.join(fsPath, "usr", "lib", "rpm")]
        for command in cmdList:
            raiseErrorIfNonZero(command)

    def createChRoot(self, repos,
                           arch,
                           apiurl,
                           obsProject):

        self.failIfUserNotInUserGroup()
        self.failIfAclsNotReady()

        fsPath = self.getDirectory()
        res = ObsLightOsc.getObsLightOsc().createChRoot(chrootDir=fsPath,
                                                        repos=repos,
                                                        arch=arch,
                                                        apiurl=apiurl,
                                                        project=obsProject,
                                                        )

        if res != 0:
            message = "Can't create the project file system. "
            message += "See the log for details about the error."
            raise ObsLightErr.ObsLightChRootError(message)

        self.fixFsRights()
        self.initRepos()

        retVal = self.prepareChroot(self.getDirectory(), obsProject)
        if retVal != 0:
            return retVal
        return self.setTimezoneInBashrc()

    def __subprocess(self, command=None):
        return self.__mySubprocessCrt.execSubprocess(command)

    def __resolveMacro(self, name):
        if not os.path.isdir(self.getDirectory()):
            message = "project file system is not initialized"
            raise ObsLightErr.ObsLightChRootError(message)
        elif not os.path.isdir(self.getDirectory()):
            raise ObsLightErr.ObsLightChRootError("'%s' is not a directory" % self.getDirectory())

        if  not ObsLightMic.getObsLightMic(name=self.getDirectory()).isInit():
            ObsLightMic.getObsLightMic(name=self.getDirectory()).initChroot(chrootDirectory=self.getDirectory(),
                                                                               chrootTransfertDirectory=self.__chrootDirTransfert,
                                                                               transfertDirectory=self.__dirTransfert)

        self.failIfUserNotInUserGroup()

        command = "rpm --eval " + name + " > /chrootTransfert/resultRpmQ.log"

        pathScript = self.__chrootDirTransfert + "/runMe.sh"
        f = open(pathScript, 'w')
        f.write("#!/bin/sh\n")
        f.write("# Created by obslight\n")
        f.write(command)
        f.close()

        os.chmod(pathScript, 0654)

        command = "sudo -H chroot " + self.getDirectory() + " " + self.__dirTransfert + "/runMe.sh"

        if self.hostArch == 'x86_64':
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
                raise ObsLightErr.ObsLightChRootError("'%s' is not a directory" % pathBuild)
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

        listDir = [item for item in os.listdir(pathBuild) if (os.path.isdir(pathBuild + "/" + item) and
                                                              (not item.startswith(".git")))]

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
            package.setChRootStatus("many BUILD directories")
            raise ObsLightErr.ObsLightChRootError("Too many sub-directories in '%s'" % pathBuild)

    def getChRootRepositories(self):
        return self.__dicoRepos

    def __getProxyconfig(self):
        command = []
        proxies = urllib.getproxies_environment()
        for scheme in proxies.keys():
            if scheme == 'http':
                command.append('export HTTP_PROXY=' + proxies[scheme])
                command.append('export http_proxy=' + proxies[scheme])

            if scheme == 'https':
                command.append('export HTTPS_PROXY=' + proxies[scheme])
                command.append('export https_proxy=' + proxies[scheme])
        return command


    def installBuildRequires(self, package, listPackageBuildRequires):
        if len(listPackageBuildRequires) == 0:
            return 0

        command = []
        command.append("zypper --no-gpg-checks --gpg-auto-import-keys ref")
        cmd = "zypper --non-interactive in --force-resolution "
        for pk in listPackageBuildRequires:
            if pk.count("-") >= 2:
                lastMinus = pk.rfind("-")
                cutMinus = pk.rfind("-", 0, lastMinus)
                # OBS sometimes returns "future" build numbers, and dependency
                # resolution fails. So with forget build number.
                pkCmd = '"' + pk[:cutMinus] + ">=" + pk[cutMinus + 1:lastMinus] + '"'
            else:
                pkCmd = pk
            cmd += " " + pkCmd
        command.append(cmd)
        res = self.execCommand(command=command)

        if res != 0:
            msg = "The installation of some dependencies of '%s' failed\n" % package.getName()
            msg += "Maybe a repository is missing."
            raise ObsLightErr.ObsLightChRootError(msg)

        return res

    def addPackageSourceInChRoot(self, package,
                                       specFile,
                                       repo):

        if package.getStatus() == "excluded":
            message = "%s has a excluded status, it can't be installed"
            raise ObsLightErr.ObsLightChRootError(message % package.getName())
        elif specFile is None:
            raise ObsLightErr.ObsLightChRootError("%s has no spec file" % package.getName())
        else:
            self.failIfUserNotInUserGroup()
            packageName = package.getName()

            command = []
            mkdirCommand = "mkdir -p %s"
            chrootRpmBuildDirectory = package.getChrootRpmBuildDirectory()

            command.append("rm -fr %s" % chrootRpmBuildDirectory)
            for directory in ["BUILD", "SPECS", "BUILDROOT", "RPMS", "SOURCES", "SRPMS"]:
                command.append(mkdirCommand % os.path.join(chrootRpmBuildDirectory, directory))

            command.append("chown  root:users " + chrootRpmBuildDirectory)
            command.append("chmod  g+rwX " + chrootRpmBuildDirectory)

            for c in self.__getProxyconfig():
                command.append(c)

            res = self.execCommand(command=command)

            specDirPath = self.getDirectory() + "/" + chrootRpmBuildDirectory + "/SPECS/"
            if os.path.isdir(specDirPath):

                command = "sudo chown root:users %s" % self.getDirectory()
                self.__subprocess(command)
                command = "sudo chmod g+rwX %s" % self.getDirectory()
                self.__subprocess(command)
                command = "sudo chown  root:users " + self.getDirectory() + "/root"
                self.__subprocess(command)
                command = "sudo chmod  g+rwX " + self.getDirectory() + "/root"
                self.__subprocess(command)
                command = "sudo chown -R root:users %s/root/%s" % (self.getDirectory(), packageName)
                self.__subprocess(command)
                command = "sudo chmod -R g+rwX %s/root/%s" % (self.getDirectory(), packageName)
                self.__subprocess(command)

                aspecFile = chrootRpmBuildDirectory + "/SPECS/" + specFile
                package.saveSpec(self.getDirectory() + "/" + aspecFile)

                macroDirectory = os.path.join(self.getDirectory(), "root")
                macroDest = os.path.join(self.getDirectory(), "root", package.getName())

                if not os.path.isfile(os.path.join(macroDest, ".rpmmacros")):
                    shutil.copy2(os.path.join(macroDirectory, ".rpmmacros"), macroDest)
                if not os.path.isfile(os.path.join(macroDest, ".rpmrc")):
                    shutil.copy2(os.path.join(macroDirectory, ".rpmrc"), macroDest)

                if package.specFileHaveAnEmptyPrepAndBuild():
                    package.setChRootStatus("No build directory")
                    return 0

                #find the directory to watch
                for aFile in package.getListFile():
                    path = "%s/%s/SOURCES/%s" % (self.getDirectory(),
                                                 chrootRpmBuildDirectory,
                                                 str(aFile))
                    if os.path.isfile(path):
                        os.unlink(path)
                    shutil.copy2(package.getOscDirectory() + "/" + str(aFile), path)
                    self.__subprocess(command="sudo chown -R root:users " + path)

                res = self.prepRpm(specFile=aspecFile, package=package)
                if res != 0:
                    msg = "The first %%prep of package '%s' failed. " % packageName
                    msg += "Return code was: %s" % str(res)
                    raise ObsLightErr.ObsLightChRootError(msg)


                package.initCurrentPatch()
                packageDirectory = self.__findPackageDirectory(package=package)
                message = "Package directory used by '%s': %s" % (packageName,
                                                                  str(packageDirectory))
                ObsLightPrintManager.getLogger().debug(message)
                package.setDirectoryBuild(packageDirectory)
                if packageDirectory != None:
                    self.__subprocess(command="sudo chmod -R og+rwX %s"
                                      % (self.getDirectory() + "/" + packageDirectory))
                    self.initGitWatch(packageDirectory, package)
                    res = self.__buildRpm(specFile=aspecFile, package=package)

                    if res == 0:
                        self.ignoreGitWatch(package=package,
                                            path=packageDirectory)
                        package.setFirstCommit(tag=self.getCommitTag(packageDirectory,
                                                                     package))
                        package.setChRootStatus("Prepared")
                    else:
                        msg = "The first build of package '%s' failed." % packageName
                        msg += " Return code was: %s" % str(res)
                        raise ObsLightErr.ObsLightChRootError(msg)
            else:
                message = packageName + " source is not installed in " + self.getDirectory()
                raise ObsLightErr.ObsLightChRootError(message)
            return res

    def execCommand(self, command=None):
        '''
        Execute a list of commands in the chroot.
        '''
        if command is None:
            return

        self.failIfUserNotInUserGroup()

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
        f.write("#!/bin/sh -x\n")
        f.write("# Created by obslight\n\n")
#        f.write("set -x\n")
        for c in command:
            f.write(c + "\n")
        f.close()

        os.chmod(scriptPath, 0654)

        aCommand = "sudo -H chroot " + self.getDirectory() + " " + self.__dirTransfert + "/" + scriptName
        if self.hostArch == 'x86_64':
            aCommand = "linux32 " + aCommand

        return self.__subprocess(command=aCommand)

    def execScript(self, aPath):
        '''
        Execute a list of commands in the chroot.
        '''
        self.failIfUserNotInUserGroup()

        if not ObsLightMic.getObsLightMic(name=self.getDirectory()).isInit():
            ObsLightMic.getObsLightMic(name=self.getDirectory()).initChroot(chrootDirectory=self.getDirectory(),
                                                                            chrootTransfertDirectory=self.__chrootDirTransfert,
                                                                         transfertDirectory=self.__dirTransfert)
        if os.path.isfile(aPath):
            scriptName = os.path.basename(aPath)
        else:
            raise ObsLightErr.ObsLightChRootError("The file '" + aPath + "' do not exit, can't exec script.")

        scriptPath = self.__chrootDirTransfert + "/" + scriptName
        shutil.copy2(aPath, scriptPath)

        self.testOwnerChRoot()

        os.chmod(scriptPath, 0654)

        aCommand = "sudo -H chroot " + self.getDirectory() + " " + self.__dirTransfert + "/" + scriptName
        if self.hostArch == 'x86_64':
            aCommand = "linux32 " + aCommand

        return self.__subprocess(command=aCommand)


    def testOwnerChRoot(self):
        if os.stat(self.getDirectory()).st_uid != 0:
            msg = "The path '%s' is not owned by root." % self.getDirectory()
            raise ObsLightErr.ObsLightChRootError(msg)

    def addRepo(self, repos=None, alias=None):
        '''
        Add a repository in the chroot's zypper configuration file.
        '''
        if alias in self.__dicoRepos.keys():
            msg = "Can't add %s, already configured in project file system" % alias
            raise ObsLightErr.ObsLightChRootError(msg)
        else:
            self.__dicoRepos[alias] = repos

        return self.__addRepo(repos=repos, alias=alias)

    def initRepos(self):
        '''
        init all the repos in the chroot.
        '''
        for alias in self.__dicoRepos.keys():
            self.__addRepo(repos=self.__dicoRepos[alias], alias=alias)

    def isAlreadyAReposAlias(self, alias):
        if alias in self.__dicoRepos.keys():
            return True
        else:
            return False

    def __addRepo(self, repos=None, alias=None):
        command = []
        for c in self.__getProxyconfig():
            command.append(c)

        command.append("zypper ar " + repos + " '" + alias + "'")
        command.append("zypper --no-gpg-checks --gpg-auto-import-keys ref")
        return self.execCommand(command=command)

    def prepRpm(self, specFile, package):
        '''
        Execute the %prep section of an RPM spec file.
        '''
        buildDir = "/root/" + package.getName() + "/" + package.getTopDirRpmBuildDirectory()
        buildLink = "/root/" + package.getName() + "/" + package.getTopDirRpmBuildLinkDirectory()
        srcdefattr = "--define '_srcdefattr (-,root,root)'"
        topdir = "--define '%_topdir %{getenv:HOME}/" + package.getTopDirRpmBuildLinkDirectory() + "'"

        rpmbuilCmd = "rpmbuild -bp %s %s %s < /dev/null" % (srcdefattr,
                                                            topdir,
                                                            specFile.replace(buildDir, buildLink))

        command = []
        command.append("HOME=/root/" + package.getName())
        command.append("rm  " + buildLink)
        command.append("ln -s %s %s" % (buildDir, buildLink))
        command.append(rpmbuilCmd)
        command.append("RPMBUILD_RETURN_CODE=$?")
        command.append("find %s -type f -name .gitignore -exec rm -v {} \; -print" % os.path.join(buildDir, "BUILD"))
        command.append("exit $RPMBUILD_RETURN_CODE")
        return self.execCommand(command=command)

    def __buildRpm(self, specFile, package):
        '''
        Execute the %build section of an RPM spec file.
        '''
        buildDir = "/root/" + package.getName() + "/" + package.getTopDirRpmBuildDirectory()
        buildLink = "/root/" + package.getName() + "/" + package.getTopDirRpmBuildLinkDirectory()

        srcdefattr = "--define '_srcdefattr (-,root,root)'"
        topdir = "--define '%_topdir %{getenv:HOME}/" + package.getTopDirRpmBuildLinkDirectory() + "'"

        rpmbuilCmd = "rpmbuild -bc --short-circuit %s %s %s < /dev/null" % (srcdefattr, topdir, specFile)

        command = []

        command.append("HOME=/root/" + package.getName())
        command.append("rm  " + buildLink)
        command.append("ln -s %s %s" % (buildDir, buildLink))
        command.append(rpmbuilCmd)
        command.append("RPMBUILD_RETURN_CODE=$?")
        command.append("exit $RPMBUILD_RETURN_CODE")
        return self.execCommand(command=command)

    def __prepGhostRpmbuild(self, package, specFile, packagePath, tarFile):
        buildDirTmp = "/root/" + package.getName() + "/" + package.getTopDirRpmBuildTmpDirectory()
        buildDir = "/root/" + package.getName() + "/" + package.getTopDirRpmBuildDirectory()
        buildLink = "/root/" + package.getName() + "/" + package.getTopDirRpmBuildLinkDirectory()

        command = []
        command.append("rm -r %s/*" % buildDirTmp)
        command.append("mkdir -p %s/BUILD" % buildDirTmp)
        command.append("mkdir -p %s/SPECS" % buildDirTmp)
        command.append("mkdir -p %s/TMP" % buildDirTmp)

        command.append("ln -sf %s/BUILDROOT %s" % (buildDir, buildDirTmp))
        command.append("ln -sf %s/RPMS %s" % (buildDir, buildDirTmp))
        command.append("ln -sf %s/SOURCES %s" % (buildDir, buildDirTmp))
        command.append("ln -sf %s/SRPMS %s" % (buildDir, buildDirTmp))

        command.append("chown -R root:users %s" % buildDirTmp)
        command.append("chmod -R g+rwX %s" % buildDirTmp)

        outputFilePath = os.path.join(buildDirTmp, "SOURCES", tarFile)

        tmpPath = packagePath.replace(buildDir + "/BUILD", "").strip("/")
        tmpPath = tmpPath.strip("/")
        command.append(self.prepareGitCommand(packagePath,
                                              self.makeArchiveGitSubcommand(outputFilePath,
                                                                            prefix=tmpPath),
                                              package.getCurrentGitDirectory()))

        self.execCommand(command=command)

        pathToSaveSpec = specFile.replace(buildDir, buildDirTmp)
        package.saveTmpSpec(path=self.getDirectory() + pathToSaveSpec, archive=tarFile)

        return pathToSaveSpec

    def __createGhostRpmbuildCommand(self, command, package, pathToSaveSpec):
        buildDirTmp = "/root/" + package.getName() + "/" + package.getTopDirRpmBuildTmpDirectory()
        buildDir = "/root/" + package.getName() + "/" + package.getTopDirRpmBuildDirectory()
        buildLink = "/root/" + package.getName() + "/" + package.getTopDirRpmBuildLinkDirectory()

        srcdefattr = "--define '_srcdefattr (-,root,root)'"
        topdir = "--define '%_topdir %{getenv:HOME}/" + package.getTopDirRpmBuildLinkDirectory() + "'"
        rpmbuilCmd = "rpmbuild -%s %s %s %s < /dev/null" % (command,
                                                            srcdefattr,
                                                            topdir,
                                                            pathToSaveSpec.replace(buildDirTmp, buildLink))

        command = []
        command.append("HOME=/root/" + package.getName())
        command.append("rm  " + buildLink)
        command.append("ln -s %s %s" % (buildDirTmp, buildLink))
        command.append(rpmbuilCmd)
        command.append("RPMBUILD_RETURN_CODE=$?")
        command.append("cp -fpr  %s/BUILD/* %s/BUILD/" % (buildDirTmp, buildDir))
        command.append("rm -r %s/TMP" % buildDirTmp)
        command.append("rm  " + buildLink)
        command.append("ln -s %s %s" % (buildDir, buildLink))
        command.append("exit $RPMBUILD_RETURN_CODE")
        return self.execCommand(command=command)

    def buildRpm(self, package, specFile, packagePath, tarFile):
        '''
        Execute the %build section of an RPM spec file.
        '''
        if package.getStatus() == "excluded":
            msg = u"Package '%s' has a excluded status, it can't be build" % package.getName()
            raise ObsLightErr.ObsLightChRootError(msg)

        self.commitGit(mess="build", package=package)

        pathToSaveSpec = self.__prepGhostRpmbuild(package, specFile, packagePath, tarFile)
        res = self.__createGhostRpmbuildCommand("bc", package, pathToSaveSpec)

        self.ignoreGitWatch(package=package,
                            path=package.getPackageDirectory(),
                            commitComment="build commit",
                            firstBuildCommit=False)
        if res == 0:
            package.setChRootStatus("Built")
        return res

    def installRpm(self, package, specFile, packagePath, tarFile):
        '''
        Execute the %install section of an RPM spec file.
        '''
        if package.getStatus() == "excluded":
            msg = u"Package '%s' has a excluded status, it can't be install" % package.getName()
            raise ObsLightErr.ObsLightChRootError(msg)

        self.commitGit(mess="install", package=package)

        pathToSaveSpec = self.__prepGhostRpmbuild(package, specFile, packagePath, tarFile)
        res = self.__createGhostRpmbuildCommand("bi", package, pathToSaveSpec)

        self.ignoreGitWatch(package=package,
                            path=package.getPackageDirectory(),
                            commitComment="build install commit",
                            firstBuildCommit=False)
        if res == 0:
            package.setChRootStatus("Build Installed")
        return res

    def packageRpm(self, package, specFile, packagePath, tarFile):
        '''
        Execute the package section of an RPM spec file.
        '''
        if package.getStatus() == "excluded":
            msg = u"Package '%s' has a excluded status, it can't be package" % package.getName()
            raise ObsLightErr.ObsLightChRootError(msg)

        self.commitGit(mess="packageRpm", package=package)

        pathToSaveSpec = self.__prepGhostRpmbuild(package, specFile, packagePath, tarFile)
        res = self.__createGhostRpmbuildCommand("ba", package, pathToSaveSpec)

        self.ignoreGitWatch(package=package,
                            path=package.getPackageDirectory(),
                            commitComment="build package commit",
                            firstBuildCommit=False)
        if res == 0:
            package.setChRootStatus("Build Packaged")
        return res

    def goToChRoot(self, path=None, detach=False, project=None):
        '''
        Go to the chroot.
        Open a Bash in the chroot.
        '''
        if not os.path.isdir(self.getDirectory()):
            msg = "Project file system not initialized"
            raise ObsLightErr.ObsLightChRootError(msg)
        elif not os.path.isdir(self.getDirectory()):
            raise ObsLightErr.ObsLightChRootError("'%s' is not a directory" % self.getDirectory())

        self.failIfUserNotInUserGroup()

        if  not ObsLightMic.getObsLightMic(name=self.getDirectory()).isInit():
            ObsLightMic.getObsLightMic(name=self.getDirectory()).initChroot(chrootDirectory=self.getDirectory(),
                                                                               chrootTransfertDirectory=self.__chrootDirTransfert,
                                                                               transfertDirectory=self.__dirTransfert)
        # FIXME: project should be accessible by self.project
        # instead of method parameter
        if project is not None:
            title = "chroot jail of %s" % project
        else:
            title = "chroot jail"
        pathScript = self.__chrootDirTransfert + "/runMe.sh"
        f = open(pathScript, 'w')
        f.write("#!/bin/sh\n")
        f.write("# Created by obslight\n")
        if path != None:
            f.write("cd " + path + "\n")
        # control code to change window title
        f.write('echo -en "\e]2;%s\a"\n' % title)
        f.write("exec bash\n")
        f.close()

        os.chmod(pathScript, 0654)

        command = "sudo -H chroot " + self.getDirectory() + " " + self.__dirTransfert + "/runMe.sh"
        if detach is True:
            command = ObsLightConfig.getConsole(title) + " " + command
        if self.hostArch == 'x86_64':
            command = "linux32 " + command

        command = shlex.split(str(command))
        message = "Opening console in chroot jail"
        ObsLightPrintManager.getLogger().info(message)
        # subprocess.call(command) waits for command to finish, which causes
        # problem with terminal emulators which don't fork themselves.
        subprocess.Popen(command)

    def initGitWatch(self, path, package):
        '''
        Initialize a Git repository in the specified path, and 'git add' everything.
        '''
        if path == None:
            raise ObsLightErr.ObsLightChRootError("Path is not defined in initGitWatch.")

        timeString = time.strftime("%Y-%m-%d_%Hh%Mm%Ss")
        comment = '\"auto commit first commit %s\"' % timeString

        command = []
        command.append(self.prepareGitCommand(path,
                                              "init ",
                                              package.getCurrentGitDirectory()))
        command.append(self.prepareGitCommand(path,
                                              "add " + path + "/\*",
                                              package.getCurrentGitDirectory()))
        command.append(self.prepareGitCommand(path,
                                              "commit -a -m %s" % comment,
                                              package.getCurrentGitDirectory()))
        self.execCommand(command=command)

    def ignoreGitWatch(self, package, path=None, commitComment="first build commit", firstBuildCommit=True):
        '''
        Add all Git untracked files of `path` to .gitignore
        and commit.
        '''
        if path == None:
            raise ObsLightErr.ObsLightChRootError("path is not defined in initGitWatch.")

        timeString = time.strftime("%Y-%m-%d_%Hh%Mm%Ss")
        comment = '\"auto commit %s %s\"' % (commitComment, timeString)

        command = []
        command.append(self.prepareGitCommand(path,
                                              u"status -u -s | sed -e 's/^[ \t]*//' " +
                                              u"| cut -d' ' -f2 >> %s/.gitignore" % path,
                                              package.getCurrentGitDirectory()))
        if firstBuildCommit:
            command.append("echo debugfiles.list >> " + path + "/.gitignore")
            command.append("echo debuglinks.list >> " + path + "/.gitignore")
            command.append("echo debugsources.list >> " + path + "/.gitignore")
            command.append("echo *.in >> " + path + "/.gitignore")
            command.append(self.prepareGitCommand(path,
                                                  u"add " + path + "/.gitignore",
                                                  package.getCurrentGitDirectory()))
        command.append(self.prepareGitCommand(path,
                                              u"commit -a -m %s" % comment,
                                              package.getCurrentGitDirectory()))
        self.execCommand(command=command)

    def getCommitTag(self, path, package):
        '''
        Get the last Git commit hash.
        '''
        command = []
        resultFile = "commitTag.log"
        command.append(self.prepareGitCommand(path,
                                              " log HEAD --pretty=short -n 1 > " +
                                              self.__dirTransfert + "/" + resultFile,
                                              package.getCurrentGitDirectory()))
        self.execCommand(command=command)

        result = []
        with open(self.__chrootDirTransfert + "/" + resultFile, 'r') as f:
            for line in f:
                result.append(line)

        for line in result:
            if line.startswith("commit "):
                res = line.strip("commit ").rstrip("\n")
                return res

    def getListCommitTag(self, path, package):
        '''
        Get the last Git commit hash.
        '''
        command = []
        resultFile = "commitTag.log"
        command.append(self.prepareGitCommand(path,
                                              " log HEAD --pretty=short -n 20 > " +
                                              self.__dirTransfert + "/" + resultFile,
                                              package.getCurrentGitDirectory()))
        self.execCommand(command=command)

        result_tmp = []
        with open(self.__chrootDirTransfert + "/" + resultFile, 'r') as f:
            for line in f:
                result_tmp.append(line)

        result = []
        for line in result_tmp:
            if line.startswith("commit "):
                res = line.strip("commit ").rstrip("\n")
                result.append((res, "Comment"))
        return result

    def commitGit(self, mess, package):
        packagePath = package.getPackageDirectory()
        command = []
        if packagePath == None:
            raise ObsLightErr.ObsLightChRootError("path is not defined in commitGit for .")

        timeString = time.strftime("%Y-%m-%d_%Hh%Mm%Ss")
        comment = '\"auto commit %s %s\"' % (mess, timeString)

        command.append(self.prepareGitCommand(packagePath,
                                              " add %s/\*" % packagePath,
                                              package.getCurrentGitDirectory()))
        command.append(self.prepareGitCommand(packagePath,
                                              " commit -a -m %s" % comment,
                                              package.getCurrentGitDirectory()))
        self.execCommand(command=command)

        tag2 = self.getCommitTag(packagePath, package)
        package.setSecondCommit(tag2)

    def createPatch(self, package=None, patch=None):
        '''
        Create a patch from modifications made in the package directory.
        '''
        if not patch.endswith(".patch"):
            patch += ".patch"
        packagePath = package.getPackageDirectory()
        pathOscPackage = package.getOscDirectory()

        self.commitGit(mess="createPatch", package=package)

        tag1 = package.getFirstCommit()
        if tag1 == None:
            raise ObsLightErr.ObsLightChRootError("package: '" + package.getName() +
                                                  "' has no git first tag.")
        tag2 = package.getSecondCommit()

        command = []
        command.append(self.prepareGitCommand(packagePath,
                                              "diff -p -a --binary %s %s > %s/%s" % (tag1,
                                                                                     tag2,
                                                                                     self.__dirTransfert,
                                                                                     patch),
                                              package.getCurrentGitDirectory()))
        self.execCommand(command=command)
        shutil.copy(self.__chrootDirTransfert + "/" + patch, pathOscPackage + "/" + patch)

        package.addPatch(aFile=patch)
        ObsLightOsc.getObsLightOsc().add(path=pathOscPackage, afile=patch)
        package.save()
        return 0

    def updatePatch(self, package=None):
        '''
        Update a patch from modifications made in the package directory.
        '''
        patch = package.getCurrentPatch()
        packagePath = package.getPackageDirectory()
        pathOscPackage = package.getOscDirectory()

        self.commitGit(mess="updatePatch", package=package)

        tag1 = package.getFirstCommit()
        if tag1 == None:
            raise ObsLightErr.ObsLightChRootError("package: '" + package.getName() +
                                                  "' has no git first tag.")
        tag2 = package.getSecondCommit()

        command = []
        command.append(self.prepareGitCommand(packagePath,
                                              "diff -p -a --binary %s %s > %s/%s" % (tag1,
                                                                                     tag2,
                                                                                     self.__dirTransfert,
                                                                                     patch),
                                              package.getCurrentGitDirectory()))
        self.execCommand(command=command)
        shutil.copy(self.__chrootDirTransfert + "/" + patch, pathOscPackage + "/" + patch)
        package.save()
        return 0

    def setTimezoneInBashrc(self):
        """
        Get the time zone of the current user and sets the TZ variable
        in chroot jail's .bashrc file. Executing it several times may
        result in duplicated lines.
        Returns 0 on success.
        """
        # These commands have not been appended to prepareChroot() so
        # we can call them separately.
        command = []
        tzname = time.tzname[0]
        msg = "Setting chroot jail's time zone to '%s'" % tzname
        ObsLightPrintManager.getLogger().info(msg)
        command.append('echo "TZ=\\"%s\\"" >> ~/.bashrc' % tzname)
        command.append('echo "export TZ" >> ~/.bashrc')
        return self.execCommand(command)

    def prepareChroot(self, chrootDir, project):
        '''
        Prepare the chroot :
        - replaces some binaries by their ARM equivalent (in case chroot is ARM)
        - configures zypper and rpm for ARM
        - rebuilds rpm database
        - customize .bashrc
        '''
        command = []

        if ObsLightMic.getObsLightMic(name=self.getDirectory()).isArmArch(chrootDir):
            # If rpm and rpmbuild binaries are not ARM, replace them by ARM versions
            command.append('[ -z "$(file /bin/rpm | grep ARM)" -a -f /bin/rpm.orig-arm ]'
                + ' && cp /bin/rpm /bin/rpm.x86 && cp /bin/rpm.orig-arm /bin/rpm')
            command.append('[ -z "$(file /usr/bin/rpmbuild ' +
                           '| grep ARM)" -a -f /usr/bin/rpmbuild.orig-arm ]' +
                           ' && cp /usr/bin/rpmbuild /usr/bin/rpmbuild.x86 ' +
                           '&& cp /usr/bin/rpmbuild.orig-arm /usr/bin/rpmbuild')
            # Remove the old (broken ?) RPM database
            command.append('rm -f /var/lib/rpm/__db*')
            # Force zypper and rpm to use armv7hl architecture
            command.append("echo 'arch = armv7hl' >> /etc/zypp/zypp.conf")
            command.append("echo -n 'armv7hl-meego-linux' > /etc/rpm/platform")

        command.append("rpm --initdb")
        command.append("rpm --rebuilddb")

        for c in self.__getProxyconfig():
            command.append('echo "' + c + '" >> ~/.bashrc')

        command.append('echo "alias ll=\\"ls -lh --color\\"" >> ~/.bashrc')
        command.append('echo "alias la=\\"ls -Alh --color\\"" >> ~/.bashrc')
        command.append('echo "alias vi=\\"vim\\"" >> ~/.bashrc')
        prompt = {"blue": "\\[\\e[34;1m\\]",
                  "green": "\\[\\e[32;1m\\]",
                  "default": "\\[\\e[0m\\]",
                  "path": "\\w",
                  "delimiter": "\\\\$ ",
                  "project": project}
        PS1 = "%(blue)s%(project)s:%(green)s%(path)s%(default)s%(delimiter)s" % prompt
        command.append('echo "PS1=\\"%s\\"" >> ~/.bashrc' % PS1)
        command.append('echo "export PS1" >> ~/.bashrc')
        return self.execCommand(command=command)

    def deleteRepo(self, repoAlias):
        if repoAlias in self.__dicoRepos.keys():
            command = []
            for c in self.__getProxyconfig():
                command.append(c)
            command.append("zypper rr " + repoAlias)
            command.append("zypper --no-gpg-checks --gpg-auto-import-keys ref")
            self.execCommand(command=command)
            del self.__dicoRepos[repoAlias]
            return 0
        else:
            raise ObsLightErr.ObsLightChRootError("Can't delete the repo '" + repoAlias + "'")

    def modifyRepo(self, repoAlias, newUrl, newAlias):
        if newUrl == None:
            newUrl = self.__dicoRepos[repoAlias]

        self.deleteRepo(repoAlias)

        if newAlias == None:
            newAlias = repoAlias

        self.__addRepo(newUrl, newAlias)

        return self.addRepo(repos=newUrl, alias=newAlias)
