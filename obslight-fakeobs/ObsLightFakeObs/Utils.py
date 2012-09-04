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
These utilities don't depend on 'Config' module.

@author: Florent Vennetier
"""

import os
import subprocess
import urllib2
import xml.dom.minidom
import hashlib
from xml.etree import ElementTree

SIZE_LIMIT_FOR_INTERNAL_MD5 = 1024 * 1024
TERMINAL_COLORS = {"black": "\033[30;1m",
                   "red": "\033[31;1m",
                   "green": "\033[32;1m",
                   "yellow": "\033[33;1m",
                   "blue": "\033[34;1m",
                   "magenta": "\033[35;1m",
                   "cyan": "\033[36;1m",
                   "white": "\033[37;1m",
                   "default": "\033[0m"}

def getEntryNameList(xmlContent, tag="entry", attribute="name"):
    """
    Makes a list of all `attribute` attributes of tags `tag`
    of the XML tree.
    """
    nameList = []
    doc = xml.dom.minidom.parseString(xmlContent)
    for element in doc.getElementsByTagName(tag):
        name = element.attributes[attribute].value
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

def httpQueryToDict(query):
    """
    Makes a dict from an HTTP query.
    With query:
      project=toto&package=foo&package=bar
    it will return:
      {"project": ["toto"], "package": ["foo", "bar"]}
    """
    queryDict = dict()
    queryParts = query.split('&')
    for queryPart in queryParts:
        subParts = queryPart.split('=')
        if len(subParts) == 1 and len(subParts[0]) > 0:
            queryDict[subParts[0]] = list()
        elif len(subParts) >= 2:
            values = queryDict.get(subParts[0], list())
            values.append(subParts[1])
            queryDict[subParts[0]] = values
    return queryDict

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

def projectExistsOnServer(api, project):
    """Verify that `project` exists on server."""
    url = "%s/source/%s" % (api, project)
    try:
        urllib2.urlopen(url)
        return True
    except urllib2.HTTPError:
        return False

def buildTargetArchTuplesFromServer(api, project, targets=[], archs=[]):
    """
    Calls `api` to search for valid targets and architectures.
    You can specify which ones you want in `targets` and `archs`.
    Returns a list of (target, arch) tuples.
    """
    result = []
    availableTargets = getTargetListFromServer(api, project)
    if len(targets) == 0:
        # User did not specify targets, take them all
        targets = availableTargets
    else:
        # Refine user-specified target list
        targets = [t for t in targets if t in availableTargets]
    for target in targets:
        availableArchs = getArchListFromServer(api, project, target)
        if len(archs) == 0:
            # User did not specify archs, so take all
            for arch in availableArchs:
                result.append((target, arch))
        else:
            # User specified wanted archs, take those which are available
            for arch in archs:
                if arch in availableArchs:
                    result.append((target, arch))
    return result

def computeMd5(path):
    """
    Compute MD5 of file at `path`,
    using python if file size is less than SIZE_LIMIT_FOR_INTERNAL_MD5,
    using md5sum subprocess otherwise.
    """
    if os.path.getsize(path) < SIZE_LIMIT_FOR_INTERNAL_MD5:
        with open(path, "rb") as myFile:
            return hashlib.md5(myFile.read()).hexdigest()
    else:
        proc = subprocess.Popen(["md5sum", path], stdout=subprocess.PIPE)
        return proc.communicate()[0][:32]

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
    """Tells if `aFile` is a spec file by looking at filename extension"""
    return aFile.endswith(".spec")

def getSubDirectoryList(path):
    """Get the list of immediate sub-directories under `path`."""
    return [d for d in os.listdir(path)
            if os.path.isdir(os.path.join(path, d))]

def levenshtein(a, b):
    """
    Calculates the Levenshtein distance between a and b.
    
    Implementation taken from http://hetland.org
    """
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

def findBestSpecFile(specFileList, packageName):
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
    proc1 = subprocess.Popen(["curl", "-k", "--retry", "5", url],
                          stdout=subprocess.PIPE)
    proc2 = subprocess.Popen(["cpio", "-idvm"], stdin=proc1.stdout,
                             cwd=destDir)
    return proc2.wait()

def createCpio(outputFile, strFileList, cwd=None):
    """
    Create a CPIO archive.
     `outputFile`:  an open file-object
     `strFileList`: string with one file name by line
     `cwd`:         directory where to execute cpio from
    """
    cmd = ["cpio", "-o", "-H", "newc", "-C", "8192"]
    proc = subprocess.Popen(cmd, cwd=cwd,
                            stdin=subprocess.PIPE,
                            stdout=outputFile)
    proc.communicate(strFileList)
    return proc.wait()

def fixObsPublicApi(api):
    """
    Removes ending '/' from `api` and appends '/public' if necessary.
    Returns the fixed api.
    """
    if api.endswith('/'):
        api = api[:-1]
    if not api.endswith("/public"):
        return api + "/public"
    else:
        return api

def checkObsPublicApi(api):
    """Try to contact `api` to see if it's valid."""
    cmd = ["curl", "-s", "-S", "-f", "-k", api]
    res = callSubprocess(cmd, stdout=subprocess.PIPE)
    return res == 0

def checkRsyncUrl(url):
    """Try to contact `url` with rsync to see if it's valid."""
    cmd = ["rsync", "-q", url]
    res = callSubprocess(cmd, stdout=subprocess.PIPE)
    return res == 0

def colorize(text, color="green"):
    """
    Return a colorized copy of `text`.
    See Utils.TERMINAL_COLORS.keys() for available colors.
    """
    return TERMINAL_COLORS.get(color, "") + text + TERMINAL_COLORS["default"]

def failIfUserIsNotRoot():
    """Raise EnvironmentError if current user is not root (uid != 0)."""
    if os.getuid() != 0:
        raise EnvironmentError("You need to be root!")
