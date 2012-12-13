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
Created on 21 sept. 2012

@author: Ronan Le Martret 
'''
from ObsLightBuilderProject import ObsLightBuilderProject
import os
import shlex
import shutil
import subprocess
import urllib
import tempfile

from ObsLightUtils import getFilteredFileList, isASpecFile, levenshtein
from ObsLightPackages import ObsLightPackages
from ObsLightChRoot import ObsLightChRoot
#import ObsLightManager
import ObsLightErr
from ObsLightSubprocess import SubprocessCrt
import subprocess


from ObsLightObject import ObsLightObject
import ObsLightOsc

import ObsLightConfig

import ObsLightGitManager
from ObsLightSpec import getSpecTagValue

import ObsLightTools

class ObsLightGbsProject(ObsLightBuilderProject):

    def __init__(self,
                 obsLightRepositories,
                 workingDirectory,
                 projectLocalName=None,
                 projectArchitecture=None,
                 projectConfPath=None,
                 repoList=[],
                 autoAddProjectRepo=True,
                 fromSave={}):
        
        ObsLightBuilderProject.__init__(self,
                                        obsLightRepositories,
                                        workingDirectory,
                                        projectLocalName=projectLocalName,
                                        projectArchitecture=projectArchitecture,
                                        fromSave=fromSave)

        #Set the type of the project
        self.setProjectType('gbs')
        self.__repoList = fromSave.get("repoList", repoList)
        
        projectConfPath=fromSave.get("buildConfigPath", projectConfPath)
        
        if projectConfPath is not None: 
            projectConflocalPath= os.path.join(self.getDirectory()  ,os.path.basename(projectConfPath))
        else:
            projectConflocalPath=None
            
        if projectConflocalPath != projectConfPath:
            shutil.copyfile(projectConfPath,projectConflocalPath)
        
        self.setBuildConfigPath(projectConflocalPath)

        self.__projectGbsConfig = fromSave.get("projectGbsConfig", None)

        if len(self.__repoList) == 0:
            msg = "The gbs '%s' like project need at least one Repository." % self.getName()
            raise ObsLightErr.ObsLightProjectsError(msg)

        if (self.__projectGbsConfig is None) :
            if autoAddProjectRepo:
                self.__repoList.append([self.getName(), self.getLocalRepository()])
            self.__projectGbsConfig = ObsLightTools.createGbsProjectConfig(self.getDirectory(),
                                                                           self.getName(),
                                                                           repoList)

    def getDic(self):
        aDic = ObsLightBuilderProject.getDic(self)
        aDic["projectGbsConfig"] = self.__projectGbsConfig
        aDic["repoList"] = self.__repoList
        return aDic

    def getProjectParameter(self, parameter):
        '''
        Get the value of a project parameter:
        the valid parameter is :
            projectGbsConfig
        '''
        if parameter == "projectGbsConfig":
            return self.__projectGbsConfig
        elif parameter == "title":
            return "Local project"
        elif parameter == "description":
            result = u''
            result += u'<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Repository:</p>'
            result += u'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
            result += u'<html>'
            result += u'<head><meta name="qrichtext" content="1" /><style type="text/css">\np, li { white-space: pre-wrap; }\n</style></head>'
            result += u'<body style=" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;">\n'
            for aRepoName, aRepoUrl in self.__repoList:
                result += u'<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">'
                result += u'<a href="%s">' % aRepoUrl
                result += u'<span style=" text-decoration: underline; color:#0057ae;">%s</span></a></p>\n' % aRepoName
            result += u'<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Build Conf:</p>'

            result += u'<a href="%s">' % self.getBuildConfigPath()
            result += u'<span style=" text-decoration: underline; color:#0057ae;">%s</span></a></p>\n' % self.getBuildConfigPath(False)
            result += u'</body></html>'
            return result
        else:
            return ObsLightBuilderProject.getProjectParameter(self, parameter)

    def setProjectParameter(self, parameter, value):
        '''
        Return the value of a parameter of the project:
        Valid parameters are:
            projectGbsConfig
        '''
        if parameter == "projectGbsConfig":
            self.__projectGbsConfig = value
        else:
            ObsLightBuilderProject.setProjectParameter(self, parameter, value)
        return 0

    def getProjectGbsConfig(self, fullPath=True):
        '''
        Return the path of the gbs project config file.
        '''
        if fullPath:
            return self.__projectGbsConfig
        else:
            os.path.basename(self.__projectGbsConfig)

    def createRpmList(self, specFile):
        buildConfig = self.getbuildConfigPath()
        longArch = self.getArchHierarchy()
        extraPackage = self.getExtraChrootPackagesList()

        ouputFile = tempfile.mkstemp(suffix=".ouputFile")
        errFile = tempfile.mkstemp(suffix=".errFile")

        cmd = []
        cmd.append("sudo /usr/bin/obslight-createrpmlistfromspec")
        for aRepoName, aRepoUrl in self.__repoList:
            cmd.append("--repository")
            cmd.append(aRepoUrl)

        cmd.append("--dist")
        cmd.append(self.getbuildConfigPath())

        cmd.append("--depfile")
        cmd.append(self.getDirectory() + "/_rpmcache")

        cmd.append("--spec")
        cmd.append(specFile)

        cmd.append("--archpath")
        cmd.append(longArch)

        for p in extraPackage:
            cmd.append("--addPackages")
            cmd.append(p)

        cmd.append("--stderr")
        cmd.append(errFile[1])

        cmd.append("--stdout")
        cmd.append(ouputFile[1])

        # FIXME: shouldn't it be .wait() instead of .communicate() ?
        res = self._subprocess(" ".join(cmd))
        if res != 0:
            msg = "Creating cache project '%s' was aborted." % self.getName()
            raise ObsLightErr.ObsLightProjectsError(msg)
#        subprocess.Popen(cmd).wait()

#        os.close(tmpSpec[0])
#        os.unlink(tmpSpec[1])

        err = ""
        if os.path.getsize(errFile[1]) > 0:
            with open(errFile[1], 'r') as f:
                noErr = True
                for line in f:
                    if line.startswith("expansion error") :
                        noErr = False
                    elif noErr == False:
                        err += line

        if len(err) > 0:
            raise ObsLightErr.ObsLightProjectsError(err)

        localRpmListFilePath = self.__createCachedRpmListOuputFile(ouputFile[1], self.__repoList)

        return localRpmListFilePath

    def __cacheRpmFile(self, rpmUrl, repoURL, cacheDir, buildTimeStamp=None):
        rpmFileDst = os.path.join(cacheDir, os.path.basename(rpmUrl))

        cmdDownload = "sudo /usr/lib/build/download %s %s" % (cacheDir, rpmUrl)

        if os.path.isfile(rpmFileDst) and buildTimeStamp is not None:
            cmdBuildTimeQuery = "rpm  -qp %s --queryformat=%%{BUILDTIME}" % rpmFileDst
            resTimeStamp = self._subprocess(cmdBuildTimeQuery, stdout=True)

            if buildTimeStamp != resTimeStamp:
                res = self._subprocess(cmdDownload)
                if res == 0:
                    return rpmFileDst
                else:
                    return None
            else:
                return rpmFileDst
        else:
            res = self._subprocess(cmdDownload)
            if res == 0:
                return rpmFileDst
            else:
                return None


    def __createCachedRpmListOuputFile(self, rpmListFilePath, reposList):
        repoMD5Dict = {}
        for aRepoName, aRepoUrl in reposList:
            repoMD5Dict[aRepoUrl] = ObsLightTools.getRepoCacheDirectory(aRepoUrl)
        rpmListCachedFilePath = tempfile.mkstemp(suffix=".rpmlist")
        f = open(rpmListFilePath, "r")

        lineList = []
        for line in f:
            lineList.append(line)
        f.close()

        fResult = open(rpmListCachedFilePath[1], "w")
        for i in range(len(lineList)):
            line = lineList[i]
            isUrlLine = True
            for b in [ "rpmid", "preinstall", "vminstall", "cbpreinstall", "cbinstall", "runscripts", "dist"]:
                if line.startswith(b):
                    isUrlLine = False
                    break
            if isUrlLine:
                rpmName, rpmUrl = line.split()
                rpmUrl.replace("\n", "")
                rpmidLine = lineList[i + 1]
                buildTimeStamp = None

                if rpmidLine.startswith("rpmid"):
                    splitRes = rpmidLine.split()
                    if len(splitRes) >= 3:
                        buildTimeStamp = splitRes[2]
                for r in repoMD5Dict.keys():
                    if rpmUrl.startswith(r):
                        rpmUrl = self.__cacheRpmFile(rpmUrl, r, repoMD5Dict[r], buildTimeStamp)
                        break

                fResult.write(rpmName + " " + rpmUrl + "\n")
            else:
                fResult.write(line)
        fResult.close()
        return rpmListCachedFilePath[1]



    def getWebProjectPage(self):
        return ""

    def getReposProject(self):
        return ""


