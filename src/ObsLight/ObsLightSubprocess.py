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
import fcntl
import os
import time

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

        ObsLightPrintManager.getLogger().debug("command: " + command)
        #need Python 2.7.3 to do shlex.split(command) 
        splittedCommand = shlex.split(str(command))

#        f_stdout = open("/dev/shm/tmp_stdout", 'w+')
#        f_stderr = open("/dev/shm/tmp_stderr", 'w+')
#        p = subprocess.Popen(splittedCommand,
#                             stdout=f_stdout,
#                             stderr=f_stderr)


        p = subprocess.Popen(splittedCommand,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        f_stdout = p.stdout
        f_stderr = p.stderr

        flags = fcntl.fcntl(f_stdout, fcntl.F_GETFL)
        if not f_stdout.closed:
            fcntl.fcntl(f_stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)

        flags = fcntl.fcntl(f_stderr, fcntl.F_GETFL)
        if not f_stderr.closed:
            fcntl.fcntl(f_stderr, fcntl.F_SETFL, flags | os.O_NONBLOCK)

        logger = ObsLightPrintManager.getSubprocessLogger()
        outputs = {f_stdout: {"EOF": False, "logcmd": logger.info},
                   f_stderr: {"EOF": False, "logcmd": logger.warning}}

        idleTime = 0
        while ((not outputs[f_stdout]["EOF"] and
               not outputs[f_stderr]["EOF"]) or
               (p.poll() == None)):
            try:
                timedOut = True
                selectTimeout = 60
                for fd in select.select([f_stdout, f_stderr], [], [], selectTimeout)[0]:
                    timedOut = False
                    output = fd.read()
                    for line in output.split("\n"):
                        if line == b"" and not output.endswith("\n"):
                            outputs[fd]["EOF"] = True
                        elif line != "":
                            outputs[fd]["logcmd"](line.decode("utf8", "replace").rstrip())
                if timedOut:
                    idleTime += selectTimeout
                    message = "Subprocess still working for %s"
                    message = message % time.strftime("%Hh%Mm%Ss",
                                                      time.gmtime(idleTime))
                    ObsLightPrintManager.getLogger().debug(message)
                else:
                    idleTime = 0

            except select.error as error:
                # see http://bugs.python.org/issue9867
                if error.args[0] == errno.EINTR:
                    ObsLightPrintManager.getLogger().warning("Got select.error: %s",
                                                             unicode(error))
                    continue
                else:
                    raise

        # maybe p.wait() is better ?
        res = p.poll()
        ObsLightPrintManager.getLogger().debug("command finished: '%s', return code: %s"
                                               % (command, unicode(res)))

        if res is None:
            res = 0
        return res

    def execPipeSubprocess(self, command, command2):
        ObsLightPrintManager.getLogger().debug("command: " + command + " | " + command2)
        splittedCommand1 = shlex.split(str(command))
        splittedCommand2 = shlex.split(str(command2))
        p1 = subprocess.Popen(splittedCommand1, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(splittedCommand2, stdin=p1.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()

        return 0





