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
import ObsLightManager
import ObsLightPrintManager

from ObsLightUtils import getLineno

__PRGNAME__ = "ObsLight"
__DICO_Help__ = {}

__DESCRIPTION__ = "ObsLight:" + "\n"
__DESCRIPTION__ += "\t" + "Provides a tool to manage an OBS project on your local machine in command line" + "\n"
__DESCRIPTION__ += "\t" + "For informations, see the Help section" + "\n"
__DESCRIPTION__ += "\t\t" + "obslight --Help" + "\n"
__DESCRIPTION__ += "\t" + "The gui for obslight is obslightgui" + "\n"
__DESCRIPTION__ += "\t" + "A FAQ is available at:" + "\n"
__DESCRIPTION__ += "\t\t" + "*http://wiki.meego.com/OBS_Light_FAQ" + "\n"
__DESCRIPTION__ += "\t" + "For additional informations, see:" + "\n"
__DESCRIPTION__ += "\t\t" + "* http://wiki.meego.com/OBS_Light" + "\n"

__Help__ = "Usage: " + __PRGNAME__ + " [global command] <command> [--command-options]" + "\n"
__Help__ += "\n"
__Help__ += "Type " + __PRGNAME__ + " <command> --Help to get Help on a specific command." + "\n"
__Help__ += "Commands:" + "\n"

#Command Level 0
__info_quiet__ = ["quiet", "-quiet", "--quiet"]
__info_debug__ = ["debug", "-debug", "--debug"]
__version__ = ["version", "-version", "--version"]
__Help__ = ["--Help", "-h", "-Help", "Help"]

#Command Level 1
__server__ = ["server"]
__obsproject__ = ["obsproject"]
__Package__ = ["package"]
__projectfilesystem__ = ["projectfilesystem", "projectfs", "filesystem", "pfs"]
__rpmbuild__ = ["rpmbuild", "rb"]
__micproject__ = ["micproject"]
__qemuproject__ = ["qemuproject"]

__DICO_Help__[__server__[0]] = __server__[0] + ":" + "\t" + "Doc __server__"
__DICO_Help__[__obsproject__[0]] = __obsproject__[0] + ":" + "\t" + "Doc __obsproject__"
__DICO_Help__[__Package__[0]] = __Package__[0] + ":" + "\t" + "Doc __Package__"
__DICO_Help__[__projectfilesystem__[0]] = __projectfilesystem__[0] + ":" + "\t" + "Doc __projectfilesystem__"
__DICO_Help__[__rpmbuild__[0]] = __rpmbuild__[0] + ":" + "\t" + "Doc __rpmbuild__"
__DICO_Help__[__micproject__[0]] = __server__[0] + ":" + "\t" + "Doc __micproject__"
__DICO_Help__[__qemuproject__[0]] = __qemuproject__[0] + ":" + "\t" + "Doc __qemuproject__"

__Help__ += __DICO_Help__[__server__[0]]
__Help__ += __DICO_Help__[__obsproject__[0]]
__Help__ += __DICO_Help__[__Package__[0]]
__Help__ += __DICO_Help__[__projectfilesystem__[0]]
__Help__ += __DICO_Help__[__rpmbuild__[0]]
__Help__ += __DICO_Help__[__micproject__[0]]
__Help__ += __DICO_Help__[__qemuproject__[0]]

#Command server Level 2
__server_Help__ = __Help__
__server_test__ = ["test"]
__server_list__ = ["list", "ll", "ls"]
__server_query__ = ["query", "get"]
__server_set__ = ["set"]
__server_add__ = ["add"]
__server_del__ = ["delete", "del", "rm"]
__server_current__ = ["current"]

__DICO_Help__[__server_Help__[0]] = __server_Help__[0] + ":" + "\t" + "Doc __server_Help__"
__DICO_Help__[__server_test__[0]] = __server_test__[0] + ":" + "\t" + " <server_alias> test the server alias \n \
                                                                        \t\t\t\t\t<login> <password> <api_url> test the API URL."
__DICO_Help__[__server_list__[0]] = __server_list__[0] + ":" + "\t" + "[<reachable>] reachable =False->return all sever,\
                                                                        \t\t\t\t\treachable =True->return only the available server,\
                                                                        \t\t\t\t\default=False."
__DICO_Help__[__server_query__[0]] = __server_query__[0] + ":" + "\t" + "[login] [apiurl] [repository_url] [weburl] {<server_alias>}."

__DICO_Help__[__server_set__[0]] = __server_set__[0] + ":" + "\t" + "[login <login>] [apiurl <apiurl>] [repository_url <repository_url>] [weburl <web_url>] {server_alias <server_alias>}"
__DICO_Help__[__server_add__[0]] = __server_add__[0] + ":" + "\t" + "server_alias <server_alias> login <login> password <password> api_url <api_url> repository_url <repository_url> web_url <web_url>"
__DICO_Help__[__server_del__[0]] = __server_del__[0] + ":" + "\t" + "<server_alias>"

#Command server Level 3
__server_alias__ = ["server_alias", "alias"]
__server_login__ = ["login"]
__server_password__ = ["password"]
__server_api_url__ = ["api_url"]
__server_repository_url__ = ["repository_url"]
__server_web_url__ = ["web_url"]
__server_reachable__ = ["reachable"]

__DICO_Help__[__server_reachable__[0]] = __server_reachable__[0] + ":" + "\t" + "False->return all sever,reachable =True->return only the available server,default=False."
__DICO_Help__[__server_alias__[0]] = __server_alias__[0] + ":" + "\t" + ""
__DICO_Help__[__server_login__[0]] = __server_login__[0] + ":" + "\t" + ""
__DICO_Help__[__server_password__[0]] = __server_password__[0] + ":" + "\t" + ""
__DICO_Help__[__server_api_url__[0]] = __server_api_url__[0] + ":" + "\t" + ""

#Command obsproject Level 2
__obsproject_Help__ = __Help__
__obsproject_list__ = __server_list__
__obsproject_add__ = __server_add__
__obsproject_del__ = __server_del__
__obsproject_query__ = __server_query__
__obsproject_set__ = __server_set__
__obsproject_current__ = ["current"]
__obsproject_import__ = ["import"]
__obsproject_export__ = ["export"]
__obsproject_dependencyrepositories__ = ["dependencyrepositories"]

__DICO_Help__[__obsproject_Help__[0]] = __obsproject_Help__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__obsproject_list__[0]] = __obsproject_list__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__obsproject_add__[0]] = __obsproject_add__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__obsproject_del__[0]] = __obsproject_del__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__obsproject_query__[0]] = __obsproject_query__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__obsproject_set__[0]] = __obsproject_set__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__obsproject_current__[0]] = __obsproject_current__[0] + ":" + "\t" + "Doc __obsproject_Help__"

#Command obsproject Level 3
__project_raw__ = ["raw"]
__project_alias__ = ["project_alias"]
__project_name_on_obs__ = ["name_on_obs"]
__project_title__ = ["title"]
__project_description__ = ["description"]
__project_server__ = ["server"]
__project_webpage__ = ["webpage"]
__project_repository__ = ["repository"]
__project_target__ = ["target"]
__project_arch__ = ["arch", "architecture"]
__project_maintainer__ = ["maintainer"]
__project_bugowner__ = ["bugowner"]
__project_remoteurl__ = ["remoteurl"]

__DICO_Help__[__project_alias__[0]] = __project_alias__[0] + ":" + "\t" + ""
__DICO_Help__[__project_name_on_obs__[0]] = __project_name_on_obs__[0] + ":" + "\t" + ""
__DICO_Help__[__project_title__[0]] = __project_title__[0] + ":" + "\t" + ""
__DICO_Help__[__project_description__[0]] = __project_description__[0] + ":" + "\t" + ""
__DICO_Help__[__project_server__[0]] = __project_server__[0] + ":" + "\t" + ""
__DICO_Help__[__project_webpage__[0]] = __project_webpage__[0] + ":" + "\t" + ""
__DICO_Help__[__project_repository__[0]] = __project_repository__[0] + ":" + "\t" + ""
__DICO_Help__[__project_target__[0]] = __project_target__[0] + ":" + "\t" + ""
__DICO_Help__[__project_arch__[0]] = __project_arch__[0] + ":" + "\t" + ""
__DICO_Help__[__project_maintainer__[0]] = __project_maintainer__[0] + ":" + "\t" + ""
__DICO_Help__[__project_bugowner__[0]] = __project_bugowner__[0] + ":" + "\t" + ""
__DICO_Help__[__project_remoteurl__[0]] = __project_remoteurl__[0] + ":" + "\t" + ""

#Command package Level 2
__package_Help__ = __Help__
__package_add__ = __server_add__
__package_delete__ = __server_del__
__package_list__ = __server_list__
__package_query__ = __server_query__
__package_set__ = __server_set__
__package_update__ = ["update", "up"]
__package_commit__ = ["commit", "co"]
__package_repair__ = ["repair"]
__package_current__ = ["current"]
__package_addfile__ = ["addfile"]
__package_deletefile__ = ["deletefile"]
__package_refresh__ = ["refresh"]

__DICO_Help__[__package_Help__[0]] = __package_Help__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__package_add__[0]] = __package_add__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__package_delete__[0]] = __package_delete__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__package_list__[0]] = __package_list__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__package_query__[0]] = __package_query__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__package_set__[0]] = __package_set__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__package_update__[0]] = __package_update__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__package_commit__[0]] = __package_commit__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__package_repair__[0]] = __package_repair__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__package_current__[0]] = __package_current__[0] + ":" + "\t" + "Doc __obsproject_Help__"

#Command obsproject Level 3
__package_package__ = ["package", "pkg"]
__package_available__ = ["available"]
__package_status__ = ["status"]
__package_revision__ = ["revision"]
__package_url__ = ["url"]
__package_obsRev__ = ["obsRev"]
__package_oscRev__ = ["oscRev"]
__listFile__ = ["listFile"]
__obsStatus__ = ["obsStatus"]
__oscStatus__ = ["oscStatus"]
__specFile__ = ["specFile"]
__yamlFile__ = ["yamlFile"]
__fsPackageDirectory__ = ["fsPackageDirectory"]
__oscPackageDirectory__ = ["oscPackageDirectory"]
__chRootStatus__ = ["chRootStatus"]
__currentPatch__ = ["currentPatch"]
__package_oscstatus__ = ["oscstatus"]
__package_obsstatus__ = ["obsstatus"]


__DICO_Help__[__package_package__[0]] = __package_package__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__package_available__[0]] = __package_available__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__package_status__[0]] = __package_status__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__package_revision__[0]] = __package_revision__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__listFile__[0]] = __listFile__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__obsStatus__[0]] = __obsStatus__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__oscStatus__[0]] = __oscStatus__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__specFile__[0]] = __specFile__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__yamlFile__[0]] = __yamlFile__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__fsPackageDirectory__[0]] = __fsPackageDirectory__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__oscPackageDirectory__[0]] = __oscPackageDirectory__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__chRootStatus__[0]] = __chRootStatus__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__currentPatch__[0]] = __currentPatch__[0] + ":" + "\t" + "Doc __obsproject_Help__"

#Command projectfilesystem Level 2
__projectfilesystem_Help__ = __Help__
__projectfilesystem_create__ = ["create", "new"]
__projectfilesystem_delete__ = __server_del__
__projectfilesystem_query__ = __server_query__
__projectfilesystem_enter__ = ["enter", "chroot"]
__projectfilesystem_executescript__ = ["executescript", "exec"]

__projectfilesystem_addrepository__ = ["addrepository", "ar"]
__projectfilesystem_extractpatch__ = ["extractpatch"]
__projectfilesystem_repositories__ = ["repositorie"]

__DICO_Help__[__projectfilesystem_Help__[0]] = __package_Help__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__projectfilesystem_query__[0]] = __projectfilesystem_query__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__projectfilesystem_create__[0]] = __projectfilesystem_create__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__projectfilesystem_delete__[0]] = __projectfilesystem_delete__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__projectfilesystem_enter__[0]] = __projectfilesystem_enter__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__projectfilesystem_executescript__[0]] = __projectfilesystem_executescript__[0] + ":" + "\t" + "Doc __obsproject_Help__"

#Command obsproject Level 3
__projectfilesystem_status__ = ["status"]
__projectfilesystem_path__ = ["path"]
__projectfilesystem_repository__ = ["repository", "repo"]

__DICO_Help__[__projectfilesystem_path__[0]] = __projectfilesystem_path__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__projectfilesystem_status__[0]] = __projectfilesystem_status__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__projectfilesystem_repository__[0]] = __projectfilesystem_repository__[0] + ":" + "\t" + "Doc __obsproject_Help__"


#Command projectfilesystem Level 3
__repository_add__ = __server_add__
__repository_delete__ = __server_del__
__repository_modify__ = ["modify"]
__repository_query__ = __server_query__

__DICO_Help__[__repository_add__[0]] = __repository_add__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__repository_delete__[0]] = __repository_delete__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__repository_modify__[0]] = __repository_modify__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__repository_query__[0]] = __repository_query__[0] + ":" + "\t" + "Doc __obsproject_Help__"

__repository_From__ = ["from"]
__repository_newUrl__ = ["newUrl"]
__repository_newAlias__ = ["newAlias"]

__DICO_Help__[__repository_From__[0]] = __repository_From__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__repository_newUrl__[0]] = __repository_newUrl__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__repository_newAlias__[0]] = __repository_newAlias__[0] + ":" + "\t" + "Doc __obsproject_Help__"

#Command rpmbuild Level 2

__rpmbuild_prepare__ = ["prepare"]
__rpmbuild_build__ = ["build"]
__rpmbuild_install__ = ["install"]
__rpmbuild_package__ = ["package"]
__rpmbuild_isInit__ = ["isinit"]
__rpmbuild_testConflict__ = ["testconflict"]
__rpmbuild_createPatch__ = ["createpatch"]
__rpmbuild_updatepatch__ = ["updatepatch"]

__DICO_Help__[__rpmbuild_prepare__[0]] = __rpmbuild_prepare__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__rpmbuild_build__[0]] = __rpmbuild_build__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__rpmbuild_install__[0]] = __rpmbuild_install__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__rpmbuild_package__[0]] = __rpmbuild_package__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__rpmbuild_createPatch__[0]] = __rpmbuild_createPatch__[0] + ":" + "\t" + "Doc __obsproject_Help__"
__DICO_Help__[__rpmbuild_updatepatch__[0]] = __rpmbuild_updatepatch__[0] + ":" + "\t" + "Doc __obsproject_Help__"

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
                elif currentCommand in __Help__:
                    print __DESCRIPTION__
                    print __Help__
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
                elif currentCommand in __Package__ :
                    return self.package(listArgv)
                elif currentCommand in __projectfilesystem__ :
                    return self.projectfilesystem(listArgv)
                elif currentCommand in __rpmbuild__ :
                    return self.rpmbuild(listArgv)
                elif currentCommand in __micproject__ :
                    return self.micproject(listArgv)
                elif currentCommand in __qemuproject__ :
                    return self.qemuproject(listArgv)
                else:
                    print "ERROR UNKNOW COMMAND", currentCommand
                    return 1

    def server(self, listArgv):
        '''
        Help
        test <server_alias>
        testapi <login> <password> <api_url>
        '''

        def server_Help():
            '''
            
            '''
            print __DESCRIPTION__
            print __DICO_Help__[__server_Help__[0]]

            return 0

        def server_test(listArgv):
            '''
            
            '''
            Help = False
            server_alias = None
            login = None
            password = None
            api_url = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __server_Help__) or (listArgv == None):
                    Help = True
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
                    Help = True
                    break

            m = ObsLightManager.getCommandLineManager()
            if Help == True:
                return server_Help()
            elif server_alias != None:
                res = m.testServer(obsServer=server_alias)
                if res == None:
                    print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                    return -1
                else:
                    if res == True:
                        print "'" + server_alias + "' is reachable"
                    else:
                        print "'" + server_alias + "' is not reachable"
                    return 0
            elif (login != None) and (password != None) and (api_url != None):
                res = m.testApi(api=api_url, user=login, passwd=password)
                if res == None:
                    print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                    return -1
                else:
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
                return server_Help()


        def server_list(listArgv):
            '''
            
            '''
            Help = False
            reachable = False

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __server_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __server_reachable__:
                    reachable = True
                else:
                    Help = True
                    break

            if Help == True:
                return server_Help()

            m = ObsLightManager.getCommandLineManager()
            res = m.getObsServerList(reachable=reachable)
            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1
            else:
                for r in res:
                    print r
                return 0

        def server_query(listArgv):
            '''
            
            '''
            Help = False
            login = None
            api_url = None
            repository_url = None
            weburl = None
            alias = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __server_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __server_login__:
                    login = currentCommand
                elif currentCommand in __server_api_url__:
                    api_url = currentCommand
                elif currentCommand in __server_repository_url__:
                    repository_url = currentCommand
                elif currentCommand in __server_web_url__:
                    weburl = currentCommand
                elif currentCommand in __server_alias__:
                    alias , listArgv = getParameter(listArgv)
                else:
                    Help = True
                    break

            if Help == True:
                return server_Help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if alias == None:
                    alias = m.getCurrentObsServer()

                    if alias == None:
                        print "No alias"
                        return 1

                if (login == None) and\
                   (api_url == None) and\
                   (repository_url == None) and\
                   (weburl == None):
                    login = True
                    api_url = True
                    repository_url = True
                    weburl = True

                if login != None:
                    res = m.getObsServerParameter(obsServerAlias=alias, parameter="user")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "alias '" + alias + "' user:\t\t" + str(res)
                if api_url != None:
                    res = m.getObsServerParameter(obsServerAlias=alias, parameter="serverAPI")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "alias '" + alias + "' serverAPI:\t" + str(res)
                if repository_url != None:
                    res = m.getObsServerParameter(obsServerAlias=alias, parameter="serverRepo")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "alias '" + alias + "' serverRepo:\t" + str(res)
                if weburl != None:
                    res = m.getObsServerParameter(obsServerAlias=alias, parameter="serverWeb")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "alias '" + alias + "' serverWeb:\t" + str(res)

            return 0


        def server_set(listArgv):
            '''
            
            '''
            Help = False
            login = None
            api_url = None
            repository_url = None
            weburl = None
            alias = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __server_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __server_login__:
                    login , listArgv = getParameter(listArgv)
                elif currentCommand in __server_api_url__:
                    api_url , listArgv = getParameter(listArgv)
                elif currentCommand in __server_repository_url__:
                    repository_url , listArgv = getParameter(listArgv)
                elif currentCommand in __server_web_url__:
                    weburl , listArgv = getParameter(listArgv)
                elif currentCommand in __server_alias__:
                    alias , listArgv = getParameter(listArgv)
                else:
                    Help = True
                    break

            if Help == True:
                return server_Help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if alias == None:
                    alias = m.getCurrentObsServer()
                    if alias == None:
                        print "No alias"
                        return 1

                if login != None:
                    res = m.setObsServerParameter(obsServerAlias=alias, parameter="user", value=login)
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                if api_url != None:
                    res = m.setObsServerParameter(obsServerAlias=alias, parameter="serverAPI", value=api_url)
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                if repository_url != None:
                    res = m.setObsServerParameter(obsServerAlias=alias, parameter="serverRepo", value=repository_url)
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                if weburl != None:
                    res = m.setObsServerParameter(obsServerAlias=alias, parameter="serverWeb", value=weburl)
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1

            return 0

        def server_add(listArgv):
            '''
            
            '''
            Help = False
            alias = None
            login = None
            password = None
            api_url = None
            repository_url = None
            weburl = None


            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __server_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __server_alias__:
                    alias , listArgv = getParameter(listArgv)
                elif currentCommand in __server_login__:
                    login , listArgv = getParameter(listArgv)
                elif currentCommand in __server_password__:
                    password , listArgv = getParameter(listArgv)
                elif currentCommand in __server_api_url__:
                    api_url , listArgv = getParameter(listArgv)
                elif currentCommand in __server_repository_url__:
                    repository_url , listArgv = getParameter(listArgv)
                elif currentCommand in __server_web_url__:
                    weburl , listArgv = getParameter(listArgv)
                else:
                    Help = True
                    break

            if  (Help == True) or\
                ((alias == None) or
                (login == None) or
                (password == None) or
                (api_url == None) or
                (repository_url == None) or
                (weburl == None)):
                return server_Help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if login != None:
                    return m.addObsServer(serverApi=api_url,
                                          user=login,
                                          password=password,
                                          alias=alias,
                                          serverRepo=repository_url,
                                          serverWeb=weburl)


        def server_del(listArgv):
            '''
            
            '''
            Help = False
            alias = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)

                if (currentCommand in __server_Help__) or (listArgv == None):
                    Help = True
                    break
                else:
                    alias = currentCommand
                    break

            if  (Help == True) :
                return server_Help()
            else:
                m = ObsLightManager.getCommandLineManager()
                return m.delObsServer(obsServer=alias)

        def server_current(listArgv):
            '''
            
            '''
            Help = False

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __server_Help__) or (listArgv == None):
                    Help = True
                    break
                else:
                    Help = True
                    break

            if  (Help == True) :
                return server_Help()
            else:
                m = ObsLightManager.getCommandLineManager()
                res = m.getCurrentObsServer()
                print res
                return 0
        #_______________________________________________________________________
        if len(listArgv) == 0:
            server_Help()
            return 0
        else:
            currentCommand = listArgv[0]
            listArgv = listArgv[1:]

            if currentCommand in __server_Help__ :
                return server_Help()
            elif currentCommand in __server_test__ :
                return server_test(listArgv)
            elif currentCommand in __server_list__:
                return server_list(listArgv)
            elif currentCommand in __server_query__:
                return server_query(listArgv)
            elif currentCommand in __server_set__:
                return server_set(listArgv)
            elif currentCommand in __server_add__:
                return server_add(listArgv)
            elif currentCommand in __server_del__ :
                return server_del(listArgv)
            elif currentCommand in __server_current__ :
                return server_current(listArgv)
            else:
                return server_Help()
        return 0

    def obsproject(self, listArgv):
        '''
        
        '''
        def obsproject_Help():
            '''
            
            '''
            print __DESCRIPTION__
            print __DICO_Help__[__obsproject__[0]]

            return 0

        def obsproject_list (listArgv):
            '''
            
            '''
            Help = False
            server_alias = None
            arch = None
            raw = False
            maintainer = False
            bugowner = False
            remoteurl = False

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)

                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __project_raw__:
                    raw = True
                elif currentCommand in __server_alias__:
                    server_alias , listArgv = getParameter(listArgv)
                elif  currentCommand in __project_arch__ :
                    arch , listArgv = getParameter(listArgv)
                elif  currentCommand in __project_maintainer__ :
                    maintainer = True
                elif  currentCommand in __project_bugowner__ :
                    bugowner = True
                elif  currentCommand in __project_remoteurl__ :
                    remoteurl = True
                else:
                    return obsproject_Help()

            if Help == True:
                return obsproject_Help()
            else:
                m = ObsLightManager.getCommandLineManager()
                res = []
                if server_alias == None:
                    res = m.getLocalProjectList()
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                elif server_alias != None:
                    res = m.getObsServerProjectList(serverApi=server_alias,
                                                    maintainer=maintainer,
                                                    bugowner=bugowner,
                                                    remoteurl=remoteurl,
                                                    arch=arch,
                                                    raw=raw)
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                else:
                    return obsproject_Help()

                if res != None:
                    for r in res:
                        print r
                else:
                    print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return 0

        def obsproject_current(listArgv):
            '''
            
            '''
            Help = False

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __server_del__:
                    alias = currentCommand
                    break
                else:
                    Help = True
                    break

            if  (Help == True) :
                return obsproject_Help()
            else:
                m = ObsLightManager.getCommandLineManager()
                res = m.getCurrentObsProject()
                print res
                return 0

        def obsproject_add(listArgv):
            '''
            
            '''
            Help = False
            project_alias = None
            name_on_obs = None
            target = None
            arch = None
            server_alias = None


            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                else :
                    project_alias = currentCommand
                    name_on_obs , listArgv = getParameter(listArgv)
                    target , listArgv = getParameter(listArgv)
                    arch , listArgv = getParameter(listArgv)
                    server_alias , listArgv = getParameter(listArgv)
                    if listArgv == None:
                        break

            if  (Help == True) or\
                ((project_alias == None) or\
                 (name_on_obs == None) or\
                 (target == None) or\
                 (arch == None)):
                return obsproject_Help()
            else:
                m = ObsLightManager.getCommandLineManager()

                if server_alias == None:
                    server_alias = m.getCurrentObsServer()
                    if server_alias == None:
                        return obsproject_Help()

                return m.addProject(serverApi=server_alias,
                                    projectObsName=name_on_obs,
                                    projectTarget=target,
                                    projectArchitecture=arch,
                                    projectLocalName=project_alias)

        def obsproject_del(listArgv):
            '''
            
            '''
            Help = False
            project = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)

                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                else:
                    project = currentCommand
                    break

            if  (Help == True) :
                return obsproject_Help()
            elif project != None:
                m = ObsLightManager.getCommandLineManager()
                return m.removeProject(projectLocalName=project)
            else:
                return obsproject_Help()


        def obsproject_query(listArgv):
            '''
            
            '''
            Help = False
            title = False
            description = False
            server = False
            webpage = False
            repository = False
            target = False
            architecture = False
            project_alias = None
            remoteurl = False
            maintainer = False
            bugowner = False

            server_alias = None
            obsproject = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __project_title__:
                    title = True
                elif currentCommand in __project_description__:
                    description = True
                elif currentCommand in __project_server__ :
                    server = True
                elif currentCommand in __project_webpage__:
                    webpage = True
                elif currentCommand in __project_repository__:
                    repository = True
                elif currentCommand in __project_target__:
                    target = True
                elif currentCommand in __project_arch__:
                    architecture = True
                elif currentCommand in __project_remoteurl__:
                    remoteurl = True
                elif currentCommand in __project_maintainer__:
                    maintainer = True
                elif currentCommand in __project_bugowner__:
                    bugowner = True
                elif currentCommand in __project_alias__:
                    project_alias , listArgv = getParameter(listArgv)
                elif currentCommand in __server_alias__:
                    server_alias , listArgv = getParameter(listArgv)
                elif currentCommand in __obsproject__:
                    obsproject , listArgv = getParameter(listArgv)
                else:
                    Help = True
                    break

            if  (Help == True) :
                return obsproject_Help()
            else:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) and ((server_alias == None) or (obsproject == None)):
                    if project_alias == None:
                        project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return obsproject_Help()

                if  (not title) and \
                    (not description) and \
                    (not server) and \
                    (not webpage) and \
                    (not repository) and \
                    (not target) and \
                    (not architecture)and \
                    (not remoteurl) and \
                    (not maintainer) and \
                    (not architecture):

                    title = True
                    description = True
                    server = True
                    webpage = True
                    repository = True
                    target = True
                    architecture = True
                    remoteurl = True
                    maintainer = True
                    bugowner = True

                if title :
                    if (server_alias == None) and (obsproject == None):
                        res = m.getProjectParameter(projectLocalName=project_alias,
                                                    parameter="title")
                    else:
                        res = m.getObsProjectParameter(serverApi=server_alias,
                                                       obsproject=obsproject,
                                                       parameter="title")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "title:" + res
                if description :
                    if (server_alias == None) and (obsproject == None):
                        res = m.getProjectParameter(projectLocalName=project_alias,
                                                    parameter="description")
                    else:
                        res = m.getObsProjectParameter(serverApi=server_alias,
                                                       obsproject=obsproject,
                                                       parameter="title")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "description:" + res
                if server and (server_alias == None) and (obsproject == None):
                    res = m.getProjectParameter(projectLocalName=project_alias,
                                                parameter="obsServer")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "server:" + res
                if webpage and (server_alias == None) and (obsproject == None) :
                    res = m.getProjectWebPage(projectLocalName=project_alias)
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "webpage:" + res
                if repository and (server_alias == None) and (obsproject == None):
                    res = m.getProjectRepository(projectLocalName=project_alias)

                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "repository:" + res

                if target :
                    if (server_alias == None) and (obsproject == None):
                        res = m.getProjectParameter(projectLocalName=project_alias,
                                                    parameter="projectTarget")
                    else:
                        res = m.getObsProjectParameter(serverApi=server_alias,
                                                       obsproject=obsproject,
                                                       parameter="repository")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    elif isinstance(res, (basestring)):
                        print "target:" + res
                    elif isinstance(res, (list, tuple)):
                        print "target:" + ",".join(res)
                    else:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1

                if architecture :
                    if (server_alias == None) and (obsproject == None):
                        res = m.getProjectParameter(projectLocalName=project_alias,
                                                    parameter="projectArchitecture")
                    else:
                        res = m.getObsProjectParameter(serverApi=server_alias,
                                                       obsproject=obsproject,
                                                       parameter="arch")

                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    elif isinstance(res, (basestring)):
                        print "architecture:" + res
                    elif isinstance(res, (list, tuple)):
                        print "architecture:" + ",".join(res)
                    else:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1

                if remoteurl and (server_alias != None) and (obsproject != None):
                    res = m.getObsProjectParameter(serverApi=server_alias,
                                                   obsproject=obsproject,
                                                   parameter="remoteurl")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "remoteurl:" + str(res)

                if maintainer  and (server_alias != None) and (obsproject != None) :
                    res = m.getObsProjectParameter(serverApi=server_alias,
                                                obsproject=obsproject,
                                                parameter="maintainer")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "maintainer:" + ",".join(res)

                if bugowner  and (server_alias != None) and (obsproject != None) :
                    res = m.getObsProjectParameter(serverApi=server_alias,
                                                obsproject=obsproject,
                                                parameter="bugowner")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "bugowner:" + ",".join(res)
            return 0

        def obsproject_set(listArgv):
            '''
            
            '''
            Help = False
            title = None
            description = None
            project_alias = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __project_title__:
                    title , listArgv = getParameter(listArgv)
                elif currentCommand in __project_description__:
                    description , listArgv = getParameter(listArgv)
                elif currentCommand in __project_alias__:
                    project_alias , listArgv = getParameter(listArgv)
                else:
                    Help = True
                    break

            if  (Help == True) :
                return obsproject_Help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return obsproject_Help()

                if title != None:
                    res = m.setProjectParameter(projectLocalName=project_alias,
                                                parameter="projectTitle",
                                                value=title)
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                if description != None:
                    res = m.setProjectParameter(projectLocalName=project_alias,
                                                parameter="description",
                                                value=description)
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
            return 0

        def obsproject_import(listArgv):
            '''
            
            '''
            Help = False
            path = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                else:
                    path = currentCommand

                    break

            if  (Help == True) and (path != None):
                return obsproject_Help()
            else:

                m = ObsLightManager.getCommandLineManager()

                res = m.importProject(path)

                if res == None:
                    print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                    return -1
            return 0

        def obsproject_export(listArgv):
            '''
            
            '''
            Help = False
            path = None
            project_alias = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                else:
                    path = currentCommand
                    project_alias, listArgv = getParameter(listArgv)
                    break

            if  (Help == True) and (path != None):
                return obsproject_Help()
            else:
                m = ObsLightManager.getCommandLineManager()

                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return obsproject_Help()

                res = m.exportProject(project_alias, path)

                if res == None:
                    print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                    return -1
            return 0

        def obsproject_dependencyrepositories(listArgv):
            '''
            
            '''
            Help = False
            project_alias = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                else:
                    project_alias = currentCommand
                    break

            if  (Help == True):
                return obsproject_Help()
            else:
                m = ObsLightManager.getCommandLineManager()

                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return obsproject_Help()

                res = m.getDependencyRepositories(project_alias)

                if res == None:
                    print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                    return -1
                for repo in res.keys():
                    print "Repository Alias: " + str(repo) + " Url: " + res[repo]
            return 0

        #_______________________________________________________________________
        if len(listArgv) == 0:
            obsproject_Help()
            return 0
        else:
            currentCommand = listArgv[0]
            listArgv = listArgv[1:]

            if currentCommand in __obsproject_Help__ :
                return obsproject_Help()
            elif currentCommand in __obsproject_list__ :
                return obsproject_list(listArgv)
            elif currentCommand in __obsproject_add__:
                return obsproject_add(listArgv)
            elif currentCommand in __obsproject_del__:
                return obsproject_del(listArgv)
            elif currentCommand in __obsproject_query__:
                return obsproject_query(listArgv)
            elif currentCommand in __obsproject_set__:
                return obsproject_set(listArgv)
            elif currentCommand in __obsproject_current__:
                return obsproject_current(listArgv)
            elif currentCommand in  __obsproject_import__ :
                return obsproject_import(listArgv)
            elif currentCommand in __obsproject_export__ :
                return obsproject_export(listArgv)
            elif currentCommand in __obsproject_dependencyrepositories__:
                return obsproject_dependencyrepositories(listArgv)
            else:
                return obsproject_Help()

        return 0

    def package(self, listArgv):
        '''
        
        '''

        def package_Help():
            '''
            
            '''
            print __DESCRIPTION__
            print __DICO_Help__[__obsproject__[0]]

            return 0

        def package_add(listArgv):
            '''
            
            '''
            Help = False
            package = None
            project_alias = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __project_alias__:
                    project_alias, listArgv = getParameter(listArgv)
                else:
                    package = currentCommand

            if  (Help == True) or (package == None) :
                return package_Help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return package_Help()

                return m.addPackage(projectLocalName=project_alias,
                                    package=package)

        def package_delete(listArgv):
            '''
            
            '''
            Help = False
            package = None
            project_alias = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __project_alias__:
                    project_alias, listArgv = getParameter(listArgv)
                else:
                    package = currentCommand

            if  (Help == True) or (package == None) :
                return package_Help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return package_Help()

                return m.removePackage(projectLocalName=project_alias,
                                       package=package)

        def package_list(listArgv):
            '''
            
            '''
            Help = False
            available = False
            project_alias = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __package_available__:
                    available = True
                elif currentCommand in __project_alias__:
                    project_alias, listArgv = getParameter(listArgv)
                else:
                    Help = True
                    break

            if  (Help == True) :
                return package_Help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return package_Help()

                if available:
                    res = m.getLocalProjectPackageList(projectLocalName=project_alias, local=0)

                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    else:
                        for r in res:
                            print r
                else:
                    res = m.getLocalProjectPackageList(projectLocalName=project_alias, local=1)

                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    else:
                        for r in res:
                            print r
            return 0



        def package_query(listArgv):
            '''
            
            '''
            Help = False

            title = False
            description = False
#            status = False
            revision = False
            obsRev = False
            oscRev = False
            url = False
            listFile = False
            obsStatus = False
            oscStatus = False
            specFile = False
            yamlFile = False
            fsPackageDirectory = False
            oscPackageDirectory = False

            chRootStatus = False
            currentPatch = False

            project_alias = None
            server_alias = None
            obsproject = None
            package = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __project_title__:
                    title = True
                elif currentCommand in __project_description__:
                    description = True
                elif currentCommand in __package_revision__:
                    revision = True
                elif currentCommand in __package_obsRev__ :
                    obsRev = True
                elif currentCommand in __package_oscRev__ :
                    oscRev = True
                elif currentCommand in __listFile__:
                    listFile = True
                elif currentCommand in __obsStatus__:
                    obsStatus = True
                elif currentCommand in __oscStatus__:
                    oscStatus = True
                elif currentCommand in __specFile__:
                    specFile = True
                elif currentCommand in __yamlFile__:
                    yamlFile = True
                elif currentCommand in __fsPackageDirectory__ :
                    fsPackageDirectory = True
                elif currentCommand in __oscPackageDirectory__ :
                    oscPackageDirectory = True
                elif currentCommand in __chRootStatus__:
                    chRootStatus = True
                elif currentCommand in __currentPatch__:
                    currentPatch = True
                elif currentCommand in __package_url__:
                    url = True
                elif currentCommand in __project_alias__:
                    project_alias , listArgv = getParameter(listArgv)
                elif currentCommand in __server_alias__:
                    server_alias , listArgv = getParameter(listArgv)
                elif currentCommand in __obsproject__:
                    obsproject , listArgv = getParameter(listArgv)
                elif currentCommand in __package_package__:
                    package , listArgv = getParameter(listArgv)
                else:
                    Help = True
                    break

            if  (Help == True) :
                return package_Help()
            else:
                m = ObsLightManager.getCommandLineManager()

                if (package == None) and (project_alias != None):
                    package = m.getCurrentPackage(project_alias)
                if package == None:
                    return package_Help()

                if (project_alias == None) and ((server_alias == None) or (obsproject == None)):
                    return package_Help()

                if (not title) and \
                   (not description) and \
                   (not revision)and \
                   (not url)and \
                   (not obsRev)and \
                   (not oscRev)and \
                   (not listFile)and \
                   (not obsStatus)and \
                   (not oscStatus)and \
                   (not specFile)and \
                   (not yamlFile)and \
                   (not fsPackageDirectory)and \
                   (not oscPackageDirectory)and \
                   (not chRootStatus)and \
                   (not currentPatch):

                    title = True
                    description = True
#                    status = True
                    revision = True
                    obsRev = True
                    oscRev = True
                    url = True
                    listFile = True
                    obsStatus = True
                    oscStatus = True
                    specFile = True
                    yamlFile = True
                    fsPackageDirectory = True
                    oscPackageDirectory = True
                    chRootStatus = True
                    currentPatch = True

                if title :
                    if (server_alias == None) and (obsproject == None):
                        res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="title")
                    else:
                        res = m.getObsPackageParameter(serverApi=server_alias,
                                                       obsproject=obsproject,
                                                       package=package,
                                                       parameter="title")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "title:" + res

                if description :
                    if (server_alias == None) and (obsproject == None):
                        res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="description")
                    else:
                        res = m.getObsPackageParameter(serverApi=server_alias,
                                                       obsproject=obsproject,
                                                       package=package,
                                                       parameter="title")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "description:" + res

                if url and ((server_alias != None) and (obsproject != None)):
                    res = m.getObsPackageParameter(serverApi=server_alias,
                                                       obsproject=obsproject,
                                                       package=package,
                                                       parameter="url")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "url:" + res

                if obsRev and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="obsRev")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "obsRev:" + res

                if oscRev and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="oscRev")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "oscRev:" + res

                if listFile :
                    if (project_alias != None):
                        res = m.getPackageParameter(projectLocalName=project_alias,
                                                        package=package,
                                                        parameter="listFile")
                    else:
                        res = m.getObsPackageParameter(serverApi=server_alias,
                                                   obsproject=obsproject,
                                                   package=package,
                                                   parameter="listFile")

                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "listFile:" + ",".join(res)

                if obsStatus and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="obsStatus")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "obsStatus:" + res

                if oscStatus and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="oscStatus")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "oscStatus:" + res

                if specFile and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="specFile")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "specFile:" + res

                if yamlFile and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="yamlFile")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "yamlFile:" + res

                if fsPackageDirectory and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="fsPackageDirectory")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "fsPackageDirectory:" + res

                if oscPackageDirectory and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="oscPackageDirectory")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "oscPackageDirectory:" + res

                if chRootStatus and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="chRootStatus")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "chRootStatus:" + res

                if currentPatch and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="currentPatch")
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "currentPatch:" + res

        def package_set(listArgv):
            '''
            
            '''
            Help = False

            title = None
            description = None

            project_alias = None
            package = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __project_title__:
                    title , listArgv = getParameter(listArgv)
                elif currentCommand in __project_description__:
                    description , listArgv = getParameter(listArgv)
                elif currentCommand in __project_alias__:
                    project_alias , listArgv = getParameter(listArgv)
                elif currentCommand in __package_package__:
                    package , listArgv = getParameter(listArgv)
                else:
                    Help = True
                    break

            if  (Help == True) :
                return package_Help()
            else:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return package_Help()

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return package_Help()

                if title != None :
                    res = m.setPackageParameter(projectLocalName=project_alias,
                                                  package=package,
                                                  parameter="title",
                                                  value=title)
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1

                if description != None :
                    res = m.setPackageParameter(projectLocalName=project_alias,
                                                  package=package,
                                                  parameter="description",
                                                  value=description)
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1

                return res

        def package_update(listArgv):
            '''
            
            '''
            Help = False

            project_alias = None
            package = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __package_update__:
                    update = True
                elif currentCommand in __project_alias__:
                    project_alias , listArgv = getParameter(listArgv)
                elif currentCommand in __package_package__:
                    package , listArgv = getParameter(listArgv)
                else:
                    Help = True
                    break

            if  (Help == True) :
                return package_Help()
            else:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return package_Help()

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return package_Help()

                res = m.updatePackage(projectLocalName=project_alias,
                                     package=package)
                if res == None:
                    print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                    return -1

                return res

        def package_commit(listArgv):
            '''
            
            '''
            Help = False

            message = None

            project_alias = None
            package = None
            message = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                else:
                    message = currentCommand
                    while(len(listArgv) > 0):
                        if currentCommand in __project_alias__:
                            project_alias , listArgv = getParameter(listArgv)
                        elif currentCommand in __package_package__:
                            package , listArgv = getParameter(listArgv)
                        else:
                            break
                    break

            if  (Help == True) and (message != None):
                return package_Help()
            else:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return package_Help()

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return package_Help()

                res = m.addAndCommitChanges(projectLocalName=project_alias,
                                            package=package,
                                            message=message)
                if res == None:
                    print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                    return -1
                return res

        def package_repair(listArgv):
            '''
            
            '''
            Help = False

            project_alias = None
            package = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __package_update__:
                    update = True
                elif currentCommand in __project_alias__:
                    project_alias , listArgv = getParameter(listArgv)
                elif currentCommand in __package_package__:
                    package , listArgv = getParameter(listArgv)
                else:
                    Help = True
                    break

            if  (Help == True) :
                return package_Help()
            else:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return package_Help()

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return package_Help()

                res = m.repairOscPackageDirectory(projectLocalName=project_alias,
                                                  package=package)
                if res == None:
                    print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                    return -1
                return res

        def package_current(listArgv):
            '''
            
            '''
            Help = False
            project_alias = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __project_alias__:
                    project_alias, listArgv = getParameter(listArgv)
                else:
                    Help = True
                    break

            if  (Help == True) :
                return package_Help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return package_Help()

                return m.getCurrentPackage(projectLocalName=project_alias)
            return 0

        def package_addfile(listArgv):
            '''
            
            '''
            Help = False
            path = None
            project_alias = None
            package = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                else:
                    path = currentCommand
                    while(len(listArgv) > 0):
                        currentCommand, listArgv = getParameter(listArgv)
                        if currentCommand in __project_alias__:
                            project_alias , listArgv = getParameter(listArgv)
                        elif currentCommand in __package_package__:
                            package , listArgv = getParameter(listArgv)
                        else:
                            break
                    break

            if  (Help == True) :
                return package_Help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return package_Help()

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return package_Help()

                return m.addFileToPackage(project_alias, package, path)
            return 0

        def package_deletefile(listArgv):
            '''
            
            '''
            Help = False
            name = None
            project_alias = None
            package = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __project_alias__:
                    project_alias, listArgv = getParameter(listArgv)
                else:
                    name = currentCommand
                    while(len(listArgv) > 0):
                        currentCommand, listArgv = getParameter(listArgv)
                        if currentCommand in __project_alias__:
                            project_alias , listArgv = getParameter(listArgv)
                        elif currentCommand in __package_package__:
                            package , listArgv = getParameter(listArgv)
                        else:
                            break
                    break

            if  (Help == True) :
                return package_Help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return package_Help()

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return package_Help()

                return m.deleteFileFromPackage(project_alias, package, name)
            return 0

        def package_refresh(listArgv):
            '''
            
            '''
            Help = False
            OscStatus = False
            ObsStatus = False
            project_alias = None
            package = None




            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                else:
                    path = currentCommand
                    while(len(listArgv) > 0):
                        currentCommand, listArgv = getParameter(listArgv)
                        if currentCommand in __package_oscstatus__:
                            OscStatus = True
                        elif currentCommand in __package_obsstatus__:
                            ObsStatus = True
                        elif currentCommand in __project_alias__:
                            project_alias , listArgv = getParameter(listArgv)
                        elif currentCommand in __package_package__:
                            package , listArgv = getParameter(listArgv)
                        else:
                            break
                    break

            if  (Help == True) :
                return package_Help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if not (OscStatus or ObsStatus):
                    OscStatus = True
                    ObsStatus = True

                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return package_Help()

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return package_Help()
                if OscStatus:
                    res = m.refreshOscDirectoryStatus(project_alias, package)
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                if ObsStatus:
                    res = m.refreshObsStatus(project_alias, package)
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                return 0
            return 0

#-------------------------------------------------------------------------------
        if len(listArgv) == 0:
            package_Help()
            return 0
        else:
            currentCommand = listArgv[0]
            listArgv = listArgv[1:]

            if currentCommand in __package_Help__ :
                return package_Help()
            elif currentCommand in __package_add__ :
                return package_add(listArgv)
            elif currentCommand in __package_delete__:
                return package_delete(listArgv)
            elif currentCommand in __package_list__:
                return package_list(listArgv)
            elif currentCommand in __package_query__:
                return package_query(listArgv)
            elif currentCommand in __package_set__:
                return package_set(listArgv)
            elif currentCommand in __package_update__:
                return package_update(listArgv)
            elif currentCommand in  __package_commit__ :
                return package_commit(listArgv)
            elif currentCommand in __package_repair__ :
                return package_repair(listArgv)
            elif currentCommand in __package_current__:
                return package_current(listArgv)
            elif currentCommand in __package_addfile__:
                return package_addfile(listArgv)
            elif currentCommand in __package_deletefile__:
                return package_deletefile(listArgv)
            elif currentCommand in __package_refresh__:
                return package_refresh(listArgv)
            else:
                return package_Help()

        return 0

    def projectfilesystem(self, listArgv):
        '''
        
        '''
        def projectfilesystem_Help():
            '''
            
            '''
            return 0

        def projectfilesystem_create(listArgv):
            '''
            
            '''
            Help = False
            project_alias = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                else:
                    project_alias = currentCommand

            if  (Help == True) :
                return projectfilesystem_Help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return projectfilesystem_Help()

                res = m.createChRoot(projectLocalName=project_alias)
                if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                return res
            return 0

        def projectfilesystem_delete(listArgv):
            '''
            
            '''
            Help = False
            project_alias = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __project_alias__:
                    project_alias, listArgv = getParameter(listArgv)
                else:
                    Help = True
                    break

            if  (Help == True) :
                return projectfilesystem_Help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return projectfilesystem_Help()

                res = m.removeChRoot(projectLocalName=project_alias)
                if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                return res
            return 0

        def projectfilesystem_query(listArgv):
            '''
            
            '''
            Help = False
            path = False
            status = False

            project_alias = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __projectfilesystem_path__:
                    path = True
                elif currentCommand in __projectfilesystem_status__:
                    status = True
                elif currentCommand in __project_alias__:
                    project_alias, listArgv = getParameter(listArgv)
                else:
                    Help = True
                    break

            if  (Help == True) :
                return projectfilesystem_Help()
            else:
                m = ObsLightManager.getCommandLineManager()

                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return projectfilesystem_Help()

                if (not path) and (not status) :

                    path = True
                    status = True

                if path :
                    res = m.getChRootPath(projectLocalName=project_alias)
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    print "path:" + res

                if status :
                    res = m.isChRootInit(projectLocalName=project_alias)
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    val = "init" if res else "not init"
                    print "status: " + val

        def projectfilesystem_enter(listArgv):
            '''
            
            '''
            Help = False

            project_alias = None
            package = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __package_package__:
                    package , listArgv = getParameter(listArgv)
                else:
                    project_alias = currentCommand

            if  (Help == True) :
                return projectfilesystem_Help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return projectfilesystem_Help()

                res = m.goToChRoot(projectLocalName=project_alias, package=package)
                if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                return res
            return 0

        def projectfilesystem_executescript(listArgv):
            '''
            
            '''
            Help = False
            aPath = None

            project_alias = None


            currentCommand, listArgv = getParameter(listArgv)
            if (currentCommand in __obsproject_Help__) or (listArgv == None):
                Help = True
            else:
                aPath = currentCommand
                project_alias, listArgv = getParameter(listArgv)

            if  (Help == True)  :
                return projectfilesystem_Help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return projectfilesystem_Help()
                if aPath == None:
                    return projectfilesystem_Help()

                res = m.execScript(projectLocalName=project_alias, aPath=aPath)
                if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                return res
            return 0

        def projectfilesystem_repository(listArgv):
            '''
            
            '''
            self.repository(listArgv)

        if len(listArgv) == 0:
            return projectfilesystem_Help()
        else:
            currentCommand = listArgv[0]
            listArgv = listArgv[1:]

            if currentCommand in __projectfilesystem_Help__ :
                return projectfilesystem_Help()
            elif currentCommand in __projectfilesystem_create__ :
                return projectfilesystem_create(listArgv)
            elif currentCommand in __projectfilesystem_delete__:
                return projectfilesystem_delete(listArgv)
            elif currentCommand in __projectfilesystem_query__:
                return projectfilesystem_query(listArgv)
            elif currentCommand in __projectfilesystem_enter__:
                return projectfilesystem_enter(listArgv)
            elif currentCommand in __projectfilesystem_executescript__:
                return projectfilesystem_executescript(listArgv)
            elif currentCommand in __projectfilesystem_repository__:
                return projectfilesystem_repository(listArgv)
            else:
                return projectfilesystem_Help()
        return 0

    def repository(self, listArgv):
        '''
        
        '''
        def repository_help():
            '''
            
            '''
            Help = False

            return 0

        def repository_add(listArgv):
            '''
            
            '''
            Help = False

            From = False

            url = None
            alias = None
            fromProject = None
            project_alias = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                elif currentCommand in __repository_From__:
                    From = True
                    fromProject, listArgv = getParameter(listArgv)
                    project_alias, listArgv = getParameter(listArgv)
                    break
                else:
                    url = currentCommand
                    alias, listArgv = getParameter(listArgv)
                    project_alias, listArgv = getParameter(listArgv)
                    break

            if  (Help == True):
                return repository_help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return repository_help()

                if From :
                    if fromProject == None:
                        return repository_help()

                    res = m.addRepo(projectLocalName=project_alias,
                                    fromProject=fromProject,
                                    repoUrl=None,
                                    alias=None)
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    return res
                else:
                    if url == None:
                        return repository_help()
                    if alias == None:
                        return repository_help()

                    res = m.addRepo(projectLocalName=project_alias,
                                    fromProject=None,
                                    repoUrl=url,
                                    alias=alias)
                    if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                    return res

        def repository_delete(listArgv):
            '''
            
            '''
            Help = False

            alias = None
            project_alias = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                else:
                    alias = currentCommand
                    project_alias, listArgv = getParameter(listArgv)
                    break

            if  (Help == True):
                return repository_help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return repository_help()

                if alias == None:
                    return repository_help()

                res = m.deleteRepo(projectLocalName=project_alias,
                                    repoAlias=alias)

                if res == None:
                    print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                    return -1
                return res


        def repository_modify(listArgv):
            '''
            
            '''
            Help = False

            alias = None
            project_alias = None
            newUrl = None
            newAlias = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                else:
                    alias = currentCommand
                    while(len(listArgv) > 0):
                        currentCommand, listArgv = getParameter(listArgv)
                        if currentCommand in __repository_newUrl__:
                            newUrl, listArgv = getParameter(listArgv)
                        elif currentCommand in __repository_newAlias__:
                            newAlias, listArgv = getParameter(listArgv)
                        else:
                            break
                    project_alias, listArgv = getParameter(listArgv)
                    break

            if  (Help == True):
                return repository_help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return repository_help()
                if alias == None:
                    return repository_help()

                if (newUrl == None) and (newAlias == None):
                    return repository_help()

                res = m.modifyRepo(projectLocalName=project_alias,
                                   repoAlias=alias,
                                   newUrl=newUrl,
                                   newAlias=newAlias)

                if res == None:
                    print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                    return -1
                return res

        def repository_query(listArgv):
            '''
            
            '''
            Help = False
            project_alias = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                else :
                    project_alias = currentCommand


            if  (Help == True) :
                return repository_help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return repository_help()
                res = m.getChRootRepositories(projectLocalName=project_alias)
                if res == None:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1
                print "repositories:"
                for k in res:
                    print "Alias: " + k + "\t\tURL: " + res[k]
            return 0

        if len(listArgv) == 0:
            return repository_help()
        else:
            currentCommand = listArgv[0]
            listArgv = listArgv[1:]

            if currentCommand in __Help__ :
                return repository_help()
            elif currentCommand in __repository_add__:
                return repository_add(listArgv)
            elif currentCommand in __repository_delete__ :
                return repository_delete(listArgv)
            elif currentCommand in __repository_modify__:
                return repository_modify(listArgv)
            elif currentCommand in __repository_query__:
                return repository_query(listArgv)
            else:
                return repository_help()
        return 0

    def rpmbuild(self, listArgv):
        '''
        
        '''
        def rpmbuild_help():
            '''
            
            '''
            return 0

        def rpmbuild_prepare(listArgv):
            '''
            
            '''
            Help = False
            project_alias = None
            package = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __project_alias__:
                    project_alias, listArgv = getParameter(listArgv)
                else :
                    package = currentCommand

            if  (Help == True) :
                return rpmbuild_help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return rpmbuild_help()

                if (package == None):
                    package = m.getCurrentPackage(project_alias)

                res = m.addPackageSourceInChRoot(projectLocalName=project_alias, package=package)
                if res == None:
                    print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                    return -1
            return 0

        def rpmbuild_build(listArgv):
            '''
            
            '''
            Help = False
            project_alias = None
            package = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __project_alias__:
                    project_alias, listArgv = getParameter(listArgv)
                else :
                    package = currentCommand

            if  (Help == True) :
                return rpmbuild_help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return rpmbuild_help()

                if (package == None):
                    package = m.getCurrentPackage(project_alias)

                res = m.buildRpm(projectLocalName=project_alias, package=package)
                if res == None:
                    print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                    return -1
            return 0

        def rpmbuild_install(listArgv):
            '''
            
            '''
            Help = False
            project_alias = None
            package = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __project_alias__:
                    project_alias, listArgv = getParameter(listArgv)
                else :
                    package = currentCommand

            if  (Help == True) :
                return rpmbuild_help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return rpmbuild_help()

                if (package == None):
                    package = m.getCurrentPackage(project_alias)

                res = m.installRpm(projectLocalName=project_alias, package=package)
                if res == None:
                    print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                    return -1
            return 0

        def rpmbuild_package(listArgv):
            '''
            
            '''
            Help = False
            project_alias = None
            package = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __project_alias__:
                    project_alias, listArgv = getParameter(listArgv)
                else :
                    package = currentCommand

            if  (Help == True) :
                return rpmbuild_help()
            else:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return rpmbuild_help()

                if (package == None):
                    package = m.getCurrentPackage(project_alias)

                res = m.packageRpm(projectLocalName=project_alias, package=package)
                if res == None:
                    print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                    return -1
            return 0

        def rpmbuild_isInit(listArgv):
            '''
            
            '''
            Help = False
            project_alias = None
            package = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __project_alias__:
                    project_alias , listArgv = getParameter(listArgv)
                elif currentCommand in __package_package__:
                    package , listArgv = getParameter(listArgv)
                else:
                    Help = True
                    break

            if  (Help == True) :
                return rpmbuild_help()
            else:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return rpmbuild_help()

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return rpmbuild_help()

                print
                res = m.patchIsInit(projectLocalName=project_alias, packageName=package)
                if res == None:
                    print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                    return -1
                print "for '" + package + "' a patch is init: " + str(res)
                return 0

        def rpmbuild_createPatch(listArgv):
            '''
            
            '''
            Help = False
            project_alias = None
            package = None
            patch = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                else:
                    patch = currentCommand
                    while (len(listArgv) > 0):
                        if currentCommand in __project_alias__:
                            project_alias , listArgv = getParameter(listArgv)
                        elif currentCommand in __package_package__:
                            package , listArgv = getParameter(listArgv)
                        else:
                            break
                    break

            if  (Help == True) :
                return rpmbuild_help()
            else:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return rpmbuild_help()

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return rpmbuild_help()

                if (patch == None) :
                    return rpmbuild_help()

                res = m.createPatch(projectLocalName=project_alias, package=package, patch=patch)
                if res == None:
                    print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                    return -1
                return 0

        def rpmbuild_updatepatch(listArgv):
            '''
            
            '''
            Help = False
            project_alias = None
            package = None

            while(len(listArgv) > 0):
                currentCommand, listArgv = getParameter(listArgv)
                if (currentCommand in __obsproject_Help__) or (listArgv == None):
                    Help = True
                    break
                elif currentCommand in __project_alias__:
                    project_alias , listArgv = getParameter(listArgv)
                elif currentCommand in __package_package__:
                    package , listArgv = getParameter(listArgv)
                else:
                    Help = True
                    break

            if  (Help == True) :
                return rpmbuild_help()
            else:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return rpmbuild_help()

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return rpmbuild_help()

                print "project_alias", project_alias
                print "package", package
                res = m.updatePatch(projectLocalName=project_alias, package=package)
                if res == None:
                    print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                    return -1
                return 0

        def rpmbuild_testConflict(listArgv):
            '''
            
            '''
            Help = False
            m = ObsLightManager.getCommandLineManager()
            return m.testConflict(projectLocalName=None, package=None)

        if len(listArgv) == 0:
            return rpmbuild_help()
        else:
            currentCommand = listArgv[0]
            listArgv = listArgv[1:]

            if currentCommand in __Help__ :
                return rpmbuild_help()
            elif currentCommand in __rpmbuild_prepare__:
                return rpmbuild_prepare(listArgv)
            elif currentCommand in __rpmbuild_build__ :
                return rpmbuild_build(listArgv)
            elif currentCommand in __rpmbuild_install__:
                return rpmbuild_install(listArgv)
            elif currentCommand in __rpmbuild_package__:
                return rpmbuild_package(listArgv)
            elif currentCommand in __rpmbuild_isInit__:
                return rpmbuild_isInit(listArgv)
            elif currentCommand in __rpmbuild_testConflict__:
                return rpmbuild_testConflict(listArgv)
            elif currentCommand in __rpmbuild_createPatch__:
                return rpmbuild_createPatch(listArgv)
            elif currentCommand in __rpmbuild_updatepatch__:
                return rpmbuild_updatepatch(listArgv)
            else:
                return rpmbuild_help()
        return 0

    def micproject(self, listArgv):
        '''
        
        '''
        print "micproject #feature", listArgv
        return 0

    def qemuproject(self, listArgv):
        '''
        
        '''
        print "qemuproject #feature", listArgv
        return 0
