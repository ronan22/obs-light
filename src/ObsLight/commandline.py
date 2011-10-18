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
Created on 29 sept. 2011

@author: ronan
'''

import sys
import ObsLightErr

from util import safewriter

import ObsLightManager

MAN_HEADER = r"""

"""
MAN_FOOTER = r"""


"""

__PRGNAME__="ObsLight"

class ObsLight():
    """
    
    """

    man_header = MAN_HEADER
    man_footer = MAN_FOOTER

    def __init__(self, *args, **kwargs):
        '''
        
        '''
        sys.stderr = safewriter.SafeWriter(sys.stderr)
        sys.stdout = safewriter.SafeWriter(sys.stdout)

        self.__listArgv=sys.argv[1::]


    def main(self):
        """
        exec the main list of argument
        """

        self.cliObsLightManager=ObsLightManager.myObsLightManager
        
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
        __HELP__=__PRGNAME__+" <command> [--command-options]"
        __HELP__+="Commandes:"+"\n"
        __HELP__+="\t"+"getListObsServers: print the list of the OBS servers"+"\n"
        __HELP__+="\t"+"addObsServer add an OBS server to "+"\n"
        __HELP__+="\t"+"addProject"+"\n"
        __HELP__+="\t"+"getListProject"+"\n"
        __HELP__+="\t"+"getListPackage"+"\n"
        __HELP__+="\t"+"addPackage"+"\n"
        __HELP__+="\t"+"createChRoot"+"\n"
        __HELP__+="\t"+"goToChRoot"+"\n"
        __HELP__+="\t"+"addPackageSourceInChRoot"+"\n"
        __HELP__+="\t"+"makePatch"+"\n"
        __HELP__+="Type "+__PRGNAME__+" <command> --help for help on a specific command."+"\n"
        
        if len(listArgv)==0:
            print "ObsLight"
            
        elif len(listArgv)>0:
            if self.__isHelp(listArgv[0]):
                print __HELP__
            elif (listArgv[0]=="getListObsServers"):
                return self.getListObsServers(listArgv[1:])
            elif (listArgv[0]=="addObsServer"):
                return self.addObsServer(listArgv[1:])
            elif (listArgv[0]=="getListProject"):
                return self.getListProject(listArgv[1:])
            elif (listArgv[0]=="addProject"):
                return self.addProject(listArgv[1:])
            elif (listArgv[0]=="getListPackage"):
                return self.getListPackage(listArgv[1:])
            elif (listArgv[0]=="addPackage"):
                return self.addPackage(listArgv[1:])
            elif (listArgv[0]=="createChRoot"):
                return self.createChRoot(listArgv[1:])
            elif (listArgv[0]=="goToChRoot"):
                return self.goToChRoot(listArgv[1:])
            elif (listArgv[0]=="addPackageSourceInChRoot"):
                return self.addPackageSourceInChRoot(listArgv[1:])
            elif (listArgv[0]=="makePatch"):
                return self.makePatch(listArgv[1:])
            else:
                raise ObsLightErr.ArgError(listArgv[0]+" is not a valid command")
            
    def __isHelp(self,arg):
        '''
        Test if tha arg is ["--help","-h","-help"]
        '''
        if arg  in ["--help","-h","-help"]:
            return 1
        else:
            return 0   
        
    def getListProject(self,listArgv):
        '''
        print the list of the name of the project 
        '''
        __HELP__="usage: "+__PRGNAME__+" getListObsServers \n"
        __HELP__+="return the list of the name of the project"        

        if len(listArgv)==0: 
            result= self.cliObsLightManager.getListProject()
            if not (len(result)==0):
                for k in result:
                    print k
            else:
                print "No project" 
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError(listArgv[0]+" is not a valid command")
        return 0 
    
        
    def getListObsServers(self,listArgv):
        '''
        print the list of the name of the OBS Servers 
        '''
        __HELP__="usage: "+__PRGNAME__+" getListObsServers \n"
        __HELP__+="return the list of the name of the OBS Servers"        

        if len(listArgv)==0: 
            result= self.cliObsLightManager.getListOBSServers()
            if not (len(result)==0):
                for k in result:
                    print k
            else:
                print "No OBS Server" 
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError(listArgv[0]+" is not a valid command")
        return 0 
        
    def addObsServer(self,listArgv):
        '''
        add a OBS Server
        '''
        __HELP__="usage: "+__PRGNAME__+" addObsServer [--command-options] \n" 
        __HELP__+="\t--serverAPI api_url (require)\n"
        __HELP__+="\t--user user_name (require)\n"
        __HELP__+="\t--passw pwd_name (require)\n"
        __HELP__+="\t--serverWeb web_url \n"
        __HELP__+="\t--serverRepos repo_url (require)\n"
        __HELP__+="\t--aliases name \n"
        __HELP__+="add a OBS Server"        

        if (len(listArgv)%2==0) and (len(listArgv)<=(6*2)): 
            serverWeb=""
            serverAPI=None
            serverRepos=""
            aliases=None
            user=None
            passw=None
            
            for i in range(0,len(listArgv),2):
                if listArgv[i]=="--serverWeb":
                    serverWeb=listArgv[i+1]
                elif listArgv[i]=="--serverAPI":
                    serverAPI=listArgv[i+1]
                elif listArgv[i]=="--serverRepos":
                    serverRepos=listArgv[i+1]
                elif listArgv[i]=="--aliases":
                    aliases=listArgv[i+1] 
                elif listArgv[i]=="--user":
                    user=listArgv[i+1]
                elif listArgv[i]=="--passw":
                    passw=listArgv[i+1]
                else:
                    raise ObsLightErr.ArgError("unknow command for addOBSServer")

            self.cliObsLightManager.addObsServer(serverWeb=serverWeb, serverAPI=serverAPI, serverRepos=serverRepos, aliases=aliases, user=user, passw=passw)
            
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError("not a valid command for addOBSServer")
        return 0 
        
        
    def addProject(self,listArgv):
        '''
        Add a project to Obs Light
        '''
        __HELP__="usage: "+__PRGNAME__+" addProject [--command-options] \n" 
        __HELP__+="\t--projectName name (require)\n"
        __HELP__+="\t--projectTitle text \n"
        __HELP__+="\t--projectDirectory path \n"
        __HELP__+="\t--chrootDirectory path \n"
        __HELP__+="\t--obsserver api_url|aliases (require)\n"
        __HELP__+="\t--projectTarget name \n"
        __HELP__+="\t--description \n"
        __HELP__+="\t--projectArchitecture \n" 
        __HELP__+="add a obs project"
        


        if (len(listArgv)%2==0) and (len(listArgv)<=(6*2)): 
            projectName=None
            projectTitle=None
            projectDirectory=None
            chrootDirectory=None
            obsserver=None
            projectTarget=None
            description=None
            projectArchitecture=None
        
            for i in range(0,len(listArgv),2):
                if listArgv[i]=="--projectName":
                    projectName=listArgv[i+1]
                elif listArgv[i]=="--projectTitle":
                    projectTitle=listArgv[i+1]
                elif listArgv[i]=="--projectDirectory":
                    projectDirectory=listArgv[i+1]
                elif listArgv[i]=="--chrootDirectory":
                    chrootDirectory=listArgv[i+1] 
                elif listArgv[i]=="--obsserver":
                    obsserver=listArgv[i+1]
                elif listArgv[i]=="--projectTarget":
                    projectTarget=listArgv[i+1]
                elif listArgv[i]=="--description":
                    description=listArgv[i+1]
                elif listArgv[i]=="--projectArchitecture":
                    projectArchitecture=listArgv[i+1]
                else:
                    raise ObsLightErr.ArgError("unknow command for addOBSServer")
            
            self.cliObsLightManager.addProject(projectName=projectName, projectTitle=projectTitle, projectDirectory=projectDirectory, chrootDirectory=chrootDirectory, obsserver=obsserver ,projectTarget=projectTarget, description=description, projectArchitecture=projectArchitecture)      
        
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError("not a valid command for addProject")
        return 0 
    
    
    def getListPackage(self,listArgv):
        '''
        
        '''
        __HELP__="usage: "+__PRGNAME__+" getListPackage [--command-options] \n" 
        __HELP__+="Commandes:"+"\n"
        __HELP__+="\t"+"--obsServer serverName (if no serverName the project is local)"+"\n"
        __HELP__+="\t"+"--projectName projectName"+"\n"
        __HELP__+="\t"+"--localPackage 1/0 (if the project is local)"+"\n"

        if (len(listArgv)%2==0) and (len(listArgv)<=(2*2)): 
            projectName=None
            obsServer=None
            localPackage="1"

        
            for i in range(0,len(listArgv),2):
                if listArgv[i]=="--projectName":
                    projectName=listArgv[i+1]
                elif listArgv[i]=="--obsServer":
                    obsServer=listArgv[i+1]
                elif listArgv[i]=="--localPackage":
                    localPackage=listArgv[i+1]
                else:
                    raise ObsLightErr.ArgError("unknow command for getListPackage")
                
            if (obsServer!=None)and(projectName!=None):
                res=self.cliObsLightManager.getListPackageFromObsProject(obsserver=obsServer,project=projectName)
            elif (projectName!=None)and(localPackage in ["0","1"]):
                res=self.cliObsLightManager.getListPackageFromLocalProject(name=projectName,local=int(localPackage))
            else:
                raise ObsLightErr.ArgError("wrong command for getListPackage")
            
            if len(res)!=0:
                for pk in res:
                    print pk
            else:
                print "No Package."
                
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError("not a valid command for getListPackage")
        return 0 

    def addPackage(self, listArgv):
        '''
        
        '''
        __HELP__="usage: "+__PRGNAME__+" addPackage [--command-options] \n"
        __HELP__+="\t"+"--project projectName"+"\n"
        __HELP__+="\t"+"--package packageName"+"\n"
        
        project=None
        package=None
        
        if (len(listArgv)%2==0) and (len(listArgv)<=(2*2)): 
            for i in range(0,len(listArgv),2):
                if listArgv[i]=="--project":
                    project=listArgv[i+1]
                elif listArgv[i]=="--package":
                    package=listArgv[i+1]
                else:
                    raise ObsLightErr.ArgError("unknow command for addPackage")
                
            if (project!=None)and(package!=None):
                self.cliObsLightManager.addPackage( project=project  ,package=package)
            else:
                raise ObsLightErr.ArgError("wrong command for getListPackage")
                
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError("not a valid command for getListPackage")
        return 0 
    
    def createChRoot(self,listArgv):
        '''
        
        '''
        __HELP__="usage: "+__PRGNAME__+" createChRoot [--command-options] \n"
        __HELP__+="\t"+"--project projectName"+"\n"
        
        project=None
        
        if (len(listArgv)%2==0) and (len(listArgv)<=(1*2)): 
            for i in range(0,len(listArgv),2):
                if listArgv[i]=="--project":
                    project=listArgv[i+1]
                else:
                    raise ObsLightErr.ArgError("unknow command for createChRoot")
                
            if (project!=None):
                self.cliObsLightManager.createChRoot( project=project )
            else:
                raise ObsLightErr.ArgError("wrong command for createChRoot")
                
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError("not a valid command for createChRoot")
        return 0 
        
    def goToChRoot(self,listArgv):
        '''
        
        '''
        __COMMAND__="goToChRoot"
        
        __HELP__="usage: "+__PRGNAME__+" "+__COMMAND__+" [--command-options] \n"
        __HELP__+="\t"+"--project projectName"+"\n"
        __HELP__+="\t"+"--package packageName"+"directly go to the BUILD directory of the package\n"
        
        project=None
        package=None
        
        if (len(listArgv)%2==0) and (len(listArgv)<=(2*2)): 
            for i in range(0,len(listArgv),2):
                if listArgv[i]=="--project":
                    project=listArgv[i+1]
                elif listArgv[i]=="--package":
                    package=listArgv[i+1]
                else:
                    raise ObsLightErr.ArgError(listArgv[i]+" is unknowed command for "+__COMMAND__+"")
                
            if (project!=None):
                self.cliObsLightManager.goToChRoot(project=project,package=package)
            else:
                raise ObsLightErr.ArgError("wrong command for "+__COMMAND__+"")
                
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError("not a valid command for "+__COMMAND__+"")
        return 0 
        
    def addPackageSourceInChRoot(self,listArgv):
        '''
        
        '''
        __COMMAND__="addPackageSourceInChRoot"
        
        __HELP__="usage: "+__PRGNAME__+" "+__COMMAND__+" [--command-options] \n"
        __HELP__+="\t"+"--project projectName (require)"+"\n"
        __HELP__+="\t"+"--package packageName"+"\n"
        
        project=None
        package=None
        
        if (len(listArgv)%2==0) and (len(listArgv)<=(2*2)): 
            for i in range(0,len(listArgv),2):
                if listArgv[i]=="--project":
                    project=listArgv[i+1]
                elif listArgv[i]=="--package":
                    package=listArgv[i+1]
                else:
                    raise ObsLightErr.ArgError("unknow command for "+__COMMAND__)
            if (project!=None) or (package!=None):
                self.cliObsLightManager.addPackageSourceInChRoot(project=project,package=package)
            else:
                raise ObsLightErr.ArgError("wrong command for "+__COMMAND__)
                
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError("not a valid command for "+__COMMAND__)
        return 0 
        
    def makePatch(self,listArgv):
        '''
        
        '''
        __COMMAND__="makePatch"
        
        __HELP__="usage: "+__PRGNAME__+" "+__COMMAND__+" [--command-options] \n"
        __HELP__+="\t"+"--project projectName (require)"+"\n"
        __HELP__+="\t"+"--package packageName (require)"+"\n"
        __HELP__+="\t"+"--patch patchName (require)"+"\n"

        project=None
        package=None
        patch=None

        if (len(listArgv)%2==0) and (len(listArgv)<=(3*2)): 
            for i in range(0,len(listArgv),2):
                if listArgv[i]=="--project":
                    project=listArgv[i+1]
                elif listArgv[i]=="--package":
                    package=listArgv[i+1]
                elif listArgv[i]=="--patch":
                    patch=listArgv[i+1]
                else:
                    raise ObsLightErr.ArgError("unknow command for "+__COMMAND__)
            print project,package,patch
            if (project!=None) and (package!=None) and (patch!=None):
                self.cliObsLightManager.makePatch(project=project,package=package,patch=patch)
            else:
                raise ObsLightErr.ArgError("wrong command for "+__COMMAND__)
                
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError("not a valid command for "+__COMMAND__)
        return 0 
        
        
        