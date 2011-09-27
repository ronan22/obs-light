#!/usr/bin/env python
'''
Created on 27 sept. 2011

@author: Florent Vennetier
'''

import sys

from OBSLight.OBSLightManager import OBSLightManager

from OBSLight import babysitter
from OBSLightGui.Gui import Gui

obsLightManager = OBSLightManager()
gui = Gui(obsLightManager)

sys.exit(babysitter.run(gui.main))
