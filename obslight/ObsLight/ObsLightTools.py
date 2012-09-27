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
Created on 17 nov. 2011

@author: Ronan Le Martret
@author: Florent Vennetier
'''
import ObsLightPrintManager
import md5
from urlparse import urlparse
import httplib
import urllib
import urllib2
import re
import traceback
import time
import sys
import tempfile
import ConfigParser

from subprocess import call
import ObsLightConfig
import ObsLightErr
import ObsLightPrintManager
import M2Crypto
from M2Crypto import SSL
from os.path import expanduser, exists
from os import makedirs

import threading
import grp
import os

SOCKETTIMEOUT = 20

def createConn(host, port, scheme):
    if scheme == "https":
        if 'https' in urllib.getproxies_environment():
            proxies_env = urllib.getproxies_environment()
            if 'https' in proxies_env.keys():
                valProxy = ['https']
            else:
                valProxy = ['http']
            netlocProxy = urlparse(valProxy)[2]
            [__PROXYHOST__, __PROXYPORT__] = netlocProxy.split(":")
            conn = httplib.HTTPConnection(host=__PROXYHOST__,
                                          port=__PROXYPORT__,
                                          timeout=SOCKETTIMEOUT)
            conn.set_tunnel(host=host, port=int(port))

            ctx = SSL.Context()
            ctx.set_allow_unknown_ca(True)
            ctx.set_verify(SSL.verify_none, 1)
            conn = M2Crypto.httpslib.ProxyHTTPSConnection(host=__PROXYHOST__, port=__PROXYPORT__)
            conn.ssl_ctx = ctx
            conn.putrequest('HEAD', scheme + "://" + ":".join(host, port))
            return conn
        else:
            return httplib.HTTPSConnection(host=host, port=port, timeout=SOCKETTIMEOUT)
    else:
        if 'http' in urllib.getproxies_environment():
            valProxy = urllib.getproxies_environment()['http']
            netlocProxy = urlparse(valProxy)[2]
            [__PROXYHOST__, __PROXYPORT__] = netlocProxy.split(":")
            return httplib.HTTPConnection(host=__PROXYHOST__,
                                          port=__PROXYPORT__,
                                          timeout=SOCKETTIMEOUT)
        else:
            return httplib.HTTPConnection(host=host, port=port, timeout=SOCKETTIMEOUT)

def getUrl(scheme, netloc, path):

    if len(urllib.getproxies_environment()) > 0:
        if path == "":
            return scheme + "://" + netloc + "/"
        else:
            return scheme + "://" + netloc + path
    else:
        return path

def testHost(url):
    '''
    Test if we can connect to the host of `url` (not to the complete URL).
    '''
    (scheme, netloc, _path, _params, _query, _fragment) = urlparse(str(url))

    if len(urllib.getproxies_environment()) > 0:
        return testUrl(scheme + "://" + netloc)

    if ":" in netloc:
        (host, port) = netloc.split(":")
    else:
        host = netloc
        if scheme == "https":
            port = "443"
        else:
            port = "80"

    logger = ObsLightPrintManager.getLogger()
    logger.info("Testing connection to '%s:%s'", host, port)
    conn = createConn(host, port, scheme)

    try:
        conn.connect()
    except BaseException, e:
        message = "Could not connect to %s: %s" % (str(host), str(e))
        logger.warning(message)
        return False
    finally:
        conn.close()
    return True

def testUrl(url):
    '''
    Test if we can reach `url`.
    '''
    logger = ObsLightPrintManager.getLogger()
    logger.info("Testing URL '%s'", url)
    opener = urllib2.build_opener(urllib2.ProxyHandler(urllib.getproxies_environment()))
    urllib2.install_opener(opener)
    try:
        _test = urllib2.urlopen(url, timeout=SOCKETTIMEOUT)
        return True
    except urllib2.URLError, e:
        message = "Could not reach %s: %s" % (str(url), str(e))
        logger.warning(message)
        return False
    return True


def testRepo(url, name):
    '''
    return url,name
    If url is a repo file (*.repo), the file is download,
    parse and return url and name of the repo directory.
    "%3a" is replace by ":" into the url.
    '''
    url = url.replace("%3a", ":")
    if url.endswith(".repo"):
        (scheme, netloc, path, _params, _query, _fragment) = urlparse(str(url))
        if ":" in netloc:
            (host, port) = netloc.split(":")
        else:
            host = netloc
            if scheme == "https":
                port = "443"
            else:
                port = "80"

        conn = createConn(host, port, scheme)

        try:
            aUrl = getUrl(scheme, netloc, path)

            conn.request('HEAD', aUrl)

            response = conn.getresponse()
            afile = response.read()
            tmpName = None
            tmpBaseUrl = None
            for line in afile.split("\n"):
                if line.startswith("name="):
                    tmpName = line[line.index("=") + 1:]
                elif line.startswith("baseurl="):
                    tmpBaseUrl = line[line.index("=") + 1:]
            return tmpBaseUrl, tmpName
        except BaseException:
            return None, None
    return url, name

def testUrlRepo(url):
    return testRepositoryUrl(url)

def testRepositoryUrl(url):
    '''
    Return True if `url` is a package repository.
    '''
    logger = ObsLightPrintManager.getLogger()
    logger.info("Testing if '%s' is a package repository", url)
    (scheme, netloc, path, _params, _query, _fragment) = urlparse(str(url))
    if ":" in netloc:
        (host, port) = netloc.split(":")
    else:
        host = netloc
        if scheme == "https":
            port = "443"
        else:
            port = "80"
    conn = createConn(host, port, scheme)
    try:
        if not path.endswith("/"):
            repomdUrl = path + "/repodata/repomd.xml"
        else:
            repomdUrl = path + "repodata/repomd.xml"
        logger.debug("Calling %s" % repomdUrl)
        conn.request('HEAD', repomdUrl)
        response = conn.getresponse()
        logger.debug("Response status: %d" % response.status)
        return response.status == 200
    except BaseException:
        logger.warning("Error while connecting to '%s'", url)
        return False
    finally:
        conn.close()

def importCert(url):
    '''
    Import the SSL certificate of an HTTPS server into osc configuration.
    '''
    (scheme, netloc, _path, _params, _query, _fragment) = urlparse(str(url))
    if scheme == "http":
        return
    if ":" in netloc:
        (host, port) = netloc.split(":")
        port = int(port)
    else:
        host = netloc
        port = 443

    ctx = SSL.Context()
    ctx.set_allow_unknown_ca(True)
    ctx.set_verify(SSL.verify_none, 1)

    proxyEnv = urllib.getproxies_environment()
    # If there is a proxy environment and the host is not in no_proxy
    useProxy = len(proxyEnv) > 0 and host not in proxyEnv.get('no', [])

    if useProxy:
        valProxy = proxyEnv['https']
        netlocProxy = urlparse(valProxy)[1]
        [__PROXYHOST__, __PROXYPORT__] = netlocProxy.split(":")
        conn = M2Crypto.httpslib.ProxyHTTPSConnection(host=__PROXYHOST__, port=__PROXYPORT__)
        conn.ssl_ctx = ctx
        conn.putrequest('HEAD', url)
        try:
            conn.connect()
        except:
            raise

    else:
        conn = SSL.Connection(ctx)
        conn.postConnectionCheck = None
        timeout = SSL.timeout(SOCKETTIMEOUT)
        conn.set_socket_read_timeout(timeout)
        conn.set_socket_write_timeout(timeout)
        try:
            conn.connect((host, port))
        except:
            raise

    if useProxy:
        cert = conn.sock.get_peer_cert()
    else:
        cert = conn.get_peer_cert()

    # if the peer did not provide a certificate chain, cert is None.
    if cert is not None:
        dirpath = expanduser('~/.config/osc/trusted-certs')
        if not exists(dirpath):
            makedirs(dirpath)
        filePath = dirpath + '/%s_%d.pem' % (host, port)
        cert.save_pem(filePath)
    conn.close()

def openFileWithDefaultProgram(filePath):
    logger = ObsLightPrintManager.getLogger()
    openCommand = ObsLightConfig.getOpenFileCommand()
    if openCommand is None:
        message = u"No 'openFile' command configured."
        raise ObsLightErr.ConfigurationError(message)
    logger.info(u"Opening %s", filePath)
    logger.debug(u"Running command: '%s %s'", openCommand, filePath)
    try:
        retVal = call([openCommand, filePath])
        return retVal
    except BaseException:
        logger.error("Failed to run '%s %s'", openCommand, filePath, exc_info=True)
        raise

class procedureWithThreads(threading.Thread):
    def __init__(self, packagePath, procedure, sem, lock, errList, progress=None):
        '''
        
        '''
        threading.Thread.__init__(self)
        self.__procedure = procedure
        self.__packagePath = packagePath
        self.__sem = sem
        self.__errList = errList
        self.__progress = progress
        self.__lock = lock

    def run(self):
        '''
        
        '''
        self.__sem.acquire()
        try:
            res = 0
            res = self.__procedure(self.__packagePath)
        finally:
            if  res != 0:
                self.__lock.acquire()
                self.__errList.append(self.__packagePath)
                self.__lock.release()
            self.__sem.release()

            if self.__progress != None:
                self.__lock.acquire()
                self.__progress()
                self.__lock.release()
        return self.__errList

def mapProcedureWithThreads(parameterList, procedure, progress=None):
    errList = []
    res = []
    maxThreads = ObsLightConfig.getMaxNbThread()
    if maxThreads > 0:
        sem = threading.BoundedSemaphore(value=maxThreads)
        aLock = threading.Lock()
        for p in parameterList:
            athread = procedureWithThreads(packagePath=p,
                                           procedure=procedure,
                                           sem=sem,
                                           lock=aLock,
                                           errList=errList,
                                           progress=progress)
            athread.start()
            res.append(athread)
        for th in res:
            th.join()
    else:
        for parameter in parameterList:
            retVal = procedure(parameter)
            if  retVal != 0:
                errList.append(parameter)
            if progress != None:
                progress()
    return errList


def fileIsArchive(fileName, tarArchive=False):
    archiveFileExtensions = [".tar",
                             ".tar.gz",
                             ".tar.bz2",
                             ".tgz",
                             ".tbz",
                             ".tz2",
                             ".tar.xz"]
    if not tarArchive:
        archiveFileExtensions += [".xz", ".zip", ".gz", ".bz2"]

    for ext in archiveFileExtensions:
        if fileName.endswith(ext):
            return True
    return False

def isUserInGroup(group):
    """Check if user running this program is member of `group`"""
    userGroups = [grp.getgrgid(gid).gr_name for gid in os.getgroups()]
    return group in userGroups

def removeShortOption(line, option):
    """
    Remove one-letter option `option` from `line`.
    Returns a new string.

    For example
        removeShortOption("%setup -qcT", "c")
    will return
        "%setup -qT"

    Warning: if there are several `option` in a group of options,
    it will be removed only once ("-qccT" -> "-qcT").
    """
    # remove option if it's alone or at end of line
    line = re.sub(r"[\s]-%s($|[\s])" % option, r"\1", line)
    # remove option if it's in a group of options like "-qcT"
    line = re.sub(r"([\s]-[\w]*)%s([\w]*)" % option, r"\1\2", line)
    return line

def dumpError(exceptionType, message, traceback_):
    timeString = time.strftime("%Y-%m-%d_%Hh%Mm") + str(time.time() % 1).split(".")[1]

    message2Dump = message
    if traceback_ is not None:
        message2Dump += "\n\n" + "".join(traceback.format_tb(traceback_))

    typeName = re.findall(".*\'(.*)\'.*", str(exceptionType))
    if len(typeName) == 1:
        exceptionType = typeName[0]

    logfile = "%s-%s.log" % (timeString, exceptionType)
    if not os.path.isdir(ObsLightConfig.ERRORLOGDIRECTORY):
        os.makedirs(ObsLightConfig.ERRORLOGDIRECTORY)
    logPath = os.path.join(ObsLightConfig.ERRORLOGDIRECTORY, logfile)

    try:
        message2Dump = unicode(message2Dump)
    except UnicodeError:
        message2Dump = unicode(str(message2Dump), errors="replace")

    with open(logPath, 'w') as f:
        print >> f, message2Dump.encode('utf-8')

    if (ObsLightConfig.getObslightLoggerLevel() == "DEBUG"):
        print >> sys.stderr, exceptionType, message2Dump
    else:
        message += "\n\nlogPath: " + logPath
        print >> sys.stderr, exceptionType, message
    return logPath

def getRepoFromGbsProjectConf(path):
    configParser = ConfigParser.ConfigParser()
    configFile = open(path, 'r')
    configParser.readfp(configFile)
    configFile.close()

    repoDict = {}
    profileDict = {}
    result = {}
    general = None

    for section in configParser.sections():
        if section.startswith("profile."):
            if "repos" in configParser.options(section):
                listRepo = configParser.get(section, 'repos').replace(" ", "").split(",")
                if len(listRepo) > 0:
                    profileDict[section] = listRepo
        elif section.startswith("repo."):
            if "url" in configParser.options(section):
                repoDict[section] = configParser.get(section, 'url')

    if configParser.has_section('general'):
        if "profile" in configParser.options('general'):
            p = configParser.get('general', "profile")
            if p in profileDict.keys():
                profileDict['general'] = profileDict[p]

    for k in profileDict.keys():
        res = []
        for r in profileDict[k]:
            if r in repoDict.keys():
                res.append((r[len("repo."):], repoDict[r]))
        if len(res) > 0:
            result[k] = res

    return result

def createGbsProjectConfig(destDir, projectName, repoList):
    if len(repoList) == 0:
        return None
    gbsProjectConfigFilePath = os.path.join(destDir, ".gbs.conf")
    configFile = open(gbsProjectConfigFilePath, 'w')
    configParser = ConfigParser.ConfigParser()

    profileName = "profile." + projectName
    rNameList = []
    for rName, rUrl in repoList:
        rName = "repo." + rName
        rNameList.append(rName)
        configParser.add_section(rName)
        configParser.set(rName, "url", rUrl)

    configParser.add_section("general")
    configParser.set("general", "profile", profileName)

    configParser.add_section(profileName)
    configParser.set(profileName, "repos", ", ".join(rNameList))

    configParser.write(configFile)
    configFile.close()

    return gbsProjectConfigFilePath


def getRpmPathDict(rpmListFilePath):
    f = open(rpmListFilePath, 'r')
    resultDep = {}
    resultDepRPMid = []
    preinstallRes = None
    vminstallRes = None
    cbpreinstallRes = None
    cbinstallRes = None
    runscriptsRes = None
    distRes = None

    for line in f:
        if line.startswith("preinstall"):
            preinstallRes = line
            preinstallList = preinstallRes[len("preinstall:"):].split()
        elif line.startswith("vminstall"):
            vminstallRes = line
            vminstallList = vminstallRes[len("vminstall:"):].split()
        elif line.startswith("cbpreinstall"):
            cbpreinstallRes = line
            cbpreinstallList = cbpreinstallRes[len("cbpreinstall:"):].split()
        elif line.startswith("cbinstall"):
            cbinstallRes = line
            cbinstallList = cbinstallRes[len("cbinstall:"):].split()
        elif line.startswith("runscripts"):
            runscriptsRes = line
            runscriptsList = runscriptsRes[len("runscripts:"):].split()
        elif line.startswith("dist"):
            distRes = line
        elif line.startswith("rpmid"):
            resultDepRPMid.append(line)
        else:
            rpmShortName, rpmPath = line.split()
            rpmName = os.path.basename(rpmPath)
            if rpmName.endswith(".rpm"):
                rpmName = rpmName[:-len(".rpm")]
            resultDep[rpmName] = rpmPath.replace("\n", "")
    f.close()
    return resultDep


def getGbsBuildRepo(path):
    f = open(path, 'r')


def getBuildConfigPathFromGbsConfig(projectTemplatePath):
    pass

if __name__ == '__main__':

#    Url = "http://repo.pub.meego.com/home:/ronan:/OBS_Light/openSUSE_11.4"
#    print "testUrlRepo", testUrlRepo(Url)
#
#    Url = "https://api.meego.com"
#    print "testUrl", testUrl(Url)
#    print "testHost", testHost(Url)
#    print "importCert", importCert(Url)

    print getRpmPathDict("/tmp/rpmlist.StF0Gh2")

def getHashRepo(url):
    m = md5.new()
    m.update(url)
    return m.hexdigest()

def getRepoCacheDirectory(url):
    return os.path.join("/var/cache/build", getHashRepo(url))




