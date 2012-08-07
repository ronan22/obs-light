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
import shutil

from ObsLightSpec import ObsLightSpec

import ObsLightOsc

import ObsLightPrintManager
from ObsLightSubprocess import SubprocessCrt

from ObsLightErr import ObsLightPackageErr

from copy import copy

import ObsLightPackages as PK_CONST

class ObsLightPackage(object):
    '''
    classdocs
    '''
    ArchiveSuffix = ".tar.gz"

    def __init__(self,
                 packagePath,
                 chrootUserHome,
                 name=None,
                 specFile=None,
                 listFile=None,
                 listInfoFile=None,
                 status="Unknown",
                 obsRev="-1",
                 oscStatus="Unknown",
                 oscRev="-1",
                 chRootStatus=PK_CONST.NOT_INSTALLED,
                 description="",
                 packageTitle="",
                 fromSave=None):
        '''
        Constructor
        '''
        listFile = listFile or []
        self.__packagePath = packagePath
        self.__mySubprocessCrt = SubprocessCrt()
        self.__specFile = None
        self.__mySpecFile = None
        self.__firstCommitTag = None
        self.__secondCommitTag = None
        self.__currentPatch = None
        self.__listInfoFile = listInfoFile
        self.__description = description
        self.__packageTitle = packageTitle
        self.__chRootStatus = chRootStatus
        self.__oscStatus = oscStatus
        self.__oscRev = oscRev
        self.__obsRev = obsRev
        self.__filesToDeleteList = []
        self.__prepDirName = None

        self.__obslightGit = ".git_obslight"
        self.__packageGit = None
        self.__currentGitIsPackageGit = False

        self.__patchMode = True
        self.__listRPMPublished = []

        if fromSave is None:
            self.__name = name
            if listFile is None:
                self.__fileList = []
            else:
                self.__fileList = listFile
            self.__status = status
            self.__obsRev = str(obsRev)
            self.__specFile = specFile
            self.__packageDirectory = None
        else:
            if "packageGit" in fromSave.keys():
                self.__packageGit = fromSave["packageGit"]
            if "currentGitIsPackageGit" in fromSave.keys():
                self.__currentGitIsPackageGit = fromSave["currentGitIsPackageGit"]
            if "name" in fromSave.keys():
                self.__name = fromSave["name"]
            if "listFile" in fromSave.keys():
                self.__fileList = copy(fromSave["listFile"])
            if "status" in fromSave.keys():
                self.__status = fromSave["status"]
            if "specFile" in fromSave.keys():
                self.__specFile = fromSave["specFile"]
            if "packageDirectory" in fromSave.keys():
                self.__packageDirectory = fromSave["packageDirectory"]
            if self.__status in [None, "None", ""]:
                self.__status = "Unknown"
            if  "description" in fromSave.keys():
                self.__description = fromSave["description"]
            if  "title" in fromSave.keys():
                self.__packageTitle = fromSave["title"]
            if "chRootStatus" in fromSave.keys():
                self.__chRootStatus = fromSave["chRootStatus"]
            if "oscStatus" in fromSave.keys():
                self.__oscStatus = fromSave["oscStatus"]
            if "firstCommitTag" in fromSave.keys():
                self.__firstCommitTag = fromSave["firstCommitTag"]
            if "secondCommitTag" in fromSave.keys():
                self.__secondCommitTag = fromSave["secondCommitTag"]
            if "oscRev" in fromSave.keys():
                self.__oscRev = str(fromSave["oscRev"])
            if "obsRev" in fromSave.keys():
                self.__obsRev = str(fromSave["obsRev"])
            if "currentPatch" in fromSave.keys():
                self.__currentPatch = fromSave["currentPatch"]
            if "listInfoFile" in fromSave.keys():
                self.__listInfoFile = copy(fromSave["listInfoFile"])
            if "listFileToDel" in fromSave.keys():
                self.__filesToDeleteList = copy(fromSave["listFileToDel"])
            if "prepDirName" in fromSave.keys():
                self.__prepDirName = fromSave["prepDirName"]

            if "patchMode" in fromSave.keys():
                self.__patchMode = fromSave["patchMode"]

            if "listRPMPublished" in fromSave.keys():
                self.__listRPMPublished = fromSave["listRPMPublished"]


        self.__rpmBuildDirectoryLink = "rpmbuild"
        self.__rpmBuildDirectory = "obslightbuild"
        self.__rpmBuildTmpDirectory = "obslightbuild_TMP"

        self.__chrootRpmBuildDirectory = chrootUserHome + "/" + self.__name + "/" + self.__rpmBuildDirectory
        self.__chrootRpmBuildTmpDirectory = chrootUserHome + "/" + self.__name + "/" + self.__rpmBuildTmpDirectory

        self.__initConfigureFile()

    #---------------------------------------------------------------------------
    def __initConfigureFile(self):
        '''
        Init the  spec.
        '''
        try:
            if not self.__specFile in (None, 'None', ""):
                self.__initSpecFile()
            else:
                self.__mySpecFile = None
        except BaseException:
            ObsLightPrintManager.getLogger().error(u"Error reading SPEC file", exc_info=1)

    def getRPMPublished(self):
        return self.__listRPMPublished

    def setRPMPublished(self, listRPMPublished):
        self.__listRPMPublished = listRPMPublished

    def getCurrentGitDirectory(self):
        if self.__currentGitIsPackageGit:
            return os.path.join(self.__chrootRpmBuildDirectory, "BUILD", self.__packageGit)
        else:
            return os.path.join(self.__chrootRpmBuildDirectory, "BUILD", self.__obslightGit)


    def setPackageGit(self, directory):
        self.__packageGit = directory

    def isCurrentGitIsPackageGit(self):
        return self.__currentGitIsPackageGit

    def getPackageInfo(self, info):
        '''
        
        '''
        res = {}
        for i in info:
            if i == "obsRev":
                res["obsRev"] = self.getObsPackageRev()
            elif i == "oscRev":
                res["oscRev"] = self.getOscPackageRev()
            elif i == "status":
                res["status"] = self.getPackageStatus()
            elif i == "oscStatus":
                res["oscStatus"] = self.getOscStatus()
            elif i == "chRootStatus":
                res["chRootStatus"] = self.getChRootStatus()
            else:
                raise ObsLightPackageErr("Error in getPackageInfo '" + str(i) + "' is not valide")
        return res
    #---------------------------------------------------------------------------
    def getOscStatus(self):
        '''
        
        '''
        return self.__oscStatus

    def getPackageStatus(self):
        '''
        
        '''
        return self.__status

    def getChRootStatus(self):
        '''
        
        '''
        return self.__chRootStatus

    def getOscPackageRev(self):
        '''
        
        '''
        return self.__oscRev

    def getObsPackageRev(self):
        '''
        
        '''
        return self.__obsRev

    #---------------------------------------------------------------------------

    def getChrootRpmBuildDirectory(self):
        '''
        
        '''
        return self.__chrootRpmBuildDirectory

    def getChrootRpmBuildTmpDirectory(self):
        '''
        
        '''
        return self.__chrootRpmBuildTmpDirectory

    def getTopDirRpmBuildDirectory(self):
        '''
        
        '''
        return  self.__rpmBuildDirectory

    def getTopDirRpmBuildLinkDirectory(self):
        '''
        
        '''
        return self.__rpmBuildDirectoryLink

    def getTopDirRpmBuildTmpDirectory(self):
        '''
        
        '''
        return self.__rpmBuildTmpDirectory



    def getPackageFileList(self):
        '''
        
        '''
        res = []
        res.extend(self.__fileList)
        res.extend(self.__filesToDeleteList)
        return res

    def setOscPackageRev(self, rev):
        '''
        
        '''
        self.__oscRev = rev

    def setObsPackageRev(self, rev):
        '''
        
        '''
        self.__obsRev = rev

    def setFirstCommit(self, tag):
        '''
        
        '''
        self.__firstCommitTag = tag

    def getFirstCommit(self):
        '''
        
        '''
        return self.__firstCommitTag

    def setSecondCommit(self, tag):
        '''
        
        '''
        self.__secondCommitTag = tag

    def getSecondCommit(self):
        return self.__secondCommitTag

    def getPackagePath(self):
        '''
        
        '''
        return self.__packagePath


    def setChRootStatus(self, status):
        '''
        
        '''
        self.__chRootStatus = status

    def __initSpecFile(self):
        '''
        
        '''
        if os.path.isfile(self.__packagePath + "/" + self.__specFile):
            self.__mySpecFile = ObsLightSpec(packagePath=self.__packagePath,
                                             aFile=self.__specFile)

    def delFromChroot(self):
        '''
        
        '''
        self.__packageDirectory = None
        self.__chRootStatus = PK_CONST.NOT_INSTALLED

    def isInstallInChroot(self):
        '''
        Return True if the package is install into the chroot.
        '''

        if self.getChRootStatus() == PK_CONST.NOT_INSTALLED:
            return False
        else:
            return True

    def update(self, status=None):
        '''
        
        '''
        if status not in [None, "", "None"]:
            self.__status = status

    def __subprocess(self, command=None, waitMess=False):
        '''
        
        '''
        return self.__mySubprocessCrt.execSubprocess(command=command,
                                                     waitMess=waitMess)

    def getName(self):
        '''
        return the name of the package.
        '''
        return self.__name

    def getDic(self):
        '''
        return a description of the object in a dictionary.
        '''
        aDic = {}
        aDic["name"] = self.__name
        aDic["listFile"] = copy(self.__fileList)
        aDic["status"] = self.__status
        aDic["specFile"] = self.__specFile
        aDic["packageDirectory"] = self.__packageDirectory
        aDic["description"] = self.__description
        aDic["title"] = self.__packageTitle
        aDic["chRootStatus"] = self.__chRootStatus
        aDic["oscStatus"] = self.__oscStatus
        aDic["firstCommitTag"] = self.__firstCommitTag
        aDic["secondCommitTag"] = self.__secondCommitTag
        aDic["oscRev"] = self.__oscRev
        aDic["currentPatch"] = self.__currentPatch
        aDic["obsRev"] = self.__obsRev
        aDic["listInfoFile"] = copy(self.__listInfoFile)
        aDic["listFileToDel"] = copy(self.__filesToDeleteList)
        aDic["prepDirName"] = self.__prepDirName
        aDic["packageGit"] = self.__packageGit
        aDic["currentGitIsPackageGit"] = self.__currentGitIsPackageGit
        aDic["patchMode"] = self.__patchMode
        aDic["listRPMPublished"] = self.__listRPMPublished
        return aDic

    def getPackageParameter(self, parameter=None):
        '''
        Get the value of a project parameter:
        the valid parameter is :
            name
            listFile
            status
            specFile
            fsPackageDirectory
            oscPackageDirectory
            description
            title
            chRootStatus
            oscStatus
            oscRev
            patchMode
            buildSortCutMode
            installSortCutMode
        '''

        if parameter == "name":
            return self.__name if self.__name != None else ""
        elif parameter == "listFile":
            return self.__fileList if self.__fileList != None else ""
        elif parameter == "obsStatus":
            return self.__status if self.__status != None else ""
        elif parameter == "specFile":
            return self.__specFile if self.__specFile != None else ""
        elif parameter == "fsPackageDirectory":
            if self.__packageDirectory != None:
                return self.__packageDirectory
            else :
                if self.getChRootStatus() == PK_CONST.NOT_INSTALLED:
                    return ""
                else:
                    return self.__chrootRpmBuildDirectory

        elif parameter == "oscPackageDirectory":
            return self.__packagePath if self.__packagePath != None else ""
        elif parameter == "description":
            return self.__description if self.__description != None else ""
        elif parameter == "title":
            return self.__packageTitle if self.__packageTitle != None else ""
        elif parameter == "chRootStatus":
            return self.__chRootStatus if self.__chRootStatus != None else ""
        elif parameter == "oscStatus":
            return  self.__oscStatus if self.__oscStatus != None else ""
        elif  parameter == "firstCommitTag":
            return self.__firstCommitTag if self.__firstCommitTag != None else ""
        elif  parameter == "oscRev":
            return self.__oscRev if self.__oscRev != None else ""
        elif parameter == "currentPatch":
            return self.__currentPatch if self.__currentPatch != None else ""
        elif parameter == "obsRev":
            return self.__obsRev if self.__obsRev != None else ""
        elif parameter == "listInfoFile":
            return self.__listInfoFile if self.__listInfoFile != None else ""
        elif parameter == "listFileToDel":
            return self.__filesToDeleteList if self.__filesToDeleteList != None else ""
        elif parameter == "prepDirName":
            return self.__prepDirName if self.__prepDirName != None else ""
        elif parameter == "patchMode":
            return self.__patchMode
        else:
            msg = "Parameter '%s' is not valid for getProjectParameter" % parameter
            raise ObsLightPackageErr(msg)

    def specFileHaveAnEmptyBuild(self):
        '''
        
        '''
        if self.__mySpecFile is None:
            self.__initSpecFile()

        if self.__mySpecFile is None:
            return None

        return self.__mySpecFile.specFileHaveAnEmptyBuild()

    def getSpecFileObj(self):

        return self.__mySpecFile



    def setPrepDirName(self, prepDirName):
        '''
        
        '''
        self.__prepDirName = prepDirName

    def getPrepDirName(self):
        '''
        
        '''
        return self.__prepDirName

    def getArchiveName(self):
        """
        Get the name of the temporary archive we create from
        sources extracted from git.
        """
        if self.__prepDirName != None:
            return self.__name + self.ArchiveSuffix
        else:
            return self.__prepDirName + self.ArchiveSuffix

    def initCurrentPatch(self):
        '''
        
        '''
        self.__currentPatch = None


    def patchIsInit(self):
        '''
        
        '''
        return self.__currentPatch != None

    def getCurrentPatch(self):
        '''
        
        '''
        return self.__currentPatch

    def setOscStatus(self, status):
        '''
        
        '''
        self.__oscStatus = status

    def setPackageParameter(self, parameter=None, value=None):
        '''
        return the value  of the parameter of the package:
        the valid parameter is :
            specFile
            packageDirectory
            description
            title
            status
            oscStatus
            patchMode
        '''
        if parameter == "specFile":
            self.__specFile = value
            self.__initConfigureFile()
        elif parameter == "packageDirectory":
            self.__packageDirectory = value
        elif parameter == "description":
            self.__description = value
        elif parameter == "title":
            self.__packageTitle = value
        elif parameter == "status":
            self.__status = value
        elif parameter == "listFile":
            self.__fileList = value
        elif parameter == "oscStatus":
            self.__oscStatus = value
        elif parameter == "oscRev":
            self.__oscRev = value
        elif parameter == "currentPatch":
            self.__currentPatch = value
        elif parameter == "obsRev":
            self.__obsRev = value
        elif parameter == "listInfoFile":
            self.__listInfoFile = value
        elif parameter == "listFileToDel":
            self.__filesToDeleteList = value
        elif parameter == "prepDirName":
            self.__prepDirName = value
        elif parameter == "patchMode":
            self.__patchMode = value
        else:
            raise ObsLightPackageErr("The parameter '" + parameter + "' value is not valid for setPackageParameter")
        return 0

    # TODO: delete this function
    def getListFile(self):
        return self.getFileList()

    def getFileList(self):
        return self.__fileList

    def getStatus(self):
        '''
        return the Status of the package.
        '''
        return self.__status

    def getSpecFile(self):
        '''
        return the  spec file.
        '''
        return self.__specFile

    def getSpecFilePath(self):
        '''
        return the  spec file abs path.
        '''
        return os.path.join(self.__packagePath, self.__specFile)

    def getOscDirectory(self):
        '''
        Return the absolute path of the osc directory of the package (base on the directory of the spec file).
        '''
        return self.__packagePath

    def setDirectoryBuild(self, packageDirectory=None):
        '''
        Set the directory of the package into the chroot.
        '''
        self.__packageDirectory = packageDirectory

    def getPackageDirectory(self):
        '''
        Return the directory of the package into the chroot.
        '''
        return self.__packageDirectory

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

    def getMacroDirectoryPackageName(self):
        '''
        Return the Name used for the BUILD directory, by setup in %prep section
        '''
        if self.__mySpecFile is None:
            self.__initSpecFile()

        if self.__mySpecFile is None:
            return None

        name = self.__mySpecFile.getMacroDirectoryPackageName()

        if name != None:
            name = self.__mySpecFile.getResolveMacroName(name)
            return name
        else:
            return None

    def getMacroPackageName(self):
        '''
        return the %{name} of the Pkg
        '''
        if self.__mySpecFile is None:
            self.__initSpecFile()

        if self.__mySpecFile is None:
            return None
        else:
            return self.__mySpecFile.getResolveMacroName("%{name}")

    def addPatch(self, aFile=None):
        '''
        add a Patch aFile to package, the patch is automatically add to the spec aFile.
        '''
        self.__currentPatch = aFile
        if self.__mySpecFile != None:
            if self.__mySpecFile.addpatch(aFile) == 1:
                ObsLightPrintManager.obsLightPrint("WARNING: Patch already exist the spec file will not be changed.")
            else:
                self.save()
        else:
            raise ObsLightPackageErr("No Spec in the package")

        self.__addFile(aFile)

    def __isASpecfile(self, afile):
        '''
        
        '''
        return afile.endswith(".spec")

    def __addFile(self, afile):
        '''
        
        '''
        self.__fileList.append(afile)

    def addFile(self, path):
        '''
        Add a aFile to the package.
        '''
        if not os.path.exists(path):
            raise ObsLightPackageErr("'" + path + "' is not a file, can't add to package")

        name = os.path.basename(path)
        shutil.copy2(path, os.path.join(self.getOscDirectory(), name))
        self.__addFile(name)
        ObsLightOsc.getObsLightOsc().add(path=self.getOscDirectory(), afile=name)

        if self.__isASpecfile(name):
            self.__specFile = name
            self.__initSpecFile()

        self.initPackageFileInfo()
        return 0

    def delFile(self, name):
        '''
        
        '''
        path = os.path.join(self.getOscDirectory(), name)
        resInfo = self.getPackageFileInfo(name)
        if not resInfo['Status'].startswith("!"):
            if not os.path.exists(path):
                raise ObsLightPackageErr("'" + path + "' not in package directory.")
            os.remove(path)

            if name in self.__fileList:
                self.__fileList.remove(name)

            if not resInfo['Status'].startswith("?"):
                self.__filesToDeleteList.append(name)
                ObsLightOsc.getObsLightOsc().remove(path=self.getOscDirectory(), afile=name)
        else:
            if name in self.__filesToDeleteList:
                self.__filesToDeleteList.remove(name)
        self.initPackageFileInfo()
        return 0

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
            self.__mySpecFile.saveTmpSpec(path=path, excludePatch=self.__currentPatch, archive=archive)
            self.initPackageFileInfo()
        else:
            raise ObsLightPackageErr("No Spec in the package")

    def saveSpecShortCut(self, path, section):
        '''
        Save the Spec file.
        '''
        if self.__mySpecFile != None:
            self.__mySpecFile.saveSpecShortCut(path, section, self.getChRootStatus(), self.getPackageDirectory())
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
            self.save()
            res = self.__mySpecFile.addFile(baseFile=baseFile, aFile=aFile)
            self.initPackageFileInfo()
            return res
        else:
            raise ObsLightPackageErr("No Spec in the package")

    def delFileToSpec(self, aFile=None):
        '''
        Add a delete command of a aFile to the spec aFile.
        '''
        if self.__mySpecFile != None:
            res = self.__mySpecFile.delFile(aFile=aFile)
            self.initPackageFileInfo()
            self.save()
            return res
        else:
            raise ObsLightPackageErr("No Spec in the package")

    def autoResolvedConflict(self):
        '''
        
        '''
        for aFile in self.__fileList:
            if self.testConflict(aFile=aFile):
                ObsLightOsc.getObsLightOsc().autoResolvedConflict(packagePath=self.getOscDirectory(), aFile=aFile)
        return self.initPackageFileInfo()

    def commitToObs(self, message=None):
        '''
        commit the package to the OBS server.
        '''
        self.autoResolvedConflict()
        ObsLightOsc.getObsLightOsc().commitProject(path=self.getOscDirectory(), message=message)
        self.__filesToDeleteList = []
        self.initPackageFileInfo()

    def addRemoveFileToTheProject(self):
        '''
        add new file and remove file to the project.
        '''
        ObsLightOsc.getObsLightOsc().addremove(path=self.getOscDirectory())
        self.initPackageFileInfo()

    def destroy(self):
        '''
        
        '''
        return self.__subprocess(command="rm -r  " + self.getOscDirectory())

    def initPackageFileInfo(self):
        '''
        
        '''
        res = ObsLightOsc.getObsLightOsc().getPackageFileInfo(workingdir=self.__packagePath)
        if res != None:
            self.__listInfoFile = {}
            for status, aFile in res:
                self.__listInfoFile[aFile] = status
        return 0

    def getPackageFileInfo(self, fileName):
        '''
        
        '''

        if self.__listInfoFile is None:
            res = ObsLightOsc.getObsLightOsc().getPackageFileInfo(workingdir=self.__packagePath)
            if res != None:
                self.__listInfoFile = {}
                for status, aFile in res:
                    self.__listInfoFile[aFile] = status
        if fileName in self.__listInfoFile.keys():
            res = self.__listInfoFile[fileName]
            if res == "A":
                res += " (Added)"
            elif res == "D":
                res += " (Deleted)"
            elif res == "M":
                res += " (Modified)"
            elif res == "!":
                res += " (item is missing, removed by non-osc command)"
            elif res == "?":
                res += " (item is not under version control)"
            elif res == "C":
                res += " (Conflicted)"

            return {u'Status': res}
        else:
            return {u'Status': u"! (item is missing, removed by non-osc command)"}

    def testConflict(self, aFile=None):
        '''
        
        '''
        if aFile != None:
            if self.getPackageFileInfo(aFile)[u'Status'].startswith("C"):
                return True
            return False
        else:
            for aFile in self.getListFile():
                if self.getPackageFileInfo(aFile)[u'Status'].startswith("C"):
                    return True
            return False








