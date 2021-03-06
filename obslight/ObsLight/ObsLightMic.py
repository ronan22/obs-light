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

# TODO: rename this module
# It was named 'Mic' because it was using MIC's functions.

import os
import subprocess
import shlex
import glob
import atexit

import ObsLightPrintManager
import ObsLightErr
from ObsLightSubprocess import SubprocessCrt
from ObsLightUtils import findBinaryPath


# This is a reimplementation of MIC's my_fuser function
def my_fuser(fp):
    fuser = findBinaryPath("fuser")
    if not os.path.exists(fp):
        return False

    rc = subprocess.call([fuser, "-s", fp])
    if rc == 0:
        proc = subprocess.Popen([fuser, fp], stdout=subprocess.PIPE)
        pids = proc.communicate()[0].split()
        for pid in pids:
            with open("/proc/%s/cmdline" % pid, "r") as fd:
                cmdline = fd.read()
            if cmdline[:-1] == "/bin/bash":
                return True

    # not found
    return False

class ObsLightMic(object):

    def __init__(self):
        self.__isInit = False

        self.__chroot_lockfd = None
        self.__chroot_lock = ""

        self.__globalmounts = None
#        self.__qemu_emulator = None

        self.__chrootDirectory = None

        self.__mySubprocessCrt = SubprocessCrt()

        self.__obsLightPrint = ObsLightPrintManager.obsLightPrint

        self.__bindmounts = None

    def destroy(self):
        if self.__isInit == True:
            self.cleanup_chrootenv(bindmounts=self.__bindmounts)
        self.__isInit = False
#        dev_null = os.open("/dev/null", os.O_WRONLY)
#        proc_mounts = subprocess.Popen([ 'cat', "/proc/mounts" ], stdout=subprocess.PIPE, stderr=dev_null)
#        outputs = proc_mounts.communicate()[0].strip().split("\n")
#        for line in outputs:
#            if line.find(os.path.abspath(self.__chrootDirectory)) >= 0:
#                if os.path.abspath(self.__chrootDirectory) == line.split()[1]:
#                    continue
#                point = line.split()[1]
#                ret = subprocess.call([ "umount", "-l", point ], stdout=dev_null, stderr=dev_null)
#                if ret != 0:
#                    print "ERROR: failed to unmount %s" % point
#                    os.close(dev_null)
#                    return ret
#        os.close(dev_null)"""

    def isInit(self):
        return self.__isInit

    def initChroot(self, chrootDirectory=None, mountDir=None):
        mountDir = mountDir or {}
        self.testOwnerChRoot(path=chrootDirectory)
        self.__bindmounts = ""
        for k in mountDir.keys():
            self.__bindmounts += mountDir[k] + ":" + k + ";"
        self.__chrootDirectory = chrootDirectory
#        self.__findArch()

        self.setup_chrootenv(bindmounts=self.__bindmounts)

        self.__isInit = True

    def testOwnerChRoot(self, path):
        if os.path.isdir(path):
            if os.stat(path).st_uid != 0:
                message = "The project file system '%s' is not owned by root." % path
                raise ObsLightErr.ObsLightChRootError(message)
        else:
            message = "Can't test owner of the project file system, "
            message += "the directory '%s' does not exist." % path
            raise ObsLightErr.ObsLightChRootError(message)

    def __subprocess(self, command=None):
        return self.__mySubprocessCrt.execSubprocess(command=command)

    def setup_chrootenv(self, bindmounts=None):
        def get_bind_mounts(chrootdir, bindmounts):
            chrootmounts = []
            if bindmounts in ("", None):
                bindmounts = ""
            mounts = bindmounts.split(";")
            for mount in mounts:
                if mount == "":
                    continue
                srcdst = mount.split(":")
                srcdst[0] = os.path.abspath(os.path.expanduser(srcdst[0]))
                if len(srcdst) == 1:
                    srcdst.append("none")
                if not os.path.isdir(srcdst[0]):
                    continue
                if srcdst[0] in ("/proc",
                                 "/proc/sys/fs/binfmt_misc",
                                 "/",
                                 "/sys",
                                 "/dev",
                                 "/dev/pts",
                                 "/dev/shm",
                                 "/var/lib/dbus",
                                  "/var/run/dbus"):
                    #chroot.pwarning("%s will be mounted by default." % srcdst[0])
                    message = "%s will be mounted by default." % srcdst[0]
                    self.__obsLightPrint(message, isDebug=True)
                    continue
                if srcdst[1] == "" or srcdst[1] == "none":
                    srcdst[1] = None
                else:
                    srcdst[1] = os.path.abspath(os.path.expanduser(srcdst[1]))
                    #if os.path.isdir(chrootdir + "/" + srcdst[1]):
                    #    #chroot.pwarning("%s has existed in %s , skip it." % (srcdst[1], chrootdir))
                    #    self.__obsLightPrint("%s has existed in %s , skip it." % (srcdst[1], chrootdir) , isDebug=True)
                    #    continue
                # "dirsync" option added to try to avoid random bug which made scripts
                # written by obslight in chrootTransfer not available from chroot jail
                chrootmounts.append(BindChrootMount(srcdst[0], chrootdir, srcdst[1], "dirsync"))

            #"""Default bind mounts"""
            chrootmounts.append(BindChrootMount("/proc", chrootdir, None))
            chrootmounts.append(BindChrootMount("/proc/sys/fs/binfmt_misc",
                                                self.__chrootDirectory,
                                                None))
            chrootmounts.append(BindChrootMount("/sys", chrootdir, None))
            chrootmounts.append(BindChrootMount("/dev", chrootdir, None))
            chrootmounts.append(BindChrootMount("/dev/pts", chrootdir, None))
            chrootmounts.append(BindChrootMount("/var/lib/dbus", chrootdir, None))
            chrootmounts.append(BindChrootMount("/var/run/dbus", chrootdir, None))

            # FIXME: is this needed ? It makes %prep of kmod-virtiogl fail.
#            for kernel in os.listdir("/lib/modules"):
#                chrootmounts.append(BindChrootMount("/lib/modules/" + kernel, chrootdir, None, "ro"))

            self.__globalmounts = chrootmounts

        def bind_mount(chrootmounts):
            for b in chrootmounts:
                self.__obsLightPrint("bind_mount: %s -> %s" % (b.src, b.dest), isDebug=True)
                b.mount()
                # b.mount() should raise an exception if it fails
                # so b.ismounted() is supposed to be always True at this point
                assert b.ismounted(), "Error while mounting %s" % b.src

        def setup_resolv(chrootdir):
            command = "sudo cp /etc/resolv.conf " + chrootdir + "/etc/resolv.conf"
            self.__subprocess(command=command)

        get_bind_mounts(self.__chrootDirectory, bindmounts)
        bind_mount(self.__globalmounts)
        setup_resolv(self.__chrootDirectory)
        mtab = "/etc/mtab"
        dstmtab = self.__chrootDirectory + mtab
        if not os.path.islink(dstmtab):
            command = "sudo cp " + mtab + " " + dstmtab
            self.__subprocess(command=command)
        self.__chroot_lock = os.path.join(self.__chrootDirectory, ".chroot.lock")
        self.__chroot_lockfd = open(self.__chroot_lock, "w")
        return self.__globalmounts

    def cleanup_chrootenv(self, bindmounts=None):

        def bind_unmount(chrootmounts):
            chrootmounts.reverse()
            for b in chrootmounts:
                self.__obsLightPrint("bind_unmount: %s -> %s" % (b.src, b.dest), isDebug=True)
                b.unmount()

        #def cleanup_resolv(chrootdir):
        #    fd = open(chrootdir + "/etc/resolv.conf", "w")
        #    fd.truncate(0)
        #    fd.close()

        def kill_processes(chrootdir):
            for procfile in glob.glob("/proc/*/root"):
                try:
                    if os.readlink(procfile) == chrootdir:
                        pid = int(procfile.split("/")[2])
                        os.kill(pid, 9)
                except BaseException:
                    return None
        self.__chroot_lockfd.close()

        bind_unmount(self.__globalmounts)
        if not my_fuser(self.__chroot_lock):
            #cleanup_resolv(self.__chrootDirectory)
            self.__subprocess(command="sudo rm " + self.__chrootDirectory + "/etc/resolv.conf")
            self.__subprocess(command="sudo touch " + self.__chrootDirectory + "/etc/resolv.conf")

            if os.path.exists(self.__chrootDirectory + "/etc/mtab"):
                command = "sudo rm " + self.__chrootDirectory + "/etc/mtab"
                self.__subprocess(command=command)

            kill_processes(self.__chrootDirectory)

        self.cleanup_mountdir(self.__chrootDirectory, bindmounts)
#        if self.__qemu_emulator:
#
#            command = "sudo rm " + self.__chrootDirectory + self.__qemu_emulator
#            self.__subprocess(command=command)

        command = "sudo rm " + self.__chroot_lock
        self.__subprocess(command=command)

    def cleanup_mountdir(self, chrootdir, bindmounts):
        if bindmounts == "" or bindmounts == None:
            return
        mounts = bindmounts.split(";")
        for mount in mounts:
            if mount == "":
                continue
            srcdst = mount.split(":")
            if len(srcdst) == 1:
                srcdst.append("none")
            if srcdst[1] == "" or srcdst[1] == "none":
                srcdst[1] = srcdst[0]
            srcdst[1] = os.path.abspath(os.path.expanduser(srcdst[1]))
            tmpdir = chrootdir + "/" + srcdst[1]
            if os.path.isdir(tmpdir):
                if len(os.listdir(tmpdir)) == 0:
                    #shutil.rmtree(tmpdir, ignore_errors = True)
                    command = "sudo rm -r " + tmpdir
                    self.__subprocess(command=command)
                else:
                    self.__obsLightPrint("dir %s isn't empty." % tmpdir, isDebug=True)
                    #chroot.pwarning("dir %s isn't empty." % tmpdir)

    def chroot(self, bindmounts=None, execute="/bin/bash"):
        def mychroot():
            os.chroot(self.__chrootDirectory)
            os.chdir("/")

        try:
            self.__obsLightPrint("Launching shell. Exit to continue.", isDebug=True)
            self.__obsLightPrint("----------------------------------", isDebug=True)
            self.setup_chrootenv(bindmounts)

            args = shlex.split(execute)

            subprocess.call(args, preexec_fn=mychroot)

        except OSError, Err:
            (errCode, msg) = Err
            self.__obsLightPrint(errCode, isDebug=True)
            raise OSError(errCode, "Failed to chroot: %s" % msg)
        finally:
            self.cleanup_chrootenv(bindmounts)


class BindChrootMount:
    """Represents a bind mount of a directory into a chroot."""
    def __init__(self, src, aChroot, dest=None, option=None):
        self.src = src
        self.root = os.path.abspath(os.path.expanduser(aChroot))
        self.option = option

        if not dest:
            dest = src
        self.dest = self.root + "/" + dest

        self.mounted = False
        self.mountcmd = findBinaryPath("mount")
        self.umountcmd = findBinaryPath("umount")

        self.__mySubprocessCrt = SubprocessCrt()


    def __subprocess(self, command=None):
        return self.__mySubprocessCrt.execSubprocess(command=command)

    def ismounted(self):
        ret = False
        pathDest = os.path.abspath(self.dest)

        if not os.path.exists(pathDest):
                ret = False
                return ret

        dev_null = os.open("/dev/null", os.O_WRONLY)
        catcmd = findBinaryPath("cat")
        args = [ catcmd, "/proc/mounts" ]
        #TODO:change to use SubprocessCrt
        proc_mounts = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=dev_null)
        outputs = proc_mounts.communicate()[0].strip().split("\n")
        for line in outputs:
            pathMount = line.split()[1]

            if not os.path.exists(pathMount):
                continue

            if os.stat(pathMount).st_ino == os.stat(pathDest).st_ino:
                ret = True
                break

        os.close(dev_null)
        return ret

    def has_chroot_instance(self):
        lock = os.path.join(self.root, ".chroot.lock")
        try:
            return my_fuser(lock)
        # After reading my_fuser code, it seems that catching
        # "file not found" exception is equivalent to False.
        except IOError as e:
            msg = u"Got an exception while testing if chroot is in use: %s" % unicode(e)
            d = {'exception': e}
            ObsLightPrintManager.getLogger().error(msg, extra=d)
            return False

    def mount(self):
        if self.mounted or self.ismounted():
            return

        #imgcreate.makedirs(self.dest)
        command = "sudo mkdir -p " + self.dest
        self.__subprocess(command=command)
        command = "sudo " + self.mountcmd + " --bind " + self.src + " " + self.dest
        rc = self.__subprocess(command=command)
        if rc != 0:
            msg = "Bind-mounting '%s' to '%s' failed" % (self.src, self.dest)
            raise ObsLightErr.ObsLightChRootError(msg)
        if self.option:
            #TODO:change to use SubprocessCrt
            rc = subprocess.call(["sudo",
                                  self.mountcmd,
                                  "--bind",
                                  "-o",
                                  "remount,%s" % self.option,
                                  self.dest])
            if rc != 0:
                msg = "Bind-remounting '%s' failed with code %d" % (self.dest, rc)
                raise ObsLightErr.ObsLightChRootError(msg)
        self.mounted = True

    def unmount(self):
        if self.has_chroot_instance():
            return
        if self.ismounted():
            command = "sudo " + self.umountcmd + " -l " + self.dest
            self.__subprocess(command=command)
        self.mounted = False

__myListObsLightMic = {}

def getObsLightMic(name=None):
    if not (name in __myListObsLightMic.keys()):
        __myListObsLightMic[name] = ObsLightMic()

    return __myListObsLightMic[name]


def isInit(name=None):
    if  (name in __myListObsLightMic.keys()):
        return True
    else:
        return False

@atexit.register
def destroy(name=None):
    if name == None:
        for aName in __myListObsLightMic.keys():
            __myListObsLightMic[aName].destroy()
            del __myListObsLightMic[aName]
    else:
        __myListObsLightMic[name].destroy()
        del __myListObsLightMic[name]

    return None
