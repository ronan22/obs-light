import sys
import os

# Check if another instance is running
from ObsLight.ObsLightManager import getWorkingDirectory

pidFilePath = os.path.join(getWorkingDirectory(), u"obslight.pid")
if os.path.exists(pidFilePath):
    print "Already running... PID file is %s" % pidFilePath
    sys.exit(1)
else:
    with open(pidFilePath, "w") as pidFile:
        pidFile.write(str(os.getpid()))
