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
Created on 3 oct. 2011

@author: ronan@fridu.net
'''

import os
import sys
from xml.etree import ElementTree
import urlparse
import urllib

from M2Crypto import m2, SSL
import httplib

from M2Crypto.SSL.Checker import SSLVerificationError

try:
    from ObsLight import ObsLightTools
except:
    pass
from osc import conf
from osc import core
from osc import oscerr

import ObsLightSubprocess
import ObsLightPrintManager
EMPTYPROJECTPATH = os.path.join(os.path.dirname(__file__), "emptySpec")

import ObsLightConfig

import ObsLightErr

import urllib2
import M2Crypto

import socket
TIMEOUT = ObsLightConfig.getSocketDefaultTimeOut()
if TIMEOUT >= 0:
    socket.setdefaulttimeout(TIMEOUT)
else:
    TIMEOUT = 60

HTTPBUFFER = ObsLightConfig.getHttpBuffer()

import threading

class ObsLightOsc(object):
    '''
    ObsLightOsc interact with osc, when possible, do it directly by python API
    '''

    WorkingCopyInconsistentMessage = ("The following working copy is inconsistent:\n\n%s\n\n" +
                                      "Maybe last update failed. " +
                                      "This often happens when there are many files in package." +
                                      " Try repairing or updating the package directory until " +
                                      "it is OK.")

    def __init__(self):
        '''
        init 
        '''
        self.__confFile = os.path.join(os.environ['HOME'], ".oscrc")
        self.__mySubprocessCrt = ObsLightSubprocess.SubprocessCrt()

        self.__aLock = threading.Lock()

        self.__httpBuffer = {}

        if os.path.isfile(self.__confFile):
            self.get_config()

    def get_config(self):
        self.__aLock.acquire()
        try:
            conf.get_config()
        finally:
            self.__aLock.release()

    def initConf(self,
                 api=None,
                 user=None,
                 passw=None,
                 alias=None):
        '''
        init a configuation for a API.
        '''
        if not os.path.isfile(self.__confFile):
            conf.write_initial_config(self.__confFile, {'apiurl':api,
                                                        'user' : user,
                                                        'pass' : passw })

        aOscConfigParser = conf.get_configParser(self.__confFile, force_read=True)

        if not (api in  aOscConfigParser.sections()):
            aOscConfigParser.add_section(api)

        aOscConfigParser.set(api, 'user', user)
        aOscConfigParser.set(api, 'pass', passw)

        option = aOscConfigParser.options(api)
        aliases = []
        if 'aliases' in option:
            aliasesRes = aOscConfigParser.get(api, 'aliases')
            if aliasesRes != None:
                aliases = aliasesRes.split(",")
            else:
                aliases = []

        if not alias in aliases:
            aliases.append(alias)
        aOscConfigParser.set(api, 'aliases', (",").join(aliases))

        aOscConfigParser.set('general', 'su-wrapper', "sudo")

        aFile = open(self.__confFile, 'w')
        aOscConfigParser.write(aFile, True)

        if aFile:
            aFile.close()

    def changeAPI(self, api, newApi):
        '''
        
        '''
        f = open(self.__confFile, 'r')
        txt = f.read()
        f.close()
        f = open(self.__confFile, 'w')
        f.write(txt.replace("[" + api + "]", "[" + newApi + "]"))
        f.close()

    def getUserProfil(self, api, user):
        "GET /person/<userid>"
        pass

    def changeUser(self, api, user):
        '''
        
        '''
        self.get_config()
        aOscConfigParser = conf.get_configParser(self.__confFile, force_read=True)

        aOscConfigParser.set(api, 'user', user)

        aFile = open(self.__confFile, 'w')
        aOscConfigParser.write(aFile, True)

    def changePassw(self, api, passw):
        '''
        
        '''
        self.get_config()
        aOscConfigParser = conf.get_configParser(self.__confFile, force_read=True)
        aOscConfigParser.set(api, 'pass', passw)

        aFile = open(self.__confFile, 'w')
        aOscConfigParser.write(aFile, True)

    def getServersFromOsc(self):
        '''
        
        '''
        result = {}
        if not os.path.isfile(self.__confFile):
            return result
        self.get_config()
        aOscConfigParser = conf.get_configParser(self.__confFile, force_read=True)

        for api in aOscConfigParser.sections():
            if api != 'general':
                server = {}
                option = aOscConfigParser.options(api)
                if 'aliases' in option:
                    aliases = aOscConfigParser.get(api, 'aliases')
                    if aliases != None:
                        aliases = aliases.split(",")
                    else:
                        aliases = []
                else:
                    aliases = ""
                if 'user' in option:
                    user = aOscConfigParser.get(api, 'user')
                else:
                    user = ""
                if 'passw' in option:
                    passw = aOscConfigParser.get(api, 'passw')
                else:
                    passw = ""
                server['api'] = api
                server['aliases'] = aliases
                server['user'] = user
                server['passw'] = passw
                result[api] = server
        return result

    def trustRepos(self,
                   api=None,
                   listDepProject=None):
        ObsLightPrintManager.getLogger().debug("api" + api)
        self.get_config()
        aOscConfigParser = conf.get_configParser(self.__confFile, force_read=True)

        if aOscConfigParser.has_option(api, "trusted_prj"):
            options = aOscConfigParser.get(api, "trusted_prj")
        else:
            options = ""

        res = options
        ObsLightPrintManager.getLogger().debug("To Add ?" + ("").join(listDepProject.keys()))
        ObsLightPrintManager.getLogger().debug("Current:" + ("").join(res))
        for depProject in listDepProject.keys():
            if not depProject in res.split(" "):
                res += " " + depProject

        ObsLightPrintManager.getLogger().debug("Result" + ("").join(res))
        aOscConfigParser.set(api, 'trusted_prj', res)

        aFile = open(self.__confFile, 'w')
        aOscConfigParser.write(aFile, True)
        if aFile: aFile.close()
        return


    def getPackageBuildRequires(self,
                                api,
                                projectObsName,
                                package,
                                projectTarget,
                                arch):
        """
        Get the list of BuildRequires of `package`, from the OBS server at `api`.
        The list contains packages names with version and release appended.
        """
        logger = ObsLightPrintManager.getLogger()
        self.get_config()
        buildinfoUrl = ("%(api)s/build/%(project)s/%(target)s/%(arch)s/%(package)s/_buildinfo" %
                        {"api": api,
                         "project": projectObsName,
                         "package": package,
                         "target": projectTarget,
                         "arch": arch})
        logger.debug("Getting buildrequires of %s from %s" % (package, buildinfoUrl))
        self.cleanBuffer(buildinfoUrl)
        res = self.getHttp_request(buildinfoUrl)
        if res != None:
            aElement = ElementTree.fromstring(res)
        else:
            return None
        result = []
        for package in aElement:
            if (package.tag == "error") :
                msg = package.text
                raise ObsLightErr.ObsLightOscErr(msg)
            if (package.tag == "bdep") :
                if (not "preinstall" in package.keys()) and (not "vminstall" in package.keys()):
                    version = "-"
                    if "epoch" in package.keys():
                        version += package.get("epoch") + ":"
                    version += package.get("version") + "-" + package.get("release")
                    result.append(package.get("name") + version)
        logger.debug("  %s" % str(result))
        return result


    def getDepProject(self,
                      apiurl=None,
                      projet=None,
                      repos=None):
        self.get_config()
        url = str(apiurl + "/source/" + projet + "/_meta")
        res = self.getHttp_request(url)
        if res == None:
            return None
        aElement = ElementTree.fromstring(res)

        result = {}
        for project in aElement:
            if (project.tag == "repository") and (project.get("name") == repos):
                for path in project.getiterator():
                    if path.tag == "path":
                        result[path.get("project")] = path.get("repository")
        return result

    def getListPackage(self,
                       apiurl=None,
                       projectLocalName=None):
        """
        Get the package list of project `projectLocalName` from `apiurl`.
        """
        url = str(apiurl + "/source/" + projectLocalName)

        res = self.getHttp_request(url)
        if res is None:
            message = "Failed to retrieve package list from server."
            raise ObsLightErr.ObsLightOscErr(message)

        aElement = ElementTree.fromstring(res)

        aList = []
        for path in aElement:
            if (path.tag == "entry"):
                aList.append(path.get("name"))
        return aList

    def getFilesListPackage(self,
                            apiurl=None,
                            projectObsName=None,
                            package=None):
        '''
        
        '''
        url = str(apiurl + "/source/" + projectObsName + "/" + package)
        self.cleanBuffer(url)
        res = self.getHttp_request(url)
        if res == None:
            return None

        aElement = ElementTree.fromstring(res)

        result = {}
        for path in aElement:
            if (path.tag == "entry"):
                file = {}
                file["name"] = path.get("name")
                file["md5"] = path.get("md5")
                file["size"] = path.get("size")
                file["mtime"] = path.get("mtime")
                result[file["name"]] = file
        return result

    def getObsPackageRev(self,
                         apiurl,
                         projectObsName,
                         package):
        '''
        
        '''
        url = str(apiurl + "/source/" + projectObsName + "/" + package)
        self.cleanBuffer(url)
        res = self.getHttp_request(url)
        if res == None:
            return res
        aElement = ElementTree.fromstring(res)

        #print "rev" , aElement.get("rev")
        #print "vrev" , aElement.get("vrev")
        #print "srcmd5" , aElement.get("srcmd5")

        return aElement.get("rev")

    def getOscPackageRev(self, workingdir):
        #Add a Lock
        self.__aLock.acquire()
        try:
            pk = core.Package(workingdir=workingdir)
        except oscerr.WorkingCopyInconsistent:
            raise ObsLightErr.ObsLightOscErr(self.WorkingCopyInconsistentMessage % workingdir)
        finally:
            self.__aLock.release()
        try:
            aElement = ElementTree.fromstring(pk.get_files_meta())
        except :
            return None

        #print "rev" , aElement.get("rev")
        #print "vrev" , aElement.get("vrev")
        #print "srcmd5" , aElement.get("srcmd5")
        return aElement.get("rev")


    def checkoutPackage(self,
                        obsServer=None,
                        projectObsName=None,
                        package=None,
                        directory=None):
        '''
            check out a package
        '''
        os.chdir(directory)
        command = "osc -A " + obsServer + " co " + projectObsName + " " + package
        self.__subprocess(command=command)

    def updatePackage(self, packagePath):
        '''
        
        '''
        os.chdir(packagePath)
        command = "osc up"
        return self.__subprocess(command=command)


    def __subprocess(self, command=None, waitMess=False):
        '''
        
        '''
        res = None
        count = 0
        while(res == None and count < 4):
            count += 1
            try:
                res = self.__mySubprocessCrt.execSubprocess(command=command, waitMess=waitMess)
                break
            except :
                logger = ObsLightPrintManager.getLogger()
                logger.error("__subprocess ERROR.")
        if res == None:
            return -1
        return res

    def getPackageStatus(self,
                         obsServer=None,
                         project=None,
                         package=None,
                         repo=None,
                         arch=None):
        '''
        Return the status of a package for a repo and arch
        The status can be:
        succeeded: Package has built successfully and can be used to build 
                   further packages.
        failed: The package does not build successfully.
                No packages have been created.
                Packages that depend on this package will be built using any
                previously created packages, if they exist.
        unresolvable: The build can not begin, because required packages are
                      either missing or not explicitly defined.
        broken: The sources either contain no build description (eg specfile) 
                or a source link does not work.
        blocked: This package waits for other packages to be built. 
                 These can be in the same or other projects.
        dispatching: A package is being copied to a build host.
                    This is an intermediate state before building.
        scheduled: A package has been marked for building,
                   but the build has not started yet.
        building: The package is currently being built.
        signing: The package has been built and is assigned to get signed.
        finished: The package has been built and signed, but has not yet been
                  picked up by the scheduler. This is an intermediate state 
                  prior to 'succeeded' or 'failed'.
        disabled: The package has been disabled from building in project or 
                  package metadata.
        excluded: The package build has been disabled in package build 
                  description (for example in the .spec file) or does not 
                  provide a matching build description for the target.
        unknown: The scheduler has not yet evaluated this package. Should be a 
                 short intermediate state for new packages.
        '''
        url = str(obsServer + "/build/" + project + "/" + repo + "/" + arch + "/" + package + "/_status")
        self.cleanBuffer(url)
        res = self.getHttp_request(url)
        if res == None:
            return None
        aElement = ElementTree.fromstring(res)

        return aElement.attrib["code"]

    def getDependencyProject(self, apiurl, projet, target):
        self.get_config()
        url = str(apiurl + "/source/" + projet + "/_meta")
        res = self.getHttp_request(url)
        if res == None:
            return None
        aElement = ElementTree.fromstring(res)

        result = {}
        for project in aElement:
            if (project.tag == "repository") and (project.get("name") == target):
                for path in project.getiterator():
                    if path.tag == "path":
                        repo = path.get("repository")
                        target = path.get("project")
                        result[target] = repo
        return result

    def getDODUrl(self, apiurl, projet, arch):
        result = []
        self.get_config()
        url = str(apiurl + "/source/" + projet + "/_meta")
        res = self.getHttp_request(url)
        if res == None:
            return None
        aElement = ElementTree.fromstring(res)

        for project in aElement:
            if (project.tag == "download") :
                if arch == project.get("arch"):
                    result.append(project.get("baseurl"))

        return result

    def getAliasOfRepo(self, repo):
        """
        
        """
        if not repo.endswith(".repo"):
            filehandle = urllib.urlopen(repo)
            aFile = filehandle.read()
            filehandle.close()
            for line in aFile.split("\n"):
                if ".repo" in line:
                    if '<a href="./' in line:
                        line = line.split('<a href="./')[1]
                        if '">' in line:
                            line = line.split('">')[0]
                            if line.endswith(".repo"):
                                repo += line

        if ObsLightTools.testUrl(repo):
            filehandle = urllib.urlopen(repo)
            aFile = filehandle.read()
            filehandle.close()
            lines = aFile.split('\n')
            for line in lines:
                if line.startswith("name="):
                    res = line.split("=")[1]
                    return res
            return None
        else:
            return None


    def createChRoot(self,
                     chrootDir,
                     repos,
                     arch,
                     apiurl,
                     project,
                     listExtraPkgs=["vim",
                                    "git",
                                    "zypper",
                                    "gzip",
                                    "strace",
                                    "iputils",
                                    "ncurses-devel",
                                    "rpm",
                                    "sed"
                                    ],
                     ):
        '''
        create a chroot
        '''
        os.chdir(EMPTYPROJECTPATH)

        extraPkgs = ""
        for pkg in listExtraPkgs:
            extraPkgs += "-x " + pkg + " "

        command = "osc -A " + apiurl + " build --root=" + chrootDir + " " + extraPkgs
        command += " --noservice --no-verify --alternative-project " + project + " "
        command += repos + " " + arch + " --local-package emptySpec.spec"
        return self.__subprocess(command=command, waitMess=True)


    def getLocalProjectList(self, obsServer):
        '''
        return a list of the project of a OBS Server.
        '''

        self.get_config()
        url = str(obsServer + "/source")
        xmlRes = self.getHttp_request(url)
        if xmlRes == None:
            raise ObsLightErr.ObsLightOscErr("The request on '" + url + "' return None.")

        aElement = ElementTree.fromstring(xmlRes)
        res = []
        for project in aElement:
            aName = project.get("name")
            res.append(aName)
        res.sort()
        return res

    def getLocalProjectListFilter(self,
                                  obsServer,
                                  maintainer=False,
                                  bugowner=False,
                                  arch=None,
                                  remoteurl=False):
        '''
        return a list of the project of a OBS Server.
        '''

        self.get_config()
        url = str(obsServer + "/search/project")
        xmlRes = self.getHttp_request(url)
        if xmlRes == None:
            raise ObsLightErr.ObsLightOscErr("The request on '" + url + "' return None.")

        aElement = ElementTree.fromstring(xmlRes)
        res = []
        for project in aElement:
            aName = project.get("name")
            aMaintainer = []
            aBugowner = []
            aArch = []
            aRemoteurl = None
            for val in project:
                if val.tag == "remoteurl":
                    aRemoteurl = val.text

                if val.tag == "repository":
                    for repo in val:
                        if repo.tag == "arch":
                            aArch.append(repo.text)
                if val.tag == "person":
                    if val.get("role") == "maintainer":
                        aMaintainer.append(val.get("userid"))
                    if val.get("role") == "bugowner":
                        aBugowner.append(val.get("userid"))
            # FIXME: this is completely unreadable
            if (((maintainer != None and (maintainer in aMaintainer)) or (maintainer == None)) and
               ((bugowner != None and (bugowner in aBugowner)) or (bugowner == None)) and
               ((arch != None and (arch in aArch)) or (arch == None)) and
               ((remoteurl != None and ((remoteurl == True and aRemoteurl != None) or
                                        (remoteurl == False and aRemoteurl == None))) or
                                        (remoteurl == None))):
                res.append(aName)
        res.sort()
        return res


    def getListRepos(self, apiurl):
        '''
        return the list of the repos of a OBS Server.
        '''
        url = str(apiurl + "/distributions")
        res = self.getHttp_request(url)
        if res == None:
            return None
        aElement = ElementTree.fromstring(res)
        result = []
        for repos in aElement:
            name = ""
            project = ""
            reponame = ""
            repository = ""
            for distri in repos:
                if distri.tag == "name":
                    name = distri.text
                elif distri.tag == "project":
                    project = distri.text
                elif distri.tag == "reponame":
                    reponame = distri.text
                elif distri.tag == "repository":
                    repository = distri.text
            result.append([name, project, reponame, repository])
        return result

    def __cleanUrl(self, url):
        '''
        
        '''
        res = urlparse.urlparse(url)

        return urlparse.urlunsplit((res[0], res[1], res[2].replace("//", "/"), '', ''))


    def getTargetList(self,
                      obsServer=None,
                      projectObsName=None):
        '''
        return the list of Target of a projectObsProject for a OBS server.
        '''
        url = str(obsServer + "/build/" + projectObsName)
        res = self.getHttp_request(url)
        if res == None:
            return None
        aElement = ElementTree.fromstring(res)
        res = []
        for directory in aElement:
            for entry in directory.getiterator():
                res.append(entry.get("name"))
        return res

    def getArchitectureList(self,
                            obsServer=None,
                            projectObsName=None,
                            projectTarget=None):
        '''
        return the list of Archictecture of the target of the projectObsName for a OBS server.
        '''

        url = str(obsServer + "/build/" + projectObsName + "/" + projectTarget)
        res = self.getHttp_request(url)
        if res == None:
            return None
        aElement = ElementTree.fromstring(res)
        result = []
        for directory in aElement:
            for entry in directory.getiterator():
                result.append(entry.get("name"))

        return result

    def commitProject(self,
                      path=None,
                      message=None,
                      skip_validation=True):
        '''
        commit a project to the OBS server.
        '''
        os.chdir(path)
        command = "osc ci -m \"" + message + "\" "

        if skip_validation:
            command += "--skip-validation"
        self.__subprocess(command=command)

    def addremove(self, path=None):
        '''
        Adds new files, removes disappeared files
        '''
        os.chdir(path)
        command = "osc ar"
        self.__subprocess(command=command)

    def remove(self, path, afile):
        '''
        Mark files or package directories to be deleted upon
        '''
        os.chdir(path)
        command = "osc del " + afile
        self.__subprocess(command=command)

    def add(self, path, afile):
        '''
        Mark files to be added upon the next commit
        '''
        os.chdir(path)
        command = "osc add " + afile
        self.__subprocess(command=command)

    def getProjectParameter(self, projectObsName, apiurl, parameter):
        '''
        Return the value of the projectObsName.
        valid parameter:
        title
        description
        
        '''
        title = None
        description = None
        remoteurl = ""
        maintainer = []
        bugowner = []
        arch = []
        repository = []

        self.get_config()
        url = str(apiurl + "/source/" + projectObsName + "/_meta")
        res = self.getHttp_request(url)
        if res == None:
            return None
        aElement = ElementTree.fromstring(res)

        for desc in aElement:
            if "title" == desc.tag:
                title = desc.text
            elif "description" == desc.tag:
                description = desc.text
            elif "person" == desc.tag:
                role = desc.get("role")
                if role == "maintainer":
                    maintainer.append(desc.get("userid"))
                elif role == "bugowner":
                    bugowner.append(desc.get("userid"))
            elif "repository" == desc.tag:
                repository.append(desc.get("name"))
                for repositoryPara in desc:
                    if "arch" == repositoryPara.tag:
                        arch.append(repositoryPara.text)
            elif "remoteurl" == desc.tag:
                remoteurl = desc.text

        if parameter == "title":
            return title
        elif parameter == "description":
            return description
        elif parameter == "remoteurl":
            return remoteurl
        elif parameter == "maintainer":
            return maintainer
        elif parameter == "bugowner":
            return bugowner
        elif parameter == "arch":
            return arch
        elif parameter == "repository" :
            return repository
        else:
            return None

    def getPackageParameter(self, projectObsName, package, apiurl, parameter):
        '''
        Return the value of the projectObsName.
        valid parameter:
        title
        description
        url
        '''
        listFile = []

        self.get_config()
        aUrl = str(apiurl + "/source/" + projectObsName + "/" + package)
        res = self.getHttp_request(aUrl)
        if res == None:
            return None
        aElement = ElementTree.fromstring(res)

        for desc in aElement:
            if "entry" == desc.tag:
                listFile.append(desc.get("name"))
        if parameter == "listFile":
            return listFile
        else:
            return None

    def getPackageMetaParameter(self, projectObsName, package, apiurl, parameter):
        '''
        Return the value of the projectObsName.
        valid parameter:
        title
        description
        url
        '''
        title = None
        description = None
        url = ""

        self.get_config()
        aUrl = str(apiurl + "/source/" + projectObsName + "/" + package + "/_meta")
        res = self.getHttp_request(aUrl)
        if res == None:
            return None
        aElement = ElementTree.fromstring(res)

        for desc in aElement:
            if "title" == desc.tag:
                title = desc.text
            elif "description" == desc.tag:
                description = desc.text
            elif "url" == desc.tag:
                role = desc.text

        if parameter == "title":
            return title
        elif parameter == "description":
            return description
        elif parameter == "url":
            return url
        else:
            return None

    def setProjectParameter(self, projectObsName, apiurl, parameter, value):
        '''
        Set the value of the projectObsName.
        valid parameter:
        title
        description
        '''
        self.get_config()
        url = str(apiurl + "/source/" + projectObsName + "/_meta")
        res = self.getHttp_request(url)
        if res == None:
            return None
        aElement = ElementTree.fromstring(res)

        for desc in aElement:
            if desc.tag == parameter:
                desc.text = value

        self.http_request("PUT", url, data=ElementTree.tostring(aElement), timeout=TIMEOUT)



    def setPackageParameter(self,
                            projectObsName,
                            package,
                            apiurl,
                            parameter,
                            value):
        '''
        Set the value of the package of the projectObsName.
        valid parameter:
        title
        description
        '''
        self.get_config()
        url = str(apiurl + "/source/" + projectObsName + "/" + package + "/_meta")
        res = self.getHttp_request(url)
        if res == None:
            return None
        aElement = ElementTree.fromstring(res)

        for desc in aElement:
            if desc.tag == parameter:
                desc.text = value
        try:
            self.http_request("PUT", url, data=ElementTree.tostring(aElement), timeout=TIMEOUT)
        except urllib2.URLError, e:
            ObsLightPrintManager.getLogger().error(str(e))
            ObsLightPrintManager.getLogger().error("apiurl %s is not reachable" % str(apiurl))
            return None
        except M2Crypto.SSL.SSLError, e:
            ObsLightPrintManager.getLogger().error(str(e))
            msg = "apiurl %s Connection reset by peer"
            ObsLightPrintManager.getLogger().error(msg % apiurl)
            return None
        except M2Crypto.SSL.Checker.NoCertificate:
            msg = "apiurl %s Peer did not return certificate"
            ObsLightPrintManager.getLogger().error(msg % str(apiurl))
            return None

    def createObsProject(self, apiurl, projectObsName, user, title="", description=""):
        self.get_config()
        url = str(apiurl + "/source/" + projectObsName + "/_meta")

        aElement = ElementTree.fromstring('<project name="' + projectObsName + '">\
                                                <title>' + title + '</title>\
                                                <description>' + description + '</description>\
                                                    <person role="maintainer" userid="' + user + '"/>\
                                                    <person role="bugowner" userid="' + user + '"/>\
                                            </project>')

        try:
            self.http_request("PUT", url, data=ElementTree.tostring(aElement), timeout=TIMEOUT)
            return 0
        except urllib2.URLError, e:
            ObsLightPrintManager.getLogger().error(str(e))
            ObsLightPrintManager.getLogger().error("apiurl %s is not reachable" % str(apiurl))
            return None
        except M2Crypto.SSL.SSLError, e:
            ObsLightPrintManager.getLogger().error(str(e))
            msg = "apiurl %s Connection reset by peer"
            ObsLightPrintManager.getLogger().error(msg % apiurl)
            return None
        except M2Crypto.SSL.Checker.NoCertificate:
            msg = "apiurl %s Peer did not return certificate"
            ObsLightPrintManager.getLogger().error(msg % str(apiurl))
            return None

    def createObsPackage(self, apiurl, projectObsName, package, title="", description=""):
        self.get_config()
        url = str(apiurl + "/source/" + projectObsName + "/" + package + "/_meta")

        tmp = '<package project="%s" name="%s"><title>%s</title>'
        tmp += '<description>%s</description></package>'
        tmp = tmp % (projectObsName, package, title, description)

        aElement = ElementTree.fromstring(tmp)

        try:
            self.http_request("PUT", url, data=ElementTree.tostring(aElement), timeout=TIMEOUT)
            return 0
        except urllib2.URLError, e:
            ObsLightPrintManager.getLogger().error(str(e))
            ObsLightPrintManager.getLogger().error("apiurl %s is not reachable" % str(apiurl))
            return None
        except M2Crypto.SSL.SSLError, e:
            ObsLightPrintManager.getLogger().error(str(e))
            msg = "apiurl %s Connection reset by peer"
            ObsLightPrintManager.getLogger().error(msg % apiurl)
            return None
        except M2Crypto.SSL.Checker.NoCertificate:
            msg = "apiurl %s Peer did not return certificate"
            ObsLightPrintManager.getLogger().error(msg % str(apiurl))
            return None

    def testApi(self, api, user, passwd):
        '''
        return 0 if the API,user and passwd is OK.
        return 1 if user and passwd  are wrong.
        return 2 if api is wrong.
        '''
        url = "/about"
        auth_handler = urllib2.HTTPBasicAuthHandler(urllib2.HTTPPasswordMgrWithDefaultRealm())
        auth_handler.add_password(realm=None,
                                  uri=api,
                                  user=user,
                                  passwd=passwd)

        opener = urllib2.build_opener(auth_handler,
                                      urllib2.ProxyHandler(urllib.getproxies_environment()))
        urllib2.install_opener(opener)

        logger = ObsLightPrintManager.getLogger()
        logger.info("Trying to log to '%s' with user '%s'", api, user)
        try:
            res = urllib2.urlopen(api + url).read()
            if isinstance(res, basestring):
                return 0
            else:
                return -1
        except urllib2.HTTPError:
            msg = "Could not open %s: wrong user or password"
            logger.warning(msg, api)
            return 1
        except urllib2.URLError:
            msg = "Could not open %s: wrong URL"
            logger.warning(msg, api)
            return 2

    def repairOscPackageDirectory(self, path):
        os.chdir(path)
        command = "pwd"
        self.__subprocess(command=command)
        command = "osc repairwc ."
        self.__subprocess(command=command)

        for f in  os.listdir(path):
            if not os.path.isdir(path + "/" + f):
                os.unlink(path + "/" + f)
        self.__subprocess(command=command)


    def getPackageFileInfo(self, workingdir):
        try:
            pk = core.Package(workingdir=workingdir)
        except oscerr.WorkingCopyInconsistent:
            raise ObsLightErr.ObsLightOscErr(self.WorkingCopyInconsistentMessage % workingdir)
        return pk.get_status()

    def autoResolvedConflict(self, packagePath, aFile):
        os.chdir(packagePath)
        command = "osc resolved " + aFile
        self.__subprocess(command=command)

    def cleanBuffer(self, url):
        if url in self.__httpBuffer.keys():
            del self.__httpBuffer[url]

    def getHttp_request(self, url, headers={}, data=None, file=None):
        url = self.__cleanUrl(url)

        if (HTTPBUFFER == 1) and (headers == {}) and (data == None) and (file == None) and (url in self.__httpBuffer.keys()):
            return self.__httpBuffer[url]
        try:
            fileXML = ""
            count = 0
            while(fileXML == "" and count < 4):
                count += 1
                res = self.http_request(method="GET", url=url, headers=headers, data=data, file=file, timeout=TIMEOUT)
                fileXML = res.read()

            if fileXML == None:
                ObsLightErr.ObsLightOscErr("Error the request on '" + url + "' return None.")

            if (HTTPBUFFER == 1) and (headers == {}) and (data == None) and (file == None):
                self.__httpBuffer[url] = fileXML

            return fileXML

        except urllib2.URLError, e:
            ObsLightPrintManager.getLogger().error("apiurl " + str(url) + " is not reachable")
            return None
        except M2Crypto.SSL.SSLError, e:
            ObsLightPrintManager.getLogger().error(str(e))
            ObsLightPrintManager.getLogger().error("apiurl " + str(url) + " Connection reset by peer")
            return None
        except M2Crypto.SSL.Checker.NoCertificate:
            ObsLightPrintManager.getLogger().error("apiurl " + str(url) + " Peer did not return certificate")
            return None
        return None

    def http_request(self, method, url, headers={}, data=None, file=None, timeout=100):
        """wrapper around urllib2.urlopen for error handling,
        and to support additional (PUT, DELETE) methods"""

        filefd = None

#        if conf.config['http_debug']:
#            print >> sys.stderr, '\n\n--', method, url

        if method == 'POST' and not file and not data:
            # adding data to an urllib2 request transforms it into a POST
            data = ''

        req = urllib2.Request(url)
        api_host_options = {}

        try:
            self.__aLock.acquire()
            if conf.is_known_apiurl(url):
                # ok no external request
                urllib2.install_opener(self._build_opener(url))
                api_host_options = conf.get_apiurl_api_host_options(url)
                for header, value in api_host_options['http_headers']:
                    req.add_header(header, value)


            req.get_method = lambda: method

            # POST requests are application/x-www-form-urlencoded per default
            # since we change the request into PUT, we also need to adjust the content type header
            if method == 'PUT' or (method == 'POST' and data):
                req.add_header('Content-Type', 'application/octet-stream')

            if type(headers) == type({}):
                for i in headers.keys():
                    req.add_header(i, headers[i])

            if file and not data:
                size = os.path.getsize(file)
                if size < 1024 * 512:
                    data = open(file, 'rb').read()
                else:
                    import mmap
                    filefd = open(file, 'rb')
                    try:
                        if sys.platform[:3] != 'win':
                            data = mmap.mmap(filefd.fileno(), os.path.getsize(file),
                                             mmap.MAP_SHARED, mmap.PROT_READ)
                        else:
                            data = mmap.mmap(filefd.fileno(), os.path.getsize(file))
                        data = buffer(data)
                    except EnvironmentError, e:
                        if e.errno == 19:
                            sys.exit('\n\n%s\nThe file \'%s\' could not be memory mapped. It is ' \
                                     '\non a filesystem which does not support this.' % (e, file))
                        elif hasattr(e, 'winerror') and e.winerror == 5:
                            # falling back to the default io
                            data = open(file, 'rb').read()
                        else:
                            raise

    #        if conf.config['debug']: print >> sys.stderr, method, url

            old_timeout = socket.getdefaulttimeout()
            # XXX: dirty hack as timeout doesn't work with python-m2crypto
            if old_timeout != timeout and not api_host_options.get('sslcertck'):
                socket.setdefaulttimeout(timeout)
        finally:
            self.__aLock.release()

        try:
            fd = urllib2.urlopen(req, data=data)
        finally:
            if old_timeout != timeout and not api_host_options.get('sslcertck'):
                socket.setdefaulttimeout(old_timeout)
            if hasattr(conf.cookiejar, 'save'):
                conf.cookiejar.save(ignore_discard=True)

        if filefd: filefd.close()

        return fd

    def _build_opener(self, url):
        from osc.core import __version__
#        import urllib2
#        import sys

        apiurl = self.urljoin(*conf.parse_apisrv_url(None, url))
        if not self.__dict__.has_key('last_opener'):
            self.last_opener = (None, None, None)
        if (apiurl == self.last_opener[0]) and (threading.currentThread().getName() == self.last_opener[2]):
            return self.last_opener[1]

        # respect no_proxy env variable
        if urllib.proxy_bypass(apiurl):
            # initialize with empty dict
            proxyhandler = urllib2.ProxyHandler({})
        else:
            # read proxies from env
            proxyhandler = urllib2.ProxyHandler()

        # workaround for http://bugs.python.org/issue9639
        authhandler_class = urllib2.HTTPBasicAuthHandler
        if sys.version_info >= (2, 6, 6) and sys.version_info < (2, 7, 1) \
            and not 'reset_retry_count' in dir(urllib2.HTTPBasicAuthHandler):
            logger = ObsLightPrintManager.getLogger()
            logger.error('warning: your urllib2 version seems to be broken. ' \
                'Using a workaround for http://bugs.python.org/issue9639')
            class OscHTTPBasicAuthHandler(urllib2.HTTPBasicAuthHandler):
                def http_error_401(self, *args):
                    response = urllib2.HTTPBasicAuthHandler.http_error_401(self, *args)
                    self.retried = 0
                    return response

                def http_error_404(self, *args):
                    self.retried = 0
                    return None

            authhandler_class = OscHTTPBasicAuthHandler
        elif sys.version_info >= (2, 6, 6) and sys.version_info < (2, 7, 1):
            class OscHTTPBasicAuthHandler(urllib2.HTTPBasicAuthHandler):
                def http_error_404(self, *args):
                    self.reset_retry_count()
                    return None

            authhandler_class = OscHTTPBasicAuthHandler
        elif sys.version_info >= (2, 6, 5) and sys.version_info < (2, 6, 6):
            # workaround for broken urllib2 in python 2.6.5: wrong credentials
            # lead to an infinite recursion
            class OscHTTPBasicAuthHandler(urllib2.HTTPBasicAuthHandler):
                def retry_http_basic_auth(self, host, req, realm):
                    # don't retry if auth failed
                    if req.get_header(self.auth_header, None) is not None:
                        return None
                    return urllib2.HTTPBasicAuthHandler.retry_http_basic_auth(self, host, req, realm)

            authhandler_class = OscHTTPBasicAuthHandler

        options = conf.config['api_host_options'][apiurl]
        # with None as first argument, it will always use this username/password
        # combination for urls for which arg2 (apisrv) is a super-url
        authhandler = authhandler_class(\
            urllib2.HTTPPasswordMgrWithDefaultRealm())
        authhandler.add_password(None, apiurl, options['user'], options['pass'])

        if options['sslcertck']:
            try:
                from osc import  oscsslexcp
                from osc import oscssl
                from M2Crypto import m2urllib2

            except ImportError, e:
                msg = 'M2Crypto is needed to access %s in a secure way.\nPlease install python-m2crypto.'
                raise oscsslexcp.NoSecureSSLError(msg % apiurl)

            cafile = options.get('cafile', None)
            capath = options.get('capath', None)
            if not cafile and not capath:
                for i in ['/etc/pki/tls/cert.pem', '/etc/ssl/certs' ]:
                    if os.path.isfile(i):
                        cafile = i
                        break
                    elif os.path.isdir(i):
                        capath = i
                        break
            ctx = oscssl.mySSLContext()
            if ctx.load_verify_locations(capath=capath, cafile=cafile) != 1:
                raise Exception('No CA certificates found')
            opener = m2urllib2.build_opener(ctx,
                                            oscssl.myHTTPSHandler(ssl_context=ctx, appname='osc'),
                                            urllib2.HTTPCookieProcessor(conf.cookiejar),
                                            authhandler,
                                            urllib2.ProxyHandler(urllib.getproxies_environment()))
        else:
#            import sys
            #print >> sys.stderr, "WARNING: SSL certificate checks disabled. Connection is insecure!\n"
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(conf.cookiejar), authhandler, urllib2.ProxyHandler(urllib.getproxies_environment()))
        opener.addheaders = [('User-agent', 'osc/%s' % __version__)]
        self.last_opener = (apiurl, opener, threading.currentThread().getName())
        return opener

    def urljoin(self, scheme, apisrv):
        return '://'.join([scheme, apisrv])

#class TrustedCertStore:
#    _tmptrusted = {}
#
#    def __init__(self, host, port, app, cert):
#
#        self.cert = cert
#        self.host = host
#        if self.host == None:
#            raise Exception("empty host")
#        if port:
#            self.host += "_%d" % port
#        import os
#        self.dir = os.path.expanduser('~/.config/%s/trusted-certs' % app)
#        self.file = self.dir + '/%s.pem' % self.host
#
#    def is_known(self):
#        if self.host in self._tmptrusted:
#            return True
#
#        import os
#        if os.path.exists(self.file):
#            return True
#        return False
#
#    def is_trusted(self):
#        import os
#        if self.host in self._tmptrusted:
#            cert = self._tmptrusted[self.host]
#        else:
#            if not os.path.exists(self.file):
#                return False
#            from M2Crypto import X509
#            cert = X509.load_cert(self.file)
#        if self.cert.as_pem() == cert.as_pem():
#            return True
#        else:
#            return False
#
#    def trust_tmp(self):
#        self._tmptrusted[self.host] = self.cert
#
#    def trust_always(self):
#        self.trust_tmp()
#        from M2Crypto import X509
#        import os
#        if not os.path.exists(self.dir):
#            os.makedirs(self.dir)
#        self.cert.save_pem(self.file)
#
#
## verify_cb is called for each error once
## we only collect the errors and return suceess
## connection will be aborted later if it needs to
#def verify_cb(ctx, ok, store):
#    if not ctx.verrs:
#        ctx.verrs = ValidationErrors()
#
#    try:
#        if not ok:
#            ctx.verrs.record(store.get_current_cert(), store.get_error(), store.get_error_depth())
#        return 1
#
#    except Exception, e:
#        logger = ObsLightPrintManager.getLogger()
#        logger.error(str(e))
#        return 0
#
#class FailCert:
#    def __init__(self, cert):
#        self.cert = cert
#        self.errs = []
#
#class ValidationErrors:
#
#    def __init__(self):
#        self.chain_ok = True
#        self.cert_ok = True
#        self.failures = {}
#
#    def record(self, cert, err, depth):
#        #print "cert for %s, level %d fail(%d)" % ( cert.get_subject().commonName, depth, err )
#        if depth == 0:
#            self.cert_ok = False
#        else:
#            self.chain_ok = False
#
#        if not depth in self.failures:
#            self.failures[depth] = FailCert(cert)
#        else:
#            if self.failures[depth].cert.get_fingerprint() != cert.get_fingerprint():
#                raise Exception("Certificate changed unexpectedly. This should not happen")
#        self.failures[depth].errs.append(err)
#
#    def show(self):
#        for depth in self.failures.keys():
#            cert = self.failures[depth].cert
#            logger = ObsLightPrintManager.getLogger()
#            logger.error("*** certificate verify failed at depth %d" % depth)
#            logger.error("Subject: ", cert.get_subject())
#            logger.error("Issuer:  ", cert.get_issuer())
#            logger.error("Valid: ", cert.get_not_before(), "-", cert.get_not_after())
#            logger.error("Fingerprint(MD5):  ", cert.get_fingerprint('md5'))
#            logger.error("Fingerprint(SHA1): ", cert.get_fingerprint('sha1'))
#
#            for err in self.failures[depth].errs:
#                reason = "Unknown"
#                try:
#                    import M2Crypto.Err
#                    reason = M2Crypto.Err.get_x509_verify_error(err)
#                except:
#                    pass
#                logger = ObsLightPrintManager.getLogger()
#                logger.error("Reason:" + str(reason))
#
#    # check if the encountered errors could be ignored
#    def could_ignore(self):
#        if not 0 in self.failures:
#            return True
#
#        from M2Crypto import m2
#        nonfatal_errors = [
#                m2.X509_V_ERR_UNABLE_TO_GET_ISSUER_CERT_LOCALLY,
#                m2.X509_V_ERR_SELF_SIGNED_CERT_IN_CHAIN,
#                m2.X509_V_ERR_DEPTH_ZERO_SELF_SIGNED_CERT,
#                m2.X509_V_ERR_CERT_UNTRUSTED,
#                m2.X509_V_ERR_UNABLE_TO_VERIFY_LEAF_SIGNATURE,
#
#                m2.X509_V_ERR_CERT_NOT_YET_VALID,
#                m2.X509_V_ERR_CERT_HAS_EXPIRED,
#                m2.X509_V_OK,
#                ]
#
#        canignore = True
#        for err in self.failures[0].errs:
#            if not err in nonfatal_errors:
#                canignore = False
#                break
#
#        return canignore
#
#class mySSLContext(SSL.Context):
#
#    def __init__(self):
#        SSL.Context.__init__(self, 'sslv23')
#        self.set_options(m2.SSL_OP_ALL | m2.SSL_OP_NO_SSLv2 | m2.SSL_OP_NO_SSLv3)
#        self.set_cipher_list("HIGH:!eNULL:!aNULL:!EXPORT:!LOW:!MEDIUM:!FZA:!kRSA:!MD5:!RC4:!SSLv2:@STRENGTH")
#        self.set_session_cache_mode(m2.SSL_SESS_CACHE_CLIENT)
#        self.verrs = None
#        #self.set_info_callback() # debug
#        self.set_verify(SSL.verify_peer | SSL.verify_fail_if_no_peer_cert, depth=9, callback=lambda ok, store: verify_cb(self, ok, store))
#
#class myHTTPSHandler(M2Crypto.m2urllib2.HTTPSHandler):
#    handler_order = 499
#    saved_session = None
#
#    def __init__(self, *args, **kwargs):
#        self.appname = kwargs.pop('appname', 'generic')
#        M2Crypto.m2urllib2.HTTPSHandler.__init__(self, *args, **kwargs)
#
#    # copied from M2Crypto.m2urllib2.HTTPSHandler
#    # it's sole purpose is to use our myHTTPSHandler/myHTTPSProxyHandler class
#    # ideally the m2urllib2.HTTPSHandler.https_open() method would be split into
#    # "do_open()" and "https_open()" so that we just need to override
#    # the small "https_open()" method...)
#    def https_open(self, req):
#        host = req.get_host()
#        if not host:
#            raise M2Crypto.m2urllib2.URLError('no host given: ' + req.get_full_url())
#
#        # Our change: Check to see if we're using a proxy.
#        # Then create an appropriate ssl-aware connection.
#        full_url = req.get_full_url()
#        target_host = urlparse.urlparse(full_url)[1]
#
#        if (target_host != host):
#            h = myProxyHTTPSConnection(host=host, appname=self.appname, ssl_context=self.ctx)
#            # M2Crypto.ProxyHTTPSConnection.putrequest expects a fullurl
#            selector = full_url
#        else:
#            h = myHTTPSConnection(host=host, appname=self.appname, ssl_context=self.ctx)
#            selector = req.get_selector()
#        # End our change
#        h.set_debuglevel(self._debuglevel)
#        if self.saved_session:
#            h.set_session(self.saved_session)
#
#        headers = dict(req.headers)
#        headers.update(req.unredirected_hdrs)
#        # We want to make an HTTP/1.1 request, but the addinfourl
#        # class isn't prepared to deal with a persistent connection.
#        # It will try to read all remaining data from the socket,
#        # which will block while the server waits for the next request.
#        # So make sure the connection gets closed after the (only)
#        # request.
#        headers["Connection"] = "close"
#        try:
#            h.request(req.get_method(), selector, req.data, headers)
#            s = h.get_session()
#            if s:
#                self.saved_session = s
#            r = h.getresponse()
#        except socket.error, err: # XXX what error?
#            err.filename = full_url
#            raise M2Crypto.m2urllib2.URLError(err)
#
#        # Pick apart the HTTPResponse object to get the addinfourl
#        # object initialized properly.
#
#        # Wrap the HTTPResponse object in socket's file object adapter
#        # for Windows.  That adapter calls recv(), so delegate recv()
#        # to read().  This weird wrapping allows the returned object to
#        # have readline() and readlines() methods.
#
#        # XXX It might be better to extract the read buffering code
#        # out of socket._fileobject() and into a base class.
#
#        r.recv = r.read
#        fp = socket._fileobject(r)
#
#        resp = urllib.addinfourl(fp, r.msg, req.get_full_url())
#        resp.code = r.status
#        resp.msg = r.reason
#        return resp
#
#class myHTTPSConnection(M2Crypto.httpslib.HTTPSConnection):
#    def __init__(self, *args, **kwargs):
#        self.appname = kwargs.pop('appname', 'generic')
#        M2Crypto.httpslib.HTTPSConnection.__init__(self, *args, **kwargs)
#
#    def connect(self, *args):
#        M2Crypto.httpslib.HTTPSConnection.connect(self, *args)
#        verify_certificate(self)
#
#    def getHost(self):
#        return self.host
#
#    def getPort(self):
#        return self.port
#
#class myProxyHTTPSConnection(M2Crypto.httpslib.ProxyHTTPSConnection, httplib.HTTPSConnection):
#    def __init__(self, *args, **kwargs):
#        self.appname = kwargs.pop('appname', 'generic')
#        M2Crypto.httpslib.ProxyHTTPSConnection.__init__(self, *args, **kwargs)
#
#    def _start_ssl(self):
#        M2Crypto.httpslib.ProxyHTTPSConnection._start_ssl(self)
#        verify_certificate(self)
#
#    def endheaders(self, *args, **kwargs):
#        if self._proxy_auth is None:
#            self._proxy_auth = self._encode_auth()
#        httplib.HTTPSConnection.endheaders(self, *args, **kwargs)
#
#    # broken in m2crypto: port needs to be an int
#    def putrequest(self, method, url, skip_host=0, skip_accept_encoding=0):
#        #putrequest is called before connect, so can interpret url and get
#        #real host/port to be used to make CONNECT request to proxy
#        proto, rest = urllib.splittype(url)
#        if proto is None:
#            raise ValueError, "unknown URL type: %s" % url
#        #get host
#        host, rest = urllib.splithost(rest)
#        #try to get port
#        host, port = urllib.splitport(host)
#        #if port is not defined try to get from proto
#        if port is None:
#            try:
#                port = self._ports[proto]
#            except KeyError:
#                raise ValueError, "unknown protocol for: %s" % url
#        self._real_host = host
#        self._real_port = int(port)
#        M2Crypto.httpslib.HTTPSConnection.putrequest(self, method, url, skip_host, skip_accept_encoding)
#
#    def getHost(self):
#        return self._real_host
#
#    def getPort(self):
#        return self._real_port
#
#def verify_certificate(connection):
#    ctx = connection.sock.ctx
#    verrs = ctx.verrs
#    ctx.verrs = None
#    cert = connection.sock.get_peer_cert()
#    if not cert:
#        connection.close()
#        raise SSLVerificationError("server did not present a certificate")
#
#    # XXX: should be check if the certificate is known anyways?
#    # Maybe it changed to something valid.
#    if not connection.sock.verify_ok():
#
#        tc = TrustedCertStore(connection.getHost(), connection.getPort(), connection.appname, cert)
#
#        if tc.is_known():
#
#            if tc.is_trusted(): # ok, same cert as the stored one
#                return
#            else:
#                logger = ObsLightPrintManager.getLogger()
#                logger.error("WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!")
#                logger.error("IT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!")
#                logger.error("offending certificate is at '%s'" % tc.file)
#                raise SSLVerificationError("remote host identification has changed")
#
#        verrs.show()
#
#
#        if not verrs.could_ignore():
#            raise SSLVerificationError("Certificate validation error cannot be ignored")
##        if not verrs.chain_ok:
##            print "A certificate in the chain failed verification"
##        if not verrs.cert_ok:
##            print "The server certificate failed verification"
#
##        while True:
##            print """
##Would you like to
##0 - quit (default)
##1 - continue anyways
##2 - trust the server certificate permanently
##9 - review the server certificate
##"""
##
##            r = raw_input("Enter choice [0129]: ")
##            if not r or r == '0':
##                connection.close()
##                raise SSLVerificationError("Untrusted Certificate")
##            elif r == '1':
##                tc.trust_tmp()
##                return
##            elif r == '2':
#        tc.trust_always()
#        return
##            elif r == '9':
##                print cert.as_text()


__myObsLightOsc = ObsLightOsc()

def getObsLightOsc():
    '''
    
    '''
    #if __myObsLightOsc == None:
    #    __myObsLightOsc = ObsLightOsc()
    return __myObsLightOsc


if __name__ == '__main__':
#    package = "intel-Lakemore"
#    projectObsName = "WindRiver:tools"
    api = "http://128.224.219.16:81"
    projectObsName = "meegotv:mutter"
    package = "xbmc"
    projectTarget = "MeeGoTV_1.2"
    arch = "i586"

#    obsuser:opensuse
    result = ObsLightOsc().getPackageBuildRequires(api,
                                                   projectObsName,
                                                   package,
                                                   projectTarget,
                                                   arch)

    print " ".join(result)
