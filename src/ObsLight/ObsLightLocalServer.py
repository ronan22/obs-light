'''
Created on 27 fev. 2012

@author: meego
'''

import os

class ObsLightLocalServer(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''

    def isObsLightServerIsAvailable(self):
        return  os.path.isfile("/etc/obslight/obslight.conf")


    def addDirectoryToServer(self, directory):
        if os.path.isdir(directory):

            return 0

        return 1
