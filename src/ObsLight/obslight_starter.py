import sys
import os

from ObsLight.ObsLightManager import getpidFilePath

_wasStoppedCorrectly = True

def userIsRoot():
    return os.getegid() == 0

def getPidFromFile():
    """
    Return the PID of the currently running obslight or obslightgui instance.
    If none is running, return 0.
    """
    pidFilePath = getpidFilePath()
    if os.path.exists(pidFilePath):
        with open(pidFilePath, "r") as pidFile:
            strpid = pidFile.readline()
            pid = int(strpid)
            return pid
    else:
        return 0

def alreadyRunning():
    """
    Check if an obslight or obslightgui instance is running.
    Sets wasStoppedCorrectly().
    """
    pid = getPidFromFile()
    if pid == 0:
        return False
    try:
        os.getpgid(pid)
        return True
    except OSError:
        global _wasStoppedCorrectly
        _wasStoppedCorrectly = False
        return False
    return False

def wasStoppedCorrectly():
    """
    Check if the last obslight or obslightgui instance was stopped correctly.
    To be called after alreadyRunning().
    """
    return _wasStoppedCorrectly

def exitIfRoot():
    if userIsRoot():
        print "Sorry, Can't run OBS Light as root."
        sys.exit(0)

def exitIfAlreadyRunning():
    if alreadyRunning():
        pid = getPidFromFile()
        print "Already running... PID is %d" % pid
        sys.exit(1)

def warnIfNotShutDownCorrectly():
    if not wasStoppedCorrectly():
        print "WARNING: OBS Light has not been shut down correctly."

def writePidFile():
    with open(getpidFilePath(), "w") as pidFile:
        pidFile.write(str(os.getpid()))
