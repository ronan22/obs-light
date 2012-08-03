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
from ObsLight.obslight_starter import alreadyRunning, userIsRoot, writePidFile
from ObsLight.obslight_starter import getpidFilePath, getPidFromFile, wasStoppedCorrectly
from ObsLight.obslight_starter import shouldUpgradeMessage

# a QApplication instance is required in order to display message boxes
qApplication = QApplication(sys.argv)

if userIsRoot():
    QMessageBox.critical(u"Cannot run as root", u"OBS Light cannot run as root!")
    sys.exit(0)

if alreadyRunning():
    pid = getPidFromFile()
    message = u"OBS Light is already running (PID: %d).\n" % pid
    QMessageBox.warning(None, u"Already running", message)
    sys.exit(1)

if not wasStoppedCorrectly():
    message = u"It seems that OBS Light has not been shut down correctly.\n"
    message += u"Please close it and re-launch it so it can clean itself."
    QMessageBox.warning(None, u"Shutdown problem", message)

shouldUpgradeMsg = shouldUpgradeMessage()
if shouldUpgradeMsg is not None:
    QMessageBox.information(None, u"Upgrade recommended", shouldUpgradeMsg)

writePidFile()

from ObsLight import babysitter, ObsLightManager
from ObsLightGui.Gui import Gui

try:
    # Now we can load the GUI
    gui = Gui(qApplication)
    gui.loadManager(ObsLightManager.getManager)
    r = babysitter.run(gui.main)
    sys.exit(r)
finally:
    import ObsLight.obslight_extinguisher
