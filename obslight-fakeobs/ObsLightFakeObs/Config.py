#
# Copyright 2012, Intel Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
"""
Configuration manager for FakeOBS.

@author: Florent Vennetier
"""

import errno
import os
import ConfigParser

GLOBAL_CONFIG_INSTANCE = None

DEFAULT_CONFIG_PATH = "/etc/obslight-fakeobs.conf"
DEFAULT_CONFIG = {
	"fakeobs_root":     "/srv/obslight-fakeobs",
	"projects_dir":     "%(fakeobs_root)s/projects",
	"repositories_dir": "%(fakeobs_root)s/repositories",
	"rsync_dir":        "%(fakeobs_root)s/_rsync",
	"live_dir":	    "%(fakeobs_root)s/repositories/live",
}

class ObsLightFakeObsConfig(object):

    PackageDescriptionFile = "_directory"

    def __init__(self, configPath=DEFAULT_CONFIG_PATH):
        self._configPath = configPath
        self._configParser = None
        self.readConfig()

    @property
    def configPath(self):
        """Path to the configuration file"""
        return self._configPath

    @property
    def cp(self):
        """A reference to the internal ConfigParser"""
        return self._configParser

    def readConfig(self):
        """Load configuration from the file at `self.configPath`."""
        self._configParser = ConfigParser.SafeConfigParser(DEFAULT_CONFIG)
        if len(self._configParser.read(self.configPath)) < 1:
            err = IOError(errno.ENOENT,
                          "Configuration file does not exist or is not readable",
                          self.configPath)
            err.fakeobs_config_error = True
            raise err

    def getFakeObsRootDir(self):
        return self.cp.get("Paths", "fakeobs_root")

    def getProjectsRootDir(self):
        return self.cp.get("Paths", "projects_dir")

    def getProjectDir(self, project):
        return os.path.join(self.cp.get("Paths", "projects_dir"), project)

    def getProjectRepositoryDir(self, project):
        return os.path.join(self.cp.get("Paths", "repositories_dir"),
                            project.replace(":", ":/"))

    def getProjectLiveDir(self, project):
        return os.path.join(self.cp.get("Paths", "live_dir"),
                            project.replace(":", ":/"))

    def getProjectPackagesDir(self, project):
        return os.path.join(self.cp.get("Paths", "projects_dir"),
                            project, "packages")

    def getProjectFullDir(self, project):
        return os.path.join(self.cp.get("Paths", "projects_dir"),
                            project, ":full")

    def getProjectInfoPath(self, project):
        return os.path.join(self.getProjectDir(project), "project_info")

    def getRsyncPath(self):
        return self.cp.get("Paths", "rsync_dir")

    def getIntLimit(self, whatLimit, default=None):
        """Get an integer property from the 'Limits' section."""
        try:
            return self.cp.getint("Limits", whatLimit)
        except ConfigParser.NoOptionError:
            return default

    def getPort(self, whatPort, default=0):
        """Get an integer property from the 'Ports' section."""
        try:
            return self.cp.getint("Ports", whatPort)
        except ConfigParser.NoOptionError:
            return default

    def getPath(self, whatPath, default=None, vars={}):
        """Get a property from the 'Paths' section."""
        try:
            return self.cp.get("Paths", whatPath, vars=vars)
        except ConfigParser.NoOptionError:
            return default

    def getCommand(self, command, default=None, vars={}):
        """Get a property from the 'Commands' section."""
        try:
            return self.cp.get("Commands", command, vars=vars)
        except ConfigParser.NoOptionError:
            return default

    def getFakeObsApiUrl(self):
        return "http://localhost:%s/public" % self.getPort("api_port", 8001)

    def getLastEventsFilePath(self):
        return os.path.join(self.getFakeObsRootDir(), "lastevents")


def loadConfig(path=DEFAULT_CONFIG_PATH):
    global GLOBAL_CONFIG_INSTANCE
    GLOBAL_CONFIG_INSTANCE = ObsLightFakeObsConfig(path)

def getConfig():
    return GLOBAL_CONFIG_INSTANCE
