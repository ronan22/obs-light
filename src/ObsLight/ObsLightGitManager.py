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
@author: Florent Vennetier
'''

import os
import time
import ObsLightErr
from ObsLightObject import ObsLightObject
from ObsLightSubprocess import SubprocessCrt

class ObsLightGitManager(ObsLightObject):
    '''
    Manage the internal Git repository used to generate patches on packages.
    '''

    def __init__(self, projectChroot):
        ObsLightObject.__init__(self)
        self.__chroot = projectChroot
        self.__mySubprocessCrt = SubprocessCrt()
        self.initialTag = "initial-prep"

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

    def makeArchiveGitSubcommand(self, prefix, revision=u"HEAD", outputFilePath=None):
        """
        Construct a Git 'archive' subcommand with auto-detected format.
        If outputFilePath is None, format will be tar, and output will
        be stdout.
        """
        command = "archive --prefix=%s/ %s "
        command = command % (prefix, revision)
        if outputFilePath is not None:
            command += " -o %s" % outputFilePath
        return command

    def execMakeArchiveGitSubcommand(self,
                                    packagePath,
                                    outputFilePath,
                                    prefix,
                                    packageCurrentGitDirectory):
        absOutputFilePath = self.__chroot.getDirectory()
        # TODO: make something more generic (gz, bz2, xz...)
        if outputFilePath.endswith(".tar.gz"):
            # git archive does not know .tar.gz,
            # we have to compress the file afterwards
            absOutputFilePath += outputFilePath[:-len('.gz')]
        else:
            absOutputFilePath += outputFilePath
        archiveSubCommand = self.makeArchiveGitSubcommand(prefix,
                                                          outputFilePath=absOutputFilePath)
        command = self.prepareGitCommand(packagePath,
                                         archiveSubCommand,
                                         packageCurrentGitDirectory)
        res = self.__subprocess(command)
        if res != 0:
            return res
        if outputFilePath.endswith(".tar.gz"):
            # Without '-f' user will be prompted if .gz file already exists
            command = "gzip -f %s" % absOutputFilePath
            res = self.__subprocess(command)
        return res

    def findEmptyDirectory(self, package):
        # git ignores empty directories so we must save them into a file.
        projectPath = self.__chroot.getDirectory() + package.getPackageDirectory()
        res = []
        for root, dirs, files in os.walk(projectPath):
            if len(dirs) == 0 and len(files) == 0:
                res.append(root.replace(projectPath + "/", ""))

        # TODO: move this file to BUILD/
        with open(projectPath + "/.emptyDirectory", 'w') as f:
            for d in res:
                f.write(d + "\n")

    def initGitWatch(self, path, package):
        '''
        Initialize a Git repository in the specified path, and 'git add' everything.
        '''
        if path is None:
            raise ObsLightErr.ObsLightChRootError("Path is not defined in initGitWatch.")

        absPath = self.__chroot.getDirectory() + path

        pkgCurGitDir = package.getCurrentGitDirectory()
        # Ensure we have access rights on the directory
        res = self.__chroot.allowAccessToObslightGroup(os.path.dirname(pkgCurGitDir),
                                                       absolutePath=False)

        self.findEmptyDirectory(package)

        timeString = time.strftime("%Y-%m-%d_%Hh%Mm%Ss")
        comment = '\"auto commit first commit %s\"' % timeString

        # Create .gitignore file.
        self.initGitignore(path, package)

        if res != 0:
            msg = "Failed to give access rights on '%s'. Git repository creation may fail."
            self.logger.warn(msg % os.path.dirname(pkgCurGitDir))
        command = []
        command.append(self.prepareGitCommand(path, "init ", pkgCurGitDir))
        command.append(self.prepareGitCommand(path, "add " + absPath + "/\*", pkgCurGitDir))
        command.append(self.prepareGitCommand(path, "commit -a -m %s" % comment, pkgCurGitDir))
        command.append(self.prepareGitCommand(path, "tag %s" % self.initialTag , pkgCurGitDir))

        res = self.__listSubprocess(command=command)
        if res != 0:
            msg = "Creation of the git repository for %s failed. See the log for more information."
            raise ObsLightErr.ObsLightChRootError(msg % package.getName())

    def resetToPrep(self, path, package):
        pkgCurGitDir = package.getCurrentGitDirectory()
        res = self.__listSubprocess([self.prepareGitCommand(path, "checkout  %s" % self.initialTag , pkgCurGitDir)])
        return res

    def initGitignore(self, path, package):
        absPath = self.__chroot.getDirectory() + path
        f = open(absPath + "/.gitignore", 'a')

        f.write("debugfiles.list\n")
        f.write("debuglinks.list\n")
        f.write("debugsources.list\n")
        f.write(".gitignore\n")
        f.write(".emptyDirectory\n")
#            f.write("*.in\n")

        f.close()

    def ignoreGitWatch(self,
                       package,
                       path=None,
                       commitComment="first build commit"):
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
        self.__subprocess("sudo chmod -f a+w %s %s/.gitignore" % (absPath, absPath))

        f = open(absPath + "/.gitignore", 'a')

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
        if packagePath is None:
            raise ObsLightErr.ObsLightChRootError("path is not defined in commitGit for .")

        timeString = time.strftime("%Y-%m-%d_%Hh%Mm%Ss")
        comment = '\"auto commit %s %s\"' % (mess, timeString)

        path = self.__chroot.getDirectory() + packagePath
        command.append(self.prepareGitCommand(packagePath,
                                              " add %s/\* " % (path),
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
