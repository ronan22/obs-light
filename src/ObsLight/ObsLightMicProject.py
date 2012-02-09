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
Created on jan 10 2012

@author: Ronan Le Martret <ronan@fridu.net>
@author: Florent Vennetier
'''

import os.path
import ObsLightErr
import shutil

from ObsLightSubprocess import SubprocessCrt
from ObsLightKickstartManager import ObsLightKickstartManager

class ObsLightMicProject(object):

    _ksManager = None

    def __init__(self, name, workingDirectory, fromSave=None):
        self.__mySubprocessCrt = SubprocessCrt()

        self.__kickstartPath = None
        self.__architecture = None
        self.__imageType = None
        self.__name = name
        self.__workingDirectory = os.path.join(workingDirectory, self.__name)

        if fromSave != None:
            if "architecture" in fromSave.keys():
                self.__architecture = fromSave["architecture"]
            if "imageType" in fromSave.keys():
                self.__imageType = fromSave["imageType"]
            if "name" in fromSave.keys():
                self.__name = fromSave["name"]
            if "workingDirectory" in fromSave.keys():
                self.__workingDirectory = fromSave["workingDirectory"]
            if "kickstartPath" in fromSave.keys():
                self.__kickstartPath = fromSave["kickstartPath"]
                self.__loadKsManager()

        if not os.path.isdir(self.getProjectDirectory()):
            os.makedirs(self.getProjectDirectory())

    def __subprocess(self, command):
        return self.__mySubprocessCrt.execSubprocess(command)

    def __loadKsManager(self):
        self._ksManager = ObsLightKickstartManager(self.getKickstartFile())

    def getProjectDirectory(self):
        """
        Get the project working directory.
        """
        return self.__workingDirectory

    def getDic(self):
        aDic = {}
        aDic["kickstartPath"] = self.__kickstartPath
        aDic["architecture"] = self.__architecture
        aDic["imageType"] = self.__imageType
        aDic["name"] = self.__name
        aDic["workingDirectory"] = self.__workingDirectory
        return aDic

# --- Kickstart management ---------------------------------------------------
    def setKickstartFile(self, filePath):
        """
        Set the kickstart file of this project.
        """
        if not os.path.isfile(filePath):
            raise ObsLightErr.ObsLightMicProjectErr("'%s' is not a file." % filePath)
        fileName = os.path.basename(filePath)
        wantedPath = os.path.join(self.getProjectDirectory(), fileName)
        if os.path.abspath(filePath) != wantedPath:
            shutil.copy(os.path.abspath(filePath), wantedPath)
        self.__kickstartPath = wantedPath
        self.__loadKsManager()

    def getKickstartFile(self):
        """
        Get the kickstart file of the project.
        """
        return self.__kickstartPath

    def saveKickstartFile(self, path=None):
        """
        Save the Kickstart of the project to `path`,
        or to the previous path if None.
        """
        self._ksManager.saveKickstart(path)

    def addKickstartRepository(self, baseurl, name, cost=None, **otherParams):
        """
        Add a package repository in the Kickstart file.
         baseurl: the URL of the repository
         name:    a name for this repository
         cost:    the cost of this repository, from 0 (highest priority) to 99, or None
        Keyword arguments can be (default value):
        - mirrorlist (""):
        - priority (None):
        - includepkgs ([]):
        - excludepkgs ([]):
        - save (False): keep the repository in the generated image
        - proxy (None):
        - proxy_username (None):
        - proxy_password (None):
        - debuginfo (False):
        - source (False):
        - gpgkey (None): the address of the GPG key of this repository
            on the generated filesystem (ex: file:///etc/pki/rpm-gpg/RPM-GPG-KEY-meego)
        - disable (False): add the repository as disabled
        - ssl_verify ("yes"):
        """
        self._ksManager.addRepository(baseurl, name, cost, **otherParams)

    def removeKickstartRepository(self, name):
        """
        Remove the `name` package repository from the Kickstart file.
        """
        self._ksManager.removeRepository(name)

    def getKickstartRepositoryDictionaries(self):
        """
        Return a list of repository dictionaries.
        """
        repoList = []
        for repoName in self._ksManager.getRepositoryList():
            repoList.append(self._ksManager.getRepositoryDict(repoName))
        return repoList

    def addKickstartPackage(self, name, excluded=False):
        """
        Add the package `name` in the Kickstart file.
        "excluded" parameter allows to add package as "explicitly excluded"
        (defaults to False).
        """
        if excluded:
            self._ksManager.addExcludedPackage(name)
        else:
            self._ksManager.addPackage(name)

    def removeKickstartPackage(self, name):
        """
        Remove the package `name` from the Kickstart file.
        """
        # We don't know if package was explicitly excluded or not
        # so we try to remove it from both lists.
        self._ksManager.removePackage(name)
        self._ksManager.removeExcludedPackage(name)

    def getKickstartPackageDictionaries(self):
        pkgList = []
        for pkgName in self._ksManager.getPackageList():
            pkgList.append({"name": pkgName, "excluded": False})
        for pkgName in self._ksManager.getExcludedPackageList():
            pkgList.append({"name": pkgName, "excluded": True})
        return pkgList

    def addKickstartPackageGroup(self, name):
        """
        Add the package group `name` in the Kickstart file.
        """
        self._ksManager.addPackageGroup(name)

    def removeKickstartPackageGroup(self, name):
        """
        Remove the package group `name` from the Kickstart file.
        """
        self._ksManager.removePackageGroup(name)

    def getKickstartPackageGroupDictionaries(self):
        pkgGrpList = []
        for grpName in self._ksManager.getPackageGroupList():
            pkgGrpList.append({"name": grpName})
        return pkgGrpList

    def addOrChangeKickstartCommand(self, fullText, command=None):
        self._ksManager.addOrChangeCommand(fullText, command)

    def removeKickstartCommand(self, command):
        self._ksManager.removeCommand(command)

    def getKickstartCommandDictionaries(self):
        return self._ksManager.getFilteredCommandDictList()
# --- end Kickstart management -----------------------------------------------

    def deleteProjectDirectory(self):
        """
        Recursively delete the project working directory.
        """
        shutil.rmtree(self.getProjectDirectory())

    def setArchitecture(self, arch):
        """
        Set the architecture of the project.
        """
        self.__architecture = arch

    def getArchitecture(self):
        """
        Get the architecture of the project.
        """
        return self.__architecture

    def setImageType(self, imageType):
        """
        Set the image type of the project.
        """
        self.__imageType = imageType

    def getImageType(self):
        """
        Get the image type of the project.
        """
        return self.__imageType

    def createImage(self):
        """
        Launch the build of an image.
        """
        logFilePath = os.path.join(self.getProjectDirectory(), "buildLog")
        cacheDirPath = os.path.join(self.getProjectDirectory(), "cache")
        cmd = "sudo mic create " + self.getImageType()
        cmd += " " + self.getKickstartFile()
        cmd += " --logfile=" + logFilePath
        cmd += " --cachedir=" + cacheDirPath
        cmd += " --outdir=" + self.getProjectDirectory()
        cmd += " --arch=" + self.__architecture
        cmd += " --release=latest"
        print cmd
        self.__subprocess(cmd)

    def getAvailableArchitectures(self):
        """
        Get the available architecture types as a list.
        """
        return ["i686", "armv8" ]

    def getAvailableImageTypes(self):
        """
        Get the available image types as a list of strings.
        """
        return ["fs", "livecd", "liveusb", "loop" , "raw" ]

    def runQemu(self):
        #TO TEST
        #"sudo qemu-system-x86_64 -hda latest/images/meego-netbook-ia32-qemu_local/meego-netbook-ia32-qemu_local-latest-hda.raw -boot c -m 2047 -k fr -vnc :1 -smp 2 -serial pty -M pc -cpu core2duo -append "root=/dev/sda1 console=ttyS0,115200n8" -kernel ./kernel/vmlinuz-2.6.37.2-6 -initrd ./kernel/initrd-2.6.37.2-6.img -vga std -sdl"
        #sudo screen /dev/pts/5
        #vncviewer :1
        pass
