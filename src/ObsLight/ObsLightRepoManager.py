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
Created on 29 May 2012

@author: Ronan Le Martret
'''

import ObsLightErr
from ObsLightSubprocess import SubprocessCrt
import os
import pickle
import tempfile

class ObsLightRepoManager(object):
    '''
    class Git management
    '''

    def __init__(self, projectChroot):

        '''
        Constructor
        '''
        self.__chroot = projectChroot
        self.__mySubprocessCrt = SubprocessCrt()

        self.__zyppLock = "/var/run/zypp.pid"

    def testZypperAvailable(self):
        if os.path.exists(self.__zyppLock):
            try:
                with open(self.__zyppLock, "r") as pidFile:
                    pid = pidFile.readline()[:-1]
            except :# pylint: disable-msg=W0702
                return 0
            if os.path.exists("/proc/%s/comm" % (pid)):
                try:
                    with open("/proc/%s/comm" % (pid), "r") as pidFile:
                        programmeName = pidFile.readline()[:-1]
                except:# pylint: disable-msg=W0702
                    return 0

                if "packagekitd" == programmeName:
                    print "programmeName", programmeName, "packagekitd" == programmeName
                    self.__subprocess("sudo pkill packagekitd")
                    return 0
                msg = "%s (pid:%s) lock obslight zypper command" % (programmeName, pid)
                raise ObsLightErr.ObsLightChRootError(msg)
            return 0
        return 0

    def __subprocess(self, command=None, stdout=False, noOutPut=False):
        return self.__mySubprocessCrt.execSubprocess(command, stdout=stdout, noOutPut=noOutPut)

    def __listSubprocess(self, command=None):
        for c in command:
            res = self.__mySubprocessCrt.execSubprocess(c)
        return res

    def __getZypperCommand(self):
        command = "sudo zypper --cache-dir %s --root %s"
        command = command % ("/var/cache/zypp", self.__chroot.getDirectory())
        return command

    def addRepo(self, repos=None, alias=None):
        self.testZypperAvailable()
        command = []
        command.append("%s ar %s '%s'" % (self.__getZypperCommand(), repos, alias))
        command.append("%s --no-gpg-checks --gpg-auto-import-keys ref" % (self.__getZypperCommand()))
        return self.__listSubprocess(command=command)

    def deleteRepo(self, repoAlias):
        self.testZypperAvailable()
        command = []
        command.append("%s rr %s " % (self.__getZypperCommand(), repoAlias))
        command.append("%s --no-gpg-checks --gpg-auto-import-keys ref" % (self.__getZypperCommand()))
        self.__listSubprocess(command=command)

    def installBuildRequires(self, packageName, dicoPackageBuildRequires, arch):
        self.testZypperAvailable()
        if len(dicoPackageBuildRequires.keys()) == 0:
            return 0

        #command = []
#        command.append("%s --no-gpg-checks --gpg-auto-import-keys ref" % (self.__getZypperCommand()))
#        cmd = "%s --non-interactive in --force-resolution " % (self.__getZypperCommand())
#        cmd = ""
#        for pk in listPackageBuildRequires:
#            if pk.count("-") >= 2:
#                lastMinus = pk.rfind("-")
#                cutMinus = pk.rfind("-", 0, lastMinus)
#                # OBS sometimes returns "future" build numbers, and dependency
#                # resolution fails. So with forget build number.
#                name = pk[:cutMinus]
#
#                #pkCmd = '"' + name + ">=" + pk[cutMinus + 1:lastMinus] + '"'
#                pkCmd = name
#            else:
#                pkCmd = pk
#            cmd += " " + pkCmd

        aFile = tempfile.NamedTemporaryFile("w", delete=False)
        pickle.dump(dicoPackageBuildRequires, aFile)
        aFile.flush()
        aFile.close()

        #command.append(cmd )
        print "sudo obsMicInstall %s %s %s " % (self.__chroot.getDirectory() ,
                                                                   arch,
                                                                   aFile.name
                                                                   )
        res = self.__subprocess("sudo obsMicInstall %s %s %s " % (self.__chroot.getDirectory() ,
                                                                   arch,
                                                                   aFile.name
                                                                   ))
        #res = self.__listSubprocess(command=command)

        if res != 0:
            msg = "The installation of some dependencies of '%s' failed\n" % packageName
            msg += "Maybe a repository is missing."
            raise ObsLightErr.ObsLightChRootError(msg)

        return res


