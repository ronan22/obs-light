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
Miscellaneous utilities for FakeOBS.

@author: Florent Vennetier
"""

import os
import subprocess
import urllib2
import xml.dom.minidom
from hashlib import md5
from xml.etree import ElementTree

SIZE_LIMIT_FOR_INTERNAL_MD5 = 1024 * 1024

def getEntryNameList(xmlContent, tag="entry", attribute="name"):
    """
    Makes a list of all `attribute` attributes of tags `tag`
    of the XML tree.
    """
    nameList = []
    doc = xml.dom.minidom.parseString(xmlContent)
    for x in doc.getElementsByTagName(tag):
        name = x.attributes[attribute].value
        nameList.append(name)
    return nameList

def getEntriesAsDicts(xmlContent, tag="entry"):
    """
    Make a dict from a string like the one returned by a request to
      /source/<project>/<package>
    """
    dictList = []
    directoryList = ElementTree.fromstring(xmlContent)
    for directory in directoryList:
        for element in directory.iter(tag):
            entry = dict()
            for attribute in element.items():
                entry[attribute[0]] = attribute[1]
            dictList.append(entry)
    return dictList

def getPackageListFromServer(api, project):
    """Get the list of packages of a project from the server."""
    url = "%s/source/%s" % (api, project)
    projectIndex = urllib2.urlopen(url).read()
    return getEntryNameList(projectIndex)

def getTargetListFromServer(api, project):
    """Get the list of targets of `project` from the server."""
    url = "%s/build/%s" % (api, project)
    xmlTargetList = urllib2.urlopen(url).read()
    return getEntryNameList(xmlTargetList)

def getArchListFromServer(api, project, target):
    """
    Get the list of architectures for `target` of `project`
    from the server.
    """
    url = "%s/build/%s/%s" % (api, project, target)
    xmlArchList = urllib2.urlopen(url).read()
    return getEntryNameList(xmlArchList)

def computeMd5(path):
    """
    Compute MD5 of file at `path`,
    using python if file size is less than SIZE_LIMIT_FOR_INTERNAL_MD5,
    using md5sum subprocess otherwise.
    """
    if os.path.getsize(path) < SIZE_LIMIT_FOR_INTERNAL_MD5:
        with open(path, "rb") as f:
            return md5(f.read()).hexdigest()
    else:
        p = subprocess.Popen(["md5sum", path], stdout=subprocess.PIPE)
        return p.communicate()[0][:32]

def callSubprocess(command, retries=0, *popenargs, **kwargs):
    """
    Run subprocess.call(command, *popenargs, **kwargs) until it
    returns 0, at most `retries` +1 times.
    """
    retCode = -1
    while retCode != 0 and retries >= 0:
        retCode = subprocess.call(command, *popenargs, **kwargs)
        retries -= 1
    return retCode

def isASpecFile(aFile):
    return aFile.endswith(".spec")

def getSubDirectoryList(path):
    return [d for d in os.listdir(path)
            if os.path.isdir(os.path.join(path, d))]

# Implementation taken from http://hetland.org
def levenshtein(a, b):
    """Calculates the Levenshtein distance between a and b."""
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current = range(n + 1)
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if a[j - 1] != b[i - 1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]

def findBestSpecFile(self, specFileList, packageName):
    """Find the name of the spec file which matches best with `packageName`"""
    specFile = None
    if len(specFileList) < 1:
        # No spec file in list
        specFile = None
    elif len(specFileList) == 1:
        # Only one spec file
        specFile = specFileList[0]
    else:
        sameStart = []
        for spec in specFileList:
            if str(spec[:-5]) == str(packageName):
                # This spec file has the same name as the package
                specFile = spec
                break
            elif spec.startswith(packageName):
                # This spec file has a name which looks like the package
                sameStart.append(spec)

        if specFile is None:
            if len(sameStart) > 0:
                # Sort the list of 'same start' by the Levenshtein distance
                sameStart.sort(key=lambda x: levenshtein(x, packageName))
                specFile = sameStart[0]
            else:
                # No spec file starts with the name of the package,
                # sort the whole spec file list by the Levenshtein distance
                specFileList.sort(key=lambda x: levenshtein(x, packageName))
                specFile = specFileList[0]
    return specFile

def curlUnpack(url, destDir):
    """Call `url` and pipe the result to cpio to extract RPMs in `destDir`"""
    p1 = subprocess.Popen(["curl", "-k", "--retry", "5", url],
                          stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["cpio", "-idvm"], stdin=p1.stdout, cwd=destDir)
    return p2.wait()

def createCpio(outputFile, strFileList, cwd=None):
    """
    Create a CPIO archive.
     `outputFile`:  an open file-object
     `strFileList`: string with one file name by line
     `cwd`:         directory where to execute cpio from
    """
    cmd = ["cpio", "-o", "-H", "newc", "-C", "8192"]
    p = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.PIPE, stdout=outputFile)
    p.communicate(strFileList)
    return p.wait()
