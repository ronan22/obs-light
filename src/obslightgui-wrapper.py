#!/usr/bin/env python
'''
Created on 27 sept. 2011

@author: Florent Vennetier
'''

import sys

from OBSLight import babysitter
from OBSLightGui import gui

sys.exit(babysitter.run(gui.main))
