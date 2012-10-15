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
Created on 30 sept. 2011

@author: ronan
'''
import os
import sys
import shutil

from ObsLightObject import ObsLightObject
from ObsLightUtils import getFilteredFileList
from ObsLightSpec import ObsLightSpec

import ObsLightOsc

import ObsLightGitManager

import ObsLightPrintManager
from ObsLightSubprocess import SubprocessCrt

import ObsLightErr
from ObsLightErr import ObsLightPackageErr

from copy import copy

from ObsLightUtils import getFilteredFileList, isASpecFile, levenshtein

from ObsLightPackageStatus import OBS_REV, OBS_STATUS, OSC_REV, OSC_STATUS, CHROOT_STATUS
from ObsLightPackageStatus import NOT_INSTALLED

from ObsLightPackageStatus import PackageInfo


from gbp.scripts.buildpackage_rpm import main as gbp_build
from gbp.rpm.git import GitRepositoryError, RpmGitRepository
import gbp.rpm as rpm
from gbp.errors import GbpError

class PrintHandler(object):
    """
    Wrapper for sys.stderr and sys.stdout that writes to a log file.
    """

    def __init__(self, stream):
        self.stream = stream


    def write(self, buf):
        self.stream(str(buf))

    def flush(self):
        pass

    def close(self):
        pass

    def isatty(self):
        return True

#        if self.__packageChrootDirectory is None:
#            self.__packageChrootDirectory = os.path.join(self.__chrootUserHome, self.__name)

class ObsLightPackage(ObsLightObject):

    ArchiveSuffix = ".tar.gz"

    def __init__(self,
                 project,
                 name=None,
                 packagePath=None,
                 packageGitPath=None,
                 fromSave={},
                 ):

        ObsLightObject.__init__(self)
        self.__project = project

        self.__mySubprocessCrt = SubprocessCrt()

        self.__mySpecFile = None

        # Package info.
        self.__packageInfo = PackageInfo(self, fromSave.get("packageInfo", {}))

        self.__name = fromSave.get("name", name)
        self.__readOnly = self.__project.isReadOnly()

        #The spec file name of the package
        self.__specFile = fromSave.get("specFile", None)

        #the path of the package source.
        self.__packageSourceDirectory = fromSave.get("packageSourceDirectory", packagePath)

        # Package git info.
        #packageGitPath can be a path or URL.
        self.__packageGitPath = fromSave.get("packageGitPath", packageGitPath)

        # Package patch tag.
        self.__firstCommitTag = fromSave.get("firstCommitTag", None)
        self.__secondCommitTag = fromSave.get("secondCommitTag", None)

        # OBS server  status, description, title.
        self.__description = fromSave.get("description", None)
        self.__packageTitle = fromSave.get("title", None)

        # Current patch info.
        self.__currentPatch = fromSave.get("currentPatch", None)
        self.__patchMode = fromSave.get("patchMode", True)

        # Build info.
        self.__prepDirName = fromSave.get("prepDirName", None)
        self.__listRPMPublished = fromSave.get("listRPMPublished", [])

        #Name of git directory used into chroot, to manage source for auto patch.
        self.__obslightGit = ".git_obslight"

        self.__rpmBuildDirectoryLink = "rpmbuild"
        self.__rpmBuildDirectory = "obslightbuild"
        self.__rpmBuildTmpDirectory = "obslightbuild_TMP"

        self.__packageChrootBuildDirectory = fromSave.get("packageChrootBuildDirectory", None)

        #the Chroot jail path with user home path.
        self.__chrootUserHome = self.__project.getChrootUserHome(fullPath=False)

        #the path of the package into the chroot.
        self.__packageChrootDirectory = fromSave.get("packageChrootDirectory", None)

        self.__chrootRpmBuildDirectory = os.path.join(self.__chrootUserHome,
                                                      self.__name,
                                                      self.__rpmBuildDirectory)

        self.__chrootRpmBuildTmpDirectory = os.path.join(self.__chrootUserHome,
                                                         self.__name ,
                                                         self.__rpmBuildTmpDirectory)

        if fromSave == {}:
            if self.isGitPackage and self.isLocalGit():
                if not os.path.isdir(os.path.join(self.getPackageSourceDirectory(), ".git")):
                    self.initAGitPackage()

            self.checkoutPackage()
        self.__mySpecFile = self.getSpecObj()

    def isLocalGit(self):
        return (self.getPackageGit() == self.getPackageSourceDirectory())

    def __subprocess(self, command=None, waitMess=False):
        return self.__mySubprocessCrt.execSubprocess(command=command,
                                                     waitMess=waitMess)
    #--------------------------------------------------------------------------- package management
    def getDic(self):
        '''
        return a description of the object in a dictionary.
        '''
        aDic = {}
        aDic["name"] = self.getName()

        aDic["specFile"] = self.getSpecFile()

        aDic["packageChrootDirectory"] = self.getPackageChrootDirectory()
        aDic["packageSourceDirectory"] = self.getPackageSourceDirectory()

        aDic["packageGitPath"] = self.__packageGitPath

        aDic["firstCommitTag"] = self.__firstCommitTag
        aDic["secondCommitTag"] = self.__secondCommitTag

        aDic["description"] = self.__description
        aDic["title"] = self.__packageTitle

        aDic["currentPatch"] = self.__currentPatch
        aDic["patchMode"] = self.__patchMode

        aDic["prepDirName"] = self.__prepDirName
        aDic["listRPMPublished"] = self.__listRPMPublished

        aDic["packageChrootBuildDirectory"] = self.getChrootBuildDirectory()

        aDic["packageInfo"] = self.__packageInfo.getDic()

        return aDic

    def initAGitPackage(self):
        cmd = "git init %s" % self.getPackageSourceDirectory()
        self.__subprocess(cmd)
        packageName = self.getName()
        packagingDir = os.path.join(self.getPackageSourceDirectory(), "packaging")
        os.makedirs(packagingDir)
        specPath = os.path.join(packagingDir, packageName + ".spec")
        with open(specPath, 'w') as f:
            f.write(specSkeleton % packageName)
        f.close()

    def getPackageParameter(self, parameter=None):
        '''
        Get the value of a project parameter:
        the valid parameter is :
            name
            
            specFile
            
            packageChrootDirectory
            packageSourceDirectory
            
            firstCommitTag
            
            description
            title
            
            currentPatch
            patchMode
            
            prepDirName
        '''

        if parameter == "name":
            return self.getName()

        elif parameter == "specFile":
            return self.getSpecFile()

        elif parameter == "packageChrootDirectory":
            return self.getPackageChrootDirectory()

        elif parameter == "packageChrootBuildDirectory":
            return self.getChrootBuildDirectory()

        elif parameter == "packageSourceDirectory":
            return self.getPackageSourceDirectory()

        elif  parameter == "firstCommitTag":
            return self.__firstCommitTag if self.__firstCommitTag != None else ""

        elif parameter == "description":
            return self.__description if self.__description != None else ""
        elif parameter == "title":
            return self.__packageTitle if self.__packageTitle != None else ""

        elif parameter == "currentPatch":
            return self.__currentPatch if self.__currentPatch != None else ""
        elif parameter == "patchMode":
            return self.__patchMode

        elif parameter == "prepDirName":
            return self.__prepDirName if self.__prepDirName != None else ""

        else:
            msg = "Parameter '%s' is not valid for getProjectParameter" % parameter
            raise ObsLightPackageErr(msg)

    def setPackageParameter(self, parameter=None, value=None):
        '''
        return the value  of the parameter of the package:
        the valid parameter is :
            specFile
            
            packageChrootDirectory
            
            description
            title
            
            currentPatch
            patchMode
            
            prepDirName
        '''

        if parameter == "specFile":
            self.setSpecFile(value)

        elif parameter == "packageChrootDirectory":
            self.__packageChrootDirectory = value

        elif parameter == "description":
            self.__description = value
        elif parameter == "title":
            self.__packageTitle = value

        elif parameter == "patchMode":
            self.__patchMode = value
        elif parameter == "currentPatch":
            self.__currentPatch = value

        elif parameter == "prepDirName":
            self.__prepDirName = value

        else:
            msg = "The parameter '%s' value is not valid for setPackageParameter" % parameter
            raise ObsLightPackageErr(msg)
        return 0

    def getName(self):
        '''
        return the name of the package.
        '''
        return self.__name

    def isReadOnly(self):
        return self.__readOnly

    def destroy(self):
        """
        When the package is delteted, the package source is remove.
        """
        sourcePath = self.getPackageSourceDirectory()
        if  sourcePath is not None:
            if os.path.isdir(sourcePath):
                return self.__subprocess("rm -fr " + sourcePath)
        return 0

    def getPackagingDirectiory(self):
        if self.isGitPackage:
            path = os.path.join(self.getPackageSourceDirectory(), "packaging")
            return path
        else:
            return self.getPackageSourceDirectory()

    def getPackagingFiles(self, returnFullPath=False):
        '''
        Return the packaging files list. 
        '''
        packagingPath = self.getPackagingDirectiory()
        if os.path.isdir(packagingPath):
            listFile = os.listdir(packagingPath)
            res = []
            for f in listFile:
                fileFullPath = os.path.join(packagingPath, f)
                if os.path.isfile(fileFullPath) and not f.startswith('.') and not f.endswith('~'):
                    if returnFullPath:
                        res.append(fileFullPath)
                    else:
                        res.append(f)
            return res
        else:
            return []

    def getPackageSourceDirectory(self):
        '''
        Return the absolute path of the source directory of the package.
        (base on the directory of the spec file).
        '''
        if self.__packageSourceDirectory is None:
            self.__packageSourceDirectory = self.__project.createPackagePath(self.getName(), self.isGitPackage)

        return self.__packageSourceDirectory

    def getPackageChrootDirectory(self):
        return self.__packageChrootDirectory
#        if self.__packageChrootDirectory != None:
#                return self.__packageChrootDirectory
#            else :
#                if self.__packageInfo.getChRootStatus() == PK_CONST.NOT_INSTALLED:
#                    return ""
#                else:
#                    return self.getChrootRpmBuildDirectory()


    #--------------------------------------------------------------------------- Check out/update file

    def checkoutPackage(self):
        if  self.isGitPackage :
            if not self.isLocalGit():
                self.__checkoutGitPackage()
        else:
            self.__checkoutOscPackage()

        self.findBestSpecFile()
        return 0

    def __checkoutOscPackage(self):
        ObsLightOsc.getObsLightOsc().checkoutPackage(obsServer=self.__project.getObsServer(),
                                                     projectObsName=self.__project.getProjectObsName(),
                                                     package=self.getName(),
                                                     directory=self.__project.getDirectory())
    def __checkoutGitPackage(self):
        sourcePath = self.getPackageSourceDirectory()

        url = self.getPackageGit()
        if url is None:
            msg = "Neither local path nor URL specified to import package from!"
            raise ObsLightErr.ObsLightPackageErr(msg)

        if os.path.isdir(sourcePath):
            if len(os.listdir(sourcePath)) > 0:
                msg = "Cannot do git clone in '%s': directory is not empty." % sourcePath
                raise ObsLightErr.ObsLightPackageErr(msg)

        ObsLightGitManager.cloneGitpackage(url, sourcePath)

        if not os.path.isdir(os.path.join(sourcePath, ".git")):
            mess = "'%s' is not a git directory" % sourcePath
            raise ObsLightErr.ObsLightPackageErr(mess)

        return 0

    def updatePackage(self):
        if  self.isGitPackage:
            self.__updateGitPackage()
        else:
            self.__updateOscPackage()

        self.findBestSpecFile()
        return 0

    def __updateGitPackage(self):
        sourcePath = self.getPackageSourceDirectory()
        return ObsLightGitManager.updateGitpackage(sourcePath)

    def __updateOscPackage(self):
        sourcePath = self.getPackageSourceDirectory()
        ObsLightOsc.getObsLightOsc().updatePackage(sourcePath)
        return 0

    #--------------------------------------------------------------------------- spec file

#    def __initConfigureFile(self):
#        '''
#        Init the  spec.
#        '''
#        try:
#            if not self.__specFile in (None, 'None', ""):
#                self.__initSpecFile()
#            else:
#                self.__mySpecFile = None
#        except BaseException:
#            ObsLightPrintManager.getLogger().error(u"Error reading SPEC file", exc_info=1)
#
#    def __initSpecFile(self):
#        if os.path.isfile(self.__packagePath + "/" + self.__specFile):
#            self.__mySpecFile = ObsLightSpec(packagePath=self.__packagePath,
#                                             aFile=self.__specFile)

    def findBestSpecFile(self):
        """Find the name of the spec file which matches best with `packageName`"""
        specFileList = self.__getSpecFileList(self.getPackagingFiles())
        packageName = self.getName()

        specFile = None
        if len(specFileList) < 1:
            # No spec file in list
            specFile = None
        elif len(specFileList) == 1:
            # Only one spec file
            specFile = specFileList[0]
        else:
            sameStart = []
            for spec in specFileList:
                if str(spec[:-5]) == str(packageName):
                    # This spec file has the same name as the package
                    specFile = spec
                    break
                elif spec.startswith(packageName):
                    # This spec file has a name which looks like the package
                    sameStart.append(spec)

            if specFile is None:
                if len(sameStart) > 0:
                    # Sort the list of 'same start' by the Levenshtein distance
                    sameStart.sort(key=lambda x: levenshtein(x, packageName))
                    specFile = sameStart[0]
                else:
                    # No spec file starts with the name of the package,
                    # sort the whole spec file list by the Levenshtein distance
                    specFileList.sort(key=lambda x: levenshtein(x, packageName))
                    specFile = specFileList[0]

        if specFile is None:
            msg = "Found no spec file matching package name '%s'" % packageName
        else:
            msg = "Spec file chosen for package '%s': '%s'" % (packageName, specFile)
        self.logger.info(msg)

        self.setSpecFile(specFile)
        return 0

    @staticmethod
    def __getSpecFileList(fileList):
        """Returns a new list from `fileList` with only spec files"""
        specFileList = []
        for f in fileList:
            if isASpecFile(f):
                specFileList.append(f)
        return specFileList


    def save(self):
        '''
        Save the Spec file.
        '''
        if self.__mySpecFile != None:
            self.__mySpecFile.save()
        else:
            raise ObsLightPackageErr("No Spec in the package")

    def saveTmpSpec(self, path, archive):
        '''
        Save the Spec file.
        '''
        if self.__mySpecFile != None:
            self.__mySpecFile.saveTmpSpec(path=path,
                                          excludePatch=self.__currentPatch,
                                          archive=archive)
#            self.initPackageFileInfo()
        else:
            raise ObsLightPackageErr("No Spec in the package")

    def saveSpecShortCut(self, path, section):
        '''
        Save the Spec file.
        '''
        if self.__mySpecFile != None:
            self.__mySpecFile.saveSpecShortCut(path,
                                               section,
                                               self.__packageInfo.getChRootStatus(),
                                               self.getPackageChrootDirectory(),
                                               )
        else:
            raise ObsLightPackageErr("No Spec in the package")

    def saveSpec(self, path):
        '''
        Save the Spec file.
        '''
        if self.__mySpecFile != None:
            self.__mySpecFile.save(path=path)
        else:
            raise ObsLightPackageErr("No Spec in the package")

    def addFileToSpec(self, baseFile=None, aFile=None):
        '''
        Add a delete command of a aFile to the spec aFile.
        '''

        if self.__mySpecFile != None:
            res = self.__mySpecFile.addFile(baseFile=baseFile, aFile=aFile)
#            self.initPackageFileInfo()
            self.save()
            return res
        else:
            raise ObsLightPackageErr("No Spec in the package")

    def delFileToSpec(self, aFile=None):
        '''
        Add a delete command of a aFile to the spec aFile.
        '''
        if self.__mySpecFile != None:
            res = self.__mySpecFile.delFile(aFile=aFile)
#            self.initPackageFileInfo()
            self.save()
            return res
        else:
            raise ObsLightPackageErr("No Spec in the package")

    def __isASpecfile(self, afile):
        return afile.endswith(".spec")

    def getSpecFile(self, fullPath=False):
        '''
        return the  spec file.
        '''
        if self.__specFile is not None:
            if fullPath:
                return os.path.join(self.getPackagingDirectiory(), self.__specFile)
            else:
                return self.__specFile
        else:
            return None

    def getSpecObj(self):
        if self.__mySpecFile is not None:
            return self.__mySpecFile
        else:
            if not self.__specFile in (None, 'None', ""):
                if os.path.isfile(self.getSpecFile(True)):
                    self.__mySpecFile = ObsLightSpec(packagePath=self.getPackagingDirectiory(),
                                                     aFile=self.getSpecFile())
                else:
                    self.__mySpecFile = None
                return self.__mySpecFile
            else:
                return None

    def setSpecFile(self, newSpecFile):
        '''
        return the  spec file.
        '''
        oldSpecFile = self.__specFile
        self.__specFile = newSpecFile

        if oldSpecFile != newSpecFile:
            self.__mySpecFile = self.getSpecObj()

    def specFileHaveAnEmptyBuild(self):
        mySpecFile = self.getSpecObj()

        if mySpecFile is None:
            return None

        return mySpecFile.specFileHaveAnEmptyBuild()

    def getMacroDirectoryPackageName(self):
        '''
        Return the Name used for the BUILD directory, by setup in %prep section
        '''
        mySpecFile = self.getSpecObj()

        if mySpecFile is None:
            return None

        name = mySpecFile.getMacroDirectoryPackageName()

        if name != None:
            name = mySpecFile.getResolveMacroName(name)
            return name
        else:
            return None

    def getMacroPackageName(self):
        '''
        return the %{name} of the Pkg
        '''
        mySpecFile = self.getSpecObj()

        if mySpecFile is None:
            return None

        return mySpecFile.getResolveMacroName("%{name}")

    #--------------------------------------------------------------------------- osc Management


    #--------------------------------------------------------------------------- git Management
    @property
    def isGitPackage(self):
        return (self.getPackageGit() is not None)

    def setPackageGit(self, path):
        self.__packageGitPath = path

    def getPackageGit(self):
        return self.__packageGitPath

    #--------------------------------------------------------------------------- chroot Management
    def exportIntoChroot(self, chrootPath):
        """
        Export package source into chroot.
        """
        def _createAbsPath(path):
            if len(path) > 0 and path.startswith("/"):
                path = path[1:]
            return os.path.join(chrootPath , path)

        def create_gbp_export_args(repo, commit, export_dir, tmp_dir, spec):
            """
            Construct the cmdline argument list for git-buildpackage export
            """
            upstream_branch = "upstream"
            upstream_tag = 'upstream/%(upstreamversion)s'

            # Now, start constructing the argument list
            args = ["argv[0] placeholder", "--git-export-only",
                    "--git-ignore-new", "--git-builder=osc",
                    "--git-upstream-branch=upstream",
                    "--git-export-dir=%s" % export_dir,
                    "--git-tmp-dir=%s" % tmp_dir,
                    "--git-packaging-dir=packaging",
                    "--git-spec-file=%s" % spec,
                    "--git-export=%s" % commit,
                    "--git-upstream-branch=%s" % upstream_branch,
                    "--git-upstream-tag=%s" % upstream_tag]


            args.extend(["--git-no-patch-export",
                         "--git-upstream-tree=%s" % commit])

            return args

        chrootRpmBuildDirectory = self.getChrootRpmBuildDirectory()
        absChrootRpmBuildDirectory = "%s%s/SOURCES/" % (self.__project.getChRootPath(), chrootRpmBuildDirectory)

        for aFile in self.getPackagingFiles():
            pathDst = absChrootRpmBuildDirectory + str(aFile)
            if os.path.isfile(pathDst):
                os.unlink(pathDst)
            pathSrc = os.path.join(self.getPackagingDirectiory() , str(aFile))
            shutil.copy2(pathSrc, pathDst)

        if self.isGitPackage:
            listFile = os.listdir(self.getPackageSourceDirectory())

            if ".git" in listFile:
                listFile.remove(".git")

            if len(listFile) > 1:
                curentDirOld = os.getcwd()
                sourcePath = self.getPackageSourceDirectory()
                repo = RpmGitRepository(sourcePath)
                os.chdir(sourcePath)
                commit = 'HEAD'
                export_dir = absChrootRpmBuildDirectory
                tmp_dir = "/tmp"
#                spec = rpm.parse_spec(self.getSpecFile(fullPath=True))
                spec = self.getSpecFile(fullPath=True)
#                comp_type = guess_comp_type(spec)
                gbp_args = create_gbp_export_args(repo,
                                                  commit,
                                                  export_dir,
                                                  tmp_dir,
                                                  spec)

#                git_archive(repo,
#                            spec,
#                            destDir,
#                            'HEAD',
#                            comp_type,
#                            comp_level=9,
#                            with_submodules=True)
                old_stderr = sys.stderr
                old_stdout = sys.stdout
                try:
                    sys.stdout = PrintHandler(ObsLightPrintManager.getLogger().info)
                    sys.stderr = PrintHandler(ObsLightPrintManager.getLogger().error)
                    ret = gbp_build(gbp_args)


                finally:
                    sys.stderr = old_stderr
                    sys.stdout = old_stdout
                    os.chdir(curentDirOld)

        self.__packageChrootDirectory = os.path.join(self.__chrootUserHome, self.__name)
        return 0

    def delFromChroot(self):
        self.__packageChrootDirectory = None
        self.__packageInfo.delFromChroot()

    def isInstallInChroot(self):
        '''
        Return True if the package is install into the chroot.
        '''
        if self.__packageInfo.getChRootStatus() == NOT_INSTALLED:
            return False
        else:
            return True


    #--------------------------------------------------------------------------- chroot build Management
    def getRPMPublished(self):
        return self.__listRPMPublished

    def setRPMPublished(self, listRPMPublished):
        self.__listRPMPublished = listRPMPublished

    def getCurrentGitDirectory(self):
        return os.path.join(self.getChrootRpmBuildDirectory(), "BUILD", self.__obslightGit)

    def isCurrentGitIsPackageGit(self):
        return self.__currentGitIsPackageGit

    def getChrootRpmBuildDirectory(self):
        return self.__chrootRpmBuildDirectory

    def getChrootRpmBuildTmpDirectory(self):
        return self.__chrootRpmBuildTmpDirectory

    def getTopDirRpmBuildDirectory(self):
        return  self.__rpmBuildDirectory

    def getTopDirRpmBuildLinkDirectory(self):
        return self.__rpmBuildDirectoryLink

    def getTopDirRpmBuildTmpDirectory(self):
        return self.__rpmBuildTmpDirectory

    def setChrootBuildDirectory(self, path):
        '''
        Set the directory of the package build directory into the chroot.
        '''
        self.__packageChrootBuildDirectory = path

    def getChrootBuildDirectory(self):
        '''
        Return the directory of the package build directory into the chroot.
        '''
        return self.__packageChrootBuildDirectory

    #--------------------------------------------------------------------------- Patch Management
    def addPatch(self, aFile=None):
        '''
        add a Patch aFile to package, the patch is automatically add to the spec aFile.
        '''
        self.__currentPatch = aFile
        if self.__mySpecFile != None:
            if self.__mySpecFile.addpatch(aFile) == 1:
                msg = "WARNING: Patch already exist the spec file will not be changed."
                ObsLightPrintManager.obsLightPrint(msg)
            else:
                self.save()
        else:
            msg = "No Spec in the package"
            raise ObsLightPackageErr(msg)

#        self.__addFile(aFile)
        if self.isGitPackage:
            pass
        else:
            ObsLightOsc.getObsLightOsc().add(path=self.getPackageSourceDirectory(), afile=self.__currentPatch)

    def initCurrentPatch(self):
        self.__currentPatch = None

    def patchIsInit(self):
        return self.__currentPatch != None

    def getCurrentPatch(self):
        return self.__currentPatch

    def setFirstCommit(self, tag):
        self.__firstCommitTag = tag

    def getFirstCommit(self):
        return self.__firstCommitTag

    def setSecondCommit(self, tag):
        self.__secondCommitTag = tag

    def getSecondCommit(self):
        return self.__secondCommitTag

    def setPrepDirName(self, prepDirName):
        self.__prepDirName = prepDirName

    def getPrepDirName(self):
        return self.__prepDirName

    def getArchiveName(self):
        """
        Get the name of the temporary archive we create from
        sources extracted from git.
        """
        if self.__prepDirName is None:
            return self.__name + self.ArchiveSuffix
        else:
            return self.__prepDirName + self.ArchiveSuffix

    #--------------------------------------------------------------------------- File management (old)
#    def addFile(self, path):
#        '''
#        Add a aFile to the package.
#        '''
#        if not os.path.exists(path):
#            raise ObsLightPackageErr("'" + path + "' is not a file, can't add to package")
#
#        name = os.path.basename(path)
#        shutil.copy2(path, os.path.join(self.getPackagingDirectiory(), name))
##        self.__addFile(name)
#
#        if self.__isGitPackage:
#            pass
#        else:
#            ObsLightOsc.getObsLightOsc().add(path=self.getPackagingDirectiory(), afile=name)
#
#
#        if self.__isASpecfile(name):
#            self.findBestSpecFile()
#
##        self.initPackageFileInfo()
#        return 0

#    def delFile(self, name):
#        path = os.path.join(self.getPackageSourceDirectory(), name)
##        resInfo = self.getPackageFileInfo(name)
#        if not resInfo['Status'].startswith("!"):
#            if not os.path.exists(path):
#                raise ObsLightPackageErr("'" + path + "' not in package directory.")
#            os.remove(path)
#
##            if name in self.__fileList:
##                self.__fileList.remove(name)
#
##            if not resInfo['Status'].startswith("?"):
##                self.__filesToDeleteList.append(name)
##                ObsLightOsc.getObsLightOsc().remove(path=self.getPackageSourceDirectory(), afile=name)
#        else:
#            if name in self.__filesToDeleteList:
#                self.__filesToDeleteList.remove(name)
##        self.initPackageFileInfo()
#        return 0

#    def getPackageFileInfo(self, fileName):
#        if self.__listInfoFile is None:
#            try:
#                res = ObsLightOsc.getObsLightOsc().getPackageFileInfo(workingdir=self.__packagePath)
#            # FVE: temporary hack to get file list in UI
#            except ObsLightOsc.oscerr.NoWorkingCopy:
#                res = []
#                for f in getFilteredFileList(self.__packagePath):
#                    res.append((' ', f))
#            if res != None:
#                self.__listInfoFile = {}
#                for status, aFile in res:
#                    self.__listInfoFile[aFile] = status
#        if fileName in self.__listInfoFile.keys():
#            res = self.__listInfoFile[fileName]
#            if res == "A":
#                res += " (Added)"
#            elif res == "D":
#                res += " (Deleted)"
#            elif res == "M":
#                res += " (Modified)"
#            elif res == "!":
#                res += " (item is missing, removed by non-osc command)"
#            elif res == "?":
#                res += " (item is not under version control)"
#            elif res == "C":
#                res += " (Conflicted)"
#
#            return {u'Status': res}
#        else:
#            return {u'Status': u"! (item is missing, removed by non-osc command)"}

#    def initPackageFileInfo(self):
#        res = ObsLightOsc.getObsLightOsc().getPackageFileInfo(workingdir=self.__packagePath)
#        if res != None:
#            self.__listInfoFile = {}
#            for status, aFile in res:
#                self.__listInfoFile[aFile] = status
#        return 0

    def testConflict(self, aFile=None):
        return False
#        if aFile != None:
#            if self.getPackageFileInfo(aFile)[u'Status'].startswith("C"):
#                return True
#            return False
#        else:
#            for aFile in self.getListFile():
#                if self.getPackageFileInfo(aFile)[u'Status'].startswith("C"):
#                    return True
#            return False

    #--------------------------------------------------------------------------- Package Info

    def getPackageInfo(self, info):
        return self.__packageInfo.getPackageInfo(info)


    def isExclude(self):
        return self.__packageInfo.isExclude()

    def setChRootStatus(self, status):
        return self.__packageInfo.setChRootStatus(status)

    def haveBuildDirectory(self):
        return self.__packageInfo.haveBuildDirectory()

    def isPackaged(self):
        return self.__packageInfo.isPackaged()
    #---------------------------------------------------------------------------
    @property
    def existsOnServer(self):
        # TODO: check that it really exists on server
        return self.__existsOnServer

#    def getPackageFileList(self):
#        res = []
#        res.extend(self.__fileList)
#        res.extend(self.__filesToDeleteList)
#        return res

    def getPackagePath(self):
        return self.__packagePath

    def repairPackageDirectory(self):
        path = self.getPackageSourceDirectory()
        ObsLightOsc.getObsLightOsc().repairOscPackageDirectory(path=path)
        return self.updatePackage(name=package)


    def __createPackageArchiveFromGit(self,
                                      gitTreePath,
                                      packagePath,
                                      packageName,
                                      packageVersion=None):
        """
        Create the archive of package `packageName`, in directory `packagePath`,
        from the git tree at `gitTreePath`.
        `packageName` should be the name of the package as written in spec file.
        Optional `packageVersion` should be the version of the package as written in spec file.
        """
        if packageVersion is None:
            archiveName = packageName + ".tar"
            packageTopDir = packageName
        else:
            versionSuffix = "-%s" % packageVersion
            archiveName = packageName + versionSuffix + ".tar"
            packageTopDir = packageName + versionSuffix
        archivePath = os.path.join(packagePath, archiveName)
        cmd = 'git --git-dir="%s/.git" archive --prefix %s/ -o "%s" HEAD' % (gitTreePath,
                                                                             packageTopDir,
                                                                             archivePath)
        res = self.__mySubprocessCrt.execSubprocess(cmd)
        errorMsg = "Failed to create archive of packageName '%s'" % packageName
        if res != 0:
            raise ObsLightErr.ObsLightProjectsError(errorMsg)
        cmd = 'gzip -f %s' % archivePath
        res = self.__mySubprocessCrt.execSubprocess(cmd)
        if res != 0:
            raise ObsLightErr.ObsLightProjectsError(errorMsg)


    # TODO: delete this function
#    def getListFile(self):
#        return self.getFileList()

#    def getFileList(self):
#        return self.__fileList


#    def getDirectoryPackageName(self):
#        '''
#        
#        '''
#        if self.__mySpecFile != None:
#            res = self.__mySpecFile.getDirectoryPackageName()
#            if res != None:
#                return None
#            else:
#                raise ObsLightPackageErr("Error " + self.__name + " Have no spec File.")
#        else:
#            raise ObsLightPackageErr("Error " + self.__name + " Have no spec File.")
#        return None

#    def __addFile(self, afile):
#        self.__fileList.append(afile)

    def autoResolvedConflict(self):
#        if not self.isGitPackage:
#            for aFile in self.__fileList:
#                if self.testConflict(aFile=aFile):
#                    ObsLightOsc.getObsLightOsc().autoResolvedConflict(packagePath=self.getPackageSourceDirectory(),
#                                                                      aFile=aFile)
        return 0
#        return self.initPackageFileInfo()

    def addRemoveFileToTheProject(self):
        '''
        add new file and remove file to the project.
        '''
        if not self.isGitPackage:
            ObsLightOsc.getObsLightOsc().addremove(path=self.getPackageSourceDirectory())
#        self.initPackageFileInfo()

    def commitPackageChange(self, message=None):
        '''
        commit the package to the OBS server.
        '''
        if not self.isGitPackage:
            if self.__packageInfo.isReadyToCommit():
                message = "Can't Commit \"%s\"\n"
                message += "because local osc rev \"%s\" and OBS rev \"%s\" do not match.\n"
                message += "Please update the package."
                message = message % (package, oscRev, obsRev)

                raise ObsLightErr.ObsLightProjectsError(message)

        self.autoResolvedConflict()
        if not self.isGitPackage:
            ObsLightOsc.getObsLightOsc().commitProject(path=self.getPackageSourceDirectory(), message=message)
        else:
            sourcePath = self.getPackageSourceDirectory()
            return ObsLightGitManager.commitGitpackage(sourcePath, message)
#        self.__filesToDeleteList = []
#        self.initPackageFileInfo()


specSkeleton = '''#
# spec file for package 
#
# Copyright (c) 2010 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

# norootforbuild


Name:           %s
Version:
Release:
License:
Summary:
Url:
Group:
Source:
Patch:
BuildRequires:
PreReq:
Provides:
BuildRoot:      %%{_tmppath}/%%{name}-%%{version}-build

%%description

%%prep
%%setup -q

%%build
%%configure
make %%{?_smp_mflags}

%%install
%%make_install

%%clean
%%{?buildroot:%%__rm -rf "%%{buildroot}"}

%%post

%%postun

%%files
%%defattr(-,root,root)
%%doc ChangeLog README COPYING

%%changelog
'''
