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
Created on 17 nov. 2011

@author: Ronan Le Martret
@author: Florent Vennetier
'''

from urlparse import urlparse
import httplib
from subprocess import call
import ObsLightConfig
import ObsLightErr
import ObsLightPrintManager

from M2Crypto import SSL
from os.path import expanduser

import threading

SOCKETTIMEOUT = 20


def isNonEmptyString(theString):
    return isinstance(theString, basestring) and len(theString) > 0

def testHost(host):
    '''
    
    '''
    (scheme, netloc, _path, _params, _query, _fragment) = urlparse(str(host))
    if ":" in netloc:
        (host, port) = netloc.split(":")
    else:
        host = netloc
        if scheme == "https":
            port = "443"
        else:
            port = "80"

    test = httplib.HTTPConnection(host=host, port=port, timeout=SOCKETTIMEOUT)

    try:
        test.connect()
    except BaseException, e:
        print "Test Host Fail on ", host, " ", e
        return False
    finally:
        test.close()
    return True

def testUrl(url):
    '''
    
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
    test = httplib.HTTPConnection(host=host, port=port, timeout=SOCKETTIMEOUT)

    try:
        test.request('HEAD', path)
        response = test.getresponse()
        if response.status == 301 and not path.endswith("/"):
            test.close()
            test = httplib.HTTPConnection(host=host, port=port, timeout=SOCKETTIMEOUT)
            path = path + "/"
            test.request('HEAD', path)
            response = test.getresponse()
        return response.status == 200
    except BaseException:
        return False
    finally:
        test.close()



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
        test = httplib.HTTPConnection(host=host, port=port, timeout=SOCKETTIMEOUT)
        try:
            test.request('GET', path)
            response = test.getresponse()
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
    test = httplib.HTTPConnection(host=host, port=port, timeout=SOCKETTIMEOUT)
    try:
        if not path.endswith("/"):
            test.request('HEAD', path + "/repodata/repomd.xml")
        else:
            test.request('HEAD', path + "repodata/repomd.xml")
        response = test.getresponse()
        return response.status == 200
    except BaseException:
        return False
    finally:
        test.close()

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
    conn = SSL.Connection(ctx)
    conn.postConnectionCheck = None
    timeout = SSL.timeout(15)
    conn.set_socket_read_timeout(timeout)
    conn.set_socket_write_timeout(timeout)
    try:
        conn.connect((host, port))
    except:
        raise
    cert = conn.get_peer_cert()
    # if the peer did not provide a certificate chain, cert is None.
    if cert is not None:
        dirpath = expanduser('~/.config/osc/trusted-certs')
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
    sem = threading.BoundedSemaphore(value=ObsLightConfig.getMaxNbThread())
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
    return  errList


if __name__ == '__main__':

    Url = "http://repo.pub.meego.com/home:/ronan:/OBS_Light/openSUSE_11.4"
    print "testUrlRepo", testUrlRepo(Url)

    Url = "https://api.meego.com"
    print "testUrl", testUrl(Url)
    print "testHost", testHost(Url)
    print "importCert", importCert(Url)
