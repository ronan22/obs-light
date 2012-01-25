#!/usr/bin/env python

# this wrapper exists so it can be put into /usr/bin, but still allows the
# python module to be called within the source directory during development

import sys
import os
import locale
# this is a hack to make osc work as expected with utf-8 characters,
# no matter how site.py is set...
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

import obslight_starter

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
    os.remove(pidFilePath)


