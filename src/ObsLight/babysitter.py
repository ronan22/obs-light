# Copyright (C) 2008 Novell Inc.  All rights reserved.
# This program is free software; it may be used, copied, modified
# and distributed under the terms of the GNU General Public Licence,
# either version 2, or (at your option) any later version.

import sys
import signal


from ObsLight import ObsLightErr
from mic import imgcreate

def catchterm(*args):
    raise ObsLightErr.SignalInterrupt

for name in 'SIGBREAK', 'SIGHUP', 'SIGTERM':
    num = getattr(signal, name, None)
    if num: signal.signal(num, catchterm)

def run(prg):
    try:
        try:
            return prg()
        except:
            raise

    except ObsLightErr.SignalInterrupt:
        print >> sys.stderr, 'killed!'
        return 1

    except KeyboardInterrupt:
        print >> sys.stderr, 'interrupted!'
        return 1
    
    except ObsLightErr.ArgError, e:
        print >> sys.stderr, 'Argument Error:', e.msg
        return 1
    
    except ObsLightErr.ManagerError, e:
        print >> sys.stderr, 'Manager Error:', e.msg
        return 1
    
    except ObsLightErr.ObsLightProjectsError, e:
        print >> sys.stderr, 'Projects Error:', e.msg
        return 1
    
    except ObsLightErr.ObsLightObsServers, e:
        print >> sys.stderr, 'OBS Error', e.msg
        return 1
        
    except ObsLightErr.ObsLightChRootError, e:
        print >> sys.stderr, 'Chroot Error', e.msg
        return 1
          
    except ObsLightErr.ObsLightSpec, e:
        print >> sys.stderr, 'Spec Error', e.msg
        return 1
          
    except imgcreate.CreatorError, e:
        print >> sys.stderr, 'Mic Error', e
        return 1
    
    except imgcreate.MountError, e:
        print >> sys.stderr, 'Mic Error', e
        return 1
    
    
    