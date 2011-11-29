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
Created on 3 oct. 2011

@author: ronan@fridu.net
'''

import os
from xml.etree import ElementTree
import urlparse

from osc import conf
from osc import core

from ObsLightSubprocess import SubprocessCrt
import ObsLightPrintManager
EMPTYPROJECTPATH = os.path.join(os.path.dirname(__file__), "emptySpec")

import urllib2
import M2Crypto

TIMEOUT = 1

class ObsLightOsc(object):
    '''
    ObsLightOsc interact with osc, when possible, do it directly by python API
    '''
    def __init__(self):
        '''
        init 
        '''
        self.__confFile = os.path.join(os.environ['HOME'], ".oscrc")
        self.__mySubprocessCrt = SubprocessCrt()

        if os.path.isfile(self.__confFile):
            conf.get_config()

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

    def changeUser(self, api, user):
        '''
        
        '''
        conf.get_config()
        aOscConfigParser = conf.get_configParser(self.__confFile, force_read=True)

        aOscConfigParser.set(api, 'user', user)

        aFile = open(self.__confFile, 'w')
        aOscConfigParser.write(aFile, True)

    def changePassw(self, api, passw):
        '''
        
        '''
        conf.get_config()
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
        conf.get_config()
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
        conf.get_config()
        aOscConfigParser = conf.get_configParser(self.__confFile, force_read=True)

        if aOscConfigParser.has_option(api, "trusted_prj"):
            options = aOscConfigParser.get(api, "trusted_prj")
        else:
            options = ""

        res = options
        ObsLightPrintManager.getLogger().debug("To Add ?" + ("").join(listDepProject))
        ObsLightPrintManager.getLogger().debug("Current:" + ("").join(res))
        for depProject in listDepProject:
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
        conf.get_config()
        url = self.__cleanUrl(str(apiurl + "/source/" + projet + "/_meta"))

        try:
            res = core.http_request("GET", url, timeout=TIMEOUT)
        except urllib2.URLError:
            ObsLightPrintManager.obsLightPrint("apiurl " + str(apiurl) + " is not reachable")
            return None
        except M2Crypto.SSL.SSLError:
            ObsLightPrintManager.obsLightPrint("apiurl " + str(apiurl) + " Connection reset by peer")
            return None

        aElement = ElementTree.fromstring(res.read())

        result = []
        for project in aElement:
            if (project.tag == "repository") and (project.get("name") == repos):
                for path in project.getiterator():
                    if path.tag == "path":
                        result.append(path.get("project"))

        return result

    def getListPackage(self,
                       obsServer=None,
                       projectLocalName=None):
        '''
            return the list of a projectLocalName
        '''
        list_package = core.meta_get_packagelist(str(obsServer), str(projectLocalName))
        return list_package

    def getFilesListPackage(self,
                            apiurl=None,
                            projectObsName=None,
                            package=None):
        '''
        
        '''
        url = self.__cleanUrl(str(apiurl + "/source/" + projectObsName + "/" + package))
        try:
            res = core.http_request("GET", url)
        except urllib2.URLError:
            ObsLightPrintManager.obsLightPrint("apiurl " + str(apiurl) + " is not reachable")
            return None

        aElement = ElementTree.fromstring(res.read())

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
        self.__subprocess(command=command)


    def __subprocess(self, command=None, waitMess=False):
        '''
        
        '''
        return self.__mySubprocessCrt.execSubprocess(command=command,
                                                     waitMess=waitMess)


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
        url = self.__cleanUrl(str(obsServer + "/build/" + project + "/" + repo + "/" + arch + "/" + package + "/_status"))


        try:
            res = core.http_request("GET", url, timeout=TIMEOUT)
        except urllib2.URLError:
            ObsLightPrintManager.obsLightPrint("apiurl " + str(obsServer) + " is not reachable")
            return None

        fileXML = res.read()

        aElement = ElementTree.fromstring(fileXML)
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
                                    "strace",
                                    "iputils",
                                    "ncurses-devel",
                                    "rpm",
                                    ],
                     ):
        '''
        create a chroot
        TODO: create chroot without build a package
        TODO: Build without a subprocess
        '''
        os.chdir(EMPTYPROJECTPATH)

        extraPkgs = ""
        for pkg in listExtraPkgs:
            extraPkgs += "-x " + pkg + " "

        command = "osc -A " + apiurl + " build --root=" + chrootDir + " " + extraPkgs + " --noservice --no-verify --alternative-project " + project + " " + repos + " " + arch + " --local-package"
        return self.__subprocess(command=command, waitMess=True)


    def getLocalProjectList(self, obsServer=None):
        '''
        return a list of the project of a OBS Server.
        '''
        conf.get_config()
        try:
            res = core.meta_get_project_list(str(obsServer))
        except Exception, e:
            ObsLightPrintManager.obsLightPrint("WARNING: Error obsServer:" + str(obsServer))
            raise e
        return res

    def getListRepos(self, apiurl):
        '''
        return the list of the repos of a OBS Server.
        '''
        url = self.__cleanUrl(str(apiurl + "/distributions"))
        aElement = ElementTree.fromstring(core.http_request("GET", url, timeout=TIMEOUT).read())

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
        url = self.__cleanUrl(str(obsServer + "/build/" + projectObsName))

        try:
            res = core.http_request("GET", url, timeout=TIMEOUT)
        except Exception, e:
            ObsLightPrintManager.getLogger().debug("Errot on: " + url)
            raise e
        aElement = ElementTree.fromstring(res.read())
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
        url = self.__cleanUrl(str(obsServer + "/build/" + projectObsName + "/" + projectTarget))

        aElement = ElementTree.fromstring(core.http_request("GET", url, timeout=TIMEOUT).read())
        res = []
        for directory in aElement:
            for entry in directory.getiterator():
                res.append(entry.get("name"))
        return res

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

    def remove(self, path, file):
        '''
        Mark files or package directories to be deleted upon
        '''
        os.chdir(path)
        command = "osc del " + file
        self.__subprocess(command=command)

    def add(self, path, file):
        '''
        Mark files to be added upon the next commit
        '''
        os.chdir(path)
        command = "osc add " + file
        self.__subprocess(command=command)

    def getProjectParameter(self, projectObsName, apiurl, parameter):
        '''
        Return the value of the projectObsName.
        valid parameter:
        title
        description
        '''
        conf.get_config()
        url = self.__cleanUrl(str(apiurl + "/source/" + projectObsName + "/_meta"))

        aElement = ElementTree.fromstring(core.http_request("GET", url, timeout=TIMEOUT).read())
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
        conf.get_config()
        url = self.__cleanUrl(str(apiurl + "/source/" + projectObsName + "/_meta"))

        aElement = ElementTree.fromstring(core.http_request("GET", url, timeout=TIMEOUT).read())

        for desc in aElement:
            if desc.tag == parameter:
                desc.text = value

        core.http_request("PUT", url, data=ElementTree.tostring(aElement), timeout=TIMEOUT)

    def getPackageParameter(self, projectObsName, package, apiurl, parameter):
        '''
        Return the value of the package of the projectObsName.
        valid parameter:
        title
        description
        '''
        conf.get_config()
        url = self.__cleanUrl(str(apiurl + "/source/" + projectObsName + "/" + package + "/_meta"))

        aElement = ElementTree.fromstring(core.http_request("GET", url, timeout=TIMEOUT).read())
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
        conf.get_config()
        url = self.__cleanUrl(str(apiurl + "/source/" + projectObsName + "/" + package + "/_meta"))

        aElement = ElementTree.fromstring(core.http_request("GET", url, timeout=TIMEOUT).read())

        for desc in aElement:
            if desc.tag == parameter:
                desc.text = value

        core.http_request("PUT", url, data=ElementTree.tostring(aElement), timeout=TIMEOUT)

__myObsLightOsc = ObsLightOsc()

def getObsLightOsc():
    '''
    
    '''
    return __myObsLightOsc


if __name__ == '__main__':
    projet = "MeeGo:1.2.0:oss"
    package = "kernel"
    apiurl = "http://128.224.218.244:81"
    print getObsLightOsc().getFilesListPackage(apiurl=apiurl,
                                               projectObsName=projet,
                                               package=package)

