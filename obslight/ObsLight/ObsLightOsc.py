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
Created on 3 oct. 2011

@author: ronan@fridu.net
@author: Florent Vennetier
'''

import os
import sys
import time
import stat
from xml.etree import ElementTree
import urlparse
import urllib

import re

#from M2Crypto import m2, SSL
#import httplib

#from M2Crypto.SSL.Checker import SSLVerificationError

try:
    from ObsLight import ObsLightTools
except:# pylint: disable-msg=W0702
    pass

from osc import conf
from osc import core
from osc import oscerr

from osc.fetch import Fetcher
from osc.build import Buildinfo
#from osc.build import  check_trusted_projects

from ObsLightObject import ObsLightObject
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

#HTTPBUFFER = ObsLightConfig.getHttpBuffer()
HTTPBUFFER = 0

import threading


import tempfile

class PrintHandler(object):
    """
    Wrapper for sys.stderr and sys.stdout that writes to a log file.
    """

    def __init__(self, stream):
        self.stream = stream


    def write(self, buf):
        self.stream(str(buf))

    def flush(self):
        pass

    def close(self):
        pass

    def isatty(self):
        return True

class ObsLightOsc(ObsLightObject):
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
        ObsLightObject.__init__(self)
        self.__confFile = os.path.join(os.environ['HOME'], ".oscrc")
        self.__mySubprocessCrt = ObsLightSubprocess.SubprocessCrt()

        self.__aLock = threading.Lock()

        self.__httpBuffer = {}

        if os.path.isfile(self.__confFile):
            self.get_config()
            if not self.isApihostInPackageCacheDir():
                self.addApihostInPackageCacheDir()

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
        f = open(self.__confFile, 'r')
        txt = f.read()
        f.close()
        f = open(self.__confFile, 'w')
        f.write(txt.replace("[" + api + "]", "[" + newApi + "]"))
        f.close()

    @staticmethod
    def isApihostInPackageCacheDir():
        """
        Test if the 'packagecachedir' configuration option
        contains an 'apihost' pattern.
        """
        return "%(apihost)s" in conf.config["packagecachedir"]

    def addApihostInPackageCacheDir(self):
        """Append '%(apihost)s' to the 'packagecachedir' config option"""
        packageCacheDir = conf.config["packagecachedir"]
        packageCacheDir = os.path.join(packageCacheDir, "%(apihost)s")
        conf.config_set_option("general", "packagecachedir", packageCacheDir)
        conf.write_config(self.__confFile, conf.get_configParser())

    def getUserProfil(self, api, user):
        "GET /person/<userid>"
        pass

    def changeUser(self, api, user):
        self.get_config()
        aOscConfigParser = conf.get_configParser(self.__confFile, force_read=True)

        aOscConfigParser.set(api, 'user', user)

        aFile = open(self.__confFile, 'w')
        aOscConfigParser.write(aFile, True)

    def changePassw(self, api, passw):
        self.get_config()
        aOscConfigParser = conf.get_configParser(self.__confFile, force_read=True)
        aOscConfigParser.set(api, 'pass', passw)

        aFile = open(self.__confFile, 'w')
        aOscConfigParser.write(aFile, True)

    def getServersFromOsc(self):
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
        self.logger.debug("api" + api)
        self.get_config()
        aOscConfigParser = conf.get_configParser(self.__confFile, force_read=True)

        if aOscConfigParser.has_option(api, "trusted_prj"):
            options = aOscConfigParser.get(api, "trusted_prj")
        else:
            options = ""

        result = options
        self.logger.debug("To Add ?" + ("").join(listDepProject.keys()))
        self.logger.debug("Current:" + ("").join(result))
        for depProject in listDepProject.keys():
            if not depProject in result.split(" "):
                result += " " + depProject

        self.logger.debug("Result" + ("").join(result))
        aOscConfigParser.set(api, 'trusted_prj', result)

        aFile = open(self.__confFile, 'w')
        aOscConfigParser.write(aFile, True)
        if aFile: aFile.close()
        return


    def getPackageBuildRequires(self,
                                api,
                                projectObsName,
                                package,
                                projectTarget,
                                arch,
                                specFile,
                                extraPackages=[],
                                existsOnServer=True):
        self.get_config()
        if existsOnServer:
            buildinfoUrl = "%(api)s/build/%(project)s/%(target)s/%(arch)s/%(package)s/_buildinfo"
        else:
            buildinfoUrl = "%(api)s/build/%(project)s/%(target)s/%(arch)s/_repository/_buildinfo"
        buildinfoUrl = buildinfoUrl % {"api": api,
                                       "project": projectObsName,
                                       "package": package,
                                       "target": projectTarget,
                                       "arch": arch}

        if len(extraPackages) > 0:
            query = "?add=" + "&add=".join(extraPackages)
            buildinfoUrl += query
        self.logger.debug("Getting buildrequires of %s from %s" % (package, buildinfoUrl))
        self.cleanBuffer(buildinfoUrl)

        try:
            # We must read specfile before giving the content to http_request "data":
            # giving the path of the specfile to http_request "aFile" would result
            # in error 400 in some obscure cases.
            with open(specFile) as specFileObj:
                build_descr_data = specFileObj.read()
            result = self.http_request("POST", str(buildinfoUrl),
                                       data=build_descr_data, timeout=TIMEOUT)
        except urllib2.HTTPError as he:
            msg = "Could not compute buildinfo. Server returned error %d" % he.getcode()
            if hasattr(he, "fp") and he.fp is not None:
                msg += " with message:\n%s" % he.fp.read()
            raise ObsLightErr.ObsLightOscErr(msg)

        buildInfo = result.read()

        for package in ElementTree.fromstring(buildInfo):
            if (package.tag == "error") :
                msg = package.text
                raise ObsLightErr.ObsLightOscErr(msg)

        return buildInfo

    def getOscPackagecachedir(self, obsDir=""):
        return conf.config['packagecachedir'] % {'apihost': obsDir}

    def updateCache(self, buildInfoXml, apihost):

        aFile = tempfile.NamedTemporaryFile("w", delete=False)
        aFile.write(buildInfoXml)
        aFile.flush()
        aFile.close()

        bi_filename = aFile.name
        apiurl = str(urlparse.urlparse(apihost)[1])

        build_type = "spec"
        prefer_pkgs = {}

        bi = Buildinfo(bi_filename, apihost, build_type, prefer_pkgs.keys())

        #Fix to solve Http 401 error under debian.
        conf._build_opener.last_opener = (None, None)

        cache_dir = self.getOscPackagecachedir(apiurl)

        urllist = []

        # transform 'url1, url2, url3' form into a list
        if 'urllist' in conf.config:
            if type(conf.config['urllist']) == str:
                re_clist = re.compile('[, ]+')
                urllist = [ i.strip() for i in re_clist.split(conf.config['urllist'].strip()) ]
            else:
                urllist = conf.config['urllist']

        # OBS 1.5 and before has no downloadurl defined in buildinfo
        if bi.downloadurl:
            urllist.append(bi.downloadurl + '/%(extproject)s/%(extrepository)s/%(arch)s/%(filename)s')

        urllist.append('%(apiurl)s/build/%(project)s/%(repository)s/%(repoarch)s/%(repopackage)s/%(repofilename)s')

        old_stderr = sys.stderr
        old_stdout = sys.stdout

        sys.stdout = PrintHandler(ObsLightPrintManager.getLogger().info)
        sys.stderr = PrintHandler(ObsLightPrintManager.getLogger().error)

        fetcher = Fetcher(cache_dir,
                          urllist=urllist,
                          api_host_options=conf.config['api_host_options'],
                          http_debug=False,
                          enable_cpio=True,
                          cookiejar=conf.cookiejar)

#        check_trusted_projects(apiurl, [ i for i in bi.projects.keys() if not i == prj ])
        self.get_config()
        fetcher.run(bi)

        sys.stderr = old_stderr
        sys.stdout = old_stdout
        return bi

    def getDepProject(self,
                      apiurl=None,
                      projet=None,
                      repos=None):
        self.get_config()
        url = str(apiurl + "/source/" + projet + "/_meta")
        result = self.getHttp_request(url)
        if result is None:
            return None
        aElement = ElementTree.fromstring(result)

        result = {}
        for project in aElement:
            if (project.tag == "repository") and (project.get("name") == repos):
                for path in project.getiterator():
                    if path.tag == "path":
                        result[path.get("project")] = path.get("repository")
        return result

    def getPackageList(self,
                       apiurl=None,
                       projectLocalName=None):
        """Deprecated, for compatibility"""
        return self.getPackageList(apiurl, projectLocalName)

    def getPackageList(self,
                       apiurl=None,
                       projectLocalName=None):
        """
        Get the package list of project `projectLocalName` from `apiurl`.
        """
        url = str(apiurl + "/source/" + projectLocalName)

        result = self.getHttp_request(url)
        if result is None:
            message = "Failed to retrieve package list from server."
            raise ObsLightErr.ObsLightOscErr(message)

        aElement = ElementTree.fromstring(result)

        aList = []
        for path in aElement:
            if (path.tag == "entry"):
                aList.append(path.get("name"))
        return aList

    def getPackageFileList(self, apiurl, projectObsName, packageName):
        """
        Get the list of files of package `packageName`
        """
        url = str(apiurl + "/source/" + projectObsName + "/" + packageName)
        self.cleanBuffer(url)
        result = self.getHttp_request(url)
        if result is None:
            return None

        aElement = ElementTree.fromstring(result)

        result = {}
        for path in aElement:
            if (path.tag == "entry"):
                fileEntry = {}
                fileEntry["name"] = path.get("name")
                fileEntry["md5"] = path.get("md5")
                fileEntry["size"] = path.get("size")
                fileEntry["mtime"] = path.get("mtime")
                result[fileEntry["name"]] = fileEntry
        return result

    def getFilesListPackage(self,
                            apiurl=None,
                            projectObsName=None,
                            package=None):
        """Deprecated, for compatibility"""
        return self.getPackageFileList(apiurl, projectObsName, package)

    def getObsPackageRev(self,
                         apiurl,
                         projectObsName,
                         package):
        url = str(apiurl + "/source/" + projectObsName + "/" + package)
        self.cleanBuffer(url)
        result = self.getHttp_request(url)
        if result is None:
            return result
        aElement = ElementTree.fromstring(result)

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
        except BaseException:
            return None

        return aElement.get("rev")





    def __subprocess(self, command=None, waitMess=False):
        result = None
        count = 0
        while(result is None and count < 4):
            count += 1
            try:
                result = self.__mySubprocessCrt.execSubprocess(command=command, waitMess=waitMess)
                break
            except BaseException:
                self.logger.error("__subprocess ERROR.")
        if result is None:
            return -1
        return result

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
        result = self.getHttp_request(url)
        if result is None:
            return None
        aElement = ElementTree.fromstring(result)

        return aElement.attrib["code"]

    def getDependencyProject(self, apiurl, project, target):
        self.get_config()
        url = str(apiurl + "/source/" + project + "/_meta")
        result = self.getHttp_request(url)
        if result is None:
            return None
        aElement = ElementTree.fromstring(result)

        result = {}

        for project in aElement:
            if (project.tag == "repository") and (project.get("name") == target):
                for path in project.getiterator():
                    if path.tag == "path":
                        aTarget = path.get("repository")
                        aProject = path.get("project")
                        result[aProject] = aTarget
        return result

    def getDependencyProjects(self, api, projectObsName, target, result=None):
        '''
        Return the list of the dependency repositories.
        '''
        result = result or {}
        listProject = self.getLocalProjectList(obsServer=api)
        resultTMP = self.getDependencyProject(api, projectObsName, target)
        resultTMP[projectObsName] = target
        for project in resultTMP.keys():
            if (project in listProject) and not (project in result.keys()):
                result[project] = resultTMP[project]
                result = self.getDependencyProjects(api, project, resultTMP[project], result)

        return result

    def getRpmListFromObsFull(self, apiurl, projet, repo , arch):
        self.get_config()
        result = str(apiurl + "/build/" + projet + "/" + repo + "/" + arch + "/_repository")
        self.cleanBuffer(result)
        result = self.getHttp_request(result)
        if result is None:
            return None
        aElement = ElementTree.fromstring(result)

        result = []
        for binTmp in aElement:
            if binTmp.tag == "binary":
                rpm = binTmp.get("filename")

                if rpm.endswith(".rpm"):
                    rpm = rpm[:-len(".rpm")]

                for arch in [arch, "noarch", "i686", "i586", "i486"]:
                    if rpm.startswith(arch + "/"):
                        rpm = rpm[len(arch + "/"):]

                    if rpm.endswith(arch):
                        rpm = rpm[:-len(".rpm")]

                if rpm.count("-") > 1:
                    rpmSplit = rpm.split("-")

                    tpmRpm = rpmSplit[:-2]
                    tpmRelease = rpmSplit[-1]
#                    tpmVersion = rpmSplit[-2]

                    if re.match(r'^[0-9]*\.[0-9]*\.', tpmRelease) != None:
                        rpm = "-".join(tpmRpm)

                result.append(rpm)
        return result


    def getDODUrl(self, apiurl, projet, arch):
        result = []
        self.get_config()
        url = str(apiurl + "/source/" + projet + "/_meta")
        resultTmp = self.getHttp_request(url)
        if resultTmp is None:
            return None
        aElement = ElementTree.fromstring(resultTmp)

        for project in aElement:
            if (project.tag == "download") :
                if arch == project.get("arch"):
                    result.append(project.get("baseurl"))

        return result

    def getAliasOfRepo(self, repo):
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
                    result = line.split("=")[1]
                    return result
            return None
        else:
            return None

    def createChRoot(self,
                     chrootDir,
                     repos,
                     arch,
                     apiurl,
                     project,
                     listExtraPkgs=None,
                     listOptExtraPkgs=None,
                     ):
        '''
        create a chroot
        '''
        listExtraPkgs = listExtraPkgs or ["ncurses-devel",
                                          "rpm"]

        listOptExtraPkgs = listOptExtraPkgs or ["gzip",
                                                "strace",
                                                "vim",
                                                "iptools",
                                                "sed"]

        os.chdir(EMPTYPROJECTPATH)

        extraPkgs = ""
        for pkg in listExtraPkgs:
            extraPkgs += "-x " + pkg + " "

        dependencyProjects = self.getDependencyProjects(apiurl, project, repos)

        resolve = []

        for prj in dependencyProjects.keys():
            res = self.getRpmListFromObsFull(apiurl, prj, dependencyProjects[prj], arch)
            resolve.extend(res)
        resolve = set(resolve)

        for pkg in listOptExtraPkgs:
            if pkg in resolve:
                extraPkgs += "-x " + pkg + " "

        command = "osc -A " + apiurl + " build --root=" + chrootDir + " " + extraPkgs
        command += " %(clean)s "
        command += " --noservice --no-verify --alternative-project " + project + " "
        command += repos + " " + arch + " --local-package emptySpec.spec"
        retCode = self.__subprocess(command % {"clean": "--clean"}, waitMess=True)

        # FIXME: since 0.5.1 there is a big regression: Tizen chroot jail creation fails.
        # The problem comes from Tizen's "rpm" package which does not own /usr/lib/rpm/tizen,
        # which gives this directory rwx------ file rights on certain conditions.
        # The following code is to workaround that.
        rpmTizenDir = os.path.join(chrootDir, "usr/lib/rpm/tizen")
        if retCode != 0 and os.path.isdir(rpmTizenDir):
            mode = os.stat(rpmTizenDir).st_mode
            if (stat.S_IMODE(mode) & (stat.S_IROTH | stat.S_IXOTH)) == 0:
                self.logger.warning("Using workaround for bug #25565")
                command2 = "sudo chmod 755 %s" % rpmTizenDir
                self.__subprocess(command2, waitMess=True)
                retCode = self.__subprocess(command % {"clean": ""}, waitMess=True)

        return retCode

    def getProjectListFromServer(self, obsApi):
        '''
        Return the list of projects hosted on the server
        pointed to by `obsApi`.
        '''
        self.get_config()
        url = str(obsApi + "/source")
        xmlRes = self.getHttp_request(url)
        if xmlRes is None:
            raise ObsLightErr.ObsLightOscErr("The request on '%s' returned None." % url)

        aElement = ElementTree.fromstring(xmlRes)
        res = []
        for project in aElement:
            aName = project.get("name")
            res.append(aName)
        res.sort()
        return res

    def getLocalProjectList(self, obsServer):
        return self.getProjectListFromServer(obsServer)

    def getFilteredProjectListFromServer(self,
                                         obsApi,
                                         maintainer=None,
                                         bugowner=None,
                                         arch=None,
                                         onlyRemoteUrls=False):
        """
        Return the list of projects hosted on the server
        pointed to by `obsApi`. `maintainer`, `bugowner` and `arch` allow
        to restrict the project list to project matching them.
        `onlyRemoteUrls` make the function return only the list of projects
        which are remote URLs.
        """
        self.get_config()
        url = str(obsApi + "/search/project")

        xmlRes = self.getHttp_request(url)
        if xmlRes is None:
            raise ObsLightErr.ObsLightOscErr("The request on '%s' returned None." % url)

        projects = ElementTree.fromstring(xmlRes)
        filteredProjectList = []
        for project in projects:
            maintainers = []
            bugowners = []
            architectures = []
            remoteUrl = None
            for val in project:
                if val.tag == "remoteurl":
                    remoteUrl = val.text
                if val.tag == "repository":
                    for repo in val:
                        if repo.tag == "arch":
                            architectures.append(repo.text)
                if val.tag == "person":
                    if val.get("role") == "maintainer":
                        maintainers.append(val.get("userid"))
                    if val.get("role") == "bugowner":
                        bugowners.append(val.get("userid"))
            if maintainer is not None and maintainer not in maintainers:
                continue
            elif bugowner is not None and bugowner not in bugowners:
                continue
            elif arch is not None and arch not in architectures:
                continue
            elif ((onlyRemoteUrls and remoteUrl is None) or
                  (not onlyRemoteUrls and remoteUrl is not None)):
                continue
            else:
                filteredProjectList.append(project.get("name"))
        filteredProjectList.sort()
        return filteredProjectList

    def getLocalProjectListFilter(self,
                                  obsServer,
                                  maintainer=False,
                                  bugowner=False,
                                  arch=None,
                                  remoteurl=False):
        return self.getFilteredProjectListFromServer(obsServer,
                                                     maintainer,
                                                     bugowner,
                                                     arch,
                                                     remoteurl)

    def saveProjectConfig(self, apiurl, projectObsName, target, filePath=None):
        if filePath is None:
            aFile = tempfile.NamedTemporaryFile("w", delete=False)
        else:
            aFile = open(filePath, "w")

        url = str(apiurl + "/build/" + projectObsName + "/" + target + "/_buildconfig")
        result = self.getHttp_request(url)
        aFile.write(result)

        aFile.flush()
        aFile.close()

        return aFile.name

    def getListRepos(self, apiurl):
        '''
        return the list of the repos of a OBS Server.
        '''
        url = str(apiurl + "/distributions")
        result = self.getHttp_request(url)
        if result is None:
            return None
        aElement = ElementTree.fromstring(result)
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
        result = urlparse.urlparse(url)

        return urlparse.urlunsplit((result[0], result[1], result[2].replace("//", "/"), '', ''))


    def getTargetList(self,
                      obsServer=None,
                      projectObsName=None):
        '''
        return the list of Target of a projectObsProject for a OBS server.
        '''
        url = str(obsServer + "/build/" + projectObsName)
        result = self.getHttp_request(url)
        if result is None:
            return None
        aElement = ElementTree.fromstring(result)
        result = []
        for directory in aElement:
            for entry in directory.getiterator():
                result.append(entry.get("name"))
        return result

    def getArchitectureList(self,
                            obsServer=None,
                            projectObsName=None,
                            projectTarget=None):
        '''
        return the list of Archictecture of the target of the projectObsName for a OBS server.
        '''

        url = str(obsServer + "/build/" + projectObsName + "/" + projectTarget)
        result = self.getHttp_request(url)
        if result is None:
            return None
        aElement = ElementTree.fromstring(result)
        result = []
        for directory in aElement:
            for entry in directory.getiterator():
                result.append(entry.get("name"))

        return result

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
        os.chdir(packagePath)
        command = "osc up"
        return self.__subprocess(command=command)

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

    def autoResolvedConflict(self, packagePath, aFile):
        os.chdir(packagePath)
        command = "osc resolved " + aFile
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
        result = self.getHttp_request(url)
        if result is None:
            return None
        aElement = ElementTree.fromstring(result)

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
        result = self.getHttp_request(aUrl)
        if result is None:
            return None
        aElement = ElementTree.fromstring(result)

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
        result = self.getHttp_request(aUrl)
        if result is None:
            return None
        aElement = ElementTree.fromstring(result)

        for desc in aElement:
            if "title" == desc.tag:
                title = desc.text
            elif "description" == desc.tag:
                description = desc.text
            elif "url" == desc.tag:
                _ = desc.text

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
        if res is None:
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
        if res is None:
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

        self.logger.info("Trying to log to '%s' with user '%s'", api, user)
        try:
            res = urllib2.urlopen(api + url).read()
            if isinstance(res, basestring):
                return 0
            else:
                return -1
        except urllib2.HTTPError:
            msg = "Could not open %s: wrong user or password"
            self.logger.warning(msg, api)
            return 1
        except urllib2.URLError:
            msg = "Could not open %s: wrong URL"
            self.logger.warning(msg, api)
            return 2



    def getPackageFileInfo(self, workingdir):
        try:
            pk = core.Package(workingdir=workingdir)
        except oscerr.WorkingCopyInconsistent:
            raise ObsLightErr.ObsLightOscErr(self.WorkingCopyInconsistentMessage % workingdir)
        return pk.get_status()

    def cleanBuffer(self, url):
        if url in self.__httpBuffer.keys():
            del self.__httpBuffer[url]

    def getHttp_request(self, url, headers=None, data=None, aFile=None):
        headers = headers or {}
        url = self.__cleanUrl(url)
        start = time.time()

        if (HTTPBUFFER == 1 and
            headers == {} and
            data is None and
            aFile is None and
            url in self.__httpBuffer.keys()):

            return self.__httpBuffer[url]
        try:
            fileXML = ""
            count = 0
            while(fileXML == "" and count < 4):
                count += 1
                res = self.http_request(method="GET",
                                        url=url,
                                        headers=headers,
                                        data=data,
                                        aFile=aFile,
                                        timeout=TIMEOUT)
                fileXML = res.read()

            if fileXML is None:
                ObsLightErr.ObsLightOscErr("Error the request on '" + url + "' return None.")
            if (HTTPBUFFER == 1) and (headers == {}) and (data is None) and (aFile is None):
                self.__httpBuffer[url] = fileXML

            if (HTTPBUFFER == 1) and (headers == {}) and (data is None) and (aFile is None):
                self.__httpBuffer[url] = fileXML
            end = time.time()
            self.logger.debug("The request on %s took %f seconds", url, end - start)
            return fileXML

        except urllib2.URLError, e:
            ObsLightPrintManager.getLogger().error("apiurl " + str(url) + " is not reachable")
            return None
        except M2Crypto.SSL.SSLError, e:
            ObsLightPrintManager.getLogger().error(str(e))
            message = "apiurl " + str(url) + " Connection reset by peer"
            ObsLightPrintManager.getLogger().error(message)
            return None
        except M2Crypto.SSL.Checker.NoCertificate:
            message = "apiurl " + str(url) + " Peer did not return certificate"
            ObsLightPrintManager.getLogger().error(message)
            return None
        return None

    def http_request(self, method, url, headers=None, data=None, aFile=None, timeout=100):
        """wrapper around urllib2.urlopen for error handling,
        and to support additional (PUT, DELETE) methods"""
        headers = headers or {}
        filefd = None

#        if conf.config['http_debug']:
#            print >> sys.stderr, '\n\n--', method, url

        if method == 'POST' and not aFile and not data:
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

            if aFile and not data:
                size = os.path.getsize(aFile)
                if size < 1024 * 512:
                    data = open(aFile, 'rb').read()
                else:
                    import mmap
                    filefd = open(aFile, 'rb')
                    try:
                        if sys.platform[:3] != 'win':
                            data = mmap.mmap(filefd.fileno(), os.path.getsize(aFile),
                                             mmap.MAP_SHARED, mmap.PROT_READ)
                        else:
                            data = mmap.mmap(filefd.fileno(), os.path.getsize(file))
                        data = buffer(data)
                    except EnvironmentError, e:
                        if e.errno == 19:
                            sys.exit('\n\n%s\nThe file \'%s\' could not be memory mapped. It is ' \
                                     '\non a filesystem which does not support this.' % (e,
                                                                                         aFile))
                        elif hasattr(e, 'winerror') and e.winerror == 5:
                            # falling back to the default io
                            data = open(aFile, 'rb').read()
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

        apiurl = self.urljoin(*conf.parse_apisrv_url(None, url))
        if not self.__dict__.has_key('last_opener'):
            self.last_opener = (None, None, None)
        if (apiurl == self.last_opener[0]) and \
            (threading.currentThread().getName() == self.last_opener[2]):
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
            self.logger.error('warning: your urllib2 version seems to be broken. ' \
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
                    return urllib2.HTTPBasicAuthHandler.retry_http_basic_auth(self,
                                                                              host,
                                                                              req,
                                                                              realm)

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

            except ImportError:
                msg = 'M2Crypto is needed to access %s in a secure way. '
                msg += 'Please install python-m2crypto.'
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
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(conf.cookiejar),
                                          authhandler,
                                          urllib2.ProxyHandler(urllib.getproxies_environment()))
        opener.addheaders = [('User-agent', 'osc/%s' % __version__)]
        self.last_opener = (apiurl, opener, threading.currentThread().getName())
        return opener

    def urljoin(self, scheme, apisrv):
        return '://'.join([scheme, apisrv])

    def initPackage(self, apiUrl, project, package, directory):
        """Initialize an OSC working copy for `package` in `directory`"""
        return core.Package.init_package(apiUrl, project, package, directory)


__myObsLightOsc = ObsLightOsc()

def getObsLightOsc():
    return __myObsLightOsc


if __name__ == '__main__':
    pass
