#
# Copyright 2011-2012, Intel Inc.
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

@author: Ronan Le Martret
@author: Florent Vennetier
'''

import subprocess
import shlex

import ObsLightPrintManager
import select
import errno

BREAKPROCESS = False

class SubprocessCrt(object):
    '''
    Control all the subprocesses in the ObsLight project. 
    '''
    def __init__(self):
        '''
        Initialize subprocess.
        '''
        self.__isPrintMess = False

    def execSubprocess(self, command, *_args, **_kwargs):
        '''
        Execute the "command" in a sub process,
        the "command" must be a valid bash command.
        _args and _kwargs are for compatibility.
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
