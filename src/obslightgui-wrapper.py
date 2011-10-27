#!/usr/bin/env python
'''
Created on 27 sept. 2011

@author: Florent Vennetier
'''

import sys

from ObsLight.ObsLightManager import ObsLightManager

from ObsLight import babysitter
from ObsLightGui.Gui import Gui

obsLightManager = ObsLightManager()
gui = Gui(obsLightManager)

sys.exit(babysitter.run(gui.main))
