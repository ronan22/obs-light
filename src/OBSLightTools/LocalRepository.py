'''
Created on 17 juin 2011

@author: rmartret
'''

class LocalRepository(object):
    '''
    classdocs
    '''


    def __init__(self,url=None):
        '''
        TO DO
        '''
        
        self.__repositoryName=None
        self.__creationDate=None
        self.__BaseReposUrl=None
        self.__reposID=None
        self.__reposVersion=None
        self.__repositoryStatus=None
        
        self.__listRPM={}
        self.__listGroupRPM={}
        
        
        