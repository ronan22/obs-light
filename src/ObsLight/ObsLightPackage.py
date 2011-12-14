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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
'''
Created on 30 sept. 2011

@author: ronan
'''
import os
import shutil

from ObsLightSpec import ObsLightSpec
from ObsLightYaml import ObsLightYaml
import ObsLightOsc

import ObsLightPrintManager
from ObsLightSubprocess import SubprocessCrt

from ObsLightErr import ObsLightPackageErr

class ObsLightPackage(object):
    '''
    classdocs
    '''

    def __init__(self,
                 packagePath,
                 name=None,
                 specFile=None,
                 yamlFile=None,
                 listFile=[],
                 listInfoFile=None,
                 status="Unknown",
                 obsRev="-1",
                 oscStatus="Unknown",
                 oscRev="-1",
                 chRootStatus="Not installed",
                 description="",
                 packageTitle="",
                 fromSave=None):
        '''
        Constructor
        '''

        self.__packagePath = packagePath
        self.__mySubprocessCrt = SubprocessCrt()
        self.__yamlFile = None
        self.__specFile = None
        self.__myYamlFile = None
        self.__mySpecFile = None
        self.__firstCommitTag = None
        self.__currentPatch = None
        self.__listInfoFile = listInfoFile
        self.__description = description
        self.__packageTitle = packageTitle
        self.__chRootStatus = chRootStatus
        self.__oscStatus = oscStatus
        self.__oscRev = oscRev
        self.__obsRev = obsRev
        self.__listFileToDel = []

        if fromSave == None:
            self.__name = name
            if listFile == None:
                self.__listFile = []
            else:
                self.__listFile = listFile
            self.__status = status
            self.__obsRev = obsRev
            self.__specFile = specFile
            self.__yamlFile = yamlFile
            self.__packageDirectory = None
        else:
            if "name" in fromSave.keys():
                self.__name = fromSave["name"]
            if "listFile" in fromSave.keys():
                self.__listFile = fromSave["listFile"]
            if "status" in fromSave.keys():
                self.__status = fromSave["status"]
            if "specFile" in fromSave.keys():
                self.__specFile = fromSave["specFile"]
            if "yamlFile" in fromSave.keys():
                self.__yamlFile = fromSave["yamlFile"]
            if "packageDirectory" in fromSave.keys():
                self.__packageDirectory = fromSave["packageDirectory"]
            if self.__status in [None, "None", ""]:
                self.__status = "Unknown"
            if  "description" in fromSave.keys():
                self.__description = fromSave["description"]
            if  "packageTitle" in fromSave.keys():
                self.__packageTitle = fromSave["packageTitle"]
            if "chRootStatus" in fromSave.keys():
                self.__chRootStatus = fromSave["chRootStatus"]
            if "oscStatus" in fromSave.keys():
                self.__oscStatus = fromSave["oscStatus"]
            if "firstCommitTag" in fromSave.keys():
                self.__firstCommitTag = fromSave["firstCommitTag"]
            if "oscRev" in fromSave.keys():
                self.__oscRev = fromSave["oscRev"]
            if "obsRev" in fromSave.keys():
                self.__obsRev = fromSave["obsRev"]
            if "currentPatch" in fromSave.keys():
                self.__currentPatch = fromSave["currentPatch"]
            if "listInfoFile" in fromSave.keys():
                self.__listInfoFile = fromSave["listInfoFile"]
            if "listFileToDel" in fromSave.keys():
                self.__listFileToDel = fromSave["listFileToDel"]

        self.__rpmBuildDirectory = "rpmbuild"
        self.__rpmBuildTmpDirectory = "obslightbuild"

        self.__chrootRpmBuildDirectory = "/root/" + self.__name + "/" + self.__rpmBuildDirectory
        self.__chrootRpmBuildTmpDirectory = "/root/" + self.__name + "/" + self.__rpmBuildTmpDirectory

        self.__initConfigureFile()

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
        return self.__name + "/" + self.__rpmBuildDirectory

    def getTopDirRpmBuildTmpDirectory(self):
        '''
        
        '''
        return self.__name + "/" + self.__rpmBuildTmpDirectory

    def setFirstCommit(self, tag):
        '''
        
        '''
        self.__firstCommitTag = tag

    def getOscPackageRev(self):
        '''
        
        '''
        return self.__oscRev

    def getPackageFileList(self):
        '''
        
        '''
        res = []
        res.extend(self.__listFile)
        res.extend(self.__listFileToDel)
        return res

    def setOscPackageRev(self, rev):
        '''
        
        '''
        self.__oscRev = rev

    def getObsPackageRev(self):
        '''
        
        '''
        return self.__obsRev

    def setObsPackageRev(self, rev):
        '''
        
        '''
        self.__obsRev = rev

    def getFirstCommit(self):
        '''
        
        '''
        return self.__firstCommitTag

    def getPackagePath(self):
        '''
        
        '''
        return self.__packagePath

    def getGetChRootStatus(self):
        '''
        
        '''
        return self.__chRootStatus

    def setChRootStatus(self, status):
        '''
        
        '''
        self.__chRootStatus = status

    def __initConfigureFile(self):
        '''
        Init the  spec or yaml file.
        '''
        if not self.__yamlFile in (None, 'None', ""):
            self.__initYamlFile()
        else:
            self.__myYamlFile = None
            if not self.__specFile in (None, 'None', ""):
                self.__initSpecFile()
            else:
                self.__mySpecFile = None

    def __initYamlFile(self):
        '''
        
        '''
        self.__myYamlFile = ObsLightYaml(packagePath=self.__packagePath,
                                         file=self.__yamlFile,
                                         specFile=self.__specFile)
        if self.__specFile in (None, 'None', ""):
            self.__specFile = self.__myYamlFile.getSpecFile()
        else:
            self.__initSpecFile()

    def __initSpecFile(self):
        '''
        
        '''
        if os.path.isfile(self.__packagePath + "/" + self.__specFile):
            self.__mySpecFile = ObsLightSpec(packagePath=self.__packagePath,
                                             file=self.__specFile)

    def delFromChroot(self):
        '''
        
        '''
        self.__packageDirectory = None
        self.__chRootStatus = "Not installed"

    def isInstallInChroot(self):
        '''
        Return True if the package is install into the chroot.
        '''
        if self.__packageDirectory in (None, ""):
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
        aDic["listFile"] = self.__listFile
        aDic["status"] = self.__status
        aDic["specFile"] = self.__specFile
        aDic["yamlFile"] = self.__yamlFile
        aDic["packageDirectory"] = self.__packageDirectory
        aDic["description"] = self.__description
        aDic["packageTitle"] = self.__packageTitle
        aDic["chRootStatus"] = self.__chRootStatus
        aDic["oscStatus"] = self.__oscStatus
        aDic["firstCommitTag"] = self.__firstCommitTag
        aDic["oscRev"] = self.__oscRev
        aDic["currentPatch"] = self.__currentPatch
        aDic["obsRev"] = self.__obsRev
        aDic["listInfoFile"] = self.__listInfoFile
        aDic["listFileToDel"] = self.__listFileToDel
        return aDic

    def getPackageParameter(self, parameter=None):
        '''
        Get the value of a project parameter:
        the valid parameter is :
            name
            listFile
            status
            specFile
            yamlFile
            packageDirectory
            description
            packageTitle
            chRootStatus
            oscStatus
            oscRev
        '''
        if parameter == "name":
            return self.__name
        elif parameter == "listFile":
            return self.__listFile
        elif parameter == "status":
            return self.__status
        elif parameter == "specFile":
            return self.__specFile
        elif parameter == "yamlFile":
            return self.__yamlFile
        elif parameter == "packageDirectory":
            return self.__packageDirectory
        elif parameter == "description":
            return self.__description
        elif parameter == "packageTitle":
            return self.__packageTitle
        elif parameter == "chRootStatus":
            return self.__chRootStatus
        elif parameter == "oscStatus":
            return  self.__oscStatus
        elif  parameter == "firstCommitTag":
            return self.__firstCommitTag
        elif  parameter == "oscRev":
            return self.__oscRev
        elif parameter == "currentPatch":
            return self.__currentPatch
        elif parameter == "obsRev":
            return self.__obsRev
        elif parameter == "listInfoFile":
            return self.__listInfoFile
        elif parameter == "listFileToDel":
            return self.__listFileToDel
        else:
            raise ObsLightPackageErr("parameter value is not valid for getProjectParameter")

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
        return self.__currentPatch != None


    def setOscStatus(self, status):
        '''
        
        '''
        self.__oscStatus = status

    def setPackageParameter(self, parameter=None, value=None):
        '''
        return the value  of the parameter of the package:
        the valid parameter is :
            specFile
            yamlFile
            packageDirectory
            description
            packageTitle
            status
            oscStatus
        '''
        if parameter == "specFile":
            self.__specFile = value
            self.__initConfigureFile()
        elif parameter == "yamlFile":
            self.__yamlFile = value
            self.__initConfigureFile()
        elif parameter == "packageDirectory":
            self.__packageDirectory = value
        elif parameter == "description":
            self.__description = value
        elif parameter == "packageTitle":
            self.__packageTitle = value
        elif parameter == "status":
            self.__status = value
        elif parameter == "listFile":
            self.__listFile = value
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
            self.__listFileToDel = value
        else:
            raise ObsLightPackageErr("parameter value is not valid for setPackageParameter")

        return 0

    def getListFile(self):
        '''
        
        '''
        return self.__listFile


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
        
        '''
        if self.__mySpecFile == None:
            self.__initSpecFile()

        if self.__mySpecFile == None:
            return None

        name = self.__mySpecFile.getMacroDirectoryPackageName()

        if name != None:
            name = self.__mySpecFile.getResolveMacroName(name)
            return name
        else:
            return None

    def addPatch(self, aFile=None):
        '''
        add a Patch aFile to package, the patch is automatically add to the spec aFile.
        '''
        self.__currentPatch = aFile
        if self.__myYamlFile != None:
            if self.__myYamlFile.addpatch(aFile) == 1:
                ObsLightPrintManager.obsLightPrint("WARNING: Patch already exist the yaml file will not be changed.")
            else:
                self.save()
        elif self.__mySpecFile != None:
            if self.__mySpecFile.addpatch(aFile) == 1:
                ObsLightPrintManager.obsLightPrint("WARNING: Patch already exist the spec file will not be changed.")
            else:
                self.save()
        else:
            raise ObsLightPackageErr("No Spec or Yaml in the package")

        self.__addFile(aFile)

    def __isASpecfile(self, afile):
        '''
        
        '''
        return afile.endswith(".spec")

    def __isAyamlfile(self, afile):
        '''
        
        '''
        return afile.endswith(".yaml")

    def __addFile(self, afile):
        '''
        
        '''
        self.__listFile.append(afile)

    def addFile(self, path):
        '''
        Add a aFile to the package.
        '''
        if not os.path.exists(path):
            raise ObsLightPackageErr("'" + path + "' is not a path, can't add to package")

        name = os.path.basename(path)
        shutil.copy2(path, os.path.join(self.getOscDirectory(), name))
        self.__addFile(name)
        ObsLightOsc.getObsLightOsc().add(path=self.getOscDirectory(), afile=name)

        if self.__isASpecfile(name):
            self.__specFile = name
            self.__initSpecFile()
        elif self.__isAyamlfile(name):
            self.__yamlFile = name
            self.__initYamlFile()

    def delFile(self, name):
        '''
        
        '''
        path = os.path.join(self.getOscDirectory(), name)
        resInfo = self.getPackageFileInfo(name)
        if not resInfo['Status'].startswith("!"):
            if not os.path.exists(path):
                raise ObsLightPackageErr("'" + path + "' not in package directory.")
            os.remove(path)

            if name in self.__listFile:
                self.__listFile.remove(name)

            if not resInfo['Status'].startswith("?"):
                self.__listFileToDel.append(name)
                ObsLightOsc.getObsLightOsc().remove(path=self.getOscDirectory(), afile=name)
        else:
            if name in self.__listFileToDel:
                self.__listFileToDel.remove(name)

    def save(self):
        '''
        Save the Spec and yaml file.
        '''
        if self.__myYamlFile != None:
            self.__myYamlFile.save()
        elif self.__mySpecFile != None:
            self.__mySpecFile.save()
        else:
            raise ObsLightPackageErr("No Spec or Yaml in the package")

    def saveTmpSpec(self, path, archive):
        '''
        Save the Spec file.
        '''
        if self.__mySpecFile != None:
            self.__mySpecFile.saveTmpSpec(path=path, archive=archive)
        else:
            raise ObsLightPackageErr("No Spec or Yaml in the package")

    def saveSpec(self, path):
        '''
        Save the Spec file.
        '''
        if self.__mySpecFile != None:
            self.__mySpecFile.save(path=path)
        else:
            raise ObsLightPackageErr("No Spec or Yaml in the package")

    def addFileToSpec(self, baseFile=None, aFile=None):
        '''
        Add a delete command of a aFile to the spec/yaml aFile.
        '''

        if self.__myYamlFile != None:
            res = self.__myYamlFile.addFile(baseFile=baseFile, aFile=aFile)
            self.save()
            return res
        elif self.__mySpecFile != None:
            self.save()
            res = self.__mySpecFile.addFile(baseFile=baseFile, aFile=aFile)
            return res
        else:
            raise ObsLightPackageErr("No Spec or Yaml in the package")

    def delFileToSpec(self, aFile=None):
        '''
        Add a delete command of a aFile to the spec/yaml aFile.
        '''
        if self.__myYamlFile != None:
            res = self.__myYamlFile.delFile(aFile=aFile)
            self.save()
            return res
        elif self.__mySpecFile != None:
            res = self.__mySpecFile.delFile(aFile=aFile)
            self.save()
            return res
        else:
            raise ObsLightPackageErr("No Spec or Yaml in the package")

    def autoResolvedConflict(self):
        '''
        
        '''
        for aFile in self.__listFile:
            print "********************aFile", aFile
            if self.testConflict(aFile=aFile):
                ObsLightOsc.getObsLightOsc().autoResolvedConflict(packagePath=self.getOscDirectory(), aFile=aFile)

    def commitToObs(self, message=None):
        '''
        commit the package to the OBS server.
        '''
        self.autoResolvedConflict()
        ObsLightOsc.getObsLightOsc().commitProject(path=self.getOscDirectory(), message=message)
        self.__listFileToDel = []

    def addRemoveFileToTheProject(self):
        '''
        add new file and remove file to the project.
        '''
        ObsLightOsc.getObsLightOsc().addremove(path=self.getOscDirectory())

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

    def getPackageFileInfo(self, fileName):
        '''
        
        '''
        if self.__listInfoFile == None:
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









