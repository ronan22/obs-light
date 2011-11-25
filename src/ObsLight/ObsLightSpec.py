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
Created on 22 juil. 2011

@author: rmartret
'''
import sys
import os
import ObsLightPrintManager

import ObsLightErr

class ObsLightSpec:
    '''
    '''
    def __init__(self, packagePath, file):
        '''
        
        '''
        self.__packagePath = packagePath
        self.__file = file
        self.__path = os.path.join(self.__packagePath, self.__file)

        self.__introduction_section = "introduction_section"
        self.__prepFlag = "%prep"
        self.__buildFlag = "%build"
        self.__installFlag = "%install"
        self.__cleanFlag = "%clean"
        self.__filesFlag = "%files "
        self.__postFlag = "%post"
        self.__preunFlag = "%preun"
        self.__postunFlag = "%postun"
        self.__verifyscriptFlag = "%verifyscript"

        self.__listSection = [self.__prepFlag,
                              self.__buildFlag,
                              self.__installFlag,
                              self.__cleanFlag,
                              self.__filesFlag,
                              self.__postFlag,
                              self.__preunFlag,
                              self.__postunFlag,
                              self.__verifyscriptFlag]
        #deprecated if you use order dico
        self.__orderList = []
        self.__spectDico = {}

        if self.__path != None:
            self.parseFile(self.__path)

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
                [macroToTest, expression] = valueToFind.split(":")
                res = self.__searchValue(macroToTest)
                if res != None:
                    res = self.__testLine(expression, valueToFind)
                    if res != None:
                        return res
                    else:
                        return value
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
            [macroToTest, expression] = valueToFind.split(":")
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
                        name = line.split("-n")[1].strip().strip("./").rstrip().rstrip("//")
                        if " " in name:
                            name = name.split(" ")[0]
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
                            res = self.getResolveMacroName(tmp[j + 1:p])
                            if res.startswith("?"):
                                toAdd = self.__getValue(res)
                            else:
                                toAdd = "%{" + res + "}"
                        else:
                            toAdd = tmp[i:p + 1]
                        break
                    p += 1
                if toAdd.count("%") > 1:
                    print "toAdd", toAdd
                    raise "Faile to parse  the spec file to get the BUILD/Repository"
                elif not toAdd == "":
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
            name = name.replace(value , self.__getValue(value))
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


    def parseFile(self, path=None):
        '''
        
        '''
        if path != None:
            tmpLineList = []


            if not os.path.exists(path):
                raise ObsLightErr.ObsLightSpec("parseFile: the path: " + path + ", do not exist")

            #Load the file in a list
            f = open(path, 'r')

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
                if tmp_line in self.__listSection:
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
                    if aId != "":
                        patchID = int(aId) + 1

                except ValueError:
                    ObsLightPrintManager.obsLightPrint(ValueError)
                except IndexError:
                    ObsLightPrintManager.obsLightPrint(IndexError)

        patch_Val_Prep = "Patch" + str(patchID)
        patch_Val_Build = " % patch" + str(patchID)

        self.__spectDico[self.__introduction_section].insert(0, patch_Val_Prep + ": " + aFile + "\n")
        self.__spectDico[self.__introduction_section].insert(0, "# This line is insert automatically , please comment and clean the code\n")


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
            self.__spectDico[self.__prepFlag].insert(res, patch_Val_Build + " -p1\n")
            self.__spectDico[self.__prepFlag].insert(res, "# This line is insert automatically, please comment and clean the code\n")

        return 0

    def addFile(self, baseFile=None, aFile=None):
        '''
        
        '''
        #init the aId of the Source
        SourceID = 0
        for line in self.__spectDico[self.__introduction_section]:
            #a regular expression sould be better
            if line.startswith("Source") and (":" in line):
                try:
                    if aFile == self.__cleanline(line.split(":")[1]):
                        return None

                    aId = line.split(":")[0].replace("Source", "")
                    #the aId can be null
                    if aId != "":
                        SourceID = int(aId) + 1

                except ValueError:
                    ObsLightPrintManager.obsLightPrint(ValueError)
                except IndexError:
                    ObsLightPrintManager.obsLightPrint(IndexError)


        source_Val_Prep = "Source" + str(SourceID)
        source_Val_Build = "SOURCE" + str(SourceID)

        self.__spectDico[self.__introduction_section].insert(0, source_Val_Prep + ": " + baseFile + "\n")
        self.__spectDico[self.__introduction_section].insert(0, "# This line is insert automatically, please comment and clean the code\n")

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
        '''
        
        '''
        if path == None:
            path = self.__path
        f = open(path, 'w')

        for section in self.__orderList:
            for line in self.__spectDico[section]:
                f.write(line)
        f.close()

    def getsection(self):
        '''
        
        '''
        return self.__orderList

if __name__ == '__main__':
    file1 = sys.argv[1]
    import subprocess
    import shlex
    s = ObsLightSpec(packagePath='', file=file1)

    try:
        name = s.getMacroDirectoryPackageName()
    except:
        print "ERROR ", file1

    if name != None:
        if "%" in name:
            #try:
            name = s.getResolveMacroName(name)
            #except:
            #    print "ERROR 2", file1

            f = open("/home/meego/OBSLight/meego1.2/chrootTransfert/runMe.sh", 'w')
            command = "rpm --eval " + name + " > /chrootTransfert/resultRpmQ.log"
            f.write(command + "\n")
            f.close()
            command = "sudo chroot /home/meego/OBSLight/meego1.2/aChroot /chrootTransfert/runMe.sh"
            p = subprocess.Popen(shlex.split(str(command)), stdout=None)
            p.wait()

            f = open("/home/meego/OBSLight/meego1.2/chrootTransfert/resultRpmQ.log", 'r')
            name = f.read().replace("\n", "")
            f.close()

            #if ("%" in name) :
            print os.path.basename(file1).ljust(50) + name.replace("\n", "")
        else:
            if "%" in name:
                print os.path.basename(file1).ljust(50) + name.replace("\n", "")















