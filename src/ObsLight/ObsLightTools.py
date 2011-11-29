'''
Created on 17 nov. 2011

@author: ronan@fridu.net
'''

from urlparse import urlparse
import httplib

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
        return response.status == 200
    except BaseException:
        return False
    finally:
        test.close()

def isNonEmptyString(theString):
    return isinstance(theString, basestring) and len(theString) > 0

if __name__ == '__main__':
    Url = "http://stackoverflow.com/questions/2486145/python-check-if-url-to-jpg-exists2"
    print "testUrl", testUrl(Url)
    print "testHost", testHost(Url)

