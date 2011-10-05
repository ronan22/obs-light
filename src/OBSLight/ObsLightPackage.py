'''
Created on 30 sept. 2011

@author: ronan
'''

class ObsLightPackage(object):
    '''
    classdocs
    '''


    def __init__(self,name="", specFile="", listFile=[], status="", fromSave=None):
        '''
        Constructor
        '''
        if fromSave==None:
            self.__name=name
            self.__listFile=listFile
            self.__status=status
            self.__specFile=specFile
        else:
            self.__name=fromSave["name"]
            self.__listFile=fromSave["listFile"]
            self.__status=fromSave["status"]
            self.__specFile=fromSave["specFile"]

    def getDic(self):
        '''
        
        '''
        aDic={}
        aDic["name"]=self.__name
        aDic["listFile"]=self.__listFile
        aDic["status"]=self.__status
        aDic["specFile"]=self.__specFile
        
        return aDic
            
    def getStatus(self):
        '''
        
        '''
        return self.__status
            
    def getSpecFile(self):
        '''
        
        '''
        return self.__specFile
            
            
            