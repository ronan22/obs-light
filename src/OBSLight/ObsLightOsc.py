'''
Created on 3 oct. 2011

@author: ronan
'''



import os

import subprocess

from osc import conf
from osc import core

from xml.etree import ElementTree

class ObsLightOsc(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.__confFile = os.path.join(os.environ['HOME'],".oscrc")
        aConf=conf.get_config()
        
    def initConf(self,api=None,user=None,passw=None,aliases=None):
        '''
        init a configuation for a API.
        '''
        if not os.path.isfile(self.__confFile): 
            conf.write_initial_config(self.__confFile, {'apiurl':api, 'user' : user, 'pass' : passw })
        
        aOscConfigParser=conf.get_configParser(self.__confFile)

        if not (api in  aOscConfigParser.sections()):
            aOscConfigParser.add_section( api)

        aOscConfigParser.set(api, 'user', user)
        aOscConfigParser.set(api, 'pass', passw)
        aOscConfigParser.set(api, 'aliases', aliases)
            
        file = open(self.__confFile, 'w')
        aOscConfigParser.write(file, True)
        if file: file.close()
        
    def getListPackage(self,obsServer=None,project=None):
        '''
            
        '''
        print "obsServer",obsServer
        print "project",project
        list_package=core.meta_get_packagelist(obsServer, project)
        return list_package
    
    def CheckoutPackage(self,obsServer=None,project=None,package=None,directory=None):
        '''
            
        '''
        os.chdir(directory)
        command="osc -A "+obsServer+" co "+project+" "+package
        command=command.split()
        p=subprocess.Popen(command , shell=False,stdout=subprocess.PIPE)
        p.wait()
        
    def getPackageStatus(self,obsServer=None,project=None,package=None,repos=None,arch=None):
        '''
            
        '''
        url=obsServer+"/build/"+project+"/"+repos+"/"+arch+"/"+package+"/_status"
        fileXML=core.http_request("GET", url).read()
        aElement=ElementTree.fromstring(fileXML)
        return aElement.attrib["code"]
        
    def createChRoot(self, chrootDir=None,projectDir=None ,repos=None,arch=None,specPath=None):
        '''
            
        '''
        os.chdir(projectDir)
        command="osc build --root="+chrootDir+" -x vim -x openssh-clients -x git -x strace -x iputils -x zypper --no-verify "+repos+" "+arch+" "+specPath
        print command
        command=command.split()
        p=subprocess.Popen(command , shell=False,stdout=subprocess.PIPE)
        p.wait()
        
        
myObsLightOsc=ObsLightOsc()

