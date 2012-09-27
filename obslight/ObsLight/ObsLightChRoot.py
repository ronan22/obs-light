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
import re
import time
import platform
import shlex
import shutil
import subprocess
import urllib

import stat

import ObsLightMic

import ObsLightErr
import ObsLightConfig
from ObsLightSubprocess import SubprocessCrt
import ObsLightTools
from ObsLightTools import isUserInGroup

import ObsLightPrintManager

from ObsLightGitManager import ObsLightGitManager

from ObsLightUtils import isNonEmptyString

import ObsLightOsc

import ObsLightPackageStatus as PK_CONST

class ObsLightChRootCore(object):
    '''
    chroot-related operations of an OBS project.
    '''
    def __init__(self, projectDirectory):
        self.__projectDirectory = None
        self.__chrootDirectory = None
        self.__transferDir = None
        self.__chrootTransferDir = None
        self.__oscCacheDir = None
        self.__chrootOscCacheDir = None
        self.__chrootUser = None
        self.__chrootUsersHome = None
        self.__chrootgroup = None
        self.__chrootUsersUID = None
        self.__chrootUsersGID = None
        self.__obsLightMic = None
        self.__chrootUserHome = None

        self.__setDirectory(projectDirectory)

        self.ObsLightUserGroup = "users"
        self.ObsLightUserGroupGID = "100"
        self.setUser("abuild")

        self._ObsLightGitManager = ObsLightGitManager(self)

        self.__mySubprocessCrt = SubprocessCrt()
        self.hostArch = platform.machine()

        self.chrootArch = ""
        self.logger = ObsLightPrintManager.getLogger()

        self.__initChRootAddDir()

    def __setDirectory(self, projectDirectory):
        self.__projectDirectory = projectDirectory
        self.__chrootDirectory = os.path.join(projectDirectory, "aChroot")
        self.__transferDir = "/chrootTransfert"
        self.__chrootTransferDir = os.path.join(projectDirectory, "chrootTransfert")

        self.__oscCacheDir = ObsLightOsc.getObsLightOsc().getOscPackagecachedir()
        self.__chrootOscCacheDir = self.__oscCacheDir

    def makeChrootScriptParameters(self):
        parameters = dict()
        parameters["usersHome"] = self.__chrootUsersHome
        parameters["userHome"] = self.__chrootUserHome
        parameters["user"] = self.__chrootUser
        parameters["userGroup"] = self.__chrootgroup
        parameters["userUID"] = self.__chrootUsersUID
        parameters["userGID"] = self.__chrootUsersGID
        parameters["ObsLightUserGroup"] = self.ObsLightUserGroup
        parameters["ObsLightUserGroupGID"] = self.ObsLightUserGroupGID
        parameters["chrootPath"] = self.getDirectory()
        return parameters

    def setUser(self, user):
        self.__chrootUser = user
        if self.__chrootUser == "root":
            self.__chrootUsersHome = "/"
        else:
            self.__chrootUsersHome = "/home"
        self.__chrootgroup = user

        self.__chrootUsersUID = "399"
        self.__chrootUsersGID = "399"

        self.__chrootUserHome = os.path.join(self.__chrootUsersHome, self.__chrootUser)

    def getChrootUserHome(self, fullPath=False):
        if fullPath:
            return self.getDirectory() + self.__chrootUserHome
        else:
            return self.__chrootUserHome

    def getDirectory(self):
        ''' 
        Return the path of aChRoot of a project 
        '''
        return self.__chrootDirectory

    def __initChRootAddDir(self):
        if not os.path.isdir(self.__chrootTransferDir):
            os.makedirs(self.__chrootTransferDir)
        if not os.path.isdir(self.__chrootOscCacheDir):
            os.makedirs(self.__chrootOscCacheDir)

    @property
    def obsLightMic(self):
        if self.__obsLightMic is None:
            self.__obsLightMic = ObsLightMic.getObsLightMic(self.getDirectory())
        return self.__obsLightMic

    @property
    def projectDirectory(self):
        return self.__projectDirectory

    def getChrootDirTransfert(self):
        return self.__chrootTransferDir

    def removeChRoot(self):
        if self.obsLightMic.isInit():
            ObsLightMic.destroy(name=self.getDirectory())
            self.__obsLightMic = None
        self.failIfUserNotInUserGroup()

        if os.path.isdir(self.getDirectory()):
            return self._subprocess(command="sudo rm -rf  " + self.getDirectory())

        return 0

    def execCommand(self, command=None, user=None, **kwargs):
        '''
        Execute a list of commands in the chroot.
        '''
        if command is None:
            return
        if isinstance(command, basestring):
            command = [command]
        parameter = self.makeChrootScriptParameters()
        if user is not None:
            parameter["user"] = user

        if user == "root":
            parameter["userHome"] = "/root"

        self.failIfUserNotInUserGroup()

        if not self.obsLightMic.isInit():
            self.__initChroot()

        self.testOwnerChRoot()
        # Need more than second %S
        timeString = time.strftime("%Y-%m-%d_%Hh%Mm") + str(time.time() % 1).split(".")[1]

        scriptName = "runMe_" + timeString + ".sh"
        scriptPath = self.__chrootTransferDir + "/" + scriptName

        with open(scriptPath, 'w') as f:
            f.write("#!/bin/sh -x\n")
            f.write("# Created by obslight\n\n")

            # Warning
            f.write("if [ -e %(userHome)s/.bashrc ] ; then . %(userHome)s/.bashrc ; fi\n" % parameter)
            # When OBS Light is used in graphic mode (without console), the commands like "tput"
            # need a value for TERM other than "unknown" (xterm, linux,...)
            f.write('if [ "$TERM" = "unknown" ] ; then TERM="xterm" ; fi\n')
            # Remove '.' from PATH. This is needed for openSUSE packages
            # to build in OBS Light.
            f.write(r'PATH=$(echo $PATH | sed -e s,:\\.,, -e s,^\\.:,,)' + "\n")

            for c in command:
                f.write(c + "\n")
            f.write('\n')

            # flush() does not necessarily write the file's data to disk. 
            # Use os.fsync(f.fileno()) to ensure this behavior.
            f.flush()
            os.fsync(f.fileno())

        # Sometimes the subprocess we run does not find the script.
        # We randomly get this error even with the call to os.fsync().
        errMsg = "The script '%s' does not exist although we just created it!" % scriptPath
        if not os.path.exists(scriptPath):
            raise RuntimeError(errMsg)
        os.chmod(scriptPath, 0755)
        if not os.path.exists(scriptPath):
            raise RuntimeError(errMsg)

        self.logger.info("Running script %s" % scriptName)

        parameter["scriptPath"] = self.__transferDir + "/" + scriptName

        if user == "root":
            aCommand = "sudo -H chroot %(chrootPath)s %(scriptPath)s"
        else:
            aCommand = "sudo -H chroot %(chrootPath)s su -c \"%(scriptPath)s\" - %(user)s"

        aCommand = aCommand % parameter

        if self.hostArch == 'x86_64':
            aCommand = "linux32 " + aCommand

        return self._subprocess(command=aCommand, **kwargs)

    def execScript(self, aPath):
        '''
        Execute a list of commands in the chroot.
        '''
        self.failIfUserNotInUserGroup()

        if not self.__obsLightMic.isInit():
            self.__initChroot()

        if os.path.isfile(aPath):
            scriptName = os.path.basename(aPath)
        else:
            message = "The file '" + aPath + "' do not exit, can't exec script."
            raise ObsLightErr.ObsLightChRootError(message)

        scriptPath = self.__chrootTransferDir + "/" + scriptName
        shutil.copy2(aPath, scriptPath)

        self.testOwnerChRoot()

        os.chmod(scriptPath, 0755)
        parameter = self.makeChrootScriptParameters()
        parameter["scriptPath"] = self.__transferDir + "/" + scriptName
        aCommand = "sudo -H chroot %(chrootPath)s su -c \"%(scriptPath)s\" - %(user)s"
        aCommand = aCommand % parameter

        if self.hostArch == 'x86_64':
            aCommand = "linux32 " + aCommand

        return self._subprocess(command=aCommand)

    def __initChroot(self):
        mountDir = {}
        mountDir[self.__transferDir] = self.__chrootTransferDir
        mountDir[self.__oscCacheDir] = self.__chrootOscCacheDir
        self.fixFsRights(recursive=False)
        self.obsLightMic.initChroot(chrootDirectory=self.getDirectory(), mountDir=mountDir)
        self.failIfCannotRunChrootEcho()

    def isInit(self):
        res = os.path.isdir(self.getDirectory())

        if res and os.path.isfile(os.path.join(self.getDirectory(), ".chroot.lock")):
            if not ObsLightMic.isInit(name=self.getDirectory()):
                self.__initChroot()

        return res

    def goToChRoot(self, path=None, detach=False, project=None, useRootId=False):
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
        # flush() does not necessarily write the file's data to disk.
        # Use os.fsync(f.fileno()) to ensure this behavior.
        f.flush()
        os.fsync(f.fileno())
        f.close()

        os.chmod(pathScript, 0755)

        parameter = self.makeChrootScriptParameters()
        if useRootId:
            parameter["user"] = "root"
        parameter["scriptPath"] = self.__transferDir + "/runMe.sh"
        command = "sudo -H chroot %(chrootPath)s su -c \"%(scriptPath)s\" - %(user)s"
        command = command % parameter

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

    def _subprocess(self, command=None, **kwargs):
        return self.__mySubprocessCrt.execSubprocess(command, **kwargs)

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

    def failIfCannotRunChrootEcho(self):
        """
        Try to run 'echo' in chroot jail. If chroot jail architecture
        is different from host architecture, and binfmt_misc is not
        correctly configured, this may fail, and raise ObsLightChRootError.
        """
        # FIXME: /bin/echo may be i386 but other binaries are ARM.
        scriptPath = self.__transferDir + "/test_binfmt.sh"
        with open(self.getDirectory() + scriptPath, "w") as f:
            script = """#!/bin/bash
/bin/echo OK
exit $?
"""
            f.write(script)
            f.flush()
        os.chmod(self.getDirectory() + scriptPath, 0755)
        parameter = self.makeChrootScriptParameters()
        parameter["scriptPath"] = scriptPath
        cmd = "sudo -H chroot %(chrootPath)s su -c \"%(scriptPath)s\" - %(user)s"
        cmd = cmd % parameter
        res = self._subprocess(cmd)
        if res != 0:
            msg = "Could not execute '/bin/echo' in chroot jail, your "
            msg += "binfmt_misc configuration is probably broken. "
            msg += "If it's available, try to run "
            msg += "'qemu-binfmt-conf.sh' as root."
            raise ObsLightErr.ObsLightChRootError(msg)

    def testOwnerChRoot(self):
        if os.stat(self.getDirectory()).st_uid != 0:
            msg = "The path '%s' is not owned by root." % self.getDirectory()
            raise ObsLightErr.ObsLightChRootError(msg)

    def _createAbsPath(self, chRootPath=""):
        if len(chRootPath) > 0 and chRootPath.startswith("/"):
            chRootPath = chRootPath[1:]
        return os.path.join(self.getDirectory() , chRootPath)

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
            retCode = self._subprocess("chacl -l %s" % path)
            return retCode == 0

        if not areAclsReady(self.projectDirectory):
            mountPoint = getmount(self.projectDirectory)
            message = "ACLs are not enabled on mount point '%s'. "
            message += "Use the following command as root to enable them:\n\n"
            message += "  mount -o remount,acl %s"
            raise ObsLightErr.ObsLightChRootError(message % (mountPoint, mountPoint))

    def failIfQemuIsNotStatic(self):
        """
        Raise an exception if host does not have a static version of qemu.
        Do nothing if we do not need qemu.
        """
        if self.chrootArch.lower().startswith("arm"):
            self.logger.info("Project has ARM architecture, checking qemu...")
            # TODO: check if the qemu is statically linked
            return

#    def getDic(self):
#        saveconfigPackages = {}
#        saveconfigPackages["dicoRepos"] = self.__dicoRepos
#        return saveconfigPackages

    def allowAccessToObslightGroup(self,
                                   path,
                                   recursive=False,
                                   writeAccess=True,
                                   absolutePath=True):
        """
        Modify ACLs on `path` so users of "obslight" group have read/write/execute rights.
        `recursive` changes ACLs recursively, `writeAccess` enables/disables write right,
        `absolutePath` prevents from prefixing `path` with chroot jail path.
        """
        if not absolutePath:
            path = self.getDirectory() + path
        rec = "-R" if recursive else ""
        rights = "rwX" if writeAccess else "rX"
        msg = "Giving group '%s' access rights (%s) to %s" % (self.ObsLightUserGroup,
                                                              rights,
                                                              path)
        self.logger.info(msg)
        return self._subprocess("sudo setfacl %s -m g:%s:%s %s" % (rec,
                                                                    self.ObsLightUserGroup,
                                                                    rights,
                                                                    path))

    def allowPackageAccessToObslightGroup(self, package):
        """
        Modify ACLs on package files so users of obslight group have read/write/execute rights.
        """
        path = self._createAbsPath(package.getChrootRpmBuildDirectory() + "/BUILD")
        cmd = "sudo setfacl -R -m g:%(group)s:%(rights)s -d -m g:%(group)s:%(rights)s %(path)s"
        cmd = cmd % {"group": self.ObsLightUserGroup, "rights": "rwX", "path": path}
        msg = "Giving group '%s' access rights (%s) to %s" % (self.ObsLightUserGroup,
                                                              "rwX",
                                                              path)
        self.logger.info(msg)
        return self._subprocess(cmd)

    def forbidPackageAccessToObslightGroup(self, package):
        """
        Undo `allowPackageAccessToObslightGroup`, with the exception of the "BUILD" directory
        itself, which has to be write-able by obslight.
        """
        path = self._createAbsPath("/%s/BUILD")
        path1 = path % package.getChrootRpmBuildDirectory()
        path2 = path % package.getChrootRpmBuildTmpDirectory()
        msg = "Removing group '%s' access rights to %s"
        self.logger.info(msg % (self.ObsLightUserGroup, path1))
        cmd = "sudo setfacl -R -x g:%(group)s -d -x g:%(group)s %(path)s"
        retval1 = self._subprocess(cmd % {"group": self.ObsLightUserGroup, "path": path1})
        self.logger.info(msg % (self.ObsLightUserGroup, path1))
        retval2 = self._subprocess(cmd % {"group": self.ObsLightUserGroup, "path": path2})
        self.allowAccessToObslightGroup(path1, False, True, True)

        return retval1, retval2

    def fixFsRights(self, recursive=True):
        fsPath = self.getDirectory()
        self.allowAccessToObslightGroup(fsPath, recursive=recursive, writeAccess=True)


    def createChRoot(self, rpmList, buildConfig, arch, specFile, projectName):

        self.chrootArch = arch
        print
        print "___ failIfUserNotInUserGroup"
        print
        self.failIfUserNotInUserGroup()
        print
        print "___ failIfAclsNotReady"
        print
        self.failIfAclsNotReady()
        print
        print "___ failIfQemuIsNotStatic"
        print
        self.failIfQemuIsNotStatic()
        print
        print "___ getDirectory"
        print
        fsPath = self.getDirectory()
        print
        print "___ sudo /usr/bin/build"
        print
        cmd = "sudo /usr/bin/build"
        cmd += " --root %s --rpmlist=%s --dist %s --target %s --norootforbuild --changelog %s"
        cmd = cmd % (fsPath, rpmList, buildConfig, arch, specFile)
        res = self._subprocess(cmd, waitMess=True)

#        res = ObsLightOsc.getObsLightOsc().createChRoot(chrootDir=fsPath,
#                                                        repos=repos,
#                                                        arch=arch,
#                                                        apiurl=apiurl,
#                                                        project=obsProject,
#                                                        )

#        # FIXME: since 0.5.1 there is a big regression: Tizen chroot jail creation fails.
#        # The problem comes from Tizen's "rpm" package which does not own /usr/lib/rpm/tizen,
#        # which gives this directory rwx------ file rights on certain conditions.
#        # The following code is to workaround that.
#        rpmTizenDir = os.path.join(chrootDir, "usr/lib/rpm/tizen")
#        if retCode != 0 and os.path.isdir(rpmTizenDir):
#            mode = os.stat(rpmTizenDir).st_mode
#            if (stat.S_IMODE(mode) & (stat.S_IROTH | stat.S_IXOTH)) == 0:
#                self.logger.warning("Using workaround for bug #25565")
#                command2 = "sudo chmod 755 %s" % rpmTizenDir
#                self.__subprocess(command2, waitMess=True)
#                retCode = self._subprocess(command % {"clean": ""}, waitMess=True)
#
#        return retCode


        if res != 0:
            message = "Can't create the project file system."
            message += "See the log for details about the error."
            raise ObsLightErr.ObsLightChRootError(message)

        self.fixFsRights()

        retVal = self.prepareChroot(self.getDirectory(), projectName)
        if retVal != 0:
            return retVal
        retVal = self.prepareChroot(self.getDirectory(), projectName, user="root")
        if retVal != 0:
            return retVal
        retVal = self.setTimezoneInBashrc("root")
        if retVal != 0:
            return retVal
        return self.setTimezoneInBashrc()

    def setTimezoneInBashrc(self, user=None):
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
        parameter = self.makeChrootScriptParameters()

        if user == "root":
            parameter["user"] = "root"
            parameter["userHome"] = "/root"


        msg = "Setting chroot jail's time zone to '%s'" % (tzname)
        ObsLightPrintManager.getLogger().info(msg)
        command.append('echo "TZ=\\"%s\\"" >> %s/.bashrc' % (tzname, parameter["userHome"]))
        command.append('echo "export TZ" >> %s/.bashrc' % parameter["userHome"])
        return self.execCommand(command, user=parameter["user"])

    def prepareChroot(self, chrootDir, project, user=None):
        '''
        Prepare the chroot :
        - replaces some binaries by their ARM equivalent (in case chroot is ARM)
        - configures zypper and rpm for ARM
        - rebuilds rpm database
        - customize .bashrc
        - adds group "user" if it does not exist
        '''
        command = []

        parameter = self.makeChrootScriptParameters()

        if user == "root":
            parameter["user"] = "root"
            parameter["userHome"] = "/root"
            # Not all distro have "%(ObsLightUserGroup)s" group, obslight needs it for acl and directory management.
            cmd = "if ! egrep '^root:' >/dev/null </etc/group ; then echo 'root:x:0:' >>/etc/group ;fi"
            command.append(cmd % parameter)


            # We need "%(user)s" user too.
            cmd = "if ! egrep '^root:' >/dev/null </etc/passwd ; then echo 'root:x:0:0:root:/root:/bin/bash' >>/etc/passwd; fi"
            command.append(cmd % parameter)
            cmd = "if ! egrep '^root:' >/dev/null </etc/shadow ; then echo 'root:*:15380:0:99999:7:::' >>/etc/shadow ; fi"
            command.append(cmd % parameter)
            cmd = "if ! egrep '^root:' >/dev/null </etc/gshadow ; then echo 'root:*::root' >>/etc/gshadow ; fi"
            command.append(cmd % parameter)

            command.append("rpm --initdb")
            command.append("rpm --rebuilddb")

        else:
            # Not all distro have "%(ObsLightUserGroup)s" group, obslight needs it for acl and directory management.
            cmd = "if ! egrep '^%(ObsLightUserGroup)s:' >/dev/null </etc/group ; then echo '%(ObsLightUserGroup)s:x:%(ObsLightUserGroupGID)s:' >>/etc/group ;fi"
            command.append(cmd % parameter)

            # We need "%(user)s" user too.
            cmd = "if ! egrep '^%(user)s:' >/dev/null </etc/passwd ; then echo '%(user)s:x:%(userUID)s:%(userGID)s:%(user)s:%(userHome)s:/bin/sh' >>/etc/passwd; fi"
            command.append(cmd % parameter)
            cmd = "if ! egrep '^%(user)s:' >/dev/null </etc/shadow ; then echo '%(user)s:*:::::::' >>/etc/shadow ; fi"
            command.append(cmd % parameter)
            cmd = "if ! egrep '^%(user)s:' >/dev/null </etc/gshadow ; then echo '%(user)s:*::' >>/etc/gshadow ; fi"
            command.append(cmd % parameter)

        userHome = parameter["userHome"]

        for c in self._getProxyconfig():
            command.append('echo "' + c + '" >> %s/.bashrc' % userHome)

        command.append('echo "alias ll=\\"ls -lh --color\\"" >> %s/.bashrc' % userHome)
        command.append('echo "alias la=\\"ls -Alh --color\\"" >> %s/.bashrc' % userHome)
        command.append('echo "alias vi=\\"vim\\"" >> %s/.bashrc' % userHome)

        prompt = {"blue": "\\[\\e[34;1m\\]",
                  "green": "\\[\\e[32;1m\\]",
                  "default": "\\[\\e[0m\\]",
                  "path": "\\w",
                  "delimiter": "\\\\\$ ",
                  "project": project}

        PS1 = "%(blue)s%(project)s:%(green)s%(path)s%(default)s%(delimiter)s" % prompt

        command.append('echo "PS1=\'%s\'" >> %s/.bashrc' % (PS1, userHome))
        command.append('echo "export PS1" >> %s/.bashrc' % userHome)

        command.append('chown %(user)s:%(userGroup)s %(userHome)s/.bashrc' % parameter)
        return self.execCommand(command=command, user="root")

    def _getProxyconfig(self):
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

    def checkReadAccessForOther(self, path):
        result = []
        for walker in os.walk(path):
            root = walker[0]
            files = walker[2]
            for f in files:
                aPath = os.path.join(root, f)
                # os.lstat does not follow symlinks,
                # so does not fail on broken symlinks.
                mode = os.lstat(aPath).st_mode
                if (mode & stat.S_IROTH) == 0:
                    result.append(aPath)
        return result

class ObsLightChRoot(ObsLightChRootCore):
    def __init__(self, projectDirectory):
        ObsLightChRootCore.__init__(self, projectDirectory)

    def makeRpmbuildScriptParameters(self, specFile, package, target="", args=""):
        parameters = self.makeChrootScriptParameters()

        parameters["packageName"] = package.getName()
        parameters["buildDir"] = "%s/%s/%s" % (parameters["userHome"],
                                               parameters["packageName"],
                                               package.getTopDirRpmBuildDirectory())

        parameters["buildLink"] = "%s/%s/%s" % (parameters["userHome"],
                                                parameters["packageName"],
                                                package.getTopDirRpmBuildLinkDirectory())

        srcdefattr = "--define '_srcdefattr (-,root,root)'"
        topdir = "--define '_topdir %%{getenv:HOME}/%s'" % package.getTopDirRpmBuildLinkDirectory()
        if isNonEmptyString(target):
            args = args + " --target=%s" % target
        rpmbuildCmd = "rpmbuild %s %s %s %s < /dev/null" % (args, srcdefattr, topdir, specFile)
        parameters["rpmbuildCmd"] = rpmbuildCmd
        parameters["directoryBuild"] = package.getChrootBuildDirectory()

        return parameters

    def __findPackageDirectory(self, package=None):
        '''
        Return the directory of where the package was installed.
        '''
        pathBuild = self._createAbsPath(package.getChrootRpmBuildDirectory() + "/BUILD")
        if not os.path.isdir(pathBuild):
            raise ObsLightErr.ObsLightChRootError("The path '" + pathBuild + "' is not a directory")

        listDir = [item for item in os.listdir(pathBuild) if (os.path.isdir(pathBuild + "/" + item) and
                                                              (not item.startswith(".git")))]

        if len(listDir) == 0:
            package.setPackageParameter("patchMode", False)
            package.setChRootStatus(PK_CONST.NO_BUILD_DIRECTORY)
            return None
#            raise ObsLightErr.ObsLightChRootError("No sub-directory in '" + pathBuild + "'." +
#                                                  " There should be exactly one.")
        elif len(listDir) == 1:
            prepDirname = listDir[0]
            resultPath = package.getChrootRpmBuildDirectory() + "/BUILD/" + prepDirname
            package.setPrepDirName(prepDirname)
            dirContent = os.listdir(pathBuild + "/" + prepDirname)
            if len(dirContent) == 0:
                # If there is nothing in package directory, we cannot
                # initialize patch mode.
                package.setPackageParameter("patchMode", False)
                return resultPath
            elif (len(dirContent) == 1) and os.path.isdir("%s/%s/%s" % (pathBuild,
                                                                        prepDirname,
                                                                        dirContent[0])):
                return resultPath + "/" + dirContent[0]
            else:
                return resultPath
        else:
            package.setPackageParameter("patchMode", False)
            package.setChRootStatus(PK_CONST.MANY_BUILD_DIRECTORIES)
            return None
#            raise ObsLightErr.ObsLightChRootError("Too many sub-directories in '%s'" % pathBuild)

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

        self.allowAccessToObslightGroup(os.path.dirname(absSpecFile_tmp),
                                        recursive=True,
                                        writeAccess=True,
                                        absolutePath=True)

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
        self._subprocess(command)

        return aSpecFile

    def addPackageSourceInChRoot(self, package):

        if package.isExclude():
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

            parameter = self.makeChrootScriptParameters()
            parameter["RpmBuildDir"] = chrootRpmBuildDirectory
            parameter["package"] = packageName

            command.append("chown  %(user)s:%(userGroup)s %(RpmBuildDir)s" % parameter)
            command.append("chown  %(user)s:%(userGroup)s %(userHome)s/%(package)s" % parameter)

            for c in self._getProxyconfig():
                command.append(c)

            res = self.execCommand(command=command, user="root")

            specDirPath = self._createAbsPath(chrootRpmBuildDirectory + "/SPECS/")
            self.allowAccessToObslightGroup(specDirPath)
            if os.path.isdir(specDirPath):
                absChrootHome = self._createAbsPath("%(userHome)s" % parameter)
                macroDirectory = absChrootHome
                macroDest = os.path.join(absChrootHome, package.getName())

                self.allowAccessToObslightGroup(macroDest)
                if not os.path.isfile(os.path.join(macroDest, ".rpmmacros")):
                    shutil.copy2(os.path.join(macroDirectory, ".rpmmacros"), macroDest)
                if not os.path.isfile(os.path.join(macroDest, ".rpmrc")):
                    shutil.copy2(os.path.join(macroDirectory, ".rpmrc"), macroDest)

                absChrootRpmBuildDirectory = self._createAbsPath("/%s/SOURCES/")
                absChrootRpmBuildDirectory = absChrootRpmBuildDirectory % chrootRpmBuildDirectory
                self.allowAccessToObslightGroup(absChrootRpmBuildDirectory)

                #copy source
                package.exportIntoChroot(self.getDirectory())

            else:
                message = packageName + " source is not installed in " + self.getDirectory()
                raise ObsLightErr.ObsLightChRootError(message)
            return res

    def removePackage(self, package):
        if self.isInit():
            parameter = self.makeChrootScriptParameters()

            parameter["package"] = package

            self.execCommand(["rm -rf %(userHome)s/%(package)s" % parameter], user="root")

        return 0

    # TODO: replace 'arch' by 'target'
    def prepRpm(self, specFile, package, arch):
        '''
        Execute the %prep section of an RPM spec file.
        '''
        scriptParameters = self.makeRpmbuildScriptParameters(specFile, package, arch, "-bp")
        # We need to rename all the .gitignore files to not disturb the git management
        prepScript = "chown -R %(user)s:%(userGroup)s %(buildDir)s"
        prepScript = prepScript % scriptParameters
        _ = self.execCommand([prepScript], user="root")

        script = """HOME=%(userHome)s/%(packageName)s
rm -f %(buildLink)s
ln -s %(buildDir)s %(buildLink)s
%(rpmbuildCmd)s
RETURN_VALUE=$?
find %(buildDir)s/BUILD -type f -name .gitignore -execdir mv {} .gitignore.obslight \;
exit $RETURN_VALUE
"""
        script = script % scriptParameters
        res = self.execCommand([script])

        if res != 0:
            msg = "The first %%prep of package '%s' failed. " % package.getName()
            msg += "Return code was: %s" % str(res)
            raise ObsLightErr.ObsLightChRootError(msg)

        packageDirectory = self.__findPackageDirectory(package=package)
        if packageDirectory is None:
            return 0

        message = "Package directory used by '%s': %s" % (package.getName(), str(packageDirectory))
        ObsLightPrintManager.getLogger().debug(message)
        package.setChrootBuildDirectory(packageDirectory)

        if package.getPackageParameter("patchMode"):
            package.initCurrentPatch()

            if packageDirectory is not None:
                # TODO: check if we can remove this
                # We shouldn't need to write to package directory anymore
                absPackageDirectory = self._createAbsPath(packageDirectory)
                cmd = "sudo chmod og+rwX %s" % absPackageDirectory
                self._subprocess(command=cmd)

                # If one or more files into the package BUILD directory do not have the
                # read access for group, the command "git add *" will fail.
                fileList = self.checkReadAccessForOther(absPackageDirectory)

                if len(fileList) > 0:
                    package.setPackageParameter("patchMode", False)
                    package.setChRootStatus(PK_CONST.PREPARED)
                    msg = "Warning: the following files do not have read access for 'other',"
                    msg += "the 'patchMode' will be ineffective:\n\n"
                    for f in fileList:
                        msg += "\t\t" + f + "\n"
                    msg += "\n"

                    raise ObsLightErr.ObsLightChRootError(msg)

                self._ObsLightGitManager.initGitWatch(packageDirectory, package)
                package.setFirstCommit(tag=self._ObsLightGitManager.initialTag)
                if package.specFileHaveAnEmptyBuild():
                    package.setChRootStatus(PK_CONST.NO_BUILD_SECTION)
                    return 0

                return self.__buildRpm(specFile, package, arch)

        elif package.haveBuildDirectory():
            package.setChRootStatus(PK_CONST.PREPARED)

        return 0

    def __buildRpm(self, specFile, package, arch):
        '''
        Execute the %build section of an RPM spec file.
        '''
        scriptParameters = self.makeRpmbuildScriptParameters(specFile,
                                                             package,
                                                             arch,
                                                             "-bc --short-circuit")

        script = """HOME=%(userHome)s/%(packageName)s
rm -f %(buildLink)s
ln -s %(buildDir)s %(buildLink)s
mv  %(directoryBuild)s/.gitignore  %(directoryBuild)s/.gitignore.tmp.build 
find %(directoryBuild)s -type f -name .gitignore.obslight -execdir mv {} .gitignore \;
%(rpmbuildCmd)s
RETURN_VALUE=$?
find %(directoryBuild)s -type f -name .gitignore -execdir mv {} .gitignore.obslight \;
mv %(directoryBuild)s/.gitignore.tmp.build %(directoryBuild)s/.gitignore
exit $RETURN_VALUE
"""
        script = script % scriptParameters

        res = self.execCommand([script])

        packageName = package.getName()
        packageDirectory = package.getChrootBuildDirectory()

        if res == 0:
            self._ObsLightGitManager.ignoreGitWatch(package=package, path=packageDirectory)

            self.allowPackageAccessToObslightGroup(package)
            res = self._ObsLightGitManager.resetToPrep(package=package, path=packageDirectory)

            if res == 0:
                scriptParameters["packageDirectory"] = packageDirectory
                cmd = "chown -R %(user)s:%(userGroup)s %(packageDirectory)s" % scriptParameters
                res = self.execCommand([cmd], user="root")
                package.setChRootStatus(PK_CONST.PREPARED)
            else:
                msg = "Fail to checkout package %s, after the first build." % packageName
                msg += " Return code was: %s" % str(res)
                raise ObsLightErr.ObsLightChRootError(msg)
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
        if package.isExclude():
            msg = u"Package '%s' has a excluded status, it can't be built" % package.getName()
            raise ObsLightErr.ObsLightChRootError(msg)
        if package.specFileHaveAnEmptyBuild():
            package.setPackageParameter("patchMode", False)
            package.setChRootStatus(PK_CONST.NO_BUILD_DIRECTORY)
            return 0
        if package.getPackageParameter("patchMode"):

            self._ObsLightGitManager.commitGit(mess="build", package=package)

            res = self.__createGhostRpmbuildCommand("bc", package, specFile, arch)

            self._ObsLightGitManager.ignoreGitWatch(package=package,
                                                     path=package.getChrootBuildDirectory(),
                                                     commitComment="build commit")
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
            package.setChRootStatus(PK_CONST.BUILD)
        return res

    # TODO: replace 'arch' by 'target'
    def installRpm(self, package, specFile, arch):
        '''
        Execute the %install section of an RPM spec file.
        '''

        if package.isExclude():
            msg = u"Package '%s' has a excluded status, it can't be install" % package.getName()
            raise ObsLightErr.ObsLightChRootError(msg)

        if package.getPackageParameter("patchMode"):
            self._ObsLightGitManager.commitGit(mess="install", package=package)

            res = self.__createGhostRpmbuildCommand("bi", package, specFile, arch)

            self._ObsLightGitManager.ignoreGitWatch(package=package,
                                                    path=package.getChrootBuildDirectory(),
                                                    commitComment="build install commit")
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

            package.setChRootStatus(PK_CONST.BUILD_INSTALLED)
        return res

    # TODO: replace 'arch' by 'target'
    def packageRpm(self, package, specFile, arch):
        '''
        Execute the package section of an RPM spec file.
        '''

        if package.isExclude():
            msg = u"Package '%s' has a excluded status, it can't be package" % package.getName()
            raise ObsLightErr.ObsLightChRootError(msg)

        if package.getPackageParameter("patchMode"):
            self._ObsLightGitManager.commitGit(mess="packageRpm", package=package)

            res = self.__createGhostRpmbuildCommand("ba", package, specFile, arch)

            self._ObsLightGitManager.ignoreGitWatch(package=package,
                                                    path=package.getChrootBuildDirectory(),
                                                    commitComment="build package commit")
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

            package.setChRootStatus(PK_CONST.BUILD_PACKAGED)
        return res

    def prepGhostRpmbuild(self, package):
        packagePath = package.getChrootBuildDirectory()
        tarFile = package.getArchiveName()

        parameter = self.makeChrootScriptParameters()
        parameter["packageName"] = package.getName()
        parameter["topDirRpmBuildTmp"] = package.getTopDirRpmBuildTmpDirectory()

        buildDirTmp = "%(userHome)s/%(packageName)s/%(topDirRpmBuildTmp)s" % parameter
        buildDir = package.getTopDirRpmBuildDirectory()
        buildDirPath = "%(userHome)s/" + package.getName() + "/" + buildDir + "/BUILD"
        buildDirPath = buildDirPath % parameter
#        buildLink = "/root/" + package.getName() + "/" + package.getTopDirRpmBuildLinkDirectory()

        command = []
        command.append("rm -rf %s/*" % buildDirTmp)
        command.append("mkdir -p %s/BUILD" % buildDirTmp)
        command.append("mkdir -p %s/SPECS" % buildDirTmp)
        command.append("mkdir -p %s/TMP" % buildDirTmp)

        command.append("ln -sf ../%s/BUILDROOT %s" % (buildDir, buildDirTmp))
        command.append("ln -sf ../%s/RPMS %s" % (buildDir, buildDirTmp))
        command.append("ln -sf ../%s/SOURCES %s" % (buildDir, buildDirTmp))
        command.append("ln -sf ../%s/SRPMS %s" % (buildDir, buildDirTmp))

        outputFilePath = os.path.join(buildDirTmp, "SOURCES", tarFile)

        tmpPath = packagePath.replace(buildDirPath , "").strip("/")
        tmpPath = tmpPath.strip("/")
        _ = self.execCommand(command=command)

        gitDir = package.getCurrentGitDirectory()
        res = self._ObsLightGitManager.execMakeArchiveGitSubcommand(packagePath,
                                                                     outputFilePath,
                                                                     tmpPath,
                                                                     gitDir)

        return res

    def __createRpmbuildCommand(self, command, package, pathToSpec, arch):
        scriptParameters = self.makeRpmbuildScriptParameters(pathToSpec,
                                                             package,
                                                             target=arch,
                                                             args="-%s" % command)
        prepScript = """chown -R %(user)s:%(userGroup)s %(buildDir)s/SOURCES/
chown -R %(user)s:%(userGroup)s %(buildDir)s/SPECS/
        """
        prepScript = prepScript % scriptParameters
        self.execCommand([prepScript], user="root")

        script = """HOME=%(userHome)s/%(packageName)s
rm -f %(buildLink)s
ln -s %(buildDir)s %(buildLink)s
rm -rf %(buildLink)s/BUILD/
%(rpmbuildCmd)s
exit $?
"""
        script = script % scriptParameters
        return self.execCommand([script])

    def __createGhostRpmbuildCommand(self, command, package, pathToSpec, arch):
        scriptParameters = self.makeRpmbuildScriptParameters(pathToSpec,
                                                             package,
                                                             target=arch,
                                                             args="-%s" % command)

        scriptParameters["buildDirTmp"] = package.getTopDirRpmBuildTmpDirectory()
        scriptParameters["buildDirTmpPath"] = "%s/%s/%s" % (scriptParameters["userHome"],
                                                            package.getName(),
                                                            scriptParameters["buildDirTmp"])

        prepScript = """chown -R %(user)s:%(userGroup)s %(buildDirTmpPath)s/SOURCES/
chown -R %(user)s:%(userGroup)s %(buildDirTmpPath)s/SPECS/
        """
        prepScript = prepScript % scriptParameters
        self.execCommand([prepScript], user="root")

        script = """HOME=%(userHome)s/%(packageName)s
rm -rf %(buildDir)s/RPMS/*
rm -f %(buildLink)s
ln -s %(buildDirTmpPath)s %(buildLink)s
%(rpmbuildCmd)s
RPMBUILD_RETURN_CODE=$?
[ $RPMBUILD_RETURN_CODE -eq 0 ] && rm -rf %(buildDirTmpPath)s/BUILD/
rm -rf %(buildDirTmpPath)s/TMP
rm -f %(buildLink)s
ln -s %(buildDir)s %(buildLink)s
exit $RPMBUILD_RETURN_CODE
"""

        script = script % scriptParameters
        return self.execCommand([script])

    def createPatch(self, package=None, patch=None):
        '''
        Create a patch from modifications made in the package directory.
        '''
        if not patch.endswith(".patch"):
            patch += ".patch"
        packagePath = package.getChrootBuildDirectory()

        self._ObsLightGitManager.commitGit(mess="createPatch", package=package)

        tag1 = package.getFirstCommit()
        if tag1 is None:
            raise ObsLightErr.ObsLightChRootError("package: '" + package.getName() +
                                                  "' has no git first tag.")
        tag2 = package.getSecondCommit()
        self._ObsLightGitManager.createPatch(package, packagePath, tag1, tag2, patch)

        package.addPatch(aFile=patch)

        package.save()
        return 0

    def updatePatch(self, package=None):
        '''
        Update a patch from modifications made in the package directory.
        '''
        patch = package.getCurrentPatch()
        packagePath = package.getChrootBuildDirectory()

        self._ObsLightGitManager.commitGit(mess="updatePatch", package=package)

        tag1 = package.getFirstCommit()
        if tag1 is None:
            raise ObsLightErr.ObsLightChRootError("package: '" + package.getName() +
                                                  "' has no git first tag.")
        tag2 = package.getSecondCommit()

        self._ObsLightGitManager.createPatch(package, packagePath, tag1, tag2, patch)

        package.save()
        return 0



#    def installBuildRequires(self, buildInfoCli, target, configPath):
    def installBuildRequires(self, rpmListFilePath, target, configPath):
        instPkgSet = set(self.getInstalledPackagesList())
#        wantedPkgList = self.__reOrderRpm(buildInfoCli, target, configPath)

        print
        print "instPkgSet", instPkgSet
        print

        if os.path.isfile(rpmListFilePath):
            absPathDict = ObsLightTools.getRpmPathDict(rpmListFilePath)
        else:
            msg = "Can't install RPM into chroot jail, the file '%s' do not exist. "
            msg = msg % rpmListFilePath
            raise ObsLightErr.ObsLightChRootError(msg)

        command = []
        instCount = 0
        eraseCount = 0

        wantedPkgSet = set(absPathDict.keys())
        print "wantedPkgSet", wantedPkgSet
        print
        # Erase unwanted packages
        unWantedPkgSet = instPkgSet.difference(wantedPkgSet)
        print "unWantedPkgSet", unWantedPkgSet
        print
        for p in wantedPkgSet:print "         ", absPathDict[p]
        for p in unWantedPkgSet:
            cmd = "rpm --nodeps -e '%s'" % p
            command.append(cmd)
            eraseCount += 1
        # Install missing packages
        missingPkgSet = wantedPkgSet.difference(instPkgSet)
        for p in missingPkgSet:
            cmd = "rpm --nodeps --ignorearch -i '%s'" % absPathDict[p]
            command.append(cmd)
            instCount += 1

        msg = "%d packages to %s"
        self.logger.info(msg % (instCount, "install"))
        self.logger.info(msg % (eraseCount, "erase"))
        return self.execCommand(command=command, user="root")

    def getInstalledPackagesList(self):
        """Returns the list packages installed in chroot jail (using RPM DB)."""
        cmd = "rpm -qa"
        res = self.execCommand(cmd, user="root", stdout=True, noOutPut=True)
        lines = [l for l in res.split("\n") if l != ""]
        return lines
        # Separate package name and version
#        myRe = re.compile(r"(.*)-([^-]+-[^-]+)")
#        packages = []
#        for line in lines:
#            match = myRe.search(line)
#            if match is not None:
#                packages.append(match.group(1, 2))
#        return packages
