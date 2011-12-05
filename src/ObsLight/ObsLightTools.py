'''
Created on 17 nov. 2011

@author: ronan@fridu.net
'''

from urlparse import urlparse
import httplib
import ObsLightOsc

SOCKETTIMEOUT = 1

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
    except BaseException:
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

def testApi(api, user, passwd):
    '''
    return 0 if the API,user and passwd is OK.
    return 1 if user and passwd  are wrong.
    return 2 if api is wrong.
    '''
    return ObsLightOsc.getObsLightOsc().testApi(api=api, user=user, passwd=passwd)

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

def isNonEmptyString(theString):
    return isinstance(theString, basestring) and len(theString) > 0

if __name__ == '__main__':
    Url = "http://repo.pub.meego.com/home:/ronan:/OBS_Light/openSUSE_11.4"
    print "testUrlRepo", testUrlRepo(Url)






