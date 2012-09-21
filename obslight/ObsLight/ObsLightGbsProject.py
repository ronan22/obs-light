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

class ObsLightProject(ObsLightBuilderProject):

    def __init__(self,
                 obsLightRepositories,
                 workingDirectory,
                 projectLocalName=None,
                 projectArchitecture=None,
                 projectTemplatePath=None,
                 projectConfPath=None,
                 addedRepo=None,
                 fromSave={}):

        ObsLightBuilderProject.__init__(self,
                             obsLightRepositories,
                             workingDirectory,
                             projectLocalName=projectLocalName,
                             projectArchitecture=projectArchitecture,
                             fromSave=fromSave)







