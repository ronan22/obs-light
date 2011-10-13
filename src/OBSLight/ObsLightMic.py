'''
Created on 4 oct. 2011

@author: meego
'''
import os 
import subprocess
import shlex
import shutil
import glob
from mic import chroot
import mic.imgcreate as imgcreate

class ObsLightMic(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.__isInit=False
        
        self.__chroot_lockfd = -1
        self.__chroot_lock = ""
    
        self.__globalmounts=None
        self.__qemu_emulator=None
        
        self.__chrootDirectory=None
        
    def __del__(self):
        '''
        
        '''
        if self.__isInit==True:
            self.cleanup_chrootenv(bindmounts = self.__bindmounts)
    
    def isInit(self):
        '''
        
        '''
        return self.__isInit
    
    def initChroot(self,chrootDirectory=None,chrootTransfertDirectory=None,transfertDirectory=None):
        '''
        
        '''
        self.__bindmounts=chrootTransfertDirectory+":"+transfertDirectory+";"
        
        self.__chrootDirectory=chrootDirectory
        self.__findArch()
        self.setup_chrootenv(bindmounts = self.__bindmounts)
        
        self.__isInit=True
        
    def setup_chrootenv(self, bindmounts = None):
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
                if srcdst[0] in ("/proc", "/proc/sys/fs/binfmt_misc", "/", "/sys", "/dev", "/dev/pts", "/dev/shm", "/var/lib/dbus", "/var/run/dbus"):
                    chroot.pwarning("%s will be mounted by default." % srcdst[0])
                    continue
                if srcdst[1] == "" or srcdst[1] == "none":
                    srcdst[1] = None
                else:
                    srcdst[1] = os.path.abspath(os.path.expanduser(srcdst[1]))
                    if os.path.isdir(chrootdir + "/" + srcdst[1]):
                        chroot.pwarning("%s has existed in %s , skip it." % (srcdst[1], chrootdir))
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
    
            self.__globalmounts= chrootmounts
    
        def bind_mount(chrootmounts):
            for b in chrootmounts:
                print "bind_mount: %s -> %s" % (b.src, b.dest)
                b.mount()
    
        def setup_resolv(chrootdir):
            subprocess.call(["sudo","cp", "/etc/resolv.conf",chrootdir + "/etc/resolv.conf"])
            
        get_bind_mounts(self.__chrootDirectory, bindmounts)
        bind_mount(self.__globalmounts)
        setup_resolv(self.__chrootDirectory)
        mtab = "/etc/mtab"
        dstmtab = self.__chrootDirectory + mtab
        if not os.path.islink(dstmtab):
            subprocess.call(["sudo","cp", mtab,dstmtab])
            
        self.__chroot_lock = os.path.join(self.__chrootDirectory, ".chroot.lock")
        self.__chroot_lockfd = open(self.__chroot_lock, "w")
        return self.__globalmounts
        
    def cleanup_chrootenv(self, bindmounts = None):
        def bind_unmount(chrootmounts):
            chrootmounts.reverse()
            for b in chrootmounts:
                print "bind_unmount: %s -> %s" % (b.src, b.dest)
                b.unmount()

                
        def cleanup_resolv(chrootdir):
            fd = open(chrootdir + "/etc/resolv.conf", "w")
            fd.truncate(0)
            fd.close()
    
        def kill_processes(chrootdir):
            for file in glob.glob("/proc/*/root"):
                try:
                    if os.readlink(file) == chrootdir:
                        pid = int(file.split("/")[2])
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
            os.unlink(self.__chrootDirectory + self.__qemu_emulator)
        
        
    def cleanup_mountdir(self,chrootdir, bindmounts):
        if bindmounts == "" or bindmounts == None:
            return
        chrootmounts = []
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
                    subprocess.call(["sudo","rm", "-r",tmpdir])
                else:
                    chroot.pwarning("dir %s isn't empty." % tmpdir)
        
    def isArmArch(self,directory=None):
        '''
        
        '''
        self.__chrootDirectory=directory
        self.__findArch()
        if self.__qemu_emulator:
            return True
        else:
            return False
        
        
    def __findArch(self):
        '''
        
        '''
        dev_null = os.open("/dev/null", os.O_WRONLY)
        files_to_check = ["/bin/bash", "/sbin/init"]
    
        architecture_found = False
    
        """ Register statically-linked qemu-arm if it is an ARM fs """
        qemu_emulator = None
    
        for ftc in files_to_check:
            ftc = "%s/%s" % (self.__chrootDirectory,ftc)
    
            # Return code of 'file' is "almost always" 0 based on some man pages
            # so we need to check the file existance first.
            if not os.path.exists(ftc):
                continue
    
            filecmd = chroot.find_binary_path("file")
            initp1 = subprocess.Popen([filecmd, ftc], stdout=subprocess.PIPE, stderr=dev_null)
            fileOutput = initp1.communicate()[0].strip().split("\n")
    
            for i in range(len(fileOutput)):
                if fileOutput[i].find("ARM") > 0:
                    qemu_emulator = imgcreate.setup_qemu_emulator(self.__chrootDirectory, "arm")
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
        
        self.__qemu_emulator= qemu_emulator
        
        
    def chroot(self,chrootdir, bindmounts = None, execute = "/bin/bash"):
        def mychroot():
            os.chroot(chrootdir)
            os.chdir("/")
        
        self.__findArch()

        try:
            print "Launching shell. Exit to continue."
            print "----------------------------------"
            self.setup_chrootenv(chrootdir, bindmounts)
            args = shlex.split(execute)
            subprocess.call(args, preexec_fn = mychroot)
            
        except OSError, (err, msg):
            raise imgcreate.CreatorError("Failed to chroot: %s" % msg)
        finally:
            self.cleanup_chrootenv(chrootdir, bindmounts)

class BindChrootMount:
    """Represents a bind mount of a directory into a chroot."""
    def __init__(self, src, chroot, dest = None, option = None):
        self.src = src
        self.root = os.path.abspath(os.path.expanduser(chroot))
        self.option = option

        if not dest:
            dest = src
        self.dest = self.root + "/" + dest

        self.mounted = False
        self.mountcmd = imgcreate.find_binary_path("mount")
        self.umountcmd = imgcreate.find_binary_path("umount")

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
        subprocess.call(["sudo","mkdir","-p", self.dest])
        
        rc = subprocess.call(["sudo",self.mountcmd, "--bind", self.src, self.dest])
        if rc != 0:
            raise imgcreate.MountError("Bind-mounting '%s' to '%s' failed" %
                             (self.src, self.dest))
        if self.option:
            rc = subprocess.call(["sudo",self.mountcmd, "--bind", "-o", "remount,%s" % self.option, self.dest])
            if rc != 0:
                raise imgcreate.MountError("Bind-remounting '%s' failed" % self.dest)
        self.mounted = True

    def unmount(self):
        if self.has_chroot_instance():
            return

        if self.ismounted():
            subprocess.call(["sudo",self.umountcmd, "-l", self.dest])
        self.mounted = False





myObsLightMic=ObsLightMic()
        
        
        