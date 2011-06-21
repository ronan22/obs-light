# Copyright (C) 2006 Novell Inc.  All rights reserved.
# This program is free software; it may be used, copied, modified
# and distributed under the terms of the GNU General Public Licence,
# either version 2, or version 3 (at your option).


import sys

import obslighterr

from util import safewriter
from optparse import SUPPRESS_HELP

from OBSLightManager import OBSLightManager

MAN_HEADER = r"""

"""
MAN_FOOTER = r"""


"""


class OBSLight():
    """
    
    """

    man_header = MAN_HEADER
    man_footer = MAN_FOOTER

    def __init__(self, *args, **kwargs):
        
        sys.stderr = safewriter.SafeWriter(sys.stderr)
        sys.stdout = safewriter.SafeWriter(sys.stdout)

        self.__listArgv=sys.argv[1::]


    def main(self):
        """
        exec the main list of argument
        """
        self.cliOBSLightManager=OBSLightManager()
        
        while ("," in self.__listArgv):
            
            ll=self.__listArgv[:self.__listArgv.index(",")]
            
            self.__listArgv=self.__listArgv[self.__listArgv.index(",")+1:]
            
            self.execute(ll)

        return self.execute(self.__listArgv)
    
    def setListArgv(self, arg):
        """
        set the main list of argument,
        you can set  many list of arg separated by " , " 
        """
        self.__listArgv=arg    
        
        
    def execute(self,listArgv):
        """
        exec the a list of argument
        """

        
        if len(listArgv)==0:
            print "OBSLight"
            
        elif len(listArgv)>0:
    
            if listArgv[0]=="addProject":
                if (len(listArgv)%2 ==1)&(len(listArgv)<=6):
                    
                    projectName=None 
                    projectDirectory=None
                    chrootDirectory=None
                    
                    for i in range(1,len(listArgv),2):
                        if listArgv[i]=="projectName":
                            projectName=listArgv[i+1]
                        if listArgv[i]=="projectDirectory":
                            projectDirectory=listArgv[i+1]
                        if listArgv[i]=="chrootDirectory":
                            chrootDirectory=listArgv[i+1]
                        r=self.cliOBSLightManager.addProject(projectName=projectName , projectDirectory=projectDirectory,chrootDirectory=chrootDirectory)

                        return r
                else:
                    raise obslighterr.ArgError("Wrong number of arg in addProject")
                
            elif (listArgv[0]=="getListOBSLightProject"):
                result= self.cliOBSLightManager.getListOBSLightProject()
                if len(result)>0:
                    for k in result:
                        print k
                else:
                    print "No Project"
                    
                return 0
            
            
        else:
            raise obslighterr.ArgError("Too Many arg")
        
        
        
        
        
        



