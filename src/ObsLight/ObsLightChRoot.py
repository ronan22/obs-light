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

import ObsLightMic

import ObsLightErr
import ObsLightConfig
from ObsLightSubprocess import SubprocessCrt
from ObsLightTools import isUserInGroup

import ObsLightPrintManager
import copy

from ObsLightGitManager import ObsLightGitManager
from ObsLightRepoManager import ObsLightRepoManager

from ObsLightUtils import isNonEmptyString

import ObsLightOsc

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
        self.__transferDir = "/chrootTransfert"
        self.__chrootTransferDir = os.path.join(projectDirectory, "chrootTransfert")

        self.__oscCacheDir = ObsLightOsc.getObsLightOsc().getOscPackagecachedir()
        self.__chrootOscCacheDir = self.__oscCacheDir

        self.__ObsLightGitManager = ObsLightGitManager(self)
        self.__ObsLightRepoManager = ObsLightRepoManager(self)

        self.__mySubprocessCrt = SubprocessCrt()
        self.hostArch = platform.machine()
        self.chrootArch = ""
        self.logger = ObsLightPrintManager.getLogger()
        self.__obsLightMic = None

        if fromSave is None:
            self.__dicoRepos = {}
        else:
            if "dicoRepos" in fromSave.keys():
                self.__dicoRepos = copy.copy(fromSave["dicoRepos"])
        self.initChRoot()

    def __initChroot(self):
        mountDir = {}
        mountDir[self.__transferDir] = self.__chrootTransferDir
        mountDir[self.__oscCacheDir] = self.__chrootOscCacheDir
        self.obsLightMic.initChroot(chrootDirectory=self.getDirectory(), mountDir=mountDir)

    def initChRoot(self):
        if not os.path.isdir(self.__chrootTransferDir):
            os.makedirs(self.__chrootTransferDir)
        if not os.path.isdir(self.__chrootOscCacheDir):
            os.makedirs(self.__chrootOscCacheDir)

    @property
    def projectDirectory(self):
        return self.__projectDirectory

    def getChrootDirTransfert(self):
        return self.__chrootTransferDir

    def getDirectory(self):
        ''' 
        Return the path of aChRoot of a project 
        '''
        return self.__chrootDirectory

    @property
    def obsLightMic(self):
        if self.__obsLightMic is None:
            self.__obsLightMic = ObsLightMic.getObsLightMic(self.getDirectory())
        return self.__obsLightMic

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

    def failIfQemuIsNotStatic(self):
        """
        Raise an exception if host does not have a static version of qemu.
        Do nothing if we do not need qemu.
        """
        if self.chrootArch.lower().startswith("arm"):
            self.logger.info("Project has ARM architecture, checking qemu...")
            # TODO: check if the qemu is statically linked
            return

    def removeChRoot(self):
        if self.obsLightMic.isInit():
            ObsLightMic.destroy(name=self.getDirectory())

        self.failIfUserNotInUserGroup()

        if os.path.isdir(self.getDirectory()):
            return self.__subprocess(command="sudo rm -r  " + self.getDirectory())

        return 0

    def isInit(self):
        res = os.path.isdir(self.getDirectory())

        if res and os.path.isfile(os.path.join(self.getDirectory(), ".chroot.lock")):
            if not ObsLightMic.isInit(name=self.getDirectory()):
                self.__initChroot()

        return res

    def getDic(self):
        saveconfigPackages = {}
        saveconfigPackages["dicoRepos"] = self.__dicoRepos
        return saveconfigPackages

    def allowAccessToObslightGroup(self, path, recursive=False,
                                   writeAccess=True, absolutePath=True):
        """
        Modify ACLs on `path` so users of "obslight" group have read/write/execute rights.
        `recursive` changes ACLs recursively, `writeAccess` enables/disables write right,
        `absolutePath` prevents from prefixing `path` with chroot jail path.
        """
        if not absolutePath:
            path = self.getDirectory() + "path"
        rec = "-R" if recursive else ""
        rights = "rwX" if writeAccess else "rX"
        msg = "Giving group '%s' access rights (%s) to %s" % (self.ObsLightUserGroup,
                                                              rights, path)
        self.logger.info(msg)
        return self.__subprocess("sudo setfacl %s -m g:%s:%s %s" % (rec, self.ObsLightUserGroup,
                                                                    rights, path))

    def allowPackageAccessToObslightGroup(self, package):
        """
        Modify ACLs on package files so users of obslight group have read/write/execute rights.
        """
        path = self.getDirectory() + "/" + package.getChrootRpmBuildDirectory() + "/BUILD"
        cmd = "sudo setfacl -R -m g:%(group)s:%(rights)s -d -m g:%(group)s:%(rights)s %(path)s"
        cmd = cmd % {"group": self.ObsLightUserGroup, "rights": "rwX", "path": path}
        msg = "Giving group '%s' access rights (%s) to %s" % (self.ObsLightUserGroup,
                                                              "rwX", path)
        self.logger.info(msg)
        return self.__subprocess(cmd)

    def forbidPackageAccessToObslightGroup(self, package):
        """
        Undo `allowPackageAccessToObslightGroup`, with the exception of the "BUILD" directory
        itself, which has to be write-able by obslight.
        """
        path = self.getDirectory() + "/%s/BUILD"
        path1 = path % package.getChrootRpmBuildDirectory()
        path2 = path % package.getChrootRpmBuildTmpDirectory()
        msg = "Removing group '%s' access rights to %s"
        self.logger.info(msg % (self.ObsLightUserGroup, path1))
        cmd = "sudo setfacl -R -x g:%(group)s -d -x g:%(group)s %(path)s"
        retval1 = self.__subprocess(cmd % {"group": self.ObsLightUserGroup, "path": path1})
        self.logger.info(msg % (self.ObsLightUserGroup, path1))
        retval2 = self.__subprocess(cmd % {"group": self.ObsLightUserGroup, "path": path2})
        self.allowAccessToObslightGroup(path1, False, True, True)

        return retval1, retval2

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

        self.allowAccessToObslightGroup(fsPath, recursive=True, writeAccess=True)

        # Some of these commands may be useless since we set ACLs
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
        self.chrootArch = arch

        self.failIfUserNotInUserGroup()
        self.failIfAclsNotReady()
        self.failIfQemuIsNotStatic()

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

    def __subprocess(self, command=None, **kwargs):
        return self.__mySubprocessCrt.execSubprocess(command, **kwargs)

    def __resolveMacro(self, name):
        if not os.path.isdir(self.getDirectory()):
            message = "project file system is not initialized"
            raise ObsLightErr.ObsLightChRootError(message)
        elif not os.path.isdir(self.getDirectory()):
            raise ObsLightErr.ObsLightChRootError("'%s' is not a directory" % self.getDirectory())

        if not self.obsLightMic.isInit():
            self.__initChroot()

        self.failIfUserNotInUserGroup()

        command = "rpm --eval " + name + " > /chrootTransfert/resultRpmQ.log"

        pathScript = self.__chrootTransferDir + "/runMe.sh"
        f = open(pathScript, 'w')
        f.write("#!/bin/sh\n")
        f.write("# Created by obslight\n")
        f.write(command)
        f.close()

        os.chmod(pathScript, 0654)

        command = "sudo -H chroot " + self.getDirectory() + " " + self.__transferDir + "/runMe.sh"

        if self.hostArch == 'x86_64':
            command = "linux32 " + command

        command = shlex.split(str(command))
        p = subprocess.Popen(command, stdout=None)
        p.wait()
        f = open(self.__chrootTransferDir + "/resultRpmQ.log", 'r')
        name = f.read().replace("\n", "")
        f.close()
        return name

    #Old perhaps to del.
    def __findPackageDirectory_bis(self, package=None):
        '''
        Return the directory of where the package were installed.
        '''
        name = package.getMacroDirectoryPackageName()

        if name is not None:
            prepDirname = self.__resolveMacro(name)
            if prepDirname is None:
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
        Return the directory of where the package was installed.
        '''
        pathBuild = self.getDirectory() + "/" + package.getChrootRpmBuildDirectory() + "/" + "BUILD"
        if not os.path.isdir(pathBuild):
            raise ObsLightErr.ObsLightChRootError("The path '" + pathBuild + "' is not a directory")

        listDir = [item for item in os.listdir(pathBuild) if (os.path.isdir(pathBuild + "/" + item) and
                                                              (not item.startswith(".git")))]

        if len(listDir) == 0:
            package.setPackageParameter("patchMode", False)
            package.setChRootStatus("No build directory")
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
            package.setPackageParameter("patchMode", False)
            package.setChRootStatus("Many BUILD directories")
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


    def addPackageSpecInChRoot(self, package,
                                     specFile,
                                     section,
                                     configPath,
                                     arch,
                                     configdir,
                                     buildDir):
        if specFile is None:
            raise ObsLightErr.ObsLightChRootError("%s has no spec file" % package.getName())

        patchMode = package.getPackageParameter("patchMode")

        if patchMode and not section == "prep":
            chrootRpmBuildDirectory = package.getChrootRpmBuildTmpDirectory()
        else:
            chrootRpmBuildDirectory = package.getChrootRpmBuildDirectory()

        aSpecFile = os.path.join(chrootRpmBuildDirectory, "SPECS", specFile)

        absSpecFile = os.path.join(self.getDirectory() , aSpecFile.strip("/"))

        absSpecFile_tmp = absSpecFile[:-5] + ".tmp.spec"

        if patchMode and not section == "prep":
            tarFile = package.getArchiveName()
            package.saveTmpSpec(path=absSpecFile_tmp, archive=tarFile)
        elif section == "prep":
            package.saveSpec(absSpecFile_tmp)
        else:
            package.saveSpec(absSpecFile_tmp)
#            package.saveSpecShortCut(absSpecFile_tmp, section)

        command = '%s/substitutedeps --root %s --dist "%s" --archpath "%s" --configdir "%s" %s %s'
        command = command % (buildDir,
                             self.getDirectory(),
                             configPath,
                             arch,
                             configdir,
                             absSpecFile_tmp,
                             absSpecFile)
        self.__subprocess(command)

        return aSpecFile

    def addPackageSourceInChRoot(self, package):

        if package.getStatus() == "excluded":
            message = "%s has a excluded status, it can't be installed"
            raise ObsLightErr.ObsLightChRootError(message % package.getName())
        else:
            self.failIfUserNotInUserGroup()
            packageName = package.getName()

            command = []
            mkdirCommand = "mkdir -p %s"
            chrootRpmBuildDirectory = package.getChrootRpmBuildDirectory()

            command.append("rm -fr %s" % chrootRpmBuildDirectory)
            rpmbuildDirectories = ["BUILD", "SPECS", "BUILDROOT", "RPMS", "SOURCES", "SRPMS"]
            for directory in rpmbuildDirectories:
                command.append(mkdirCommand % os.path.join(chrootRpmBuildDirectory, directory))

            command.append("chown  root:users " + chrootRpmBuildDirectory)

            for c in self.__getProxyconfig():
                command.append(c)

            res = self.execCommand(command=command)

            specDirPath = self.getDirectory() + "/" + chrootRpmBuildDirectory + "/SPECS/"
            self.allowAccessToObslightGroup(specDirPath)
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

                macroDirectory = os.path.join(self.getDirectory(), "root")
                macroDest = os.path.join(self.getDirectory(), "root", package.getName())

                self.allowAccessToObslightGroup(macroDest)
                if not os.path.isfile(os.path.join(macroDest, ".rpmmacros")):
                    shutil.copy2(os.path.join(macroDirectory, ".rpmmacros"), macroDest)
                if not os.path.isfile(os.path.join(macroDest, ".rpmrc")):
                    shutil.copy2(os.path.join(macroDirectory, ".rpmrc"), macroDest)

                self.allowAccessToObslightGroup("%s/%s/SOURCES/" % (self.getDirectory(),
                                                                    chrootRpmBuildDirectory))
                #copy source
                for aFile in package.getFileList():
                    path = "%s/%s/SOURCES/%s" % (self.getDirectory(),
                                                 chrootRpmBuildDirectory,
                                                 str(aFile))
                    if os.path.isfile(path):
                        os.unlink(path)
                    shutil.copy2(package.getOscDirectory() + "/" + str(aFile), path)
                    self.__subprocess(command="sudo chown -R root:users " + path)
            else:
                message = packageName + " source is not installed in " + self.getDirectory()
                raise ObsLightErr.ObsLightChRootError(message)
            return res

    def makeRpmbuildScriptParameters(self, specFile, package, target="", args=""):
        parameters = dict()
        parameters["packageName"] = package.getName()
        parameters["buildDir"] = "/root/%s/%s" % (parameters["packageName"],
                                                  package.getTopDirRpmBuildDirectory())
        parameters["buildLink"] = "/root/%s/%s" % (parameters["packageName"],
                                                   package.getTopDirRpmBuildLinkDirectory())
        srcdefattr = "--define '_srcdefattr (-,root,root)'"
        topdir = "--define '_topdir %%{getenv:HOME}/%s'" % package.getTopDirRpmBuildLinkDirectory()
        if isNonEmptyString(target):
            args = args + " --target=%s" % target
        rpmbuildCmd = "rpmbuild %s %s %s %s << /dev/null" % (args, srcdefattr, topdir, specFile)
        parameters["rpmbuildCmd"] = rpmbuildCmd
        return parameters

    # TODO: replace 'arch' by 'target'
    def prepRpm(self, specFile, package, arch):
        '''
        Execute the %prep section of an RPM spec file.
        '''
        scriptParameters = self.makeRpmbuildScriptParameters(specFile, package, arch, "-bp")
        #We need to rename all the .gitignore file to do not disturb the git management
        script = """HOME=/root/%(packageName)s
rm -f %(buildLink)s
ln -s %(buildDir)s %(buildLink)s
chown -R root:users %(buildDir)s
%(rpmbuildCmd)s
RETURN_VALUE=$?
find %(buildDir)s/BUILD -type f -name .gitignore -execdir mv .gitignore .gitignore.obslight  \;
exit $RETURN_VALUE
"""
        script = script % scriptParameters
        res = self.execCommand([script])

        if res != 0:
            msg = "The first %%prep of package '%s' failed. " % package.getName()
            msg += "Return code was: %s" % str(res)
            raise ObsLightErr.ObsLightChRootError(msg)

        packageDirectory = self.__findPackageDirectory(package=package)
        message = "Package directory used by '%s': %s" % (package.getName(),
                                                          str(packageDirectory))
        ObsLightPrintManager.getLogger().debug(message)
        package.setDirectoryBuild(packageDirectory)

        if package.getPackageParameter("patchMode"):
            package.initCurrentPatch()

            if packageDirectory is not None:
                # TODO: check if we can remove this
                # We shouldn't need to write to package directory anymore
                self.__subprocess(command="sudo chmod og+rwX %s"
                                  % (self.getDirectory() + "/" + packageDirectory))

                self.__ObsLightGitManager.initGitWatch(packageDirectory, package)

                if package.specFileHaveAnEmptyBuild():
                    package.setChRootStatus("No build directory")
                    return 0

                return self.__buildRpm(specFile, package, arch)

        else:
            package.setChRootStatus("Prepared")


        return 0

    def __buildRpm(self, specFile, package, arch):
        '''
        Execute the %build section of an RPM spec file.
        '''
        scriptParameters = self.makeRpmbuildScriptParameters(specFile, package, arch,
                                                             "-bc --short-circuit")
        script = """HOME=/root/%(packageName)s
rm -f %(buildLink)s
ln -s %(buildDir)s %(buildLink)s
%(rpmbuildCmd)s
exit $?
"""
        script = script % scriptParameters
        res = self.execCommand([script])

        packageName = package.getName()
        packageDirectory = package.getPackageDirectory()

        if res == 0:
            self.__ObsLightGitManager.ignoreGitWatch(package=package, path=packageDirectory)
            package.setFirstCommit(tag=self.__ObsLightGitManager.getCommitTag(packageDirectory,
                                                                              package))
            package.setChRootStatus("Prepared")
        else:
            msg = "The first build of package '%s' failed." % packageName
            msg += " Return code was: %s" % str(res)
            raise ObsLightErr.ObsLightChRootError(msg)
        return 0

    # TODO: replace 'arch' by 'target'
    def buildRpm(self, package, specFile, arch):
        '''
        Execute the %build section of an RPM spec file.
        '''
        if package.getStatus() == "excluded":
            msg = u"Package '%s' has a excluded status, it can't be built" % package.getName()
            raise ObsLightErr.ObsLightChRootError(msg)
        if package.specFileHaveAnEmptyBuild():
            package.setChRootStatus("No build directory")
            return 0
        if package.getPackageParameter("patchMode"):

            self.__ObsLightGitManager.commitGit(mess="build", package=package)

            res = self.__createGhostRpmbuildCommand("bc", package, specFile, arch)

            self.__ObsLightGitManager.ignoreGitWatch(package=package,
                                                     path=package.getPackageDirectory(),
                                                     commitComment="build commit",
                                                     firstBuildCommit=False)
        else:
            res = self.__createRpmbuildCommand("bc", package, specFile, arch)
        if res == 0:
#            if package.getChRootStatus() in ["Not installed",
#                                            "No build directory",
#                                            "Many BUILD directories"]:
#                packageDirectory = self.__findPackageDirectory(package=package)
#                message = "Package directory used by '%s': %s" % (package.getName(),
#                                                          str(packageDirectory))
#                ObsLightPrintManager.getLogger().debug(message)
#                package.setDirectoryBuild(packageDirectory)
            package.setChRootStatus("Built")
        return res

    # TODO: replace 'arch' by 'target'
    def installRpm(self, package, specFile, arch):
        '''
        Execute the %install section of an RPM spec file.
        '''

        if package.getStatus() == "excluded":
            msg = u"Package '%s' has a excluded status, it can't be install" % package.getName()
            raise ObsLightErr.ObsLightChRootError(msg)

        if package.getPackageParameter("patchMode"):
            self.__ObsLightGitManager.commitGit(mess="install", package=package)

            res = self.__createGhostRpmbuildCommand("bi", package, specFile, arch)

            self.__ObsLightGitManager.ignoreGitWatch(package=package,
                                                    path=package.getPackageDirectory(),
                                                    commitComment="build install commit",
                                                    firstBuildCommit=False)
        else:
            res = self.__createRpmbuildCommand("bi", package, specFile, arch)

        if res == 0:
#            if package.getChRootStatus() in ["Not installed",
#                                            "No build directory",
#                                            "Many BUILD directories"]:
#                packageDirectory = self.__findPackageDirectory(package=package)
#                message = "Package directory used by '%s': %s" % (package.getName(),
#                                                          str(packageDirectory))
#                ObsLightPrintManager.getLogger().debug(message)
#                package.setDirectoryBuild(packageDirectory)

            package.setChRootStatus("Build Installed")
        return res

    # TODO: replace 'arch' by 'target'
    def packageRpm(self, package, specFile, arch):
        '''
        Execute the package section of an RPM spec file.
        '''

        if package.getStatus() == "excluded":
            msg = u"Package '%s' has a excluded status, it can't be package" % package.getName()
            raise ObsLightErr.ObsLightChRootError(msg)

        if package.getPackageParameter("patchMode"):
            self.__ObsLightGitManager.commitGit(mess="packageRpm", package=package)

            res = self.__createGhostRpmbuildCommand("ba", package, specFile, arch)

            self.__ObsLightGitManager.ignoreGitWatch(package=package,
                                                    path=package.getPackageDirectory(),
                                                    commitComment="build package commit",
                                                    firstBuildCommit=False)
        else:
            res = self.__createRpmbuildCommand("ba", package, specFile, arch)

        if res == 0:
#            if package.getChRootStatus() in ["Not installed",
#                                            "No build directory",
#                                            "Many BUILD directories"]:
#                packageDirectory = self.__findPackageDirectory(package=package)
#                message = "Package directory used by '%s': %s" % (package.getName(),
#                                                          str(packageDirectory))
#                ObsLightPrintManager.getLogger().debug(message)
#                package.setDirectoryBuild(packageDirectory)

            package.setChRootStatus("Build Packaged")
        return res

    def prepGhostRpmbuild(self, package):
        packagePath = package.getPackageDirectory()
        tarFile = package.getArchiveName()

        buildDirTmp = "/root/" + package.getName() + "/" + package.getTopDirRpmBuildTmpDirectory()
        buildDir = package.getTopDirRpmBuildDirectory()
        buildDirPath = "/root/" + package.getName() + "/" + buildDir
#        buildLink = "/root/" + package.getName() + "/" + package.getTopDirRpmBuildLinkDirectory()

        command = []
        command.append("rm -r %s/*" % buildDirTmp)
        command.append("mkdir -p %s/BUILD" % buildDirTmp)
        command.append("mkdir -p %s/SPECS" % buildDirTmp)
        command.append("mkdir -p %s/TMP" % buildDirTmp)

        command.append("ln -sf ../%s/BUILDROOT %s" % (buildDir, buildDirTmp))
        command.append("ln -sf ../%s/RPMS %s" % (buildDir, buildDirTmp))
        command.append("ln -sf ../%s/SOURCES %s" % (buildDir, buildDirTmp))
        command.append("ln -sf ../%s/SRPMS %s" % (buildDir, buildDirTmp))

        command.append("chown -R root:users %s" % buildDirTmp)
        command.append("chmod -R g+rwX %s" % buildDirTmp)

        outputFilePath = os.path.join(buildDirTmp, "SOURCES", tarFile)

        tmpPath = packagePath.replace(buildDirPath + "/BUILD", "").strip("/")
        tmpPath = tmpPath.strip("/")
        _ = self.execCommand(command=command)

        res = self.__ObsLightGitManager.execMakeArchiveGitSubcommand(packagePath,
                                                                    outputFilePath,
                                                                    tmpPath,
                                                                    package.getCurrentGitDirectory())

        return res

    def __createRpmbuildCommand(self, command, package, pathToSpec, arch):
        scriptParameters = self.makeRpmbuildScriptParameters(pathToSpec, package, target=arch,
                                                             args="-%s" % command)
        script = """HOME=/root/%(packageName)s
rm -f %(buildLink)s
ln -s %(buildDir)s %(buildLink)s
chown -R root:users %(buildLink)s/SOURCES/
chown -R root:users %(buildLink)s/SPECS/
%(rpmbuildCmd)s
exit $?
"""
        script = script % scriptParameters
        return self.execCommand([script])

    def __createGhostRpmbuildCommand(self, command, package, pathToSpec, arch):
        scriptParameters = self.makeRpmbuildScriptParameters(pathToSpec, package,
                                                             target=arch, args="-%s" % command)
        script = """HOME=/root/%(packageName)s
rm -f %(buildLink)s
ln -s %(buildDirTmp)s %(buildLink)s
chown -R root:users %(buildLink)s/SOURCES/
chown -R root:users %(buildLink)s/SPECS/
%(rpmbuildCmd)s
RPMBUILD_RETURN_CODE=$?
cp -fpr %(buildDirTmpPath)s/BUILD/* %(buildDir)s/BUILD/
rm -r %(buildDirTmpPath)s/TMP
rm -f %(buildLink)s
ln -s %(buildDir)s %(buildLink)s
exit $RPMBUILD_RETURN_CODE
"""
        scriptParameters["buildDirTmp"] = package.getTopDirRpmBuildTmpDirectory()
        scriptParameters["buildDirTmpPath"] = "/root/%s/%s" % (package.getName(),
                                                               scriptParameters["buildDirTmp"])
        script = script % scriptParameters
        return self.execCommand([script])

    def execCommand(self, command=None):
        '''
        Execute a list of commands in the chroot.
        '''
        if command is None:
            return

        self.failIfUserNotInUserGroup()

        if not self.obsLightMic.isInit():
            self.__initChroot()

        self.testOwnerChRoot()
        # Need more than second %S
        timeString = time.strftime("%Y-%m-%d_%Hh%Mm") + str(time.time() % 1).split(".")[1]

        scriptName = "runMe_" + timeString + ".sh"
        scriptPath = self.__chrootTransferDir + "/" + scriptName

        f = open(scriptPath, 'w')
        f.write("#!/bin/sh -x\n")
        f.write("# Created by obslight\n\n")

        # Warning
        f.write("if [ -e /root/.bashrc ] ; then . /root/.bashrc ; fi\n")
        # When OBS Light is used in graphic mode (without console), the commands like "tput"
        # need a value for TERM other than "unknown" (xterm, linux,...)
        f.write('if [ "$TERM" = "unknown" ] ; then TERM="xterm" ; fi\n')

        for c in command:
            f.write(c + "\n")
        f.close()

        os.chmod(scriptPath, 0654)

        aCommand = "sudo -H chroot %s %s/%s"
        aCommand = aCommand % (self.getDirectory(), self.__transferDir, scriptName)

        if self.hostArch == 'x86_64':
            aCommand = "linux32 " + aCommand

        return self.__subprocess(command=aCommand)

    def execScript(self, aPath):
        '''
        Execute a list of commands in the chroot.
        '''
        self.failIfUserNotInUserGroup()

        if not self.obsLightMic.isInit():
            self.__initChroot()

        if os.path.isfile(aPath):
            scriptName = os.path.basename(aPath)
        else:
            message = "The file '" + aPath + "' do not exit, can't exec script."
            raise ObsLightErr.ObsLightChRootError(message)

        scriptPath = self.__chrootTransferDir + "/" + scriptName
        shutil.copy2(aPath, scriptPath)

        self.testOwnerChRoot()

        os.chmod(scriptPath, 0654)

        aCommand = "sudo -H chroot %s %s/%s"
        aCommand = aCommand % (self.getDirectory(), self.__transferDir, scriptName)


        if self.hostArch == 'x86_64':
            aCommand = "linux32 " + aCommand

        return self.__subprocess(command=aCommand)

    def testOwnerChRoot(self):
        if os.stat(self.getDirectory()).st_uid != 0:
            msg = "The path '%s' is not owned by root." % self.getDirectory()
            raise ObsLightErr.ObsLightChRootError(msg)

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

        if not self.obsLightMic.isInit():
            self.__initChroot()

        # FIXME: project should be accessible by self.project
        # instead of method parameter
        if project is not None:
            title = "chroot jail of %s" % project
        else:
            title = "chroot jail"
        pathScript = self.__chrootTransferDir + "/runMe.sh"
        f = open(pathScript, 'w')
        f.write("#!/bin/sh\n")
        f.write("# Created by obslight\n")
        if path is not None:
            f.write("cd " + path + "\n")
        # control code to change window title
        f.write('echo -en "\e]2;%s\a"\n' % title)
        f.write("exec bash\n")
        f.close()

        os.chmod(pathScript, 0654)

        command = "sudo -H chroot " + self.getDirectory() + " " + self.__transferDir + "/runMe.sh"
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

    def createPatch(self, package=None, patch=None):
        '''
        Create a patch from modifications made in the package directory.
        '''
        if not patch.endswith(".patch"):
            patch += ".patch"
        packagePath = package.getPackageDirectory()

        self.__ObsLightGitManager.commitGit(mess="createPatch", package=package)

        tag1 = package.getFirstCommit()
        if tag1 is None:
            raise ObsLightErr.ObsLightChRootError("package: '" + package.getName() +
                                                  "' has no git first tag.")
        tag2 = package.getSecondCommit()
        self.__ObsLightGitManager.createPatch(package, packagePath, tag1, tag2, patch)

        package.addPatch(aFile=patch)

        ObsLightOsc.getObsLightOsc().add(path=package.getOscDirectory(), afile=patch)
        package.save()
        return 0

    def updatePatch(self, package=None):
        '''
        Update a patch from modifications made in the package directory.
        '''
        patch = package.getCurrentPatch()
        packagePath = package.getPackageDirectory()

        self.__ObsLightGitManager.commitGit(mess="updatePatch", package=package)

        tag1 = package.getFirstCommit()
        if tag1 is None:
            raise ObsLightErr.ObsLightChRootError("package: '" + package.getName() +
                                                  "' has no git first tag.")
        tag2 = package.getSecondCommit()

        self.__ObsLightGitManager.createPatch(package, packagePath, tag1, tag2, patch)

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
        - adds group "user" if it does not exist
        '''
        command = []

        # Not all distro have "user" group, obslight needs it for acl and directory management. 
        command.append("if ! egrep '^users:' >/dev/null </etc/group ; then echo 'users::100:' >>/etc/group ;fi")
        command.append("if ! egrep '^root:' >/dev/null </etc/group ; then echo 'root:x:0:' >>/etc/group ;fi")

        # We need "root" user too.
        command.append("if ! egrep '^root:' >/dev/null </etc/passwd ; then echo 'root:x:0:0:root:/root:/bin/sh' >>/etc/passwd; fi")
        command.append("if ! egrep '^root:' >/dev/null </etc/shadow ; then echo 'root:*:15484:0:99999:7:::' >>/etc/shadow ; fi")
        command.append("if ! egrep '^root:' >/dev/null </etc/gshadow ; then echo 'root:*::' >>/etc/gshadow ; fi")

        # FIXME: is this still required ?
        # We need a "/etc/zypp/repos.d" directory.
        command.append("mkdir -p /etc/zypp/repos.d")
        command.append("chown -R root:users /etc/zypp/repos.d")
        command.append("chmod g+rwX etc/zypp/repos.d")

        # Tizen ARM chroot jails work without this.
        # TODO: test with MeeGo
#        if self.obsLightMic.isArmArch(chrootDir):
#            # If rpm and rpmbuild binaries are not ARM, replace them by ARM versions
#            command.append('[ -z "$(file /bin/rpm | grep ARM)" -a -f /bin/rpm.orig-arm ]'
#                + ' && cp /bin/rpm /bin/rpm.x86 && cp /bin/rpm.orig-arm /bin/rpm')
#            command.append('[ -z "$(file /usr/bin/rpmbuild ' +
#                           '| grep ARM)" -a -f /usr/bin/rpmbuild.orig-arm ]' +
#                           ' && cp /usr/bin/rpmbuild /usr/bin/rpmbuild.x86 ' +
#                           '&& cp /usr/bin/rpmbuild.orig-arm /usr/bin/rpmbuild')
#            # Remove the old (broken ?) RPM database
#            command.append('rm -f /var/lib/rpm/__db*')
#            # Force zypper and rpm to use armv7hl architecture
#            command.append("echo 'arch = armv7hl' >> /etc/zypp/zypp.conf")
#            command.append("echo -n 'armv7hl-meego-linux' > /etc/rpm/platform")


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


#Manage the repository of the chroot jail
#_____________________________________________________________________________
    def addRepo(self, repos=None, alias=None):
        '''
        Add a repository in the chroot's zypper configuration file.
        '''
        if alias in self.__dicoRepos.keys():
            msg = "Can't add %s, already configured in project file system" % alias
            raise ObsLightErr.ObsLightChRootError(msg)
        else:
            self.__dicoRepos[alias] = repos

        return self.__ObsLightRepoManager.addRepo(repos=repos, alias=alias)

    def initRepos(self):
        '''
        init all the repos in the chroot.
        '''
        for alias in self.__dicoRepos.keys():
            self.__ObsLightRepoManager.addRepo(repos=self.__dicoRepos[alias], alias=alias)

    def isAlreadyAReposAlias(self, alias):
        if alias in self.__dicoRepos.keys():
            return True
        else:
            return False

    def modifyRepo(self, repoAlias, newUrl, newAlias):
        if newUrl is None:
            newUrl = self.__dicoRepos[repoAlias]

        self.__ObsLightRepoManager.deleteRepo(repoAlias)

        if newAlias is None:
            newAlias = repoAlias

        self.__ObsLightRepoManager.addRepo(newUrl, newAlias)

        return self.addRepo(repos=newUrl, alias=newAlias)


    def deleteRepo(self, repoAlias):
        if repoAlias in self.__dicoRepos.keys():
            res = self.__ObsLightRepoManager.deleteRepo(repoAlias)
            del self.__dicoRepos[repoAlias]
            return res
        else:
            raise ObsLightErr.ObsLightChRootError("Can't delete the repo '" + repoAlias + "'")

    def installBuildRequires(self, buildInfoCli):
        command = []

        for i in buildInfoCli.deps:
            if not ((i in buildInfoCli.preinstall_list) or(i in buildInfoCli.vminstall_list)) :
                absPath = i.fullfilename
                pkgName = os.path.basename(i.fullfilename)
                if pkgName.endswith(".rpm"):
                    pkgName = pkgName[:-4]

                testInstall = "rpm --quiet -q " + pkgName
                installCommand = "rpm --nodeps --ignorearch -i '%s'" % absPath

                cmd = "if ! %s ; then %s || exit 1; fi" % (testInstall, installCommand)
                command.append(cmd)


        return self.execCommand(command=command)

#        return self.__ObsLightRepoManager.installBuildRequires(packageName, dicoPackageBuildRequires, arch)
#_____________________________________________________________________________

