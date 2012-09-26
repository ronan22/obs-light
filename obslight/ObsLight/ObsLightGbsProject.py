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

from ObsLightUtils import getFilteredFileList, isASpecFile, levenshtein
from ObsLightPackages import ObsLightPackages
from ObsLightChRoot import ObsLightChRoot
#import ObsLightManager
import ObsLightErr
from ObsLightSubprocess import SubprocessCrt
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

        self.setBuildConfigPath(fromSave.get("buildConfigPath", projectConfPath))

        self.__projectGbsConfig = fromSave.get("projectGbsConfig", None)

        if len(self.__repoList) == 0:
            msg = "A gbs '%s' like project need at least one Repository." % self.getName()
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
        cmd.append("obslight-createrpmlistfromspec")
        for aRepo in self.__buildRepoList:
            cmd.append("--repository")
            cmd.append(aRepo)

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
        Popen(cmd).wait()

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

        return ouputFile[1]


