#
# Copyright 2011, Intel Inc.
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
'''
Created on 13 sept. 2011

@author: ronan@fridu.net
'''
import os

from ObsLightObject import ObsLightObject
from ObsLight import ObsLightErr

import ObsLightPackages as PK_CONST

# define the package status into the chroot jail.
CHROOT_UNKNOWN_STATUS = "Unknown"
NOT_INSTALLED = "Not installed"
NO_BUILD_DIRECTORY = "No build directory"
NO_BUILD_SECTION = "No build section"
MANY_BUILD_DIRECTORIES = "Many BUILD directories"
PREPARED = "Prepared"
BUILD = "Built"
BUILD_INSTALLED = "Build Installed"
BUILD_PACKAGED = "Build Packaged"

LIST_CHROOT_STATUS = [NOT_INSTALLED,
                    NO_BUILD_DIRECTORY,
                    NO_BUILD_SECTION,
                    MANY_BUILD_DIRECTORIES,
                    PREPARED,
                    BUILD,
                    BUILD_INSTALLED,
                    BUILD_PACKAGED]

# define the package source status.
READ_ONLY = "ro"
READ_WRITE = "rw"
readWriteStatus = [READ_ONLY,
                   READ_WRITE]

#LOCAL_STATUS = [UNKNOWN_STATUS,
#                OSC_INCONSISTENT_STATE,
#                OSC_CLEAN_STATE]

# define the package status on OBS SERVER.
OBS_SUCCEEDED = "succeeded"
OBS_FAILED = "failed"
OBS_UNRESOLVABLE = "unresolvable"
OBS_BROKEN = "broken"
OBS_BLOCKED = "blocked"
OBS_DISPATCHING = "dispatching"
OBS_SCHEDULED = "scheduled"
OBS_BUILDING = "building"
OBS_SIGNING = "signing"
OBS_FINISHED = "finished"
OBS_DISABLEED = "disabled"
OBS_EXCLUDED = "excluded"
OBS_UNKNOWN = "Unknown"

OBS_SERVER_STATUS = [OBS_SUCCEEDED,
                     OBS_FAILED,
                     OBS_UNRESOLVABLE,
                     OBS_BROKEN,
                     OBS_BLOCKED,
                     OBS_DISPATCHING,
                     OBS_SCHEDULED,
                     OBS_BUILDING,
                     OBS_SIGNING,
                     OBS_FINISHED,
                     OBS_DISABLEED,
                     OBS_EXCLUDED,
                     OBS_UNKNOWN,
                     ]

LIST_PACKAGE_STATUS = []
LIST_PACKAGE_STATUS.extend(OBS_SERVER_STATUS)

#List
OBS_REV = "obsRev"
OBS_STATUS = "status"
OSC_REV = "oscRev"
OSC_STATUS = "oscStatus"
CHROOT_STATUS = "chRootStatus"

SYNC_OK = "OK"
SYNC_FAIL = "FAIL"
SYNC_UNKNOWN = "Unknown"

LIST_SYNC_STATUS = [SYNC_OK, SYNC_FAIL, SYNC_UNKNOWN]

NameColumn = 0
StatusColumn = 1
FSStatusColumn = 2
SyncStatusColumn = 3

ID_PACKAGE_NAME = 100
ID_PACKAGE_STATUS = 101
ID_PACKAGE_CHROOT_STATUS = 102
ID_PACKAGE_SYNC = 103

PACKAGE_TXT_VALUE = {}
PACKAGE_TXT_VALUE[ID_PACKAGE_NAME] = "Package"
PACKAGE_TXT_VALUE[ID_PACKAGE_STATUS] = "Status"
PACKAGE_TXT_VALUE[ID_PACKAGE_CHROOT_STATUS] = "Filesystem status"
PACKAGE_TXT_VALUE[ID_PACKAGE_SYNC] = "Sync"

ColumnHeaders = {}
ColumnHeaders[NameColumn] = PACKAGE_TXT_VALUE[ID_PACKAGE_NAME]
ColumnHeaders[StatusColumn] = PACKAGE_TXT_VALUE[ID_PACKAGE_STATUS]
ColumnHeaders[FSStatusColumn] = PACKAGE_TXT_VALUE[ID_PACKAGE_CHROOT_STATUS]
ColumnHeaders[SyncStatusColumn] = PACKAGE_TXT_VALUE[ID_PACKAGE_SYNC]

ColumnHeadersIndex = {}
ColumnHeadersIndex[NameColumn] = ID_PACKAGE_NAME
ColumnHeadersIndex[StatusColumn] = ID_PACKAGE_STATUS
ColumnHeadersIndex[FSStatusColumn] = ID_PACKAGE_CHROOT_STATUS
ColumnHeadersIndex[SyncStatusColumn] = ID_PACKAGE_SYNC

StatusColorsDict = {}
for c in ColumnHeaders.keys():
    StatusColorsDict[c] = {}

# http://www.w3.org/TR/SVG/types.html#ColorKeywords
StatusColorsDict[StatusColumn][OBS_SUCCEEDED] = u"green"
StatusColorsDict[StatusColumn][OBS_EXCLUDED] = u"grey"
StatusColorsDict[StatusColumn][OBS_BROKEN] = u"red"
StatusColorsDict[StatusColumn][OBS_BUILDING] = u"gold"
StatusColorsDict[StatusColumn][OBS_FAILED] = u"red"
StatusColorsDict[StatusColumn][OBS_SCHEDULED] = u"blue"
StatusColorsDict[StatusColumn][OBS_UNRESOLVABLE] = u"darkred"

StatusColorsDict[FSStatusColumn][CHROOT_UNKNOWN_STATUS] = u"red"

def StatusColumnCount():
    return len(ColumnHeaders.keys())

def getPackageListID():
    return PACKAGE_TXT_VALUE.keys()

class PackageInfo(ObsLightObject):
    def __init__(self, package, fromSave={}):

        self.__package = package

        # Local package osc status and rev.
        self.__oscStatus = fromSave.get(OSC_STATUS, None)
        self.__oscRev = fromSave.get(OSC_REV, None)

        self.__obsRev = fromSave.get(OBS_REV, None)
        self.__obsStatus = fromSave.get(OBS_STATUS, OBS_UNKNOWN)

        self.__chRootStatus = fromSave.get(CHROOT_STATUS, CHROOT_UNKNOWN_STATUS)

    def getPackageInfo(self, info):
        res = {}
        for i in info:
            if i == OBS_REV:
                res[OBS_REV] = self.getObsPackageRev()
            elif i == OSC_REV:
                res[OSC_REV] = self.getOscPackageRev()
            elif i == OBS_STATUS:
                res[OSC_STATUS] = self.getPackageStatus()
            elif i == OSC_STATUS:
                res[OSC_STATUS] = self.getOscStatus()
            elif i == CHROOT_STATUS :
                res[CHROOT_STATUS ] = self.getChRootStatus()

            elif i == ID_PACKAGE_NAME:
                res[ID_PACKAGE_NAME] = self.__package.getName()
            elif i == ID_PACKAGE_STATUS:
                res[ID_PACKAGE_STATUS] = OBS_UNKNOWN
            elif i == ID_PACKAGE_CHROOT_STATUS:
                res[ID_PACKAGE_CHROOT_STATUS] = CHROOT_UNKNOWN_STATUS
            elif i == ID_PACKAGE_SYNC:
                res[ID_PACKAGE_SYNC] = SYNC_UNKNOWN


            else:
                msg = "Error in getPackageInfo '%s' is not valide" % str(i)
                raise ObsLightPackageErr(msg)
        return res

    def setPackageParameter(self, parameter=None, value=None):
        '''
        return the value  of the parameter of the package:
        the valid parameter is :
            %s
            %s
            %s
            %s
        ''' % (OBS_REV, OBS_STATUS, OSC_STATUS, OSC_REV)

        if parameter == OBS_REV:
            self.__obsRev = value
        elif parameter == OBS_STATUS:
            self.__obsStatus = value
        elif parameter == OSC_STATUS:
            self.__oscStatus = value
        elif parameter == OSC_REV:
            self.__oscRev = value

    def getPackageParameter(self, parameter=None):
        '''
        Get the value of a project parameter:
        the valid parameter is :
            %s
            %s
            %s
            %s
            %s
            prepDirName
        ''' % (OBS_REV, OBS_STATUS, OSC_STATUS, OSC_REV, CHROOT_STATUS)

        if parameter == OBS_REV:
            return self.__obsRev if self.__obsRev != None else ""
        elif parameter == OBS_STATUS:
            return self.__obsStatus if self.__obsStatus != None else ""
        elif parameter == OSC_STATUS:
            return  self.__oscStatus if self.__oscStatus != None else ""
        elif  parameter == OSC_REV:
            return self.__oscRev if self.__oscRev != None else ""
        elif parameter == CHROOT_STATUS:
            return self.__chRootStatus if self.__chRootStatus != None else ""
        else:
            msg = "Parameter '%s' is not valid for getProjectParameter" % parameter
            raise ObsLightPackageErr(msg)

    def getDic(self):
        '''
        return a description of the object in a dictionary.
        '''
        aDic = {}

        aDic[OSC_STATUS] = self.__oscStatus
        aDic[OSC_REV] = self.__oscRev

        aDic[OBS_REV] = self.__obsRev
        aDic[OBS_STATUS] = self.__obsStatus

        aDic[CHROOT_STATUS] = self.__chRootStatus

        return aDic

    def getObsPackageRev(self):
        return self.__obsRev

    def isReadyToCommit(self):
        obsRev = self.getObsPackageRev()
        oscRev = self.getOscPackageRev()
        return obsRev != oscRev

    def setObsPackageRev(self, rev):
        self.__obsRev = rev

    def getOscPackageRev(self):
        return self.__oscRev

#    def getPackageStatus(self):
#        return self.__obsStatus

    def getOscStatus(self):
        return self.__oscStatus

    def getChRootStatus(self):
        return self.__chRootStatus

    def setOscStatus(self, status):
        self.__oscStatus = status

    def setOscPackageRev(self, rev):
        self.__oscRev = rev

    def delFromChroot(self):
        self.__chRootStatus = NOT_INSTALLED

    def setChRootStatus(self, status):
        self.__chRootStatus = status

#    def update(self, status=None):
#        if status not in [None, "", "None"]:
#            self.__obsStatus = status

    def getStatus(self):
        '''
        return the Status of the package.
        '''
        return self.__obsStatus

    def isExclude(self):
        return self.getStatus() == "excluded"

    def haveBuildDirectory(self):
        return self.getChRootStatus() != NO_BUILD_DIRECTORY

    def isPackaged(self):
        return self.getChRootStatus() == "Build Packaged"
