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
Manage the projects of FakeOBS.

@author: Florent Vennetier
"""

import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import urllib
import urllib2

import xml.dom.minidom
import ConfigParser

from Utils import callSubprocess, computeMd5, curlUnpack, findBestSpecFile
from Utils import getEntryNameList, getEntriesAsDicts
from Utils import getPackageListFromServer, getSubDirectoryList
from Utils import isASpecFile
from Config import getConfig

def getProjectList():
    """Get the local project list."""
    projectList = os.listdir(getConfig().getProjectsRootDir())
    projectList.sort()
    return projectList

def getPackageList(project):
    """Get the list of packages `project`."""
    packageList = os.listdir(getConfig().getProjectPackagesDir(project))
    packageList.sort()
    return packageList

def getTargetList(project):
    """Get the list of targets of a local project."""
    return getSubDirectoryList(getConfig().getProjectFullDir(project))

def getArchList(project, target):
    """Get the list of architectures available for `target` of `project`."""
    td = os.path.join(getConfig().getProjectFullDir(project), target)
    return getSubDirectoryList(td)

def getSpecFileList(project, package):
    """Get the list of all spec files of `package`."""
    pDir = os.path.join(getConfig().getProjectPackagesDir(project), package)
    fileList = os.listdir(pDir)
    specFileList = []
    for f in fileList:
        if isASpecFile(f):
            specFileList.append(f)
    return specFileList

def getSpecFile(project, package):
    """Get the name of the spec file of `package`."""
    return findBestSpecFile(getSpecFileList(project, package))

def readProjectSpecialFile(project, specialFile="_meta"):
    """Get the content of a file in `project`'s directory (ex: _meta)"""
    projectDir = getConfig().getProjectDir(project)
    filePath = os.path.join(projectDir, specialFile)
    content = ""
    with open(filePath, "r") as f:
        content = f.read()
    return content

def failIfProjectExists(project):
    """Raise ValueError if `project` already exists"""
    if project in getProjectList():
        raise ValueError("Project '%s' already exists!" % project)

def failIfProjectDoesNotExist(project):
    """Raise ValueError if `project` does not exist"""
    if project not in getProjectList():
        raise ValueError("Project '%s' does not exist!" % project)

def failIfTargetDoesNotExist(project, target):
    if target not in getTargetList(project):
        raise ValueError("Target '%s' does not exist for project '%s'!"
                         % (target, project))

def downloadFile(url, destDir=None, fileName=None):
    """Download the file at `url` to `destDir` and name it `fileName`"""
    conf = getConfig()
    maxRetries = conf.getIntLimit("max_download_retries", 2)
    cmd = [conf.getCommand("wget", "wget")]
    cmd += shlex.split(conf.getCommand("wget_options",
                                       "--no-check-certificate"))
    if fileName is not None:
        cmd += ["-O", fileName]
    cmd += [url]

    retCode = callSubprocess(cmd, maxRetries, cwd=destDir)
    return retCode

def downloadFiles(baseUrl, fileNames, destDir=None):
    """Download several files with a common base URL"""
    conf = getConfig()
    maxRetries = conf.getIntLimit("max_download_retries", 2)
    cmd = [conf.getCommand("wget", "wget")]
    cmd += shlex.split(conf.getCommand("wget_options",
                                       "--no-check-certificate"))
    urls = []
    for f in fileNames:
        urls.append(baseUrl + urllib.quote(f))
    cmd += urls

    retCode = callSubprocess(cmd, retries=maxRetries, cwd=destDir)
    return retCode

def makeCpioQueries(namesViewPath, maxRpmPerCpio=48):
    """
    Analyze the result of a '_repository?view=names' request and
    prepare CPIO query strings, with a maximum of `maxRpmPerCpio` RPMs
    in each query.
    """
    outputList = []
    doc = xml.dom.minidom.parse(namesViewPath)
    count = 0
    initial = [("view", "cpio")]
    for x in doc.getElementsByTagName("binary"):
        if (x.attributes["filename"].value.endswith("debuginfo.rpm") or
            x.attributes["filename"].value.endswith("debugsource.rpm")):
            continue
        if count == maxRpmPerCpio:
            outputList.append(urllib.urlencode(initial))
            initial = [("view", "cpio")]
            count = 0

        initial.append(("binary",
                        os.path.splitext(x.attributes["filename"].value)[0]))
        count = count + 1

    if count <= maxRpmPerCpio:
        outputList.append(urllib.urlencode(initial))

    return outputList

def downloadFull(api, project, target, arch, destDir):
    """
    Download the full (aka bootstrap) of `project` from `api`
    for `target` and `arch`, into `destDir`.
    """
    if not os.path.isdir(destDir):
        os.makedirs(destDir)
    viewUrl = "%s/build/%s/%s/%s/_repository?view=%s"
    cpioUrl = "%s/build/%s/%s/%s/_repository?%s"
    for viewType in ["cache", "names", "binaryversions", "solvstate"]:
        url = viewUrl % (api, project, target, arch, viewType)
        retCode = downloadFile(url, destDir)

    namesViewPath = os.path.join(destDir, "_repository?view=names")
    cpioQueries = makeCpioQueries(namesViewPath,
                                  getConfig().getIntLimit("max_rpms_per_cpio",
                                                          48))
    for query in cpioQueries:
        url = cpioUrl % (api, project, target, arch, query)
        retCode = curlUnpack(url, destDir)

def downloadFulls(api, project, targets, archs, fullDir):
    """
    Download the fulls (aka bootstraps) of `project` for `target`
    and the architectures in `archs`. A directory named `target`
    will be created in `fullDir`, and a subdirectory for each
    architecture of `archs`.
    """
    for target in targets:
        for arch in archs:
            destDir = os.path.join(fullDir, target, arch)
            downloadFull(api, project, target, arch, destDir)

def downloadRepository(rsyncUrl, project, target, repoDir):
    """Download the RPM repository of `project`, for `target`, using rsync"""
    if not os.path.isdir(repoDir):
        os.makedirs(repoDir)

    packagesDir = os.path.join(repoDir, target, "packages")
    debugDir = os.path.join(repoDir, target, "debug")
    if not os.path.exists(packagesDir):
        os.makedirs(packagesDir)
    if not os.path.exists(debugDir):
        os.makedirs(debugDir)

    conf = getConfig()
    rsync = [conf.getCommand("rsync", "rsync")]
    rsync += shlex.split(conf.getCommand("rsync_options", "-aHx"))
    rsync += ["--exclude=*.src.rpm", "--exclude=repocache/",
              "--exclude=*.repo", "--exclude=repodata/",
              "--exclude=src/", "--include=*.rpm",
              "%s/%s/%s/*" % (rsyncUrl, project.replace(":", ":/"), target),
              "."]
    retCode = callSubprocess(rsync, cwd=packagesDir)
    # TODO: check retCode
    # Is that useful ?
    retCode = callSubprocess(["find", packagesDir,
                              "-name", "*.rpm",
                              "-exec", "rpm", "--delsign", "{}", ";"])
    # TODO: check retCode
    retCode = callSubprocess(["find", packagesDir,
                              "-name", "*-debuginfo-*", "-o",
                              "-name", "*-debugsource-*",
                              "-exec", "mv", "-f", "{}", debugDir, ";"])
    # TODO: check retCode
    retCode = callSubprocess(["createrepo", packagesDir])
    retCode = callSubprocess(["createrepo", debugDir])

def downloadRepositories(rsyncUrl, project, targets, repoDir):
    """Download the RPM repositories of `project` using rsync"""
    for target in targets:
        downloadRepository(rsyncUrl, project, target, repoDir)

def downloadPackageFiles(api, project, package, destDir):
    """
    Download source files of `package` of `project` from `api`
    and put them in `destDir`.
    Returns the result of `checkPackageFilesByPath(destDir)`.
    """
    if not os.path.isdir(destDir):
        os.makedirs(destDir)

    # Download the file index, save it to '_directory'
    indexUrl = "%s/source/%s/%s" % (api, project, package)
    indexPath = os.path.join(destDir, getConfig().PackageDescriptionFile)
    res = downloadFile(indexUrl, fileName=indexPath)

    # Download special files, often missing. Don't care about return code.
    for special in ["_meta", "_attribute"]:
        fileUrl = urllib.quote("source/%s/%s/%s" %
                               (project, package, special))
        fileUrl = "%s/%s" % (api, fileUrl)
        downloadFile(fileUrl, destDir)

    # Parse the file index and download files
    xmlContent = None
    with open(indexPath, "r") as indexFile:
        xmlContent = indexFile.read()
    entries = getEntriesAsDicts(xmlContent)
    baseUrl = urllib.quote("source/%s/%s/" % (project, package))
    baseUrl = "%s/%s" % (api, baseUrl)
    res = downloadFiles(baseUrl,
                        [entry["name"] for entry in entries],
                        destDir)

    # Check everything is OK, and retry files which failed
    maxRetries = getConfig().getIntLimit("max_download_retries", 2)
    filesInError = checkPackageFilesByPath(destDir)
    while len(filesInError) > 0 and maxRetries > 0:
        res = downloadFiles(baseUrl,
                            [os.path.basename(x[1]) for x in filesInError],
                            destDir)
        maxRetries -= 1
        filesInError = checkPackageFilesByPath(destDir)
    return filesInError

def downloadPackages(api, project, packagesDir):
    """Download sources of all packages of `project` from `api`"""
    for package in getPackageListFromServer(api, project):
        packageDir = os.path.join(packagesDir, package)
        downloadPackageFiles(api, project, package, packageDir)

def downloadConfAndMeta(api, project, destDir):
    """Download configuration and meta information about `project`"""
    if not os.path.isdir(destDir):
        os.makedirs(destDir)
    for f in ["_meta", "_config"]:
        fileUrl = urllib.quote("source/%s/%s" % (project, f))
        fileUrl = "%s/%s" % (api, fileUrl)
        retCode = downloadFile(fileUrl, destDir)

def fixProjectMeta(project):
    """
    Fix the _meta file of `project`.
    
    - remove 'fakeobs' project link in dependency projects
    - fix the name of the project (in case user renamed it)
    """
    projectDir = getConfig().getProjectDir(project)
    metaFilePath = os.path.join(projectDir, "_meta")
    # TODO: do these operations with Python instead of sed
    # Remove "fakeobs" project link in dependency projects
    retCode = callSubprocess(["sed", "-r", "-i", "-e",
                              r"s,(<path\s+project=\")fakeobs:,\1,",
                              metaFilePath])
    # Fix the name of the project, in case user renamed it
    retCode = callSubprocess(["sed", "-r", "-i", "-e",
                              r"s,(<project.+name=\")\S+(\".*),\1%s\2,"
                              % project,
                              metaFilePath])

def fixProjectPackagesMeta(project):
    """
    Fix the 'project' attribute of 'package' tags in _meta file
    of each package of `project`.
    """
    packagesDir = getConfig().getProjectPackagesDir(project)
    for package in getPackageList(project):
        metaPath = os.path.join(packagesDir, package, "_meta")
        res = callSubprocess(["sed", "-r", "-i", "-e",
                              (r"s,(<package.+project=\")\S+(\".*),\1%s\2,"
                               % project),
                              metaPath])

def grabProject(api, rsyncUrl, project, targets, archs, newName=None):
    """
    Grab a project from an OBS server.
      api:       the public API of the OBS server
                  (ex: "https://api.tizen.org/public")
      rsyncUrl:  the rsync URL to fetch repositories from
                  (ex: "rsync://download.tizen.org/live")
      project:   the name of the project to grab
                  (ex: "Tizen:1.0:Base")
      targets:    a list of build targets to grab
                  (ex: "standard")
      archs:     a list of architectures to grab
                  (ex: ["i586", "armv7el"])
      newName:   the name to give to the project after it has been grabbed.
                 If it's None, don't change the name.
    """
    if newName is None:
        newName = project
    failIfProjectExists(newName)
    # TODO: check other parameters

    conf = getConfig()
    projectDir = conf.getProjectDir(newName)
    fullDir = conf.getProjectFullDir(newName)
    packagesDir = conf.getProjectPackagesDir(newName)
    repoDir = conf.getProjectRepositoryDir(newName)

    downloadConfAndMeta(api, project, projectDir)
    fixProjectMeta(newName)
    downloadFulls(api, project, targets, archs, fullDir)
    downloadPackages(api, project, packagesDir)
    fixProjectPackagesMeta(newName)
    downloadRepositories(rsyncUrl, project, targets, repoDir)

    grabTime = time.asctime()
    cp = ConfigParser.SafeConfigParser()
    cp.add_section("GrabInfo")
    cp.set("GrabInfo", "api", api)
    cp.set("GrabInfo", "rsync_url", rsyncUrl)
    cp.set("GrabInfo", "project", project)
    cp.set("GrabInfo", "targets", ",".join(targets))
    cp.set("GrabInfo", "archs", ",".join(archs))
    cp.set("GrabInfo", "date", grabTime)

    cp.add_section("UpdateInfo")
    cp.set("UpdateInfo", "last_update", grabTime)
    cp.set("UpdateInfo", "rsync_update_url", "")

    with open(conf.getProjectInfoPath(newName), "wb") as configFile:
        cp.write(configFile)
    updateLiveRepository(newName)

def removeProject(project):
    """Remove `project` from fakeobs."""
    conf = getConfig()
    for d in {conf.getProjectDir(project),
              conf.getProjectRepositoryDir(project),
              conf.getProjectLiveDir(project)}:
        if os.path.isdir(d):
            shutil.rmtree(d)

def exportProject(project, destPath=None):
    """
    Export a project to an archive.
    `destPath` is either the path of the output archive or
    the path to a directory to create the archive in.
    Compression is guessed from archive suffix (defaults to gzip).
    """
    conf = getConfig()
    fakeobsRootDir = conf.getFakeObsRootDir()
    projectDir = conf.getProjectDir(project)
    repoDir = conf.getProjectRepositoryDir(project)
    projectRelPath = projectDir[len(fakeobsRootDir) + 1:]
    repoRelPath = repoDir[len(fakeobsRootDir) + 1:]

    archiveName = "%s-%s.tar.gz" % (project.replace(':', '_'),
                                    time.strftime("%Y%m%d%H%M%S"))
    if destPath is None:
        destPath = archiveName
    elif os.path.isdir(destPath):
        destPath = os.path.join(destPath, archiveName)
    vars = {"archive": destPath, "fakeobs_root": fakeobsRootDir}
    tarCmd = [conf.getCommand("tar")]
    tarCmd += shlex.split(conf.getCommand("tar_create_options", vars=vars))
    tarCmd += [projectRelPath, repoRelPath]
    res = callSubprocess(tarCmd)

def importProject(archivePath, newName=None):
    """
    Import a project from an archive.
    `newName` is the name to give to the project after
    it has been extracted, None means 'do not rename'.
    """
    if newName is not None:
        failIfProjectExists(newName)

    conf = getConfig()
    fakeobsRootDir = conf.getFakeObsRootDir()
    stagingDir = tempfile.mkdtemp(dir=fakeobsRootDir)
    try:
        # Extract archive to a temporary directory
        vars = {"archive": archivePath, "fakeobs_root": stagingDir}
        tarCmd = [conf.getCommand("tar")]
        tarCmd += shlex.split(conf.getCommand("tar_extract_options", vars=vars))
        res = callSubprocess(tarCmd)
        if res != 0:
            # FIXME: raise exception instead of returning 1
            return 1

        # The name of the project is the name of the unique directory
        # under projects/
        tmpProjectsRootDir = os.path.join(stagingDir, "projects")
        project = os.listdir(tmpProjectsRootDir)[0]

        if newName is None:
            failIfProjectExists(project)
            newName = project

        # Move/rename the project directory
        shutil.move(os.path.join(tmpProjectsRootDir, project),
                    conf.getProjectDir(newName))
        # Move/rename the project repository
        projectRepositoryDir = conf.getProjectRepositoryDir(newName)
        parentDir = os.path.dirname(projectRepositoryDir)
        if not os.path.isdir(parentDir):
            os.makedirs(parentDir)
        tmpProjectRepositoryDir = os.path.join(stagingDir, "repositories",
                                               project.replace(":", ":/"))
        shutil.move(tmpProjectRepositoryDir, projectRepositoryDir)
    finally:
        shutil.rmtree(stagingDir)
    updateLiveRepository(newName)

def checkProjectConfigAndMeta(project):
    """
    Check for common errors in _meta and _config
    and return a list of error messages.
    """
    errorList = []
    projectDir = getConfig().getProjectDir(project)
    metaPath = os.path.join(projectDir, "_meta")
    if not os.path.exists(metaPath):
        errorList.append("Project meta does not exist!")
    else:
        if os.path.getsize(metaPath) == 0:
            errorList.append("Project meta is empty!")
        else:

            exp = re.compile(r'<path project="fakeobs:')
            found = False
            lineCount = 0
            with open(metaPath, "r") as f:
                for line in f:
                    lineCount += 1
                    if exp.search(line):
                        found = True
                        break
            if found:
                msg = """Project meta contains a path to a fakeobs project! (line %d)
This won't work. Please edit %s
and replace any occurence of
  '<path project=\"fakeobs:Your:Project\" repository=\"something\" />'
by
  '<path project=\"Your:Project\" repository=\"something\" />'

"""
                errorList.append(msg % (lineCount, metaPath))

    configPath = os.path.join(projectDir, "_config")
    if not os.path.exists(configPath):
        errorList.append("Project config does not exist!")
    else:
        if os.path.getsize(configPath) == 0:
            errorList.append("Project config is empty, may be a problem " +
                             "for top-level projects.\n" +
                             "Please check %s" % configPath)
    return errorList

def checkProjectFull(project):
    """
    Check for the integrity of project's :full directory.
    """
    errorList = []
    fullDir = getConfig().getProjectFullDir(project)
    if not os.path.isdir(fullDir):
        errorList.append("Project :full directory is missing!")
        return errorList
    for target in os.listdir(fullDir):
        targetDir = os.path.join(fullDir, target)
        for arch in os.listdir(targetDir):
            archDir = os.path.join(targetDir, arch)
            namesRawFilePath = os.path.join(archDir,
                                            "_repository?view=names")
            if not os.path.exists(namesRawFilePath):
                msg = "The file listing the RPMs is missing for %s %s"
                errorList.append(msg % (target, arch))
                break
            xmlContent = ""
            with open(namesRawFilePath, "r") as f:
                xmlContent = f.read()
            fileList = getEntryNameList(xmlContent, "binary", "filename")
            for fileName in fileList:
                if (fileName.endswith("debuginfo.rpm") or
                    fileName.endswith("debugsource.rpm")):
                    continue
                filePath = os.path.join(archDir, fileName)
                if not os.path.exists(filePath):
                    errorList.append("%s is missing" % filePath)
                    continue
                res = callSubprocess(["rpm", "--checksig", filePath],
                                      stdout=subprocess.PIPE)
                if res != 0:
                    errorList.append("%s failed the integrity test"
                                     % filePath)
    return errorList

def checkProjectRepository(project):
    """
    Check for the integrity of RPMs in project's repository.
    """
    errorList = []
    repoDir = getConfig().getProjectRepositoryDir(project)
    if not os.path.isdir(repoDir):
        errorList.append("No repository for project %s!" % project)
        return errorList
    targetList = os.listdir(repoDir)
    if len(targetList) == 0:
        errorList.append("Repository of %s is empty!" % project)
        return errorList
    for target in targetList:
        targetDir = os.path.join(repoDir, target)
        for (dirPath, dirNames, fileNames) in os.walk(targetDir):
            for fileName in fileNames:
                if fileName.endswith(".rpm"):
                    filePath = os.path.join(dirPath, fileName)
                    cmd = ["rpm", "--checksig", filePath]
                    res = callSubprocess(cmd, stdout=subprocess.PIPE)
                    if res != 0:
                        errorList.append("%s failed the integrity test"
                                         % filePath)
    return errorList

def checkPackageFilesByPath(packagePath):
    """
    Check consistency of all files of the package living in `packagePath`.
    Returns a list of tuples like (error_message, path).
    """
    errorList = []
    indexPath = os.path.join(packagePath, getConfig().PackageDescriptionFile)
    xmlContent = None
    with open(indexPath, "r") as indexFile:
        xmlContent = indexFile.read()
    entries = getEntriesAsDicts(xmlContent)
    for entry in entries:
        entryPath = os.path.join(packagePath, entry["name"])
        msg = None
        if not os.path.exists(entryPath):
            msg = "%s is missing!" % entryPath
        elif os.path.getsize(entryPath) != int(entry["size"]):
            msg = "%s has unexpected file size!" % entryPath
        elif computeMd5(entryPath) != entry["md5"]:
            msg = "%s is corrupted!" % entryPath
        if msg is not None:
            errorList.append((msg, entryPath))
    return errorList

def checkPackageFiles(project, package):
    """
    Check consistency of all files of `package` of `project`.
    Returns a list of tuples like (error_message, path).
    """
    packagesDir = getConfig().getProjectPackagesDir(project)
    packagePath = os.path.join(packagesDir, package)
    return checkPackageFilesByPath(packagePath)

def checkAllPackagesFiles(project):
    """
    Check consistency of all package files of `project`.
    Returns a list of error messages.
    """
    conf = getConfig()
    packagesDir = conf.getProjectPackagesDir(project)
    errorList = []
    for package in getPackageList(project):
        errors = checkPackageFiles(project, package)
        for error in errors:
            errorList.append(error[0])
    return errorList

def getProjectDependencies(project, target):
    """
    Returns the dependencies of `project` for `target`
    as a set of (project, target) tuples.
    """
#    failIfProjectDoesNotExist(project)
#    failIfTargetDoesNotExist(project, target)
    if not project in getProjectList():
        return []
    projectDir = getConfig().getProjectDir(project)
    metaFilePath = os.path.join(projectDir, "_meta")
    depSet = set()
    # Find first-level dependencies
    doc = xml.dom.minidom.parse(metaFilePath)
    for repo in doc.getElementsByTagName("repository"):
        if repo.attributes["name"].value == target:
            for dep in repo.getElementsByTagName("path"):
                depSet.add((str(dep.attributes["project"].value),
                         str(dep.attributes["repository"].value)))

    recDepSet = set()
    # Recursively find dependencies
    for project1, target1 in depSet:
        recDepSet.update(getProjectDependencies(project1, target1))
    depSet.update(recDepSet)

    depSet.add((project, target))
    return depSet

def updateLiveRepository(project):
    """
    Create/update a directory hierarchy suitable for use as an OBS live
    RPM repository, based on actual repositories suitable for image
    generation by MIC.
    """
    for target in getTargetList(project):
        conf = getConfig()
        prjLiveDir = conf.getProjectLiveDir(project)
        prjRepoDir = conf.getProjectRepositoryDir(project)
        if not os.path.isdir(prjLiveDir):
            os.makedirs(prjLiveDir)
        linkTarget = os.path.join(prjRepoDir, target, "packages")
        linkTarget = os.path.relpath(linkTarget, prjLiveDir)
        linkName = os.path.join(prjLiveDir, target)
        print linkName, " -> ", linkTarget
        if os.path.lexists(linkName):
            os.unlink(linkName)
        os.symlink(linkTarget, linkName)

def updateLiveRepositories():
    """Call `updateLiveRepository(project)` on each installed project."""
    for project in getProjectList():
        updateLiveRepository(project)
