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
