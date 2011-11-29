'''
Created on 17 nov. 2011

@author: ronan@fridu.net
'''

from urlparse import urlparse
import httplib
import socket

SOCKETTIMEOUT = 1

def testHost(host):
    '''
    
    '''
    (scheme, netloc, path, params, query, fragment) = urlparse(str(host))
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
    except :
        return False
    return True

def testUrl(Url):
    '''
    
    '''
    (scheme, netloc, path, params, query, fragment) = urlparse(str(Url))
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
        test.close()
        return response.status == 200
    except :
        return False


def isNonEmptyString(theString):
    return isinstance(theString, basestring) and len(theString) > 0

if __name__ == '__main__':
    Url = "http://stackoverflow.com/questions/2486145/python-check-if-url-to-jpg-exists2"
    print "testUrl", testUrl(Url)
    print "testHost", testHost(Url)

