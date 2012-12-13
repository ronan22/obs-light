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
Created on 22 juil. 2011

@author: rmartret
@author: Florent Vennetier
'''

import os
import re
import ObsLightPrintManager

from ObsLightTools import fileIsArchive, removeShortOption
from ObsLightObject import ObsLightObject

import ObsLightErr

import ObsLightPackages as PK_CONST

class ObsLightSpec(ObsLightObject):

    WrittenByObsLight = "# File written by OBS Light, don't modify it\n"

    def __init__(self, packagePath, aFile):
        ObsLightObject.__init__(self)
        self.__packagePath = packagePath
        self.__file = aFile
        self.__path = os.path.join(self.__packagePath, self.__file)

        self.__introduction_section = "introduction_section"
        self.__package = "%package"
        self.__description = "%description"
        self.__prepFlag = "%prep"
        self.__buildFlag = "%build"
        self.__installFlag = "%install"
        self.__cleanFlag = "%clean"
        self.__filesFlag = "%files"
        self.__checkFlag = "%check"
        self.__postFlag = "%post"
        self.__preunFlag = "%preun"
        self.__postunFlag = "%postun"
        self.__verifyscriptFlag = "%verifyscript"

        self.__listSection = [self.__package,
                              self.__description,
                              self.__prepFlag,
                              self.__buildFlag,
                              self.__installFlag,
                              self.__cleanFlag,
                              self.__filesFlag,
                              self.__checkFlag,
                              self.__postFlag,
                              self.__preunFlag,
                              self.__postunFlag,
                              self.__verifyscriptFlag]

        self.__orderList = []
        self.__spectDico = {}

        # FIXME: search minimum available source number in spec file
        self.archiveNumber = 9999

        if self.__path != None:
            self.parseFile()

    def parseFile(self,value=None):
        def testSection(line):
            for sect in self.__listSection:
                if line.startswith(sect):
                    return True
            return False


        self.__orderList = []
        self.__spectDico = {}

        path = self.__path
        if path != None:
            

            if not os.path.exists(path):
                raise ObsLightErr.ObsLightSpec("parseFile: the path: " + path + ", do not exist")
            
            
            if value is None:
                tmpLineList = []
                #Load the file in a list
                f = open(path, 'rb')
                
                for line in f:
                    tmpLineList.append(line)
                f.close()
            else:
                tmpLineList = value.split("\n")
                for i in range(len(tmpLineList)):
                    tmpLineList[i]=tmpLineList[i]+"\n"
                
            #init variable
            self.__spectDico = {}
            currentSection = self.__introduction_section
            self.__spectDico[currentSection] = []
            self.__orderList.append(currentSection)

            for line in tmpLineList:
                #use a clean string

                tmp_line = self.__cleanline(line)
                if testSection(tmp_line) :
                    while tmp_line in self.__spectDico.keys():
                        tmp_line = tmp_line + "(1)"
                    currentSection = tmp_line
                    self.__spectDico[currentSection] = []
                    self.__orderList.append(currentSection)
                self.__spectDico[currentSection].append(line)
        else:
            ObsLightPrintManager.obsLightPrint("ERROR")

    def __cleanline(self, line):
        return line.replace("\n", "").replace(" ", "")


    def __testLine(self, line, valueToFind):
        line = line.replace("\n", "")
        if line.startswith("%define"):
            line = line.replace("%define", "").strip()
        elif line.startswith("%global"):
            line = line.replace("%global", "").strip()
        elif line.startswith("%{!?"):
            line = line.strip("%{!?").strip("}").rstrip(" ").strip(" ")
            macroToTest = line[:line.index(":")]
            expression = line[line.index(":") + 1:]

            if macroToTest == valueToFind:
                res = self.__testLine(expression, valueToFind)
                if res != None:
                    return res
        l = []
        l.append(line)
        l.append(valueToFind)

        if line.startswith(valueToFind):
            result = line[len(valueToFind):].strip().strip(":").strip().rstrip()

            if "%" in result:
                if (valueToFind == "Version") and (result == "%{version}"):
                    res = self.__searchValue("version")
                    if "%" in result:
                        return self.getResolveMacroName(res)
                    else:
                        return res
                elif (valueToFind == "Name") and (result == "%{name}"):
                    res = self.__searchValue("name")
                    if "%" in result:
                        return self.getResolveMacroName(res)
                    else:
                        return res
                elif (valueToFind == "Release") and (result == "%{release}"):
                    res = self.__searchValue("release")
                    if "%" in result:
                        return self.getResolveMacroName(res)
                    else:
                        return res
                else:
                    return self.getResolveMacroName(result)
            else:
                return result
        else:
            return None

    def __searchValue(self, valueToFind):
        for line in self.__spectDico[self.__introduction_section]:
            res = self.__testLine(line, valueToFind)
            if res != None:
                return res

        return  None

    def __getValue(self, value):
        if value == "%{}":
            return ""
        elif value.strip("%").strip("{").rstrip("}") == "version":
            valueToFind = "Version"
        elif value.strip("%").strip("{").rstrip("}") == "name":
            valueToFind = "Name"
        elif value.strip("%").strip("{").rstrip("}") == "release":
            valueToFind = "Release"
        else:
            valueToFind = value.strip("%").strip("{").rstrip("}")

        if valueToFind.startswith("?"):
            valueToFind = valueToFind.strip("?")
            if ":" in valueToFind:
                #[macroToTest, expression] = valueToFind.split(":")
                macroToTest = valueToFind[:valueToFind.index(":")]
                expression = valueToFind[valueToFind.index(":") + 1:]
                res = self.__searchValue(macroToTest)
                if (res != None) :
                    res = self.__testLine(expression, valueToFind)
                    if res != None:
                        return res
                    else:
                        return expression
                else:
                    return ""
            else:
                macroToTest = valueToFind
                res = self.__searchValue(macroToTest)
                if res != None:
                    return res
                else:
                    return ""
        elif valueToFind.startswith("!?"):
            valueToFind = valueToFind.strip("!?")
            #[macroToTest, expression] = valueToFind.split(":")
            macroToTest = valueToFind[:valueToFind.index(":")]
            expression = valueToFind[valueToFind.index(":") + 1:]
            res = self.__searchValue(macroToTest)

            if res != None:
                return res
            else:
                res = self.__testLine(expression, valueToFind)
                if res != None:
                    return res
                else:
                    return value
        else:
            res = self.__searchValue(valueToFind)
            if res != None:
                return res
            else:
                return value

    def getMacroDirectoryPackageName(self):
        if self.__prepFlag in self.__spectDico.keys():
            for line in self.__spectDico[self.__prepFlag]:
                if line.startswith('%setup'):
                    line.replace("\n", "")

                    if "-n" in line:
                        name = line[line.index("-n") + 2:]
                        name = name.strip().strip("./").rstrip().rstrip("//")
                        if " " in name:
                            name = name.split(" ")[0]
                            name = name.strip().strip("./").rstrip().rstrip("//")
                        return name
                    elif "-qn" in line:
                        name = line[line.index("-qn") + 3:]
                        name = name.strip().strip("./").rstrip().rstrip("//")

                        if " " in name:
                            name = name.split(" ")[0]
                            name = name.strip().strip("./").rstrip().rstrip("//")
                        return name
                    else:
                        return "%{Name}-%{Version}"
            return None
        else:
            return None

    def getResolveMacroName(self, name):
        listToChange = []
        tmp = name
        while ("%" in tmp):
            i = tmp.index("%")
            if "{" in tmp:
                bOpen = 0
                bClose = 0
                j = tmp.index("{")
                p = j
                for c in tmp[j:]:
                    if c == "{":
                        bOpen += 1
                    elif c == "}":
                        bClose += 1
                    if bOpen == bClose:
                        if bOpen > 1:
                            toChange = tmp[j + 1:p]
                            res = self.getResolveMacroName(toChange)
                            name = name.replace(toChange , res)
                            if res.startswith("?"):
                                toAdd = "%{" + res + "}"
                            else:
                                toAdd = "%{" + res + "}"
                        else:
                            toAdd = tmp[i:p + 1]
                        break
                    p += 1
                if not toAdd == "":
                    listToChange.append(toAdd)
                tmp = tmp[p + 1:]
            else:
                tmp = tmp[i :]
                if " " in tmp:
                    p = tmp.index(" ")
                    toAdd = tmp[:p]
                    tmp = tmp[p + 1:]
                else:
                    toAdd = tmp
                    tmp = ""
                listToChange.append(toAdd)
        for value in listToChange:
            res = self.__getValue(value)
            name = name.replace(value , res)
        return name


    def getPrep(self):
        if self.__prepFlag in self.__spectDico.keys():
            res = ""
            for line in self.__spectDico[self.__prepFlag]:
                res += line
            return res
        else:
            return None

    def addpatch(self, aFile):
        #init the aId of the patch
        patchID = 0
        for line in self.__spectDico[self.__introduction_section]:
            #a regular expression sould be better
            if line.startswith("Patch") and (":" in line):
                try:
                    if aFile == self.__cleanline(line.split(":")[1]):
                        return 1

                    aId = line.split(":")[0].replace("Patch", "")
                    #the aId can be null
                    if (aId != "") and  (patchID <= int(aId)):
                        patchID = int(aId) + 1
                except ValueError:
                    ObsLightPrintManager.obsLightPrint(ValueError)
                except IndexError:
                    ObsLightPrintManager.obsLightPrint(IndexError)

        patch_Val_Prep = "Patch" + str(patchID)
        patch_Val_Build = "%patch" + str(patchID)
        patchCommand = patch_Val_Prep + ": " + aFile + "\n"
        self.__spectDico[self.__introduction_section].insert(0, patchCommand)
        comment = "# This line is insert automatically , please comment and clean the code\n"
        self.__spectDico[self.__introduction_section].insert(0, comment)

        #You can have not %prep section
        #add the patch after the last one or if any patch present in the prep part, at the end.
        if self.__prepFlag in self.__spectDico.keys():
            i = 0
            res = 0
            for line in self.__spectDico[self.__prepFlag]:
                i += 1
                if line.startswith("%patch"):
                    res = i
            if res == 0:
                res = i
            self.__spectDico[self.__prepFlag].insert(res, patch_Val_Build + " -p1 \n")
            comment = "# This line is insert automatically, please comment and clean the code\n"
            self.__spectDico[self.__prepFlag].insert(res, comment)

        return 0

    def addFile(self, baseFile=None, aFile=None):
        #init the aId of the Source
        SourceID = 1
        for line in self.__spectDico[self.__introduction_section]:
            #a regular expression sould be better
            if line.startswith("Source") and (":" in line):
                try:
                    if aFile == self.__cleanline(line.split(":")[1]):
                        return None

                    aId = line.split(":")[0].replace("Source", "")
                    #the aId can be null
                    if (aId != "") and (SourceID <= int(aId)):
                        SourceID = int(aId) + 1

                except ValueError:
                    ObsLightPrintManager.obsLightPrint(ValueError)
                except IndexError:
                    ObsLightPrintManager.obsLightPrint(IndexError)


        source_Val_Prep = "Source" + str(SourceID)
        source_Val_Build = "SOURCE" + str(SourceID)

        insertLine = source_Val_Prep + ": " + baseFile + "\n"
        self.__spectDico[self.__introduction_section].insert(0, insertLine)

        comment = "# This line is insert automatically, please comment and clean the code\n"
        self.__spectDico[self.__introduction_section].insert(0, comment)

        #You can have not %prep section
        if not self.__prepFlag in self.__spectDico.keys():
            self.__spectDico[self.__prepFlag] = []
            self.__orderList.append(self.__prepFlag)
            self.__spectDico[self.__prepFlag].append(self.__prepFlag + "\n")

        self.__spectDico[self.__prepFlag].append("cp %{" + source_Val_Build + "} " + aFile + "\n")

        return None

    def delFile(self, aFile=None):
        if self.__prepFlag in self.__spectDico.keys():
            for line in self.__spectDico[self.__prepFlag]:
                if aFile in line:
                    return None
            self.__spectDico[self.__prepFlag].append("rm " + aFile + "\n")

        return None

    def save(self, path=None):
        if path == None:
            path = self.__path
        f = open(path, 'w')
        for section in self.__orderList:
            for line in self.__spectDico[section]:
                if line.startswith("Release:") and \
                   (line.strip("Release:").strip(" ").rstrip("\n") == ""):
                    f.write("Release:1\n")
                else:
                    f.write(line)
        f.close()

    def getSpecTxt(self):
        res=""
        for section in self.__orderList:
            for line in self.__spectDico[section]:
                if line.startswith("Release:") and \
                   (line.strip("Release:").strip(" ").rstrip("\n") == ""):
                    res+="Release:1\n"
                else:
                    res+=line
        return res
        

    def saveSpecShortCut(self, path, sectionTarget, packageStatus, packagedir):
        if path == None:
            path = self.__path
        f = open(path, 'w')
        f.write(self.WrittenByObsLight)
        NoPrep = False

        for section in self.__orderList:
            for line in self.__spectDico[section]:
                if (section == "introduction_section"):
                    if line.startswith("Release:") and \
                       (line.strip("Release:").strip(" ").rstrip("\n") == ""):
                        f.write("Release:1\n")
                    else:
                        f.write(line)

                elif (section == "%prep") :
                    if not packageStatus in [PK_CONST.NOT_INSTALLED]:
                        f.write("%prep\n\n")
                        NoPrep = True
                        break
                    else:
                        f.write(line)

                elif (section == "%build"):

                    if sectionTarget == "install" and \
                       packageStatus in [ PK_CONST.BUILD,
                                          PK_CONST.BUILD_INSTALLED,
                                          PK_CONST.BUILD_PACKAGED]:

                        f.write("%build\n\n")
                        break
                    else:
                        if (line.startswith('%build')) and NoPrep :
                            f.write(line)
                            f.write("cd " + packagedir + "\n")
                        else:
                            f.write(line)

                elif (section == "%install"):
                    if (line.startswith('%install')) and NoPrep :
                        f.write(line)
                        f.write("cd " + packagedir + "\n")
                    else:
                        f.write(line)

                elif (section == "%check"):
                    if (line.startswith('%check')) and NoPrep :
                        f.write(line)
                        f.write("cd " + packagedir + "\n")
                    else:
                        f.write(line)

                else:
                    f.write(line)


        f.close()

    def saveTmpSpec(self, path, excludePatch, archive):
        SETUP = False
        if path is None:
            return None
        toWrite = ""
        isSourceAnArchive = False
        for section in self.__orderList:
            for line in self.__spectDico[section]:
                if line.startswith("Release:") and \
                   (line.strip("Release:").strip(" ").rstrip("\n") == ""):
                    toWrite += "Release: 1\n"
                elif (section == "introduction_section"):
                    patternSourceArch = r'[Ss]ource[0]?\s*:[\s]*(.*)'

                    for sourceVal in re.findall(patternSourceArch, line):
                        if fileIsArchive(sourceVal):
                            isSourceAnArchive = True
#                    if not line.startswith("Patch"):
#                        toWrite += line
                    #Patch can be used in %install (ex:rpmlint-mini-x86 MeeGo 1.2)
                    toWrite += line
                elif (section == "%prep"):
                    if (line.startswith('%prep')) :
                        toWrite += line
                    elif (line.startswith('%setup') and (not SETUP)):
                        line = removeShortOption(line, "c")
                        # If we match -a0, remove -T even if not isSourceAnArchive
                        a0Matched = re.match(r".*[\s]-a[\s]*[0]+($|([^\d].*))", line)
                        self.logger.debug('Matched "-a0" in %%setup: %s', a0Matched)
                        # Remove "-aN", N being a number
                        line = re.sub(r"[\s]-a[\s]*[\d]+", '', line)
                        if not isSourceAnArchive or a0Matched:
                            line = removeShortOption(line, "T")
                        # OBS Light generates its own archive.
                        # "-T" disables auto-unpack of Source0,
                        # "-b NNN" forces unpack of SourceNNN and cd into extracted dir
                        line = line[:-1] + " -T -b %d\n" % self.archiveNumber
                        toWrite += line + "\n"
                        toWrite += "if [ -e .emptyDirectory  ]; "
                        toWrite += "then for i in `cat .emptyDirectory` ; "
                        toWrite += "do mkdir -p $i ; echo $i ; done ; fi\n"
                        # we need to rename the file ".gitignore.obslight" to ".gitignore"
                        toWrite += "find ./ -type f -name .gitignore.obslight"
                        toWrite += " -execdir mv {} .gitignore \\;\n"
                        SETUP = True
                    elif line.startswith('%docs_package'):
                        toWrite += line
                else:
                    toWrite += line

            if (section == "%prep") and (not SETUP):
                toWrite += "mkdir -p %{name}-%{version}\n"
                toWrite += '%%setup -q -D -T -b %d\n' % self.archiveNumber

#        patternSourceFile = r'[Ss]ource[0]?\s*:\s*(.*)'

        aFile = open(path, 'w')
        aFile.write(self.WrittenByObsLight)
        # Insert OBS Light source declaration on top 
        aFile.write('Source%d: %s\n' % (self.archiveNumber, archive))

        # TODO: remove following code
        # This is useless since we add our Source9999
#        listFind = re.findall(patternSourceFile, toWrite)
#        if  len(listFind) > 0:
#            for sourceFile in listFind:
#                openBracket = sourceFile.count("{")
#                closeBracket = sourceFile.count("}")
#                if closeBracket > openBracket:
#                    lastBracket = sourceFile.rfind("}", closeBracket - openBracket)
#                    sourceFile = sourceFile[:lastBracket]
#                pattern = r'([Ss]ource[0]?\s*:\s*)' + sourceFile + "(.*)"
#                toWrite = re.sub(pattern, r'\1%s\2' % str(archive), toWrite)
#        else:
#            aFile.write('Source:%s\n' % archive)

        aFile.write(toWrite)
        aFile.close()

    def getsection(self):
        return self.__orderList

    def specFileHaveAnEmptyBuild(self):
        PrepAndBuild = True
        if "%build" in self.__spectDico.keys():
            for line in self.__spectDico["%build"]:
                if not (line.startswith("#")or line == "\n" or line == "%build\n"):
                    return False

        return PrepAndBuild


def getSpecTagValue(specPath, tag, startsWithDigit=False):
    """
    Search for the value of `tag` ("Name", "Version", etc.) in the spec file at `specPath`.
    If `startsWithDigit` is True, match only values starting with a digit.
    Returns None if nothing found.

    WARNING: macros are not resolved.
    """
    exp = re.compile(r"\s*%s\s*:\s*(%s.*)\s*" % (tag, r"\d" if startsWithDigit else ""), re.I)
    with open(specPath, "r") as f:
        for line in f:
            m = exp.match(line)
            if m is not None:
                return m.group(1)
    return None

if __name__ == '__main__':
    absSpecPath = "/home/meego/OBSLight/ObsProjects/Meego_oss_Build_Failed/meegotv:oss/xmlrpc-c"
    absSpecFile = "xmlrpc-c.spec"
    absSpecTmpFile = "xmlrpc-c.tmp.spec"
    absSpecFile_tmp = absSpecPath + "/" + absSpecTmpFile

    cli = ObsLightSpec(absSpecPath, absSpecFile)
    #cli.save(absSpecFile_tmp)
    cli.saveTmpSpec(absSpecFile_tmp, "", "testArchive.gz")

