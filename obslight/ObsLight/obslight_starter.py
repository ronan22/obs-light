import sys
import os
from distutils.version import LooseVersion

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
        print >> sys.stderr, "Sorry, Can't run OBS Light as root."
        sys.exit(1)

def exitIfAlreadyRunning():
    if alreadyRunning():
        pid = getPidFromFile()
        print >> sys.stderr, "Already running... PID is %d" % pid
        sys.exit(1)

def warnIfNotShutDownCorrectly():
    if not wasStoppedCorrectly():
        print >> sys.stderr, "WARNING: OBS Light has not been shut down correctly."

def writePidFile():
    with open(getpidFilePath(), "w") as pidFile:
        pidFile.write(str(os.getpid()))

def getMicVersionString():
    try:
        from mic.__version__ import VERSION as MIC_VERSION
        return MIC_VERSION
    except ImportError:
        return "unknown"

def compareVersion(v1, v2):
    """
    Compare `v1` and `v2` as version strings.
      compareVersion("0.8", "0.8.4") ->  <0
      compareVersion("0.8", "0.8")   ->   0
      compareVersion("0.8.4", "0.8") ->  >0
    """
    v1_obj = LooseVersion(v1)
    v2_obj = LooseVersion(v2)
    return cmp(v1_obj, v2_obj)

def messageIfMicVersionLessThan_0_8_1():
    """
    Since Monday, 02 April 2012, MIC is not maintained in OBS Light
    repositories anymore. Latest maintained version is 0.8. This
    function returns a message if MIC version on the system is prior
    to 0.8.1. Returns None otherwise.
    """
    micVersion = getMicVersionString()
    if compareVersion(micVersion, "0.8.1") < 0:
        message = "WARNING: You have an old version of MIC (%s). " % micVersion
        message += "Consider upgrading to a newer version.\n"
	message += "See http://en.opensuse.org/openSUSE:OBS_Light_Installation#Migration_from_old_versions"
        message += " for more information."
        return message

def shouldUpgradeMessage():
    """
    Return a message if user should upgrade OBS Light
    or one of its dependencies. Return None otherwise.
    """
    msg = messageIfMicVersionLessThan_0_8_1()
    return msg
