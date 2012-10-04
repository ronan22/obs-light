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
'''
Created on 24 Sept 2012

@author: Ronan Le Martret
'''

import os
import urlparse
from ObsLightSubprocess import SubprocessCrt

CACHEDIRECTORY = "/tmp/cache/obslight/"

import subprocess

def testCacheDir():
    if not os.path.isdir(CACHEDIRECTORY):
        os.makedirs(CACHEDIRECTORY)
        return True
    else:
        return True

def downloadFiles(rpmUrl):
    """Download several files with a common base URL"""
    cmd = "wget --continue --no-check-certificate %s -O %s"

    parseRes = urlparse.urlparse()
    mySubprocessCrt = SubprocessCrt()

    destPath = CACHEDIRECTORY + "/" + parseRes[1] + parseRes[2]

    mySubprocessCrt.execSubprocess(cmd % (rpmUrl, destPath))

    return destPath

def checkCacheFile(rpmDict):
    testCacheDir()
    res = {}

    for package in rpmDict.keys():
        url = rpmDict[package]
        if url.start("http"):
            res[package] = downloadFiles(url)
        else:
            res[package] = url

    return res



