#
# Copyright 2011-2012, Intel Inc.
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

__PRGNAME__ = "OBS Light"

firstBorderLen = 4
secondBorderLen = 30
firstBorder = " "*firstBorderLen
secondBorder = " "*secondBorderLen

# function to format the help.
def createDoc(command, comment):
    '''
    Generate/format the documentation to be bash friendly.
     `command` should be a list of command aliases
     `comment` should be a string or a string list of comments
    about the command.
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
    Format and store documentation for `command`.
    '''
    __command_help_dict__[command[0]] = createDoc(command, comment)

def createServerSubCommandHelp(command, comment):
    '''
    Format and store documentation for a sub-command of 'server' command.
    '''
    __server_command_help_dict__[command[0]] = createDoc(command, comment)

def createObsProjectSubCommandHelp(command, comment):
    '''
    Format and store documentation for a sub-command of 'obsproject' command.
    '''
    __obsproject_command_help_dict__[command[0]] = createDoc(command, comment)

def createPackageSubCommandHelp(command, comment):
    '''
    Format and store documentation for a sub-command of 'package' command.
    '''
    __package_command_help_dict__[command[0]] = createDoc(command, comment)

def createFileSystemSubCommandHelp(command, comment):
    '''
    Format and store documentation for a sub-command of 'filesystem' command.
    '''
    __filesystem_command_help_dict__[command[0]] = createDoc(command, comment)

def createMicProjectSubCommandHelp(command, comment):
    '''
    Format and store documentation for a sub-command of 'micproject' command.
    '''
    __micproject_command_help_dict__[command[0]] = createDoc(command, comment)

def createRpmBuildSubCommandHelp(command, comment):
    '''
    Format and store documentation for a sub-command of 'rpmbuild' command.
    '''
    __rpmbuild_command_help_dict__[command[0]] = createDoc(command, comment)

def createRepositorySubCommandHelp(command, comment):
    '''
    Format and store documentation for a sub-command of 'repository' command.
    '''
    __repositories_command_help_dict__[command[0]] = createDoc(command, comment)


def createGlobalOption(option):
    '''
    Add `option` to the global option list.
    '''
    __global_option_list__.append(option[0])

def createCommand(command):
    '''
    Add `command` to the global command list.
    '''
    __global_command_list__.append(command[0])

def createParameterHelp(parameter, comment):
    '''
    Format and store parameter documentation.
    The parameter/documentation couple is unique.
    '''
    __parameter_help_dict__[parameter[0]] = createDoc(parameter, comment)

def appendServerSubCommand(command):
    """
    Append sub-command to command 'server'.
    """
    __server_subcommand_list__.append(command[0])

def appendObsProjectSubCommand(command):
    """
    Append sub-command to command 'obsproject'.
    """
    __obsproject_subcommand_list__.append(command[0])

def appendPackageSubCommand(command):
    """
    Append sub-command to command 'package'.
    """
    __package_subcommand_list__.append(command[0])

def appendFileSystemSubCommand(command):
    """
    Append sub-command to command 'filesystem'.
    """
    __filesystem_subcommand_list__.append(command[0])

def appendRepositoriesSubCommand(command):
    """
    Append sub-command to command 'repositories'.
    """
    __repositories_subcommand_list__.append(command[0])

def appendRpmBuildSubCommand(command):
    """
    Append sub-command to command 'rpmbuild'.
    """
    __rpmbuild_subcommand_list__.append(command[0])

def appendMicProjectSubCommand(command):
    """
    Append sub-command to command 'micproject'.
    """
    __micproject_subcommand_list__.append(command[0])


def _createCommandParameter(command,
                            parameterList,
                            completionBlacklist,
                            commandParameterDict,
                            commandParameterCompletionDict):
    commandParameterDict[command[0]] = []
    for parameter in parameterList:
        commandParameterDict[command[0]].append(parameter[0])
        if (completionBlacklist is None) or (not parameter in completionBlacklist):
            if not command[0] in commandParameterCompletionDict:
                commandParameterCompletionDict[command[0]] = []
            commandParameterCompletionDict[command[0]].append(parameter[0])

def createServerParameter(command, parameterList, completionBlacklist=None):
    '''
    Add parameter to the sub-command of 'server'.
    The parameters are automatically added to the completion list
    except if present in `completionBlacklist`.
    '''
    _createCommandParameter(command,
                            parameterList,
                            completionBlacklist,
                            __server_parameter_dict__,
                            __server_parameter_completion_dict__)

def createObsProjectParameter(command, parameterList, completionBlacklist=None):
    '''
    Add parameter to the sub-command of 'obsproject'.
    The parameters are automatically added to the completion list
    except if present in `completionBlacklist`.
    '''
    _createCommandParameter(command,
                            parameterList,
                            completionBlacklist,
                            __obsproject_parameter_dict__,
                            __obsproject_parameter_completion_dict__)

def createPackageParameter(command, parameterList, completionBlacklist=None):
    '''
    Add parameter to the sub-command of 'package'.
    The parameters are automatically added to the completion list
    except if present in `completionBlacklist`.
    '''
    _createCommandParameter(command,
                            parameterList,
                            completionBlacklist,
                            __package_parameter_dict__,
                            __package_parameter_completion_dict__)

def createFilesystemParameter(command, parameterList, completionBlacklist=None):
    '''
    Add parameter to the sub-command of 'filesystem'.
    The parameters are automatically added to the completion list
    except if present in `completionBlacklist`.
    '''
    _createCommandParameter(command,
                            parameterList,
                            completionBlacklist,
                            __filesystem_parameter_dict__,
                            __filesystem_parameter_completion_dict__)

def createRepositoriesParameter(command, parameterList, completionBlacklist=None):
    '''
    Add parameter to the sub-command of 'repositories'.
    The parameters are automatically added to the completion list
    except if present in `completionBlacklist`.
    '''
    _createCommandParameter(command,
                            parameterList,
                            completionBlacklist,
                            __repositories_parameter_dict__,
                            __repositories_parameter_completion_dict__)

def createRpmBuildParameter(command, parameterList, completionBlacklist=None):
    '''
    Add parameter to the sub-command of 'rpmbuild'.
    Rhe parameters are automatically added to the completion list
    except if present in `completionBlacklist`.
    '''
    _createCommandParameter(command,
                            parameterList,
                            completionBlacklist,
                            __rpmbuild_parameter_dict__,
                            __rpmbuild_parameter_completion_dict__)

def createMicProjectParameter(command, parameterList, completionBlacklist=None):
    '''
    Add parameter to the sub-command of 'micproject'
    The parameters are automatically added to the completion list
    except if present in `completionBlacklist`.
    '''
    _createCommandParameter(command,
                            parameterList,
                            completionBlacklist,
                            __micproject_parameter_dict__,
                            __micproject_parameter_completion_dict__)

__DESCRIPTION__ = __PRGNAME__ + ":" + "\n"
__DESCRIPTION__ += firstBorder + "Provides a tool to manage an OBS project on your"
__DESCRIPTION__ += " local machine in command line\n"
__DESCRIPTION__ += firstBorder + "For informations, see the Help section" + "\n"
__DESCRIPTION__ += firstBorder * 2 + "obslight --help\n"
__DESCRIPTION__ += firstBorder + "The GUI for %s is obslightgui\n" % __PRGNAME__
__DESCRIPTION__ += firstBorder + "A FAQ is available at:\n"
__DESCRIPTION__ += firstBorder * 2 + "* http://en.opensuse.org/openSUSE:OBS_Light_FAQ\n"
__DESCRIPTION__ += firstBorder + "For additional information, see:\n"
__DESCRIPTION__ += firstBorder * 2 + "* http://en.opensuse.org/openSUSE:OBS_Light\n"

__DESCRIPTION__ += "Usage: %s [global command] <command> [--command-options]\n" % __PRGNAME__
__DESCRIPTION__ += "\n"
__DESCRIPTION__ += "Type %s <command> --Help to get Help on a specific command.\n" % __PRGNAME__
__DESCRIPTION__ += "Commands:\n"

__SYNTAX_HELP__ = 'Syntax:\n'
__SYNTAX_HELP__ += firstBorder + '  project    the string "project"\n'
__SYNTAX_HELP__ += firstBorder + ' [project]   the optional string "project"\n'
__SYNTAX_HELP__ += firstBorder + ' <project>   a project name\n'
__SYNTAX_HELP__ += firstBorder + '[<project>]  an optional project name\n'
__SYNTAX_HELP__ += firstBorder + '{<project>}  an optional project name, if absent, '
__SYNTAX_HELP__ += 'the current used is taken\n'
__SYNTAX_HELP__ += firstBorder + '   BLANK     no parameter\n'

__global_option_list__ = []
__global_command_list__ = []

__command_help_dict__ = {}

#Command ****
__server_subcommand_list__ = []
__obsproject_subcommand_list__ = []
__package_subcommand_list__ = []
__filesystem_subcommand_list__ = []
__repositories_subcommand_list__ = []
__rpmbuild_subcommand_list__ = []
__micproject_subcommand_list__ = []
#__LIST_qemuproject__ = []

#Define the **** command help
__server_command_help_dict__ = {}
__obsproject_command_help_dict__ = {}
__package_command_help_dict__ = {}
__filesystem_command_help_dict__ = {}
__repositories_command_help_dict__ = {}
__rpmbuild_command_help_dict__ = {}
__micproject_command_help_dict__ = {}
#__DICO_command_qemuproject_help__ = {}

#Command **** parameter 
__server_parameter_dict__ = {}
__obsproject_parameter_dict__ = {}
__package_parameter_dict__ = {}
__filesystem_parameter_dict__ = {}
__repositories_parameter_dict__ = {}
__rpmbuild_parameter_dict__ = {}
__micproject_parameter_dict__ = {}
#__DICO_parameter_qemuproject__ = {}

#Define the parameter help
__parameter_help_dict__ = {}

#Define the parameter list for **** completion
__server_parameter_completion_dict__ = {}
__obsproject_parameter_completion_dict__ = {}
__package_parameter_completion_dict__ = {}
__filesystem_parameter_completion_dict__ = {}
__repositories_parameter_completion_dict__ = {}
__rpmbuild_parameter_completion_dict__ = {}
__micproject_parameter_completion_dict__ = {}
__DICO_parameter_qemuproject_completion__ = {}

#Command 
__info_quiet__ = ["quiet", "-quiet", "--quiet"]
__info_debug__ = ["debug", "-debug", "--debug"]
__version__ = ["version", "--version"]
__command_help__ = ["help", "-h", "-help", "--help"]
__noaction__ = ["noaction"]
__man_command__ = ["man"]

__help_command_help__ = "show this help message and exit"

createGlobalOption(__info_quiet__)
createGlobalOption(__info_debug__)
createGlobalOption(__version__)
createGlobalOption(__command_help__)
createGlobalOption(__noaction__)

createCommandHelp(__info_quiet__,
                 "run obslight in quiet mode")
createCommandHelp(__info_debug__,
                 "run obslight in debug mode")
createCommandHelp(__version__,
                 "show program version and exit")
createCommandHelp(__command_help__, __help_command_help__)
createCommandHelp(__noaction__,
                 "execute command but do nothing")
createCommandHelp(__man_command__,
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
#__command_repositories__ = ["repositories"]
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
__command_testBuildPackages__ = ["testBuildPackages"]

#Parameter 
__parameter_gitUrl__ = ["url"]
__parameter_reachable__ = ["reachable"]
__parameter_server_alias__ = ["server_alias", "alias"]
__parameter_login__ = ["login", "user"]
__parameter_password__ = ["password", "pwd"]
__parameter_api_url__ = ["api_url"]
__parameter_readonly__ = ["readonly"]
__parameter_repository_url__ = ["repository_url"]
__parameter_web_url__ = ["web_url"]
__parameter_project_alias__ = ["project_alias"]
__parameter_patch_mode__ = ["patch_modes", "pm"]
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
__parameter_obsRev__ = ["obsrev"]
__parameter_oscRev__ = ["oscrev"]
__parameter_filelist__ = ["filelist"]
__parameter_filelist_status__ = ["filelist_status"]
__parameter_obsstatus__ = ["obsStatus"]
__parameter_oscstatus__ = ["oscStatus"]
__parameter_specFile__ = ["specfile"]
__parameter_packageChrootDirectory__ = ["packageChrootDirectory"]
__parameter_packageSourceDirectory__ = ["packageSourceDirectory"]
__parameter_filesystemstatus__ = ["status"]
__parameter_currentPatch__ = ["currentpatch"]
__parameter_package_title__ = ["title"]
__parameter_packge_description__ = ["description"]
__parameter_message__ = ["message", "msg"]
__parameter_file__ = ["file"]
__parameter_From__ = ["from"]
__parameter_newUrl__ = ["newurl"]
__parameter_newAlias__ = ["newalias"]
__parameter_repo_url__ = ["repository_url"]
__parameter_repo_alias__ = ["repository_alias"]

#Define the server parameter help
createParameterHelp(__command_help__, __help_command_help__)
createParameterHelp(__parameter_gitUrl__ , ["the URL git project (like: git://XXX.org/XXX/XXX.git)"])
createParameterHelp(__parameter_reachable__, ["[reachable] optional"])
createParameterHelp(__parameter_server_alias__, "the alias of an OBS server ")
createParameterHelp(__parameter_login__, "the login for an account on an OBS server")
createParameterHelp(__parameter_password__, "the password for an account on an OBS server")
createParameterHelp(__parameter_api_url__, "the URL of an OBS server API")
createParameterHelp(__parameter_repository_url__, "the URL of an OBS server repository")
createParameterHelp(__parameter_web_url__, "the URL of an OBS server web interface")
createParameterHelp(__parameter_project_alias__ ,
                    "the name of the obslight project on the local drive.")
createParameterHelp(__parameter_readonly__,
                    "true if the project is in read only mode.")

createParameterHelp(__parameter_patch_mode__,
                    "The Patch Mode allows the user to automatically generate patches from his local work.\n\
                    The Patch Mode requires the user to perform a % prep and a first % build.\n\
                    If the user disables the Patch Mode, it definitely will be disabled.\n\
                    To reactivate the Patch Mode re-install the package.")
createParameterHelp(__parameter_name_on_obs__ , "the name of the project on the OBS server")
createParameterHelp(__parameter_project_title__ , "the title of a project")
createParameterHelp(__parameter_project_description__ , "the description of a project")
createParameterHelp(__parameter_server__, "the ???")
createParameterHelp(__parameter_project__, "the name of the project on the OBS server.")
createParameterHelp(__parameter_webpage__, "the webpage of the OBS project management ")
createParameterHelp(__parameter_repository__,
                    "the repository is the file depot of an OBS Project.")
createParameterHelp(__parameter_target__ , "the target repository of an OBS project")
createParameterHelp(__parameter_arch__ , "the architecture of an OBS project")
createParameterHelp(__parameter_maintainer__ , "the maintainer of an OBS project")
createParameterHelp(__parameter_bugowner__ , "the bugowner of an OBS project")
createParameterHelp(__parameter_remoteurl__ ,
                    "an OBS project can build again a remote project through a remote project link")
createParameterHelp(__parameter_path__ , "a file path")
createParameterHelp(__parameter_package__, "a package name")
createParameterHelp(__parameter_available__, "result is available ")
createParameterHelp(__parameter_status__, "the status")
createParameterHelp(__parameter_revision__, "the revision")
createParameterHelp(__parameter_url__, "the URL")
createParameterHelp(__parameter_obsRev__, "the OBS server package revision")
createParameterHelp(__parameter_oscRev__, "the OSC local revision")
createParameterHelp(__parameter_filelist__, "the list of files of a package")
createParameterHelp(__parameter_filelist_status__, "the list of files of a package with status.")
createParameterHelp(__parameter_obsstatus__, "the OBS status")
createParameterHelp(__parameter_oscstatus__, "OSC status")
createParameterHelp(__parameter_specFile__, "the spec file name")
createParameterHelp(__parameter_packageChrootDirectory__, "the directory of the project file system")
createParameterHelp(__parameter_packageSourceDirectory__, "the OSC package directory")
createParameterHelp(__parameter_filesystemstatus__, "the project file system directory")
createParameterHelp(__parameter_currentPatch__, "the name of the current patch of the local package")
createParameterHelp(__parameter_package_title__, "the title of a package")
createParameterHelp(__parameter_packge_description__, "the description of a package")
createParameterHelp(__parameter_message__, "a text message")
createParameterHelp(__parameter_file__, "a file name")
createParameterHelp(__parameter_From__, "specify the local project")
createParameterHelp(__parameter_newUrl__, "the new URL of the repository")
createParameterHelp(__parameter_newAlias__, "the new alias of the repository")
createParameterHelp(__parameter_repo_url__, "the URL of a repository")
createParameterHelp(__parameter_repo_alias__, "the alias of a repository")

#Global command
__server_command__ = ["server"]
__obsproject_command__ = ["obsproject"]
__package_command__ = ["package"]
__projectfilesystem_command__ = ["projectfilesystem", "projectfs", "filesystem", "pfs"]
__rpmbuild_command__ = ["rpmbuild", "rb"]
#__micproject__ = ["micproject"] #Feature
__man_command__ = ["man"]
#__qemuproject__ = ["qemuproject"] #Feature

createCommand(__server_command__)
createCommand(__obsproject_command__)
createCommand(__package_command__)
createCommand(__projectfilesystem_command__)
createCommand(__rpmbuild_command__)
#createCommand(__micproject__) #Feature
createCommand(__man_command__)
#createCommand(__qemuproject__) #Feature

createCommandHelp(__server_command__, "Manage the OBS servers")
createCommandHelp(__obsproject_command__, "Manage the OBSlight projects")
createCommandHelp(__package_command__, "Manage the packages of OBS Light projects")
createCommandHelp(__projectfilesystem_command__,
                  "Manage the project filesystem of OBS Light project")
createCommandHelp(__rpmbuild_command__, "Manage the build of packages into the project filesystem")
#createCommandHelp(__micproject__, "Manage image biulding") #Feature
createCommandHelp(__man_command__, "print the man help document")
#createCommandHelp(__command_repositories__, ["the command for file system repositories"])
#createCommandHelp(__qemuproject__, "Manage qemu") #Feature


#Command server
appendServerSubCommand(__command_help__)
appendServerSubCommand(__command_test__)
appendServerSubCommand(__command_list__)
appendServerSubCommand(__command_query__)
appendServerSubCommand(__command_set__)
appendServerSubCommand(__command_add__)
appendServerSubCommand(__command_del__)
appendServerSubCommand(__command_current__)

#Define the server command help
createServerSubCommandHelp(__command_help__, __help_command_help__)

createServerSubCommandHelp(__command_test__,
                           ["server test server_alias <server_alias>",
                            "  test the server alias",
                            "login <login> password <password> api_url <api_url> ",
                            "  test the API URL."])

createServerSubCommandHelp(__command_list__,
                           ["server list [reachable]",
                            "  if reachable  -> return all servers",
                            "  else  -> return only the available servers"])

createServerSubCommandHelp(__command_query__,
                           ["server query [login|apiurl|repository_url|weburl] " +
                            "{server_alias <server_alias>}",
                            "  return the server parameters."])

createServerSubCommandHelp(__command_set__,
                           ["server set [login <login>] [apiurl <apiurl>] " +
                            "[repository_url <repository_url>]" +
                            "[weburl <web_url>] {server_alias <server_alias>}",
                            "  set the server parameters"])

createServerSubCommandHelp(__command_add__,
                           ["server add server_alias <server_alias> login <login> " +
                            "password <password> api_url <api_url> repository_url " +
                            "<repository_url> web_url <web_url>",
                            "  add a new OBS server"])

createServerSubCommandHelp(__command_del__,
                           ["server delete <server_alias> ",
                            "  delete an OBS server"])

createServerSubCommandHelp(__command_current__,
                           ["server current BLANK",
                            "  return the current OBS server"])

#Define the parameter list for server command


createServerParameter(__command_test__, [__command_help__,
                                         __parameter_server_alias__,
                                         __parameter_login__,
                                         __parameter_password__,
                                         __parameter_api_url__])

createServerParameter(__command_list__, [__parameter_reachable__, __command_help__])

createServerParameter(__command_query__, [__command_help__,
                                          __parameter_server_alias__,
                                          __parameter_login__,
                                          __parameter_api_url__,
                                          __parameter_repository_url__,
                                          __parameter_web_url__])

createServerParameter(__command_set__, [__command_help__,
                                        __parameter_server_alias__,
                                        __parameter_login__,
                                        __parameter_api_url__,
                                        __parameter_repository_url__,
                                        __parameter_web_url__])

createServerParameter(__command_add__, [__command_help__,
                                        __parameter_server_alias__,
                                        __parameter_login__,
                                        __parameter_password__,
                                        __parameter_api_url__,
                                        __parameter_repository_url__,
                                        __parameter_web_url__])

createServerParameter(__command_del__, [__command_help__,
                                        __parameter_server_alias__],
                                        [__parameter_server_alias__])

createServerParameter(__command_current__, [__command_help__])

#Command obsproject 
appendObsProjectSubCommand(__command_help__)
appendObsProjectSubCommand(__command_create__)
appendObsProjectSubCommand(__command_list__)
appendObsProjectSubCommand(__command_add__)
appendObsProjectSubCommand(__command_del__)
appendObsProjectSubCommand(__command_query__)
appendObsProjectSubCommand(__command_set__)
appendObsProjectSubCommand(__command_current__)
#appendObsProjectSubCommand(__command_import__)
#appendObsProjectSubCommand(__command_export__)
appendObsProjectSubCommand(__command_dependencyrepositories__)
appendObsProjectSubCommand(__command_testBuildPackages__)

#Define the obsproject command help
createObsProjectSubCommandHelp(__command_help__, __help_command_help__)

createObsProjectSubCommandHelp(__command_create__,
                               ["obsproject create server_alias <server_alias> name_on_obs <name_on_obs> [title <title>] [description <description>]",
                                "  Create a new project on the OBS server"])

createObsProjectSubCommandHelp(__command_list__,
                               ["obsproject list BLANK",
                                "  return all local projects.",
                                "obsproject list server_alias <server_alias> " +
                                "[arch <arch>|maintainer|bugowner|remoteurl]",
                                "  return project on the OBS server filtered " +
                                "with arch, maintainer, bugowner, remoteurl"])

createObsProjectSubCommandHelp(__command_current__,
                               ["obsproject current BLANK",
                                "  print the curent local project"])

createObsProjectSubCommandHelp(__command_dependencyrepositories__,
                               ["obsproject dependencyrepositories {<project_alias>}",
                                "  print the dependency repositories of a local project "])

createObsProjectSubCommandHelp(__command_del__,
                               ["obsproject delete <project_alias>",
                                "  delete a local project"])

createObsProjectSubCommandHelp(__command_add__,
                               ["obsproject add <project_alias> <name_on_obs> " +
                                "<target> <arch> {<server_alias>}",
                                "  create a local project"])

createObsProjectSubCommandHelp(__command_query__,
                               ["obsproject query [title|description|obsServer|webpage|" +
                                "repository|target|architecture] {project_alias <project_alias>}",
                                "  query local project parameters",
                                "obsproject query [title|description|target|architecture|" +
                                "remoteurl|maintainer|bugowner|readonly] server_alias <server_alias> " +
                                "obsproject <project> ",
                                "  query OBS project parameters"])

createObsProjectSubCommandHelp(__command_set__,
                               ["obsproject set [title <title>] [description <description>] " +
                                "{project_alias <project_alias>}",
                                "  modify local project parameters"])

#createObsProjectSubCommandHelp(__command_import__,
#                               ["obsproject import <path>",
#                                "  import a backup file"])

#createObsProjectSubCommandHelp(__command_export__,
#                               ["obsproject export <path> {<project_alias>}}",
#                                "  export a backup file"])

createObsProjectSubCommandHelp(__command_testBuildPackages__,
                               ["test the build of package on the obslight" +
                                "<repository_alias> {project_alias <project_alias>} " +
                                "{package <package>}",
                                "import/prep/build/remove"])

#Define the obsproject parameter help
createObsProjectParameter(__command_create__, [__command_help__,
                                               __parameter_server_alias__,
                                               __parameter_name_on_obs__,
                                               __parameter_project_title__,
                                               __parameter_project_description__])


createObsProjectParameter(__command_list__, [__command_help__,
                                             __parameter_server_alias__,
                                             __parameter_arch__,
                                             __parameter_maintainer__,
                                             __parameter_bugowner__,
                                             __parameter_remoteurl__])

createObsProjectParameter(__command_current__, [__command_help__])

createObsProjectParameter(__command_dependencyrepositories__,
                          [__command_help__, __parameter_project_alias__],
                          [__parameter_project_alias__])

createObsProjectParameter(__command_del__,
                          [__command_help__, __parameter_project_alias__],
                          [__parameter_project_alias__])

createObsProjectParameter(__command_add__,
                          [__command_help__,
                           __parameter_project_alias__,
                           __parameter_name_on_obs__,
                           __parameter_target__,
                           __parameter_arch__,
                           __parameter_server_alias__],
                          [__parameter_project_alias__,
                           __parameter_name_on_obs__,
                           __parameter_target__,
                           __parameter_arch__,
                           __parameter_server_alias__])

createObsProjectParameter(__command_query__,
                          [__command_help__,
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
                           __parameter_project__,
                           __parameter_readonly__],
                          [])

createObsProjectParameter(__command_set__, [__command_help__,
                                            __parameter_project_title__,
                                            __parameter_project_description__,
                                            __parameter_project_alias__])

#createObsProjectParameter(__command_import__, [__command_help__,
#                                               __parameter_path__],
#                                               [__parameter_path__])

#createObsProjectParameter(__command_export__,
#                          [__command_help__,
#                           __parameter_path__,
#                           __parameter_project_alias__],
#                          [__parameter_path__,
#                           __parameter_project_alias__])

createObsProjectParameter(__command_testBuildPackages__, [__command_help__,
                                                            __parameter_project_alias__,
                                                            __parameter_package__])

#Command package
appendPackageSubCommand(__command_help__)
appendPackageSubCommand(__command_create__)
appendPackageSubCommand(__command_list__)
appendPackageSubCommand(__command_current__)
appendPackageSubCommand(__command_import__)
appendPackageSubCommand(__command_add__)
appendPackageSubCommand(__command_del__)
appendPackageSubCommand(__command_query__)
appendPackageSubCommand(__command_set__)
appendPackageSubCommand(__command_update__)
appendPackageSubCommand(__command_commit__)
appendPackageSubCommand(__command_repair__)
#appendPackageSubCommand(__command_addfile__)
#appendPackageSubCommand(__command_deletefile__)
appendPackageSubCommand(__command_refresh__)
appendPackageSubCommand(__command_testConflict__)
appendPackageSubCommand(__command_resolveConflict__)

#Define the package command help
createPackageSubCommandHelp(__command_help__, __help_command_help__)



createPackageSubCommandHelp(__command_create__,
                            ["obsproject create server_alias <server_alias> package <package>\
                             name_on_obs <name_on_obs> [title <title>] [description <description>]",
                            " Create a new package on the OBS server"])

createPackageSubCommandHelp(__command_list__,
                            ["package list [available] {project_alias <project_alias>}",
                             "print the package list of the project",
                             "if available, print the packages avaible on the OBS project server"])

createPackageSubCommandHelp(__command_current__,
                            ["package current {project_alias <project_alias>}",
                             "print the current package use on the local project"])

createPackageSubCommandHelp(__command_import__,
                            ["package import {project_alias <project_alias>} path|url <path|url> package <package>",
                             "import a source git package {path|url} to local project with the name package"])

createPackageSubCommandHelp(__command_add__,
                            ["package add {package <package>} {project_alias <project_alias>}",
                             "add a package from the OBS project to local project"])

createPackageSubCommandHelp(__command_del__,
                            ["package delete {package <package>} {project_alias <project_alias>}",
                             "delete package from local project"])

createPackageSubCommandHelp(__command_query__,
                            ["package query [title|description|url|filelist] {package <package> " +
                             "{server_alias <server_alias> {project <project>}}} ",
                             "  query information from OBS project",
                             "package query [title|description|obsrev|oscrev|filelist|" +
                             "filelist_status|obsstatus|oscstatus|specfile|" +
                             "packageChrootDirectory|packageSourceDirectory|filesystemstatus|" +
                             "currentpatch] {package <package> {project_alias <project_alias>} }",
                             "  query information from local project",
                             "  if no information is specified all informations are queried"])

createPackageSubCommandHelp(__command_set__,
                            ["package set [title <title>] [description <description>] " +
                             "{package <package> {project_alias <project_alias>}} ",
                             "  set information to local project"])

createPackageSubCommandHelp(__command_update__,
                            ["package update {package <package> {project_alias <project_alias>}}",
                             "  update information from OBS project to local project"])

createPackageSubCommandHelp(__command_commit__,
                            ["package commit <message> {package <package> " +
                             "{project_alias <project_alias>}}",
                             "  commit information from local project to OBS project"])

createPackageSubCommandHelp(__command_repair__,
                            ["package repair {package <package> {project_alias <project_alias>}",
                             "  repair an inconsistent package working copy"])

#createPackageSubCommandHelp(__command_addfile__,
#                            ["package addfile <path> {package <package> " +
#                             "{project_alias <project_alias>}",
#                             "  add file to local package"])
#
#createPackageSubCommandHelp(__command_deletefile__,
#                            ["package deletefile <file> {package <package> " +
#                             "{project_alias <project_alias>}",
#                             "  delete file from local package"])

createPackageSubCommandHelp(__command_refresh__,
                            ["package refresh [oscStatus|obsstatus] {package <package> " +
                             "{project_alias <project_alias>}}",
                             "  refresh osc,obs statuses",
                             "  if oscstatus and obsstatus are not specified, " +
                             "the two statuses are refreshed"])

createPackageSubCommandHelp(__command_testConflict__,
                            ["package testconflict {package <package>} " +
                             "{project_alias <project_alias>}",
                             "  test and print the status of conflict"])

createPackageSubCommandHelp(__command_resolveConflict__,
                            ["package resolveconflict {package <package>} " +
                             "{project_alias <project_alias>}",
                             "  try to resolve a conflict in package files"])
#Define the package parameter help
createPackageParameter(__command_list__, [__command_help__,
                                          __parameter_available__,
                                          __parameter_project_alias__])

createPackageParameter(__command_create__, [__command_help__,
                                               __parameter_server_alias__,
                                               __parameter_name_on_obs__,
                                               __parameter_package__,
                                               __parameter_project_title__,
                                               __parameter_project_description__])

createPackageParameter(__command_current__, [__command_help__,
                                             __parameter_project_alias__])

createPackageParameter(__command_import__, [__command_help__,
                                            __parameter_project_alias__,
                                            __parameter_gitUrl__,
                                            __parameter_package__])

createPackageParameter(__command_add__, [__command_help__,
                                         __parameter_package__,
                                         __parameter_project_alias__])

createPackageParameter(__command_del__, [__command_help__,
                                         __parameter_package__,
                                         __parameter_project_alias__])

createPackageParameter(__command_query__, [__command_help__,
                                           __parameter_package_title__,
                                           __parameter_packge_description__,
                                           __parameter_url__,
                                           __parameter_filelist__,
                                           __parameter_filelist_status__,
                                           __parameter_package__,
                                           __parameter_server_alias__,
                                           __parameter_project__,
                                           __parameter_obsRev__,
                                           __parameter_oscRev__,
                                           __parameter_obsstatus__,
                                           __parameter_oscstatus__,
                                           __parameter_specFile__,
                                           __parameter_packageChrootDirectory__,
                                           __parameter_packageSourceDirectory__,
                                           __parameter_filesystemstatus__,
                                           __parameter_currentPatch__,
                                           __parameter_project_alias__,
                                           __parameter_patch_mode__])

createPackageParameter(__command_set__, [__command_help__,
                                         __parameter_package_title__,
                                         __parameter_packge_description__,
                                         __parameter_package__,
                                           __parameter_project_alias__,
                                           __parameter_patch_mode__])

createPackageParameter(__command_update__, [__command_help__,
                                            __parameter_package__,
                                           __parameter_project_alias__])

createPackageParameter(__command_commit__, [__command_help__,
                                            __parameter_message__,
                                            __parameter_package__,
                                           __parameter_project_alias__], [__parameter_message__])

createPackageParameter(__command_repair__, [__command_help__,
                                            __parameter_package__,
                                           __parameter_project_alias__])

#createPackageParameter(__command_addfile__, [__command_help__,
#                                             __parameter_path__,
#                                             __parameter_package__,
#                                             __parameter_project_alias__], [__parameter_path__])
#
#createPackageParameter(__command_deletefile__, [__command_help__,
#                                                __parameter_file__,
#                                             __parameter_package__,
#                                             __parameter_project_alias__], [__parameter_file__])

createPackageParameter(__command_refresh__, [__command_help__,
                                             __parameter_obsstatus__,
                                             __parameter_oscstatus__,
                                             __parameter_package__,
                                             __parameter_project_alias__])

createPackageParameter(__command_testConflict__, [__command_help__,
                                                   __parameter_package__,
                                                   __parameter_project_alias__])

createPackageParameter(__command_resolveConflict__, [__command_help__,
                                                     __parameter_package__,
                                                     __parameter_project_alias__])

#Command filesystem
appendFileSystemSubCommand(__command_help__)
appendFileSystemSubCommand(__command_create__)
appendFileSystemSubCommand(__command_del__)
appendFileSystemSubCommand(__command_query__)
appendFileSystemSubCommand(__command_enter__)
appendFileSystemSubCommand(__command_executescript__)
#appendFileSystemSubCommand(__command_repositories__)

#Define the filesystem command help
createFileSystemSubCommandHelp(__command_help__, __help_command_help__)

createFileSystemSubCommandHelp(__command_create__,
                               ["projectfilesystem create {<project_alias>}",
                                "  Create a new project filesystem"])

createFileSystemSubCommandHelp(__command_del__,
                               ["projectfilesystem delete <project_alias>",
                                "  Remove the project filesystem"])

createFileSystemSubCommandHelp(__command_query__,
                               ["projectfilesystem query [path|status] " +
                                "{project_alias <project_alias>}",
                                "  print the path and the status of a filesystem"])

createFileSystemSubCommandHelp(__command_enter__,
                               ["projectfilesystem enter [package <package>] " +
                                "{project_alias <project_alias>}",
                                "  chroot into the filesystem"])

createFileSystemSubCommandHelp(__command_executescript__,
                               ["projectfilesystem executescript <path> " +
                                "{project_alias <project_alias>}",
                                ""])

#createFileSystemSubCommandHelp(__command_repositories__,
#                               ["the sub-command for file system repositories"])

#Define the filesystem parameter help
createFilesystemParameter(__command_create__,
                          [__command_help__,
                           __parameter_project_alias__],
                          [__parameter_project_alias__])

createFilesystemParameter(__command_del__,
                          [__command_help__,
                           __parameter_project_alias__],
                          [__parameter_project_alias__])

createFilesystemParameter(__command_query__,
                          [__command_help__,
                           __parameter_path__,
                           __parameter_filesystemstatus__,
                           __parameter_project_alias__])

createFilesystemParameter(__command_enter__,
                          [__command_help__,
                           __parameter_package__,
                           __parameter_project_alias__])

createFilesystemParameter(__command_executescript__,
                          [__command_help__,
                           __parameter_path__,
                           __parameter_project_alias__],
                          [__parameter_path__])

#createFilesystemParameter(__command_repositories__, [__command_help__])

#Command Repositories
appendRepositoriesSubCommand(__command_help__)
appendRepositoriesSubCommand(__command_add__)
appendRepositoriesSubCommand(__command_del__)
appendRepositoriesSubCommand(__command_query__)
appendRepositoriesSubCommand(__command_modify__)

#Define the Repositories command help
createRepositorySubCommandHelp(__command_help__, __help_command_help__)

createRepositorySubCommandHelp(__command_add__,
                               ["projectfilesystem repositories add <repository_url> " +
                                "<repository_alias> {<project_alias>}",
                                "  add a repository by url/alias to the project filesystem",
                                "projectfilesystem repositories add from <source_project_alias>" +
                                " <destination_project_alias>",
                                "  add the repository of a local project to the project filesystem"])

createRepositorySubCommandHelp(__command_del__,
                               ["projectfilesystem repositories delete <repository_alias> " +
                                "{<project_alias>} ",
                                "  remove a repository from a project file system"])

createRepositorySubCommandHelp(__command_query__,
                               ["projectfilesystem repositories query project_alias <project_alias>",
                                "  print the url/alias of repositories of the project filesystem"])

createRepositorySubCommandHelp(__command_modify__,
                               ["projectfilesystem repositories modify [newUrl <repository_url>] " +
                                "[newAlias <repository_alias>] repository_alias " +
                                "<repository_alias> {project_alias <project_alias>}",
                                "  modify the url/alias of a repository"])



#Define the Repositories parameter help
createRepositoriesParameter(__command_add__, [__command_help__,
                                              __parameter_project_alias__,
                                              __parameter_From__], [__parameter_project_alias__])

createRepositoriesParameter(__command_del__, [__command_help__,
                                              __parameter_repo_alias__,
                                              __parameter_project_alias__])

createRepositoriesParameter(__command_query__, [__command_help__,
                                                __parameter_project_alias__])

createRepositoriesParameter(__command_modify__, [__command_help__,
                                                 __parameter_newUrl__,
                                                 __parameter_newAlias__,
                                                 __parameter_repo_alias__,
                                                 __parameter_project_alias__])



#Command rpmbuild
appendRpmBuildSubCommand(__command_help__)
appendRpmBuildSubCommand(__command_prepare__)
appendRpmBuildSubCommand(__command_build__)
appendRpmBuildSubCommand(__command_install__)
appendRpmBuildSubCommand(__command_buildpackage__)
appendRpmBuildSubCommand(__command_isInit__)
appendRpmBuildSubCommand(__command_createPatch__)
appendRpmBuildSubCommand(__command_updatepatch__)


#Define the rpmbuild command help
createRpmBuildSubCommandHelp(__command_help__, __help_command_help__)
createRpmBuildSubCommandHelp(__command_prepare__,
                             ["rpmbuild prepare {package <package>} {project_alias <project_alias>}",
                              "  create the the rpmbuild directory, build one time the " +
                              "package and initialize git"])

createRpmBuildSubCommandHelp(__command_build__,
                             ["rpmbuild build {package <package>} {project_alias <project_alias>}",
                              "  build the package"])

createRpmBuildSubCommandHelp(__command_install__,
                             ["rpmbuild install {package <package>} {project_alias <project_alias>}",
                              "  build and install the package"])

createRpmBuildSubCommandHelp(__command_buildpackage__,
                             ["rpmbuild buildpackage {package <package>} " +
                              "{project_alias <project_alias>}",
                              "  build, install and create the RPM package"])

createRpmBuildSubCommandHelp(__command_isInit__,
                             ["rpmbuild isinit {package <package>} {project_alias <project_alias>}",
                              "  print if 'rpmbuild prepare' was done for this package"])

createRpmBuildSubCommandHelp(__command_createPatch__,
                             ["rpmbuild createpatch <patch> {package <package>} " +
                              "{project_alias <project_alias>}",
                              "  create a current patch and add patch file into osc local " +
                              "package, and into specfile"])

createRpmBuildSubCommandHelp(__command_updatepatch__,
                             ["rpmbuild updatepatch {package <package> " +
                              "{project_alias <project_alias>}",
                              "update the current patch"])



#Define the rpmbuild parameter help
createRpmBuildParameter(__command_prepare__, [__command_help__,
                                              __parameter_package__,
                                              __parameter_project_alias__])

createRpmBuildParameter(__command_build__, [__command_help__,
                                            __parameter_package__,
                                              __parameter_project_alias__])

createRpmBuildParameter(__command_install__, [__command_help__,
                                              __parameter_package__,
                                              __parameter_project_alias__])

createRpmBuildParameter(__command_buildpackage__, [__command_help__,
                                                   __parameter_package__,
                                              __parameter_project_alias__])

createRpmBuildParameter(__command_isInit__, [__command_help__,
                                             __parameter_package__,
                                             __parameter_project_alias__])

createRpmBuildParameter(__command_createPatch__, [__command_help__,
                                                  __parameter_path__,
                                                  __parameter_package__,
                                                  __parameter_project_alias__],
                        [__parameter_path__])

createRpmBuildParameter(__command_updatepatch__, [__command_help__,
                                                  __parameter_package__,
                                                  __parameter_project_alias__])

createRpmBuildParameter(__command_testConflict__, [__command_help__,
                                                   __parameter_package__,
                                                   __parameter_project_alias__])


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

        self.__argv = sys.argv[1:]

        self.commandList = None
        self.parameterCompletionDict = None
        self.commandHelpDict = None
        self.parameterDict = None

        self.currentCommand = None

        self.parameterHelpDict = __parameter_help_dict__

    def setListArgv(self, arg):
        """
        Set the main list of arguments.
        You can set many lists of args separated by " , "
        """
        self.__argv = arg

    def getParameter(self, argv):
        '''
        return the first paramater and argv
        '''
        if argv is None or len(argv) < 1:
            return None, None
        else:
            return argv[0], argv[1:]

    def testArgv(self, argv):
        return  ((argv != None) and len(argv) > 0)

    def testResult(self, res, lineId):
        if res is None:
            print "ERROR NO RESULT " + __file__ + " " + str(lineId)
            return -1
        else:
            return 0

    def testServerAlias(self, server_alias):
        '''
        test server_alias 
        return the current OBS server if server_alias is None  
        '''
        if server_alias is None:
            m = ObsLightManager.getCommandLineManager()
            server_alias = m.getCurrentObsServer()
            if server_alias is None:
                print "No alias"
        return server_alias

    def main(self):
        """
        Execute the main list of arguments
        """
        while ("," in self.__argv):
            tmpListArgv = self.__argv[:self.__argv.index(",")]
            self.__argv = self.__argv[self.__argv.index(",") + 1:]
            self.execute(tmpListArgv)

        return self.execute(self.__argv)

    def printServerCompletionList(self):
        m = ObsLightManager.getCommandLineManager()
        res = m.getObsServerList(reachable=False)
        if res is not None:
            print " ".join(res)
        return 0

    def printProjectCompletionList(self):
        m = ObsLightManager.getCommandLineManager()
        res = m.getLocalProjectList()
        if res is not None:
            print " ".join(res)
        return 0

    def printPackageCompletionList(self, project_alias, onlyInstalled=True):
        m = ObsLightManager.getCommandLineManager()
        if m.isALocalProject(project_alias):
            res = m.getLocalProjectPackageList(projectLocalName=project_alias, onlyInstalled=onlyInstalled)
            if res is not None:
                print " ".join(res)
            return 0
        else:
            return -1

    def printServerObsProjectCompletionList(self, server_alias):
        m = ObsLightManager.getCommandLineManager()
        res = m.getObsServerProjectList(serverApi=server_alias)
        if res is not None:
            print " ".join(res)
        return 0

    def execute(self, argv):
        '''
        Execute a list of arguments.
        '''
        pass

    def printHelp(self, cmd=None):
        '''
        print help.
        '''
        if isinstance(cmd, (list, tuple)):
            cmd = cmd[0]

        if ObsLightBase.noaction:
            if cmd is None:
                if self.commandList is not None:
                    print " ".join(self.commandList)
            else:
                if self.parameterCompletionDict is not None:
                    if cmd in self.parameterCompletionDict:
                        print " ".join(self.parameterCompletionDict[cmd])
                    else:
                        message = "ERROR: '%s' is not in self.parameterCompletionDict: %s"
                        print message % (cmd, ",".join(self.parameterCompletionDict.keys()))
                        return 1
            return 0
        else:
            if cmd is None:
                print "Command: " + self.currentCommand
                if self.currentCommand in __command_help_dict__.keys():
                    print __command_help_dict__[self.currentCommand]
                    print
                else:
                    message = "ERROR: '%s' is not in __command_help_dict__: %s"
                    print message % (self.currentCommand, ",".join(__command_help_dict__.keys()))
                    return 1

                print "Sub-command:"
                if self.commandList is not None:
                    for cmd in self.commandList:
                        if cmd in self.commandHelpDict.keys():
                            print self.commandHelpDict[cmd]
                        else:
                            message = "ERROR: '%s' is not in self.commandHelpDict: %s"
                            print message % (cmd, ",".join(self.commandHelpDict.keys()))
                            return 1
            else:
                if self.commandHelpDict is not None:
                    if cmd in __command_help__:
                        return 0
                    if cmd in self.commandHelpDict.keys():
                        print "Sub-command: " + self.currentCommand + " " + cmd
                        print self.commandHelpDict[cmd]

                        print "Parameter:"
                        if self.parameterDict != None:
                            if cmd in self.parameterDict.keys():
                                for para in self.parameterDict[cmd]:
                                    if self.parameterHelpDict != None:
                                        if para in self.parameterHelpDict.keys():
                                            print self.parameterHelpDict[para]
                                        else:
                                            message = "ERROR: '%s' is not in self.parameterHelpDict"
                                            message += ": %s"
                                            print message % (para,
                                                        ",".join(self.parameterHelpDict.keys()))
                                            return 1
                                print
                            else:
                                message = "ERROR '%s' is not in self.parameterDict: %s"
                                print message % (cmd, ",".join(self.parameterDict.keys()))
                                return 1
                    else:
                        message = "ERROR: '%s' is not in self.commandHelpDict: %s"
                        print message % ",".join(self.commandHelpDict.keys())
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
        print the pseudo-man doc of the commands
        '''
        self.printHelp()

        for command in self.commandList:
            self.printHelp(command)

    def networkRequest(self):
        if ObsLightPrintManager.QUIET == 0:
            sys.stdout.write("Network Request ...")
            sys.stdout.flush()

    def printResultList(self, result, comment=None, row=True):
        if ObsLightPrintManager.QUIET == 0:
            sys.stdout.write("\r" + " "*20 + "\r")
            if comment is not None:
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

    def printErrorMessage(self, message):
        if ObsLightBase.noaction:
            print ""
        else:
            print message

    def printError(self, message, command):
        if ObsLightBase.noaction:
            self.printHelp(command)
        else:
            if ObsLightPrintManager.QUIET == 0:
                print message

    def printSimpleResult(self, verboseResult, result):
        if ObsLightPrintManager.QUIET == 0:
            sys.stdout.write("\r" + " "*20 + "\r")
            sys.stdout.write(verboseResult + "\n")
            sys.stdout.flush()
        else:
            sys.stdout.write(result + "\n")
            sys.stdout.flush()

    def printBoolResult(self, printableResult, boolResult):
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
            for h in __global_command_list__:
                print __command_help_dict__[h]
            print
            print "global Options:\n"
            for h in __global_option_list__:
                print __command_help_dict__[h]
            print
        return 0

    def printDescriptionLevel0(self):
        '''
        print the global description or return the list for completion
        '''
        if ObsLightBase.noaction:
            listArg = __global_option_list__
            listArg.extend(__global_command_list__)
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
            print "ERROR: UNKNOWN COMMAND: ", currentCommand
            if listCommand is None:
                avalableCommand = self.commandList
            else:
                avalableCommand = self.parameterDict[listCommand[0]]
            if (avalableCommand is not None) and (len(avalableCommand) > 0):
                print "Available argument are :" + ",".join(avalableCommand)
        else:
            self.printHelp(listCommand)
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

        self.currentCommand = __server_command__[0]

        self.commandList = __server_subcommand_list__
        self.parameterCompletionDict = __server_parameter_completion_dict__
        self.commandHelpDict = __server_command_help_dict__
        self.parameterDict = __server_parameter_dict__

    def execute(self, listArgv):
        if len(listArgv) == 0:
            return self.printHelp()
        else:
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                return self.printHelp()
            elif currentCommand in __command_current__:
                return self.server_current(listArgv)
            elif currentCommand in __command_test__:
                return self.server_test(listArgv)
            elif currentCommand in __command_list__:
                return self.server_list(listArgv)
            elif currentCommand in __command_query__:
                return self.server_query(listArgv)
            elif currentCommand in __command_set__:
                return self.server_set(listArgv)
            elif currentCommand in __command_add__:
                return self.server_add(listArgv)
            elif currentCommand in __command_del__:
                return self.server_del(listArgv)
            else:
                return self.printUnknownCommand(currentCommand)
        return 0

    def server_test(self, listArgv):
        Help = False
        server_alias = None
        login = None
        password = None
        api_url = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_server_alias__:
                server_alias, listArgv = self.getParameter(listArgv)
                if (server_alias == None) and ObsLightBase.noaction:
                    return self.printServerCompletionList()
            elif currentCommand in __parameter_login__:
                login, listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_password__:
                password, listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_api_url__:
                api_url, listArgv = self.getParameter(listArgv)
            else:
                return self.printUnknownCommand(currentCommand, __command_test__)

        if Help == True:
            return self.printHelp(__command_test__)
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
                        self.printBoolResult("'%s' is reachable" % api_url, 1)
                    elif res == 1:
                        message = "'%s' is not reachable, user and password are wrong." % api_url
                        self.printBoolResult(message, 0)
                    elif res == 2:
                        self.printBoolResult("'%s' is not reachable, API is wrong.." % api_url, 0)
                    else:
                        self.printBoolResult("'%s' is not reachable" % api_url, 0)
                    return 0
                else:
                    return -1
            else:
                return self.printHelp(__command_test__)
        else:
            return self.printHelp(__command_test__)

    def server_list(self, listArgv):
        Help = False
        reachable = False

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_reachable__:
                reachable = True
            else:
                return self.printUnknownCommand(currentCommand, __command_list__)

        if Help == True:
            return self.printHelp(__command_list__)
        if not ObsLightBase.noaction:
            m = ObsLightManager.getCommandLineManager()
            if reachable:self.networkRequest()
            res = m.getObsServerList(reachable=reachable)
            if self.testResult(res, getLineno()) == -1 :return - 1
            self.printResultList(res)
            return 0
        else:
            return self.printHelp(__command_list__)

    def server_query(self, listArgv):
        Help = False
        login = False
        api_url = False
        repository_url = False
        weburl = False
        server_alias = None
        while self.testArgv(listArgv):
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
                    return self.printServerCompletionList()
            else:
                return self.printUnknownCommand(currentCommand, __command_query__)

        if Help == True:
            return self.printHelp(__command_query__)
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

                if login:
                    res = m.getObsServerParameter(obsServerAlias=server_alias,
                                                  parameter="user")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    message = "alias '%s'\tuser:\t%s" % (server_alias, str(res))
                    self.printSimpleResult(message, str(res))
                if api_url:
                    res = m.getObsServerParameter(obsServerAlias=server_alias,
                                                  parameter="serverAPI")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    message = "alias '%s'\tserverAPI:\t%s" % (server_alias, str(res))
                    self.printSimpleResult(message, str(res))
                if repository_url:
                    res = m.getObsServerParameter(obsServerAlias=server_alias,
                                                  parameter="serverRepo")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    message = "alias '%s'\tserverRepo:\t%s" % (server_alias, str(res))
                    self.printSimpleResult(message, str(res))
                if weburl:
                    res = m.getObsServerParameter(obsServerAlias=server_alias,
                                                  parameter="serverWeb")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    message = "alias '%s'\tserverWeb:\t%s" % (server_alias, str(res))
                    self.printSimpleResult(message, str(res))
            else:
                return self.printHelp(__command_query__)
        return 0

    def server_set(self, listArgv):
        Help = False
        login = None
        api_url = None
        repository_url = None
        weburl = None
        server_alias = None

        while self.testArgv(listArgv):
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
                    return self.printServerCompletionList()
            else:
                return self.printUnknownCommand(currentCommand, __command_set__)

        if Help == True:
            return self.printHelp(__command_set__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                server_alias = self.testServerAlias(server_alias)
                if server_alias == None:
                    return 1
                if login != None:
                    res = m.setObsServerParameter(obsServerAlias=server_alias,
                                                  parameter="user", value=login)
                    if self.testResult(res, getLineno()) == -1:return - 1
                if api_url != None:
                    res = m.setObsServerParameter(obsServerAlias=server_alias,
                                                  parameter="serverAPI", value=api_url)
                    if self.testResult(res, getLineno()) == -1:return - 1
                if repository_url != None:
                    res = m.setObsServerParameter(obsServerAlias=server_alias,
                                                  parameter="serverRepo", value=repository_url)
                    if self.testResult(res, getLineno()) == -1:return - 1
                if weburl != None:
                    res = m.setObsServerParameter(obsServerAlias=server_alias,
                                                  parameter="serverWeb", value=weburl)
                    if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.printHelp(__command_set__)

    def server_add(self, listArgv):
        Help = False
        server_alias = None
        login = None
        password = None
        api_url = None
        repository_url = None
        weburl = None

        while self.testArgv(listArgv):
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
            return self.printHelp(__command_add__)
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
                return self.printHelp(__command_add__)

    def server_del(self, listArgv):
        Help = False
        server_alias = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)

            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                server_alias = currentCommand
                break

        if  Help or (server_alias == None):
            return self.printHelp(__command_del__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                return m.delObsServer(obsServer=server_alias)
            else:
                return self.printHelp(__command_del__)

    def server_current(self, listArgv):
        '''
        Return the current OBS help
        '''
        Help = False

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                return self.printUnknownCommand(currentCommand, __command_current__)

        if  Help :
            return self.printHelp(__command_current__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                res = m.getCurrentObsServer()
                print res
                return 0
            else:
                return self.printHelp(__command_current__)

class ObsLightObsproject(ObsLightBase):
    '''
    manage OBSlight server
    '''
    def __init__(self):
        '''
        init class
        '''
        ObsLightBase.__init__(self)

        self.currentCommand = __obsproject_command__[0]

        self.commandList = __obsproject_subcommand_list__
        self.parameterCompletionDict = __obsproject_parameter_completion_dict__
        self.commandHelpDict = __obsproject_command_help_dict__
        self.parameterDict = __obsproject_parameter_dict__


    def obsproject_create(self, listArgv):
        Help = False
        server_alias = None
        name_on_obs = None
        title = ""
        description = ""

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)

            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_server_alias__:
                server_alias , listArgv = self.getParameter(listArgv)
                if (server_alias == None) and ObsLightBase.noaction:
                    return self.printServerCompletionList()
            elif currentCommand in __parameter_name_on_obs__:
                name_on_obs , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_project_title__:
                title , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_project_description__:
                description , listArgv = self.getParameter(listArgv)
            else:
                return self.printUnknownCommand(currentCommand, __command_create__)

        if Help == True:
            return self.printHelp(__command_create__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if (server_alias != None) and (name_on_obs != None):
                    return m.createObsProject(server_alias, name_on_obs, title, description)
                else:
                    return self.printHelp()

            else:
                return self.printHelp(__command_create__)

    def obsproject_list (self, listArgv):
        Help = False
        server_alias = None
        arch = None
        maintainer = False
        bugowner = False
        remoteurl = False

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)

            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_server_alias__:
                server_alias , listArgv = self.getParameter(listArgv)
                if (server_alias == None) and ObsLightBase.noaction:
                    return self.printServerCompletionList()
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
            return self.printHelp(__command_list__)
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
                                                    arch=arch)
                    if self.testResult(res, getLineno()) == -1:return - 1
                else:
                    return self.printHelp()
                self.printResultList(res)
                return 0
            else:
                return self.printHelp(__command_list__)

    def obsproject_current(self, listArgv):
        Help = False

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                return self.printUnknownCommand(currentCommand, __command_current__)

        if  Help :
            return self.printHelp(__command_current__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                res = m.getCurrentObsProject()
                print res
                return 0
            else:
                return self.printHelp(__command_current__)

    def obsproject_add(self, listArgv):
        Help = False
        project_alias = None
        name_on_obs = None
        target = None
        arch = None
        server_alias = None

        while self.testArgv(listArgv):
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
            return self.printHelp(__command_add__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if server_alias == None:
                    server_alias = m.getCurrentObsServer()
                    if server_alias == None:
                        return self.printHelp(__command_add__)

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
                return self.printHelp(__command_add__)

    def obsproject_del(self, listArgv):
        Help = False
        project = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)

            if (currentCommand in __command_help__):
                Help = True
                break
            else:
                project = currentCommand
                break

        if  Help :
            return self.printHelp(__command_del__)
        else:
            if not ObsLightBase.noaction:
                if project == None:
                    return self.printError("Missing project", __command_del__)
                m = ObsLightManager.getCommandLineManager()
                res = m.removeProject(projectLocalName=project)
                if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.printHelp(__command_del__)

    def obsproject_query(self, listArgv):
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
        readonly = False

        server_alias = None
        obsproject = None

        while self.testArgv(listArgv):
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
            elif currentCommand in __parameter_readonly__:
                readonly = True
            elif currentCommand in __parameter_project_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()
            elif currentCommand in __parameter_server_alias__:
                server_alias , listArgv = self.getParameter(listArgv)
                if (server_alias == None) and ObsLightBase.noaction:
                    return self.printServerCompletionList()
            elif currentCommand in __parameter_project__:
                obsproject , listArgv = self.getParameter(listArgv)
                if (server_alias != None) and (obsproject == None) and ObsLightBase.noaction:
                    return self.printServerObsProjectCompletionList(server_alias)
            else:
                return self.printUnknownCommand(currentCommand, __command_query__)

        if  Help :
            return self.printHelp(__command_query__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) and ((server_alias == None) or (obsproject == None)):
                    if project_alias == None:
                        project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp(__command_query__)

                if  (not title) and \
                    (not description) and \
                    (not server) and \
                    (not webpage) and \
                    (not repository) and \
                    (not target) and \
                    (not architecture)and \
                    (not remoteurl) and \
                    (not maintainer) and \
                    (not architecture) and \
                    (not readonly):

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
                    readonly = True

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
                        self.printResultList(res, comment="target: ")
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
                        self.printResultList(res, comment="architecture: ")
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
                    self.printResultList(res, comment="maintainer: ")
                if readonly  and (server_alias != None) and (obsproject != None) :
                    res = m.getObsProjectParameter(serverApi=server_alias,
                                                obsproject=obsproject,
                                                parameter="readonly")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("readonly: " + str(res), str(res))
                if bugowner  and (server_alias != None) and (obsproject != None) :
                    res = m.getObsProjectParameter(serverApi=server_alias,
                                                obsproject=obsproject,
                                                parameter="bugowner")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printResultList(res, comment="bugowner: ")
                return 0
            else:
                return self.printHelp(__command_query__)

    def obsproject_set(self, listArgv):
        Help = False
        title = None
        description = None
        project_alias = None

        while self.testArgv(listArgv):
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
                    return self.printProjectCompletionList()
            else:
                return self.printUnknownCommand(currentCommand, __command_set__)

        if  Help :
            return self.printHelp(__command_set__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp(__command_set__)

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
                return self.printHelp(__command_set__)

#    def obsproject_import(self, listArgv):
#        Help = False
#        path = None
#
#        while self.testArgv(listArgv):
#            currentCommand, listArgv = self.getParameter(listArgv)
#            if (currentCommand in __command_help__) or (listArgv == None):
#                Help = True
#                break
#            else:
#                path = currentCommand
#                break
#
#        if  Help :
#            return self.printHelp(__command_import__)
#        else:
#            if not ObsLightBase.noaction:
#                if (path == None):
#                    return self.printError("Missing  path", __command_import__)
#                m = ObsLightManager.getCommandLineManager()
#
#                res = m.importProject(path)
#
#                if self.testResult(res, getLineno()) == -1:return - 1
#                return 0
#            else:
#                return self.printHelp(__command_import__)


#    def obsproject_export(self, listArgv):
#        Help = False
#        path = None
#        project_alias = None
#
#        while self.testArgv(listArgv):
#            currentCommand, listArgv = self.getParameter(listArgv)
#            if (currentCommand in __command_help__) or (listArgv == None):
#                Help = True
#                break
#            else:
#                path = currentCommand
#                project_alias, listArgv = self.getParameter(listArgv)
#                break
#
#        if  Help:
#            return self.printHelp(__command_export__)
#        else:
#            if not ObsLightBase.noaction:
#                if (path == None):
#                    return self.printError("Missing  path", __command_export__)
#
#                m = ObsLightManager.getCommandLineManager()
#
#                if project_alias == None:
#                    project_alias = m.getCurrentObsProject()
#                    if project_alias == None:
#                        return self.printHelp()
#
#                res = m.exportProject(project_alias, path)
#
#                if self.testResult(res, getLineno()) == -1:return - 1
#                return 0
#            else:
#                return self.printHelp(__command_export__)

    def obsproject_dependencyrepositories(self, listArgv):
        Help = False
        project_alias = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                project_alias = currentCommand
                break

        if  Help:
            return self.printHelp(__command_dependencyrepositories__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp()

                res = m.getDependencyRepositories(project_alias)

                if self.testResult(res, getLineno()) == -1:return - 1
                for repo in res.keys():
                    message = "Repository alias: %s\tURL: %s" % (str(repo), res[repo])
                    self.printSimpleResult(message, str(repo) + " , " + res[repo])
                return 0
            else:
                return self.printHelp(__command_dependencyrepositories__)

    def obsproject_testBuildPackages(self, listArgv):
        Help = False
        project_alias = None
        listPackage = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)

            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()
            elif currentCommand in __parameter_package__:
                listPackage = listArgv
                break
            else:
                return self.printUnknownCommand(currentCommand, __command_testBuildPackages__)

        if  Help:
            return self.printHelp(__command_testBuildPackages__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp()

                res = m.testBuildPackages(project_alias, listPackage)

                if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.printHelp(__command_testBuildPackages__)

    def execute(self, listArgv):
        '''
        Execute a list of arguments.
        '''
        if len(listArgv) == 0:
            self.printHelp()
            return 0
        else:
            currentCommand, listArgv = self.getParameter(listArgv)

            if currentCommand in __command_help__ :
                return self.printHelp()
            elif currentCommand in __command_create__:
                return self.obsproject_create(listArgv)
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
#            elif currentCommand in  __command_import__ :
#                return self.obsproject_import(listArgv)
#            elif currentCommand in __command_export__ :
#                return self.obsproject_export(listArgv)
            elif currentCommand in __command_dependencyrepositories__:
                return self.obsproject_dependencyrepositories(listArgv)
            elif currentCommand in __command_testBuildPackages__:
                return self.obsproject_testBuildPackages(listArgv)
            else:
                return self.printHelp()

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

        self.currentCommand = __package_command__[0]

        self.commandList = __package_subcommand_list__
        self.parameterCompletionDict = __package_parameter_completion_dict__
        self.commandHelpDict = __package_command_help_dict__
        self.parameterDict = __package_parameter_dict__


    def package_create(self, listArgv):
        Help = False
        server_alias = None
        name_on_obs = None
        package = None
        title = ""
        description = ""

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)

            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_server_alias__:
                server_alias , listArgv = self.getParameter(listArgv)
                if (server_alias == None) and ObsLightBase.noaction:
                    return self.printServerCompletionList()
            elif currentCommand in __parameter_name_on_obs__:
                name_on_obs , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_package__:
                package , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_project_title__:
                title , listArgv = self.getParameter(listArgv)
            elif currentCommand in __parameter_project_description__:
                description , listArgv = self.getParameter(listArgv)
            else:
                return self.printUnknownCommand(currentCommand, __command_create__)

        if Help == True:
            return self.printHelp(__command_create__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if (server_alias != None) and (name_on_obs != None) and (package != None):
                    return m.createObsPackage(server_alias, name_on_obs, package, title, description)
                else:
                    return self.printHelp()

            else:
                return self.printHelp(__command_create__)



    def package_import(self, listArgv):
        Help = False
        package = None
        url = None
        project_alias = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()
            elif currentCommand in __parameter_gitUrl__:
                url, listArgv = self.getParameter(listArgv)
                if (url == None) and ObsLightBase.noaction:
                    return self.printHelp(__command_import__)
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and ObsLightBase.noaction:
                    return self.printHelp(__command_import__)
            else:
                return self.printUnknownCommand(currentCommand, __command_import__)

        if  Help  :
            return self.printHelp(__command_import__)
        else:
            if not ObsLightBase.noaction:
                if (package == None):
                    return self.printError("Missing  package", __command_import__)

                m = ObsLightManager.getCommandLineManager()

                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp(__command_import__)

                return m.importPackage(project_alias,
                                       package,
                                       url)
            else:
                return self.printHelp(__command_import__)


    def package_add(self, listArgv):
        Help = False
        package = None
        project_alias = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printPackageCompletionList(project_alias, onlyInstalled=False)
            else:
                return self.printUnknownCommand(currentCommand, __command_add__)

        if  Help  :
            return self.printHelp(__command_add__)
        else:
            if not ObsLightBase.noaction:
                if (package == None):
                    return self.printError("Missing  package", __command_add__)

                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp()

                return m.addPackage(projectLocalName=project_alias,
                                    package=package)
            else:
                return self.printHelp(__command_add__)

    def package_delete(self, listArgv):
        Help = False
        package = None
        project_alias = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) :
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printPackageCompletionList(project_alias)
            else:
                self.printUnknownCommand(currentCommand, __command_del__)

        if  Help or (package == None) :
            return self.printHelp(__command_del__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp(__command_del__)

                return m.removePackage(projectLocalName=project_alias,
                                       package=package)
            else:
                return self.printHelp(__command_del__)



    def package_list(self, listArgv):
        Help = False
        available = False
        project_alias = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_available__:
                available = True
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()
            else:
                return self.printUnknownCommand(currentCommand, __command_list__)

        if  Help :
            return self.printHelp(__command_list__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp(__command_list__)

                if available:
                    res = m.getLocalProjectPackageList(projectLocalName=project_alias, onlyInstalled=False)
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printResultList(res)
                else:
                    res = m.getLocalProjectPackageList(projectLocalName=project_alias, onlyInstalled=True)
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printResultList(res)
            else:
                return self.printHelp(__command_list__)
        return 0



    def package_query(self, listArgv):
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
        packageChrootDirectory = False
        packageSourceDirectory = False
        patch_mode = False

        chRootStatus = False
        currentPatch = False

        project_alias = None
        server_alias = None
        obsproject = None
        package = None


        while self.testArgv(listArgv):
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
            elif currentCommand in __parameter_filelist__:
                listFile = True
            elif currentCommand in __parameter_filelist_status__:
                listFile_status = True
            elif currentCommand in __parameter_obsstatus__:
                obsStatus = True
            elif currentCommand in __parameter_oscstatus__:
                oscStatus = True
            elif currentCommand in __parameter_specFile__:
                specFile = True
            elif currentCommand in __parameter_packageChrootDirectory__ :
                packageChrootDirectory = True
            elif currentCommand in __parameter_packageSourceDirectory__ :
                packageSourceDirectory = True
            elif currentCommand in __parameter_filesystemstatus__:
                chRootStatus = True
            elif currentCommand in __parameter_currentPatch__:
                currentPatch = True
            elif currentCommand in __parameter_patch_mode__:
                patch_mode = True
            elif currentCommand in __parameter_url__:
                url = True
            elif currentCommand in __parameter_project_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()
            elif currentCommand in __parameter_server_alias__:
                server_alias , listArgv = self.getParameter(listArgv)
                if (server_alias == None) and ObsLightBase.noaction:
                    return self.printServerCompletionList()
            elif currentCommand in __parameter_project__:
                obsproject , listArgv = self.getParameter(listArgv)
                if (server_alias != None) and (obsproject == None) and ObsLightBase.noaction:
                    return self.printServerObsProjectCompletionList(server_alias)
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printPackageCompletionList(project_alias)
            else:
                return self.printUnknownCommand(currentCommand, __command_query__)

        if  Help :
            return self.printHelp(__command_query__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if (package == None) and (project_alias != None):
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.printHelp(__command_query__)

                if (project_alias == None) and ((server_alias == None) or (obsproject == None)):
                    return self.printHelp(__command_query__)

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
                   (not packageChrootDirectory)and \
                   (not packageSourceDirectory)and \
                   (not chRootStatus)and \
                   (not currentPatch)and \
                   (not patch_mode):

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
                    packageChrootDirectory = True
                    packageSourceDirectory = True
                    chRootStatus = True
                    currentPatch = True
                    patch_mode = True

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
                    self.printResultList(res, comment="listFile: ", row=True)

                if listFile_status and (project_alias != None):
                    if (project_alias != None):
                        res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="listFile")

                        res2 = []
                        for aFile in res:
                            status = m.getPackageFileInfo(projectLocalName=project_alias,
                                                        package=package,
                                                        fileName=aFile)
                            fileResult = aFile + "\t" + status['Status']
                            res2.append(fileResult)

                        if self.testResult(res, getLineno()) == -1:return - 1
                        self.printResultList(res2, comment="File list with status: ", row=True)

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

                if packageChrootDirectory and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                    package=package,
                                                    parameter="packageChrootDirectory")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("packageChrootDirectory: " + res, str(res))

                if packageSourceDirectory and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                package=package,
                                                parameter="packageSourceDirectory")

                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("packageSourceDirectory: " + res, str(res))

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

                if patch_mode and (project_alias != None):
                    res = m.getPackageParameter(projectLocalName=project_alias,
                                                package=package,
                                                parameter="patchMode")
                    if self.testResult(res, getLineno()) == -1:return - 1
                    self.printSimpleResult("patchMode: " + res, str(res))
            else:
                return self.printHelp(__command_query__)

    def package_set(self, listArgv):
        Help = False

        title = None
        description = None

        project_alias = None
        package = None

        patch_mode = None

        while self.testArgv(listArgv):
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
                    return self.printProjectCompletionList()

            elif patch_mode in __parameter_patch_mode__:
                patch_mode , listArgv = self.getParameter(listArgv)
                if (patch_mode == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()

            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printPackageCompletionList(project_alias)
            else:
                return self.printUnknownCommand(currentCommand, __command_set__)

        if  Help :
            return self.printHelp(__command_set__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp(__command_set__)

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.printHelp(__command_set__)

                if title != None :
                    res = m.setPackageParameter(projectLocalName=project_alias,
                                                  package=package,
                                                  parameter="title",
                                                  value=title)
                    if self.testResult(res, getLineno()) == -1:return - 1

                if patch_mode != None :
                    res = m.setPackageParameter(projectLocalName=project_alias,
                                                package=package,
                                                parameter="patchMode",
                                                value=patch_mode)
                    if self.testResult(res, getLineno()) == -1:return - 1

                if description != None :
                    res = m.setPackageParameter(projectLocalName=project_alias,
                                                  package=package,
                                                  parameter="description",
                                                  value=description)
                    if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.printHelp(__command_set__)

    def package_update(self, listArgv):
        Help = False

        project_alias = None
        package = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printPackageCompletionList(project_alias)
            else:
                return self.printUnknownCommand(currentCommand, __command_update__)

        if  Help :
            return self.printHelp(__command_update__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp(__command_update__)

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.printHelp(__command_update__)

                res = m.updatePackage(projectLocalName=project_alias,
                                     package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.printHelp(__command_update__)

    def package_commit(self, listArgv):
        Help = False

        project_alias = None
        package = None
        message = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__):
                Help = True
                break
            else:
                message = currentCommand
                while self.testArgv(listArgv):
                    currentCommand, listArgv = self.getParameter(listArgv)
                    if currentCommand in __parameter_project_alias__:
                        project_alias , listArgv = self.getParameter(listArgv)
                        if (project_alias == None) and ObsLightBase.noaction:
                            return self.printProjectCompletionList()
                    elif currentCommand in __parameter_package__:
                        package, listArgv = self.getParameter(listArgv)
                        if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                            return self.printPackageCompletionList(project_alias)
                    else:
                        return self.printUnknownCommand(currentCommand, __command_commit__)
                break

        if  Help :
            return self.printHelp(__command_commit__)
        else:
            if not ObsLightBase.noaction:
                if message == None :
                    return self.printError("Missing  message", __command_commit__)

                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp(__command_commit__)

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.printHelp(__command_commit__)

                res = m.updatePackage(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                res = m.testConflict(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                if res:
                    message = "Can't commit, package '%s' has files in conflict" % package
                    self.printErrorMessage(message)
                    return

                res = m.addAndCommitChanges(project_alias,
                                            package,
                                            message)
                if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.printHelp(__command_commit__)

    def package_repair(self, listArgv):
        Help = False

        project_alias = None
        package = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias , listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printPackageCompletionList(project_alias)
            else:
                return self.printUnknownCommand(currentCommand, __command_repair__)

        if  Help :
            return self.printHelp(__command_repair__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp(__command_repair__)

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.printHelp(__command_repair__)

                res = m.repairPackageDirectory(projectLocalName=project_alias,
                                                  package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.printHelp(__command_repair__)

    def package_current(self, listArgv):
        Help = False
        project_alias = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()
            else:
                return self.printUnknownCommand(currentCommand, __command_current__)

        if  Help :
            return self.printHelp(__command_current__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp(__command_current__)

                return m.getCurrentPackage(projectLocalName=project_alias)
            else:
                return self.printHelp(__command_current__)

#    def package_addfile(self, listArgv):
#        Help = False
#        path = None
#        project_alias = None
#        package = None
#
#        while self.testArgv(listArgv):
#            currentCommand, listArgv = self.getParameter(listArgv)
#            if (currentCommand in __command_help__) or (listArgv == None):
#                Help = True
#                break
#            else:
#                path = currentCommand
#                while(len(listArgv) > 0):
#                    currentCommand, listArgv = self.getParameter(listArgv)
#                    if currentCommand in __parameter_project_alias__:
#                        project_alias , listArgv = self.getParameter(listArgv)
#                        if (project_alias == None) and ObsLightBase.noaction:
#                            return self.printProjectCompletionList()
#                    elif currentCommand in __parameter_package__:
#                        package, listArgv = self.getParameter(listArgv)
#                        if (package == None) and (project_alias != None) and ObsLightBase.noaction:
#                            return self.printPackageCompletionList(project_alias)
#                    else:
#                        return self.printUnknownCommand(currentCommand, __command_addfile__)
#                break
#
#        if  Help :
#            return self.printHelp(__command_addfile__)
#        else:
#            if not ObsLightBase.noaction:
#                m = ObsLightManager.getCommandLineManager()
#                if project_alias == None:
#                    project_alias = m.getCurrentObsProject()
#                    if project_alias == None:
#                        return self.printHelp(__command_addfile__)
#
#                if (package == None) :
#                    package = m.getCurrentPackage(project_alias)
#                    if package == None:
#                        return self.printHelp(__command_addfile__)
#
#                return m.addFileToPackage(project_alias, package, path)
#            else:
#                return self.printHelp(__command_addfile__)

#    def package_deletefile(self, listArgv):
#        Help = False
#        name = None
#        project_alias = None
#        package = None
#
#        while self.testArgv(listArgv):
#            currentCommand, listArgv = self.getParameter(listArgv)
#            if (currentCommand in __command_help__) or (listArgv == None):
#                Help = True
#                break
#            else:
#                name = currentCommand
#                while(len(listArgv) > 0):
#                    currentCommand, listArgv = self.getParameter(listArgv)
#                    if currentCommand in __parameter_project_alias__:
#                        project_alias , listArgv = self.getParameter(listArgv)
#                        if (project_alias == None) and ObsLightBase.noaction:
#                            return self.printProjectCompletionList()
#                    elif currentCommand in __parameter_package__:
#                        package, listArgv = self.getParameter(listArgv)
#                        if (package == None) and (project_alias != None) and ObsLightBase.noaction:
#                            return self.printPackageCompletionList(project_alias)
#                    else:
#                        return self.printUnknownCommand(currentCommand, __command_deletefile__)
#                break
#
#        if  Help :
#            return self.printHelp(__command_deletefile__)
#        else:
#            if not ObsLightBase.noaction:
#                m = ObsLightManager.getCommandLineManager()
#                if project_alias == None:
#                    project_alias = m.getCurrentObsProject()
#                    if project_alias == None:
#                        return self.printHelp(__command_deletefile__)
#
#                if (package == None) :
#                    package = m.getCurrentPackage(project_alias)
#                    if package == None:
#                        return self.printHelp(__command_deletefile__)
#
#                return m.deleteFileFromPackage(project_alias, package, name)
#            else:
#                return self.printHelp(__command_deletefile__)

    def package_refresh(self, listArgv):
        Help = False
        OscStatus = False
        ObsStatus = False
        project_alias = None
        package = None

        while self.testArgv(listArgv):
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
                    return self.printProjectCompletionList()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printPackageCompletionList(project_alias)
            else:
                return self.printUnknownCommand(currentCommand, __command_refresh__)

        if  Help :
            return self.printHelp(__command_refresh__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if not (OscStatus or ObsStatus):
                    OscStatus = True
                    ObsStatus = True

                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp(__command_refresh__)

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.printHelp(__command_refresh__)
                if OscStatus:
                    res = m.refreshPackageDirectoryStatus(project_alias, package)
                    if self.testResult(res, getLineno()) == -1:return - 1
                if ObsStatus:
                    res = m.refreshObsStatus(project_alias, package)
                    if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.printHelp(__command_refresh__)

    def package_testConflict(self, listArgv):
        Help = False
        project_alias = None
        package = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printPackageCompletionList(project_alias)
            else:
                return self.printUnknownCommand(currentCommand, __command_testConflict__)

        if  Help :
            return self.printHelp(__command_testConflict__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp(__command_testConflict__)

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.printHelp(__command_testConflict__)
                res = m.updatePackage(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                res = m.testConflict(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                message = "the '%s' has a conflict: %s" % (package, str(res))
                self.printSimpleResult(message, str(res))
                return 0
            else:
                return self.printHelp(__command_testConflict__)

    def package_resolveConflict(self, listArgv):
        Help = False
        project_alias = None
        package = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printPackageCompletionList(project_alias)
            else:
                return self.printUnknownCommand(currentCommand, __command_testConflict__)

        if  Help :
            return self.printHelp(__command_resolveConflict__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp(__command_resolveConflict__)

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.printHelp(__command_resolveConflict__)

                res = m.resolveConflict(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.printHelp(__command_resolveConflict__)

    def execute(self, listArgv):
        if len(listArgv) == 0:
            self.printHelp()
            return 0
        else:
            currentCommand = listArgv[0]
            listArgv = listArgv[1:]

            if currentCommand in __command_help__ :
                return self.printHelp()
            elif currentCommand in __command_create__ :
                return self.package_create(listArgv)
            elif currentCommand in __command_import__:
                return self.package_import(listArgv)
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
#            elif currentCommand in __command_addfile__:
#                return self.package_addfile(listArgv)
#            elif currentCommand in __command_deletefile__:
#                return self.package_deletefile(listArgv)
            elif currentCommand in __command_refresh__:
                return self.package_refresh(listArgv)
            elif currentCommand in __command_testConflict__:
                return self.package_testConflict(listArgv)
            elif currentCommand in __command_resolveConflict__:
                return self.package_resolveConflict(listArgv)
            else:
                return self.printHelp()

        return 0

#class ObsLightObsRepository(ObsLightBase):
#    '''
#    manage OBSlight server
#    '''
#    def __init__(self):
#        '''
#        init class
#        '''
#        ObsLightBase.__init__(self)
#
#        self.currentCommand = __command_repositories__[0]
#
#        self.commandList = __repositories_subcommand_list__
#        self.parameterCompletionDict = __repositories_parameter_completion_dict__
#        self.commandHelpDict = __repositories_command_help_dict__
#        self.parameterDict = __repositories_parameter_dict__
#
#    def repository_add(self, listArgv):
#        Help = False
#
#        From = False
#
#        url = None
#        alias = None
#        fromProject = None
#        project_alias = None
#
#        while self.testArgv(listArgv):
#            currentCommand, listArgv = self.getParameter(listArgv)
#            if (currentCommand in __command_help__) or (listArgv == None):
#                Help = True
#            elif currentCommand in __parameter_From__:
#                From = True
#                fromProject, listArgv = self.getParameter(listArgv)
#                if (fromProject == None) and ObsLightBase.noaction:
#                    return self.printProjectCompletionList()
#                project_alias, listArgv = self.getParameter(listArgv)
#                if (project_alias == None) and ObsLightBase.noaction:
#                    return self.printProjectCompletionList()
#                break
#            else:
#                url = currentCommand
#                alias, listArgv = self.getParameter(listArgv)
#                if (alias == None) and ObsLightBase.noaction:
#                    return self.printProjectCompletionList()
#                project_alias, listArgv = self.getParameter(listArgv)
#                break
#
#        if  Help:
#            return self.printHelp(__command_add__)
#        else:
#            if not ObsLightBase.noaction:
#                m = ObsLightManager.getCommandLineManager()
#                if project_alias == None:
#                    project_alias = m.getCurrentObsProject()
#                    if project_alias == None:
#                        return self.printHelp(__command_add__)
#
#                if From :
#                    if fromProject == None:
#                        return self.printError("Missing  fromProject", __command_commit__)
#
#                    res = m.addRepo(projectLocalName=project_alias,
#                                    fromProject=fromProject,
#                                    repoUrl=None,
#                                    alias=None)
#                    if self.testResult(res, getLineno()) == -1:return - 1
#                    return res
#                else:
#                    if url == None:
#                        return self.printError("Missing  url", __command_commit__)
#                    if alias == None:
#                        return self.printError("Missing  alias", __command_commit__)
#
#                    res = m.addRepo(projectLocalName=project_alias,
#                                    fromProject=None,
#                                    repoUrl=url,
#                                    alias=alias)
#                    if self.testResult(res, getLineno()) == -1:return - 1
#                    return res
#            else:
#                return self.printHelp(__command_add__)
#
#    def repository_delete(self, listArgv):
#        Help = False
#
#        repo_alias = None
#        project_alias = None
#
#        while self.testArgv(listArgv):
#            currentCommand, listArgv = self.getParameter(listArgv)
#            if currentCommand in __command_help__:
#                Help = True
#            elif currentCommand in __parameter_repo_alias__:
#                repo_alias, listArgv = self.getParameter(listArgv)
#            elif currentCommand in __parameter_project_alias__:
#                project_alias, listArgv = self.getParameter(listArgv)
#                if (project_alias == None) and ObsLightBase.noaction:
#                    return self.printProjectCompletionList()
#            else:
#                return self.printUnknownCommand(currentCommand, __command_del__)
#
#        if  Help:
#            return self.printHelp(__command_del__)
#        else:
#            if not ObsLightBase.noaction:
#                m = ObsLightManager.getCommandLineManager()
#                if project_alias == None:
#                    project_alias = m.getCurrentObsProject()
#                    if project_alias == None:
#                        return self.printHelp(__command_del__)
#
#                if repo_alias == None:
#                    return self.printError("Missing  repo_alias", __command_del__)
#
#                res = m.deleteRepo(projectLocalName=project_alias,
#                                    repoAlias=repo_alias)
#
#                if self.testResult(res, getLineno()) == -1:return - 1
#                return res
#            else:
#                return self.printHelp(__command_del__)
#
#
#    def repository_modify(self, listArgv):
#        Help = False
#
#        repo_alias = None
#        project_alias = None
#        newUrl = None
#        newAlias = None
#        while self.testArgv(listArgv):
#            currentCommand, listArgv = self.getParameter(listArgv)
#            if currentCommand in __command_help__:
#                Help = True
#            elif currentCommand in __parameter_newUrl__:
#                newUrl, listArgv = self.getParameter(listArgv)
#            elif currentCommand in __parameter_newAlias__:
#                newAlias, listArgv = self.getParameter(listArgv)
#            elif currentCommand in __parameter_repo_alias__:
#                repo_alias, listArgv = self.getParameter(listArgv)
#            elif currentCommand in __parameter_project_alias__:
#                project_alias, listArgv = self.getParameter(listArgv)
#                if (project_alias == None) and ObsLightBase.noaction:
#                    return self.printProjectCompletionList()
#            else:
#                return self.printUnknownCommand(currentCommand, __command_modify__)
#        if  Help:
#            return self.printHelp(__command_modify__)
#        else:
#            if not ObsLightBase.noaction:
#                m = ObsLightManager.getCommandLineManager()
#                if project_alias == None:
#                    project_alias = m.getCurrentObsProject()
#                    if project_alias == None:
#                        return self.printHelp(__command_modify__)
#                if repo_alias == None:
#                    return self.printError("Missing  repo_alias ", __command_del__)
#
#                if (newUrl == None) and (newAlias == None):
#                    return self.printError("Missing  newUrl/newAlias ", __command_del__)
#
#                res = m.modifyRepo(projectLocalName=project_alias,
#                                   repoAlias=repo_alias,
#                                   newUrl=newUrl,
#                                   newAlias=newAlias)
#
#                if self.testResult(res, getLineno()) == -1:return - 1
#                return res
#            else:
#                return self.printHelp(__command_modify__)

#    def repository_query(self, listArgv):
#        Help = False
#        project_alias = None
#
#        while self.testArgv(listArgv):
#            currentCommand, listArgv = self.getParameter(listArgv)
#            if (currentCommand in __command_help__):
#                Help = True
#                break
#            elif currentCommand in __parameter_project_alias__:
#                project_alias , listArgv = self.getParameter(listArgv)
#                if (project_alias == None) and ObsLightBase.noaction:
#                    return self.printProjectCompletionList()
#            else:
#                return self.printUnknownCommand(currentCommand, __command_query__)
#
#        if  Help :
#            return self.printHelp(__command_query__)
#        else:
#            if not ObsLightBase.noaction:
#                m = ObsLightManager.getCommandLineManager()
#                if project_alias == None:
#                    project_alias = m.getCurrentObsProject()
#                    if project_alias == None:
#                        return self.printHelp(__command_query__)
#
#                res = m.getChRootRepositories(projectLocalName=project_alias)
#                if self.testResult(res, getLineno()) == -1:return - 1
#                self.printSimpleResult("repository: ", "")
#                for k in res:
#                    self.printSimpleResult("Alias: " + k + "\t\tURL: " + res[k], k + " " + res[k])
#                return 0
#            else:
#                return self.printHelp(__command_query__)

#    def execute(self, listArgv):
#        if len(listArgv) == 0:
#            return self.printHelp()
#        else:
#            currentCommand = listArgv[0]
#            listArgv = listArgv[1:]
#
#            if currentCommand in __command_help__ :
#                return self.printHelp()
#            elif currentCommand in __command_add__:
#                return self.repository_add(listArgv)
#            elif currentCommand in __command_del__ :
#                return self.repository_delete(listArgv)
#            elif currentCommand in __command_modify__:
#                return self.repository_modify(listArgv)
#            elif currentCommand in __command_query__:
#                return self.repository_query(listArgv)
#            else:
#                return self.printHelp()
#        return 0


class ObsLightObsProjectfilesystem(ObsLightBase):
    '''
    manage OBSlight server
    '''
    def __init__(self):
        '''
        init class
        '''
        ObsLightBase.__init__(self)

        self.currentCommand = __projectfilesystem_command__[0]

        self.commandList = __filesystem_subcommand_list__
        self.parameterCompletionDict = __filesystem_parameter_completion_dict__
        self.commandHelpDict = __filesystem_command_help_dict__
        self.parameterDict = __filesystem_parameter_dict__


    def man(self):
        ObsLightBase.man(self)
#        ObsLightObsRepository().man()

    def projectfilesystem_create(self, listArgv):
        Help = False
        project_alias = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                project_alias = currentCommand

        if  Help :
            return self.printHelp(__command_create__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp(__command_create__)

                res = m.createChRoot(projectLocalName=project_alias)
                if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.printHelp(__command_create__)

    def projectfilesystem_delete(self, listArgv):
        Help = False
        project_alias = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            else:
                project_alias, listArgv = self.getParameter(listArgv)

        if  Help :
            return self.printHelp(__command_del__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp()

                res = m.removeChRoot(projectLocalName=project_alias)
                if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.printHelp(__command_del__)

    def projectfilesystem_query(self, listArgv):
        Help = False
        path = False
        status = False

        project_alias = None

        while self.testArgv(listArgv):
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
                    return self.printProjectCompletionList()
            else:
                return self.printUnknownCommand(currentCommand, __command_query__)

        if  Help :
            return self.printHelp(__command_query__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp()

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
                return self.printHelp(__command_query__)

    def projectfilesystem_enter(self, listArgv):
        Help = False

        project_alias = None
        package = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
                break
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printPackageCompletionList(project_alias)
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()
            else:
                return self.printUnknownCommand(currentCommand, __command_enter__)

        if  Help :
            return self.printHelp(__command_enter__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp(__command_enter__)

                res = m.goToChRoot(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.printHelp(__command_enter__)

    def projectfilesystem_executescript(self, listArgv):
        Help = False
        aPath = None

        project_alias = None
        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()
            else:
                aPath = currentCommand

        if  Help  :
            return self.printHelp(__command_executescript__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp()
                if aPath == None:
                    return self.printError("Missing  aPath", __command_executescript__)

                res = m.execScript(projectLocalName=project_alias, aPath=aPath)
                if self.testResult(res, getLineno()) == -1:return - 1
                return res
            else:
                return self.printHelp(__command_executescript__)

    def execute(self, listArgv):
        if len(listArgv) == 0:
            return self.printHelp()
        else:
            currentCommand = listArgv[0]
            listArgv = listArgv[1:]

            if currentCommand in __command_help__ :
                return self.printHelp()
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
#            elif currentCommand in __command_repositories__:
#                return ObsLightObsRepository().execute(listArgv)
            else:
                return self.printHelp()
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

        self.currentCommand = __rpmbuild_command__[0]

        self.commandList = __rpmbuild_subcommand_list__
        self.parameterCompletionDict = __rpmbuild_parameter_completion_dict__
        self.commandHelpDict = __rpmbuild_command_help_dict__
        self.parameterDict = __rpmbuild_parameter_dict__

    def rpmbuild_prepare(self, listArgv):
        Help = False
        project_alias = None
        package = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printPackageCompletionList(project_alias)
            else :
                return self.printUnknownCommand(currentCommand, __command_prepare__)

        if  Help :
            return self.printHelp(__command_prepare__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp(__command_prepare__)

                if (package == None):
                    package = m.getCurrentPackage(project_alias)

                res = m.buildPrep(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.printHelp(__command_prepare__)

    def rpmbuild_build(self, listArgv):
        Help = False
        project_alias = None
        package = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if (currentCommand in __command_help__) or (listArgv == None):
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printPackageCompletionList(project_alias)
            else :
                return self.printUnknownCommand(currentCommand, __command_build__)

        if  Help :
            return self.printHelp(__command_build__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp(__command_build__)

                if (package == None):
                    package = m.getCurrentPackage(project_alias)

                res = m.buildRpm(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.printHelp(__command_build__)


    def rpmbuild_install(self, listArgv):
        Help = False
        project_alias = None
        package = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printPackageCompletionList(project_alias)
            else :
                return self.printUnknownCommand(currentCommand, __command_install__)

        if  Help :
            return self.printHelp(__command_install__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp()

                if (package == None):
                    package = m.getCurrentPackage(project_alias)

                res = m.installRpm(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.printHelp(__command_install__)

    def rpmbuild_package(self, listArgv):
        Help = False
        project_alias = None
        package = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printPackageCompletionList(project_alias)
            else :
                return self.printUnknownCommand(currentCommand, __command_buildpackage__)

        if  Help :
            return self.printHelp(__command_buildpackage__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()
                if project_alias == None:
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp()

                if (package == None):
                    package = m.getCurrentPackage(project_alias)

                res = m.packageRpm(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.printHelp(__command_buildpackage__)

    def rpmbuild_isInit(self, listArgv):
        Help = False
        project_alias = None
        package = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printPackageCompletionList(project_alias)
            else :
                return self.printUnknownCommand(currentCommand, __command_isInit__)

        if  Help :
            return self.printHelp(__command_isInit__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp()

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.printHelp()

                res = m.isInstalledInChRoot(project_alias, package)
                if self.testResult(res, getLineno()) == -1:
                    return -1
                if res:
                    message = "'%s' is initialized" % (package,)
                else:
                    message = "'%s' is not initialized" % (package,)
                self.printBoolResult(message, res)
                return 0
            else:
                return self.printHelp(__command_isInit__)

    def rpmbuild_createPatch(self, listArgv):
        Help = False
        project_alias = None
        package = None
        patch = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
                break
            else:
                patch = currentCommand
                while self.testArgv(listArgv):
                    currentCommand, listArgv = self.getParameter(listArgv)
                    if currentCommand in __parameter_project_alias__:
                        project_alias, listArgv = self.getParameter(listArgv)
                        if (project_alias == None) and ObsLightBase.noaction:
                            return self.printProjectCompletionList()
                    elif currentCommand in __parameter_package__:
                        package, listArgv = self.getParameter(listArgv)
                        if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                            return self.printPackageCompletionList(project_alias)
                    else:
                        return self.printUnknownCommand(currentCommand, __command_createPatch__)
                break

        if  Help :
            return self.printHelp(__command_createPatch__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp(__command_createPatch__)

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.printHelp(__command_createPatch__)

                if (patch == None) :
                    return self.printError("Missing  <patch>", __command_createPatch__)

                res = m.createPatch(projectLocalName=project_alias, package=package, patch=patch)
                if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.printHelp(__command_createPatch__)

    def rpmbuild_updatepatch(self, listArgv):
        Help = False
        project_alias = None
        package = None

        while self.testArgv(listArgv):
            currentCommand, listArgv = self.getParameter(listArgv)
            if currentCommand in __command_help__:
                Help = True
                break
            elif currentCommand in __parameter_project_alias__:
                project_alias, listArgv = self.getParameter(listArgv)
                if (project_alias == None) and ObsLightBase.noaction:
                    return self.printProjectCompletionList()
            elif currentCommand in __parameter_package__:
                package, listArgv = self.getParameter(listArgv)
                if (package == None) and (project_alias != None) and ObsLightBase.noaction:
                    return self.printPackageCompletionList(project_alias)
            else:
                return self.printUnknownCommand(currentCommand, __command_updatepatch__)

        if  Help :
            return self.printHelp(__command_updatepatch__)
        else:
            if not ObsLightBase.noaction:
                m = ObsLightManager.getCommandLineManager()

                if (project_alias == None) :
                    project_alias = m.getCurrentObsProject()
                    if project_alias == None:
                        return self.printHelp()

                if (package == None) :
                    package = m.getCurrentPackage(project_alias)
                    if package == None:
                        return self.printHelp()

                res = m.updatePatch(projectLocalName=project_alias, package=package)
                if self.testResult(res, getLineno()) == -1:return - 1
                return 0
            else:
                return self.printHelp(__command_updatepatch__)

    def execute(self, listArgv):
        '''
        Execute a list of arguments.
        '''
        if len(listArgv) == 0:
            return self.printHelp()
        else:
            currentCommand = listArgv[0]
            listArgv = listArgv[1:]

            if currentCommand in __command_help__ :
                return self.printHelp()
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
                return self.printHelp()
        return 0

class ObsLight(ObsLightBase):
    '''
    manage OBSlight
    '''
    def __init__(self):
        ObsLightBase.__init__(self)

        self.commandList = __global_command_list__


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
                if currentCommand in __server_command__ :
                    return ObsLightServer().execute(listArgv)
                elif currentCommand in __obsproject_command__ :
                    return ObsLightObsproject().execute(listArgv)
                elif currentCommand in __package_command__ :
                    return ObsLightObsPackage().execute(listArgv)
                elif currentCommand in __projectfilesystem_command__ :
                    return ObsLightObsProjectfilesystem().execute(listArgv)
                elif currentCommand in __rpmbuild_command__ :
                    return ObsLightRpmbuild().execute(listArgv)
#                elif currentCommand in __micproject__ :
#                    return self.micproject(listArgv)
                elif currentCommand in __man_command__ :
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
        print "micproject #feature", listArgv
        return 0

    def qemuproject(self, listArgv):
        print "qemuproject #feature", listArgv
        return 0
