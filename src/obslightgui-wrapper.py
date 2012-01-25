#!/usr/bin/env python
'''
Created on 27 sept. 2011

@author: Florent Vennetier
'''

import sys, os, os.path

# If we are launched with --version, just print version and exit
if "--version" in sys.argv:
    from ObsLight.ObsLightManager import getVersion
    print u"OBS Light GUI version %s" % getVersion()
    sys.exit(0)

from ObsLight import babysitter, ObsLightManager
from ObsLightGui.Gui import Gui

import obslight_starter

try:
    # Now we can load the GUI
    gui = Gui()
    gui.loadManager(ObsLightManager.getManager)
    sys.exit(babysitter.run(gui.main))
finally:
    os.remove(pidFilePath)
