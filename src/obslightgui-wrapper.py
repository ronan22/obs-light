#!/usr/bin/env python
'''
Created on 27 sept. 2011

@author: Florent Vennetier
'''

import sys

from ObsLight import babysitter, ObsLightManager
from ObsLightGui.Gui import Gui

obsLightManager = ObsLightManager.getManager()
gui = Gui(obsLightManager)

sys.exit(babysitter.run(gui.main))
