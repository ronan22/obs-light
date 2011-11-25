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
import select

BREAKPROCESS = False

class SubprocessCrt(object):
    '''
    Control All the subprocess in the ObsLight project. 
    '''
    def __init__(self):
        '''
        Init subprocess.
        '''
        self.__isPrintMess = False

    def execSubprocess(self, command=None, waitMess=False):
        '''
        Execute the "command" in a sub process,
        the "command" must be a valid bash command.
        If waitMess is set to True:
            -A message "please wait" is print at the start of the sub process,
            -A message "." is print every second during the sub process,
            -A message "work finish" is print at the end of the sub process
        '''
        #ObsLightPrintManager.obsLightPrint("command: " + command, isDebug=True)
        ObsLightPrintManager.getLogger().debug("command: " + command)
        #need Python 2.7.3 to do shlex.split(command) 
        splittedCommand = shlex.split(str(command))

        p = subprocess.Popen(splittedCommand,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        outputs = {p.stdout: {"EOF": False, "logcmd": ObsLightPrintManager.getLogger().info},
                   p.stderr: {"EOF": False, "logcmd": ObsLightPrintManager.getLogger().error}}
        while (not outputs[p.stdout]["EOF"] and
               not outputs[p.stderr]["EOF"]):
            for fd in select.select([p.stdout, p.stderr], [], [])[0]:
                output = fd.readline()
                if output == b"":
                    outputs[fd]["EOF"] = True
                else:
                    #outputs[fd]["logcmd"](output.rstrip())
                    outputs[fd]["logcmd"](output.decode("utf8", errors="replace").rstrip())
        res = p.returncode

        ObsLightPrintManager.getLogger().debug("command finished: " + command + ", return code: " + str(res))
        if res == None:
            res = 0
        return res





