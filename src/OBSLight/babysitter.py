# Copyright (C) 2008 Novell Inc.  All rights reserved.
# This program is free software; it may be used, copied, modified
# and distributed under the terms of the GNU General Public Licence,
# either version 2, or (at your option) any later version.

import sys
import signal




from OBSLight import obslighterr


def catchterm(*args):
    raise obslighterr.SignalInterrupt

for name in 'SIGBREAK', 'SIGHUP', 'SIGTERM':
    num = getattr(signal, name, None)
    if num: signal.signal(num, catchterm)

def run(prg):
    try:
        try:
            return prg()
        except:
            raise

    except obslighterr.SignalInterrupt:
        print >>sys.stderr, 'killed!'
        return 1

    except KeyboardInterrupt:
        print >>sys.stderr, 'interrupted!'
        return 1
    
    except obslighterr.ArgError,e:
        print >>sys.stderr, ' Arg Stop:', e.msg
        return 1
    
    except obslighterr.ManagerError,e:
        print >>sys.stderr, ' Manager Stop:', e.msg
        return 1
    
    except obslighterr.OBSLightProjectsError,e:
        print >>sys.stderr, ' Projects Stop:', e.msg
        return 1
    
    


