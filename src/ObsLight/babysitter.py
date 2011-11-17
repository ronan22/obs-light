# Copyright (C) 2008 Novell Inc.  All rights reserved.
# This program is free software; it may be used, copied, modified
# and distributed under the terms of the GNU General Public Licence,
# either version 2, or (at your option) any later version.

import sys
import signal


from ObsLight import ObsLightErr
from mic import imgcreate
from osc.oscerr import ConfigError

import urllib2

import ObsLightMic

def catchterm(*args):
    '''
    
    '''
    raise ObsLightErr.SignalInterrupt

for name in 'SIGBREAK', 'SIGHUP', 'SIGTERM':
    num = getattr(signal, name, None)
    if num:
        signal.signal(num, catchterm)

def run(prg=None):
    '''
     
    '''
    try:
        try:
            return prg()
        except:
            raise
        finally:
            try:
                ObsLightMic.destroy()
            except:
                raise

    except ObsLightErr.SignalInterrupt:
        print >> sys.stderr, 'killed!'
        return 1

    except KeyboardInterrupt:
        print >> sys.stderr, 'interrupted!'
        return 1

    except ObsLightErr.ArgError, err:
        print >> sys.stderr, 'Argument Error:', err.msg
        return 1

    except ObsLightErr.ManagerError, err:
        print >> sys.stderr, 'Manager Error:', err.msg
        return 1

    except ObsLightErr.ObsLightProjectsError, err:
        print >> sys.stderr, 'Projects Error:', err.msg
        return 1

    except ObsLightErr.ObsLightObsServers, err:
        print >> sys.stderr, 'OBS Error', err.msg
        return 1

    except ObsLightErr.ObsLightChRootError, err:
        print >> sys.stderr, 'Chroot Error', err.msg
        return 1

    except ObsLightErr.ObsLightSpec, err:
        print >> sys.stderr, 'Spec Error', err.msg
        return 1

    except imgcreate.MountError, err:
        print >> sys.stderr, 'Mic Error', err
        return 1

    except imgcreate.CreatorError, err:
        print >> sys.stderr, 'Mic Error', err
        return 1

    except ConfigError, err:
        print >> sys.stderr, 'Osc Error', err
        return 1

    except urllib2.URLError, err:
        print >> sys.stderr, 'Osc Error', err
        return 1



