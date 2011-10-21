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

__PRGNAME__ = "ObsLight"

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

        self.__listArgv = sys.argv[1:]


    def main(self):
        """
        exec the main list of argument
        """

        self.cliObsLightManager = ObsLightManager.myObsLightManager
        
        while ("," in self.__listArgv):
            
            ll = self.__listArgv[:self.__listArgv.index(",")]
            
            self.__listArgv = self.__listArgv[self.__listArgv.index(",") + 1:]
            
            self.execute(ll)

        return self.execute(self.__listArgv)
    
    def setListArgv(self, arg):
        """
        set the main list of argument,
        you can set  many list of arg separated by " , " 
        """
        self.__listArgv = arg    
        

 
    def execute(self, listArgv):
        """
        exec the a list of argument
        """
        __HELP__ = __PRGNAME__ + " <command> [--command-options]"
        __HELP__ += "Commandes:" + "\n"
        __HELP__ += "\t" + "getListObsServers: print the list of the OBS servers" + "\n"
        __HELP__ += "\t" + "addObsServer add an OBS server to " + "\n"
        __HELP__ += "\t" + "addProject" + "\n"
        __HELP__ += "\t" + "getListLocalProject" + "\n"
        __HELP__ += "\t" + "getListPackage" + "\n"
        __HELP__ += "\t" + "addPackage" + "\n"
        __HELP__ += "\t" + "createChRoot" + "\n"
        __HELP__ += "\t" + "goToChRoot" + "\n"
        __HELP__ += "\t" + "addPackageSourceInChRoot" + "\n"
        __HELP__ += "\t" + "makePatch" + "\n"
        __HELP__ += "\t" + "addAndCommitChange" + "\n"
        __HELP__ += "\t" + "addRepoInChRoot" + "\n"
        __HELP__ += "Type " + __PRGNAME__ + " <command> --help for help on a specific command." + "\n"
        
        __DESCRIPTION__ = "ObsLight: http://wiki.meego.com/OBS_Light  "
        __DESCRIPTION__ += "\tProvide a tool to manage a OBS project on your local machine"
        
        if len(listArgv) == 0:
            print __DESCRIPTION__
            
        elif len(listArgv) > 0:
            if self.__isHelp(listArgv[0]):
                print __HELP__
            elif (listArgv[0] == "getListObsServers"):
                return self.getListObsServers(listArgv[1:])
            elif (listArgv[0] == "addObsServer"):
                return self.addObsServer(listArgv[1:])
            elif (listArgv[0] == "getListLocalProject"):
                return self.getListLocalProject(listArgv[1:])
            elif (listArgv[0] == "addProject"):
                return self.addProject(listArgv[1:])
            elif (listArgv[0] == "getListPackage"):
                return self.getListPackage(listArgv[1:])
            elif (listArgv[0] == "addPackage"):
                return self.addPackage(listArgv[1:])
            elif (listArgv[0] == "createChRoot"):
                return self.createChRoot(listArgv[1:])
            elif (listArgv[0] == "goToChRoot"):
                return self.goToChRoot(listArgv[1:])
            elif (listArgv[0] == "addPackageSourceInChRoot"):
                return self.addPackageSourceInChRoot(listArgv[1:])
            elif (listArgv[0] == "makePatch"):
                return self.makePatch(listArgv[1:])
            elif (listArgv[0] == "addAndCommitChange"):
                return self.addAndCommitChange(listArgv[1:])
            elif (listArgv[0] == "addRepoInChRoot"):
                return self.addRepoInChRoot(listArgv[1:])
            else:
                raise ObsLightErr.ArgError(listArgv[0] + " is not a valid command")
            
    def __isHelp(self, arg):
        '''
        Test if tha arg is ["--help","-h","-help"]
        '''
        if arg  in ["--help", "-h", "-help", "help"]:
            return 1
        else:
            return 0   
        
    def getListLocalProject(self, listArgv):
        '''
        print the list of the name of the project 
        '''
        __COMMAND__ = "getListLocalProject"
        __HELP__ = "usage: " + __PRGNAME__ + " getListLocalProject \n"
        __HELP__ += "return the list of the name of the project"        

        if len(listArgv) == 0: 
            result = self.cliObsLightManager.getListLocalProject()
            if not (len(result) == 0):
                for k in result:
                    print k
            else:
                print "No project" 
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError(listArgv[0] + " is not a valid command for " + __COMMAND__)
        return 0 
    
        
    def getListObsServers(self, listArgv):
        '''
        print the list of the name of the OBS Servers 
        '''
        __COMMAND__ = "getListObsServers"
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " \n"
        __HELP__ += "return the list of the name of the OBS Servers"        

        if len(listArgv) == 0: 
            result = self.cliObsLightManager.getListObsServers()
            if not (len(result) == 0):
                for k in result:
                    print k
            else:
                print "No OBS Server" 
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError(listArgv[0] + " is not a valid command for " + __COMMAND__)
        return 0 
        
    def addObsServer(self, listArgv):
        '''
        add a OBS Server
        '''
        __COMMAND__ = "addObsServer"
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n" 
        __HELP__ += "\t--serverAPI api_url (require)\n"
        __HELP__ += "\t--user user_name (require)\n"
        __HELP__ += "\t--passw pwd_name (require)\n"
        __HELP__ += "\t--serverWeb web_url \n"
        __HELP__ += "\t--serverRepos repo_url (require)\n"
        __HELP__ += "\t--aliases name \n"
        __HELP__ += "add a OBS Server"        

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (6 * 2)): 
            serverWeb = ""
            serverAPI = None
            serverRepos = ""
            aliases = None
            user = None
            passw = None
            
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--serverWeb":
                    serverWeb = listArgv[i + 1]
                elif listArgv[i] == "--serverAPI":
                    serverAPI = listArgv[i + 1]
                elif listArgv[i] == "--serverRepos":
                    serverRepos = listArgv[i + 1]
                elif listArgv[i] == "--aliases":
                    aliases = listArgv[i + 1] 
                elif listArgv[i] == "--user":
                    user = listArgv[i + 1]
                elif listArgv[i] == "--passw":
                    passw = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgError("unknow command for " + __COMMAND__)

            self.cliObsLightManager.addObsServer(serverWeb=serverWeb,
                                                 serverAPI=serverAPI,
                                                 serverRepos=serverRepos,
                                                 aliases=aliases,
                                                 user=user,
                                                 passw=passw)
            
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError("not a valid command for " + __COMMAND__)
        return 0 
        
        
    def addProject(self, listArgv):
        '''
        Add a project to Obs Light
        '''
        __COMMAND__ = "addProject"
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t--projectLocalName name :if no name are define the projectLocalName is equal to projectObsName ,the symbol : are replace by _\n"
        __HELP__ += "\t--projectObsName name (require)\n"
        __HELP__ += "\t--projectTitle text \n"
        __HELP__ += "\t--projectDirectory path \n"
        __HELP__ += "\t--chrootDirectory path \n"
        __HELP__ += "\t--obsServer api_url|aliases (require)\n"
        __HELP__ += "\t--projectTarget name \n"
        __HELP__ += "\t--description \n"
        __HELP__ += "\t--projectArchitecture \n" 
        __HELP__ += "add a obs project \n"
        
        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (9 * 2)): 
            projectLocalName = None
            projectObsName = None
            projectTitle = None
            projectDirectory = None
            chrootDirectory = None
            obsServer = None
            projectTarget = None
            description = None
            projectArchitecture = None
        
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--projectObsName":
                    projectObsName = listArgv[i + 1]
                elif listArgv[i] == "--projectLocalName":
                    projectLocalName = listArgv[i + 1]
                elif listArgv[i] == "--projectTitle":
                    projectTitle = listArgv[i + 1]
                elif listArgv[i] == "--projectDirectory":
                    projectDirectory = listArgv[i + 1]
                elif listArgv[i] == "--chrootDirectory":
                    chrootDirectory = listArgv[i + 1] 
                elif listArgv[i] == "--obsServer":
                    obsServer = listArgv[i + 1]
                elif listArgv[i] == "--projectTarget":
                    projectTarget = listArgv[i + 1]
                elif listArgv[i] == "--description":
                    description = listArgv[i + 1]
                elif listArgv[i] == "--projectArchitecture":
                    projectArchitecture = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgError("unknow command " + listArgv[i] + " for " + __COMMAND__)

            self.cliObsLightManager.addProject(projectLocalName=projectLocalName,
                                                projectObsName=projectObsName,
                                                projectTitle=projectTitle,
                                                projectDirectory=projectDirectory,
                                                chrootDirectory=chrootDirectory,
                                                obsServer=obsServer ,
                                                projectTarget=projectTarget,
                                                description=description,
                                                projectArchitecture=projectArchitecture)      
        
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError("not a valid command for " + __COMMAND__)
        return 0 
    
    
    def getListPackage(self, listArgv):
        '''
        return the list of the package.
        '''
        __COMMAND__ = "getListPackage"
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n" 
        __HELP__ += "Commandes:" + "\n"
        __HELP__ += "\t" + "--obsServer serverName (if no serverName the projectLocalName is local)" + "\n"
        __HELP__ += "\t" + "--projectLocalName projectLocalName" + "\n"
        __HELP__ += "\t" + "--localPackage 1/0 (if the projectLocalName is local)" + "\n"

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (2 * 2)): 
            projectLocalName = None
            obsServer = None
            localPackage = "1"
        
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--projectLocalName":
                    projectLocalName = listArgv[i + 1]
                elif listArgv[i] == "--obsServer":
                    obsServer = listArgv[i + 1]
                elif listArgv[i] == "--localPackage":
                    localPackage = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgError("unknow command for " + __COMMAND__)
                
            if (obsServer != None)and(projectLocalName != None):
                res = self.cliObsLightManager.getListPackageFromObsProject(obsServer=obsServer, 
                                                                           projectLocalName=projectLocalName)
            elif (projectLocalName != None)and(localPackage in ["0", "1"]):
                res = self.cliObsLightManager.getListPackageFromLocalProject(name=projectLocalName, 
                                                                             local=int(localPackage))
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)
            
            if len(res) != 0:
                for pk in res:
                    print pk
            else:
                print "No Package."
                
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError("not a valid command for " + __COMMAND__)
        return 0 

    def addPackage(self, listArgv):
        '''
        add a package.
        '''
        __COMMAND__ = "addPackage"
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectLocalName projectName" + "\n"
        __HELP__ += "\t" + "--package packageName" + "\n"
        
        projectLocalName = None
        package = None
        
        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (2 * 2)): 
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--projectLocalName":
                    projectLocalName = listArgv[i + 1]
                elif listArgv[i] == "--package":
                    package = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgError("unknow command " + listArgv[i] + " for " + __COMMAND__)
                
            if (projectLocalName != None)and(package != None):
                self.cliObsLightManager.addPackage(projectLocalName=projectLocalName  , 
                                                   package=package)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)
                
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError("not a valid command for " + __COMMAND__)
        return 0 
    
    def createChRoot(self, listArgv):
        '''
        create a chroot
        '''
        __COMMAND__ = "createChRoot"
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectLocalName projectName" + "\n"
        
        projectLocalName = None
        
        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (1 * 2)): 
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--projectLocalName":
                    projectLocalName = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgError("unknow command " + listArgv[i] + " for " + __COMMAND__)
                
            if (projectLocalName != None):
                self.cliObsLightManager.createChRoot(projectLocalName=projectLocalName)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)
                
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError("not a valid command for " + __COMMAND__)
        return 0 
        
    def goToChRoot(self, listArgv):
        '''
        open a bash in the chroot
        '''
        __COMMAND__ = "goToChRoot"
        
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectLocalName projectName" + "\n"
        __HELP__ += "\t" + "--package packageName" + "directly go to the BUILD directory of the package\n"
        
        projectLocalName = None
        package = None
        
        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (2 * 2)): 
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--projectLocalName":
                    projectLocalName = listArgv[i + 1]
                elif listArgv[i] == "--package":
                    package = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgError(listArgv[i] + " is unknowed command " + listArgv[i] + " for " + __COMMAND__ + "")
                
            if (projectLocalName != None):
                self.cliObsLightManager.goToChRoot(projectLocalName=projectLocalName, 
                                                   package=package)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__ + "")
                
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError("not a valid command for " + __COMMAND__ + "")
        return 0 
        
    def addPackageSourceInChRoot(self, listArgv):
        '''
        install a package source into a chroot, and make the spec %prep
        '''
        __COMMAND__ = "addPackageSourceInChRoot"
        
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectLocalName projectName (require)" + "\n"
        __HELP__ += "\t" + "--package packageName" + "\n"
        
        projectLocalName = None
        package = None
        
        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (2 * 2)): 
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--projectLocalName":
                    projectLocalName = listArgv[i + 1]
                elif listArgv[i] == "--package":
                    package = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgError("unknow command " + listArgv[i] + " for " + __COMMAND__)
            if (projectLocalName != None) or (package != None):
                self.cliObsLightManager.addPackageSourceInChRoot(projectLocalName=projectLocalName,
                                                                 package=package)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)
                
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError("not a valid command for " + __COMMAND__)
        return 0 
        
    def makePatch(self, listArgv):
        '''
        generate a patch 
        '''
        __COMMAND__ = "makePatch"
        
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectLocalName projectName (require)" + "\n"
        __HELP__ += "\t" + "--package packageName (require)" + "\n"
        __HELP__ += "\t" + "--patch patchName (require)" + "\n"

        projectLocalName = None
        package = None
        patch = None

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (3 * 2)): 
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--projectLocalName":
                    projectLocalName = listArgv[i + 1]
                elif listArgv[i] == "--package":
                    package = listArgv[i + 1]
                elif listArgv[i] == "--patch":
                    patch = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgError("unknow command for " + listArgv[i] + " " + __COMMAND__)

            if (projectLocalName != None) and (package != None) and (patch != None):
                self.cliObsLightManager.makePatch(projectLocalName=projectLocalName,
                                                  package=package,
                                                  patch=patch)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)
                
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError("not a valid command for " + __COMMAND__)
        return 0 
        
        
    def addAndCommitChange(self, listArgv):
        '''
        add/delete file in a osc directory. 
        '''
        __COMMAND__ = "addAndCommitChange"
        
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectLocalName projectName (require)" + "\n"
        __HELP__ += "\t" + "--package packageName (require)" + "\n"
        __HELP__ += "\t" + "--message message(require)" + "\n"
        __HELP__ += "Add new file in the osc directory and commit"
        
        projectLocalName = None
        package = None
        message = None

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (3 * 2)): 
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--projectLocalName":
                    projectLocalName = listArgv[i + 1]
                elif listArgv[i] == "--package":
                    package = listArgv[i + 1]
                elif listArgv[i] == "--message":
                    message = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgError("unknow command " + listArgv[i] + " for " + __COMMAND__)
            if (message == None):
                raise ObsLightErr.ArgError("No message for " + __COMMAND__)
            elif (projectLocalName != None) and (package != None) :
                self.cliObsLightManager.addAndCommitChange(projectLocalName=projectLocalName, 
                                                           package=package, message=message)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)
                
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError("not a valid command for " + __COMMAND__)
        return 0 
        
    def addRepoInChRoot(self, listArgv):
        '''
        add a repo in zypper in the chroot
        '''
        __COMMAND__ = "addRepoInChRoot"
        
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--fromProject projectName " + "\n"
        __HELP__ += "\t" + "--projectLocalName projectName (require)" + "\n"
        __HELP__ += "\t" + "--alias message" + "\n"
        __HELP__ += "\t" + "--url message" + "\n"
        __HELP__ += "\t" + "if --fromProject is specified, --alias and --url are ignored" + "\n"
        
        fromProject = None
        projectLocalName = None
        alias = None
        url = None

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (3 * 2)): 
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--fromProject":
                    fromProject = listArgv[i + 1]
                elif listArgv[i] == "--projectLocalName":
                    projectLocalName = listArgv[i + 1]
                elif listArgv[i] == "--alias":
                    alias = listArgv[i + 1]
                elif listArgv[i] == "--url":
                    url = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgError("unknown command " + listArgv[i] + " for " + __COMMAND__)
            if (projectLocalName != None) and (fromProject != None):
                self.cliObsLightManager.addRepos(projectLocalName=projectLocalName,
                                                 fromProject=fromProject)
            elif (projectLocalName != None) and (alias != None) and (url != None):
                self.cliObsLightManager.addRepos(projectLocalName=projectLocalName,
                                                 alias=alias,
                                                 repos=url)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)
                
        elif self.__isHelp(listArgv[0]):
            print  __HELP__
        else:
            raise ObsLightErr.ArgError("not a valid command for " + __COMMAND__)
        return 0 
        
        
