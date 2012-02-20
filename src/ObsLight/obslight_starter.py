import sys
import os

from ObsLight.ObsLightManager import getpidFilePath

def userIsRoot():
    return os.getegid() == 0

def alreadyRunning():
    pidFilePath = getpidFilePath()
    return os.path.exists(pidFilePath)

def exitIfRoot():
    if userIsRoot():
        print "Sorry, Can't run OBS Light as root."
        sys.exit(0)

def exitIfAlreadyRunning():
    if alreadyRunning():
        pidFilePath = getpidFilePath()
        print "Already running... PID file is %s" % pidFilePath
        sys.exit(1)

def writePidFile():
    with open(getpidFilePath(), "w") as pidFile:
        pidFile.write(str(os.getpid()))
