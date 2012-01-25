#!/usr/bin/env python
import os
from ObsLight.ObsLightManager import getpidFilePath

os.remove(getpidFilePath())
