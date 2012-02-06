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

from mic import kickstart
from mic.kickstart.custom_commands.moblinrepo import Moblin_RepoData

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

    @property
    def kickstartParser(self):
        """
        The `pykickstart.parser.KickstartParser` instance used
        internally by `ObsLightKickstartManager`. May change after
        calling `parseKickstart`.
        """
        return self._ksParser

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
        if self.kickstartParser is None:
            msg = "Kickstart file not or incorrectly parsed"
            raise ObsLightErr.ObsLightMicProjectErr(msg)

    def parseKickstart(self):
        """
        Do the parsing of the Kickstart file.
        Raises `ObsLightErr.ObsLightMicProjectErr` if no Kickstart file is set.
        """
        self._checkKsFile()
        self._ksParser = kickstart.read_kickstart(self.kickstartPath)

    def saveKickstart(self, alternateFile=None):
        """
        Save the Kickstart to `alternateFile`,
        or to `self.kickstartPath` if `alternateFile` is None.
        """
        self._checkKsParser()
        outputPath = self.kickstartPath
        if alternateFile is not None and isinstance(alternateFile, file):
            alternateFile.write(str(self.kickstartParser.handler))
        else:
            outputPath = self.kickstartPath if alternateFile is None else alternateFile
            with open(outputPath, "w") as outputFile:
                outputFile.write(str(self.kickstartParser.handler))

# --- Repositories -----------------------------------------------------------
    def getRepositoryList(self):
        """
        Get the list of packages repositories configured in the Kickstart
        file (only their name).
        """
        self._checkKsParser()
        retVal = [repo[0] for repo in kickstart.get_repos(self.kickstartParser)]
        retVal.sort()
        return retVal

    def _checkRepository(self, name):
        if not name in self.getRepositoryList():
            msg = "Repository '%s' does not exist" % name
            raise ObsLightErr.ObsLightMicProjectErr(msg)

    def __getRepoObj(self, name):
        for repo in self.kickstartParser.handler.repo.repoList:
            if repo.name == name:
                return repo

    def addRepositoryByConfigLine(self, line):
        """
        Add a repository to the Kickstart by specifying the whole
        configuration line.
        ex: "repo --name=adobe --baseurl=http://linuxdownload.adobe.com/linux/i386/ --save"
        """
        self._checkKsParser()
        kickstart.add_repo(self.kickstartParser, line)

    def addRepository(self, baseurl, name, cost=None, **kwargs):
        """
        Add a package repository in the Kickstart file.
         baseurl: the URL of the repository
         name:    a name for this repository
         cost:    the cost of this repository, from 0 (highest priority) to 99, or None
        Keyword arguments can be (default value from `Moblin_RepoData`):
        - mirrorlist (""):
        - priority (None):
        - includepkgs ([]):
        - excludepkgs ([]):
        - save (False): keep the repository in the generated image
        - proxy (None):
        - proxy_username (None):
        - proxy_password (None):
        - debuginfo (False):
        - source (False):
        - gpgkey (None): the address of the GPG key of this repository
            on the generated filesystem (ex: file:///etc/pki/rpm-gpg/RPM-GPG-KEY-meego)
        - disable (False): add the repository as disabled
        - ssl_verify ("yes"):
        """
        self._checkKsParser()
        if name in self.getRepositoryList():
            msg = "A repository with name '%s' already exists" % name
            raise ObsLightErr.ObsLightMicProjectErr(msg)
        repoObj = Moblin_RepoData(baseurl=baseurl, name=name, **kwargs)
        # cost is not available in the constructor of Moblin_RepoData
        # but exists in its parent class
        repoObj.cost = cost
        self.kickstartParser.handler.repo.repoList.append(repoObj)

    def removeRepository(self, name):
        """
        Remove the package repository `name` from the Kickstart file.
        """
        self._checkRepository(name)
        for i in range(len(self.kickstartParser.handler.repo.repoList)):
            repo = self.kickstartParser.handler.repo.repoList[i]
            if repo.name == name:
                del self.kickstartParser.handler.repo.repoList[i]
                break

    def getRepositoryDict(self, name):
        """
        Get a dictionary object representing a repository,
        suitable for input to `addRepository`.
        """
        self._checkRepository(name)
        repoObj = self.__getRepoObj(name)
        myDict = dict(repoObj.__dict__)
        # these entries are no to be known by user and
        # may cause problems if dictionary is used as input
        # to addRepository
        myDict.pop("lineno", None)
        myDict.pop("preceededInclude", None)
        return myDict
# --- end Repositories -------------------------------------------------------

# --- Packages ---------------------------------------------------------------
    def getPackageList(self):
        """
        Get the list of packages configured in the Kickstart
        file.
        """
        self._checkKsParser()
        return kickstart.get_packages(self.kickstartParser)

    def getExcludedPackageList(self):
        """
        Get the list of excluded packages configured in the Kickstart
        file.
        """
        self._checkKsParser()
        return kickstart.get_excluded(self.kickstartParser)

    def getPackageGroupList(self):
        """
        Get the list of package groups configured in the Kickstart
        file.
        """
        self._checkKsParser()
        return [group.name for group in kickstart.get_groups(self.kickstartParser)]

    def __addRemovePackages(self, packageOrList, action="add", excluded=False, group=False):
        # if packageOrList is a string, transform it in a list of one string
        if isinstance(packageOrList, basestring):
            pkgList = [packageOrList]
        else:
            pkgList = packageOrList

        if action == "add":
            # The kickstartParser.handler.packages.add method takes a 
            # list of strings formatted as in the %packages section of
            # the Kickstart file:
            #  - package groups start with '@'
            #  - excluded packages or groups start with '-'
            if group:
                pkgList = [("@" + pkg) for pkg in pkgList]
            if excluded:
                pkgList = [("-" + pkg) for pkg in pkgList]
            self.kickstartParser.handler.packages.add(pkgList)
        elif action == "remove":
            # No method in kickstartParser.handler.packages to remove
            # packages from the different lists, so doing it by hand
            packagesObj = self.kickstartParser.handler.packages
            if group:
                # excludedGroupList may not exist
                groupList = packagesObj.excludedGroupList if excluded else packagesObj.groupList
                for groupName in pkgList:
                    for i in range(len(groupList)):
                        # groups are objects, not simple strings
                        if groupList[i].name == groupName:
                            del groupList[i]
                            break
            else:
                myList = packagesObj.excludedList if excluded else packagesObj.packageList
                for pkg in pkgList:
                    if pkg in myList:
                        myList.remove(pkg)

    def addPackage(self, packageOrList):
        """
        Add a package (or a list of) to the package list of the
        Kickstart file.
        """
        self._checkKsParser()
        self.__addRemovePackages(packageOrList, action="add", excluded=False)

    def addExcludedPackage(self, packageOrList):
        """
        Add a package (or a list of) to be explicitly excluded
        in the package list of the Kickstart file.
        """
        self._checkKsParser()
        self.__addRemovePackages(packageOrList, action="add", excluded=True)

    def removePackage(self, packageOrList):
        """
        Remove a package (or a list of) from the package list of the
        Kickstart file. Does nothing if package was not in the list.
        """
        self._checkKsParser()
        self.__addRemovePackages(packageOrList, action="remove", excluded=False)

    def removeExcludedPackage(self, packageOrList):
        """
        Remove a package (or a list of) from the explicitly excluded
        package list of the Kickstart file.
        Does nothing if package was not in the list.
        """
        self._checkKsParser()
        self.__addRemovePackages(packageOrList, action="remove", excluded=True)

    def addPackageGroup(self, packageOrList):
        """
        Add a package group (or a list of) to the package section of
        the Kickstart file.
        """
        self._checkKsParser()
        self.__addRemovePackages(packageOrList, action="add", excluded=False, group=True)

    def removePackageGroup(self, packageOrList):
        """
        Remove a package group (or a list of) from the package section
        of the Kickstart file.
        Does nothing if package group was not in the list.
        """
        self._checkKsParser()
        self.__addRemovePackages(packageOrList, action="remove", excluded=False, group=True)

    # Excluded package groups seems to be unsupported
#    def getExcludedPackageGroupList(self):
#        """
#        Get the list of excluded package groups configured in the
#        Kickstart file.
#        """
#        self._checkKsParser()
#        if not hasattr(self.kickstartParser.handler.packages, "excludedGroupList"):
#            return []
#        return [group.name for group in self.kickstartParser.handler.packages.excludedGroupList]
#
#    def addExcludedPackageGroup(self, packageOrList):
#        """
#        Add a package group (or a list of) to be explicitly excluded
#        in the package section of the Kickstart file.
#        """
#        self._checkKsParser()
#        self.__addRemovePackages(packageOrList, action="add", excluded=True, group=True)
#
#    def removeExcludedPackageGroup(self, packageOrList):
#        """
#        Remove a package group (or a list of) from the explicitly excluded
#        package list of the Kickstart file.
#        Does nothing if package group was not in the list.
#        """
#        self._checkKsParser()
#        self.__addRemovePackages(packageOrList, action="remove", excluded=True, group=True)
# --- end Packages -----------------------------------------------------------
