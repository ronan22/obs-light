'''
Created on 7 juil. 2011

@author: hellmann
'''

import sys
from OBSLight import LocalRepository
from OBSLight import babysitter


class CTestRepo(object):
    
    def __init__(self):
        '''
        
        '''
        
    def UpDateCorrectlyRepository(self):
            
        url='http://repo.meego.com/MeeGo/builds/1.2.80/1.2.80.8.0.20110628.2/repos/oss/ia32/packages/repodata/'
        path='./RepoTest/MyRepo'
        aLocalRepository=LocalRepository.LocalRepository()
        return aLocalRepository.upDateRepositoryVerif(url,path)  
              
    
    def UpDateWronglyRepository(self):
            
        url='httTTp://repo.meego.com/MeeGo/builds/1.2.80/1.2.80.8.0.20110628.2/repos/oss/ia32/packages/repodata/'
        path='./RepoTest/MyRepo'
        aLocalRepository=LocalRepository.LocalRepository()
        return aLocalRepository.upDateRepositoryVerif(url,path)  