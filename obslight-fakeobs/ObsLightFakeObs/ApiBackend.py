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
Functions to be used by FakeOBS API daemon.

@author: Florent Vennetier
"""

import csv
import os
import xml.dom.minidom

import ProjectManager
from Config import getConfig

def buildEntryList(entries, rootTag="directory", entryTag="entry"):
    impl = xml.dom.minidom.getDOMImplementation()
    indexdoc = impl.createDocument(None, rootTag, None)
    for entry in entries:
        entryelm = indexdoc.createElement(entryTag)
        entryelm.setAttribute("name", entry)
        indexdoc.childNodes[0].appendChild(entryelm)
    return indexdoc.childNodes[0].toprettyxml(encoding="us-ascii")

def projectExists(project):
    return project in ProjectManager.getProjectList()

def getProjectMeta(project):
    return ProjectManager.readProjectSpecialFile(project, "_meta")

def getProjectConfig(project):
    return ProjectManager.readProjectSpecialFile(project, "_config")

def getProjectDependencies(project, target):
    return ProjectManager.getProjectDependencies(project, target)

def getRecursiveProjectConfig(project, target):
    configStr = ""
    for prj, _ in getProjectDependencies(project, target):
        configStr += ProjectManager.readProjectSpecialFile(prj, "_config")
    return configStr

def getPackageFilePath(project, package, fileName):
    packagesDir = getConfig().getProjectPackagesDir(project)
    filePath = os.path.join(packagesDir, package, fileName)
    return filePath

def getPackageLastRevSrcmd5(project, package):
    """Get rev and srcmd5 attributes of `package` (as a tuple)."""
    xmlContent = buildFileIndex(project, package)
    doc = xml.dom.minidom.parseString(xmlContent)
    for x in doc.getElementsByTagName("directory"):
        rev = x.attributes["rev"]
        srcmd5 = x.attributes["srcmd5"]
        return rev, srcmd5

def getProjectSpecFile(project, package):
    return ProjectManager.getSpecFile(project, package)

def buildProjectIndex():
    return buildEntryList(ProjectManager.getProjectList())

def buildPackageIndex(project):
    return buildEntryList(ProjectManager.getPackageList(project))

def buildTargetIndex(project):
    return buildEntryList(ProjectManager.getTargetList(project))

def buildArchIndex(project, target):
    return buildEntryList(ProjectManager.getArchList(project, target))

def buildFileIndex(project, package):
    packagesDir = getConfig().getProjectPackagesDir(project)
    packagePath = os.path.join(packagesDir, package)
    indexPath = os.path.join(packagePath, getConfig().PackageDescriptionFile)
    with open(indexPath, "r") as f:
        return f.read()

def buildSearchIndex():
    content = "<collection>\n"
    for project in ProjectManager.getProjectList():
        content += getProjectMeta(project)
    content += "</collection>\n"
    return content

def getNextEvent():
    with open(getConfig().getLastEventsFilePath(), 'rb') as f:
        csvReader = csv.reader(f, delimiter='|', quotechar='"')
        last = 0
        for row in csvReader:
            last = int(row[0])
        return last

def getEventsFiltered(start, filters):
    impl = getDOMImplementation()
    indexdoc = impl.createDocument(None, "events", None)

    def appendTextElement(parent, tag, text):
        node = indexdoc.createElement(tag)
        node.appendChild(doc1.createTextNode(text))
        parent.appendChild(node)

    with open("lastevents", 'rb') as f:
        indexdoc.childNodes[0].setAttribute("next", str(getNextEvent()))

        csvReader = csv.reader(f, delimiter='|', quotechar='"')
        for row in csvReader:
            num = int(row[0])
            if num <= start:
                continue
            is_ok = False
            for filter in filters:
                if filter[2] is None:
                    if filter[0] == row[2] and filter[1] == row[3]:
                       is_ok = True
                elif filter[0] == row[2] and filter[1] == row[3] and filter[2] == row[4]:
                    is_ok = True
            if is_ok:
                eventelm = indexdoc.createElement("event")
                eventelm.setAttribute("type", row[2])
                if row[2] == "package":
                    appendTextElement(eventelm, "project", row[3])
                    appendTextElement(eventelm, "package", row[4])
                if row[2] == "repository":
                    appendTextElement(eventelm, "project", row[3])
                    appendTextElement(eventelm, "repository", row[4])
                    appendTextElement(eventelm, "arch", row[5])
                if row[2] == "project":
                    appendTextElement(eventelm, "project", row[3])
                indexdoc.childNodes[0].appendChild(eventelm)

    return indexdoc.childNodes[0].toxml(encoding="us-ascii")

def updateLiveRepositories():
    ProjectManager.updateLiveRepositories()
