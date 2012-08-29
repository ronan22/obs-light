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
