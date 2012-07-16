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
Created on 2 Jui. 2012

@author: ronan@fridu.net
'''
import os
import shutil
import ObsLightConfig

from ObsLightSubprocess import SubprocessCrt

class ObsLightRepository(object):
    '''
    classdocs
    '''
    def __init__(self, pathDir, projectName):
        '''
        Constructor
        '''
        self.__repositoryPath = pathDir
        if not os.path.isdir(pathDir):
            os.makedirs(pathDir)
        self.__projectName = projectName
        self.__projectDir = os.path.join(self.__repositoryPath, self.__projectName)
        if not os.path.isdir(self.__projectDir):
            os.makedirs(self.__projectDir)

        self.__outOfDate = os.path.join(self.__projectDir, "outOfDate")

        self.__baseurl = None

        self.__createOptionDico = {}
#       -u --baseurl <url>
#              Optional base URL location for all files.
        if self.__baseurl != None:
            self.__createOptionDico["baseurl"] = "--baseurl " + self.__baseurl
        else:
            self.__createOptionDico["baseurl"] = ""

        self.__createOptionDico["path"] = self.__projectDir

        self.__mySubprocessCrt = SubprocessCrt()

    def __subprocess(self, command=None, waitMess=False, stdout=False):
        return self.__mySubprocessCrt.execSubprocess(command=command,
                                                     waitMess=waitMess,
                                                     stdout=stdout)

    def addRPM(self, absBuildRootpath, listRPM):
        needTouch = False
        for rpm in listRPM:
            srcPath = os.path.join(absBuildRootpath, rpm)
            dstPath = os.path.join(self.__projectDir, rpm)
            if os.path.isfile(srcPath):
                dstDir = os.path.dirname(dstPath)
                if os.path.isfile(srcPath) and srcPath.endswith(".rpm"):
                    if not os.path.isdir(dstDir):
                        os.makedirs(dstDir)

                shutil.copyfile(srcPath, dstPath)

                needTouch = True
        if needTouch:
            self.touch()

    def removeRPM(self, listRPM):
        needTouch = False

        for rpm in listRPM:
            rpmPath = os.path.join(self.__projectDir, rpm)

            if os.path.isfile(rpmPath):
                os.unlink(rpmPath)
                needTouch = True
        if needTouch:
            self.touch()

    def touch(self):
        with file(self.__outOfDate, 'a'):
            os.utime(self.__outOfDate, None)

    def removeTouch(self):
        if os.path.isfile(self.__outOfDate):
            os.unlink(self.__outOfDate)

    def createRepo(self):
#       --update
#              If  metadata already exists in the outputdir and an rpm is unchanged (based on file size and mtime) since the metadata was generated, reuse the existing metadata
#              rather than recalculating it. In the case of a large repository with only a few new or modified rpms this can significantly reduce I/O and processing time.
        command = "createrepo --update %(baseurl)s %(path)s"
        command = command % self.__createOptionDico

        res = self.__subprocess(command=command)
        self.removeTouch()
        return res


    def  isOutOfDate(self):
        if os.path.isfile(self.__outOfDate):
            return True
        else:
            return False

    def DeleteRepository(self):
        command = "rm -r %(path)s"
        command = command % self.__createOptionDico

        return self.__subprocess(command=command)


    def getLocalRepository(self):
        return ObsLightConfig.getLocalRepoServer() + "/" + self.__projectName

