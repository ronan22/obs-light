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

import util
from util import safewriter
import ObsLightErr
import ObsLightManager
import ObsLightPrintManager

__PRGNAME__ = "ObsLight"
__DICO_HELP__ = {}

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

#Command Level 0
__info_quiet__ = ["quiet", "-quiet", "--quiet"]
__info_debug__ = ["debug", "-debug", "--debug"]
__version__ = ["version", "-version", "--version"]
__help__ = ["--help", "-h", "-help", "help"]

#Command Level 1
__server__ = ["server"]
__obsproject__ = ["obsproject"]
__package__ = ["package"]
__projectfilesystem__ = ["projectfilesystem", "projectfs", "filesystem"]
__spec__ = ["spec"]
__micproject__ = ["micproject"]
__qemuproject__ = ["qemuproject"]

__DICO_HELP__[__server__[0]] = __server__[0] + ":" + "\t" + "Doc __server__"
__DICO_HELP__[__obsproject__[0]] = __obsproject__[0] + ":" + "\t" + "Doc __obsproject__"
__DICO_HELP__[__package__[0]] = __package__[0] + ":" + "\t" + "Doc __package__"
__DICO_HELP__[__projectfilesystem__[0]] = __projectfilesystem__[0] + ":" + "\t" + "Doc __projectfilesystem__"
__DICO_HELP__[__spec__[0]] = __spec__[0] + ":" + "\t" + "Doc __spec__"
__DICO_HELP__[__micproject__[0]] = __server__[0] + ":" + "\t" + "Doc __micproject__"
__DICO_HELP__[__qemuproject__[0]] = __qemuproject__[0] + ":" + "\t" + "Doc __qemuproject__"

#Command server Level 2
__server_help__ = __help__
__server_test__ = ["test"]
__server_list__ = ["list"]
__server_query__ = ["query", "get"]

#Command server Level 3
__server_alias__ = ["server_alias", "alias"]
__server_login__ = ["login"]
__server_password__ = ["password"]
__server_api_url__ = ["api_url"]
__server_repositoryurl__ = ["repositoryurl"]
__server_weburl__ = ["weburl"]
__server_reachable__ = ["reachable"]
__server_reachable_True__ = ["True", "true", "T", "t", "1"]
__server_reachable_False__ = ["False", "false", "F", "fe", "0"]

__DICO_HELP__[__server_help__[0]] = __server_help__[0] + ":" + "\t" + "Doc __server_help__"
__DICO_HELP__[__server_test__[0]] = __server_test__[0] + ":" + "\t" + " <server_alias> test the server alias \n \
                                                                        \t\t\t\t\t<login> <password> <api_url> test the API URL."
__DICO_HELP__[__server_list__[0]] = __server_list__[0] + ":" + "\t" + "[<reachable>] reachable =False->return all sever,\
                                                                        \t\t\t\t\treachable =True->return only the available server,\
                                                                        \t\t\t\t\default=False."
__DICO_HELP__[__server_query__[0]] = __server_query__[0] + ":" + "\t" + "[login] [apiurl] [repositoryurl] [weburl] {<server_alias>}."



__DICO_HELP__[__server_reachable__[0]] = __server_reachable__[0] + ":" + "\t" + "False->return all sever,reachable =True->return only the available server,default=False."
__DICO_HELP__[__server_alias__[0]] = __server_alias__[0] + ":" + "\t" + "False->return all sever,reachable =True->return only the available server,default=False."
__DICO_HELP__[__server_login__[0]] = __server_login__[0] + ":" + "\t" + "False->return all sever,reachable =True->return only the available server,default=False."
__DICO_HELP__[__server_password__[0]] = __server_password__[0] + ":" + "\t" + "False->return all sever,reachable =True->return only the available server,default=False."
__DICO_HELP__[__server_api_url__[0]] = __server_api_url__[0] + ":" + "\t" + "False->return all sever,reachable =True->return only the available server,default=False."

__HELP__ += __DICO_HELP__[__server__[0]]
__HELP__ += __DICO_HELP__[__obsproject__[0]]
__HELP__ += __DICO_HELP__[__package__[0]]
__HELP__ += __DICO_HELP__[__projectfilesystem__[0]]
__HELP__ += __DICO_HELP__[__spec__[0]]
__HELP__ += __DICO_HELP__[__micproject__[0]]
__HELP__ += __DICO_HELP__[__qemuproject__[0]]


def getParameter(listArgv):
    if listArgv == None:
        return None, None
    elif len(listArgv) > 0:
        return listArgv[0], listArgv[1:]
    else:
        return None, None

class ObsLight():
    """
    
    """
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

        ObsLightPrintManager.quiet = 0
        ObsLightPrintManager.DEBUG = 0

        if len(listArgv) == 0:
            print __DESCRIPTION__
            return None
        elif len(listArgv) > 0:

            while(len(listArgv) > 0):
                currentCommand = listArgv[0]

                if currentCommand in __info_quiet__:
                    listArgv = listArgv[1:]
                    ObsLightPrintManager.QUIET = 1
                    ObsLightPrintManager.setLoggerLevel('CRITICAL')
                    continue
                elif currentCommand in __info_debug__:
                    listArgv = listArgv[1:]
                    ObsLightPrintManager.DEBUG += 1
                    ObsLightPrintManager.setLoggerLevel('DEBUG')
                    continue
                elif currentCommand in __version__:
                    print "OBS Light version", ObsLightManager.getVersion()
                    return None
                elif currentCommand in __help__:
                    print __DESCRIPTION__
                    print __HELP__
                    return None
                else :
                    break

            if len(listArgv) == 0:
                print __DESCRIPTION__
                return None
            else:
                currentCommand = listArgv[0]
                listArgv = listArgv[1:]
                if currentCommand in __server__ :
                    return self.server(listArgv)
                elif currentCommand in __obsproject__ :
                    return self.obsproject(listArgv)
                elif currentCommand in __package__ :
                    return self.package(listArgv)
                elif currentCommand in __projectfilesystem__ :
                    return self.projectfilesystem(listArgv)
                elif currentCommand in __spec__ :
                    return self.spec(listArgv)
                elif currentCommand in __micproject__ :
                    return self.micproject(listArgv)
                elif currentCommand in __qemuproject__ :
                    return self.qemuproject(listArgv)
                else:
                    print "ERROR UNKNOW COMMAND", currentCommand
                    return 1

    def server(self, listArgv):
        '''
        help
        test <server_alias>
        testapi <login> <password> <api_url>
        '''

        def server_help():
            '''
            
            '''
            print __DESCRIPTION__
            print __DICO_HELP__[__server_help__[0]]

            return 0

        def server_server_test(listArgv):
            '''
            
            '''
            help = False
            server_alias = None
            login = None
            password = None
            api_url = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __server_help__) or (listArgv == None):
                    help = True
                    break
                elif currentCommand in __server_alias__:
                    server_alias, listArgv = getParameter(listArgv)
                elif currentCommand in __server_login__:
                    login, listArgv = getParameter(listArgv)
                elif currentCommand in __server_password__:
                    password, listArgv = getParameter(listArgv)
                elif currentCommand in __server_api_url__:
                    api_url, listArgv = getParameter(listArgv)
                else:
                    help = True
                    break

            m = ObsLightManager.getManager()
            if help == True:
                return server_help()
            elif server_alias != None:
                res = m.testServer(obsServer=server_alias)
                if res == True:
                    print "'" + server_alias + "' is reachable"
                else:
                    print "'" + server_alias + "' is not reachable"
                return 0
            elif (login != None) and (password != None) and (api_url != None):
                res = m.testApi(api=api_url, user=login, passwd=password)
                if res == 0:
                    print "'" + api_url + "' is reachable"
                elif res == 1:
                    print "'" + api_url + "' is not reachable, user and passwd  are wrong."
                elif res == 2:
                    print "'" + api_url + "' is not reachable, api is wrong.."
                else:
                    print "'" + api_url + "' is not reachable"
                return 0
            else:
                return server_help()


        def server_server_list(listArgv):
            '''
            
            '''
            help = False
            reachable = False

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __server_help__) or (listArgv == None):
                    help = True
                    break
                elif currentCommand in __server_reachable__:
                    if len(listArgv) > 0:
                        reachable, listArgv = getParameter(listArgv)
                        if commandValue in __server_reachable_True__:
                            reachable = True
                        elif commandValue in __server_reachable_False__:
                            reachable = False
                        else:
                            help = True
                            break
                    else:
                        help = True
                        break
                else:
                    help = True
                    break

            if help == True:
                return server_help()

            m = ObsLightManager.getManager()
            res = m.getObsServerList(reachable=reachable)
            for r in res:
                print r
            return 0

        def server_server_query(listArgv):
            '''
            
            '''
            help = False
            login = None
            api_url = None
            repositoryurl = None
            weburl = None
            alias = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __server_help__) or (listArgv == None):
                    help = True
                    break
                elif currentCommand in __server_login__:
                    login = currentCommand
                elif currentCommand in __server_api_url__:
                    api_url = currentCommand
                elif currentCommand in __server_repositoryurl__:
                    repositoryurl = currentCommand
                elif currentCommand in __server_weburl__:
                    weburl = currentCommand
                elif currentCommand in __server_alias__:
                    alias , listArgv = getParameter(listArgv)
                else:
                    help = True
                    break

            if help == True:
                return server_help()
            else:
                m = ObsLightManager.getManager()
                if alias == None:
                    alias = m.getCurrentObsServer()
                if alias == None:
                    print "No alias"
                    return 1

                if login != None:
                    res = m.getObsServerParameter(obsServerAlias=alias, parameter="user")
                    print "alias '" + alias + "' user:\t\t" + str(res)
                if api_url != None:
                    res = m.getObsServerParameter(obsServerAlias=alias, parameter="serverAPI")
                    print "alias '" + alias + "' serverAPI:\t" + str(res)
                if repositoryurl != None:
                    res = m.getObsServerParameter(obsServerAlias=alias, parameter="serverRepo")
                    print "alias '" + alias + "' serverRepo:\t" + str(res)
                if weburl != None:
                    res = m.getObsServerParameter(obsServerAlias=alias, parameter="serverWeb")
                    print "alias '" + alias + "' serverWeb:\t" + str(res)

            return 0

        #_______________________________________________________________________
        if len(listArgv) == 0:
            server_help()
            return 0
        else:
            currentCommand = listArgv[0]
            listArgv = listArgv[1:]

            if currentCommand in __server_help__ :
                return server_help()
            elif currentCommand in __server_test__ :
                return server_server_test(listArgv)
            elif currentCommand in __server_list__:
                return server_server_list(listArgv)
            elif currentCommand in __server_query__:
                return server_server_query(listArgv)
            else:
                return server_help()

        return 0

    def obsproject(self, listArgv):
        '''
        
        '''
        print "obsproject"
        return 0


    def package(self, listArgv):
        '''
        
        '''
        print "package"
        return 0


    def projectfilesystem(self, listArgv):
        '''
        
        '''
        print "projectfilesystem"
        return 0

    def spec(self, listArgv):
        '''
        
        '''
        print "spec"
        return 0


    def micproject(self, listArgv):
        '''
        
        '''
        print "micproject"
        return 0

    def qemuproject(self, listArgv):
        '''
        
        '''
        print "qemuproject"
        return 0

