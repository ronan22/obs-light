#!/usr/bin/python
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
Data converter from Fake OBS < 1.0.0 to >= 1.0.0.

@author: Florent Vennetier
"""

import os
import shutil
import subprocess
import time

from Config import getConfig
import ProjectManager
import Utils

def copyFull(project, fullDir):
    """Copy the content of :full from the old `project` to `fullDir`."""
    oldFullDir = os.path.join("/srv/fakeobs/obs-repos", project + ":latest")
    shutil.copytree(oldFullDir, fullDir)

def copyRepository(project, release, target, repoDir):
    extProject = project.replace(":", ":/")
    if not os.path.isdir(repoDir):
        os.makedirs(repoDir)

    targetDir = os.path.join(repoDir, target)
    oldTargetDir = os.path.join("/srv/fakeobs/releases", release,
                                "builds", extProject, target)
    shutil.copytree(oldTargetDir, targetDir)

def convertProject(project, release, newName=None):
    if newName is None:
        newName = project
    ProjectManager.failIfProjectExists(newName)

    conf = getConfig()
    port = 7999
    delay = 8
    api = "http://localhost:%s/public" % port
    fRoot = conf.getFakeObsRootDir()
    cmd = [os.path.join(fRoot, "tools", "legacy_fakeobs.py"),
           str(port)]
    msg = "Running '%s' and waiting %d seconds" % (" ".join(cmd), delay)
    print Utils.colorize(msg, "green")
    oldFakeObs = subprocess.Popen(cmd, cwd="/srv/fakeobs")
    time.sleep(delay)

    projectDir = conf.getProjectDir(newName)
    fullDir = conf.getProjectFullDir(newName)
    packagesDir = conf.getProjectPackagesDir(newName)
    repoDir = conf.getProjectRepositoryDir(newName)

    try:
        msg = "Getting _config and _meta"
        print Utils.colorize(msg, "green")
        ProjectManager.downloadConfAndMeta(api, project, projectDir)
        ProjectManager.fixProjectMeta(newName)
        msg = "Copying packages"
        print Utils.colorize(msg, "green")
        ProjectManager.downloadPackages(api, project, packagesDir)
        ProjectManager.fixProjectPackagesMeta(newName)
        msg = "Copying :full"
        print Utils.colorize(msg, "green")
        copyFull(project, fullDir)
        msg = "Copying repositories"
        print Utils.colorize(msg, "green")
        for target in ProjectManager.getTargetList(newName):
            copyRepository(project, release, target, repoDir)
        ProjectManager.updateLiveRepository(newName)
        return newName
    except:
        print Utils.colorize("Failed", "red")
        raise
    finally:
        oldFakeObs.terminate()
