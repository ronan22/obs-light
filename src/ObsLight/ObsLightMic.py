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

import os 
import subprocess
import shlex
import glob
from mic import chroot
import mic.imgcreate as imgcreate

import ObsLightManager

class ObsLightMic(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.__isInit = False
        
        self.__chroot_lockfd = -1
        self.__chroot_lock = ""
    
        self.__globalmounts = None
        self.__qemu_emulator = None
        
        self.__chrootDirectory = None
        
    def __del__(self):
        '''
        
        '''
        if self.__isInit == True:
            self.cleanup_chrootenv(bindmounts=self.__bindmounts)

    
    def isInit(self):
        '''
        
        '''
        return self.__isInit
    
    def initChroot(self, chrootDirectory=None,
                        chrootTransfertDirectory=None,
                        transfertDirectory=None):
        '''
        
        '''
        self.__bindmounts = chrootTransfertDirectory + ":" + transfertDirectory + ";"
        self.__chrootDirectory = chrootDirectory
        self.__findArch()
        
        self.setup_chrootenv(bindmounts=self.__bindmounts)
        
        self.__isInit = True
        
    def __subprocess(self, command=None):
        '''
        
        '''
        import ObsLightManager
        ObsLightManager.obsLightPrint("command: " + command, isDebug=True)
        command = shlex.split(command)
        return subprocess.call(command, stdin=open(os.devnull, 'rw'), close_fds=True)
        
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
                    ObsLightManager.obsLightPrint("%s will be mounted by default." % srcdst[0] , isDebug=True)
                    continue
                if srcdst[1] == "" or srcdst[1] == "none":
                    srcdst[1] = None
                else:
                    srcdst[1] = os.path.abspath(os.path.expanduser(srcdst[1]))
                    if os.path.isdir(chrootdir + "/" + srcdst[1]):
                        #chroot.pwarning("%s has existed in %s , skip it." % (srcdst[1], chrootdir))
                        ObsLightManager.obsLightPrint("%s has existed in %s , skip it." % (srcdst[1], chrootdir) , isDebug=True)
                        continue
                chrootmounts.append(BindChrootMount(srcdst[0], chrootdir, srcdst[1]))
            
            """Default bind mounts"""
            chrootmounts.append(BindChrootMount("/proc", chrootdir, None))
            chrootmounts.append(BindChrootMount("/proc/sys/fs/binfmt_misc", self.__chrootDirectory, None))
            chrootmounts.append(BindChrootMount("/sys", chrootdir, None))
            chrootmounts.append(BindChrootMount("/dev", chrootdir, None))
            chrootmounts.append(BindChrootMount("/dev/pts", chrootdir, None))
            chrootmounts.append(BindChrootMount("/dev/shm", chrootdir, None))
            chrootmounts.append(BindChrootMount("/var/lib/dbus", chrootdir, None))
            chrootmounts.append(BindChrootMount("/var/run/dbus", chrootdir, None))

            for kernel in os.listdir("/lib/modules"):
                chrootmounts.append(BindChrootMount("/lib/modules/" + kernel, chrootdir, None, "ro"))
    
            self.__globalmounts = chrootmounts
    
        def bind_mount(chrootmounts):
            for b in chrootmounts:
                import ObsLightManager
                ObsLightManager.obsLightPrint("bind_mount: %s -> %s" % (b.src, b.dest), isDebug=True)
                b.mount()
    
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
                import ObsLightManager
                ObsLightManager.obsLightPrint("bind_unmount: %s -> %s" % (b.src, b.dest), isDebug=True)
                b.unmount()

                
        def cleanup_resolv(chrootdir):
            fd = open(chrootdir + "/etc/resolv.conf", "w")
            fd.truncate(0)
            fd.close()
    
        def kill_processes(chrootdir):
            for procfile in glob.glob("/proc/*/root"):
                try:
                    if os.readlink(procfile) == chrootdir:
                        pid = int(procfile.split("/")[2])
                        os.kill(pid, 9)
                except:
                    pass
    
        self.__chroot_lockfd.close()
        bind_unmount(self.__globalmounts)
        if not imgcreate.my_fuser(self.__chroot_lock):
            #cleanup_resolv(self.__chrootDirectory)

            if os.path.exists(self.__chrootDirectory + "/etc/mtab"):
                os.unlink(self.__chrootDirectory + "/etc/mtab")
            kill_processes(self.__chrootDirectory)
        self.cleanup_mountdir(self.__chrootDirectory, bindmounts)
        if self.__qemu_emulator:
            
            command = "sudo rm " + self.__chrootDirectory + self.__qemu_emulator
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
                    import ObsLightManager
                    ObsLightManager.obsLightPrint("dir %s isn't empty." % tmpdir, isDebug=True)
                    #chroot.pwarning("dir %s isn't empty." % tmpdir)
        
    def isArmArch(self, directory=None):
        '''
        
        '''
        self.__chrootDirectory = directory
        self.__findArch()
        if self.__qemu_emulator:
            return True
        else:
            return False
        
        
    def __findArch(self):
        '''
        
        '''
        dev_null = os.open("/dev/null", os.O_WRONLY)
        files_to_check = ["/bin/bash", "/sbin/init", "/bin/ps", "/bin/kill"]
    
        architecture_found = False
    
        """ Register statically-linked qemu-arm if it is an ARM fs """
        qemu_emulator = None
    
        for ftc in files_to_check:
            ftc = "%s/%s" % (self.__chrootDirectory, ftc)
    
            # Return code of 'file' is "almost always" 0 based on some man pages
            # so we need to check the file existance first.
            if not os.path.exists(ftc):
                continue
    
            filecmd = chroot.find_binary_path("file")
            initp1 = subprocess.Popen([filecmd, ftc], stdout=subprocess.PIPE, stderr=dev_null)
            fileOutput = initp1.communicate()[0].strip().split("\n")
    
            for i in range(len(fileOutput)):
                if fileOutput[i].find("ARM") > 0:
                    qemu_emulator = self.setup_qemu_emulator(self.__chrootDirectory, "arm")
                    architecture_found = True
                    break
                if fileOutput[i].find("Intel") > 0:
                    architecture_found = True
                    break
    
            if architecture_found:
                break
    
        os.close(dev_null)
        if not architecture_found:
            raise imgcreate.CreatorError("Failed to get architecture from any of the following files %s from chroot." % files_to_check)
        
        self.__qemu_emulator = qemu_emulator
        
        
    def chroot(self, chrootdir, bindmounts=None, execute="/bin/bash"):
        def mychroot():
            os.chroot(chrootdir)
            os.chdir("/")
        
        self.__findArch()

        try:
            import ObsLightManager
            ObsLightManager.obsLightPrint("Launching shell. Exit to continue.", isDebug=True)
            ObsLightManager.obsLightPrint("----------------------------------", isDebug=True)
            self.setup_chrootenv(chrootdir, bindmounts)
            args = shlex.split(execute)
            subprocess.call(args, preexec_fn=mychroot)
            
        except OSError, (err, msg):
            import ObsLightManager
            ObsLightManager.obsLightPrint(err, isDebug=True)
            raise imgcreate.CreatorError("Failed to chroot: %s" % msg)
        finally:
            self.cleanup_chrootenv(chrootdir, bindmounts)
            
    def setup_qemu_emulator(self, rootdir, arch):
        # mount binfmt_misc if it doesn't exist
        if not os.path.exists("/proc/sys/fs/binfmt_misc"):
            modprobecmd = imgcreate.find_binary_path("modprobe")
            command = "sudo " + modprobecmd + " binfmt_misc"
            self.__subprocess(command=command)
        if not os.path.exists("/proc/sys/fs/binfmt_misc/register"):
            mountcmd = imgcreate.find_binary_path("mount")
            command = "sudo " + mountcmd + " -t binfmt_misc none /proc/sys/fs/binfmt_misc"
            self.__subprocess(command=command)
        # qemu_emulator is a special case, we can't use find_binary_path
        # qemu emulator should be a statically-linked executable file
        qemu_emulator = "/usr/bin/qemu-arm"
        if not os.path.exists(qemu_emulator) or not imgcreate.is_statically_linked(qemu_emulator):
            qemu_emulator = "/usr/bin/qemu-arm-static"
        if not os.path.exists(qemu_emulator):
            raise imgcreate.CreatorError("Please install a statically-linked qemu-arm")
        if not os.path.exists(rootdir + "/usr/bin"):
            command = "sudo mkdir -p " + rootdir + " /usr/bin"
            self.__subprocess(command=command)
        command = "sudo cp " + qemu_emulator + " " + rootdir + qemu_emulator
        self.__subprocess(command=command)  
        # disable selinux, selinux will block qemu emulator to run
        #if os.path.exists("/usr/sbin/setenforce"):
        #   subprocess.call(["/usr/sbin/setenforce", "0"])
    
        node = "/proc/sys/fs/binfmt_misc/arm"
        if imgcreate.is_statically_linked(qemu_emulator) and os.path.exists(node):
            return qemu_emulator
    
        # unregister it if it has been registered and is a dynamically-linked executable
        if not imgcreate.is_statically_linked(qemu_emulator) and os.path.exists(node):
            qemu_unregister_string = "-1\n"
            command = "sudo chmod o+w /proc/sys/fs/binfmt_misc/arm"
            self.__subprocess(command=command)
            fd = open("/proc/sys/fs/binfmt_misc/arm", "w")
            fd.write(qemu_unregister_string)
            fd.close()
            command = "sudo  chmod o-w /proc/sys/fs/binfmt_misc/arm"
            self.__subprocess(command=command)
#            subprocess.call(["sudo", "echo", qemu_unregister_string, ">", "/proc/sys/fs/binfmt_misc/arm"])
    
        #TODO
        # register qemu emulator for interpreting other arch executable file
        if not os.path.exists(node):
            qemu_arm_string = ":arm:M::\\x7fELF\\x01\\x01\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x02\\x00\\x28\\x00:\\xff\\xff\\xff\\xff\\xff\\xff\\xff\\x00\\xff\\xff\\xff\\xff\\xff\\xff\\xff\\xff\\xfa\\xff\\xff\\xff:%s:\n" % qemu_emulator
            command = "sudo chmod o+w /proc/sys/fs/binfmt_misc/register"
            self.__subprocess(command=command)
            fd = open("/proc/sys/fs/binfmt_misc/register", "w")
            fd.write(qemu_arm_string)
            fd.close()
            command = "sudo chmod o+w /proc/sys/fs/binfmt_misc/register"
            self.__subprocess(command=command)
#            subprocess.call(["sudo", "echo", qemu_arm_string, ">", "/proc/sys/fs/binfmt_misc/register"])
    
        return qemu_emulator


class BindChrootMount:
    """Represents a bind mount of a directory into a chroot."""
    def __init__(self, src, chroot, dest=None, option=None):
        self.src = src
        self.root = os.path.abspath(os.path.expanduser(chroot))
        self.option = option

        if not dest:
            dest = src
        self.dest = self.root + "/" + dest

        self.mounted = False
        self.mountcmd = imgcreate.find_binary_path("mount")
        self.umountcmd = imgcreate.find_binary_path("umount")

    def __subprocess(self, command=None):
        '''
        
        '''
        import ObsLightManager
        ObsLightManager.obsLightPrint("command: " + command, isDebug=True)
        command = shlex.split(command)
        return subprocess.call(command, stdin=open(os.devnull, 'rw'), close_fds=True)

    def ismounted(self):
        ret = False
        dev_null = os.open("/dev/null", os.O_WRONLY)
        catcmd = imgcreate.find_binary_path("cat")
        args = [ catcmd, "/proc/mounts" ]
        proc_mounts = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=dev_null)
        outputs = proc_mounts.communicate()[0].strip().split("\n")
        for line in outputs:
            if line.split()[1] == os.path.abspath(self.dest):
                ret = True
                break
        os.close(dev_null)
        return ret

    def has_chroot_instance(self):
        lock = os.path.join(self.root, ".chroot.lock")
        return imgcreate.my_fuser(lock)

    def mount(self):
        if self.mounted or self.ismounted():
            return

        #imgcreate.makedirs(self.dest)
        command = "sudo mkdir -p " + self.dest
        self.__subprocess(command=command)
        command = "sudo " + self.mountcmd + " --bind " + self.src + " " + self.dest
        rc = self.__subprocess(command=command)
        if rc != 0:
            raise imgcreate.MountError("Bind-mounting '%s' to '%s' failed" % 
                             (self.src, self.dest))
        if self.option:
            rc = subprocess.call(["sudo", self.mountcmd, "--bind", "-o", "remount,%s" % self.option, self.dest])
            if rc != 0:
                raise imgcreate.MountError("Bind-remounting '%s' failed" % self.dest)
        self.mounted = True

    def unmount(self):
        if self.has_chroot_instance():
            return

        if self.ismounted():
            command = "sudo " + self.umountcmd + " -l " + self.dest
            self.__subprocess(command=command)
        self.mounted = False



myObsLightMic = ObsLightMic()
