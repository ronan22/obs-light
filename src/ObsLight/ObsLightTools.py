'''
Created on 17 nov. 2011

@author: ronan@fridu.net
'''

from urlparse import urlparse
import httplib
import ObsLightOsc

from M2Crypto import SSL
from os.path import expanduser

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

def importCert(url):
    (scheme, netloc, _path, _params, _query, _fragment) = urlparse(str(url))
    if ":" in netloc:
        (host, port) = netloc.split(":")
        port = int(port)
    else:
        host = netloc
        if scheme == "https":
            port = 443
        else:
            port = 80
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
    dirpath = expanduser('~/.config/osc/trusted-certs')
    filePath = dirpath + '/%s.pem' % host
    cert.save_pem(filePath)
    conn.close()

def isNonEmptyString(theString):
    return isinstance(theString, basestring) and len(theString) > 0

if __name__ == '__main__':
    Url = "https://api.meego.com"
    print "testUrl", testUrl(Url)
    print "testHost", testHost(Url)
    print "importCert", importCert(Url)
