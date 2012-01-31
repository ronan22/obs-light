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
__delObsServer__ = "delObsServer"
__getListLocalProject__ = "getLocalProjectList"
__addProject__ = "addProject"
__removeProject__ = "removeProject"
__removePackage__ = "removePackage"
__getListPackage__ = "getPackageList"
__addPackage__ = "addPackage"

__createChRoot__ = "createChRoot"
__goToChRoot__ = "goToChRoot"

__addPackageSourceInChRoot__ = "addPackageSourceInChRoot"
__makePatch__ = "makePatch"
__addAndCommitChange__ = "addAndCommitChanges"
__addRepoInChRoot__ = "addRepoInChRoot"
__exportProject__ = "exportProject"
__importProject__ = "importProject"
__getWebProjectPage__ = "getWebProjectPage"

__addMicProjects__ = "addMicProjects"
__delMicProjects__ = "delMicProjects"
__addKickstartFile__ = "setKickstartFile"
__getKickstartFile__ = "getKickstartFile"
__getMicProjectArchitecture__ = "getMicProjectArchitecture"
__setMicProjectArchitecture__ = "setMicProjectArchitecture"
__setMicProjectImageType__ = "setMicProjectImageType"
__getMicProjectImageType__ = "getMicProjectImageType"
__createImage__ = "createImage"
__getMicProjectList__ = "getMicProjectList"


__info_quiet__ = "--quiet"
__info_debug__ = "--debug"
__version__ = "--version"

__DICO_HELP__ = {}
__DICO_HELP__[__getListObsServers__] = "Print the list of OBS servers."
__DICO_HELP__[__getListLocalProject__] = "Print the list of local projects."
__DICO_HELP__[__getListPackage__] = "Print the list of packages of a project."
__DICO_HELP__[__addObsServer__] = "Add an OBS server."
__DICO_HELP__[__delObsServer__] = "Del an OBS server."

__DICO_HELP__[__addProject__] = "Create a local project based on an existing project on an OBS server."
__DICO_HELP__[__addPackage__] = "Create a local package in a local project, based on an existing package in a project on an OBS server."
__DICO_HELP__[__createChRoot__] = "Create a chroot, built from a local project."
__DICO_HELP__[__addPackageSourceInChRoot__] = "Install the source RPM of a package into the chroot of the project."
__DICO_HELP__[__goToChRoot__] = "Open a bash in the chroot of a project."
__DICO_HELP__[__makePatch__] = "Generate a patch with modifications made in the chroot of a local project."
__DICO_HELP__[__addAndCommitChange__] = "Add the new files (including patches) and commit them to the OBS"
__DICO_HELP__[__addRepoInChRoot__] = "Add a repository to the chroot's zypper configuration file."
__DICO_HELP__[__removeProject__] = "Remove local project"
__DICO_HELP__[__removePackage__] = "Remove local package from a local project"
__DICO_HELP__[__exportProject__] = "save a Project into a path"
__DICO_HELP__[__importProject__] = "import a Project from a file"
__DICO_HELP__[__getWebProjectPage__] = "return the web URL of a project."

__DICO_HELP__[__getMicProjectList__] = "Return the Mic project list."
__DICO_HELP__[__addMicProjects__] = "Add a Mic project."
__DICO_HELP__[__delMicProjects__] = "Del a Mic project."
__DICO_HELP__[__addKickstartFile__] = "Add a ks file to a Mic project."
__DICO_HELP__[__getKickstartFile__ ] = "Get the ks file of the Mic project."
__DICO_HELP__[__getMicProjectArchitecture__] = "return the architecture of a Mic project."
__DICO_HELP__[__setMicProjectArchitecture__] = "Set the architecture of the Mic project."
__DICO_HELP__[__setMicProjectImageType__] = "Set the image type of the  Mic project."
__DICO_HELP__[__getMicProjectImageType__] = "Return the image type of the  Mic project."
__DICO_HELP__[__createImage__] = "Create the image of the Mic project."

__DICO_OPTION_HELP__ = {}
__DICO_OPTION_HELP__[__info_quiet__] = "Print no outputs."
__DICO_OPTION_HELP__[__info_debug__] = "Print all outputs."
__DICO_OPTION_HELP__[__version__] = "print the obslight version number and exit"

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

    def main(self):
        """
        Execute the main list of arguments
        """
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
        __DESCRIPTION__ += "\t" + "Provides a tool to manage an OBS project on your local machine in command line" + "\n"
        __DESCRIPTION__ += "\t" + "For informations, see the help section" + "\n"
        __DESCRIPTION__ += "\t\t" + "obslight --help" + "\n"
        __DESCRIPTION__ += "\t" + "The gui for obslight is obslightgui" + "\n"
        __DESCRIPTION__ += "\t" + "A FAQ is available at:" + "\n"
        __DESCRIPTION__ += "\t\t" + "*http://wiki.meego.com/OBS_Light_FAQ" + "\n"
        __DESCRIPTION__ += "\t" + "For additional informations, see:" + "\n"
        __DESCRIPTION__ += "\t\t" + "* http://wiki.meego.com/OBS_Light" + "\n"

        __HELP__ = "Usage: " + __PRGNAME__ + " [global command] <command> [--command-options]" + "\n"
        __HELP__ += "\n"
        __HELP__ += "Type " + __PRGNAME__ + " <command> --help to get help on a specific command." + "\n"
        __HELP__ += "Commands:" + "\n"
        __HELP__ += "\n"
        __HELP__ += "\t" + __getListLocalProject__ + ":" + "\t" + __DICO_HELP__[__getListLocalProject__] + "\n"
        __HELP__ += "\t" + __getListPackage__ + ":" + "\t\t" + __DICO_HELP__[__getListPackage__] + "\n"
        __HELP__ += "\n"
        __HELP__ += "\t" + __getListObsServers__ + ":" + "\t" + __DICO_HELP__[__getListObsServers__] + "\n"
        __HELP__ += "\t" + __addObsServer__ + ":" + "\t\t" + __DICO_HELP__[__addObsServer__] + "\n"
        __HELP__ += "\t" + __delObsServer__ + ":" + "\t\t" + __DICO_HELP__[__delObsServer__] + "\n"
        __HELP__ += "\n"
        __HELP__ += "\t" + __addProject__ + ":" + "\t\t" + __DICO_HELP__[__addProject__] + "\n"
        __HELP__ += "\t" + __exportProject__ + ":" + "\t\t" + __DICO_HELP__[__exportProject__] + "\n"
        __HELP__ += "\t" + __importProject__ + ":" + "\t\t" + __DICO_HELP__[__importProject__] + "\n"
        __HELP__ += "\t" + __getWebProjectPage__ + ":" + "\t\t" + __DICO_HELP__[__getWebProjectPage__] + "\n"
        __HELP__ += "\n"
        __HELP__ += "\t" + __removeProject__ + ":" + "\t\t" + __DICO_HELP__[__removeProject__] + "\n"
        __HELP__ += "\t" + __removePackage__ + ":" + "\t\t" + __DICO_HELP__[__removePackage__] + "\n"
        __HELP__ += "\n"
        __HELP__ += "\t" + __addPackage__ + ":" + "\t\t" + __DICO_HELP__[__addPackage__] + "\n"
        __HELP__ += "\t" + __createChRoot__ + ":" + "\t\t" + __DICO_HELP__[__createChRoot__] + "\n"
        __HELP__ += "\t" + __addPackageSourceInChRoot__ + ":" + __DICO_HELP__[__addPackageSourceInChRoot__] + "\n"
        __HELP__ += "\t" + __goToChRoot__ + ":" + "\t\t" + __DICO_HELP__[__goToChRoot__] + "\n"
        __HELP__ += "\t" + __makePatch__ + ":" + "\t\t" + __DICO_HELP__[__makePatch__] + "\n"
        __HELP__ += "\t" + __addAndCommitChange__ + ":" + "\t" + __DICO_HELP__[__addAndCommitChange__] + "\n"
        __HELP__ += "\t" + __addRepoInChRoot__ + ":" + "\t" + __DICO_HELP__[__addRepoInChRoot__] + "\n"
        __HELP__ += "\n"
        __HELP__ += "\t" + __getMicProjectList__ + ":" + "\t" + __DICO_HELP__[__getMicProjectList__] + "\n"
        __HELP__ += "\t" + __addMicProjects__ + ":" + "\t\t" + __DICO_HELP__[__addMicProjects__] + "\n"
        __HELP__ += "\t" + __delMicProjects__ + ":" + "\t\t" + __DICO_HELP__[__delMicProjects__] + "\n"
        __HELP__ += "\t" + __addKickstartFile__ + ":" + "\t" + __DICO_HELP__[__addKickstartFile__] + "\n"
        __HELP__ += "\t" + __getKickstartFile__ + ":" + "\t" + __DICO_HELP__[__getKickstartFile__ ] + "\n"
        __HELP__ += "\t" + __getMicProjectArchitecture__ + ":" + "\t" + __DICO_HELP__[__getMicProjectArchitecture__] + "\n"
        __HELP__ += "\t" + __setMicProjectArchitecture__ + ":" + "" + __DICO_HELP__[__setMicProjectArchitecture__] + "\n"
        __HELP__ += "\t" + __setMicProjectImageType__ + ":" + "\t" + __DICO_HELP__[__setMicProjectImageType__] + "\n"
        __HELP__ += "\t" + __getMicProjectImageType__ + ":" + "\t" + __DICO_HELP__[__getMicProjectImageType__] + "\n"
        __HELP__ += "\t" + __createImage__ + ":" + "\t\t" + __DICO_HELP__[__createImage__] + "\n"
        __HELP__ += "\n"
        __HELP__ += "\t" + __version__ + ":" + "\t" + __DICO_OPTION_HELP__[__version__] + "\n"
        __HELP__ += "\n"
        __HELP__ += "global commands\n"
        __HELP__ += "\t" + __info_quiet__ + ":" + "\t" + __DICO_OPTION_HELP__[__info_quiet__] + "\n"
        __HELP__ += "\t" + __info_debug__ + ":" + "\t" + __DICO_OPTION_HELP__[__info_debug__] + "\n"
        __HELP__ += "\n"
        __HELP__ += __DESCRIPTION__
        __HELP__ += "\n"

        ObsLightPrintManager.quiet = 0
        ObsLightPrintManager.DEBUG = 0
        if len(listArgv) == 0:
            print __DESCRIPTION__
            return None
        elif len(listArgv) > 0:
            while(1):
                if (listArgv[0] == __info_quiet__):
                    listArgv = listArgv[1:]
                    ObsLightPrintManager.QUIET = 1
                    ObsLightPrintManager.setLoggerLevel('CRITICAL')
                    continue
                elif (listArgv[0] == __info_debug__):
                    listArgv = listArgv[1:]
                    ObsLightPrintManager.DEBUG += 1
                    ObsLightPrintManager.setLoggerLevel('DEBUG')
                    continue
                elif (listArgv[0] == __version__):
                    listArgv = listArgv[1:]
                    print "OBS Light version", ObsLightManager.getVersion()
                    return None
                elif self.__isHelp(listArgv[0]):
                    if ObsLightPrintManager.DEBUG == 0:
                        print __HELP__
                        return None
                    elif ObsLightPrintManager.DEBUG == 1:
                        for k in __DICO_HELP__.keys():
                            print k
                        return None
                    elif ObsLightPrintManager.DEBUG == 2:
                        for k in __DICO_OPTION_HELP__.keys():
                            print k
                        return None
                    elif ObsLightPrintManager.DEBUG == 3:
                        for k in __DICO_HELP__.keys():
                            print k
                        for k in __DICO_OPTION_HELP__.keys():
                            print k
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
                elif (listArgv[0] == __removeProject__):
                    return self.removeProject(listArgv[1:])
                elif (listArgv[0] == __removePackage__):
                    return self.removePackage(listArgv[1:])
                elif (listArgv[0] == __exportProject__):
                    return self.exportProject(listArgv[1:])
                elif (listArgv[0] == __importProject__):
                    return self.importProject(listArgv[1:])
                elif (listArgv[0] == __getWebProjectPage__):
                    return self.getWebProjectPage(listArgv[1:])
                elif (listArgv[0] == __delObsServer__):
                    return self.delObsServer(listArgv[1:])
                elif (listArgv[0] == __getMicProjectList__):
                    return self.getMicProjectList(listArgv[1:])
                elif (listArgv[0] == __addMicProjects__):
                    return self.addMicProjects(listArgv[1:])
                elif (listArgv[0] == __delMicProjects__):
                    return self.delMicProjects(listArgv[1:])
                elif (listArgv[0] == __addKickstartFile__):
                    return self.setKickstartFile(listArgv[1:])
                elif (listArgv[0] == __getKickstartFile__):
                    return self.getKickstartFile(listArgv[1:])
                elif (listArgv[0] == __getMicProjectArchitecture__):
                    return self.getMicProjectArchitecture(listArgv[1:])
                elif (listArgv[0] == __setMicProjectArchitecture__):
                    return self.setMicProjectArchitecture(listArgv[1:])
                elif (listArgv[0] == __setMicProjectImageType__):
                    return self.setMicProjectImageType(listArgv[1:])
                elif (listArgv[0] == __getMicProjectImageType__):
                    return self.getMicProjectImageType(listArgv[1:])
                elif (listArgv[0] == __createImage__):
                    return self.createImage(listArgv[1:])
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
            result = ObsLightManager.getManager().getLocalProjectList()
            if len(result) > 0:
                for k in result:
                    print k
            else:
                print "No project"
        elif self.__isHelp(listArgv[0]):
            print __HELP__
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
            result = ObsLightManager.getManager().getObsServerList()
            if len(result) > 0:
                for k in result:
                    print k
            else:
                print "No OBS server"
        elif self.__isHelp(listArgv[0]):
            print __HELP__
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

            ObsLightManager.getManager().addObsServer(serverWeb=serverWeb,
                                                      serverApi=serverApi,
                                                      serverRepo=serverRepo,
                                                      alias=alias,
                                                      user=user,
                                                      password=password)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
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
        __HELP__ += "\t--obsServer api_url|alias (require)\n"
        __HELP__ += "\t--projectTarget name\n"
        __HELP__ += "\t--description description\n"
        __HELP__ += "\t--projectArch architecture\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (7 * 2)):
            projectLocalName = None
            projectObsName = None
            projectTitle = None
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

            ObsLightManager.getManager().addProject(projectLocalName=projectLocalName,
                                                    projectObsName=projectObsName,
                                                    projectTitle=projectTitle,
                                                    serverApi=obsServer ,
                                                    projectTarget=projectTarget,
                                                    description=description,
                                                    projectArchitecture=projectArchitecture)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0

    def delObsServer(self, listArgv):
        '''
        Add a project to OBS Light.
        '''
        __COMMAND__ = __addProject__
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t--obsServer alias (require)\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (1 * 2)):
            obsServer = None

            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--obsServer":
                    obsServer = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])

            ObsLightManager.getManager().delObsServer(obsServer=obsServer)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
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
                res = ObsLightManager.getManager().getObsProjectPackageList(serverApi=obsServer,
                                                                           projectObsName=projectLocalName)
            elif (projectLocalName != None) and (localPackage in ["0", "1"]):
                res = ObsLightManager.getManager().getLocalProjectPackageList(projectLocalName=projectLocalName,
                                                                             local=int(localPackage))
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

            if res is not None and len(res) > 0:
                for pk in res:
                    print pk
            else:
                print "No Package."

        elif self.__isHelp(listArgv[0]):
            print __HELP__
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
                ObsLightManager.getManager().addPackage(projectLocalName=projectLocalName  ,
                                                   package=package)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
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
                ObsLightManager.getManager().createChRoot(projectLocalName=projectLocalName)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
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
                ObsLightManager.getManager().goToChRoot(projectLocalName=projectLocalName,
                                                   package=package)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__ + "")

        elif self.__isHelp(listArgv[0]):
            print __HELP__
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
                ObsLightManager.getManager().addPackageSourceInChRoot(projectLocalName=projectLocalName,
                                                                 package=package)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
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
                ObsLightManager.getManager().makePatch(projectLocalName=projectLocalName,
                                                  package=package,
                                                  patch=patch)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
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
                ObsLightManager.getManager().addAndCommitChanges(projectLocalName=projectLocalName,
                                                           package=package, message=message)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
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
                ObsLightManager.getManager().addRepo(projectLocalName=projectLocalName,
                                                 fromProject=fromProject)
            elif (projectLocalName != None) and (alias != None) and (url != None):
                ObsLightManager.getManager().addRepo(projectLocalName=projectLocalName,
                                                 alias=alias,
                                                 repoUrl=url)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0

    def removeProject(self, listArgv):
        '''
        
        '''
        __COMMAND__ = __removeProject__

        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectLocalName projectName (required)" + "\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]

        projectLocalName = None

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (1 * 2)):
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--projectLocalName":
                    projectLocalName = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])
            if (projectLocalName != None):
                ObsLightManager.getManager().removeProject(projectLocalName=projectLocalName)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0

    def removePackage(self, listArgv):
        '''
        
        '''
        __COMMAND__ = __removeProject__

        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectLocalName projectName (required)" + "\n"
        __HELP__ += "\t" + "--package packageName (required)" + "\n"
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
                ObsLightManager.getManager().removePackage(projectLocalName=projectLocalName, package=package)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0


    def exportProject(self, listArgv):
        '''
        Export a project to a file.
        '''
        __COMMAND__ = __exportProject__

        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectLocalName projectName (required)" + "\n"
        __HELP__ += "\t" + "--path file (required)" + "\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]

        projectLocalName = None
        path = None

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (2 * 2)):
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--projectLocalName":
                    projectLocalName = listArgv[i + 1]
                elif listArgv[i] == "--path":
                    path = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])

            if (projectLocalName != None) and (path != None):
                ObsLightManager.getManager().exportProject(projectLocalName=projectLocalName, path=path)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0


    def importProject(self, listArgv):
        '''
        Import a project from a file.
        '''
        __COMMAND__ = __importProject__
        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--path file (required)" + "\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]
        path = None
        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (1 * 2)):
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--path":
                    path = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])
            if  (path != None):
                ObsLightManager.getManager().importProject(filePath=path)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0

    def getWebProjectPage(self, listArgv):
        '''
        return the Web url of an OBS project for a local project.
        '''
        __COMMAND__ = __getWebProjectPage__

        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectLocalName projectName (required)" + "\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]

        projectLocalName = None

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (1 * 2)):
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--projectLocalName":
                    projectLocalName = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])
            if (projectLocalName != None):

                print ObsLightManager.getManager().getProjectWebPage(projectLocalName=projectLocalName)

            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0

    def getMicProjectList(self, listArgv):
        '''
        return the Mic project list.
        '''
        __COMMAND__ = __getMicProjectList__

        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " \n"
        __HELP__ += __DICO_HELP__[__COMMAND__]

        if len(listArgv) == 0:

            res = ObsLightManager.getManager().getMicProjectList()

            if len(res) > 0:
                for r in res:
                    print "\t" + r
            else:
                print "No Mic project."
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0

    def addMicProjects(self, listArgv):
        '''
        add a Mic Project to obslight.
        '''
        __COMMAND__ = __addMicProjects__

        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--micProjectName projectName" + "\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]

        micProjectName = None

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (1 * 2)):
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--micProjectName":
                    micProjectName = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])
            if (micProjectName != None):
                ObsLightManager.getManager().addMicProjects(micProjectName=micProjectName)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0

    def delMicProjects(self, listArgv):
        '''
        Del a Mic Project to obslight.
        '''
        __COMMAND__ = __delMicProjects__

        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--micProjectName projectName" + "\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]

        micProjectName = None

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (1 * 2)):
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--micProjectName":
                    micProjectName = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])
            if (micProjectName != None):
                ObsLightManager.getManager().delMicProjects(micProjectName=micProjectName)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0

    def setKickstartFile(self, listArgv):
        '''
        Add a ks file to the Mic Project.
        '''
        __COMMAND__ = __addKickstartFile__

        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--micProjectName projectName" + "\n"
        __HELP__ += "\t" + "--filePath aPath" + "\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]

        micProjectName = None
        filePath = None

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (2 * 2)):
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--micProjectName":
                    micProjectName = listArgv[i + 1]
                elif listArgv[i] == "--filePath":
                    filePath = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])
            if (micProjectName != None) and (filePath != None):
                ObsLightManager.getManager().setKickstartFile(micProjectName=micProjectName,
                                                              filePath=filePath)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0

    def getKickstartFile(self, listArgv):
        '''
        Return the ks file of the Mic Project .
        '''
        __COMMAND__ = __getKickstartFile__

        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--micProjectName projectName" + "\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]

        micProjectName = None

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (1 * 2)):
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--micProjectName":
                    micProjectName = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])
            if (micProjectName != None):
                res = ObsLightManager.getManager().getKickstartFile(micProjectName=micProjectName)
                if res == None:
                    print "No kickstart file."
                else:
                    print "\t" + res
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0

    def setMicProjectArchitecture(self, listArgv):
        '''
        set Architecture to the Mic Project.
        '''
        __COMMAND__ = __setMicProjectArchitecture__

        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--micProjectName projectName" + "\n"
        __HELP__ += "\t" + "--arch arch" + "\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]

        micProjectName = None
        arch = None

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (2 * 2)):
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--micProjectName":
                    micProjectName = listArgv[i + 1]
                elif listArgv[i] == "--arch":
                    arch = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])
            if (micProjectName != None) and (arch != None):
                ObsLightManager.getManager().setMicProjectArchitecture(micProjectName=micProjectName,
                                                                       arch=arch)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0

    def getMicProjectArchitecture(self, listArgv):
        '''
        Return the architecture of the Mic Project.
        '''
        __COMMAND__ = __getMicProjectArchitecture__

        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--micProjectName projectName" + "\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]

        micProjectName = None

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (1 * 2)):
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--micProjectName":
                    micProjectName = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])
            if (micProjectName != None):
                res = ObsLightManager.getManager().getMicProjectArchitecture(micProjectName=micProjectName)
                if res == None:
                    print "No Architecture Define."
                else:
                    print "\t" + res
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0

    def setMicProjectImageType(self, listArgv):
        '''
        set image type to the Mic Project.
        '''
        __COMMAND__ = __setMicProjectArchitecture__

        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectMicName projectName" + "\n"
        __HELP__ += "\t" + "--imageType imageType" + "\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]

        projectMicName = None
        imageType = None

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (2 * 2)):
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--projectMicName":
                    projectMicName = listArgv[i + 1]
                elif listArgv[i] == "--imageType":
                    imageType = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])
            if (projectMicName != None) and (imageType != None):
                ObsLightManager.getManager().setMicProjectImageType(projectMicName=projectMicName,
                                                                       imageType=imageType)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0

    def getMicProjectImageType(self, listArgv):
        '''
        Return the image type of Mic Project.
        '''
        __COMMAND__ = __getMicProjectImageType__

        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectMicName projectName" + "\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]

        projectMicName = None

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (1 * 2)):
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--projectMicName":
                    projectMicName = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])
            if (projectMicName != None):
                res = ObsLightManager.getManager().getMicProjectImageType(projectMicName=projectMicName)
                if res == None:
                    print "No ImageType Define."
                else:
                    print "\t" + res
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0

    def createImage(self, listArgv):
        '''
        Create an Image.
        '''
        __COMMAND__ = __createImage__

        __HELP__ = "usage: " + __PRGNAME__ + " " + __COMMAND__ + " [--command-options] \n"
        __HELP__ += "\t" + "--projectMicName projectName" + "\n"
        __HELP__ += __DICO_HELP__[__COMMAND__]

        projectMicName = None

        if (len(listArgv) % 2 == 0) and (len(listArgv) <= (1 * 2)):
            for i in range(0, len(listArgv), 2):
                if listArgv[i] == "--projectMicName":
                    projectMicName = listArgv[i + 1]
                else:
                    raise ObsLightErr.ArgUnknownError(__COMMAND__, listArgv[i])
            if (projectMicName != None):
                ObsLightManager.getManager().createImage(projectMicName=projectMicName)
            else:
                raise ObsLightErr.ArgError("wrong command for " + __COMMAND__)

        elif self.__isHelp(listArgv[0]):
            print __HELP__
        else:
            raise ObsLightErr.ArgNumError(None, __COMMAND__, len(listArgv))
        return 0


