#!/usr/bin/env python

import sys
import os
import locale

from ObsLight import ObsLightSubprocess

import signal
from ObsLight import ObsLightMic

def signal_handler(signal, frame):
    ObsLightSubprocess.BREAKPROCESS = True
    if (signal == 2):
        print >> sys.stderr, "user escape..."
    else:
        print >> sys.stderr, "kill process..."
    sys.exit(0)

from ObsLight.obslight_starter import exitIfRoot, exitIfAlreadyRunning, writePidFile
from ObsLight.obslight_starter import warnIfNotShutDownCorrectly

exitIfRoot()
exitIfAlreadyRunning()
warnIfNotShutDownCorrectly()
writePidFile()

try:
    signal.signal(signal.SIGINT, signal_handler)

    reload(sys)
    loc = locale.getdefaultlocale()[1]
    if not loc:
        loc = sys.getdefaultencoding()
    sys.setdefaultencoding(loc)
    del sys.setdefaultencoding

    from ObsLight import commandline
    from ObsLight import babysitter

    obslightcli = commandline.ObsLight()
    r = babysitter.run(obslightcli.main)

    sys.exit(r)
finally:
    import ObsLight.obslight_extinguisher
