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

@author: Ronan Le Martret
'''

import sys

from util import safewriter
import ObsLightErr
import ObsLightManager
import ObsLightPrintManager

MAN_HEADER = r"""

"""
MAN_FOOTER = r"""


"""

__PRGNAME__ = "ObsLight"
__getListObsServers__ = "getObsServerList"
__addObsServer__ = "addObsServer"
__getListLocalProject__ = "getLocalProjectList"
__addProject__ = "addProject"
__getListPackage__ = "getPackageList"
__addPackage__ = "addPackage"
__createChRoot__ = "createChRoot"
__goToChRoot__ = "goToChRoot"
__addPackageSourceInChRoot__ = "addPackageSourceInChRoot"
__makePatch__ = "makePatch"
__addAndCommitChange__ = "addAndCommitChanges"
__addRepoInChRoot__ = "addRepoInChRoot"


__DICO_HELP__ = {}
__DICO_HELP__[__getListObsServers__] = "Print the list of OBS servers."
__DICO_HELP__[__getListLocalProject__] = "Print the list of local projects."
__DICO_HELP__[__getListPackage__] = "Print the list of packages of a project."
__DICO_HELP__[__addObsServer__] = "Add an OBS server."
__DICO_HELP__[__addProject__] = "Create a local project based on an existing project on an OBS server."
__DICO_HELP__[__addPackage__] = "Create a local package in a local project, based on an existing package in a project on an OBS server."
__DICO_HELP__[__createChRoot__] = "Create a chroot, built from a local project." 
__DICO_HELP__[__addPackageSourceInChRoot__] = "Install the source RPM of a package into the chroot of the project."    
__DICO_HELP__[__goToChRoot__] = "Open a bash in the chroot of a project."
__DICO_HELP__[__makePatch__] = "Generate a patch with modifications made in the chroot of a local project." 
__DICO_HELP__[__addAndCommitChange__] = "Add the new files (including patches) and commit them to the OBS"
__DICO_HELP__[__addRepoInChRoot__] = "Add a repository to the chroot's zypper configuration file."



class ObsLight():
    """
    
    """

    man_header = MAN_HEADER
    man_footer = MAN_FOOTER

    def __init__(self):
        '''
        
        '''
        sys.stderr = safewriter.SafeWriter(sys.stderr)
        sys.stdout = safewriter.SafeWriter(sys.stdout)

        self.__listArgv = sys.argv[1:]
        
        self.cliObsLightManager = None

    def main(self):
        """
        Execute the main list of arguments
        """

        self.cliObsLightManager = ObsLightManager.myObsLightManager
        
        while ("," in self.__listArgv):
            
            ll = self.__listArgv[:self.__listArgv.index(",")]
            self.__listArgv = self.__listArgv[self.__listArgv.index(",") + 1:]
            self.execute(ll)

        return self.execute(self.__listArgv)
    
    def setListArgv(self, arg):
        """
        Set the main list of arguments.
        You can set many lists of args separated by " , "
        """
        self.__listArgv = arg


    def execute(self, listArgv):
        """
        Execute a list of arguments.
        """
        __DESCRIPTION__ = "ObsLight:" + "\n"
        __DESCRIPTION__ += "\t" + "Provides a tool to manage an OBS project on your local machine" + "\n"
        __DESCRIPTION__ += "\t" + "For additional informations, see" + "\n"
        __DESCRIPTION__ += "\t" + "* http://wiki.meego.com/OBS_Light" + "\n"
        
        
        __HELP__ = "Usage: " + __PRGNAME__ + " [global command] <command> [--command-options]" + "\n"
        __HELP__ += "\n"
        __HELP__ += "Type " + __PRGNAME__ + " <command> --help to get help on a specific command." + "\n"
        __HELP__ += "Commands:" + "\n"
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
        __HELP__ += "global commands\n"
        __HELP__ += "\t" + "--verbose:" + "\t" + " Print all subprocess outputs." + "\n"
        __HELP__ += "\t" + "--debug:" + "\t" + " Print all subprocess commands." + "\n"
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
                    return self.getObsServerList(listArgv[1:])
                elif (listArgv[0] == __addObsServer__):
                    return self.addObsServer(listArgv[1:])
                elif (listArgv[0] == __getListLocalProject__):
                    return self.getLocalProjectList(listArgv[1:])
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
                    return self.addAndCommitChanges(listArgv[1:])
                elif (listArgv[0] == __addRepoInChRoot__):
                    return self.addRepoInChRoot(listArgv[1:])
                else:
                    raise ObsLightErr.ArgError(listArgv[0] + " is not a valid command")
            
    def __isHelp(self, arg):
        '''
        Test if the argument is "--help", "-h" or "-help"
        '''
        return arg in ["--help", "-h", "-help", "help"]


    def getLocalProjectList(self, listArgv):
        '''
        Print the list of local projects. 
        '''
        __COMMAND__ = __getListLocalProject__
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " \n"
        __HELP__ += __DICO_HELP__[__COMMAND__]

        if len(listArgv) == 0:
            result = self.cliObsLightManager.getLocalProjectList()
            if len(result) > 0:
                for k in result:
                    ObsLightPrintManager.obsLightPrint(k)
            else:
                ObsLightPrintManager.obsLightPrint("No project")
        elif self.__isHelp(listArgv[0]):
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0 
    
        
    def getObsServerList(self, listArgv):
        '''
        Print the list OBS servers. 
        '''
        __COMMAND__ = __getListObsServers__
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " \n"
        __HELP__ += __DICO_HELP__[__getListObsServers__]       

        if len(listArgv) == 0: 
            result = self.cliObsLightManager.getObsServerList()
            if len(result) > 0:
                for k in result:
                    ObsLightPrintManager.obsLightPrint(k)
            else:
                print "No OBS server" 
        elif self.__isHelp(listArgv[0]):
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0 
        
    def addObsServer(self, listArgv):
        '''
        Add an OBS Server
        '''
        __COMMAND__ = __addObsServer__
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options]\n" 
        __HELP__ += "\t--serverApi api_url (required)\n"
        __HELP__ += "\t--user user_name (required)\n"
        __HELP__ += "\t--password password (required)\n"
        __HELP__ += "\t--serverWeb web_url\n"
        __HELP__ += "\t--serverRepo repo_url (required)\n"
        __HELP__ += "\t--alias name\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]        

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (6 * 2)): 
            serverWeb = ""
            serverApi = None
            serverRepo = ""
            alias = None
            user = None
            password = None
            
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--serverWeb":
                    serverWeb = listArgv[i + 1]
                elif listArgv[i] == "--serverApi":
                    serverApi = listArgv[i + 1]
                elif listArgv[i] == "--serverRepo":
                    serverRepo = listArgv[i + 1]
                elif listArgv[i] == "--alias":
                    alias = listArgv[i + 1] 
                elif listArgv[i] == "--user":
                    user = listArgv[i + 1]
                elif listArgv[i] == "--password":
                    password = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])

            self.cliObsLightManager.addObsServer(serverWeb=serverWeb,
                                                 serverAPI=serverApi,
                                                 serverRepos=serverRepo,
                                                 aliases=alias,
                                                 user=user,
                                                 passw=password)
            
        elif self.__isHelp(listArgv[0]):
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0 
         
        
    def addProject(self, listArgv):
        '''
        Add a project to OBS Light.
        '''
        __COMMAND__ = __addProject__
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t--projectLocalName name: if no name is defined, the projectLocalName is equal to projectObsName, the ':' characters are replaced by '_'\n"
        __HELP__ += "\t--projectObsName name (required)\n"
        __HELP__ += "\t--projectTitle title\n"
        __HELP__ += "\t--projectDirectory path\n"
        __HELP__ += "\t--chrootDirectory path\n"
        __HELP__ += "\t--obsServer api_url|alias (require)\n"
        __HELP__ += "\t--projectTarget name\n"
        __HELP__ += "\t--description description\n"
        __HELP__ += "\t--projectArch architecture\n"
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
                elif listArgv[i] == "--projectArch":
                    projectArchitecture = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])

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
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0 
    

    def getListPackage(self, listArgv):
        '''
        Print the list of packages of a project.
        '''
        __COMMAND__ = __getListPackage__
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n" 
        __HELP__ += "Commands:" + "\n"
        __HELP__ += "\t" + "--obsServer serverName (if no serverName, the projectLocalName is local)" + "\n"
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
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])
                
            if (obsServer != None) and (projectLocalName != None):
                res = self.cliObsLightManager.getObsProjectPackageList(obsServer=obsServer,
                                                                           projectLocalName=projectLocalName)
            elif (projectLocalName != None) and (localPackage in ["0", "1"]):
                res = self.cliObsLightManager.getLocalProjectPackageList(name=projectLocalName,
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
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0


    def addPackage(self, listArgv):
        '''
        Add a package to a project.
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
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])
                
            if (projectLocalName != None) and (package != None):
                self.cliObsLightManager.addPackage(projectLocalName=projectLocalName  ,
                                                   package=package)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)
                
        elif self.__isHelp(listArgv[0]):
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0 
    
    
    def createChRoot(self, listArgv):
        '''
        Create a chroot.
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
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])
                
            if (projectLocalName != None):
                self.cliObsLightManager.createChRoot(projectLocalName=projectLocalName)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)
                
        elif self.__isHelp(listArgv[0]):
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0 
        

        
    def goToChRoot(self, listArgv):
        '''
        Open a bash in the chroot.
        '''
        __COMMAND__ = __goToChRoot__
        
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectLocalName projectName (required)\n"
        __HELP__ += "\t" + "--package packageName\t" + "directly go to the BUILD directory of the package\n"
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
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])
                
            if (projectLocalName != None):
                self.cliObsLightManager.goToChRoot(projectLocalName=projectLocalName,
                                                   package=package)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__ + "")
                
        elif self.__isHelp(listArgv[0]):
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0 
        
    def addPackageSourceInChRoot(self, listArgv):
        '''
        Install a source package in the chroot, and execute the %prep section of the spec file.
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
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])
            if (projectLocalName != None) and (package != None):
                self.cliObsLightManager.addPackageSourceInChRoot(projectLocalName=projectLocalName,
                                                                 package=package)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)
                
        elif self.__isHelp(listArgv[0]):
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0
        

    def makePatch(self, listArgv):
        '''
        Generate a patch from the modifications made in the chroot.
        '''
        __COMMAND__ = __makePatch__
        
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectLocalName projectName (required)" + "\n"
        __HELP__ += "\t" + "--package packageName (required)" + "\n"
        __HELP__ += "\t" + "--patch patchName (required)" + "\n"
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
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])

            if (projectLocalName != None) and (package != None) and (patch != None):
                self.cliObsLightManager.makePatch(projectLocalName=projectLocalName,
                                                  package=package,
                                                  patch=patch)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)
                
        elif self.__isHelp(listArgv[0]):
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0 
        
        
    def addAndCommitChanges(self, listArgv):
        '''
        Add/delete files in an osc directory, and commit modifications to the OBS. 
        '''
        __COMMAND__ = __addAndCommitChange__
        
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectLocalName projectName (required)" + "\n"
        __HELP__ += "\t" + "--package packageName (required)" + "\n"
        __HELP__ += "\t" + "--message (-m) message(required)" + "\n"
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
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])
            if (message == None):
                raise ObsLightErr.ArgError("No message for " + __COMMAND__)
            elif (projectLocalName != None) and (package != None) :
                self.cliObsLightManager.addAndCommitChanges(projectLocalName=projectLocalName,
                                                           package=package, message=message)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)
                
        elif self.__isHelp(listArgv[0]):
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0 
        
    def addRepoInChRoot(self, listArgv):
        '''
        Add a repository in chroot's zypper configuration file.
        '''
        __COMMAND__ = __addRepoInChRoot__
        
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--fromProject projectName " + "\n"
        __HELP__ += "\t" + "--projectLocalName projectName (required)" + "\n"
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
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])
            if (projectLocalName != None) and (fromProject != None):
                self.cliObsLightManager.addRepo(projectLocalName=projectLocalName,
                                                 fromProject=fromProject)
            elif (projectLocalName != None) and (alias != None) and (url != None):
                self.cliObsLightManager.addRepo(projectLocalName=projectLocalName,
                                                 alias=alias,
                                                 repos=url)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)
                
        elif self.__isHelp(listArgv[0]):
            ObsLightPrintManager.obsLightPrint(__HELP__)
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0 
        
        
