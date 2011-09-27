'''
Created on 20 juin 2011

@author: rmartret
'''

class RPMFileObject(object):
    '''
    classdocs
    '''


    def __init__(self,rpmFileName=None):
        '''
        Constructor
        '''
        self.__rPMName=None
        self.__rPMVersion=None
        self.__rPMPackageVersion=None
        self.__rPMFile=rpmFileName
        
        
        