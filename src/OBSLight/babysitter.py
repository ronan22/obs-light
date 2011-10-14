# Copyright (C) 2008 Novell Inc.  All rights reserved.
# This program is free software; it may be used, copied, modified
# and distributed under the terms of the GNU General Public Licence,
# either version 2, or (at your option) any later version.

import sys
import signal


<<<<<<< HEAD


from OBSLight import obslighterr


def catchterm(*args):
    raise obslighterr.SignalInterrupt
=======
from OBSLight import ObsLightErr


def catchterm(*args):
    raise ObsLightErr.SignalInterrupt
>>>>>>> 0f14dab9ce584c8b24463b4d79e1cbba05d90668

for name in 'SIGBREAK', 'SIGHUP', 'SIGTERM':
    num = getattr(signal, name, None)
    if num: signal.signal(num, catchterm)

def run(prg):
    try:
        try:
            return prg()
        except:
            raise

<<<<<<< HEAD
    except obslighterr.SignalInterrupt:
=======
    except ObsLightErr.SignalInterrupt:
>>>>>>> 0f14dab9ce584c8b24463b4d79e1cbba05d90668
        print >>sys.stderr, 'killed!'
        return 1

    except KeyboardInterrupt:
        print >>sys.stderr, 'interrupted!'
        return 1
    
<<<<<<< HEAD
    except obslighterr.ArgError,e:
        print >>sys.stderr, ' Arg Stop:', e.msg
        return 1
    
    except obslighterr.ManagerError,e:
        print >>sys.stderr, ' Manager Stop:', e.msg
        return 1
    
    except obslighterr.OBSLightProjectsError,e:
        print >>sys.stderr, ' Projects Stop:', e.msg
        return 1
    
    #added by Gustav
    except obslighterr.XMLExistenceError,e:
        print >>sys.stderr, ' XML Existence Error: ', e.msg
        return 1
    
    #added by Gustav
    except obslighterr.XMLEmptyFileError,e:
        print >>sys.stderr, ' XML Empty File: ', e.msg
        return 1
    
    #added by Gustav
    except obslighterr.XMLParseFileError,e:
        print >>sys.stderr, ' XML Parse File: ', e.msg
        return 1
    
    #added by Gustav
    except obslighterr.XMLDictToXMLError,e:
        print >>sys.stderr, ' XML conversion Dict to XML: ', e.msg
        return 1
        
    #added by Gustav
    except obslighterr.XMLModDictError,e:
        print >>sys.stderr, ' Modification of a dictionary: ', e.msg
        return 1
    
    #added by Gustav
    except obslighterr.UpDateRepositoryError,e:
        print >>sys.stderr, ' Update of a Repository: ', e.msg
        return 1
        
        
    
=======
    except ObsLightErr.ArgError,e:
        print >>sys.stderr, ' Arg Stop:', e.msg
        return 1
    
    except ObsLightErr.ManagerError,e:
        print >>sys.stderr, ' Manager Stop:', e.msg
        return 1
    
    except ObsLightErr.OBSLightProjectsError,e:
        print >>sys.stderr, ' Projects Stop:', e.msg
        return 1
    

    except ObsLightErr.UpDateRepositoryError,e:
        print >>sys.stderr, ' Update of a Repository: ', e.msg
        return 1
        
    except ObsLightErr.ObsLightObsServers,e:
        print >>sys.stderr, '', e.msg
        return 1
        
>>>>>>> 0f14dab9ce584c8b24463b4d79e1cbba05d90668
        


