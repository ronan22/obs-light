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
Created on 28 oct. 2011

@author: ronan
'''
import sys
import os
import ObsLightPrintManager

import ObsLightErr
import shlex
import subprocess

class ObsLightYaml:
    '''
    '''
    def __init__(self, path=None, specPath=None):
        '''
        
        '''
        self.__path = path

        if specPath in (None, 'None', ""):
            self.__specPath = self.__path[:self.__path.rfind(".")] + ".spec"
        else:
            self.__specPath = specPath


        self.__introduction_section = "introduction_section"
        self.__Name__ = "Name"
        self.__Summary__ = "Summary"
        self.__Version__ = "Version"
        self.__Release__ = "Release"
        self.__Epoch__ = "Epoch"
        self.__Group__ = "Group"
        self.__License__ = "License"
        self.__URL__ = "URL"
        self.__BuildArch__ = "BuildArch"
        self.__ExclusiveArch__ = "ExclusiveArch"
        self.__Prefix__ = "Prefix"
        self.__LocaleName__ = "LocaleName"
        self.__LocaleOptions__ = "LocaleOptions"
        self.__Description__ = "Description"
        self.__Sources__ = "Sources"
        self.__SourcePrefix__ = "SourcePrefix"
        self.__ExtraSources__ = "ExtraSources"
        self.__SetupOptions__ = "SetupOptions"
        self.__Patches__ = "Patches"
        self.__Requires__ = "Requires"
        self.__RequiresPre__ = "RequiresPre"
        self.__RequiresPreUn__ = "RequiresPreUn"
        self.__RequiresPost__ = "RequiresPost"
        self.__RequiresPostUn__ = "RequiresPostUn"
        self.__PkgBR__ = "PkgBR"
        self.__PkgConfigBR__ = "PkgConfigBR"
        self.__Provides__ = "Provides"
        self.__Conflicts__ = "Conflicts"
        self.__Obsoletes__ = "Obsoletes"
        self.__BuildConflicts__ = "BuildConflicts"
        self.__Configure__ = "Configure"
        self.__ConfigOptions__ = "ConfigOptions"
        self.__Builder__ = "Builder"
        self.__QMakeOptions__ = "QMakeOptions"
        self.__Files__ = "Files"
        self.__FilesInput__ = "FilesInput"
        self.__NoFiles__ = "NoFiles"
        self.__RunFdupes__ = "RunFdupes"
        self.__RpmLintIgnore__ = "RpmLintIgnore"
        self.__Check__ = "Check"
        self.__SupportOtherDistros__ = "SupportOtherDistros"
        self.__UseAsNeeded__ = "UseAsNeeded"
        self.__NoAutoReq__ = "NoAutoReq"
        self.__NoAutoProv__ = "NoAutoProv"
        self.__NoSetup__ = "NoSetup"
        self.__NoAutoLocale__ = "NoAutoLocale"
        self.__NoDesktop__ = "NoDesktop"
        self.__UpdateDesktopDB__ = "UpdateDesktopDB"
        self.__NoIconCache__ = "NoIconCache"
        self.__AutoDepend__ = "AutoDepend"
        self.__AsWholeName__ = "AsWholeName"
        self.__AutoSubPackages__ = "AutoSubPackages"
        self.__SubPackages__ = "SubPackages"

        self.__listSection = [self.__introduction_section,
                              self.__Name__,
                              self.__Summary__,
                              self.__Version__,
                              self.__Release__,
                              self.__Epoch__,
                              self.__Group__,
                              self.__License__,
                              self.__URL__,
                              self.__BuildArch__,
                              self.__ExclusiveArch__,
                              self.__Prefix__,
                              self.__LocaleName__,
                              self.__LocaleOptions__,
                              self.__Description__,
                              self.__Sources__,
                              self.__SourcePrefix__,
                              self.__ExtraSources__,
                              self.__SetupOptions__,
                              self.__Patches__,
                              self.__Requires__,
                              self.__RequiresPre__,
                              self.__RequiresPreUn__,
                              self.__RequiresPost__,
                              self.__RequiresPostUn__,
                              self.__PkgBR__,
                              self.__PkgConfigBR__,
                              self.__Provides__,
                              self.__Conflicts__,
                              self.__Obsoletes__,
                              self.__BuildConflicts__,
                              self.__Configure__,
                              self.__ConfigOptions__,
                              self.__Builder__,
                              self.__QMakeOptions__,
                              self.__Files__,
                              self.__FilesInput__,
                              self.__NoFiles__,
                              self.__RunFdupes__,
                              self.__RpmLintIgnore__,
                              self.__Check__,
                              self.__SupportOtherDistros__,
                              self.__UseAsNeeded__,
                              self.__NoAutoReq__,
                              self.__NoAutoProv__,
                              self.__NoSetup__,
                              self.__NoAutoLocale__,
                              self.__NoDesktop__,
                              self.__UpdateDesktopDB__,
                              self.__NoIconCache__,
                              self.__AutoDepend__,
                              self.__AsWholeName__,
                              self.__AutoSubPackages__,
                              self.__SubPackages__]

        #deprecated if you use order dico
        self.__orderList = []
        self.__yamlDico = {}

        if path != None:
            self.parseFile(path)

    def __cleanline(self, line):
        '''
            
        '''
        return line.replace("\n", "")

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
            self.__yamlDico = {}
            currentSection = self.__introduction_section
            self.__yamlDico[currentSection] = []
            self.__orderList.append(currentSection)

            for line in tmpLineList:
                #use a clean string

                tmp_line = self.__cleanline(line)
                if ":" in tmp_line:
                    tag = tmp_line[:tmp_line.index(":")]
                    while tag.endswith(" "):
                        tag = tag[:-1]

                    if tag in self.__listSection:
                        currentSection = tag
                        self.__yamlDico[currentSection] = []
                        self.__orderList.append(currentSection)
                self.__yamlDico[currentSection].append(line)
        else:
            ObsLightPrintManager.obsLightPrint("ERROR")

    def addpatch(self, aFile):
        '''
        
        '''
        if not self.__Patches__ in self.__yamlDico.keys():
            self.__orderList.append(self.__Patches__)
            self.__yamlDico[self.__Patches__] = []
            self.__yamlDico[self.__Patches__].append(self.__Patches__ + ":\n")

        for line in self.__yamlDico[self.__Patches__]:
            if aFile in line:
                return 1

        self.__yamlDico[self.__Patches__].append("    - " + aFile + "\n")
        return 0

    def addFile(self, baseFile=None, aFile=None):
        '''
        
        '''
        if not self.__Sources__ in self.__yamlDico.keys():
            self.__orderList.append(self.__Sources__)
            self.__yamlDico[self.__Sources__] = []
            self.__yamlDico[self.__Sources__].append(self.__Sources__ + ":\n")
        #TO DO add Target cp    
        self.__yamlDico[self.__Sources__].append("    - " + baseFile + "\n")


        return None

    def delFile(self, aFile=None):
        '''
        
        '''
        #TODO
        return None

    def save(self, path=None):
        '''
        
        '''
        if path == None:
            path = self.__path
        f = open(path, 'w')

        for section in self.__orderList:
            for line in self.__yamlDico[section]:
                f.write(line)

        f.close()
        self.generateSpecFile()

    def getsection(self):
        '''
        
        '''
        return self.__orderList

    def getSpecFile(self):
        '''
        
        '''
        return self.__specPath

    def generateSpecFile(self):
        '''
        
        '''
        command = "specify --not-download --non-interactive " + self.__path + " --output=" + self.__specPath
        res = subprocess.Popen(shlex.split(command),
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)

        res.wait()
        return res

if __name__ == '__main__':
    file1 = sys.argv[1]
    file2 = sys.argv[1] + ".sav"
    #print "------------------", file1
    s = ObsLightYaml(path=file1)
    #s.addFile("aPatch.patch")
    s.save(file2)


    import subprocess
    subprocess.call(["diff", file1, file2])













