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
Created on 23 May 2012

@author: Ronan Le Martret
'''

import os
import time
import ObsLightErr
from ObsLightSubprocess import SubprocessCrt

class ObsLightGitManager(object):
    '''
    class Git management
    '''

    def __init__(self, projectChroot):

        '''
        Constructor
        '''
        self.__chroot = projectChroot
        self.__mySubprocessCrt = SubprocessCrt()

    def __subprocess(self, command=None, stdout=False, noOutPut=False):

        return self.__mySubprocessCrt.execSubprocess(command, stdout=stdout, noOutPut=noOutPut)

    def __listSubprocess(self, command=None):
        for c in command:
            res = self.__mySubprocessCrt.execSubprocess(c)
        return res

    def ___execPipeSubprocess(self, command, command2):
        return self.__mySubprocessCrt.execPipeSubprocess(command, command2)

    def prepareGitCommand(self, workTree, subcommand, gitDir):
        """
        Construct a Git command-line, setting its working tree to `workTree`,
        and git directory to `gitDir`, and then appends `subcommand`.
        Output example:
          git --git-dir=<gitDir> --work-tree=<workTree> <subcommand>
        """
        absWorkTree = self.__chroot.getDirectory() + workTree
        absGitDir = self.__chroot.getDirectory() + gitDir
        command = "git --git-dir=%s --work-tree=%s " % (absGitDir, absWorkTree)
        command += subcommand
        return command

    def makeArchiveGitSubcommand(self, prefix, revision=u"HEAD"):
        """
        Construct a Git 'archive' subcommand with tar format,
        piped on gzip to produce a .tar.gz file.
        """
        command = "archive --format=zip --prefix=%s/ %s "
        command = command % (prefix, revision)
        return command

    def execMakeArchiveGitSubcommand(self,
                                    packagePath,
                                    outputFilePath,
                                    prefix,
                                    packageCurrentGitDirectory):

        command = self.prepareGitCommand(packagePath,
                                         self.makeArchiveGitSubcommand(prefix),
                                         packageCurrentGitDirectory)

        res = self.__subprocess(command, stdout=True, noOutPut=True)
        f = open(self.__chroot.getDirectory() + outputFilePath, 'w')
        f.write(res)
        f.close()

        return 0

    def initGitWatch(self, path, package):
        '''
        Initialize a Git repository in the specified path, and 'git add' everything.
        '''
        if path == None:
            raise ObsLightErr.ObsLightChRootError("Path is not defined in initGitWatch.")

        absPath = self.__chroot.getDirectory() + path

        #git ignore the empty directory so we must save them into a file.
        projectPath = self.__chroot.getDirectory() + package.getPackageDirectory()
        res = []
        for root, dirs, files in os.walk(projectPath):
            if len(dirs) == 0 and len(files) == 0:
                res.append(root.replace(projectPath + "/", ""))

        f = open(projectPath + "/.emptyDirectory", 'w')

        for d in res:
            f.write(d + "\n")
        f.close()

        timeString = time.strftime("%Y-%m-%d_%Hh%Mm%Ss")
        comment = '\"auto commit first commit %s\"' % timeString

        pkgCurGitDir = package.getCurrentGitDirectory()
        command = []
        command.append(self.prepareGitCommand(path, "init ", pkgCurGitDir))
        command.append(self.prepareGitCommand(path, "add " + absPath + "/\*", pkgCurGitDir))
        command.append(self.prepareGitCommand(path, "commit -a -m %s" % comment, pkgCurGitDir))

        res = self.__listSubprocess(command=command)

    def ignoreGitWatch(self, package, path=None, commitComment="first build commit", firstBuildCommit=True):
        '''
        Add all Git untracked files of `path` to .gitignore
        and commit.
        '''

        if path is None:
            raise ObsLightErr.ObsLightChRootError("path is not defined in initGitWatch.")

        absPath = self.__chroot.getDirectory() + path

        timeString = time.strftime("%Y-%m-%d_%Hh%Mm%Ss")
        comment = '\"auto commit %s %s\"' % (commitComment, timeString)

        command = self.prepareGitCommand(path, u"status -u -s ", package.getCurrentGitDirectory())
        #| sed -e 's/^[ \t]*//' " + u"| cut -d' ' -f2 >> %s/.gitignore" % absPath, package.getCurrentGitDirectory()

        res = self.__subprocess(command=command, stdout=True)
        # some packages modify their file rights, so we have to ensure
        # this file is writable
        self.__subprocess("sudo chmod a+w %s/.gitignore" % absPath)

        f = open(absPath + "/.gitignore", 'a')
        if firstBuildCommit:
            f.write("debugfiles.list\n")
            f.write("debuglinks.list\n")
            f.write("debugsources.list\n")
            f.write("*.in\n")

            self.__subprocess(self.prepareGitCommand(path,
                                                     u"add " + absPath + "/.gitignore",
                                                     package.getCurrentGitDirectory()))

        if type(res) is not type(int()):
            for line in res.split("\n"):
                if len(line) > 0:
                    line = " ".join(line.strip(" ").split(" ")[1:])
                    f.write(line + "\n")
        f.close()

        return self.__subprocess(self.prepareGitCommand(path,
                                 u"commit -a -m %s" % comment,
                                 package.getCurrentGitDirectory()))

    def getCommitTag(self, path, package):
        '''
        Get the last Git commit hash.
        '''

#        resultFile = "commitTag.log"
        command = self.prepareGitCommand(path,
                                         " log HEAD --pretty=short -n 1 " ,
                                        package.getCurrentGitDirectory())

#        resPath = self.__chroot.getChrootDirTransfert() + "/" + resultFile
        result = self.__subprocess(command=command, stdout=True)

        for line in result.split("\n"):
            if line.startswith("commit "):
                res = line.strip("commit").strip().rstrip("\n")
                return res

    def getListCommitTag(self, path, package):
        '''
        Get the last Git commit hash.
        '''
#        resultFile = self.__chroot.getChrootDirTransfert() + "/" + "commitTag.log"
        command = self.prepareGitCommand(path,
                                         " log HEAD --pretty=short -n 20 ",
                                         package.getCurrentGitDirectory())

        result_tmp = self.__subprocess(command=command, stdout=True)
        result = []
        for line in result_tmp.split("\n"):
            if line.startswith("commit "):
                res = line.strip("commit ").rstrip("\n")
                result.append((res, "Comment"))
        return result

    def commitGit(self, mess, package):
        packagePath = package.getPackageDirectory()
        command = []
        if packagePath == None:
            raise ObsLightErr.ObsLightChRootError("path is not defined in commitGit for .")

        timeString = time.strftime("%Y-%m-%d_%Hh%Mm%Ss")
        comment = '\"auto commit %s %s\"' % (mess, timeString)

        command.append(self.prepareGitCommand(packagePath,
                                              " add %s/\* " % (self.__chroot.getDirectory() + packagePath),
                                              package.getCurrentGitDirectory()))
        command.append(self.prepareGitCommand(packagePath,
                                              " commit -a -m %s" % comment,
                                              package.getCurrentGitDirectory()))
        self.__listSubprocess(command=command)

        tag2 = self.getCommitTag(packagePath, package)
        package.setSecondCommit(tag2)

    def createPatch(self, package, packagePath, tag1, tag2, patch):
        command = self.prepareGitCommand(packagePath,
                                         "diff -p -a --binary %s %s " % (tag1, tag2),
                                         package.getCurrentGitDirectory())
        res = self.__subprocess(command=command, stdout=True)

        pathOscPackage = package.getOscDirectory()

        f = open(pathOscPackage + "/" + patch, "w'")
        f.write(res)
        f.close()
        return 0





