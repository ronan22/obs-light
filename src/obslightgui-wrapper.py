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

from PySide.QtGui import QApplication, QMessageBox
from ObsLight.obslight_starter import alreadyRunning, userIsRoot, writePidFile, getpidFilePath

if userIsRoot():
    qa = QApplication(sys.argv)
    QMessageBox.critical(u"Cannot run as root", u"OBS Light cannot run as root!")
    sys.exit(0)

if alreadyRunning():
    qa = QApplication(sys.argv)
    pidFilePath = getpidFilePath()
    message = u"OBS Light is already running.\n"
    message += u"If it is not the case, please remove the file '%s' " % pidFilePath
    message += u"and retry."
    QMessageBox.warning(None, u"Already running", message)
    sys.exit(1)

writePidFile()

from ObsLight import babysitter, ObsLightManager
from ObsLightGui.Gui import Gui

try:
    # Now we can load the GUI
    gui = Gui()
    gui.loadManager(ObsLightManager.getManager)
    r = babysitter.run(gui.main)
    sys.exit(r)
finally:
    import ObsLight.obslight_extinguisher
