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
            #getListOBSLightProject    
            if (listArgv[0]=="getListOBSLightProject"):
                result= self.cliOBSLightManager.getListOBSLightProject()
                if len(result)>0:
                    for k in result:
                        print k
                else:
                    print "No Project"
                    
                return 0
            #getListLocalRepositoryName 
            elif (listArgv[0]=="getListLocalRepositoryName"):
                result= self.cliOBSLightManager.getListLocalRepositoryName()
                if len(result)>0:
                    for k in result:
                        print k
                else:
                    print "No Repository"
                    
                return 0
            #addRepository    
            elif listArgv[0]=="addRepository":
                if ( (len(listArgv)%(2) ==1) & (len(listArgv)<=(7)) ):
                    
                    repositoryName=None 
                    repositoryPath=None
                    repositoryURL=None
                    
                    for i in range(1,len(listArgv),2):
                        if listArgv[i]=="name":
                            repositoryName=listArgv[i+1]
                        if listArgv[i]=="path":
                            repositoryPath=listArgv[i+1]
                        if listArgv[i]=="url":
                            repositoryURL=listArgv[i+1] 

                    print "path",repositoryPath, "url",repositoryURL, "name",repositoryName
                    return self.cliOBSLightManager.addRepository(path=repositoryPath, url=repositoryURL, name=repositoryName  )

                else:
                    raise obslighterr.ArgError("Wrong number of arg in addRepository")
            #getRepositoryInfo
            elif (listArgv[0]=="getRepositoryInfo"):
                if ( (len(listArgv)%(2) ==0) & (len(listArgv)<=(2)) ):
                    
                    repositoryName=None 
                    
                    repositoryName=listArgv[1]

                    result=  self.cliOBSLightManager.getRepositoryInfo( name=repositoryName  )
                    
                    if len(result)!=0:
                        for k in result:
                            print k
                    else:
                        print "not valide Repos Name"
                        

                else:
                    raise obslighterr.ArgError("Wrong number of arg in addRepository")
            #setUrlToRepositoty
            elif (listArgv[0]=="setUrlToRepositoty"):

                if ( (len(listArgv)%(2) ==1) & (len(listArgv)<=(5)) ):
                    
                    for i in range(1,len(listArgv),2):
                        if listArgv[i]=="name":
                            name=listArgv[i+1]
                        if listArgv[i]=="url":
                            url=listArgv[i+1] 
                            
                    return   self.cliOBSLightManager.setUrlToRepositoty(name=name,url=url)
                        
                else:
                    raise obslighterr.ArgError("Wrong number of arg in setUrlToRepositoty")
            #setPathToRepositoty
            elif (listArgv[0]=="setPathToRepositoty"):

                if ( (len(listArgv)%(2) ==1) & (len(listArgv)<=(4)) ):
                    
                    for i in range(1,len(listArgv),2):
                        if listArgv[i]=="name":
                            name=listArgv[i+1]
                        if listArgv[i]=="path":
                            path=listArgv[i+1] 
                            
                    return   self.cliOBSLightManager.setPathToRepositoty(name=name,path=path)
                        
                else:
                    raise obslighterr.ArgError("Wrong number of arg in setPathToRepositoty")
            #checkRepos
            elif (listArgv[0]=="checkRepos"):

                if ( (len(listArgv)%(2) ==0) & (len(listArgv)<=(2)) ):
                    
                    name=listArgv[1]

                    return   self.cliOBSLightManager.check(name=name)
                else:
                    raise obslighterr.ArgError("Wrong number of arg in checkRPMList")
            #addProject
            elif listArgv[0]=="addProject":
                if ( (len(listArgv)%(2) ==1) & (len(listArgv)<=(6)) ):
                    
                    ProjectName=None 
                    ProjectDirectory=None
                    ProjectChrootDirectory=None
                    ProjectTarget=None
                    ProjectArchitecture=None
                    
                    for i in range(1,len(listArgv),2):
                        if listArgv[i]=="name":
                            ProjectName=listArgv[i+1]
                        if listArgv[i]=="directory":
                            ProjectDirectory=listArgv[i+1]
                        if listArgv[i]=="chroot":
                            ProjectChrootDirectory=listArgv[i+1]
                        if listArgv[i]=="target":
                            ProjectTarget=listArgv[i+1]
                        if listArgv[i]=="architecture":
                            ProjectArchitecture=listArgv[i+1]
                                 
                    return self.cliOBSLightManager.addProject(name=ProjectName, directory=ProjectDirectory, chrootDirectory=ProjectChrootDirectory , target=ProjectTarget , architecture=ProjectArchitecture  )


                else:
                    raise obslighterr.ArgError("Wrong number of arg in addProject")
            #getProjectInfo
            elif (listArgv[0]=="getProjectInfo"):
                if ( (len(listArgv)%(2) ==0) & (len(listArgv)<=(2)) ):
                    
                    projectName=listArgv[1]

                    result=  self.cliOBSLightManager.getProjectInfo( name=projectName  )
                    
                    if len(result)!=0:
                        for k in result:
                            print k
                    else:
                        print "not valide Project Name"
                        
                else:
                    raise obslighterr.ArgError("Wrong number of arg in addRepository")
            #creatChroot
            elif (listArgv[0]=="creatChroot"):
                if ( (len(listArgv)%(2) ==0) & (len(listArgv)<=(2)) ):
                    
                    projectName=listArgv[1]
                    result=  self.cliOBSLightManager.creatChroot( name=projectName  )
                    
                        
                else:
                    raise obslighterr.ArgError("Wrong number of arg in addRepository")
            
            #addRPM
            elif listArgv[0]=="addRPM":

                if ( (len(listArgv)%(2) ==1) & (len(listArgv)<=(7)) ):
                    
                    project=None 
                    rpm=None
                    type=None
                    
                    for i in range(1,len(listArgv),2):
                        if listArgv[i]=="project":
                            project=listArgv[i+1]
                        if listArgv[i]=="rpm":
                            rpm=listArgv[i+1]
                        if listArgv[i]=="type":
                            type=listArgv[i+1]

                                 
                    return self.cliOBSLightManager.addRPM(project=project, rpm=rpm, type=type )


                else:
                    raise obslighterr.ArgError("Wrong number of arg in addRPM")
                
            #upDateRepository
            elif listArgv[0]=="upDateRepository":
                if ( (len(listArgv)%(2) ==0) & (len(listArgv)<=(2)) ):
                    
                    name=None 

                    name=listArgv[1]
                                 
                    return self.cliOBSLightManager.upDateRepository(name=name )

                else:
                    raise obslighterr.ArgError("Wrong number of arg in upDateRepository")
            
            
            
            
            #checkChRoot
            elif listArgv[0]=="checkChRoot":
                if ( (len(listArgv)%(2) ==0) & (len(listArgv)<=(2)) ):
                    
                    name=None 

                    name=listArgv[1]
                                 
                    return self.cliOBSLightManager.checkChRoot(project=name )

                else:
                    raise obslighterr.ArgError("Wrong number of arg in checkChRoot")
            
            elif listArgv[0]=="getProviderLib":
                if ( (len(listArgv)%(2) ==1) & (len(listArgv)<=(5)) ):
                    
                    project=None 
                    lib=None
                    
                    for i in range(1,len(listArgv),2):
                        if listArgv[i]=="project":
                            project=listArgv[i+1]
                        if listArgv[i]=="lib":
                            lib=listArgv[i+1]
                                 
                    res= self.cliOBSLightManager.getProviderLib(project=project,lib=lib)
                    
                    print res


                else:
                    raise obslighterr.ArgError("Wrong number of arg in getProviderLib")
            
            
            
            # 
            else:  
                raise obslighterr.ArgError("Not valid argument")
            
            
            
            
        else:
            raise obslighterr.ArgError("Too Many arg")
        
        
        
        
        
        



