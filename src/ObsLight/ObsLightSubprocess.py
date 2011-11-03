'''
Created on 24 oct. 2011

@author: meego
'''

import os
import sys
import subprocess
import shlex
import time

from threading import Thread
import ObsLightPrintManager


BREAKPROCESS = False


 
class SubprocessCrt(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.__isPrintMess = False
        
    def execSubprocess(self, command=None, waitMess=False):
        '''
        
        '''
        ObsLightPrintManager.obsLightPrint("command: " + command, isDebug=True)
        #need Python 2.7.3 to do shlex.split(command) 
        splittedCommand = shlex.split(str(command))
        
        if ObsLightPrintManager.VERBOSE == True:
            return subprocess.call(splittedCommand,
                                   stdin=open(os.devnull, 'rw'),
                                   close_fds=True) 
        else:
            if waitMess:
                self.__isPrintMess = True
                aThread = Thread(group=None,
                                 target=self.printWaitMess,
                                 name=None,
                                 args=(),
                                 kwargs=None,
                                 verbose=None)
                aThread.start()
                
            res = subprocess.Popen(splittedCommand,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   stdin=open(os.devnull, 'rw'))
            fileErr = res.communicate()[1]
            
            if waitMess:
                self.__isPrintMess = False
            
            if res.returncode != 0:
                sys.stdout.flush()  
                sys.stderr.write(fileErr)
                sys.stderr.flush()        
            return res.returncode

    def printWaitMess(self):
        '''
        
        '''
        global BREAKPROCESS
        
        sys.stdout.write("please wait\n")
        sys.stdout.flush()
        while((self.__isPrintMess)and(not BREAKPROCESS)):
            sys.stdout.write(".")
            sys.stdout.flush()
            i = 0
            while((i <= 10)and((self.__isPrintMess)and(not BREAKPROCESS))):
                time.sleep(0.1)
                i += 1
                
        sys.stdout.write("work finish\n")
        sys.stdout.flush()
        
