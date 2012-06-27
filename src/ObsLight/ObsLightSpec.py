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
Created on 22 juil. 2011

@author: rmartret
'''
import sys
import os
import re
import ObsLightPrintManager

import ObsLightErr

class ObsLightSpec:
    '''
    
    '''
    def __init__(self, packagePath, aFile):
        '''
        
        '''
        self.__packagePath = packagePath
        self.__file = aFile
        self.__path = os.path.join(self.__packagePath, self.__file)

        self.__introduction_section = "introduction_section"
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

        self.__listSection = [self.__prepFlag,
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

        if self.__path != None:
            self.parseFile()

    def __cleanline(self, line):
        '''
            
        '''
        return line.replace("\n", "").replace(" ", "")


    def __testLine(self, line, valueToFind):
        '''
        
        '''
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
        '''
        
        '''
        for line in self.__spectDico[self.__introduction_section]:
            res = self.__testLine(line, valueToFind)
            if res != None:
                return res

        return  None

    def __getValue(self, value):
        '''
        
        '''

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
        '''
        
        '''
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
        '''
        
        '''
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
        '''
        
        '''
        if self.__prepFlag in self.__spectDico.keys():
            res = ""
            for line in self.__spectDico[self.__prepFlag]:
                res += line
            return res
        else:
            return None


    def parseFile(self):
        '''
        
        '''
        self.__orderList = []
        self.__spectDico = {}

        path = self.__path
        if path != None:
            tmpLineList = []

            if not os.path.exists(path):
                raise ObsLightErr.ObsLightSpec("parseFile: the path: " + path + ", do not exist")

            #Load the file in a list
            f = open(path, 'rb')

            for line in f:
                tmpLineList.append(line)

            f.close()

            #init variable
            self.__spectDico = {}
            currentSection = self.__introduction_section
            self.__spectDico[currentSection] = []
            self.__orderList.append(currentSection)

            for line in tmpLineList:
                #use a clean string

                tmp_line = self.__cleanline(line)
                if (tmp_line in self.__listSection) and (tmp_line != currentSection):
                    currentSection = tmp_line
                    self.__spectDico[currentSection] = []
                    self.__orderList.append(currentSection)
                self.__spectDico[currentSection].append(line)
        else:
            ObsLightPrintManager.obsLightPrint("ERROR")

    def addpatch(self, aFile):
        '''
        
        '''
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
        '''
        
        '''
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
        '''
        
        '''
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
        f.write("# File written by OBS Light, don't modify it\n")
        for section in self.__orderList:
            for line in self.__spectDico[section]:
                if line.startswith("Release:") and \
                   (line.strip("Release:").strip(" ").rstrip("\n") == ""):
                    f.write("Release:1\n")
                else:
                    f.write(line)
        f.close()

    def saveSpecShortCut(self, path, sectionTarget, packageStatus, packagedir):
        if path == None:
            path = self.__path
        f = open(path, 'w')
        f.write("#File Write by OBSLight don't modify it\n")
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
                    if not packageStatus in ["Not installed"]:
                        f.write("%prep\n\n")
                        NoPrep = True
                        break
                    else:
                        f.write(line)

                elif (section == "%build"):

                    if sectionTarget == "install" and \
                       packageStatus in [ "Built",
                                          "Build Installed",
                                          "Build Packaged"]:

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
        '''
        
        '''
        SETUP = False

        if path == None:
            return None
        toWrite = "#File Write by OBSLight don't modify it\n"
        for section in self.__orderList:
            for line in self.__spectDico[section]:
                if line.startswith("Release:") and \
                   (line.strip("Release:").strip(" ").rstrip("\n") == ""):
                    toWrite += "Release:1\n"
                elif (section == "introduction_section"):
                    if not line.startswith("Patch"):
                        toWrite += line
                elif (section == "%prep"):
                    if (line.startswith('%prep')) :
                        toWrite += line
                    elif (line.startswith('%setup') and (SETUP == False)):
                        line = line.replace("-c", "")
                        toWrite += line
                        toWrite += "if [ -e .emptyDirectory  ]; "
                        toWrite += "then for i in `cat .emptyDirectory` ; "
                        toWrite += "do mkdir -p $i;echo $i ; done;fi\n"
                        SETUP = True
                else:
                    toWrite += line

            if (section == "%prep") and (not SETUP):
                toWrite += '%setup -q -c\n'

        pattern = r'(Source[0]?\s*:).*'

        aFile = open(path, 'w')

        if  len(re.findall(pattern, toWrite)) > 0:
            aFile.write(re.sub(pattern, r'\1%s' % str(archive), toWrite))
        else:
            aFile.write('Source:%s\n' % archive)
            aFile.write(toWrite)
        aFile.close()

    def getsection(self):
        '''
        
        '''
        return self.__orderList

    def specFileHaveAnEmptyBuild(self):
        '''
        
        '''
        PrepAndBuild = True
        if "%build" in self.__spectDico.keys():
            for line in self.__spectDico["%build"]:
                if not (line.startswith("#")or line == "\n" or line == "%build\n"):
                    return False

        return PrepAndBuild

if __name__ == '__main__':
    absSpecFile_tmp = "/home/meego/OBSLight/ObsProjects/Tizen_Base/Tizen:FromObsTizen:1.0:Base/nss/nss.tmp.spec"
    absSpecPath = "/home/meego/OBSLight/ObsProjects/Tizen_Base/Tizen:FromObsTizen:1.0:Base/nss/"
    absSpecFile = "nss.spec"

    cli = ObsLightSpec(absSpecPath, absSpecFile)
    cli.save(absSpecFile_tmp)










