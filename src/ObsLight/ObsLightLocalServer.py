# -*- coding: utf8 -*-
'''
Created on 27 fev. 2012

@author: meego
'''

import os
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


    def __subprocess(self, command, command2=None, waitMess=False):
        '''
        
        '''
        if command2 != None:
            return self.__mySubprocessCrt.execPipeSubprocess(command=command,
                                                             command2=command2)

        return self.__mySubprocessCrt.execSubprocess(command=command,
                                                     waitMess=waitMess)

    def isObsLightServerAvailable(self):
        return  os.path.isfile("/etc/obslight/obslight.conf")


    def addDirectoryToServer(self, directory):
        if os.path.isdir(directory):
            theBasename = os.path.basename(directory)
            command1 = "sudo mkdir /srv/obslight/" + theBasename
            command2 = "sudo mount --bind " + directory + " /srv/obslight/" + theBasename
            command31 = '''echo '/srv/obslight/''' + theBasename + '''  *(rw,no_root_squash,nohide,insecure,no_subtree_check)' '''
            command32 = '''sudo tee -a /etc/exports'''
            command4 = "sudo /usr/sbin/exportfs -ra"

            self.__subprocess(command=command1)
            self.__subprocess(command=command2)
            self.__subprocess(command=command31, command2=command32)
            self.__subprocess(command=command4)

            return 0
        else:
            raise ObsLightLocalServerErr("'" + directory + "' is not a directory.")