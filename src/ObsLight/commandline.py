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
import ObsLightPrintManager

MAN_HEADER = r"""

"""
MAN_FOOTER = r"""


"""

__PRGNAME__ = "ObsLight"
__getListObsServers__ = "getListObsServers"
__addObsServer__ = "addObsServer"
__getListLocalProject__ = "getListLocalProject"
__addProject__ = "addProject"
__getListPackage__ = "getListPackage"
__addPackage__ = "addPackage"
__createChRoot__ = "createChRoot"
__goToChRoot__ = "goToChRoot"
__addPackageSourceInChRoot__ = "addPackageSourceInChRoot"
__makePatch__ = "makePatch"
__addAndCommitChange__ = "addAndCommitChange"
__addRepoInChRoot__ = "addRepoInChRoot"


__DICO_HELP__ = {}
__DICO_HELP__[__getListObsServers__] = "Print the list of the OBS servers."
__DICO_HELP__[__getListLocalProject__] = "Print the list of the local project."
__DICO_HELP__[__getListPackage__] = "Print the list of the package of a project."
__DICO_HELP__[__addObsServer__] = "Add an OBS server."
__DICO_HELP__[__addProject__] = "Create a local project base from an existing project on a obs serveur"
__DICO_HELP__[__addPackage__] = "Create a local package in a local project, base from an existing package in project on a obs serveur"
__DICO_HELP__[__createChRoot__] = "create a chroot, build from a local project" 
__DICO_HELP__[__addPackageSourceInChRoot__] = "Install the source rpm of a package from the obs to the chroot of the project."    
__DICO_HELP__[__goToChRoot__] = "Open a bash into the chroot of a project."
__DICO_HELP__[__makePatch__] = "Generate the patch from a package from the chroot to local project." 
__DICO_HELP__[__addAndCommitChange__] = "Add, remove the file from local package and commit the package to the OBS."
__DICO_HELP__[__addRepoInChRoot__] = "Add a repo to zypper into the chroot of a project."



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
        
        self.cliObsLightManager = None

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
        exec the a list of argument.
        """
        __DESCRIPTION__ = "ObsLight:" + "\n"
        __DESCRIPTION__ += "\t" + "Provide a tool to manage a OBS project on your local machine" + "\n"
        __DESCRIPTION__ += "\t" + "For additional information, see" + "\n"
        __DESCRIPTION__ += "\t" + "* http://wiki.meego.com/OBS_Light" + "\n"
        
        
        __HELP__ = "Usage: " + __PRGNAME__ + "[global command] <command> [--command-options]" + "\n"
        __HELP__ += "\n"
        __HELP__ += "Type " + __PRGNAME__ + " <command> --help for help on a specific command." + "\n"
        __HELP__ += "Commandes:" + "\n"
        __HELP__ += "\n"
        __HELP__ += "\t" + __getListObsServers__ + ":" + "\t" + __DICO_HELP__[__getListObsServers__] + "\n"
        __HELP__ += "\t" + __getListLocalProject__ + ":" + "\t" + __DICO_HELP__[__getListLocalProject__] + "\n"
        __HELP__ += "\t" + __getListPackage__ + ":" + "\t\t" + __DICO_HELP__[__getListPackage__] + "\n"
        __HELP__ += "\n"
        __HELP__ += "\t" + __addObsServer__ + ":" + "\t\t" + __DICO_HELP__[__addObsServer__] + "\n"
        __HELP__ += "\t" + __addProject__ + ":" + "\t\t" + __DICO_HELP__[__addProject__] + "\n"
        __HELP__ += "\n"
        __HELP__ += "\t" + __addPackage__ + ":" + "\t\t" + __DICO_HELP__[__addPackage__] + "\n"
        __HELP__ += "\t" + __createChRoot__ + ":" + "\t\t" + __DICO_HELP__[__createChRoot__] + "\n"
        __HELP__ += "\t" + __addPackageSourceInChRoot__ + ":" + __DICO_HELP__[__addPackageSourceInChRoot__] + "\n"   
        __HELP__ += "\t" + __goToChRoot__ + ":" + "\t\t" + __DICO_HELP__[__goToChRoot__] + "\n"
        __HELP__ += "\t" + __makePatch__ + ":" + "\t\t" + __DICO_HELP__[__makePatch__] + "\n"
        __HELP__ += "\t" + __addAndCommitChange__ + ":" + "\t" + __DICO_HELP__[__addAndCommitChange__] + "\n"
        __HELP__ += "\t" + __addRepoInChRoot__ + ":" + "\t" + __DICO_HELP__[__addRepoInChRoot__] + "\n"
        __HELP__ += "\n"
        __HELP__ += "global command\n"
        __HELP__ += "\t" + "--verbose:" + "\t" + " Print all subprocess ouput." + "\n"
        __HELP__ += "\t" + "--debug:" + "\t" + " Print all subprocess command." + "\n"
        __HELP__ += "\n"
        __HELP__ += __DESCRIPTION__
        __HELP__ += "\n"
        
        
        if len(listArgv) == 0:
            ObsLightPrintManager.obsLightPrint(__DESCRIPTION__)
            return None
        elif len(listArgv) > 0:
            while(1):
                
                if (listArgv[0] == "--verbose"):
                    listArgv = listArgv[1:]
                    ObsLightPrintManager.VERBOSE = 1
                    continue
                if (listArgv[0] == "--debug"):
                    listArgv = listArgv[1:]
                    ObsLightPrintManager.DEBUG = 1
                    continue
                elif self.__isHelp(listArgv[0]):
                    ObsLightPrintManager.obsLightPrint(__HELP__)
                    return None
                elif (listArgv[0] == __getListObsServers__):
                    return self.getListObsServers(listArgv[1:])
                elif (listArgv[0] == __addObsServer__):
                    return self.addObsServer(listArgv[1:])
                elif (listArgv[0] == __getListLocalProject__):
                    return self.getListLocalProject(listArgv[1:])
                elif (listArgv[0] == __addProject__):
                    return self.addProject(listArgv[1:])
                elif (listArgv[0] == __getListPackage__):
                    return self.getListPackage(listArgv[1:])
                elif (listArgv[0] == __addPackage__):
                    return self.addPackage(listArgv[1:])
                elif (listArgv[0] == __createChRoot__):
                    return self.createChRoot(listArgv[1:])
                elif (listArgv[0] == __goToChRoot__):
                    return self.goToChRoot(listArgv[1:])
                elif (listArgv[0] == __addPackageSourceInChRoot__):
                    return self.addPackageSourceInChRoot(listArgv[1:])
                elif (listArgv[0] == __makePatch__):
                    return self.makePatch(listArgv[1:])
                elif (listArgv[0] == __addAndCommitChange__):
                    return self.addAndCommitChange(listArgv[1:])
                elif (listArgv[0] == __addRepoInChRoot__):
                    return self.addRepoInChRoot(listArgv[1:])
                else:
                    raise ObsLightErr.ArgError(listArgv[0] + " is not a valid command")
            
    def __isHelp(self, arg):
        '''
        Test if the arg is ["--help","-h","-help"]
        '''
        if arg  in ["--help", "-h", "-help", "help"]:
            return 1
        else:
            return 0   
        
        
    def getListLocalProject(self, listArgv):
        '''
        print the list of the name of the project. 
        '''
        __COMMAND__ = __getListLocalProject__
        __HELP__ = "usage: " + __PRGNAME__ + " getListLocalProject" + " \n"
        __HELP__ += "return the list of the local project." + " \n"        

        if len(listArgv) == 0: 
            result = self.cliObsLightManager.getListLocalProject()
            if not (len(result) == 0):
                for k in result:
                    ObsLightPrintManager.obsLightPrint(k)
            else:
                ObsLightPrintManager.obsLightPrint("No project")
        elif self.__isHelp(listArgv[0]):
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgError(listArgv[0] + " is not a valid command for " + __COMMAND__)
        return 0 
    
        
    def getListObsServers(self, listArgv):
        '''
        print the list of the name of the OBS Servers 
        '''
        __COMMAND__ = __getListObsServers__
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " \n"
        __HELP__ += __DICO_HELP__[__getListObsServers__]       

        if len(listArgv) == 0: 
            result = self.cliObsLightManager.getListObsServers()
            if not (len(result) == 0):
                for k in result:
                    ObsLightPrintManager.obsLightPrint(k)
            else:
                print "No OBS Server" 
        elif self.__isHelp(listArgv[0]):
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgError(listArgv[0] + " is not a valid command for " + __COMMAND__)
        return 0 
        
    def addObsServer(self, listArgv):
        '''
        add a OBS Server
        '''
        __COMMAND__ = __addObsServer__
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n" 
        __HELP__ += "\t--serverAPI api_url (require)\n"
        __HELP__ += "\t--user user_name (require)\n"
        __HELP__ += "\t--passw pwd_name (require)\n"
        __HELP__ += "\t--serverWeb web_url \n"
        __HELP__ += "\t--serverRepos repo_url (require)\n"
        __HELP__ += "\t--aliases name \n"
        __HELP__ += __DICO_HELP__[__COMMAND__]        

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
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgError("not a valid command for " + __COMMAND__)
        return 0 
         
        
    def addProject(self, listArgv):
        '''
        Add a project to Obs Light
        '''
        __COMMAND__ = __addProject__
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
        __HELP__ += __DICO_HELP__[__COMMAND__]
        
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
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgError("not a valid command for " + __COMMAND__)
        return 0 
    
    
    
    def getListPackage(self, listArgv):
        '''
        return the list of the package.
        '''
        __COMMAND__ = __getListPackage__
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n" 
        __HELP__ += "Commandes:" + "\n"
        __HELP__ += "\t" + "--obsServer serverName (if no serverName the projectLocalName is local)" + "\n"
        __HELP__ += "\t" + "--projectLocalName projectLocalName" + "\n"
        __HELP__ += "\t" + "--localPackage 1/0 (if the projectLocalName is local)" + "\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]
        
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
                    ObsLightPrintManager.obsLightPrint(pk)
            else:
                ObsLightPrintManager.obsLightPrint("No Package.")
                
        elif self.__isHelp(listArgv[0]):
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgError("not a valid command for " + __COMMAND__)
        return 0 



    def addPackage(self, listArgv):
        '''
        add a package.
        '''
        __COMMAND__ = __addPackage__
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectLocalName projectName" + "\n"
        __HELP__ += "\t" + "--package packageName" + "\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]
        
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
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgError("not a valid command for " + __COMMAND__)
        return 0 
    
    
    def createChRoot(self, listArgv):
        '''
        create a chroot
        '''
        __COMMAND__ = __createChRoot__
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectLocalName projectName" + "\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]
        
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
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgError("not a valid command for " + __COMMAND__)
        return 0 
        

        
    def goToChRoot(self, listArgv):
        '''
        open a bash in the chroot
        '''
        __COMMAND__ = __goToChRoot__
        
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectLocalName projectName" + "\n"
        __HELP__ += "\t" + "--package packageName" + "directly go to the BUILD directory of the package\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]
        
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
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgError("not a valid command for " + __COMMAND__ + "")
        return 0 
        
    def addPackageSourceInChRoot(self, listArgv):
        '''
        install a package source into a chroot, and make the spec %prep
        '''
        __COMMAND__ = __addPackageSourceInChRoot__
        
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectLocalName projectName (require)" + "\n"
        __HELP__ += "\t" + "--package packageName" + "\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]
        
        projectLocalName = None
        package = None
        
        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (2 * 2)): 
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--projectLocalName":
                    projectLocalName = listArgv[i + 1]
                elif listArgv[i] == "--package":
                    package = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgError("unknown command '" + listArgv[i] + "' for " + __COMMAND__)
            if (projectLocalName != None) and (package != None):
                self.cliObsLightManager.addPackageSourceInChRoot(projectLocalName=projectLocalName,
                                                                 package=package)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)
                
        elif self.__isHelp(listArgv[0]):
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgError("not a valid command for " + __COMMAND__)
        return 0 
        

    def makePatch(self, listArgv):
        '''
        generate a patch 
        '''
        __COMMAND__ = __makePatch__
        
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectLocalName projectName (require)" + "\n"
        __HELP__ += "\t" + "--package packageName (require)" + "\n"
        __HELP__ += "\t" + "--patch patchName (require)" + "\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]
        
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
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgError("not a valid command for " + __COMMAND__)
        return 0 
        
        
    def addAndCommitChange(self, listArgv):
        '''
        add/delete file in a osc directory. 
        '''
        __COMMAND__ = __addAndCommitChange__
        
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectLocalName projectName (require)" + "\n"
        __HELP__ += "\t" + "--package packageName (require)" + "\n"
        __HELP__ += "\t" + "--message (-m) message(require)" + "\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]
        
        projectLocalName = None
        package = None
        message = None

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (3 * 2)): 
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--projectLocalName":
                    projectLocalName = listArgv[i + 1]
                elif listArgv[i] == "--package":
                    package = listArgv[i + 1]
                elif listArgv[i] in ("--message", "-m"):
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
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgError("not a valid command for " + __COMMAND__)
        return 0 
        
    def addRepoInChRoot(self, listArgv):
        '''
        add a repo in zypper in the chroot
        '''
        __COMMAND__ = __addRepoInChRoot__
        
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--fromProject projectName " + "\n"
        __HELP__ += "\t" + "--projectLocalName projectName (require)" + "\n"
        __HELP__ += "\t" + "--alias message" + "\n"
        __HELP__ += "\t" + "--url message" + "\n"
        __HELP__ += "\t" + "if --fromProject is specified, --alias and --url are ignored" + "\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]
        
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
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgError("not a valid command for " + __COMMAND__)
        return 0 
        
        
