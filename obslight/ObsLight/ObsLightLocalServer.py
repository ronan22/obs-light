# -*- coding: utf8 -*-
#
# Copyright 2012, Intel Inc.
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
Created on 27 fev. 2012

@author: Ronan Le Martret
'''

import os

import ObsLightConfig
from ObsLightSubprocess import SubprocessCrt
from ObsLightErr import ObsLightLocalServerErr

class ObsLightLocalServer(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.__mySubprocessCrt = SubprocessCrt()
        self.__serverPath = ObsLightConfig.getImageServerPath()


    def __subprocess(self, command, command2=None, waitMess=False):
        '''
        
        '''
        if command2 != None:
            return self.__mySubprocessCrt.execPipeSubprocess(command=command,
                                                             command2=command2)

        return self.__mySubprocessCrt.execSubprocess(command=command,
                                                     waitMess=waitMess)

    def isObsLightServerAvailable(self):
        return  os.path.isfile("/apache2/vhosts.d/obslight-image.conf")


    def addDirectoryToServer(self, directory):
        if os.path.isdir(directory):
            theBasename = os.path.basename(directory)
            projetPath = os.path.join(self.__serverPath, theBasename)
            command1 = "sudo mkdir " + projetPath
            command2 = "sudo mount --bind " + directory + " " + projetPath
            command31 = '''echo \'''' + projetPath + '''  *(rw,no_root_squash,nohide,insecure,no_subtree_check)\' '''
            command32 = '''sudo tee -a /etc/exports'''
            command4 = "sudo /usr/sbin/exportfs -ra"

            self.__subprocess(command=command1)
            self.__subprocess(command=command2)
            self.__subprocess(command=command31, command2=command32)
            self.__subprocess(command=command4)

            return 0
        else:
            raise ObsLightLocalServerErr("'" + directory + "' is not a directory.")
