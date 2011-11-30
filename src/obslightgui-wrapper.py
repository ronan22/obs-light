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

# Check if another instance is running
from ObsLight.ObsLightManager import getWorkingDirectory
pidFilePath = os.path.join(getWorkingDirectory(), u"obslightgui.pid")
if os.path.exists(pidFilePath):
    print "Already running... PID file is %s" % pidFilePath
    sys.exit(1)
else:
    with open(pidFilePath, "w") as pidFile:
        pidFile.write(str(os.getpid()))

# Now we can load the GUI
from ObsLight import babysitter, ObsLightManager
from ObsLightGui.Gui import Gui

try:
    obsLightManager = ObsLightManager.getManager()
    gui = Gui(obsLightManager)
    sys.exit(babysitter.run(gui.main))
finally:
    os.remove(pidFilePath)
