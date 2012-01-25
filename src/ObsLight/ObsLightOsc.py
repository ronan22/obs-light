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

import threading

class ObsLightOsc(object):
    '''
    ObsLightOsc interact with osc, when possible, do it directly by python API
    '''
    def __init__(self):
        '''
        init 
        '''
        self.__confFile = os.path.join(os.environ['HOME'], ".oscrc")
        self.__mySubprocessCrt = ObsLightSubprocess.SubprocessCrt()

        self.__aLock = threading.Lock()

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
        '''
        
        '''
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

    def getDepProject(self,
                      apiurl=None,
                      projet=None,
                      repos=None):
        '''
        
        '''
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
                       obsServer=None,
                       projectLocalName=None):
        '''
            return the list of a projectLocalName
        '''
        try:
            list_package = core.meta_get_packagelist(str(obsServer), str(projectLocalName))
        except urllib2.URLError:
            ObsLightPrintManager.getLogger().error("apiurl " + str(obsServer) + " is not reachable 2")
            return None
        except M2Crypto.SSL.SSLError:
            ObsLightPrintManager.getLogger().error("apiurl " + str(obsServer) + " Connection reset by peer")
            return None
        except M2Crypto.SSL.Checker.NoCertificate:
            ObsLightPrintManager.getLogger().error("apiurl " + str(obsServer) + " Peer did not return certificate")
            return None

        return list_package

    def getFilesListPackage(self,
                            apiurl=None,
                            projectObsName=None,
                            package=None):
        '''
        
        '''
        url = str(apiurl + "/source/" + projectObsName + "/" + package)
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
        res = self.getHttp_request(url)
        if res == None:
            return res
        aElement = ElementTree.fromstring(res)

        #print "rev" , aElement.get("rev")
        #print "vrev" , aElement.get("vrev")
        #print "srcmd5" , aElement.get("srcmd5")

        return aElement.get("rev")

    def getOscPackageRev(self, workingdir):
        '''
        
        '''
        #Add a Lock
        self.__aLock.acquire()
        try:
            pk = core.Package(workingdir=workingdir)
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
                print "__subprocess ERROR."
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
        res = self.getHttp_request(url)
        if res == None:
            return None
        aElement = ElementTree.fromstring(res)

        return aElement.attrib["code"]

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


    def getLocalProjectList(self, obsServer=None):
        '''
        return a list of the project of a OBS Server.
        '''
        self.get_config()
        res = []
        try:
            res = core.meta_get_project_list(str(obsServer))
        except urllib2.URLError:
            ObsLightPrintManager.getLogger().error("apiurl " + str(obsServer) + " is not reachable 8")
        except M2Crypto.SSL.SSLError:
            ObsLightPrintManager.getLogger().error("apiurl " + str(obsServer) + " Connection reset by peer")
        except M2Crypto.SSL.Checker.NoCertificate:
            ObsLightPrintManager.getLogger().error("apiurl " + str(obsServer) + " Peer did not return certificate")
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
        self.get_config()
        url = str(apiurl + "/source/" + projectObsName + "/_meta")
        res = self.getHttp_request(url)
        if res == None:
            return None
        aElement = ElementTree.fromstring(res)

        for desc in aElement:
            if parameter == desc.tag:
                return desc.text

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

    def getPackageParameter(self, projectObsName, package, apiurl, parameter):
        '''
        Return the value of the package of the projectObsName.
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
            if parameter == desc.tag:
                return desc.text

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
        except urllib2.URLError:
            ObsLightPrintManager.getLogger().error("apiurl " + str(apiurl) + " is not reachable 15")
            return None
        except M2Crypto.SSL.SSLError:
            ObsLightPrintManager.getLogger().error("apiurl " + str(apiurl) + " Connection reset by peer")
            return None
        except M2Crypto.SSL.Checker.NoCertificate:
            ObsLightPrintManager.getLogger().error("apiurl " + str(apiurl) + " Peer did not return certificate")
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

        opener = urllib2.build_opener(auth_handler)
        # ...and install it globally so it can be used with urlopen.
        urllib2.install_opener(opener)
        try:
            if isinstance(urllib2.urlopen(api + url).read(), basestring):
                return 0
            else:
                return -1
        except urllib2.HTTPError:
            return 1
        except urllib2.URLError:
            return 2

    def repairOscPackageDirectory(self, path):
        '''
        
        '''
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
        '''
        
        '''
        try:
            pk = core.Package(workingdir=workingdir)
        except oscerr.WorkingCopyInconsistent, e:
            raise ObsLightErr.ObsLightOscErr("'" + workingdir + "' is a inconsistent working copy")
        return pk.get_status()

    def autoResolvedConflict(self, packagePath, aFile):
        '''
        
        '''
        os.chdir(packagePath)
        command = "osc resolved " + aFile
        self.__subprocess(command=command)

    def getHttp_request(self, url, headers={}, data=None, file=None):
        '''
        
        '''
        url = self.__cleanUrl(url)
        try:
            fileXML = ""
            count = 0
            while(fileXML == "" and count < 4):
                count += 1
                res = self.http_request(method="GET", url=url, headers=headers, data=data, file=file, timeout=TIMEOUT)
                fileXML = res.read()
            return fileXML
        except urllib2.URLError:
            ObsLightPrintManager.getLogger().error("apiurl " + str(url) + " is not reachable")
            return None
        except M2Crypto.SSL.SSLError:
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
                            data = mmap.mmap(filefd.fileno(), os.path.getsize(file), mmap.MAP_SHARED, mmap.PROT_READ)
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

        # workaround for http://bugs.python.org/issue9639
        authhandler_class = urllib2.HTTPBasicAuthHandler
        if sys.version_info >= (2, 6, 6) and sys.version_info < (2, 7, 1) \
            and not 'reset_retry_count' in dir(urllib2.HTTPBasicAuthHandler):
            print >> sys.stderr, 'warning: your urllib2 version seems to be broken. ' \
                'Using a workaround for http://bugs.python.org/issue9639'
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
                from osc import oscssl, oscsslexcp
                from M2Crypto import m2urllib2

            except ImportError, e:
                print e
                raise oscsslexcp.NoSecureSSLError('M2Crypto is needed to access %s in a secure way.\nPlease install python-m2crypto.' % apiurl)

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
            if ctx.load_verify_locations(capath=capath, cafile=cafile) != 1: raise Exception('No CA certificates found')
            opener = m2urllib2.build_opener(ctx, oscssl.myHTTPSHandler(ssl_context=ctx, appname='osc'), urllib2.HTTPCookieProcessor(conf.cookiejar), authhandler)
        else:
#            import sys
            #print >> sys.stderr, "WARNING: SSL certificate checks disabled. Connection is insecure!\n"
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(conf.cookiejar), authhandler)
        opener.addheaders = [('User-agent', 'osc/%s' % __version__)]
        self.last_opener = (apiurl, opener, threading.currentThread().getName())
        return opener

    def urljoin(self, scheme, apisrv):
        return '://'.join([scheme, apisrv])

__myObsLightOsc = ObsLightOsc()

def getObsLightOsc():
    '''
    
    '''
    #if __myObsLightOsc == None:
    #    __myObsLightOsc = ObsLightOsc()
    return __myObsLightOsc



if __name__ == '__main__':
#    val = '''<project name="home:obsuser:testRemoteLink">
#                <title>Remote OBS instance</title>
#                <description>This project is representing a remote build service instance.</description>
#                <person role="maintainer" userid="obsuser"/>
#                <person role="bugowner" userid="obsuser"/>
#            </project>'''
#
#    url = "http://128.224.218.244:81/source/testNewProjet/_meta"
#    res = getObsLightOsc().http_request('PUT', url, data=val)

#    url = "http://128.224.218.244:81/source/testNewProjet/zlib/_link"
#
#    val = '''<link project="MeeGo:1.2.0:oss" package="zlib"  >
#<patches>
#  <!-- <apply name="patch" /> apply a patch on the source directory  -->
#  <!-- <topadd>%define build_with_feature_x 1</topadd> add a line on the top (spec file only) -->
#  <!-- <add>file.patch</add> add a patch to be applied after %setup (spec file only) -->
#  <!-- <delete>filename</delete> delete a file -->
#</patches>
#</link>'''
#
#    res = getObsLightOsc().http_request('PUT', url, data=val)
#    print "------------------------------------------------------"
#    print res.read()


#    try:
#        url = "http://128.224.218.244:81/source/testNewProjet/zlib/_meta"
#        res = getObsLightOsc().http_request('GET', url)
#    finally:
#        print "toto"
#    print "------------------------------------------------------"
#    print res.read()

#    <remoteurl>https://api.meego.com/public</remoteurl>   
    val = '''<project name="home:obsuser:testRemoteLink">  
      <title>testRemoteLink</title>  
      <description>test</description>
      <remoteurl>https://api.meego.com/public</remoteurl>
      <person role="maintainer" userid="obsuser"/>  
      <person role="bugowner" userid="obsuser"/>  
    </project>'''

    url = "http://128.224.218.244:81/source/home:obsuser:testRemoteLink/_meta"
    res = getObsLightOsc().http_request('PUT', url, data=val)






