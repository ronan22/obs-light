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
Manage the distributions.xml file of an OBS server
(usually /srv/www/obs/api/files/distributions.xml).

@author: Florent Vennetier
"""

import os
import re
import shutil
import xml.dom.minidom
import ProjectManager
from Config import getConfig


def appendTextElement(doc, parent, tag, text):
    node = doc.createElement(tag)
    node.appendChild(doc.createTextNode(text))
    parent.appendChild(node)

def addDistrib(doc, project, target):
    """Add a distribution in `doc`."""
    # Name of the OBS project linking to the fakeobs API
    fakeobsLinkName = "fakeobs"
    projectId = "fakeobs-%s-%s" % (project.replace(":", "-").lower(),
                                   target)
    projectRepoName = project.replace(":", "_")
    projectCleanedName = project.replace(":", " ")
    projectCleanedName += " (%s)" % target

    newDistrib = doc.createElement("distribution")

    newDistrib.setAttribute("vendor", "fakeobs")
    newDistrib.setAttribute("version", "Testing")
    newDistrib.setAttribute("id", projectId)

    appendTextElement(doc, newDistrib, "name", projectCleanedName)
    appendTextElement(doc, newDistrib, "project",
                      "%s:%s" % (fakeobsLinkName, project))
    appendTextElement(doc, newDistrib, "reponame", projectRepoName)
    appendTextElement(doc, newDistrib, "repository", target)
    appendTextElement(doc, newDistrib, "link",
                      "http://en.opensuse.org/openSUSE:OBS_Light_Fakeobs")

    doc.firstChild.appendChild(newDistrib)

def removeDistrib(doc, project, target):
    """Remove a distribution matching `project` and `target` from `doc`."""
    projectId = "fakeobs-%s-%s" % (project.replace(":", "-").lower(),
                                   target)
    nodeToRemove = None
    for distrib in doc.getElementsByTagName("distribution"):
        if distrib.attributes["id"].value == projectId:
            targetElm = distrib.getElementsByTagName("repository")[0]
            if target is None or str(targetElm.firstChild.data) == target:
                nodeToRemove = distrib
                break
    if nodeToRemove is not None:
        doc.firstChild.removeChild(distrib)

def listFakeObsDistribs(doc):
    """
    List FakeOBS distributions found in `doc`.
    Returns a set of (project, target) tuples.
    """
    distribs = set()
    for distrib in doc.getElementsByTagName("distribution"):
        id = distrib.attributes["id"].value
        if id.startswith("fakeobs-"):
            projectElm = distrib.getElementsByTagName("project")[0]
            targetElm = distrib.getElementsByTagName("repository")[0]
            project = str(projectElm.firstChild.data)
            target = str(targetElm.firstChild.data)
            distribs.add((project, target))
    return distribs

def saveDocument(doc, filePath):
    """Save `doc` XML document to `filePath`."""
    # Hack found here:
    # http://stackoverflow.com/questions/749796/pretty-printing-xml-in-python
    uglyXml = doc.toprettyxml(indent='  ', encoding="UTF-8")
    textRe = re.compile('>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL)
    prettyXml = textRe.sub('>\g<1></', uglyXml)
    with open(filePath, "w+") as outputFile:
        # The auto-indent makes crap
#       doc.writexml(outputFile, indent=" ", addindent=" ",
#                    newl="\n", encoding="UTF-8")
#       doc.writexml(outputFile, encoding="UTF-8")
        outputFile.write(prettyXml)

def copyFakeObsLogo():
    conf = getConfig()
    themeDir = conf.getPath("theme_dir", "/srv/obslight-fakeobs/theme")
    logoDir = "/srv/www/obs/webui/public/images/distributions/"
    src = os.path.join(themeDir, "fakeobs.png")
    dst = os.path.join(logoDir, "fakeobs.png")
    if not os.path.exists(dst):
        try:
            shutil.copy(src, dst)
        except IOError as myError:
            # It's not a real problem if logo is not copied
            pass

def updateFakeObsDistributions():
    """
    Update distributions.xml. Add new projects, remove no longer
    existing projects.
    """
    conf = getConfig()
    # File where are described the default target distributions.
    # Probably /srv/www/obs/api/files/distributions.xml
    distributionsFile = conf.getPath(
        "obs_distributions_file",
        "/srv/www/obs/api/files/distributions.xml")

    doc1 = xml.dom.minidom.parse(distributionsFile)

    localProjectSet = ProjectManager.getProjectTargetTuples()
    fileProjectSet = listFakeObsDistribs(doc1)

    toBeRemoved = fileProjectSet.difference(localProjectSet)
    toBeAdded = localProjectSet.difference(fileProjectSet)

    for project, target in toBeRemoved:
        removeDistrib(doc1, project, target)

    for project, target in toBeAdded:
        addDistrib(doc1, project, target)

    saveDocument(doc1, distributionsFile)
    copyFakeObsLogo()
