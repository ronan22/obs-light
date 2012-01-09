#
# Copyright 2011, Intel Inc.
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
Created on 24 oct. 2011

@author: meego
'''

import subprocess
import shlex

import ObsLightPrintManager
import select
import errno

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
                   p.stderr: {"EOF": False, "logcmd": ObsLightPrintManager.getLogger().warning}}
        while (not outputs[p.stdout]["EOF"] and
               not outputs[p.stderr]["EOF"]):
            try:
                # FIXME: add a timeout ?
                for fd in select.select([p.stdout, p.stderr], [], [])[0]:
                    output = fd.readline()
                    if output == b"":
                        outputs[fd]["EOF"] = True
                    else:
                        #outputs[fd]["logcmd"](output.rstrip())
                        outputs[fd]["logcmd"](output.decode("utf8", errors="replace").rstrip())
            except select.error as error:
                # see http://bugs.python.org/issue9867
                if error.args[0] == errno.EINTR:
                    ObsLightPrintManager.getLogger().warning(u"Got select.error: %s", unicode(error))
                    continue
                else:
                    raise


        # maybe p.wait() is better ?
        res = p.poll()
        ObsLightPrintManager.getLogger().debug(u"command finished: '%s', return code: %s"
                                               % (command, unicode(res)))
        if res == None:
            res = 0
        return res





