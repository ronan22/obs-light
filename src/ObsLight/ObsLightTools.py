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

from urlparse import urlparse
import httplib
import urllib
import urllib2

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
            (schemeProxy, netlocProxy, pathProxy, paramsProxy, queryProxy, fragmentProxy) = urlparse(valProxy)
            [__PROXYHOST__, __PROXYPORT__] = netlocProxy.split(":")
            conn = httplib.HTTPConnection(host=__PROXYHOST__, port=__PROXYPORT__, timeout=SOCKETTIMEOUT)
            conn.set_tunnel(host=host, port=int(port))

            ctx = SSL.Context()
            ctx.set_allow_unknown_ca(True)
            ctx.set_verify(SSL.verify_none, 1)
            conn = M2Crypto.httpslib.ProxyHTTPSConnection(host=__PROXYHOST__, port=__PROXYPORT__)
            conn.ssl_ctx = ctx
            conn.putrequest('HEAD', ":".join(host, port))
            return conn
        else:
            return httplib.HTTPSConnection(host=host, port=port, timeout=SOCKETTIMEOUT)
    else:
        if 'http' in urllib.getproxies_environment():
            valProxy = urllib.getproxies_environment()['http']
            (schemeProxy, netlocProxy, pathProxy, paramsProxy, queryProxy, fragmentProxy) = urlparse(valProxy)
            [__PROXYHOST__, __PROXYPORT__] = netlocProxy.split(":")
            return httplib.HTTPConnection(host=__PROXYHOST__, port=__PROXYPORT__, timeout=SOCKETTIMEOUT)
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

def testHost(host):
    '''
    
    '''
    (scheme, netloc, _path, _params, _query, _fragment) = urlparse(str(host))

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

    conn = createConn(host, port, scheme)

    try:
        conn.connect()
    except BaseException, e:
        ObsLightPrintManager.getLogger().debug("Test Host Fail on " + str(host) + " " + str(e))
        return False
    finally:
        conn.close()
    return True

def testUrl(url):
    '''
    
    '''
    opener = urllib2.build_opener(urllib2.ProxyHandler(urllib.getproxies_environment()))
    urllib2.install_opener(opener)
    try:
        test = urllib2.urlopen(url, timeout=SOCKETTIMEOUT)
        return True
    except urllib2.URLError, e:
        ObsLightPrintManager.getLogger().debug("Test url Fail on " + str(url) + " " + str(e))
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
    '''
    return True if the url is a repo.
    '''
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
            conn.request('HEAD', netloc + path + "/repodata/repomd.xml")
        else:
            conn.request('HEAD', netloc + path + "repodata/repomd.xml")
        response = conn.getresponse()
        return response.status == 200
    except BaseException:
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

    if len(urllib.getproxies_environment()) > 0:
        valProxy = urllib.getproxies_environment()['https']
        (schemeProxy, netlocProxy, pathProxy, paramsProxy, queryProxy, fragmentProxy) = urlparse(valProxy)
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

    if len(urllib.getproxies_environment()) > 0:
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

def isUserInGroup(group):
    """Check if user running this program is member of `group`"""
    userGroups = [grp.getgrgid(gid).gr_name for gid in os.getgroups()]
    return group in userGroups


if __name__ == '__main__':

    Url = "http://repo.pub.meego.com/home:/ronan:/OBS_Light/openSUSE_11.4"
    print "testUrlRepo", testUrlRepo(Url)

    Url = "https://api.meego.com"
    print "testUrl", testUrl(Url)
    print "testHost", testHost(Url)
#    print "importCert", importCert(Url)
