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

class ObsLightMicProject(object):

    def __init__(self, name, workingDirectory, fromSave=None):
        self.__mySubprocessCrt = SubprocessCrt()

        self.__kickstartPath = None
        self.__architecture = None
        self.__imageType = None
        self.__name = name
        self.__workingDirectory = os.path.join(workingDirectory, self.__name)

        if fromSave != None:
            if "kickstartPath" in fromSave.keys():
                self.__kickstartPath = fromSave["kickstartPath"]
            if "architecture" in fromSave.keys():
                self.__architecture = fromSave["architecture"]
            if "imageType" in fromSave.keys():
                self.__imageType = fromSave["imageType"]
            if "name" in fromSave.keys():
                self.__name = fromSave["name"]
            if "workingDirectory" in fromSave.keys():
                self.__workingDirectory = fromSave["workingDirectory"]

        if not os.path.isdir(self.getProjectDirectory()):
            os.makedirs(self.getProjectDirectory())

    def __subprocess(self, command):
        return self.__mySubprocessCrt.execSubprocess(command)

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

    def getKickstartFile(self):
        """
        Get the kickstart file of the project.
        """
        return self.__kickstartPath

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
        '''
        Get the available architecture types as a list.
        '''
        # TODO Add to Manager
        return ["i686", "armv8" ]

    def getAvailableImageType(self):
        '''
        Get the available image types as a list of strings.
        '''
        # TODO: Add to Manager
        return ["fs", "livecd", "liveusb", "loop" , "raw" ]

    def runQemu(self):
        #TO TEST
        #"sudo qemu-system-x86_64 -hda latest/images/meego-netbook-ia32-qemu_local/meego-netbook-ia32-qemu_local-latest-hda.raw -boot c -m 2047 -k fr -vnc :1 -smp 2 -serial pty -M pc -cpu core2duo -append "root=/dev/sda1 console=ttyS0,115200n8" -kernel ./kernel/vmlinuz-2.6.37.2-6 -initrd ./kernel/initrd-2.6.37.2-6.img -vga std -sdl"
        #sudo screen /dev/pts/5
        #vncviewer :1
        pass
