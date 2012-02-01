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
Created on 1 Feb 2012

@author: Florent Vennetier
"""

import os
import collections

from mic import kickstart

import ObsLightErr
from ObsLightUtils import isNonEmptyString

# TODO: create a KickstartManagerException class

class ObsLightKickstartManager(object):
    # pylint: disable-msg=E0202, E1101

    _kickstartPath = None
    _ksParser = None

    def __init__(self, kickstartPath=None):
        self.kickstartPath = kickstartPath
        if self.kickstartPath is not None:
            self.parseKickstart()

    @property
    def kickstartPath(self):
        return self._kickstartPath

    @kickstartPath.setter
    def kickstartPath(self, value): # pylint: disable-msg=E0102
        self._kickstartPath = value

    def _checkKsFile(self):
        """
        Raise an exception if Kickstart file is not set
        or does not exist.
        """
        ks = self.kickstartPath
        if not isNonEmptyString(ks):
            msg = "No Kickstart file set"
            raise ObsLightErr.ObsLightMicProjectErr(msg)
        if not os.path.exists(ks):
            msg = "Kickstart file '%s' does not exist" % ks
            raise ObsLightErr.ObsLightMicProjectErr(msg)

    def _checkKsParser(self):
        """
        Calls `_checkKsFile` first and then
        raises an exception if Kickstart file has not been parsed
        or correctly parsed.
        """
        self._checkKsFile()
        if self._ksParser is None:
            msg = "Kickstart file not or incorrectly parsed"
            raise ObsLightErr.ObsLightMicProjectErr(msg)

    def parseKickstart(self):
        """
        Do the parsing of the Kickstart file.
        Raises `ObsLightErr.ObsLightMicProjectErr` if no Kickstart file is set.
        """
        self._checkKsFile()
        self._ksParser = kickstart.read_kickstart(self.kickstartPath)

    # TODO: check if this method is useful
    def __getRepositoriesDict(self):
        self._checkKsParser()
        if not hasattr(self._ksParser.handler, "repo"):
            msg = "Could not find Kickstart repositories"
            raise ObsLightErr.ObsLightMicProjectErr(msg)
        return {repo.name: repo for repo in self._ksParser.handler.repo.repoList}

    def getRepositoryList(self):
        """
        Get the list of packages repositories configured in the Kickstart
        file (only their name).
        """
        self._checkKsParser()
        return [repo[0] for repo in kickstart.get_repos(self._ksParser)]

    def getPackageList(self):
        """
        Get the list of packages configured in the Kickstart
        file.
        """
        self._checkKsParser()
        return kickstart.get_packages(self._ksParser)

    def getExcludedPackageList(self):
        """
        Get the list of excluded packages configured in the Kickstart
        file.
        """
        self._checkKsParser()
        return kickstart.get_excluded(self._ksParser)

    def getPackageGroupList(self):
        """
        Get the list of package groups configured in the Kickstart
        file.
        """
        self._checkKsParser()
        return [str(group) for group in kickstart.get_groups(self._ksParser)]

    def addRepositoryByConfigLine(self, line):
        """
        Add a repository to the Kickstart by specifying the whole
        configuration line.
        ex: "repo --name=adobe --baseurl=http://linuxdownload.adobe.com/linux/i386/ --save"
        """
        self._checkKsParser()
        kickstart.add_repo(self._ksParser, line)

    def __addPackages(self, packageOrList, excluded=False):
        if isinstance(packageOrList, basestring):
            pkgList = [packageOrList]
        else:
            pkgList = packageOrList
        if excluded:
            pkgList = [("-" + pkg) for pkg in pkgList]
        self._ksParser.handler.packages.add(pkgList)

    def addPackage(self, packageOrList):
        """
        Add a package (or a list of) to the Kickstart file.
        """
        self._checkKsParser()
        self.__addPackages(packageOrList)

    def addExcludedPackage(self, packageOrList):
        """
        Add a package (or a list of) to be explicitly excluded
        in the package list of the Kickstart file.
        """
        self._checkKsParser()
        self.__addPackages(packageOrList, excluded=True)
