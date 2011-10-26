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
    def __init__(self, path=None):
        '''
        
        '''
        self.__path = path
        
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
        if path != None:
            self.parseFile(path)

    def __cleanline(self, line):   
        '''
            
        '''
        return line.replace("\n", "").replace(" ", "")
        
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
        patch_Val_Build = "%patch" + str(patchID)

        self.__spectDico[self.__introduction_section].insert(0, patch_Val_Prep + ": " + aFile + "\n")
        self.__spectDico[self.__introduction_section].insert(0, "# This line is insert automatically , please comment and clean the code\n")

        
        #You can have not %prep section
        #add the patch after the last one or if any patch present in the prep part, at the end.
        if self.__prepFlag in self.__spectDico.keys():
            i=0
            res=0
            for line in self.__spectDico[self.__prepFlag]:
                i+=1
                if line.startswith("%patch"):
                    res=i
            if res==0:
                res=i
            self.__spectDico[self.__prepFlag].insert(res,patch_Val_Build + " -p1\n")
            self.__spectDico[self.__prepFlag].insert(res, "# This line is insert automatically, please comment and clean the code\n")

        return 0
        
    def addFile(self,
                baseFile=None,
                aFile=None):
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
        if self.__prepFlag in self.__spectDico.keys():
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
    file2 = sys.argv[1] + ".sav"
    
    s = ObsLightSpec(file1)
    s.addpatch("aPatch.patch")
    s.save(file2)


    import subprocess
    subprocess.call(["diff", file1, file2])
    
    
    
    
    
    
    
    
    
     
    
    
    
