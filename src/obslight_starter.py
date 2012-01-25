import sys
import os

if os.getegid() == 0:
    print "Sorry, Can't run OBS Light as root."
    sys.exit(0)

# Check if another instance is running
from ObsLight.ObsLightManager import getpidFilePath
pidFilePath = getpidFilePath()
if os.path.exists(pidFilePath):
    print "Already running... PID file is %s" % pidFilePath
    sys.exit(1)
else:
    with open(getpidFilePath(), "w") as pidFile:
        pidFile.write(str(os.getpid()))


