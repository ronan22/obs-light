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

def createCommandMicprojectHelp(command, comment):
    '''
    format end store command/documentation for Micproject command
    '''
    __DICO_command_micproject_help__[command[0]] = createDoc(command, comment)

def createCommandRpmbuildHelp(command, comment):
    '''
    format end store command/documentation for Rpmbuild command
    '''
    __DICO_command_rpmbuild_help__[command[0]] = createDoc(command, comment)

def createCommandRepositoryHelp(command, comment):
    '''
    format end store command/documentation for Micproject command
    '''
    __DICO_command_repositories_help__[command[0]] = createDoc(command, comment)

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

def appendCommandRepositories(command):
    """
    Append sub command to command Repositories
    """
    __LIST_repositories__.append(command[0])

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
        if (completionBlacklist == None) or (not parameter in  completionBlacklist):
            if not command[0] in __DICO_parameter_server_completion__.keys():
                __DICO_parameter_server_completion__[command[0]] = []
            __DICO_parameter_server_completion__[command[0]].append(parameter[0])

def createParameterObsproject(command, parameterList, completionBlacklist=None):
    '''
    Add parameter to the sub command of Obsproject, the parameter are automatically add
    to the completion list except if present on the completionBlacklist.
    '''
    __DICO_parameter_obsproject__[command[0]] = []
    for parameter in parameterList:
        __DICO_parameter_obsproject__[command[0]].append(parameter[0])
        if (completionBlacklist == None) or (not parameter in  completionBlacklist):
            if not command[0] in __DICO_parameter_obsproject_completion__.keys():
                __DICO_parameter_obsproject_completion__[command[0]] = []
            __DICO_parameter_obsproject_completion__[command[0]].append(parameter[0])

def createParameterPackage(command, parameterList, completionBlacklist=None):
    '''
    Add parameter to the sub command of Package, the parameter are automatically add
    to the completion list except if present on the completionBlacklist.
    '''
    __DICO_parameter_package__[command[0]] = []
    for parameter in parameterList:
        __DICO_parameter_package__[command[0]].append(parameter[0])
        if (completionBlacklist == None) or (not parameter in  completionBlacklist):
            if not command[0] in __DICO_parameter_package_completion__.keys():
                __DICO_parameter_package_completion__[command[0]] = []
            __DICO_parameter_package_completion__[command[0]].append(parameter[0])

def createParameterFilesystem(command, parameterList, completionBlacklist=None):
    '''
    Add parameter to the sub command of Filesystem, the parameter are automatically add
    to the completion list except if present on the completionBlacklist.
    '''
    __DICO_parameter_filesystem__[command[0]] = []
    for parameter in parameterList:
        __DICO_parameter_filesystem__[command[0]].append(parameter[0])
        if (completionBlacklist == None) or (not parameter in  completionBlacklist):
            if not command[0] in __DICO_parameter_filesystem_completion__.keys():
                __DICO_parameter_filesystem_completion__[command[0]] = []
            __DICO_parameter_filesystem_completion__[command[0]].append(parameter[0])

def createParameterRepositories(command, parameterList, completionBlacklist=None):
    '''
    Add parameter to the sub command of repositories, the parameter are automatically add
    to the completion list except if present on the completionBlacklist.
    '''
    __DICO_parameter_repositories__[command[0]] = []
    for parameter in parameterList:
        __DICO_parameter_repositories__[command[0]].append(parameter[0])
        if (completionBlacklist == None) or (not parameter in  completionBlacklist):
            if not command[0] in __DICO_parameter_repositories_completion__.keys():
                __DICO_parameter_repositories_completion__[command[0]] = []
            __DICO_parameter_repositories_completion__[command[0]].append(parameter[0])

def createParameterRpmbuild(command, parameterList, completionBlacklist=None):
    '''
    Add parameter to the sub command of Rpmbuild, the parameter are automatically add
    to the completion list except if present on the completionBlacklist.
    '''
    __DICO_parameter_rpmbuild__[command[0]] = []
    for parameter in parameterList:
        __DICO_parameter_rpmbuild__[command[0]].append(parameter[0])
        if (completionBlacklist == None) or (not parameter in  completionBlacklist):
            if not command[0] in __DICO_parameter_rpmbuild_completion__.keys():
                __DICO_parameter_rpmbuild_completion__[command[0]] = []
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
            if not command[0] in __DICO_parameter_micproject_completion__.keys():
                __DICO_parameter_micproject_completion__[command[0]] = []
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

__SYNTAX_HELP__ = 'syntax used:\n'
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
__LIST_repositories__ = []
__LIST_rpmbuild__ = []
__LIST_micproject__ = []
#__LIST_qemuproject__ = []

#Define the **** command help
__DICO_command_server_help__ = {}
__DICO_command_obsproject_help__ = {}
__DICO_command_package_help__ = {}
__DICO_command_filesystem_help__ = {}
__DICO_command_repositories_help__ = {}
__DICO_command_rpmbuild_help__ = {}
__DICO_command_micproject_help__ = {}
#__DICO_command_qemuproject_help__ = {}

#Command **** parameter 
__DICO_parameter_server__ = {}
__DICO_parameter_obsproject__ = {}
__DICO_parameter_package__ = {}
__DICO_parameter_filesystem__ = {}
__DICO_parameter_repositories__ = {}
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
__DICO_parameter_repositories_completion__ = {}
__DICO_parameter_rpmbuild_completion__ = {}
__DICO_parameter_micproject_completion__ = {}
__DICO_parameter_qemuproject_completion__ = {}

#Command 
__info_quiet__ = ["quiet", "-quiet", "--quiet"]
__info_debug__ = ["debug", "-debug", "--debug"]
__version__ = ["version", "--version"]
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
__command_import__ = ["import"]
__command_export__ = ["export"]
__command_dependencyrepositories__ = ["dependencyrepositories", "deprepo"]
__command_update__ = ["update", "up"]
__command_commit__ = ["commit", "co"]
__command_repair__ = ["repair"]
__command_addfile__ = ["addfile"]
__command_deletefile__ = ["deletefile"]
__command_refresh__ = ["refresh"]
__command_create__ = ["create", "new"]
__command_enter__ = ["enter", "chroot"]
__command_executescript__ = ["executescript", "exec"]
__command_repositories__ = ["repositories"]
__command_prepare__ = ["prepare"]
__command_build__ = ["build"]
__command_install__ = ["install"]
__command_buildpackage__ = ["buildpackage"]
__command_isInit__ = ["isinit"]
__command_testConflict__ = ["testconflict"]
__command_resolveConflict__ = ["resolveConflict"]
__command_createPatch__ = ["createpatch"]
__command_updatepatch__ = ["updatepatch"]
__command_modify__ = ["modify"]

#Parameter 
__parameter_reachable__ = ["reachable"]
__parameter_server_alias__ = ["server_alias", "alias"]
__parameter_login__ = ["login", "user"]
__parameter_password__ = ["password", "pwd"]
__parameter_api_url__ = ["api_url"]
__parameter_repository_url__ = ["repository_url"]
__parameter_web_url__ = ["web_url"]
__parameter_raw__ = ["raw"]
__parameter_project_alias__ = ["project_alias"]
__parameter_name_on_obs__ = ["name_on_obs"]
__parameter_project_title__ = ["title"]
__parameter_project_description__ = ["description"]
__parameter_server__ = ["server"]
__parameter_project__ = ["project"]
__parameter_webpage__ = ["webpage"]
__parameter_repository__ = ["repository"]
__parameter_target__ = ["target"]
__parameter_arch__ = ["arch", "architecture"]
__parameter_maintainer__ = ["maintainer"]
__parameter_bugowner__ = ["bugowner"]
__parameter_remoteurl__ = ["remoteurl"]
__parameter_path__ = ["path"]
__parameter_package__ = ["package", "pkg"]
__parameter_available__ = ["available"]
__parameter_status__ = ["status"]
__parameter_revision__ = ["revision"]
__parameter_url__ = ["url"]
__parameter_obsRev__ = ["obsRev"]
__parameter_oscRev__ = ["oscRev"]
__parameter_listFile__ = ["listFile"]
__parameter_listFile_status__ = ["listFile_status"]
__parameter_obsstatus__ = ["obsStatus"]
__parameter_oscstatus__ = ["oscStatus"]
__parameter_specFile__ = ["specFile"]
__parameter_yamlFile__ = ["yamlFile"]
__parameter_fsPackageDirectory__ = ["fspackagedirectory"]
__parameter_oscPackageDirectory__ = ["oscpackagedirectory"]
__parameter_filesystemstatus__ = ["status"]
__parameter_currentPatch__ = ["currentpatch"]
__parameter_package_title__ = ["title"]
__parameter_packge_description__ = ["description"]
__parameter_message__ = ["message", "msg"]
__parameter_file__ = ["file"]
__parameter_From__ = ["from"]
__parameter_newUrl__ = ["newUrl"]
__parameter_newAlias__ = ["newAlias"]
__parameter_repo_url__ = ["repository_url"]
__parameter_repo_alias__ = ["repository_alias"]

#Define the server parameter help
createParameterHelp(__command_help__, __help_command_help__)
createParameterHelp(__parameter_reachable__, ["[reachable] optional"])
createParameterHelp(__parameter_server_alias__, "the alias of an OBS server ")
createParameterHelp(__parameter_login__, "the login for a account on an OBS server")
createParameterHelp(__parameter_password__, "the password for a account on an OBS server")
createParameterHelp(__parameter_api_url__, "the URL of an OBS server API")
createParameterHelp(__parameter_repository_url__, "the URL of an OBS server repository")
createParameterHelp(__parameter_web_url__, "the URL of an OBS server web")
createParameterHelp(__parameter_raw__, "no filter on the project list")
createParameterHelp(__parameter_project_alias__ , "the name of the obslight project on the locale drive.")
createParameterHelp(__parameter_name_on_obs__ , "the name of the project on the OBS server")
createParameterHelp(__parameter_project_title__ , "the title of a project")
createParameterHelp(__parameter_project_description__ , "the description of a project")
createParameterHelp(__parameter_server__ , "the ???")
createParameterHelp(__parameter_project__ , "the name of the project on the OBS sever.")
createParameterHelp(__parameter_webpage__ , "the webpage of the OBS project management ")
createParameterHelp(__parameter_repository__ , "the repository is the file depot of a OBS Project.")
createParameterHelp(__parameter_target__ , "the target repository of an OBS project")
createParameterHelp(__parameter_arch__ , "the architecture of an OBS project")
createParameterHelp(__parameter_maintainer__ , "the maintainer of an OBS project")
createParameterHelp(__parameter_bugowner__ , "the bugowner of an OBS project")
createParameterHelp(__parameter_remoteurl__ , "an OBS project can build again a remote project throught a remote project link")
createParameterHelp(__parameter_path__ , "a file path")
createParameterHelp(__parameter_package__, "a package name")
createParameterHelp(__parameter_available__, "result is available ")
createParameterHelp(__parameter_status__, "the status")
createParameterHelp(__parameter_revision__, "the revision")
createParameterHelp(__parameter_url__, "the url")
createParameterHelp(__parameter_obsRev__, "the server package OBS revision")
createParameterHelp(__parameter_oscRev__, "the osc local revision")
createParameterHelp(__parameter_listFile__, "the list of file of a package")
createParameterHelp(__parameter_listFile_status__, "the list of file of a package with status.")
createParameterHelp(__parameter_obsstatus__, "the OBS status")
createParameterHelp(__parameter_oscstatus__, "osc status")
createParameterHelp(__parameter_specFile__, "the spec file name")
createParameterHelp(__parameter_yamlFile__, "the yaml file name")
createParameterHelp(__parameter_fsPackageDirectory__, "the directory of the project file system")
createParameterHelp(__parameter_oscPackageDirectory__, "the osc package directory")
createParameterHelp(__parameter_filesystemstatus__, "the project file system directory")
createParameterHelp(__parameter_currentPatch__, "the name of the current patch of the local package")
createParameterHelp(__parameter_package_title__, "the title of a package")
createParameterHelp(__parameter_packge_description__, "the description of a package")
createParameterHelp(__parameter_message__, "a text message")
createParameterHelp(__parameter_file__, "a file name")
createParameterHelp(__parameter_From__, "specify the local project")
createParameterHelp(__parameter_newUrl__, "the new url of the repository")
createParameterHelp(__parameter_newAlias__, "the new alias of the repository")
createParameterHelp(__parameter_repo_url__, "the url of a repository")
createParameterHelp(__parameter_repo_alias__, "the alias of a repository")

#obslight   
#    server
#    obsproject
#    package
#    filesystem
#    rpmbuild
#    micproject #Feature
#    qemuproject #Feature

#Global command
__server__ = ["server"]
__obsproject__ = ["obsproject"]
__Package__ = ["package"]
__projectfilesystem__ = ["projectfilesystem", "projectfs", "filesystem", "pfs"]
__rpmbuild__ = ["rpmbuild", "rb"]
#__micproject__ = ["micproject"] #Feature
__man__ = ["man"]
#__qemuproject__ = ["qemuproject"] #Feature

createCommand(__server__)
createCommand(__obsproject__)
createCommand(__Package__)
createCommand(__projectfilesystem__)
createCommand(__rpmbuild__)
#createCommand(__micproject__) #Feature
createCommand(__man__)
#createCommand(__qemuproject__) #Feature

createCommandHelp(__server__, "Manage the OBS server")
createCommandHelp(__obsproject__, "Manage the OBSlight project")
createCommandHelp(__Package__, "Manage the packages of OBSlight project")
createCommandHelp(__projectfilesystem__, "Manage the project filesystem of OBSlight project")
createCommandHelp(__rpmbuild__, "Manage the rpmbuild of the package into the project filesystem")
#createCommandHelp(__micproject__, "Manage image biulding") #Feature
createCommandHelp(__man__, "print the man help document")
createCommandHelp(__command_repositories__, ["the command for file system repositorie"])
#createCommandHelp(__qemuproject__, "Manage qemu") #Feature

#    server    test    server_alias <server_alias> 
#    server    test    login <login> password <password> api_url <api_url> 
#    server    list      [reachable]
#    server    query    [login|apiurl|repository_url|weburl] {server_alias <server_alias>}
#    server    set        [login <login>] [apiurl <apiurl>] [repository_url <repository_url>] [weburl <web_url>] {server_alias <server_alias>}
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

createCommandServerHelp(__command_test__, ["server test server_alias <server_alias>",
                                           "test the server alias",
                                           "login <login> password <password> api_url <api_url> ",
                                           "test the API URL."])

createCommandServerHelp(__command_list__, ["server list [reachable]",
                                           "if reachable  -> return all sever",
                                           "else  -> return only the available server"])

createCommandServerHelp(__command_query__, ["server query [login|apiurl|repository_url|weburl] {server_alias <server_alias>}",
                                            "return the server parameter."])

createCommandServerHelp(__command_set__, ["server set [login <login>] [apiurl <apiurl>] [repository_url <repository_url>] [weburl <web_url>] {server_alias <server_alias>}",
                                          "set the server parameter"])

createCommandServerHelp(__command_add__, ["server add server_alias <server_alias> login <login> password <password> api_url <api_url> repository_url <repository_url> web_url <web_url>",
                                          "add a new OBS server"])

createCommandServerHelp(__command_del__, ["server delete <server_alias> ",
                                          "del an OBS server"])

createCommandServerHelp(__command_current__, ["server current BLANK",
                                              "return the current OBS server"])

#Define the parameter list for server command
createParameterServer(__command_test__, [__command_help__,
                                         __parameter_server_alias__,
                                         __parameter_login__,
                                         __parameter_password__,
                                         __parameter_api_url__])

createParameterServer(__command_list__, [__parameter_reachable__, __command_help__])

createParameterServer(__command_query__, [__command_help__,
                                          __parameter_server_alias__,
                                          __parameter_login__,
                                          __parameter_api_url__,
                                          __parameter_repository_url__,
                                          __parameter_web_url__])

createParameterServer(__command_set__, [__command_help__,
                                        __parameter_server_alias__,
                                        __parameter_login__,
                                        __parameter_api_url__,
                                        __parameter_repository_url__,
                                        __parameter_web_url__])

createParameterServer(__command_add__, [__command_help__,
                                        __parameter_server_alias__,
                                        __parameter_login__,
                                        __parameter_password__,
                                        __parameter_api_url__,
                                        __parameter_repository_url__,
                                        __parameter_web_url__])

createParameterServer(__command_del__, [__command_help__,
                                        __parameter_server_alias__], [__parameter_server_alias__])

createParameterServer(__command_current__, [__command_help__])

#    obsproject    list    BLANK
#    obsproject    list    server_alias <server_alias> raw|[arch <arch>|maintainer|bugowner|remoteurl]
#    obsproject    current BLANK
#    obsproject    dependencyrepositories {<project_alias>}
#    obsproject    delete    <project_alias>
#    obsproject    add    <project_alias> <name_on_obs> <target> <arch> {<server_alias>}
#    obsproject    query    [title|description|obsServer|webpage|repository|target|architecture] {project_alias <project_alias>}
#    obsproject    query    [title|description|target|architecture|remoteurl|maintainer|bugowner] server_alias <server_alias> obsproject <project> 
#    obsproject    set    [title <title>] [description <description>] {project_alias <project_alias>}
#    obsproject    import    <path>
#    obsproject    export  <path> {<project_alias>}

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

#Define the obsproject command help
createCommandObsprojectHelp(__command_help__, __help_command_help__)

createCommandObsprojectHelp(__command_list__, ["obsproject list BLANK",
                                               "return all local project.",
                                               "obsproject list server_alias <server_alias> raw|[arch <arch>|maintainer|bugowner|remoteurl]",
                                               "return project on the OBS server filter with arch, maintainer, bugowner, remoteurl"])

createCommandObsprojectHelp(__command_current__, ["obsproject current BLANK",
                                                  "print the curent local project"])

createCommandObsprojectHelp(__command_dependencyrepositories__, ["obsproject dependencyrepositories {<project_alias>}",
                                                                 "print the dependency repositories of a local project "])

createCommandObsprojectHelp(__command_del__, ["obsproject delete <project_alias>",
                                              "delete a local project"])

createCommandObsprojectHelp(__command_add__, ["obsproject add <project_alias> <name_on_obs> <target> <arch> {<server_alias>}",
                                              "create a local project"])

createCommandObsprojectHelp(__command_query__, ["obsproject query [title|description|obsServer|webpage|repository|target|architecture] {project_alias <project_alias>}",
                                                "query locale project parameter",
                                                "obsproject query [title|description|target|architecture|remoteurl|maintainer|bugowner] server_alias <server_alias> obsproject <project> ",
                                                "query OBS project parameter"])

createCommandObsprojectHelp(__command_set__, ["obsproject set [title <title>] [description <description>] {project_alias <project_alias>}",
                                              "modify local project parameter"])

createCommandObsprojectHelp(__command_import__, ["obsproject import <path>",
                                                 "import a back up file"])

createCommandObsprojectHelp(__command_export__, ["obsproject export <path> {<project_alias>}}",
                                                 "export a back up file"])

#Define the obsproject parameter help
createParameterObsproject(__command_list__, [__command_help__,
                                             __parameter_server_alias__,
                                             __parameter_raw__,
                                             __parameter_arch__,
                                             __parameter_maintainer__,
                                             __parameter_bugowner__,
                                             __parameter_remoteurl__])

createParameterObsproject(__command_current__, [__command_help__])

createParameterObsproject(__command_dependencyrepositories__, [__command_help__,
                                                               __parameter_project_alias__], [__parameter_project_alias__])

createParameterObsproject(__command_del__, [__command_help__,
                                            __parameter_project_alias__], [__parameter_project_alias__])

createParameterObsproject(__command_add__, [__command_help__,
                                            __parameter_project_alias__,
                                            __parameter_name_on_obs__,
                                            __parameter_target__,
                                            __parameter_arch__,
                                            __parameter_server_alias__], [__parameter_project_alias__,
                                                                         __parameter_name_on_obs__,
                                                                         __parameter_target__,
                                                                         __parameter_arch__,
                                                                         __parameter_server_alias__])

createParameterObsproject(__command_query__, [__command_help__,
                                              __parameter_project_title__,
                                              __parameter_project_description__,
                                              __parameter_server__,
                                              __parameter_webpage__,
                                              __parameter_repository__,
                                              __parameter_target__,
                                              __parameter_arch__,
                                              __parameter_project_alias__,
                                              __parameter_remoteurl__,
                                              __parameter_maintainer__,
                                              __parameter_bugowner__,
                                              __parameter_server_alias__,
                                              __parameter_project__], [])

createParameterObsproject(__command_set__, [__command_help__,
                                            __parameter_project_title__,
                                            __parameter_project_description__,
                                            __parameter_project_alias__])

createParameterObsproject(__command_import__, [__command_help__,
                                               __parameter_path__], [__parameter_path__])

createParameterObsproject(__command_export__, [__command_help__,
                                               __parameter_path__,
                                               __parameter_project_alias__], [__parameter_path__,
                                                                              __parameter_project_alias__])

#Command package
appendCommandPackage(__command_help__)
appendCommandPackage(__command_list__)
appendCommandPackage(__command_current__)
appendCommandPackage(__command_add__)
appendCommandPackage(__command_del__)
appendCommandPackage(__command_query__)
appendCommandPackage(__command_set__)
appendCommandPackage(__command_update__)
appendCommandPackage(__command_commit__)
appendCommandPackage(__command_repair__)
appendCommandPackage(__command_addfile__)
appendCommandPackage(__command_deletefile__)
appendCommandPackage(__command_refresh__)
appendCommandPackage(__command_testConflict__)
appendCommandPackage(__command_resolveConflict__)
#Define the package command help
createCommandPackageHelp(__command_help__, __help_command_help__)
createCommandPackageHelp(__command_list__, ["package list [available] {project_alias <project_alias>}",
                                            "print the package list of the project",
                                            "if available, print the packages avaible on the OBS project server"])

createCommandPackageHelp(__command_current__, ["package current {project_alias <project_alias>}",
                                               "print the current package use on the local project"])

createCommandPackageHelp(__command_add__, ["package add {package <package>} {project_alias <project_alias>}",
                                           "add a package from the OBS project to local project"])

createCommandPackageHelp(__command_del__, ["package delete {package <package>} {project_alias <project_alias>}",
                                           "delete package from local project"])

createCommandPackageHelp(__command_query__, ["package query [title|description|url|listFile] {package <package> {server_alias <server_alias> {project <project>}}} ",
                                             "query information from OBS project",
                                             "package query [title|description|obsrev|oscrev|listfile|listFile_status|obsstatus|oscstatus|specfile|yamlfile|fspackagedirectory|oscpackagedirectory|filesystemstatus|currentPatch] {package <package> {project_alias <project_alias>} }",
                                             "query information from local project",
                                             "if no information is specify all informations are query"])

createCommandPackageHelp(__command_set__, ["package set [title <title>] [description <description>] {package <package> {project_alias <project_alias>}} ",
                                           "set information to local project"])

createCommandPackageHelp(__command_update__, ["package update {package <package> {project_alias <project_alias>}}",
                                              "update information from OBS project to local project"])

createCommandPackageHelp(__command_commit__, ["package commit <message> {package <package> {project_alias <project_alias>}}",
                                              "commit information from local project to OBS project"])

createCommandPackageHelp(__command_repair__, ["package repair {package <package> {project_alias <project_alias>}",
                                              "repair conflict betwen OBS project and local project"])

createCommandPackageHelp(__command_addfile__, ["package addfile <path> {package <package> {project_alias <project_alias>}",
                                               "add file to local package"])

createCommandPackageHelp(__command_deletefile__, ["package deletefile <file> {package <package> {project_alias <project_alias>}",
                                                  "delete file from local package"])

createCommandPackageHelp(__command_refresh__, ["package refresh [oscStatus|obsstatus] {package <package> {project_alias <project_alias>}}",
                                               "refresh osc,obs status",
                                               "if oscStatus and obsstatus ar not specify, the two status aure refresh"])

createCommandPackageHelp(__command_testConflict__, ["package testconflict {package <package>} {project_alias <project_alias>}",
                                                     "test and print the status of conflict"])

createCommandPackageHelp(__command_resolveConflict__, ["package resolveconflict {package <package>} {project_alias <project_alias>}",
                                                      "test and print the status of conflict"])
#Define the package parameter help
createParameterPackage(__command_list__, [__command_help__,
                                          __parameter_available__,
                                          __parameter_project_alias__])

createParameterPackage(__command_current__, [__command_help__,
                                             __parameter_project_alias__])

createParameterPackage(__command_add__, [__command_help__,
                                         __parameter_package__,
                                         __parameter_project_alias__])

createParameterPackage(__command_del__, [__command_help__,
                                         __parameter_package__,
                                         __parameter_project_alias__])

createParameterPackage(__command_query__, [__command_help__,
                                           __parameter_package_title__,
                                           __parameter_packge_description__,
                                           __parameter_url__,
                                           __parameter_listFile__,
                                           __parameter_listFile_status__,
                                           __parameter_package__,
                                           __parameter_server_alias__,
                                           __parameter_project__,
                                           __parameter_obsRev__,
                                           __parameter_oscRev__,
                                           __parameter_obsstatus__,
                                           __parameter_oscstatus__,
                                           __parameter_specFile__,
                                           __parameter_yamlFile__,
                                           __parameter_fsPackageDirectory__,
                                           __parameter_oscPackageDirectory__,
                                           __parameter_filesystemstatus__,
                                           __parameter_currentPatch__,
                                           __parameter_project_alias__])

createParameterPackage(__command_set__, [__command_help__,
                                         __parameter_package_title__,
                                         __parameter_packge_description__,
                                         __parameter_package__,
                                           __parameter_project_alias__])

createParameterPackage(__command_update__, [__command_help__,
                                            __parameter_package__,
                                           __parameter_project_alias__])

createParameterPackage(__command_commit__, [__command_help__,
                                            __parameter_message__,
                                            __parameter_package__,
                                           __parameter_project_alias__], [__parameter_message__])

createParameterPackage(__command_repair__, [__command_help__,
                                            __parameter_package__,
                                           __parameter_project_alias__])

createParameterPackage(__command_addfile__, [__command_help__,
                                             __parameter_path__,
                                             __parameter_package__,
                                             __parameter_project_alias__], [__parameter_path__])

createParameterPackage(__command_deletefile__, [__command_help__,
                                                __parameter_file__,
                                             __parameter_package__,
                                             __parameter_project_alias__], [__parameter_file__])

createParameterPackage(__command_refresh__, [__command_help__,
                                             __parameter_obsstatus__,
                                             __parameter_oscstatus__,
                                             __parameter_package__,
                                             __parameter_project_alias__])

createParameterPackage(__command_testConflict__, [__command_help__,
                                                   __parameter_package__,
                                                   __parameter_project_alias__])

createParameterPackage(__command_resolveConflict__, [__command_help__,
                                                     __parameter_package__,
                                                     __parameter_project_alias__])

#Command filesystem
appendCommandFilesystem(__command_help__)
appendCommandFilesystem(__command_create__)
appendCommandFilesystem(__command_del__)
appendCommandFilesystem(__command_query__)
appendCommandFilesystem(__command_enter__)
appendCommandFilesystem(__command_executescript__)
appendCommandFilesystem(__command_repositories__)

#Define the filesystem command help
createCommandFilesystemHelp(__command_help__, __help_command_help__)

createCommandFilesystemHelp(__command_create__, ["projectfilesystem create {<project_alias>}",
                                                 "Create a new project filesystem"])

createCommandFilesystemHelp(__command_del__, ["projectfilesystem delete <project_alias>",
                                              "Remove the project filesystem"])

createCommandFilesystemHelp(__command_query__, ["projectfilesystem query [path|status] {project_alias <project_alias>}",
                                                "print the path and the status of a filesystem"])

createCommandFilesystemHelp(__command_enter__, ["projectfilesystem enter [package <package>] {project_alias <project_alias>}",
                                                "chroot into the filesystem"])

createCommandFilesystemHelp(__command_executescript__, ["projectfilesystem executescript <path> {project_alias <project_alias>}",
                                                        ""])

createCommandFilesystemHelp(__command_repositories__, ["the command for file system repositorie"])

#Define the filesystem parameter help
createParameterFilesystem(__command_create__, [__command_help__,
                                               __parameter_project_alias__], [__parameter_project_alias__])

createParameterFilesystem(__command_del__, [__command_help__,
                                            __parameter_project_alias__], [__parameter_project_alias__])

createParameterFilesystem(__command_query__, [__command_help__,
                                              __parameter_path__,
                                              __parameter_filesystemstatus__,
                                              __parameter_project_alias__])

createParameterFilesystem(__command_enter__, [__command_help__,
                                              __parameter_package__,
                                              __parameter_project_alias__])

createParameterFilesystem(__command_executescript__, [__command_help__,
                                                      __parameter_path__,
                                                      __parameter_project_alias__], [__parameter_path__])

createParameterFilesystem(__command_repositories__, [__command_help__])

#Command Repositories
appendCommandRepositories(__command_help__)
appendCommandRepositories(__command_add__)
appendCommandRepositories(__command_del__)
appendCommandRepositories(__command_query__)
appendCommandRepositories(__command_modify__)

#Define the Repositories command help
createCommandRepositoryHelp(__command_help__, __help_command_help__)

createCommandRepositoryHelp(__command_add__, ["projectfilesystem repositories add <repository_url> <repository_alias> {<project_alias>}",
                                             "add a repository by url/alias to the project filesystem",
                                             "projectfilesystem repositories add from <project_alias> ",
                                             "add a repository of a local project to the project filesystem"])

createCommandRepositoryHelp(__command_del__, ["projectfilesystem repositories delete <repository_alias> {<project_alias>} ",
                                             "remove a repository from a project file system"])

createCommandRepositoryHelp(__command_query__, ["projectfilesystem repositories query project_alias <project_alias>",
                                               "print the url/alias of the repositories of the project filesystem"])

createCommandRepositoryHelp(__command_modify__, ["projectfilesystem repositories modify [newUrl <repository_url>] [newAlias <repository_alias>] repository_alias <repository_alias> {project_alias <project_alias>}",
                                                "modify the url/alias of a repository"])

#Define the Repositories parameter help
createParameterRepositories(__command_add__, [__command_help__,
                                              __parameter_repo_url__,
                                              __parameter_repo_alias__,
                                              __parameter_project_alias__,
                                              __parameter_From__], [__parameter_repo_url__,
                                                                    __parameter_repo_alias__,
                                                                    __parameter_project_alias__])

createParameterRepositories(__command_del__, [__command_help__,
                                              __parameter_repo_alias__,
                                              __parameter_project_alias__])

createParameterRepositories(__command_query__, [__command_help__,
                                                __parameter_project_alias__])

createParameterRepositories(__command_modify__, [__command_help__,
                                                 __parameter_newUrl__,
                                                 __parameter_newAlias__,
                                                 __parameter_repo_alias__,
                                                 __parameter_project_alias__])

#Command rpmbuild
appendCommandRpmbuild(__command_help__)
appendCommandRpmbuild(__command_prepare__)
appendCommandRpmbuild(__command_build__)
appendCommandRpmbuild(__command_install__)
appendCommandRpmbuild(__command_buildpackage__)
appendCommandRpmbuild(__command_isInit__)
appendCommandRpmbuild(__command_createPatch__)
appendCommandRpmbuild(__command_updatepatch__)


#Define the rpmbuild command help
createCommandRpmbuildHelp(__command_help__, __help_command_help__)
createCommandRpmbuildHelp(__command_prepare__, ["rpmbuild prepare {package <package>} {project_alias <project_alias>}",
                                                "create the the rpmbuild directorie, build one time the package and initialise git "])

createCommandRpmbuildHelp(__command_build__, ["rpmbuild build {package <package>} {project_alias <project_alias>}",
                                              "build the package"])

createCommandRpmbuildHelp(__command_install__, ["rpmbuild install {package <package>} {project_alias <project_alias>}",
                                                "build and install the package"])

createCommandRpmbuildHelp(__command_buildpackage__, ["rpmbuild buildpackage {package <package>} {project_alias <project_alias>}",
                                                     "build,install and create the rpm package"])

createCommandRpmbuildHelp(__command_isInit__, ["rpmbuild isinit {package <package>} {project_alias <project_alias>}",
                                               "print if package prepare was doing"])

createCommandRpmbuildHelp(__command_createPatch__, ["rpmbuild createpatch <patch> {package <package>} {project_alias <project_alias>}",
                                                    "create a current patch and add patch file into osc local package, and into yaml/specfile"])

createCommandRpmbuildHelp(__command_updatepatch__, ["rpmbuild updatepatch {package <package> {project_alias <project_alias>}",
                                                    "update the current patch"])



#Define the rpmbuild parameter help
createParameterRpmbuild(__command_prepare__, [__command_help__,
                                              __parameter_package__,
                                              __parameter_project_alias__])

createParameterRpmbuild(__command_build__, [__command_help__,
                                            __parameter_package__,
                                              __parameter_project_alias__])

createParameterRpmbuild(__command_install__, [__command_help__,
                                              __parameter_package__,
                                              __parameter_project_alias__])

createParameterRpmbuild(__command_buildpackage__, [__command_help__,
                                                   __parameter_package__,
                                              __parameter_project_alias__])

createParameterRpmbuild(__command_isInit__, [__command_help__,
                                             __parameter_package__,
                                             __parameter_project_alias__])

createParameterRpmbuild(__command_createPatch__, [__command_help__,
                                                  __parameter_path__,
                                                  __parameter_package__,
                                                  __parameter_project_alias__], [__parameter_path__])

createParameterRpmbuild(__command_updatepatch__, [__command_help__,
                                                  __parameter_package__,
                                                  __parameter_project_alias__])

createParameterRpmbuild(__command_testConflict__, [__command_help__,
                                                   __parameter_package__,
                                                   __parameter_project_alias__])

##Command micproject
#appendCommandMicproject
##Define the micproject command help
#createCommandMicprojectHelp
##Define the micproject parameter help
#createParameterMicproject

class ObsLightBase():
    '''
    only management doc print and obslight core.
    '''
    noaction = False
    manTag = False

    def __init__(self):
        '''
        init ObsLightBase parameter
        '''
        sys.stderr = safewriter.SafeWriter(sys.stderr)
        sys.stdout = safewriter.SafeWriter(sys.stdout)

        self.__listArgv = sys.argv[1:]

        self.listCommand = None
        self.dicoParameterCompletion = None
        self.dicoCommandHelp = None
        self.dicoParameter = None

        self.currentCommand = None

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

    def printCompletionListAlias(self):
        m = ObsLightManager.getCommandLineManager()
        res = m.getObsServerList(reachable=False)
        if res != None:
            print " ".join(res)
        return 0

    def printCompletionListProject(self):
        m = ObsLightManager.getCommandLineManager()
        res = m.getLocalProjectList()
        if res != None:
            print " ".join(res)
        return 0

    def printCompletionListPackage(self, project_alias, local=1):
        m = ObsLightManager.getCommandLineManager()
        if m.isALocalProject(project_alias):
            res = m.getLocalProjectPackageList(projectLocalName=project_alias, local=local)
            if res != None:
                print " ".join(res)
            return 0
        else:
            return -1

    def printCompletionListObsProject(self, server_alias):
        m = ObsLightManager.getCommandLineManager()
        res = m.getObsServerProjectList(serverApi=server_alias)
        if res != None:
            print " ".join(res)
        return 0

    def execute(self, listArgv):
        '''
        Execute a list of arguments.
        '''
        pass

    def print_Help(self, cmd=None):
        '''
        print help.
        '''
        if isinstance(cmd, (list, tuple)):
            cmd = cmd[0]

        if ObsLightBase.noaction:
            if cmd == None:
                if self.listCommand != None:
                    print " ".join(self.listCommand)
            else:
                if self.dicoParameterCompletion != None:
                    if cmd in self.dicoParameterCompletion.keys():
                        print " ".join(self.dicoParameterCompletion[cmd])
                    else:
                        print "ERROR '" + cmd + "' is not in self.dicoParameterCompletion.keys() : " + ",".join(self.dicoParameterCompletion.keys())
                        return 1
            return 0
        else:
            if cmd == None:
                print "Command: " + self.currentCommand
                if self.currentCommand in __DICO_command_help__.keys():
                    print __DICO_command_help__[self.currentCommand]
                    print
                else:
                    print "ERROR '" + self.currentCommand + "' is not in __DICO_command_help__.keys() : " + ",".join(__DICO_command_help__.keys())
                    return 1

                print "Sub command:"
                if self.listCommand != None:
                    for cmd in self.listCommand:
                        if cmd in self.dicoCommandHelp.keys():
                            print self.dicoCommandHelp[cmd]
                        else:
                            print "ERROR '" + cmd + "' is not in self.dicoCommandHelp.keys() : " + ",".join(self.dicoCommandHelp.keys())
                            return 1
            else:
                if self.dicoCommandHelp != None:
                    if cmd in __command_help__:
                        return 0
                    if cmd in self.dicoCommandHelp.keys():
                        print "Sub command : " + self.currentCommand + " " + cmd
                        print self.dicoCommandHelp[cmd]

                        print "Parameter:"
                        if self.dicoParameter != None:
                            if cmd in self.dicoParameter.keys():
                                for para in self.dicoParameter[cmd]:
                                    if self.dicoParameterHelp != None:
                                        if para in self.dicoParameterHelp.keys():
                                            print self.dicoParameterHelp[para]
                                        else:
                                            print "ERROR '" + para + "' is not in self.dicoParameterHelp.keys() : " + ",".join(self.dicoParameterHelp.keys())
                                            return 1
                                print
                            else:
                                print "ERROR '" + cmd + "' is not in self.dicoParameter.keys() : " + ",".join(self.dicoParameter.keys())
                                return 1
                    else:
                        print "ERROR '" + cmd + "' is not in self.dicoCommandHelp.keys() : " + ",".join(self.dicoCommandHelp.keys())
                        return 1
            if not ObsLightBase.manTag:
                self.printSyntaxHelp()
        return 0

    def printSyntaxHelp(self):
        '''
        print the syntax help
        '''
        print __SYNTAX_HELP__

    def man(self):
        '''
        print the pseudo-man doc of the command
        '''
        self.print_Help()

        for command in self.listCommand:
            self.print_Help(command)

    def networkRequest(self):
        '''
        
        '''
        if ObsLightPrintManager.QUIET == 0:
            sys.stdout.write("Network Request ...")
            sys.stdout.flush()

    def printListResult(self, result, comment=None, row=True):
        '''
        
        '''
        if ObsLightPrintManager.QUIET == 0:
            sys.stdout.write("\r" + " "*20 + "\r")
            if comment != None:
                sys.stdout.write(comment + "\n")
            if row :
                for res in result:
                    if comment != None:
                        sys.stdout.write(" "*len(comment))
                    sys.stdout.write(res + "\n")
            else:
                sys.stdout.write(", ".join(result) + "\n")

            sys.stdout.flush()
        else:
            sys.stdout.write(" ".join(result) + "\n")
            sys.stdout.flush()

    def printMessageError(self, message):
        '''
        
        '''
        if ObsLightBase.noaction:
            print ""
        else:
            if ObsLightPrintManager.QUIET == 0:
                print message
            else:
                print message

    def printError(self, message, command):
        '''
        
        '''
        if ObsLightBase.noaction:
            self.print_Help(command)
        else:
            if ObsLightPrintManager.QUIET == 0:
                print message

    def printSimpleResult(self, verboseResult, result):
        '''
        
        '''
        if ObsLightPrintManager.QUIET == 0:
            sys.stdout.write("\r" + " "*20 + "\r")
            sys.stdout.write(verboseResult + "\n")
            sys.stdout.flush()
        else:
            sys.stdout.write(result + "\n")
            sys.stdout.flush()

    def printBoolResult(self, printableResult, boolResult):
        '''
        
        '''
        if ObsLightPrintManager.QUIET == 0:
            sys.stdout.write("\r" + " "*20 + "\r")
            sys.stdout.write("\r")
            sys.stdout.write(printableResult + "\n")
            sys.stdout.flush()
        else:
            print str(boolResult)

    def globalDescription(self):
        '''
        Print the global description
        '''
        if not ObsLightBase.noaction:
            print __DESCRIPTION__
            for h in __LIST_command__:
                print __DICO_command_help__[h]
            print
            print "global Options:\n"
            for h in __LIST_command_global__:
                print __DICO_command_help__[h]
            print
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
            if listCommand == None:
                avalableCommand = self.listCommand
            else:
                avalableCommand = self.dicoParameter[listCommand[0]]
            if (avalableCommand != None) and (len(avalableCommand) > 0):
                print "Available argument are :" + ",".join(avalableCommand)
        else:
            self.print_Help(listCommand)
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

        self.currentCommand = __server__[0]

        self.listCommand = __LIST_command_server__
        self.dicoParameterCompletion = __DICO_parameter_server_completion__
        self.dicoCommandHelp = __DICO_command_server_help__
        self.dicoParameter = __DICO_parameter_server__

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
                return self.printUnknownCommand(currentCommand)
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
            elif currentCommand in __parameter_server_alias__:
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
                return self.printUnknownCommand(currentCommand, __command_test__)

        if Help == True:
            return self.print_Help(__command_test__)
        if not ObsLightBase.noaction:
            if server_alias != None:
                m = ObsLightManager.getCommandLineManager()
                self.networkRequest()
                res = m.testServer(obsServer=server_alias)
                if self.testResult(res, getLineno()) == 0 :
                    if res == True:
                        self.printBoolResult("'" + server_alias + "' is reachable", 1)
                    else:
                        self.printBoolResult("'" + server_alias + "' is not reachable", 0)
                    return 0
                else:
                    return -1
            elif (login != None) and (password != None) and (api_url != None):
                m = ObsLightManager.getCommandLineManager()
                self.networkRequest()
                res = m.testApi(api=api_url, user=login, passwd=password)
                if self.testResult(res, getLineno()) == 0 :
                    if res == 0:
                        self.printBoolResult("'" + api_url + "' is reachable", 1)
                    elif res == 1:
                        self.printBoolResult("'" + api_url + "' is not reachable, user and passwd  are wrong.", 0)
                    elif res == 2:
                        self.printBoolResult("'" + api_url + "' is not reachable, api is wrong..", 0)
                    else:
                        self.printBoolResult("'" + api_url + "' is not reachable", 0)
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
                return self.printUnknownCommand(currentCommand, __command_list__)

        if Help == True:
            return self.print_Help(__command_list__)
        if not ObsLightBase.noaction:
            m = ObsLightManager.getCommandLineManager()
            if reachable:self.networkRequest()
            res = m.getObsServerList(reachable=reachable)
            if self.testResult(res, getLineno()) == -1 :return - 1
            self.printListResult(res)
            return 0
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
            elif currentCommand in __parameter_server_alias__:
                server_alias, listArgv = self.getParameter(listArgv)
                if (server_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListAlias()
            else:
                return self.printUnknownCommand(currentCommand, __command_query__)

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
                    self.printSimpleResult("alias '" + server_alias + "' user:\t\t" + str(res), str(res))
                if api_url :
                    res = m.getObsServerParameter(obsServerAlias=server_alias, parameter="serverAPI")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("alias '" + server_alias + "' serverAPI:\t" + str(res), str(res))
                if repository_url :
                    res = m.getObsServerParameter(obsServerAlias=server_alias, parameter="serverRepo")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("alias '" + server_alias + "' serverRepo:\t" + str(res), str(res))
                if weburl :
                    res = m.getObsServerParameter(obsServerAlias=server_alias, parameter="serverWeb")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("alias '" + server_alias + "' serverWeb:\t" + str(res), str(res))
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
            elif currentCommand in __parameter_server_alias__:
                server_alias, listArgv = self.getParameter(listArgv)
                if (server_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListAlias()
            else:
                return self.printUnknownCommand(currentCommand, __command_set__)

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
            elif currentCommand in __parameter_server_alias__:
                server_alias, listArgv = self.getParameter(listArgv)
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
                return self.printUnknownCommand(currentCommand, __command_add__)

        if  Help :
            return self.print_Help(__command_add__)
        elif (password == None):
            return self.printError("Missing password", __command_add__)
        elif (weburl == None):
            return self.printError("Missing weburl", __command_add__)
        elif (repository_url == None):
            return self.printError("Missing repository_url", __command_add__)
        elif (api_url == None):
            return self.printError("Missing repository_url", __command_add__)
        elif (api_url == None) :
            return self.printError("Missing api_url", __command_add__)
        elif (login == None) :
            return self.printError("Missing login", __command_add__)
        elif (server_alias == None)  :
            return self.printError("Missing server_alias", __command_add__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                return m.addObsServer(serverApi=api_url,
                                      user=login,
                                      password=password,
                                      alias=server_alias,
                                      serverRepo=repository_url,
                                      serverWeb=weburl)
            else:
                return self.print_Help(__command_add__)

    def server_del(self, listArgv):
        '''
        
        '''
        Help = False
        server_alias = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)

            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                server_alias = currentCommand
                break

        if  Help or (server_alias == None):
            return self.print_Help(__command_del__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                return m.delObsServer(obsServer=server_alias)
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
                return self.printUnknownCommand(currentCommand, __command_current__)

        if  Help :
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

        self.currentCommand = __obsproject__[0]

        self.listCommand = __LIST_command_obsproject__
        self.dicoParameterCompletion = __DICO_parameter_obsproject_completion__
        self.dicoCommandHelp = __DICO_command_obsproject_help__
        self.dicoParameter = __DICO_parameter_obsproject__

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

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)

            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_raw__:
                raw = True
            elif currentCommand in __parameter_server_alias__:
                server_alias , listArgv = self.getParameter(listArgv)
                if (server_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListAlias()
            elif  currentCommand in __parameter_arch__ :
                arch , listArgv = self.getParameter(listArgv)
            elif  currentCommand in __parameter_maintainer__ :
                maintainer = True
            elif  currentCommand in __parameter_bugowner__ :
                bugowner = True
            elif  currentCommand in __parameter_remoteurl__ :
                remoteurl = True
            else:
                return self.printUnknownCommand(currentCommand, __command_list__)

        if Help == True:
            return self.print_Help(__command_list__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                res = []
                if server_alias == None:
                    res = m.getLocalProjectList()
                    if self.testResult(res, getLineno()) == -1:return - 1
                elif server_alias != None:
                    self.networkRequest()
                    res = m.getObsServerProjectList(serverApi=server_alias,
                                                    maintainer=maintainer,
                                                    bugowner=bugowner,
                                                    remoteurl=remoteurl,
                                                    arch=arch,
                                                    raw=raw)
                    if self.testResult(res, getLineno()) == -1:return - 1
                else:
                    return self.print_Help()
                self.printListResult(res)
                return 0
            else:
                return self.print_Help(__command_list__)

    def obsproject_current(self, listArgv):
        '''
        
        '''
        Help = False

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                return self.printUnknownCommand(currentCommand, __command_current__)

        if  Help :
            return self.print_Help(__command_current__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                res = m.getCurrentObsProject()
                print res
                return 0
            else:
                return self.print_Help(__command_current__)

    def obsproject_add(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None
        name_on_obs = None
        target = None
        arch = None
        server_alias = None

        while self.testListArgv(listArgv):
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

        if  Help == True:
            return self.print_Help(__command_add__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if server_alias == None:
                    server_alias = m.getCurrentObsServer()
                    if server_alias == None:
                        return self.print_Help(__command_add__)

                if (name_on_obs == None):
                    return self.printError("Missing projectObsName", __command_add__)
                elif (target == None):
                    return self.printError("Missing target", __command_add__)
                elif (target == None):
                    return self.printError("Missing target", __command_add__)
                elif (arch == None):
                    return self.printError("Missing arch", __command_add__)
                elif (project_alias == None):
                    return self.printError("Missing project_alias", __command_add__)

                res = m.addProject(serverApi=server_alias,
                                    projectObsName=name_on_obs,
                                    projectTarget=target,
                                    projectArchitecture=arch,
                                    projectLocalName=project_alias)

                if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.print_Help(__command_add__)

    def obsproject_del(self, listArgv):
        '''
        
        '''
        Help = False
        project = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)

            if (currentCommand in __command_help__):
                Help = True
                break
            else:
                project = currentCommand
                break

        if  Help :
            return self.print_Help(__command_del__)
        else:
            if not ObsLightBase.noaction:
                if project == None:
                    return self.printError("Missing project", __command_del__)
                m = ObsLightManager.getCommandLineManager()
                res = m.removeProject(projectLocalName=project)
                if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.print_Help(__command_del__)

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

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__):
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
            elif currentCommand in __parameter_project_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            elif currentCommand in __parameter_server_alias__:
                server_alias , listArgv = self.getParameter(listArgv)
                if (server_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListAlias()
            elif currentCommand in __parameter_project__:
                obsproject , listArgv = self.getParameter(listArgv)
                if (server_alias != None) and (obsproject == None) and ObsLightBase.noaction:
                    return self.printCompletionListObsProject(server_alias)
            else:
                return self.printUnknownCommand(currentCommand, __command_query__)

        if  Help :
            return self.print_Help(__command_query__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) and ((server_alias == None) or (obsproject == None)):
                    if project_alias == None:
                        project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_query__)

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
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("title: " + res, str(res))

                if description :
                    if (server_alias == None) and (obsproject == None):
                        res = m.getProjectParameter(projectLocalName=project_alias,
                                                    parameter="description")
                    else:
                        res = m.getObsProjectParameter(serverApi=server_alias,
                                                       obsproject=obsproject,
                                                       parameter="title")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("description: " + res, str(res))

                if server and (server_alias == None) and (obsproject == None):
                    res = m.getProjectParameter(projectLocalName=project_alias,
                                                parameter="obsServer")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("server: " + res, str(res))

                if webpage and (server_alias == None) and (obsproject == None) :
                    res = m.getProjectWebPage(projectLocalName=project_alias)
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("webpage: " + res, str(res))

                if repository and (server_alias == None) and (obsproject == None):
                    res = m.getProjectRepository(projectLocalName=project_alias)
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("repository: " + res, str(res))

                if target :
                    if (server_alias == None) and (obsproject == None):
                        res = m.getProjectParameter(projectLocalName=project_alias,
                                                    parameter="projectTarget")
                    else:
                        res = m.getObsProjectParameter(serverApi=server_alias,
                                                       obsproject=obsproject,
                                                       parameter="repository")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    elif isinstance(res, (basestring)):
                        self.printSimpleResult("target: " + res, str(res))
                    elif isinstance(res, (list, tuple)):
                        self.printListResult(res, comment="target: ")
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
                    if self.testResult(res, getLineno()) == -1:return - 1
                    elif isinstance(res, (basestring)):
                        self.printSimpleResult("architecture: " + res, str(res))
                    elif isinstance(res, (list, tuple)):
                        self.printListResult(res, comment="architecture: ")
                    else:
                        print "ERROR NO RESULT " + __file__ + " " + str(getLineno())
                        return -1

                if remoteurl and (server_alias != None) and (obsproject != None):
                    res = m.getObsProjectParameter(serverApi=server_alias,
                                                   obsproject=obsproject,
                                                   parameter="remoteurl")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("remoteurl: " + str(res), str(res))

                if maintainer  and (server_alias != None) and (obsproject != None) :
                    res = m.getObsProjectParameter(serverApi=server_alias,
                                                obsproject=obsproject,
                                                parameter="maintainer")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printListResult(res, comment="maintainer: ")
                if bugowner  and (server_alias != None) and (obsproject != None) :
                    res = m.getObsProjectParameter(serverApi=server_alias,
                                                obsproject=obsproject,
                                                parameter="bugowner")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printListResult(res, comment="bugowner: ")
                return 0
            else:
                return self.print_Help(__command_query__)

    def obsproject_set(self, listArgv):
        '''
        
        '''
        Help = False
        title = None
        description = None
        project_alias = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_project_title__:
                title , listArgv = self.getParameter(listArgv)
                if (title == None) and not ObsLightBase.noaction:
                    return self.printError("Missing  title", __command_add__)
            elif currentCommand in __parameter_project_description__:
                description , listArgv = self.getParameter(listArgv)
                if (description == None) and not ObsLightBase.noaction:
                    return self.printError("Missing  description", __command_add__)
            elif currentCommand in __parameter_project_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            else:
                return self.printUnknownCommand(currentCommand, __command_set__)

        if  Help :
            return self.print_Help(__command_set__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_set__)

                if (title == None) and (description == None):
                    return self.printError("Missing title/description", __command_add__)

                if title != None:
                    res = m.setProjectParameter(projectLocalName=project_alias,
                                                parameter="title",
                                                value=title)
                    if self.testResult(res, getLineno()) == -1:return - 1

                if description != None:
                    res = m.setProjectParameter(projectLocalName=project_alias,
                                                parameter="description",
                                                value=description)
                    if self.testResult(res, getLineno()) == -1:return - 1

                return 0
            else:
                return self.print_Help(__command_set__)

    def obsproject_import(self, listArgv):
        '''
        
        '''
        Help = False
        path = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                path = currentCommand
                break

        if  Help :
            return self.print_Help(__command_import__)
        else:
            if not ObsLightBase.noaction:
                if (path == None):
                    return self.printError("Missing  path", __command_import__)
                m = ObsLightManager.getCommandLineManager()

                res = m.importProject(path)

                if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.print_Help(__command_import__)


    def obsproject_export(self, listArgv):
        '''
        
        '''
        Help = False
        path = None
        project_alias = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                path = currentCommand
                project_alias, listArgv = self.getParameter(listArgv)
                break

        if  Help:
            return self.print_Help(__command_export__)
        else:
            if not ObsLightBase.noaction:
                if (path == None):
                    return self.printError("Missing  path", __command_export__)

                m = ObsLightManager.getCommandLineManager()

                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help()

                res = m.exportProject(project_alias, path)

                if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.print_Help(__command_export__)

    def obsproject_dependencyrepositories(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                project_alias = currentCommand
                break

        if  Help:
            return self.print_Help(__command_dependencyrepositories__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help()

                res = m.getDependencyRepositories(project_alias)

                if self.testResult(res, getLineno()) == -1:return - 1
                for repo in res.keys():
                    self.printSimpleResult("Repository Alias: " + str(repo) + " Url: " + res[repo], str(repo) + " , " + res[repo])
                return 0
            else:
                return self.print_Help(__command_dependencyrepositories__)

    def execute(self, listArgv):
        '''
        Execute a list of arguments.
        '''
        if len(listArgv) == 0:
            self.print_Help()
            return 0
        else:
            currentCommand, listArgv = self.getParameter(listArgv)

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

        self.currentCommand = __Package__[0]

        self.listCommand = __LIST_package__
        self.dicoParameterCompletion = __DICO_parameter_package_completion__
        self.dicoCommandHelp = __DICO_command_package_help__
        self.dicoParameter = __DICO_parameter_package__

    def package_add(self, listArgv):
        '''
        
        '''
        Help = False
        package = None
        project_alias = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printCompletionListPackage(project_alias, local=0)
            else:
                self.printUnknownCommand(currentCommand, __command_add__)

        if  Help  :
            return self.print_Help(__command_add__)
        else:
            if not ObsLightBase.noaction:
                if (package == None):
                    return self.printError("Missing  package", __command_add__)

                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help()

                return m.addPackage(projectLocalName=project_alias,
                                    package=package)
            else:
                return self.print_Help(__command_add__)

    def package_delete(self, listArgv):
        '''
        
        '''
        Help = False
        package = None
        project_alias = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) :
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printCompletionListPackage(project_alias)
            else:
                self.printUnknownCommand(currentCommand, __command_del__)

        if  Help or (package == None) :
            return self.print_Help(__command_del__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_del__)

                return m.removePackage(projectLocalName=project_alias,
                                       package=package)
            else:
                return self.print_Help(__command_del__)



    def package_list(self, listArgv):
        '''
        
        '''
        Help = False
        available = False
        project_alias = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_available__:
                available = True
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            else:
                return self.printUnknownCommand(currentCommand, __command_list__)

        if  Help :
            return self.print_Help(__command_list__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_list__)

                if available:
                    res = m.getLocalProjectPackageList(projectLocalName=project_alias, local=0)
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printListResult(res)
                else:
                    res = m.getLocalProjectPackageList(projectLocalName=project_alias, local=1)
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printListResult(res)
            else:
                return self.print_Help(__command_list__)
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
        listFile_status = False
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

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__):
                Help = True
                break
            elif currentCommand in __parameter_project_title__:
                title = True
            elif currentCommand in __parameter_project_description__:
                description = True
            elif currentCommand in __parameter_revision__:
                revision = True
            elif currentCommand in __parameter_obsRev__ :
                obsRev = True
            elif currentCommand in __parameter_oscRev__ :
                oscRev = True
            elif currentCommand in __parameter_listFile__:
                listFile = True
            elif currentCommand in __parameter_listFile_status__:
                listFile_status = True
            elif currentCommand in __parameter_obsstatus__:
                obsStatus = True
            elif currentCommand in __parameter_oscstatus__:
                oscStatus = True
            elif currentCommand in __parameter_specFile__:
                specFile = True
            elif currentCommand in __parameter_yamlFile__:
                yamlFile = True
            elif currentCommand in __parameter_fsPackageDirectory__ :
                fsPackageDirectory = True
            elif currentCommand in __parameter_oscPackageDirectory__ :
                oscPackageDirectory = True
            elif currentCommand in __parameter_filesystemstatus__:
                chRootStatus = True
            elif currentCommand in __parameter_currentPatch__:
                currentPatch = True
            elif currentCommand in __parameter_url__:
                url = True
            elif currentCommand in __parameter_project_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            elif currentCommand in __parameter_server_alias__:
                server_alias , listArgv = self.getParameter(listArgv)
                if (server_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListAlias()
            elif currentCommand in __parameter_project__:
                obsproject , listArgv = self.getParameter(listArgv)
                if (server_alias != None) and (obsproject == None) and ObsLightBase.noaction:
                    return self.printCompletionListObsProject(server_alias)
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printCompletionListPackage(project_alias)
            else:
                return self.printUnknownCommand(currentCommand, __command_query__)

        if  Help :
            return self.print_Help(__command_query__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if (package == None) and (project_alias != None):
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.print_Help(__command_query__)

                if (project_alias == None) and ((server_alias == None) or (obsproject == None)):
                    return self.print_Help(__command_query__)

                if (not title) and \
                   (not description) and \
                   (not revision)and \
                   (not url)and \
                   (not obsRev)and \
                   (not oscRev)and \
                   (not listFile)and \
                   (not listFile_status)and \
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
                    listFile_status = True
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
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("title: " + res, str(res))

                if description :
                    if (server_alias == None) and (obsproject == None):
                        res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="description")
                    else:
                        res = m.getObsPackageParameter(serverApi=server_alias,
                                                       obsproject=obsproject,
                                                       package=package,
                                                       parameter="description")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("description: " + res, str(res))

                if url and ((server_alias != None) and (obsproject != None)):
                    res = m.getObsPackageParameter(serverApi=server_alias,
                                                       obsproject=obsproject,
                                                       package=package,
                                                       parameter="url")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("url: " + res, str(res))

                if obsRev and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="obsRev")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("obsRev: " + res, str(res))

                if oscRev and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="oscRev")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("oscRev: " + res, str(res))

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

                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printListResult(res, comment="listFile: ", row=True)

                if listFile_status and (project_alias != None):
                    if (project_alias != None):
                        res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="listFile")
                        print "project_alias", project_alias
                        print "package", package

                        res2 = []
                        for aFile in res:
                            status = m.getPackageFileInfo(projectLocalName=project_alias,
                                                        package=package,
                                                        fileName=aFile)
                            fileResult = aFile + " " + status['Status']
                            res2.append(fileResult)

                        if self.testResult(res, getLineno()) == -1:return - 1
                        self.printListResult(res2, comment="listFile status: ", row=True)

                if obsStatus and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="obsStatus")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("obsStatus: " + res, str(res))

                if oscStatus and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="oscStatus")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("oscStatus: " + res, str(res))

                if specFile and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="specFile")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("specFile: " + res, str(res))

                if yamlFile and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="yamlFile")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("yamlFile: " + res, str(res))

                if fsPackageDirectory and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="fsPackageDirectory")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("fsPackageDirectory: " + res, str(res))

                if oscPackageDirectory and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="oscPackageDirectory")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("oscPackageDirectory: " + res, str(res))

                if chRootStatus and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="chRootStatus")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("chRootStatus: " + res, str(res))

                if currentPatch and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="currentPatch")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("currentPatch: " + res, str(res))
            else:
                return self.print_Help(__command_query__)

    def package_set(self, listArgv):
        '''
        
        '''
        Help = False

        title = None
        description = None

        project_alias = None
        package = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_project_title__:
                title , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_project_description__:
                description , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_project_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printCompletionListPackage(project_alias)
            else:
                return self.printUnknownCommand(currentCommand, __command_set__)

        if  Help :
            return self.print_Help(__command_set__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_set__)

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.print_Help(__command_set__)

                if title != None :
                    res = m.setPackageParameter(projectLocalName=project_alias,
                                                  package=package,
                                                  parameter="title",
                                                  value=title)
                    if self.testResult(res, getLineno()) == -1:return - 1

                if description != None :
                    res = m.setPackageParameter(projectLocalName=project_alias,
                                                  package=package,
                                                  parameter="description",
                                                  value=description)
                    if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.print_Help(__command_set__)

    def package_update(self, listArgv):
        '''
        
        '''
        Help = False

        project_alias = None
        package = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printCompletionListPackage(project_alias)
            else:
                return self.printUnknownCommand(currentCommand, __command_update__)

        if  Help :
            return self.print_Help(__command_update__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_update__)

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.print_Help(__command_update__)

                res = m.updatePackage(projectLocalName=project_alias,
                                     package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.print_Help(__command_update__)

    def package_commit(self, listArgv):
        '''
        
        '''
        Help = False

        project_alias = None
        package = None
        message = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__):
                Help = True
                break
            else:
                message = currentCommand
                while self.testListArgv(listArgv):
                    currentCommand, listArgv = self.getParameter(listArgv)
                    if currentCommand in __parameter_project_alias__:
                        project_alias , listArgv = self.getParameter(listArgv)
                        if (project_alias == None) and ObsLightBase.noaction:
                            return self.printCompletionListProject()
                    elif currentCommand in __parameter_package__:
                        package, listArgv = self.getParameter(listArgv)
                        if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                            return self.printCompletionListPackage(project_alias)
                    else:
                        return self.printUnknownCommand(currentCommand, __command_commit__)
                break

        if  Help :
            return self.print_Help(__command_commit__)
        else:
            if not ObsLightBase.noaction:
                if message == None :
                    return self.printError("Missing  message", __command_commit__)

                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_commit__)

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.print_Help(__command_commit__)

                res = m.updatePackage(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                res = m.testConflict(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                if res : return self.printMessageError("Can't commit, package '" + package + "' is on conflict.")

                res = m.addAndCommitChanges(project_alias,
                                            package,
                                            message)
                if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.print_Help(__command_commit__)

    def package_repair(self, listArgv):
        '''
        
        '''
        Help = False

        project_alias = None
        package = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printCompletionListPackage(project_alias)
            else:
                return self.printUnknownCommand(currentCommand, __command_repair__)

        if  Help :
            return self.print_Help(__command_repair__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_repair__)

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.print_Help(__command_repair__)

                res = m.repairOscPackageDirectory(projectLocalName=project_alias,
                                                  package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.print_Help(__command_repair__)

    def package_current(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            else:
                return self.printUnknownCommand(currentCommand, __command_current__)

        if  Help :
            return self.print_Help(__command_current__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_current__)

                return m.getCurrentPackage(projectLocalName=project_alias)
            else:
                return self.print_Help(__command_current__)

    def package_addfile(self, listArgv):
        '''
        
        '''
        Help = False
        path = None
        project_alias = None
        package = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                path = currentCommand
                while(len(listArgv) > 0):
                    currentCommand, listArgv = self.getParameter(listArgv)
                    if currentCommand in __parameter_project_alias__:
                        project_alias , listArgv = self.getParameter(listArgv)
                        if (project_alias == None) and ObsLightBase.noaction:
                            return self.printCompletionListProject()
                    elif currentCommand in __parameter_package__:
                        package, listArgv = self.getParameter(listArgv)
                        if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                            return self.printCompletionListPackage(project_alias)
                    else:
                        return self.printUnknownCommand(currentCommand, __command_addfile__)
                break

        if  Help :
            return self.print_Help(__command_addfile__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_addfile__)

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.print_Help(__command_addfile__)

                return m.addFileToPackage(project_alias, package, path)
            else:
                return self.print_Help(__command_addfile__)

    def package_deletefile(self, listArgv):
        '''
        
        '''
        Help = False
        name = None
        project_alias = None
        package = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                name = currentCommand
                while(len(listArgv) > 0):
                    currentCommand, listArgv = self.getParameter(listArgv)
                    if currentCommand in __parameter_project_alias__:
                        project_alias , listArgv = self.getParameter(listArgv)
                        if (project_alias == None) and ObsLightBase.noaction:
                            return self.printCompletionListProject()
                    elif currentCommand in __parameter_package__:
                        package, listArgv = self.getParameter(listArgv)
                        if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                            return self.printCompletionListPackage(project_alias)
                    else:
                        return self.printUnknownCommand(currentCommand, __command_deletefile__)
                break

        if  Help :
            return self.print_Help(__command_deletefile__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_deletefile__)

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.print_Help(__command_deletefile__)

                return m.deleteFileFromPackage(project_alias, package, name)
            else:
                return self.print_Help(__command_deletefile__)

    def package_refresh(self, listArgv):
        '''
        
        '''
        Help = False
        OscStatus = False
        ObsStatus = False
        project_alias = None
        package = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_oscstatus__:
                OscStatus = True
            elif currentCommand in __parameter_obsstatus__:
                ObsStatus = True
            elif currentCommand in __parameter_project_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printCompletionListPackage(project_alias)
            else:
                return self.printUnknownCommand(currentCommand, __command_refresh__)

        if  Help :
            return self.print_Help(__command_refresh__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if not (OscStatus or ObsStatus):
                    OscStatus = True
                    ObsStatus = True

                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_refresh__)

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.print_Help(__command_refresh__)
                if OscStatus:
                    res = m.refreshOscDirectoryStatus(project_alias, package)
                    if self.testResult(res, getLineno()) == -1:return - 1
                if ObsStatus:
                    res = m.refreshObsStatus(project_alias, package)
                    if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.print_Help(__command_refresh__)

    def package_testConflict(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None
        package = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printCompletionListPackage(project_alias)
            else:
                return self.printUnknownCommand(currentCommand, __command_testConflict__)

        if  Help :
            return self.print_Help(__command_testConflict__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_testConflict__)

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.print_Help(__command_testConflict__)
                res = m.updatePackage(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                res = m.testConflict(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                self.printSimpleResult("the '" + package + "' is on Conflict: " + str(res), str(res))
                return 0
            else:
                return self.print_Help(__command_testConflict__)

    def package_resolveConflict(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None
        package = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printCompletionListPackage(project_alias)
            else:
                return self.printUnknownCommand(currentCommand, __command_testConflict__)

        if  Help :
            return self.print_Help(__command_resolveConflict__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_resolveConflict__)

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.print_Help(__command_resolveConflict__)

                res = m.resolveConflict(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.print_Help(__command_resolveConflict__)

    def execute(self, listArgv):

        if len(listArgv) == 0:
            self.print_Help()
            return 0
        else:
            currentCommand = listArgv[0]
            listArgv = listArgv[1:]

            if currentCommand in __command_help__ :
                return self.print_Help()
            elif currentCommand in __command_add__ :
                return self.package_add(listArgv)
            elif currentCommand in __command_del__:
                return self.package_delete(listArgv)
            elif currentCommand in __command_list__:
                return self.package_list(listArgv)
            elif currentCommand in __command_query__:
                return self.package_query(listArgv)
            elif currentCommand in __command_set__:
                return self.package_set(listArgv)
            elif currentCommand in __command_update__:
                return self.package_update(listArgv)
            elif currentCommand in  __command_commit__ :
                return self.package_commit(listArgv)
            elif currentCommand in __command_repair__ :
                return self.package_repair(listArgv)
            elif currentCommand in __command_current__:
                return self.package_current(listArgv)
            elif currentCommand in __command_addfile__:
                return self.package_addfile(listArgv)
            elif currentCommand in __command_deletefile__:
                return self.package_deletefile(listArgv)
            elif currentCommand in __command_refresh__:
                return self.package_refresh(listArgv)
            elif currentCommand in __command_testConflict__:
                return self.package_testConflict(listArgv)
            elif currentCommand in __command_resolveConflict__:
                return self.package_resolveConflict(listArgv)
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

        self.currentCommand = __command_repositories__[0]

        self.listCommand = __LIST_repositories__
        self.dicoParameterCompletion = __DICO_parameter_repositories_completion__
        self.dicoCommandHelp = __DICO_command_repositories_help__
        self.dicoParameter = __DICO_parameter_repositories__

    def repository_add(self, listArgv):
        '''
        
        '''
        Help = False

        From = False

        url = None
        alias = None
        fromProject = None
        project_alias = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
            elif currentCommand in __parameter_From__:
                From = True
                fromProject, listArgv = self.getParameter(listArgv)
                if (fromProject == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
                break
            else:
                url = currentCommand
                alias, listArgv = self.getParameter(listArgv)
                if (alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
                project_alias, listArgv = self.getParameter(listArgv)
                break

        if  Help:
            return self.print_Help(__command_add__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_add__)

                if From :
                    if fromProject == None:
                        return self.printError("Missing  fromProject", __command_commit__)

                    res = m.addRepo(projectLocalName=project_alias,
                                    fromProject=fromProject,
                                    repoUrl=None,
                                    alias=None)
                    if self.testResult(res, getLineno()) == -1:return - 1
                    return res
                else:
                    if url == None:
                        return self.printError("Missing  url", __command_commit__)
                    if alias == None:
                        return self.printError("Missing  alias", __command_commit__)

                    res = m.addRepo(projectLocalName=project_alias,
                                    fromProject=None,
                                    repoUrl=url,
                                    alias=alias)
                    if self.testResult(res, getLineno()) == -1:return - 1
                    return res
            else:
                return self.print_Help(__command_add__)

    def repository_delete(self, listArgv):
        '''
        
        '''
        Help = False

        repo_alias = None
        project_alias = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
            elif currentCommand in __parameter_repo_alias__:
                repo_alias, listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            else:
                return self.printUnknownCommand(currentCommand, __command_del__)

        if  Help:
            return self.print_Help(__command_del__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_del__)

                if repo_alias == None:
                    return self.printError("Missing  repo_alias", __command_del__)

                res = m.deleteRepo(projectLocalName=project_alias,
                                    repoAlias=repo_alias)

                if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.print_Help(__command_del__)


    def repository_modify(self, listArgv):
        '''
        
        '''
        Help = False

        repo_alias = None
        project_alias = None
        newUrl = None
        newAlias = None
        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
            elif currentCommand in __parameter_newUrl__:
                newUrl, listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_newAlias__:
                newAlias, listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_repo_alias__:
                repo_alias, listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            else:
                return self.printUnknownCommand(currentCommand, __command_modify__)
        if  Help:
            return self.print_Help(__command_modify__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_modify__)
                if repo_alias == None:
                    return self.printError("Missing  repo_alias ", __command_del__)

                if (newUrl == None) and (newAlias == None):
                    return self.printError("Missing  newUrl/newAlias ", __command_del__)

                res = m.modifyRepo(projectLocalName=project_alias,
                                   repoAlias=repo_alias,
                                   newUrl=newUrl,
                                   newAlias=newAlias)

                if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.print_Help(__command_modify__)

    def repository_query(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__):
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            else:
                return self.printUnknownCommand(currentCommand, __command_query__)

        if  Help :
            return self.print_Help(__command_query__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_query__)

                res = m.getChRootRepositories(projectLocalName=project_alias)
                if self.testResult(res, getLineno()) == -1:return - 1
                self.printSimpleResult("repository: ", "")
                for k in res:
                    self.printSimpleResult("Alias: " + k + "\t\tURL: " + res[k], k + " " + res[k])
                return 0
            else:
                return self.print_Help(__command_query__)

    def execute(self, listArgv):
        if len(listArgv) == 0:
            return self.print_Help()
        else:
            currentCommand = listArgv[0]
            listArgv = listArgv[1:]

            if currentCommand in __command_help__ :
                return self.print_Help()
            elif currentCommand in __command_add__:
                return self.repository_add(listArgv)
            elif currentCommand in __command_del__ :
                return self.repository_delete(listArgv)
            elif currentCommand in __command_modify__:
                return self.repository_modify(listArgv)
            elif currentCommand in __command_query__:
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

        self.currentCommand = __projectfilesystem__[0]

        self.listCommand = __LIST_filesystem__
        self.dicoParameterCompletion = __DICO_parameter_filesystem_completion__
        self.dicoCommandHelp = __DICO_command_filesystem_help__
        self.dicoParameter = __DICO_parameter_filesystem__


    def man(self):
        ObsLightBase.man(self)
        ObsLightObsRepository().man()

    def projectfilesystem_create(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                project_alias = currentCommand

        if  Help :
            return self.print_Help(__command_create__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_create__)

                res = m.createChRoot(projectLocalName=project_alias)
                if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.print_Help(__command_create__)

    def projectfilesystem_delete(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                project_alias, listArgv = self.getParameter(listArgv)

        if  Help :
            return self.print_Help(__command_del__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help()

                res = m.removeChRoot(projectLocalName=project_alias)
                if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.print_Help(__command_del__)

    def projectfilesystem_query(self, listArgv):
        '''
        
        '''
        Help = False
        path = False
        status = False

        project_alias = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) :
                Help = True
                break
            elif currentCommand in __parameter_path__:
                path = True
            elif currentCommand in __parameter_filesystemstatus__:
                status = True
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            else:
                return self.printUnknownCommand(currentCommand, __command_query__)

        if  Help :
            return self.print_Help(__command_query__)
        else:
            if not ObsLightBase.noaction:
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
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("path: " + res, str(res))

                if status :
                    res = m.isChRootInit(projectLocalName=project_alias)
                    if self.testResult(res, getLineno()) == -1:return - 1
                    val = "init" if res else "not init"
                    self.printSimpleResult("status: " + val, str(val))
            else:
                return self.print_Help(__command_query__)

    def projectfilesystem_enter(self, listArgv):
        '''
        
        '''
        Help = False

        project_alias = None
        package = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
                break
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printCompletionListPackage(project_alias)
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            else:
                return self.printUnknownCommand(currentCommand, __command_enter__)

        if  Help :
            return self.print_Help(__command_enter__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_enter__)

                res = m.goToChRoot(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.print_Help(__command_enter__)

    def projectfilesystem_executescript(self, listArgv):
        '''
        
        '''
        Help = False
        aPath = None

        project_alias = None
        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            else:
                aPath = currentCommand

        if  Help  :
            return self.print_Help(__command_executescript__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help()
                if aPath == None:
                    return self.printError("Missing  aPath", __command_executescript__)

                res = m.execScript(projectLocalName=project_alias, aPath=aPath)
                if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.print_Help(__command_executescript__)

    def execute(self, listArgv):
        if len(listArgv) == 0:
            return self.print_Help()
        else:
            currentCommand = listArgv[0]
            listArgv = listArgv[1:]

            if currentCommand in __command_help__ :
                return self.print_Help()
            elif currentCommand in __command_create__ :
                return self.projectfilesystem_create(listArgv)
            elif currentCommand in __command_del__:
                return self.projectfilesystem_delete(listArgv)
            elif currentCommand in __command_query__:
                return self.projectfilesystem_query(listArgv)
            elif currentCommand in __command_enter__:
                return self.projectfilesystem_enter(listArgv)
            elif currentCommand in __command_executescript__:
                return self.projectfilesystem_executescript(listArgv)
            elif currentCommand in __command_repositories__:
                return ObsLightObsRepository().execute(listArgv)
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

        self.currentCommand = __rpmbuild__[0]

        self.listCommand = __LIST_rpmbuild__
        self.dicoParameterCompletion = __DICO_parameter_rpmbuild_completion__
        self.dicoCommandHelp = __DICO_command_rpmbuild_help__
        self.dicoParameter = __DICO_parameter_rpmbuild__

    def rpmbuild_prepare(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None
        package = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printCompletionListPackage(project_alias)
            else :
                return self.printUnknownCommand(currentCommand, __command_prepare__)

        if  Help :
            return self.print_Help(__command_prepare__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_prepare__)

                if (package == None):
                    package = m.getCurrentPackage(project_alias)

                res = m.addPackageSourceInChRoot(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.print_Help(__command_prepare__)

    def rpmbuild_build(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None
        package = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printCompletionListPackage(project_alias)
            else :
                return self.printUnknownCommand(currentCommand, __command_build__)

        if  Help :
            return self.print_Help(__command_build__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_build__)

                if (package == None):
                    package = m.getCurrentPackage(project_alias)

                res = m.buildRpm(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.print_Help(__command_build__)


    def rpmbuild_install(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None
        package = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printCompletionListPackage(project_alias)
            else :
                return self.printUnknownCommand(currentCommand, __command_install__)

        if  Help :
            return self.print_Help(__command_install__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help()

                if (package == None):
                    package = m.getCurrentPackage(project_alias)

                res = m.installRpm(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.print_Help(__command_install__)

    def rpmbuild_package(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None
        package = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printCompletionListPackage(project_alias)
            else :
                return self.printUnknownCommand(currentCommand, __command_buildpackage__)

        if  Help :
            return self.print_Help(__command_buildpackage__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help()

                if (package == None):
                    package = m.getCurrentPackage(project_alias)

                res = m.packageRpm(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.print_Help(__command_buildpackage__)

    def rpmbuild_isInit(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None
        package = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printCompletionListPackage(project_alias)
            else :
                return self.printUnknownCommand(currentCommand, __command_isInit__)

        if  Help :
            return self.print_Help(__command_isInit__)
        else:
            if not ObsLightBase.noaction:
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
                if self.testResult(res, getLineno()) == -1:return - 1
                self.printSimpleResult("for '" + package + "' a patch is init: " + str(res), str(res))
                return 0
            else:
                return self.print_Help(__command_isInit__)

    def rpmbuild_createPatch(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None
        package = None
        patch = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
                break
            else:
                patch = currentCommand
                while self.testListArgv(listArgv):
                    currentCommand, listArgv = self.getParameter(listArgv)
                    if currentCommand in __parameter_project_alias__:
                        project_alias, listArgv = self.getParameter(listArgv)
                        if (project_alias == None) and ObsLightBase.noaction:
                            return self.printCompletionListProject()
                    elif currentCommand in __parameter_package__:
                        package, listArgv = self.getParameter(listArgv)
                        if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                            return self.printCompletionListPackage(project_alias)
                    else:
                        return self.printUnknownCommand(currentCommand, __command_createPatch__)
                break

        if  Help :
            return self.print_Help(__command_createPatch__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help(__command_createPatch__)

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.print_Help(__command_createPatch__)

                if (patch == None) :
                    return self.printError("Missing  <patch>", __command_createPatch__)

                res = m.createPatch(projectLocalName=project_alias, package=package, patch=patch)
                if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.print_Help(__command_createPatch__)

    def rpmbuild_updatepatch(self, listArgv):
        '''
        
        '''
        Help = False
        project_alias = None
        package = None

        while self.testListArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printCompletionListProject()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printCompletionListPackage(project_alias)
            else:
                return self.printUnknownCommand(currentCommand, __command_updatepatch__)

        if  Help :
            return self.print_Help(__command_updatepatch__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.print_Help()

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.print_Help()

                res = m.updatePatch(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.print_Help(__command_updatepatch__)

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
            elif currentCommand in __command_prepare__:
                return self.rpmbuild_prepare(listArgv)
            elif currentCommand in __command_build__ :
                return self.rpmbuild_build(listArgv)
            elif currentCommand in __command_install__:
                return self.rpmbuild_install(listArgv)
            elif currentCommand in __command_buildpackage__:
                return self.rpmbuild_package(listArgv)
            elif currentCommand in __command_isInit__:
                return self.rpmbuild_isInit(listArgv)
            elif currentCommand in __command_createPatch__:
                return self.rpmbuild_createPatch(listArgv)
            elif currentCommand in __command_updatepatch__:
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

        self.listCommand = __LIST_command__


    def execute(self, listArgv):
        '''
        Execute a list of arguments.
        '''

        ObsLightPrintManager.QUIET = 0
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
#                elif currentCommand in __micproject__ :
#                    return self.micproject(listArgv)
                elif currentCommand in __man__ :
                    ObsLightBase.manTag = True
                    self.printDescriptionLevel0()
                    ObsLightServer().man()
                    ObsLightObsproject().man()
                    ObsLightObsPackage().man()
                    ObsLightObsProjectfilesystem().man()
                    ObsLightRpmbuild().man()
                    self.printSyntaxHelp()
                    ObsLightBase.manTag = False
#                elif currentCommand in __qemuproject__ :
#                    return self.qemuproject(listArgv)
                else:
                    return self.printUnknownCommand(currentCommand)


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
