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
import collections

from ObsLightUtils import getLineno

__PRGNAME__ = "OBSlight"

firstBorderLen = 4
secondBorderLen = 30
firstBorder = " "*firstBorderLen
secondBorder = " "*secondBorderLen

# function to format the help.
def createDoc(command, comment):
    '''
    Generate/format the documentation to be bash friendly
    '''

    doc = ""
    currentLine = firstBorder + command[0]
    #currentLine = firstBorder + '\033[94m' + command[0] + '\033[0m'

    if len(command) > 1:
        currentLine += " (" + ",".join(command[1:]) + ") "

    currentLine += ":"
    if len(currentLine) > secondBorderLen:
        doc += currentLine + "\n"
        currentLine = secondBorder
    else:
        currentLine += " "*(secondBorderLen - len(currentLine))

    if (isinstance(comment, collections.Iterable) and
        not isinstance(comment, str) and
        not isinstance(comment, unicode)):
        for line in comment:
            doc += currentLine + line + "\n"
            currentLine = secondBorder
    else:
        doc += currentLine + comment
    return doc

def createCommandHelp(command, comment):
    '''
    format end store command/documentation
    '''
    __DICO_command_help__[command[0]] = createDoc(command, comment)

def createCommandServerHelp(command, comment):
    '''
    format end store command/documentation for server command
    '''
    __DICO_command_server_help__[command[0]] = createDoc(command, comment)

def createCommandObsprojectHelp(command, comment):
    '''
    format end store command/documentation for Obsproject command
    '''
    __DICO_command_obsproject_help__[command[0]] = createDoc(command, comment)

def createCommandPackageHelp(command, comment):
    '''
    format end store command/documentation for Package command
    '''
    __DICO_command_package_help__[command[0]] = createDoc(command, comment)

def createCommandFilesystemHelp(command, comment):
    '''
    format end store command/documentation for Filesystem command
    '''
    __DICO_command_filesystem_help__[command[0]] = createDoc(command, comment)

def createCommandRpmbuildHelp(command, comment):
    '''
    format end store command/documentation for Rpmbuild command
    '''
    __DICO_command_rpmbuild_help__[command[0]] = createDoc(command, comment)

def createCommandMicprojectHelp(command, comment):
    '''
    format end store command/documentation for Micproject command
    '''
    __DICO_command_micproject_help__[command[0]] = createDoc(command, comment)

#def createCommandQemuprojectHelp(command, comment):
#    __DICO_command_qemuproject_help__[command[0]] = createDoc(command, comment)

def createCommandGlobal(command):
    '''
    Add command to the command global list (global)
    '''
    __LIST_command_global__.append(command[0])

def createCommand(command):
    '''
    Add command to the command global list (main command)
    '''
    __LIST_command__.append(command[0])

def createParameterHelp(command, comment):
    '''
    Format end store parameter/documentation, the parameter/documentation is unique for all OBSlight.
    '''
    __DICO_parameter_help__[command[0]] = createDoc(command, comment)

def appendCommandServer(command):
    """
    Append sub command to command server
    """
    __LIST_command_server__.append(command[0])

def appendCommandObsproject(command):
    """
    Append sub command to command Obsproject
    """
    __LIST_command_obsproject__.append(command[0])

def appendCommandPackage(command):
    """
    Append sub command to command Package
    """
    __LIST_package__.append(command[0])

def appendCommandFilesystem(command):
    """
    Append sub command to command Filesystem
    """
    __LIST_filesystem__.append(command[0])

def appendCommandRpmbuild(command):
    """
    Append sub command to command Rpmbuild
    """
    __LIST_rpmbuild__.append(command[0])

def appendCommandMicproject(command):
    """
    Append sub command to command Micproject
    """
    __LIST_micproject__.append(command[0])

#def appendCommandQemuproject(command):
#    """
#    Append sub command to command Qemuproject
#    """
#    __LIST_qemuproject__.append(command[0])

def createParameterServer(command, parameterList, completionBlacklist=None):
    '''
    Add parameter to the sub command of server, the parameter are automatically add
    to the completion list except if present on the completionBlacklist.
    '''
    __DICO_parameter_server__[command[0]] = []
    for parameter in parameterList:
        __DICO_parameter_server__[command[0]].append(parameter[0])
        if (completionBlacklist != None) and (not parameter in  completionBlacklist):
            __DICO_parameter_server_completion__[command[0]].append(parameter[0])

def createParameterObsproject(command, parameterList, completionBlacklist=None):
    '''
    Add parameter to the sub command of Obsproject, the parameter are automatically add
    to the completion list except if present on the completionBlacklist.
    '''
    __DICO_parameter_obsproject__[command[0]] = []
    for parameter in parameterList:
        __DICO_parameter_obsproject__[command[0]].append(parameter[0])
        if (completionBlacklist != None) and (not parameter in  completionBlacklist):
            __DICO_parameter_obsproject_completion__[command[0]].append(parameter[0])

def createParameterPackage(command, parameterList, completionBlacklist=None):
    '''
    Add parameter to the sub command of Package, the parameter are automatically add
    to the completion list except if present on the completionBlacklist.
    '''
    __DICO_parameter_package__[command[0]] = []
    for parameter in parameterList:
        __DICO_parameter_package__[command[0]].append(parameter[0])
        if (completionBlacklist != None) and (not parameter in  completionBlacklist):
            __DICO_parameter_package_completion__[command[0]].append(parameter[0])

def createParameterFilesystem(command, parameterList, completionBlacklist=None):
    '''
    Add parameter to the sub command of Filesystem, the parameter are automatically add
    to the completion list except if present on the completionBlacklist.
    '''
    __DICO_parameter_filesystem__[command[0]] = []
    for parameter in parameterList:
        __DICO_parameter_filesystem__[command[0]].append(parameter[0])
        if (completionBlacklist != None) and (not parameter in  completionBlacklist):
            __DICO_parameter_filesystem_completion__[command[0]].append(parameter[0])

def createParameterRpmbuild(command, parameterList, completionBlacklist=None):
    '''
    Add parameter to the sub command of Rpmbuild, the parameter are automatically add
    to the completion list except if present on the completionBlacklist.
    '''
    __DICO_parameter_rpmbuild__[command[0]] = []
    for parameter in parameterList:
        __DICO_parameter_rpmbuild__[command[0]].append(parameter[0])
        if (completionBlacklist != None) and (not parameter in  completionBlacklist):
            __DICO_parameter_rpmbuild_completion__[command[0]].append(parameter[0])

def createParameterMicproject(command, parameterList, completionBlacklist=None):
    '''
    Add parameter to the sub command of Micproject, the parameter are automatically add
    to the completion list except if present on the completionBlacklist.
    '''
    __DICO_parameter_micproject__[command[0]] = []
    for parameter in parameterList:
        __DICO_parameter_micproject__[command[0]].append(parameter[0])
        if (completionBlacklist != None) and (not parameter in  completionBlacklist):
            __DICO_parameter_micproject_completion__[command[0]].append(parameter[0])

__DESCRIPTION__ = __PRGNAME__ + ":" + "\n"
__DESCRIPTION__ += firstBorder + "Provides a tool to manage an OBS project on your local machine in command line" + "\n"
__DESCRIPTION__ += firstBorder + "For informations, see the Help section" + "\n"
__DESCRIPTION__ += firstBorder * 2 + "obslight --Help" + "\n"
__DESCRIPTION__ += firstBorder + "The gui for " + __PRGNAME__ + " is obslightgui" + "\n"
__DESCRIPTION__ += firstBorder + "A FAQ is available at:" + "\n"
__DESCRIPTION__ += firstBorder * 2 + "*http://wiki.meego.com/OBS_Light_FAQ" + "\n"
__DESCRIPTION__ += firstBorder + "For additional informations, see:" + "\n"
__DESCRIPTION__ += firstBorder * 2 + "*http://wiki.meego.com/OBS_Light" + "\n"

__DESCRIPTION__ += "Usage: " + __PRGNAME__ + " [global command] <command> [--command-options]" + "\n"
__DESCRIPTION__ += "\n"
__DESCRIPTION__ += "Type " + __PRGNAME__ + " <command> --Help to get Help on a specific command." + "\n"
__DESCRIPTION__ += "Commands:" + "\n"

__SYNTAX_HELP__ = 'synthax used:\n'
__SYNTAX_HELP__ += firstBorder + '  project    the string "project"\n'
__SYNTAX_HELP__ += firstBorder + ' [project]   the optional string "project"\n'
__SYNTAX_HELP__ += firstBorder + ' <project>   a project name\n'
__SYNTAX_HELP__ += firstBorder + '[<project>]  an optional project name\n'
__SYNTAX_HELP__ += firstBorder + '{<project>}  an optional project name, if absent, the current used is taken\n'
__SYNTAX_HELP__ += firstBorder + '   BLANK     no parameter\n'

__LIST_command_global__ = []
__LIST_command__ = []

__DICO_command_help__ = {}

#Command ****
__LIST_command_server__ = []
__LIST_command_obsproject__ = []
__LIST_package__ = []
__LIST_filesystem__ = []
__LIST_rpmbuild__ = []
__LIST_micproject__ = []
#__LIST_qemuproject__ = []

#Define the **** command help
__DICO_command_server_help__ = {}
__DICO_command_obsproject_help__ = {}
__DICO_command_package_help__ = {}
__DICO_command_filesystem_help__ = {}
__DICO_command_rpmbuild_help__ = {}
__DICO_command_micproject_help__ = {}
#__DICO_command_qemuproject_help__ = {}

#Command **** parameter 
__DICO_parameter_server__ = {}
__DICO_parameter_obsproject__ = {}
__DICO_parameter_package__ = {}
__DICO_parameter_filesystem__ = {}
__DICO_parameter_rpmbuild__ = {}
__DICO_parameter_micproject__ = {}
#__DICO_parameter_qemuproject__ = {}

#Define the parameter help
__DICO_parameter_help__ = {}

#Define the parameter list for **** completion
__DICO_parameter_server_completion__ = {}
__DICO_parameter_obsproject_completion__ = {}
__DICO_parameter_package_completion__ = {}
__DICO_parameter_filesystem_completion__ = {}
__DICO_parameter_rpmbuild_completion__ = {}
__DICO_parameter_micproject_completion__ = {}
__DICO_parameter_qemuproject_completion__ = {}

#Command 
__info_quiet__ = ["quiet", "-quiet", "--quiet"]
__info_debug__ = ["debug", "-debug", "--debug"]
__version__ = ["version", "-version", "--version"]
__command_help__ = ["help", "-h", "-help", "--help"]
__noaction__ = ["noaction"]
__man__ = ["man"]

__help_command_help__ = "show this help message and exit"

createCommandGlobal(__info_quiet__)
createCommandGlobal(__info_debug__)
createCommandGlobal(__version__)
createCommandGlobal(__command_help__)
createCommandGlobal(__noaction__)

createCommandHelp(__info_quiet__,
                 "run obslight in quiet mode")
createCommandHelp(__info_debug__,
                 "run obslight in debugger mode")
createCommandHelp(__version__,
                 "show program's version number and exit")
createCommandHelp(__command_help__, __help_command_help__)
createCommandHelp(__noaction__,
                 "Execute command but do nothing")
createCommandHelp(__man__,
                 "print the full help ")
#Command 
__command_current__ = ["current"]
__command_list__ = ["list", "ll", "ls"]
__command_test__ = ["test"]
__command_query__ = ["query", "get"]
__command_set__ = ["set"]
__command_add__ = ["add"]
__command_del__ = ["delete", "del", "rm"]
__command_current__ = ["current"]
__command_import__ = ["import"]
__command_export__ = ["export"]
__command_dependencyrepositories__ = ["dependencyrepositories"]

#Parameter 
__parameter_reachable__ = ["reachable"]
__parameter_alias__ = ["server_alias", "alias"]
__parameter_login__ = ["login", "user"]
__parameter_password__ = ["password", "pwd"]
__parameter_api_url__ = ["api_url"]
__parameter_repository_url__ = ["repository_url"]
__parameter_web_url__ = ["web_url"]
__parameter_raw__ = ["raw"]
__parameter_alias__ = ["project_alias"]
__parameter_name_on_obs__ = ["name_on_obs"]
__parameter_project_title__ = ["title"]
__parameter_project_description__ = ["description"]
__parameter_server__ = ["server"]
__parameter_webpage__ = ["webpage"]
__parameter_repository__ = ["repository"]
__parameter_target__ = ["target"]
__parameter_arch__ = ["arch", "architecture"]
__parameter_maintainer__ = ["maintainer"]
__parameter_bugowner__ = ["bugowner"]
__parameter_remoteurl__ = ["remoteurl"]

#Define the server parameter help
createParameterHelp(__command_help__, __help_command_help__)
createParameterHelp(__parameter_reachable__, ["[reachable] optional"])
createParameterHelp(__parameter_alias__, "the alias of an OBS server ")
createParameterHelp(__parameter_login__, "the login for a account on an OBS server")
createParameterHelp(__parameter_password__, "the password for a account on an OBS server")
createParameterHelp(__parameter_api_url__, "the URL of an OBS server API")
createParameterHelp(__parameter_repository_url__, "the URL of an OBS server repository")
createParameterHelp(__parameter_web_url__, "the URL of an OBS server web")
createParameterHelp(__parameter_raw__, "no filter on the project list")
createParameterHelp(__parameter_alias__ , "the name of the obslight project on the locale drive.")
createParameterHelp(__parameter_name_on_obs__ , "the name of the project on the OBS server")
createParameterHelp(__parameter_project_title__ , "the title of a OBS project")
createParameterHelp(__parameter_project_description__ , "the description of a OBS project")
createParameterHelp(__parameter_server__ , "the ???")
createParameterHelp(__parameter_webpage__ , "the webpage of the OBS project management ")
createParameterHelp(__parameter_repository__ , "the repository is the file depot of a OBS Project.")
createParameterHelp(__parameter_target__ , "the target repository of an OBS project")
createParameterHelp(__parameter_arch__ , "the architecture of an OBS project")
createParameterHelp(__parameter_maintainer__ , "the maintainer of an OBS project")
createParameterHelp(__parameter_bugowner__ , "the bugowner of an OBS project")
createParameterHelp(__parameter_remoteurl__ , "an OBS project can build again a remote project throught a remote project link")

#obslight   
#    server
#    obsproject
#    package
#    filesystem
#    rpmbuild
#    micproject
#    qemuproject #Feature

#Global command Level 0
__server__ = ["server"]
__obsproject__ = ["obsproject"]
__Package__ = ["package"]
__projectfilesystem__ = ["projectfilesystem", "projectfs", "filesystem", "pfs"]
__rpmbuild__ = ["rpmbuild", "rb"]
__micproject__ = ["micproject"]
#__qemuproject__ = ["qemuproject"] #Feature

createCommand(__server__)
createCommand(__obsproject__)
createCommand(__Package__)
createCommand(__projectfilesystem__)
createCommand(__rpmbuild__)
createCommand(__micproject__)
#createCommand(__qemuproject__) #Feature

createCommandHelp(__server__, "Manage the OBS server")
createCommandHelp(__obsproject__, "Manage the OBSlight project")
createCommandHelp(__Package__, "Manage the packages of OBSlight project")
createCommandHelp(__projectfilesystem__, "Manage the project filesystem of OBSlight project")
createCommandHelp(__rpmbuild__, "Manage the rpmbuild of the package into the project filesystem")
createCommandHelp(__micproject__, "Manage image biulding")
#createCommandHelp(__qemuproject__, "Manage qemu") #Feature

#    server    test    server_alias <server_alias> 
#    server    test    login <login> password <password> api_url <api_url> 
#    server    list    [reachable]
#    server    query    [login|apiurl|repository_url|weburl] {server_alias <server_alias>}
#    server    set    [login <login>] [apiurl <apiurl>] [repository_url <repository_url>] [weburl <web_url>] {server_alias <server_alias>}
#    server    add    server_alias <server_alias> login <login> password <password> api_url <api_url> repository_url <repository_url> web_url <web_url>
#    server    delete    <server_alias>  
#    server    current BLANK

#Command server
appendCommandServer(__command_help__)
appendCommandServer(__command_test__)
appendCommandServer(__command_list__)
appendCommandServer(__command_query__)
appendCommandServer(__command_set__)
appendCommandServer(__command_add__)
appendCommandServer(__command_del__)
appendCommandServer(__command_current__)

#Define the server command help
createCommandServerHelp(__command_help__, __help_command_help__)

createCommandServerHelp(__command_test__, ["server_alias <server_alias>",
                                          "test the server alias",
                                          "login <login> password <password> api_url <api_url>",
                                          "test the API URL."])

createCommandServerHelp(__command_list__, ["[<reachable>]",
                                          "if reachable  -> return all sever",
                                          "else  -> return only the available server"])

createCommandServerHelp(__command_query__, ["[login|apiurl|repository_url|weburl] {server_alias <server_alias>}",
                                           "return the server parameter."])

createCommandServerHelp(__command_set__, ["[login <login>] [apiurl <apiurl>] [repository_url <repository_url>] [weburl <web_url>] {server_alias <server_alias>}",
                                         "set the server parameter"])

createCommandServerHelp(__command_add__, ["server_alias <server_alias> login <login> password <password> api_url <api_url> repository_url <repository_url> web_url <web_url>",
                                         "add a new OBS server"])

createCommandServerHelp(__command_del__, ["<server_alias>",
                                         "del an OBS server"])

createCommandServerHelp(__command_current__, ["BLANK",
                                             "return the current OBS server"])

#Define the parameter list for server command
createParameterServer(__command_list__, [__parameter_reachable__, __command_help__])

createParameterServer(__command_current__, __command_help__)

createParameterServer(__command_test__, [__command_help__,
                                         __parameter_alias__,
                                         __parameter_login__,
                                         __parameter_password__,
                                         __parameter_api_url__])

createParameterServer(__command_query__, [__command_help__,
                                          __parameter_alias__,
                                          __parameter_login__,
                                          __parameter_api_url__,
                                          __parameter_repository_url__,
                                          __parameter_web_url__])

createParameterServer(__command_set__, [__command_help__,
                                        __parameter_alias__,
                                        __parameter_login__,
                                        __parameter_api_url__,
                                        __parameter_repository_url__,
                                        __parameter_web_url__])

createParameterServer(__command_add__, [__command_help__,
                                        __parameter_alias__,
                                        __parameter_login__,
                                        __parameter_password__,
                                        __parameter_api_url__,
                                        __parameter_repository_url__,
                                        __parameter_web_url__])

createParameterServer(__command_del__, [__command_help__,
                                      __parameter_alias__],
                                      completionBlacklist=[__parameter_alias__])

#    obsproject    list    BLANK
#    obsproject    list    server_alias <server_alias> raw|[arch <arch>|maintainer|bugowner|remoteurl]
#    obsproject    current
#    obsproject    dependencyrepositories {<project_alias>}
#    obsproject    delete    <project_alias>
#    obsproject    add    <project_alias> <name_on_obs> <target> <arch> {<server_alias>}
#    obsproject    query    [title|description|obsServer|webpage|repository|target|architecture] {project_alias <project_alias>}
#    obsproject    query    [title|description|target|architecture|remoteurl|maintainer|bugowner] server_alias <server_alias> obsproject <project> 
#    obsproject    set    [title <title>] [description <description>] {project_alias <project_alias>}
#    obsproject    import    path
#    obsproject    export  path {<project_alias>}

#Command obsproject 
appendCommandObsproject(__command_help__)
appendCommandObsproject(__command_list__)
appendCommandObsproject(__command_add__)
appendCommandObsproject(__command_del__)
appendCommandObsproject(__command_query__)
appendCommandObsproject(__command_set__)
appendCommandObsproject(__command_current__)
appendCommandObsproject(__command_import__)
appendCommandObsproject(__command_export__)
appendCommandObsproject(__command_dependencyrepositories__)

#Define the server obsproject help
createCommandObsprojectHelp(__command_help__, __help_command_help__)

createCommandObsprojectHelp(__command_list__, ["BLANK",
                                         "return all local project.",
                                         "server_alias <server_alias> raw|[arch <arch>|maintainer|bugowner|remoteurl]",
                                         "return project on the OBS server filter with arch, maintainer, bugowner, remoteurl"])

createCommandObsprojectHelp(__command_add__, ["<project_alias> <name_on_obs> <target> <arch> {<server_alias>}",
                                        "create a local project"])

createCommandObsprojectHelp(__command_del__, ["<project_alias>",
                                        "delete a local project"])

createCommandObsprojectHelp(__command_query__, ["[title|description|obsServer|webpage|repository|target|architecture] {project_alias <project_alias>}",
                                          "query locale project parameter",
                                          "[title|description|target|architecture|remoteurl|maintainer|bugowner] server_alias <server_alias> obsproject <project>",
                                          "query OBS project parameter"])

createCommandObsprojectHelp(__command_set__, ["[title <title>] [description <description>] {project_alias <project_alias>}",
                                        "modify local project parameter"])

createCommandObsprojectHelp(__command_current__, ["BLANK",
                                            "print the curent local project"])

createCommandObsprojectHelp(__command_import__, ["path",
                                           "import a back up file"])

createCommandObsprojectHelp(__command_export__, ["path {<project_alias>}",
                                           "export a back up file"])

createCommandObsprojectHelp(__command_dependencyrepositories__, ["dependencyrepositories {<project_alias>}",
                                                           "print the dependency repositories of a local project "])

#Define the obsproject parameter help
createParameterObsproject(__command_list__, [])
createParameterObsproject(__command_add__, [])
createParameterObsproject(__command_del__, [])
createParameterObsproject(__command_query__, [])
createParameterObsproject(__command_set__, [])
createParameterObsproject(__command_current__, [])
createParameterObsproject(__command_import__, [])
createParameterObsproject(__command_export__, [])
createParameterObsproject(__command_dependencyrepositories__, [])







##Command package
#appendCommandPackage
##Define the package command help
#createCommandPackageHelp
##Define the package parameter help
#createParameterPackage
#
##Command filesystem
#appendCommandFilesystem
##Define the filesystem command help
#createCommandFilesystemHelp
##Define the filesystem parameter help
#createParameterFilesystem
#
##Command rpmbuild
#appendCommandRpmbuild
##Define the rpmbuild command help
#createCommandRpmbuildHelp
##Define the rpmbuild parameter help
#createParameterRpmbuild
#
##Command micproject
#appendCommandMicproject
##Define the micproject command help
#createCommandMicprojectHelp
##Define the micproject parameter help
#createParameterMicproject



#Command obsproject Level 3


#Command package Level 2
__package_Help__ = __command_help__
__package_add__ = __command_add__
__package_delete__ = __command_del__
__package_list__ = __command_list__
__package_query__ = __command_query__
__package_set__ = __command_set__
__package_update__ = ["update", "up"]
__package_commit__ = ["commit", "co"]
__package_repair__ = ["repair"]
__package_current__ = ["current"]
__package_addfile__ = ["addfile"]
__package_deletefile__ = ["deletefile"]
__package_refresh__ = ["refresh"]

#__DICO_parameter_help__[__self.print_Help__[0]] = __self.print_Help__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__package_add__[0]] = __package_add__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__package_delete__[0]] = __package_delete__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__package_list__[0]] = __package_list__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__package_query__[0]] = __package_query__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__package_set__[0]] = __package_set__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__package_update__[0]] = __package_update__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__package_commit__[0]] = __package_commit__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__package_repair__[0]] = __package_repair__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__package_current__[0]] = __package_current__[0] + ":" + "\t" + "Doc __command_help__"

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

__DICO_parameter_help__[__package_package__[0]] = __package_package__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__package_available__[0]] = __package_available__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__package_status__[0]] = __package_status__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__package_revision__[0]] = __package_revision__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__listFile__[0]] = __listFile__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__obsStatus__[0]] = __obsStatus__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__oscStatus__[0]] = __oscStatus__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__specFile__[0]] = __specFile__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__yamlFile__[0]] = __yamlFile__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__fsPackageDirectory__[0]] = __fsPackageDirectory__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__oscPackageDirectory__[0]] = __oscPackageDirectory__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__chRootStatus__[0]] = __chRootStatus__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__currentPatch__[0]] = __currentPatch__[0] + ":" + "\t" + "Doc __command_help__"

#Command projectfilesystem Level 2
__projectfilesystem_Help__ = __command_help__
__projectfilesystem_create__ = ["create", "new"]
__projectfilesystem_delete__ = __command_del__
__projectfilesystem_query__ = __command_query__
__projectfilesystem_enter__ = ["enter", "chroot"]
__projectfilesystem_executescript__ = ["executescript", "exec"]

__projectfilesystem_addrepository__ = ["addrepository", "ar"]
__projectfilesystem_extractpatch__ = ["extractpatch"]
__projectfilesystem_repositories__ = ["repositorie"]

#__DICO_parameter_help__[__projectfilesystem_Help__[0]] = __self.print_Help__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__projectfilesystem_query__[0]] = __projectfilesystem_query__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__projectfilesystem_create__[0]] = __projectfilesystem_create__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__projectfilesystem_delete__[0]] = __projectfilesystem_delete__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__projectfilesystem_enter__[0]] = __projectfilesystem_enter__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__projectfilesystem_executescript__[0]] = __projectfilesystem_executescript__[0] + ":" + "\t" + "Doc __command_help__"

#Command obsproject Level 3
__projectfilesystem_status__ = ["status"]
__projectfilesystem_path__ = ["path"]
__projectfilesystem_repository__ = ["repository", "repo"]

__DICO_parameter_help__[__projectfilesystem_path__[0]] = __projectfilesystem_path__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__projectfilesystem_status__[0]] = __projectfilesystem_status__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__projectfilesystem_repository__[0]] = __projectfilesystem_repository__[0] + ":" + "\t" + "Doc __command_help__"

#Command projectfilesystem Level 3
__repository_add__ = __command_add__
__repository_delete__ = __command_del__
__repository_modify__ = ["modify"]
__repository_query__ = __command_query__

__DICO_parameter_help__[__repository_add__[0]] = __repository_add__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__repository_delete__[0]] = __repository_delete__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__repository_modify__[0]] = __repository_modify__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__repository_query__[0]] = __repository_query__[0] + ":" + "\t" + "Doc __command_help__"

__repository_From__ = ["from"]
__repository_newUrl__ = ["newUrl"]
__repository_newAlias__ = ["newAlias"]

__DICO_parameter_help__[__repository_From__[0]] = __repository_From__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__repository_newUrl__[0]] = __repository_newUrl__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__repository_newAlias__[0]] = __repository_newAlias__[0] + ":" + "\t" + "Doc __command_help__"

#Command rpmbuild Level 2

__rpmbuild_prepare__ = ["prepare"]
__rpmbuild_build__ = ["build"]
__rpmbuild_install__ = ["install"]
__rpmbuild_package__ = ["package"]
__rpmbuild_isInit__ = ["isinit"]
__rpmbuild_testConflict__ = ["testconflict"]
__rpmbuild_createPatch__ = ["createpatch"]
__rpmbuild_updatepatch__ = ["updatepatch"]

__DICO_parameter_help__[__rpmbuild_prepare__[0]] = __rpmbuild_prepare__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__rpmbuild_build__[0]] = __rpmbuild_build__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__rpmbuild_install__[0]] = __rpmbuild_install__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__rpmbuild_package__[0]] = __rpmbuild_package__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__rpmbuild_createPatch__[0]] = __rpmbuild_createPatch__[0] + ":" + "\t" + "Doc __command_help__"
__DICO_parameter_help__[__rpmbuild_updatepatch__[0]] = __rpmbuild_updatepatch__[0] + ":" + "\t" + "Doc __command_help__"

class ObsLightBase():
    '''
    only management doc print and obslight core.
    '''
    noaction = False
    def __init__(self):
        '''
        init ObsLightBase parameter
        '''
        sys.stderr = safewriter.SafeWriter(sys.stderr)
        sys.stdout = safewriter.SafeWriter(sys.stdout)

        self.__listArgv = sys.argv[1:]

        self.listCommand = __LIST_command_server__
        self.dicoParameterServerCompletion = __DICO_parameter_server_completion__
        self.dicoCommandHelp = __DICO_command_server_help__
        self.dicoParameter = __DICO_parameter_server__
        self.dicoParameterHelp = __DICO_parameter_help__

    def setListArgv(self, arg):
        """
        Set the main list of arguments.
        You can set many lists of args separated by " , "
        """
        self.__listArgv = arg

    def getParameter(self, listArgv):
        '''
        return the first paramater and listArgv
        '''
        if listArgv == None:
            return None, None
        elif len(listArgv) > 0:
            return listArgv[0], listArgv[1:]
        else:
            return None, None

    def testListArgv(self, listArgv):
        return  ((listArgv != None) and len(listArgv) > 0)

    def testResult(self, res, idLine):
        if res == None:
            print "ERROR NO RESULT " + __file__ + " " + str(idLine)
            return -1
        else:
            return 0

    def testServerAlias(self, server_alias):
        '''
        test server_alias 
        return the current OBS server if server_alias is None  
        '''
        if server_alias == None:
            m = ObsLightManager.getCommandLineManager()
            server_alias = m.getCurrentObsServer()
            if server_alias == None:
                print "No alias"
        return server_alias


    def main(self):
        """
        Execute the main list of arguments
        """
        while ("," in self.__listArgv):
            tmpListArgv = self.__listArgv[:self.__listArgv.index(",")]
            self.__listArgv = self.__listArgv[self.__listArgv.index(",") + 1:]
            self.execute(tmpListArgv)

        return self.execute(self.__listArgv)

    def execute(self, listArgv):
        '''
        Execute a list of arguments.
        '''
        pass

    def print_Help(self, cmd=None):
        '''
        print help.
        '''
        if ObsLightBase.noaction:
            if cmd == None:
                print " ".join(self.listCommand)
            else:
                print " ".join(self.dicoParameterServerCompletion[cmd[0]])
            return 0
        else:
            if cmd == None:
                for cmd in self.listCommand:
                    print self.dicoCommandHelp[cmd]

            else:
                print self.dicoCommandHelp[cmd[0]]
                print "Parameter:"
                for para in self.dicoParameter[cmd[0]]:
                    print self.dicoParameterHelp[para]
            print __SYNTAX_HELP__

        return 0

    def globalDescription(self):
        '''
        Print the global description
        '''
        if not ObsLightBase.noaction:
            print __DESCRIPTION__
            for h in __LIST_command__:
                print __DICO_command_help__[h]
            print "\nglobal Options:\n"
            for h in __LIST_command_global__:
                print __DICO_command_help__[h]
        return 0
    def printDescriptionLevel0(self):
        '''
        print the global description or return the list for completion
        '''
        if ObsLightBase.noaction:
            listArg = __LIST_command_global__
            listArg.extend(__LIST_command__)
            print " ".join(listArg)
        else:
            self.globalDescription()
        return 0

    def printVersion(self):
        '''
        print the OBS Light version
        '''
        if not ObsLightBase.noaction:
            print "OBS Light version", ObsLightManager.getVersion()
        return 0

    def printUnknownCommand(self, currentCommand, listCommand=None):
        if not ObsLightBase.noaction:
            print "ERROR UNKNOWN COMMAND", currentCommand
            if (listCommand != None) and (len(listCommand) > 0):
                print "Available argument are :" + ",".join(listCommand)
        return 1

class ObsLightServer(ObsLightBase):
    '''
    manage OBSlight server
    '''
    def __init__(self):
        '''
        init class
        '''
        ObsLightBase.__init__(self)
        self.listCommand = __LIST_command_server__
        self.dicoParameterServerCompletion = __DICO_parameter_server_completion__
        self.dicoParameter = __DICO_parameter_server__

        self.dicoCommandHelp = __DICO_command_server_help__

        self.dicoParameterHelp = __DICO_parameter_help__

    def printCompletionListAlias(self):
        '''
        
        '''
        m = ObsLightManager.getCommandLineManager()
        res = m.getObsServerList(reachable=True)
        if res != None:
            print " ".join(res)
        return 0

    def execute(self, listArgv):
        '''
        
        '''
        if len(listArgv) == 0:
            return self.print_Help()
        else:
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__ :
                return self.print_Help()
            elif currentCommand in __command_current__ :
                return self.server_current(listArgv)
            elif currentCommand in __command_test__ :
                return self.server_test(listArgv)
            elif currentCommand in __command_list__:
                return self.server_list(listArgv)
            elif currentCommand in __command_query__:
                return self.server_query(listArgv)
            elif currentCommand in __command_set__:
                return self.server_set(listArgv)
            elif currentCommand in __command_add__:
                return self.server_add(listArgv)
            elif currentCommand in __command_del__ :
                return self.server_del(listArgv)
            else:
                return self.printUnknownCommand(currentCommand, __LIST_command_server__)
        return 0

    def server_test(self, listArgv):
        '''
        
        '''
        Help = False
        server_alias = None
        login = None
        password = None
        api_url = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_alias__:
                server_alias, listArgv = self.getParameter(listArgv)
                if (server_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListAlias()
            elif currentCommand in __parameter_login__:
                login, listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_password__:
                password, listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_api_url__:
                api_url, listArgv = self.getParameter(listArgv)
            else:
                return self.printUnknownCommand(currentCommand, __DICO_parameter_server__[__command_test__[0]])

        if Help == True:
            return self.print_Help(__command_test__)
        if not ObsLightBase.noaction:
            if server_alias != None:
                m = ObsLightManager.getCommandLineManager()
                res = m.testServer(obsServer=server_alias)
                if self.testResult(res, getLineno()) == 0 :
                    if res == True:
                        print "'" + server_alias + "' is reachable"
                    else:
                        print "'" + server_alias + "' is not reachable"
                    return 0
                else:
                    return -1
            elif (login != None) and (password != None) and (api_url != None):
                m = ObsLightManager.getCommandLineManager()
                res = m.testApi(api=api_url, user=login, passwd=password)
                if self.testResult(res, getLineno()) == 0 :
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
                    return -1
            else:
                return self.print_Help(__command_test__)
        else:
            return self.print_Help(__command_test__)

    def server_list(self, listArgv):
        '''
        
        '''
        Help = False
        reachable = False

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_reachable__:
                reachable = True
            else:
                return self.printUnknownCommand(currentCommand, __DICO_parameter_server__[__command_list__[0]])

        if Help == True:
            return self.print_Help(__command_list__)
        if not ObsLightBase.noaction:
            m = ObsLightManager.getCommandLineManager()
            res = m.getObsServerList(reachable=reachable)
            if self.testResult(res, getLineno()) == 0 :
                for r in res:
                    print r
                return 0
            else:
                return -1
        else:
            return self.print_Help(__command_list__)

    def server_query(self, listArgv):
        '''
        
        '''
        Help = False
        login = False
        api_url = False
        repository_url = False
        weburl = False
        server_alias = None
        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_login__:
                login = True
            elif currentCommand in __parameter_api_url__:
                api_url = True
            elif currentCommand in __parameter_repository_url__:
                repository_url = True
            elif currentCommand in __parameter_web_url__:
                weburl = True
            elif currentCommand in __parameter_alias__:
                server_alias, listArgv = self.getParameter(listArgv)
                if (server_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListAlias()
            else:
                return self.printUnknownCommand(currentCommand, __DICO_parameter_server__[__command_query__[0]])

        if Help == True:
            return self.print_Help(__command_query__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                server_alias = self.testServerAlias(server_alias)
                if server_alias == None:
                    return 1

                if (login == False) and\
                   (api_url == False) and\
                   (repository_url == False) and\
                   (weburl == False):
                    login = True
                    api_url = True
                    repository_url = True
                    weburl = True

                if login :
                    res = m.getObsServerParameter(obsServerAlias=server_alias, parameter="user")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    print "alias '" + server_alias + "' user:\t\t" + str(res)
                if api_url :
                    res = m.getObsServerParameter(obsServerAlias=server_alias, parameter="serverAPI")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    print "alias '" + server_alias + "' serverAPI:\t" + str(res)
                if repository_url :
                    res = m.getObsServerParameter(obsServerAlias=server_alias, parameter="serverRepo")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    print "alias '" + server_alias + "' serverRepo:\t" + str(res)
                if weburl :
                    res = m.getObsServerParameter(obsServerAlias=server_alias, parameter="serverWeb")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    print "alias '" + server_alias + "' serverWeb:\t" + str(res)
            else:
                return self.print_Help(__command_query__)
        return 0


    def server_set(self, listArgv):
        '''
        
        '''
        Help = False
        login = None
        api_url = None
        repository_url = None
        weburl = None
        server_alias = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_login__:
                login , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_api_url__:
                api_url , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_repository_url__:
                repository_url , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_web_url__:
                weburl , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_alias__:
                server_alias, listArgv = self.getParameter(listArgv)
                if (server_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListAlias()
            else:
                return self.printUnknownCommand(currentCommand, __DICO_parameter_server__[__command_set__[0]])

        if Help == True:
            return self.print_Help(__command_set__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                server_alias = self.testServerAlias(server_alias)
                if server_alias == None:
                    return 1
                if login != None:
                    res = m.setObsServerParameter(obsServerAlias=server_alias, parameter="user", value=login)
                    if self.testResult(res, getLineno()) == -1:return - 1
                if api_url != None:
                    res = m.setObsServerParameter(obsServerAlias=server_alias, parameter="serverAPI", value=api_url)
                    if self.testResult(res, getLineno()) == -1:return - 1
                if repository_url != None:
                    res = m.setObsServerParameter(obsServerAlias=server_alias, parameter="serverRepo", value=repository_url)
                    if self.testResult(res, getLineno()) == -1:return - 1
                if weburl != None:
                    res = m.setObsServerParameter(obsServerAlias=server_alias, parameter="serverWeb", value=weburl)
                    if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.print_Help(__command_set__)

    def server_add(self, listArgv):
        '''
        
        '''
        Help = False
        server_alias = None
        login = None
        password = None
        api_url = None
        repository_url = None
        weburl = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_alias__:
                server_alias, listArgv = self.getParameter(listArgv)
                if (server_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListAlias()
            elif currentCommand in __parameter_login__:
                login , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_password__:
                password , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_api_url__:
                api_url , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_repository_url__:
                repository_url , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_web_url__:
                weburl , listArgv = self.getParameter(listArgv)
            else:
                return self.printUnknownCommand(currentCommand, __DICO_parameter_server__[__command_add__[0]])

        if  (Help == True) or\
            ((server_alias == None) or
            (login == None) or
            (password == None) or
            (api_url == None) or
            (repository_url == None) or
            (weburl == None)):
            return self.print_Help(__command_add__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                return m.addObsServer(serverApi=api_url,
                                      user=login,
                                      password=password,
                                      server_alias=server_alias,
                                      serverRepo=repository_url,
                                      serverWeb=weburl)
            else:
                return self.print_Help(__command_add__)

    def server_del(self, listArgv):
        '''
        
        '''
        Help = False
        alias = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)

            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                alias = currentCommand
                break

        if  (Help == True) or (alias == None):
            return self.print_Help(__command_del__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                return m.delObsServer(obsServer=alias)
            else:
                return self.print_Help(__command_del__)

    def server_current(self, listArgv):
        '''
        Return the current OBS help
        '''
        Help = False

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                return self.printUnknownCommand(currentCommand, __DICO_parameter_server__[__command_current__[0]])

        if  (Help == True) :
            return self.print_Help(__command_current__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                res = m.getCurrentObsServer()
                print res
                return 0
            else:
                return self.print_Help(__command_current__)

class ObsLightObsproject(ObsLightBase):
    '''
    manage OBSlight server
    '''
    def __init__(self):
        '''
        init class
        '''
        ObsLightBase.__init__(self)

        self.listCommand = __LIST_command_server__
        self.dicoParameterServerCompletion = __DICO_parameter_server_completion__
        self.dicoParameter = __DICO_parameter_server__

        self.dicoCommandHelp = __DICO_command_server_help__

        self.dicoParameterHelp = __DICO_parameter_help__

    def obsproject_list (self, listArgv):
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
            currentCommand, listArgv = self.getParameter(listArgv)

            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_raw__:
                raw = True
            elif currentCommand in __parameter_alias__:
                server_alias , listArgv = self.getParameter(listArgv)
            elif  currentCommand in __parameter_arch__ :
                arch , listArgv = self.getParameter(listArgv)
            elif  currentCommand in __parameter_maintainer__ :
                maintainer = True
            elif  currentCommand in __parameter_bugowner__ :
                bugowner = True
            elif  currentCommand in __parameter_remoteurl__ :
                remoteurl = True
            else:
                return self.print_Help()

        if Help == True:
            return self.print_Help()
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
                return self.print_Help()

            if res != None:
                for r in res:
                    print r
            else:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
            return 0

    def obsproject_current(self, listArgv):
        '''
        
        '''
        Help = False

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                Help = True
                break

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            res = m.getCurrentObsProject()
            print res
            return 0

    def obsproject_add(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None
        name_on_obs = None
        target = None
        arch = None
        server_alias = None


        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else :
                project_alias = currentCommand
                name_on_obs , listArgv = self.getParameter(listArgv)
                target , listArgv = self.getParameter(listArgv)
                arch , listArgv = self.getParameter(listArgv)
                server_alias , listArgv = self.getParameter(listArgv)
                if listArgv == None:
                    break

        if  (Help == True) or\
            ((project_alias == None) or\
             (name_on_obs == None) or\
             (target == None) or\
             (arch == None)):
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()

            if server_alias == None:
                server_alias = m.getCurrentObsServer()
                if server_alias == None:
                    return self.print_Help()

            return m.addProject(serverApi=server_alias,
                                projectObsName=name_on_obs,
                                projectTarget=target,
                                projectArchitecture=arch,
                                projectLocalName=project_alias)

    def obsproject_del(self, listArgv):
        '''
        
        '''
        Help = False
        project = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)

            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                project = currentCommand
                break

        if  (Help == True) :
            return self.print_Help()
        elif project != None:
            m = ObsLightManager.getCommandLineManager()
            return m.removeProject(projectLocalName=project)
        else:
            return self.print_Help()


    def obsproject_query(self, listArgv):
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
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_project_title__:
                title = True
            elif currentCommand in __parameter_project_description__:
                description = True
            elif currentCommand in __parameter_server__ :
                server = True
            elif currentCommand in __parameter_webpage__:
                webpage = True
            elif currentCommand in __parameter_repository__:
                repository = True
            elif currentCommand in __parameter_target__:
                target = True
            elif currentCommand in __parameter_arch__:
                architecture = True
            elif currentCommand in __parameter_remoteurl__:
                remoteurl = True
            elif currentCommand in __parameter_maintainer__:
                maintainer = True
            elif currentCommand in __parameter_bugowner__:
                bugowner = True
            elif currentCommand in __parameter_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_alias__:
                server_alias , listArgv = self.getParameter(listArgv)
            elif currentCommand in __obsproject__:
                obsproject , listArgv = self.getParameter(listArgv)
            else:
                Help = True
                break

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()

            if (project_alias == None) and ((server_alias == None) or (obsproject == None)):
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

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

    def obsproject_set(self, listArgv):
        '''
        
        '''
        Help = False
        title = None
        description = None
        project_alias = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_project_title__:
                title , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_project_description__:
                description , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
            else:
                Help = True
                break

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

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

    def obsproject_import(self, listArgv):
        '''
        
        '''
        Help = False
        path = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                path = currentCommand

                break

        if  (Help == True) and (path != None):
            return self.print_Help()
        else:

            m = ObsLightManager.getCommandLineManager()

            res = m.importProject(path)

            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1
        return 0

    def obsproject_export(self, listArgv):
        '''
        
        '''
        Help = False
        path = None
        project_alias = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                path = currentCommand
                project_alias, listArgv = self.getParameter(listArgv)
                break

        if  (Help == True) and (path != None):
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()

            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            res = m.exportProject(project_alias, path)

            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1
        return 0

    def obsproject_dependencyrepositories(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                project_alias = currentCommand
                break

        if  (Help == True):
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()

            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            res = m.getDependencyRepositories(project_alias)

            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1
            for repo in res.keys():
                print "Repository Alias: " + str(repo) + " Url: " + res[repo]
        return 0

    def execute(self, listArgv):
        '''
        Execute a list of arguments.
        '''
        if len(listArgv) == 0:
            self.print_Help()
            return 0
        else:
            currentCommand = listArgv[0]
            listArgv = listArgv[1:]

            if currentCommand in __command_help__ :
                return self.print_Help()
            elif currentCommand in __command_list__ :
                return self.obsproject_list(listArgv)
            elif currentCommand in __command_add__:
                return self.obsproject_add(listArgv)
            elif currentCommand in __command_del__:
                return self.obsproject_del(listArgv)
            elif currentCommand in __command_query__:
                return self.obsproject_query(listArgv)
            elif currentCommand in __command_set__:
                return self.obsproject_set(listArgv)
            elif currentCommand in __command_current__:
                return self.obsproject_current(listArgv)
            elif currentCommand in  __command_import__ :
                return self.obsproject_import(listArgv)
            elif currentCommand in __command_export__ :
                return self.obsproject_export(listArgv)
            elif currentCommand in __command_dependencyrepositories__:
                return self.obsproject_dependencyrepositories(listArgv)
            else:
                return self.print_Help()

        return 0


class ObsLightObsPackage(ObsLightBase):
    '''
    manage OBSlight server
    '''
    def __init__(self):
        '''
        init class
        '''
        ObsLightBase.__init__(self)

        self.listCommand = __LIST_command_server__
        self.dicoParameterServerCompletion = __DICO_parameter_server_completion__
        self.dicoParameter = __DICO_parameter_server__

        self.dicoCommandHelp = __DICO_command_server_help__

        self.dicoParameterHelp = __DICO_parameter_help__

    def package_add(self, listArgv):
        '''
        
        '''
        Help = False
        package = None
        project_alias = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
            else:
                package = currentCommand

        if  (Help == True) or (package == None) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            return m.addPackage(projectLocalName=project_alias,
                                package=package)

    def package_delete(self, listArgv):
        '''
        
        '''
        Help = False
        package = None
        project_alias = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
            else:
                package = currentCommand

        if  (Help == True) or (package == None) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            return m.removePackage(projectLocalName=project_alias,
                                   package=package)

    def package_list(self, listArgv):
        '''
        
        '''
        Help = False
        available = False
        project_alias = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __package_available__:
                available = True
            elif currentCommand in __parameter_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
            else:
                Help = True
                break

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

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



    def package_query(self, listArgv):
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
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_project_title__:
                title = True
            elif currentCommand in __parameter_project_description__:
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
            elif currentCommand in __parameter_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_alias__:
                server_alias , listArgv = self.getParameter(listArgv)
            elif currentCommand in __obsproject__:
                obsproject , listArgv = self.getParameter(listArgv)
            elif currentCommand in __package_package__:
                package , listArgv = self.getParameter(listArgv)
            else:
                Help = True
                break

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()

            if (package == None) and (project_alias != None):
                package = m.getCurrentPackage(project_alias)
            if package == None:
                return self.print_Help()

            if (project_alias == None) and ((server_alias == None) or (obsproject == None)):
                return self.print_Help()

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

    def package_set(self, listArgv):
        '''
        
        '''
        Help = False

        title = None
        description = None

        project_alias = None
        package = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_project_title__:
                title , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_project_description__:
                description , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
            elif currentCommand in __package_package__:
                package , listArgv = self.getParameter(listArgv)
            else:
                Help = True
                break

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()

            if (project_alias == None) :
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            if (package == None) :
                package = m.getCurrentPackage(project_alias)
                if package == None:
                    return self.print_Help()

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

    def package_update(self, listArgv):
        '''
        
        '''
        Help = False

        project_alias = None
        package = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
            elif currentCommand in __package_package__:
                package , listArgv = self.getParameter(listArgv)
            else:
                Help = True
                break

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()

            if (project_alias == None) :
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            if (package == None) :
                package = m.getCurrentPackage(project_alias)
                if package == None:
                    return self.print_Help()

            res = m.updatePackage(projectLocalName=project_alias,
                                 package=package)
            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1

            return res

    def package_commit(self, listArgv):
        '''
        
        '''
        Help = False

        project_alias = None
        package = None
        message = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                message = currentCommand
                while(len(listArgv) > 0):
                    if currentCommand in __parameter_alias__:
                        project_alias , listArgv = self.getParameter(listArgv)
                    elif currentCommand in __package_package__:
                        package , listArgv = self.getParameter(listArgv)
                    else:
                        break
                break

        if  (Help == True) and (message != None):
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()

            if (project_alias == None) :
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            if (package == None) :
                package = m.getCurrentPackage(project_alias)
                if package == None:
                    return self.print_Help()

            res = m.addAndCommitChanges(project_alias,
                                        package,
                                        message)
            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1
            return res

    def package_repair(self, listArgv):
        '''
        
        '''
        Help = False

        project_alias = None
        package = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
            elif currentCommand in __package_package__:
                package , listArgv = self.getParameter(listArgv)
            else:
                Help = True
                break

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()

            if (project_alias == None) :
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            if (package == None) :
                package = m.getCurrentPackage(project_alias)
                if package == None:
                    return self.print_Help()

            res = m.repairOscPackageDirectory(projectLocalName=project_alias,
                                              package=package)
            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1
            return res

    def package_current(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
            else:
                Help = True
                break

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            return m.getCurrentPackage(projectLocalName=project_alias)
        return 0

    def package_addfile(self, listArgv):
        '''
        
        '''
        Help = False
        path = None
        project_alias = None
        package = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                path = currentCommand
                while(len(listArgv) > 0):
                    currentCommand, listArgv = self.getParameter(listArgv)
                    if currentCommand in __parameter_alias__:
                        project_alias , listArgv = self.getParameter(listArgv)
                    elif currentCommand in __package_package__:
                        package , listArgv = self.getParameter(listArgv)
                    else:
                        break
                break

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            if (package == None) :
                package = m.getCurrentPackage(project_alias)
                if package == None:
                    return self.print_Help()

            return m.addFileToPackage(project_alias, package, path)
        return 0

    def package_deletefile(self, listArgv):
        '''
        
        '''
        Help = False
        name = None
        project_alias = None
        package = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
            else:
                name = currentCommand
                while(len(listArgv) > 0):
                    currentCommand, listArgv = self.getParameter(listArgv)
                    if currentCommand in __parameter_alias__:
                        project_alias , listArgv = self.getParameter(listArgv)
                    elif currentCommand in __package_package__:
                        package , listArgv = self.getParameter(listArgv)
                    else:
                        break
                break

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            if (package == None) :
                package = m.getCurrentPackage(project_alias)
                if package == None:
                    return self.print_Help()

            return m.deleteFileFromPackage(project_alias, package, name)
        return 0

    def package_refresh(self, listArgv):
        '''
        
        '''
        Help = False
        OscStatus = False
        ObsStatus = False
        project_alias = None
        package = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __package_oscstatus__:
                OscStatus = True
            elif currentCommand in __package_obsstatus__:
                ObsStatus = True
            elif currentCommand in __parameter_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
            elif currentCommand in __package_package__:
                package , listArgv = self.getParameter(listArgv)
            else:
                break

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            if not (OscStatus or ObsStatus):
                OscStatus = True
                ObsStatus = True

            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            if (package == None) :
                package = m.getCurrentPackage(project_alias)
                if package == None:
                    return self.print_Help()
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

    def execute(self, listArgv):

        if len(listArgv) == 0:
            self.print_Help()
            return 0
        else:
            currentCommand = listArgv[0]
            listArgv = listArgv[1:]

            if currentCommand in __package_Help__ :
                return self.print_Help()
            elif currentCommand in __package_add__ :
                return self.package_add(listArgv)
            elif currentCommand in __package_delete__:
                return self.package_delete(listArgv)
            elif currentCommand in __package_list__:
                return self.package_list(listArgv)
            elif currentCommand in __package_query__:
                return self.package_query(listArgv)
            elif currentCommand in __package_set__:
                return self.package_set(listArgv)
            elif currentCommand in __package_update__:
                return self.package_update(listArgv)
            elif currentCommand in  __package_commit__ :
                return self.package_commit(listArgv)
            elif currentCommand in __package_repair__ :
                return self.package_repair(listArgv)
            elif currentCommand in __package_current__:
                return self.package_current(listArgv)
            elif currentCommand in __package_addfile__:
                return self.package_addfile(listArgv)
            elif currentCommand in __package_deletefile__:
                return self.package_deletefile(listArgv)
            elif currentCommand in __package_refresh__:
                return self.package_refresh(listArgv)
            else:
                return self.print_Help()

        return 0

class ObsLightObsRepository(ObsLightBase):
    '''
    manage OBSlight server
    '''
    def __init__(self):
        '''
        init class
        '''
        ObsLightBase.__init__(self)

        self.listCommand = __LIST_command_server__
        self.dicoParameterServerCompletion = __DICO_parameter_server_completion__
        self.dicoParameter = __DICO_parameter_server__

        self.dicoCommandHelp = __DICO_command_server_help__

        self.dicoParameterHelp = __DICO_parameter_help__

    def repository_add(self, listArgv):
        '''
        
        '''
        Help = False

        From = False

        url = None
        alias = None
        fromProject = None
        project_alias = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
            elif currentCommand in __repository_From__:
                From = True
                fromProject, listArgv = self.getParameter(listArgv)
                project_alias, listArgv = self.getParameter(listArgv)
                break
            else:
                url = currentCommand
                alias, listArgv = self.getParameter(listArgv)
                project_alias, listArgv = self.getParameter(listArgv)
                break

        if  (Help == True):
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            if From :
                if fromProject == None:
                    return self.print_Help()

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
                    return self.print_Help()
                if alias == None:
                    return self.print_Help()

                res = m.addRepo(projectLocalName=project_alias,
                                fromProject=None,
                                repoUrl=url,
                                alias=alias)
                if res == None:
                    print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                    return -1
                return res

    def repository_delete(self, listArgv):
        '''
        
        '''
        Help = False

        alias = None
        project_alias = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
            else:
                alias = currentCommand
                project_alias, listArgv = self.getParameter(listArgv)
                break

        if  (Help == True):
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            if alias == None:
                return self.print_Help()

            res = m.deleteRepo(projectLocalName=project_alias,
                                repoAlias=alias)

            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1
            return res


    def repository_modify(self, listArgv):
        '''
        
        '''
        Help = False

        alias = None
        project_alias = None
        newUrl = None
        newAlias = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
            else:
                alias = currentCommand
                while(len(listArgv) > 0):
                    currentCommand, listArgv = self.getParameter(listArgv)
                    if currentCommand in __repository_newUrl__:
                        newUrl, listArgv = self.getParameter(listArgv)
                    elif currentCommand in __repository_newAlias__:
                        newAlias, listArgv = self.getParameter(listArgv)
                    else:
                        break
                project_alias, listArgv = self.getParameter(listArgv)
                break

        if  (Help == True):
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()
            if alias == None:
                return self.print_Help()

            if (newUrl == None) and (newAlias == None):
                return self.print_Help()

            res = m.modifyRepo(projectLocalName=project_alias,
                               repoAlias=alias,
                               newUrl=newUrl,
                               newAlias=newAlias)

            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1
            return res

    def repository_query(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else :
                project_alias = currentCommand


        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()
            res = m.getChRootRepositories(projectLocalName=project_alias)
            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1
            print "repositories:"
            for k in res:
                print "Alias: " + k + "\t\tURL: " + res[k]
        return 0

    def execute(self, listArgv):
        if len(listArgv) == 0:
            return self.print_Help()
        else:
            currentCommand = listArgv[0]
            listArgv = listArgv[1:]

            if currentCommand in __command_help__ :
                return self.print_Help()
            elif currentCommand in __repository_add__:
                return self.repository_add(listArgv)
            elif currentCommand in __repository_delete__ :
                return self.repository_delete(listArgv)
            elif currentCommand in __repository_modify__:
                return self.repository_modify(listArgv)
            elif currentCommand in __repository_query__:
                return self.repository_query(listArgv)
            else:
                return self.print_Help()
        return 0


class ObsLightObsProjectfilesystem(ObsLightBase):
    '''
    manage OBSlight server
    '''
    def __init__(self):
        '''
        init class
        '''
        ObsLightBase.__init__(self)

        self.listCommand = __LIST_command_server__
        self.dicoParameterServerCompletion = __DICO_parameter_server_completion__
        self.dicoParameter = __DICO_parameter_server__

        self.dicoCommandHelp = __DICO_command_server_help__

        self.dicoParameterHelp = __DICO_parameter_help__

    def projectfilesystem_create(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                project_alias = currentCommand

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            res = m.createChRoot(projectLocalName=project_alias)
            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1
            return res
        return 0

    def projectfilesystem_delete(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
            else:
                Help = True
                break

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            res = m.removeChRoot(projectLocalName=project_alias)
            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1
            return res
        return 0

    def projectfilesystem_query(self, listArgv):
        '''
        
        '''
        Help = False
        path = False
        status = False

        project_alias = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __projectfilesystem_path__:
                path = True
            elif currentCommand in __projectfilesystem_status__:
                status = True
            elif currentCommand in __parameter_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
            else:
                Help = True
                break

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()

            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

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

    def projectfilesystem_enter(self, listArgv):
        '''
        
        '''
        Help = False

        project_alias = None
        package = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __package_package__:
                package , listArgv = self.getParameter(listArgv)
            else:
                project_alias = currentCommand

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            res = m.goToChRoot(projectLocalName=project_alias, package=package)
            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1
            return res
        return 0

    def projectfilesystem_executescript(self, listArgv):
        '''
        
        '''
        Help = False
        aPath = None

        project_alias = None


        currentCommand, listArgv = self.getParameter(listArgv)
        if (currentCommand in __command_help__) or (listArgv == None):
            Help = True
        else:
            aPath = currentCommand
            project_alias, listArgv = self.getParameter(listArgv)

        if  (Help == True)  :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()
            if aPath == None:
                return self.print_Help()

            res = m.execScript(projectLocalName=project_alias, aPath=aPath)
            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1
            return res
        return 0

    def projectfilesystem_repository(self, listArgv):
        '''
        
        '''
        ObsLightObsRepository().execute(listArgv)

    def execute(self, listArgv):
        if len(listArgv) == 0:
            return self.print_Help()
        else:
            currentCommand = listArgv[0]
            listArgv = listArgv[1:]

            if currentCommand in __projectfilesystem_Help__ :
                return self.print_Help()
            elif currentCommand in __projectfilesystem_create__ :
                return self.projectfilesystem_create(listArgv)
            elif currentCommand in __projectfilesystem_delete__:
                return self.projectfilesystem_delete(listArgv)
            elif currentCommand in __projectfilesystem_query__:
                return self.projectfilesystem_query(listArgv)
            elif currentCommand in __projectfilesystem_enter__:
                return self.projectfilesystem_enter(listArgv)
            elif currentCommand in __projectfilesystem_executescript__:
                return self.projectfilesystem_executescript(listArgv)
            elif currentCommand in __projectfilesystem_repository__:
                return self.projectfilesystem_repository(listArgv)
            else:
                return self.print_Help()
        return 0



class ObsLightRpmbuild(ObsLightBase):
    '''
    manage OBSlight server
    '''
    def __init__(self):
        '''
        init class
        '''
        ObsLightBase.__init__(self)

        self.listCommand = __LIST_command_server__
        self.dicoParameterServerCompletion = __DICO_parameter_server_completion__
        self.dicoParameter = __DICO_parameter_server__

        self.dicoCommandHelp = __DICO_command_server_help__

        self.dicoParameterHelp = __DICO_parameter_help__

    def rpmbuild_prepare(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None
        package = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
            else :
                package = currentCommand

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            if (package == None):
                package = m.getCurrentPackage(project_alias)

            res = m.addPackageSourceInChRoot(projectLocalName=project_alias, package=package)
            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1
        return 0

    def rpmbuild_build(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None
        package = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
            else :
                package = currentCommand

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            if (package == None):
                package = m.getCurrentPackage(project_alias)

            res = m.buildRpm(projectLocalName=project_alias, package=package)
            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1
        return 0

    def rpmbuild_install(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None
        package = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
            else :
                package = currentCommand

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            if (package == None):
                package = m.getCurrentPackage(project_alias)

            res = m.installRpm(projectLocalName=project_alias, package=package)
            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1
        return 0

    def rpmbuild_package(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None
        package = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
            else :
                package = currentCommand

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()
            if project_alias == None:
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            if (package == None):
                package = m.getCurrentPackage(project_alias)

            res = m.packageRpm(projectLocalName=project_alias, package=package)
            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1
        return 0

    def rpmbuild_isInit(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None
        package = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
            elif currentCommand in __package_package__:
                package , listArgv = self.getParameter(listArgv)
            else:
                Help = True
                break

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()

            if (project_alias == None) :
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            if (package == None) :
                package = m.getCurrentPackage(project_alias)
                if package == None:
                    return self.print_Help()

            print
            res = m.patchIsInit(projectLocalName=project_alias, packageName=package)
            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1
            print "for '" + package + "' a patch is init: " + str(res)
            return 0

    def rpmbuild_createPatch(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None
        package = None
        patch = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                patch = currentCommand
                while (len(listArgv) > 0):
                    if currentCommand in __parameter_alias__:
                        project_alias , listArgv = self.getParameter(listArgv)
                    elif currentCommand in __package_package__:
                        package , listArgv = self.getParameter(listArgv)
                    else:
                        break
                break

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()

            if (project_alias == None) :
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            if (package == None) :
                package = m.getCurrentPackage(project_alias)
                if package == None:
                    return self.print_Help()

            if (patch == None) :
                return self.print_Help()

            res = m.createPatch(projectLocalName=project_alias, package=package, patch=patch)
            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1
            return 0

    def rpmbuild_updatepatch(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None
        package = None

        while(len(listArgv) > 0):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
            elif currentCommand in __package_package__:
                package , listArgv = self.getParameter(listArgv)
            else:
                Help = True
                break

        if  (Help == True) :
            return self.print_Help()
        else:
            m = ObsLightManager.getCommandLineManager()

            if (project_alias == None) :
                project_alias = m.getCurrentObsProject()
                if project_alias == None:
                    return self.print_Help()

            if (package == None) :
                package = m.getCurrentPackage(project_alias)
                if package == None:
                    return self.print_Help()

            print "project_alias", project_alias
            print "package", package
            res = m.updatePatch(projectLocalName=project_alias, package=package)
            if res == None:
                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                return -1
            return 0

    def rpmbuild_testConflict(self):
        '''
        
        '''
        m = ObsLightManager.getCommandLineManager()
        return m.testConflict(projectLocalName=None, package=None)

    def execute(self, listArgv):
        '''
        Execute a list of arguments.
        '''
        if len(listArgv) == 0:
            return self.print_Help()
        else:
            currentCommand = listArgv[0]
            listArgv = listArgv[1:]

            if currentCommand in __command_help__ :
                return self.print_Help()
            elif currentCommand in __rpmbuild_prepare__:
                return self.rpmbuild_prepare(listArgv)
            elif currentCommand in __rpmbuild_build__ :
                return self.rpmbuild_build(listArgv)
            elif currentCommand in __rpmbuild_install__:
                return self.rpmbuild_install(listArgv)
            elif currentCommand in __rpmbuild_package__:
                return self.rpmbuild_package(listArgv)
            elif currentCommand in __rpmbuild_isInit__:
                return self.rpmbuild_isInit(listArgv)
            elif currentCommand in __rpmbuild_testConflict__:
                return self.rpmbuild_testConflict()
            elif currentCommand in __rpmbuild_createPatch__:
                return self.rpmbuild_createPatch(listArgv)
            elif currentCommand in __rpmbuild_updatepatch__:
                return self.rpmbuild_updatepatch(listArgv)
            else:
                return self.print_Help()
        return 0

class ObsLight(ObsLightBase):
    '''
    manage OBSlight
    '''
    def __init__(self):
        '''
        
        '''
        ObsLightBase.__init__(self)


    def execute(self, listArgv):
        '''
        Execute a list of arguments.
        '''

        ObsLightPrintManager.quiet = 0
        ObsLightPrintManager.DEBUG = 0

        #If no argument print help
        if len(listArgv) == 0:
            return self.globalDescription()
        elif len(listArgv) > 0:
            #Set the global variable
            currentCommand, listArgv = self.getParameter(listArgv)

            while(currentCommand != None):
                #only use for completion
                if currentCommand in __noaction__:
                    ObsLightBase.noaction = True
                    currentCommand, listArgv = self.getParameter(listArgv)
                    continue

                elif currentCommand in __info_quiet__:
                    ObsLightPrintManager.QUIET = 1
                    ObsLightPrintManager.setLoggerLevel('CRITICAL')
                    currentCommand, listArgv = self.getParameter(listArgv)
                    continue

                elif currentCommand in __info_debug__:
                    ObsLightPrintManager.DEBUG = 1
                    ObsLightPrintManager.setLoggerLevel('DEBUG')
                    currentCommand, listArgv = self.getParameter(listArgv)
                    continue

                elif currentCommand in __version__:
                    return self.printVersion()

                elif currentCommand in __command_help__:
                    return self.printDescriptionLevel0()
                else :
                    break

            if currentCommand == None:
                return self.printDescriptionLevel0()
            else:
                if currentCommand in __server__ :
                    return ObsLightServer().execute(listArgv)
                elif currentCommand in __obsproject__ :
                    return ObsLightObsproject().execute(listArgv)
                elif currentCommand in __Package__ :
                    return ObsLightObsPackage().execute(listArgv)
                elif currentCommand in __projectfilesystem__ :
                    return ObsLightObsProjectfilesystem().execute(listArgv)
                elif currentCommand in __rpmbuild__ :
                    return ObsLightRpmbuild().execute(listArgv)
                elif currentCommand in __micproject__ :
                    return self.micproject(listArgv)
#                elif currentCommand in __qemuproject__ :
#                    return self.qemuproject(listArgv)
                else:
                    return self.printUnknownCommand(currentCommand, __LIST_command__)

#class ObsLightRpmbuild(ObsLightBase):
#    '''
#    manage OBSlight server
#    '''
#    def __init__(self):
#        '''
#        init class
#        '''
#        ObsLightBase.__init__(self)
#
#        self.listCommand = __LIST_command_server__
#        self.dicoParameterServerCompletion = __DICO_parameter_server_completion__
#        self.dicoParameter = __DICO_parameter_server__
#
#        self.dicoCommandHelp = __DICO_command_server_help__
#
#        self.dicoParameterHelp = __DICO_parameter_help__
#
#    def rpmbuild_prepare(self, listArgv):
#        '''
#        
#        '''
#        Help = False
#        project_alias = None
#        package = None
#
#        while(len(listArgv) > 0):
#            currentCommand, listArgv = self.getParameter(listArgv)
#            if (currentCommand in __command_help__) or (listArgv == None):
#                Help = True
#                break
#            elif currentCommand in __parameter_alias__:
#                project_alias, listArgv = self.getParameter(listArgv)
#            else :
#                package = currentCommand
#
#        if  (Help == True) :
#            return self.print_Help()
#        else:
#            m = ObsLightManager.getCommandLineManager()
#            if project_alias == None:
#                project_alias = m.getCurrentObsProject()
#                if project_alias == None:
#                    return self.print_Help()
#
#            if (package == None):
#                package = m.getCurrentPackage(project_alias)
#
#            res = m.addPackageSourceInChRoot(projectLocalName=project_alias, package=package)
#            if res == None:
#                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
#                return -1
#        return 0
#
#    def rpmbuild_build(self, listArgv):
#        '''
#        
#        '''
#        Help = False
#        project_alias = None
#        package = None
#
#        while(len(listArgv) > 0):
#            currentCommand, listArgv = self.getParameter(listArgv)
#            if (currentCommand in __command_help__) or (listArgv == None):
#                Help = True
#                break
#            elif currentCommand in __parameter_alias__:
#                project_alias, listArgv = self.getParameter(listArgv)
#            else :
#                package = currentCommand
#
#        if  (Help == True) :
#            return self.print_Help()
#        else:
#            m = ObsLightManager.getCommandLineManager()
#            if project_alias == None:
#                project_alias = m.getCurrentObsProject()
#                if project_alias == None:
#                    return self.print_Help()
#
#            if (package == None):
#                package = m.getCurrentPackage(project_alias)
#
#            res = m.buildRpm(projectLocalName=project_alias, package=package)
#            if res == None:
#                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
#                return -1
#        return 0
#
#    def rpmbuild_install(self, listArgv):
#        '''
#        
#        '''
#        Help = False
#        project_alias = None
#        package = None
#
#        while(len(listArgv) > 0):
#            currentCommand, listArgv = self.getParameter(listArgv)
#            if (currentCommand in __command_help__) or (listArgv == None):
#                Help = True
#                break
#            elif currentCommand in __parameter_alias__:
#                project_alias, listArgv = self.getParameter(listArgv)
#            else :
#                package = currentCommand
#
#        if  (Help == True) :
#            return self.print_Help()
#        else:
#            m = ObsLightManager.getCommandLineManager()
#            if project_alias == None:
#                project_alias = m.getCurrentObsProject()
#                if project_alias == None:
#                    return self.print_Help()
#
#            if (package == None):
#                package = m.getCurrentPackage(project_alias)
#
#            res = m.installRpm(projectLocalName=project_alias, package=package)
#            if res == None:
#                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
#                return -1
#        return 0
#
#    def rpmbuild_package(self, listArgv):
#        '''
#        
#        '''
#        Help = False
#        project_alias = None
#        package = None
#
#        while(len(listArgv) > 0):
#            currentCommand, listArgv = self.getParameter(listArgv)
#            if (currentCommand in __command_help__) or (listArgv == None):
#                Help = True
#                break
#            elif currentCommand in __parameter_alias__:
#                project_alias, listArgv = self.getParameter(listArgv)
#            else :
#                package = currentCommand
#
#        if  (Help == True) :
#            return self.print_Help()
#        else:
#            m = ObsLightManager.getCommandLineManager()
#            if project_alias == None:
#                project_alias = m.getCurrentObsProject()
#                if project_alias == None:
#                    return self.print_Help()
#
#            if (package == None):
#                package = m.getCurrentPackage(project_alias)
#
#            res = m.packageRpm(projectLocalName=project_alias, package=package)
#            if res == None:
#                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
#                return -1
#        return 0
#
#    def rpmbuild_isInit(self, listArgv):
#        '''
#        
#        '''
#        Help = False
#        project_alias = None
#        package = None
#
#        while(len(listArgv) > 0):
#            currentCommand, listArgv = self.getParameter(listArgv)
#            if (currentCommand in __command_help__) or (listArgv == None):
#                Help = True
#                break
#            elif currentCommand in __parameter_alias__:
#                project_alias , listArgv = self.getParameter(listArgv)
#            elif currentCommand in __package_package__:
#                package , listArgv = self.getParameter(listArgv)
#            else:
#                Help = True
#                break
#
#        if  (Help == True) :
#            return self.print_Help()
#        else:
#            m = ObsLightManager.getCommandLineManager()
#
#            if (project_alias == None) :
#                project_alias = m.getCurrentObsProject()
#                if project_alias == None:
#                    return self.print_Help()
#
#            if (package == None) :
#                package = m.getCurrentPackage(project_alias)
#                if package == None:
#                    return self.print_Help()
#
#            print
#            res = m.patchIsInit(projectLocalName=project_alias, packageName=package)
#            if res == None:
#                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
#                return -1
#            print "for '" + package + "' a patch is init: " + str(res)
#            return 0
#
#    def rpmbuild_createPatch(self, listArgv):
#        '''
#        
#        '''
#        Help = False
#        project_alias = None
#        package = None
#        patch = None
#
#        while(len(listArgv) > 0):
#            currentCommand, listArgv = self.getParameter(listArgv)
#            if (currentCommand in __command_help__) or (listArgv == None):
#                Help = True
#                break
#            else:
#                patch = currentCommand
#                while (len(listArgv) > 0):
#                    if currentCommand in __parameter_alias__:
#                        project_alias , listArgv = self.getParameter(listArgv)
#                    elif currentCommand in __package_package__:
#                        package , listArgv = self.getParameter(listArgv)
#                    else:
#                        break
#                break
#
#        if  (Help == True) :
#            return self.print_Help()
#        else:
#            m = ObsLightManager.getCommandLineManager()
#
#            if (project_alias == None) :
#                project_alias = m.getCurrentObsProject()
#                if project_alias == None:
#                    return self.print_Help()
#
#            if (package == None) :
#                package = m.getCurrentPackage(project_alias)
#                if package == None:
#                    return self.print_Help()
#
#            if (patch == None) :
#                return self.print_Help()
#
#            res = m.createPatch(projectLocalName=project_alias, package=package, patch=patch)
#            if res == None:
#                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
#                return -1
#            return 0
#
#    def rpmbuild_updatepatch(self, listArgv):
#        '''
#        
#        '''
#        Help = False
#        project_alias = None
#        package = None
#
#        while(len(listArgv) > 0):
#            currentCommand, listArgv = self.getParameter(listArgv)
#            if (currentCommand in __command_help__) or (listArgv == None):
#                Help = True
#                break
#            elif currentCommand in __parameter_alias__:
#                project_alias , listArgv = self.getParameter(listArgv)
#            elif currentCommand in __package_package__:
#                package , listArgv = self.getParameter(listArgv)
#            else:
#                Help = True
#                break
#
#        if  (Help == True) :
#            return self.print_Help()
#        else:
#            m = ObsLightManager.getCommandLineManager()
#
#            if (project_alias == None) :
#                project_alias = m.getCurrentObsProject()
#                if project_alias == None:
#                    return self.print_Help()
#
#            if (package == None) :
#                package = m.getCurrentPackage(project_alias)
#                if package == None:
#                    return self.print_Help()
#
#            print "project_alias", project_alias
#            print "package", package
#            res = m.updatePatch(projectLocalName=project_alias, package=package)
#            if res == None:
#                print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
#                return -1
#            return 0
#
#    def rpmbuild_testConflict(self, listArgv):
#        '''
#        
#        '''
#        Help = False
#        m = ObsLightManager.getCommandLineManager()
#        return m.testConflict(projectLocalName=None, package=None)
#
#    def execute(self, listArgv):
#        '''
#        Execute a list of arguments.
#        '''
#
#        if len(listArgv) == 0:
#            return self.print_Help()
#        else:
#            currentCommand = listArgv[0]
#            listArgv = listArgv[1:]
#
#            if currentCommand in __command_help__ :
#                return self.print_Help()
#            elif currentCommand in __rpmbuild_prepare__:
#                return self.rpmbuild_prepare(listArgv)
#            elif currentCommand in __rpmbuild_build__ :
#                return self.rpmbuild_build(listArgv)
#            elif currentCommand in __rpmbuild_install__:
#                return self.rpmbuild_install(listArgv)
#            elif currentCommand in __rpmbuild_package__:
#                return self.rpmbuild_package(listArgv)
#            elif currentCommand in __rpmbuild_isInit__:
#                return self.rpmbuild_isInit(listArgv)
#            elif currentCommand in __rpmbuild_testConflict__:
#                return self.rpmbuild_testConflict(listArgv)
#            elif currentCommand in __rpmbuild_createPatch__:
#                return self.rpmbuild_createPatch(listArgv)
#            elif currentCommand in __rpmbuild_updatepatch__:
#                return self.rpmbuild_updatepatch(listArgv)
#            else:
#                return self.print_Help()
#        return 0

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
