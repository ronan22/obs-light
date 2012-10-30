# coding=utf-8
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
@author: José Bollo
"""

import os
import re
import shlex
import shutil
import subprocess
import tempfile
import time
import urllib
import urllib2

import xml.dom.minidom
import ConfigParser

import Utils
import Dupes
import GbsTree
from Config import getConfig
from DistributionsManager import updateFakeObsDistributions
from ObsManager import createFakeObsLink

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
    return Utils.getSubDirectoryList(getConfig().getProjectFullDir(project))

def getArchList(project, target):
    """Get the list of architectures available for `target` of `project`."""
    targetDir = os.path.join(getConfig().getProjectFullDir(project), target)
    return Utils.getSubDirectoryList(targetDir)

def getProjectTargetTuples():
    """Get a set of locally installed (project, target) tuples."""
    result = set()
    for project in getProjectList():
        for target in getTargetList(project):
            result.add((project, target))
    return result

def getSpecFileList(project, package):
    """Get the list of all spec files of `package`."""
    pDir = os.path.join(getConfig().getProjectPackagesDir(project), package)
    fileList = os.listdir(pDir)
    specFileList = []
    for myFile in fileList:
        if Utils.isASpecFile(myFile):
            specFileList.append(myFile)
    return specFileList

def getSpecFile(project, package):
    """Get the name of the spec file of `package`."""
    return Utils.findBestSpecFile(getSpecFileList(project, package), package)

def readProjectSpecialFile(project, specialFile="_meta"):
    """Get the content of a file in `project`'s directory (ex: _meta)"""
    projectDir = getConfig().getProjectDir(project)
    filePath = os.path.join(projectDir, specialFile)
    content = ""
    with open(filePath, "r") as myFile:
        content = myFile.read()
    return content

def getUpdateInformations(project):
    """
    Get a dictionary with informations of the [UpdateInfo] section
    of the project_info file of `project`.
    """
    projectInfoPath = getConfig().getProjectInfoPath(project)
    confParser = ConfigParser.SafeConfigParser()
    confParser.read(projectInfoPath)
    infoDict = {"rsync_update_url": None,
                "project": None,
                "last_update": None}
    for option in infoDict.keys():
        if confParser.has_option("UpdateInfo", option):
            value = confParser.get("UpdateInfo", option)
            if Utils.isNonEmptyString(value):
                infoDict[option] = value
    return infoDict

def failIfProjectExists(project):
    """Raise ValueError if `project` already exists"""
    if project in getProjectList():
        raise ValueError("Project '%s' already exists!" % project)

def failIfProjectDoesNotExist(project):
    """Raise ValueError if `project` does not exist"""
    if project not in getProjectList():
        raise ValueError("Project '%s' does not exist!" % project)

def failIfTargetDoesNotExist(project, target):
    """Raise ValueError if `target` does not exist for `project`"""
    if target not in getTargetList(project):
        raise ValueError("Target '%s' does not exist for project '%s'!"
                         % (target, project))

def downloadFile(url, destDir=None, fileName=None, retryIfEmpty=True):
    """
    Download the file at `url` to `destDir` and name it `fileName`.
    `retryIfEmpty` works only if `fileName` is provided.
    """
    conf = getConfig()
    maxRetries = conf.getIntLimit("max_download_retries", 2)
    cmd = [conf.getCommand("wget", "wget")]
    cmd += shlex.split(conf.getCommand("wget_options",
                                       "--no-check-certificate"))
    if fileName is not None:
        cmd += ["-O", fileName]
    cmd += [url]

    retryCount = 0
    sizeOk = False
    while not sizeOk and retryCount <= maxRetries:
        retryCount += 1
        retCode = Utils.callSubprocess(cmd, maxRetries, cwd=destDir)
        if retCode == 0 and fileName is not None:
            if destDir is None:
                absolutePath = fileName
            else:
                # if fileName starts with '/', absolutePath == fileName
                absolutePath = os.path.join(destDir, fileName)
            sizeOk = (os.path.getsize(absolutePath) > 0)
        else:
            sizeOk = True
    return retCode

def downloadTo(uri, filename):
    """
    Download the file at `uri` to `fileName`.
    """
    nrtry = max(1, getConfig().getIntLimit("max_download_retries", 2))
    f = None
    while True:
	try:
	    f = urllib2.urlopen(uri)
	    data = f.read()
	    f.close()
	    f = open(filename, "w")
	    f.write(data)
	    f.close()
	    return True
	except Exception as e:
	    if f:
		f.close()
	    if nrtry > 1:
		nrtry = nrtry - 1
	    else:
		raise e
    return False

def downloadFiles(baseUrl, fileNames, destDir=None):
    """Download several files with a common base URL"""
    conf = getConfig()
    maxRetries = conf.getIntLimit("max_download_retries", 2)
    cmd = [conf.getCommand("wget", "wget")]
    cmd += shlex.split(conf.getCommand("wget_options",
                                       "--no-check-certificate"))
    urls = []
    for myFile in fileNames:
        urls.append(baseUrl + urllib.quote(myFile))
    cmd += urls

    retCode = Utils.callSubprocess(cmd, retries=maxRetries, cwd=destDir)
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

def deleteRpmSignatures(topDir):
    """Delete signatures of all RPMs under `topDir`"""
    retCode = Utils.callSubprocess(["find", topDir, "-name", "*.rpm",
                                    "-exec", "rpm", "--delsign", "{}", ";"])
    return retCode

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
        maxRetries = getConfig().getIntLimit("max_download_retries", 2)
        retCode = -1
        while retCode != 0 and maxRetries >= 0:
            maxRetries -= 1
            url = cpioUrl % (api, project, target, arch, query)
            retCode = Utils.curlUnpack(url, destDir)

def downloadFulls(api, project, targetArchTuples, fullDir):
    """
    Download the fulls (aka bootstraps) of `project` for each
    target and architecture in `targetArchTuples`.
    A directory named after each target will be created in `fullDir`,
    and a subdirectory for each architecture.
    """
    for target, arch in targetArchTuples:
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

    if rsyncUrl.startswith("http"):
        rejectTample = '--reject "index.html*","*.btih","*.magnet","*.md5","*.meta4","*.metalink","*.mirrorlist","*.sha1","*.sha256","robots.txt"'
        option = "--mirror --no-parent --no-host-directories "
        wgetCmd = 'wget --directory-prefix=%s %s %s --cut-dirs=%s %s'

        url = "%s/%s/%s" % (rsyncUrl, project.replace(":", ":/"), target)

        true_slash_count = url.count('/') - 2 * url.count('//')

        wgetCmd = wgetCmd % (packagesDir, rejectTample, option, true_slash_count, url)

        # TODO: check retCode
        retCode = Utils.callSubprocess(shlex.split(wgetCmd))

    else:
        conf = getConfig()
        rsync = [conf.getCommand("rsync", "rsync")]
        rsync += shlex.split(conf.getCommand("rsync_options", "-aHx"))
        rsync += ["--exclude=*.src.rpm", "--exclude=repocache/",
                  "--exclude=*.repo", "--exclude=repodata/",
                  "--exclude=src/", "--include=*.rpm",
                  "%s/%s/%s/*" % (rsyncUrl, project.replace(":", ":/"), target),
                  "."]
        # TODO: check retCode
        retCode = Utils.callSubprocess(rsync, cwd=packagesDir)

    # Original MDS code was deleting RPM signatures.
    # We do not do it, so RPMs in :full and repositories are the same,
    # and we can make hard links between them.
    #deleteRpmSignatures(packagesDir)

    # TODO: check retCode
    retCode = Utils.callSubprocess(["find", packagesDir,
                                    "-name", "*-debuginfo-*", "-o",
                                    "-name", "*-debugsource-*",
                                    "-exec", "mv", "-f", "{}", debugDir, ";"])

def updateRepositoryMetadata(repoDir):
    """Call 'createrepo' on `repoDir`"""
    # TODO: check retCode
    retCode = Utils.callSubprocess(["createrepo", "--update", repoDir])

def downloadRepositories(rsyncUrl, project, targets, repoDir):
    """Download the RPM repositories of `project` using rsync"""
    for target in targets:
        downloadRepository(rsyncUrl, project, target, repoDir)
        completeRepoDir = os.path.join(repoDir, target, "packages")
        updateRepositoryMetadata(completeRepoDir)
        completeRepoDir = os.path.join(repoDir, target, "debug")
        updateRepositoryMetadata(completeRepoDir)

def downloadPackageFiles(api, project, package, destDir):
    """
    Download source files of `package` of `project` from `api`
    and put them in `destDir`.
    Returns the result of `checkPackageFilesByPath(destDir)`.
    """
    conf = getConfig()
    if not os.path.isdir(destDir):
        os.makedirs(destDir)

    # Download the file index, save it to '_directory'
    indexUrl = "%s/source/%s/%s" % (api, project, package)
    indexPath = os.path.join(destDir, conf.PackageDescriptionFile)
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
    entries = Utils.getEntriesAsDicts(xmlContent)
    baseUrl = urllib.quote("source/%s/%s/" % (project, package))
    baseUrl = "%s/%s" % (api, baseUrl)
    res = downloadFiles(baseUrl,
                        [entry["name"] for entry in entries],
                        destDir)

    # Check everything is OK, and retry files which failed
    maxRetries = conf.getIntLimit("max_download_retries", 2)
    filesInError = checkPackageFilesByPath(destDir)
    while len(filesInError) > 0 and maxRetries > 0:
        pathList = [os.path.basename(x[1]) for x in filesInError]
        res = downloadFiles(baseUrl, pathList, destDir)
        maxRetries -= 1
        filesInError = checkPackageFilesByPath(destDir)
    return filesInError

def downloadPackages(api, project, packagesDir):
    """Download sources of all packages of `project` from `api`"""
    packagesInError = []
    packageList = Utils.getPackageListFromServer(api, project)

    # First make a directory for each package
    for package in packageList:
        packageDir = os.path.join(packagesDir, package)
        if not os.path.isdir(packageDir):
            os.makedirs(packageDir)

    # Then download packages
    for package in packageList:
        packageDir = os.path.join(packagesDir, package)
        try:
            filesInError = downloadPackageFiles(api, project,
                                                package, packageDir)
            if len(filesInError) > 0:
                packagesInError.append((package, filesInError))
        except BaseException as myException:
            packagesInError.append((package, myException))
    return packagesInError

def downloadConfAndMeta(api, project, destDir):
    """Download configuration and meta information about `project`"""
    if not os.path.isdir(destDir):
        os.makedirs(destDir)
    for myFile in ["_meta", "_config"]:
        fileUrl = urllib.quote("source/%s/%s" % (project, myFile))
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
    retCode = Utils.callSubprocess(["sed", "-r", "-i", "-e",
                                    r"s,(<path\s+project=\")fakeobs:,\1,",
                                    metaFilePath])
    # Fix the name of the project, in case user renamed it
    retCode = Utils.callSubprocess(["sed", "-r", "-i", "-e",
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
        myExp = r"s,(<package.+project=\")\S+(\".*),\1%s\2," % project
        res = Utils.callSubprocess(["sed", "-r", "-i", "-e", myExp, metaPath])

def writeProjectInfo(api, rsyncUrl, project, targets, archs, newName):
    """
    Write informations about recently grabbed `newName` project
    in a file, for future use.
    """
    grabTime = time.asctime()
    confParser = ConfigParser.SafeConfigParser()
    confParser.add_section("GrabInfo")
    confParser.set("GrabInfo", "api", api)
    confParser.set("GrabInfo", "rsync_url", rsyncUrl)
    confParser.set("GrabInfo", "project", project)
    confParser.set("GrabInfo", "targets", ",".join(targets))
    if archs is None:
	confParser.set("GrabInfo", "archs", "*")
    else:
	confParser.set("GrabInfo", "archs", ",".join(archs))
    confParser.set("GrabInfo", "date", grabTime)

    confParser.add_section("UpdateInfo")
    confParser.set("UpdateInfo", "last_update", grabTime)
    confParser.set("UpdateInfo", "rsync_update_url", "")
    confParser.set("UpdateInfo", "project", project)

    with open(getConfig().getProjectInfoPath(newName), "wb") as configFile:
        confParser.write(configFile)

def testRsyncUrl(rsyncUrl):
    if rsyncUrl.startswith("http"):
        #TODO Check url
        pass
    else:
        if not Utils.checkRsyncUrl(rsyncUrl):
            msg = "Invalid rsync URL: %s" % rsyncUrl
            raise ValueError(msg)

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

    api = Utils.fixObsPublicApi(api)
    if not Utils.checkObsPublicApi(api):
        raise ValueError("Invalid API: %s" % api)

    testRsyncUrl(rsyncUrl)

    if not Utils.projectExistsOnServer(api, project):
        raise ValueError("Could not find project '%s' on server" % project)

    targetArchTuples = Utils.buildTargetArchTuplesFromServer(api, project,
                                                             targets, archs)
    if len(targetArchTuples) == 0:
        msg = "Invalid target/arch specified, or all disabled on server!"
        raise ValueError(msg)

    targets = {t for t, a in targetArchTuples}
    archs = {a for t, a in targetArchTuples}

    conf = getConfig()
    projectDir = conf.getProjectDir(newName)
    fullDir = conf.getProjectFullDir(newName)
    packagesDir = conf.getProjectPackagesDir(newName)
    repoDir = conf.getProjectRepositoryDir(newName)

    if not os.path.isdir(projectDir):
        os.makedirs(projectDir)
    writeProjectInfo(api, rsyncUrl, project, targets, archs, newName)
    downloadConfAndMeta(api, project, projectDir)
    fixProjectMeta(newName)
    downloadFulls(api, project, targetArchTuples, fullDir)
    downloadPackages(api, project, packagesDir)

    # TODO: check return value of downloadPackages()
    fixProjectPackagesMeta(newName)

    downloadRepositories(rsyncUrl, project, targets, repoDir)
    # findOrphanRpms is a generator
    for orphan in findOrphanRpms(newName):
        pass
    updateLiveRepository(newName)
    try:
        # These operations will fail if program is not run
        # on an OBS server
        updateFakeObsDistributions()
        createFakeObsLink()
    except IOError:
        pass

    return newName


grabGBSKnowledge = {
    "i586": [ "noarch", "i586" ],
    "i686": [ "noarch", "i586", "i686" ],
}


def grabGBSTree(uri, name, targets, archs, orders, verbose=False, force=False):
    """
    Grab a project from an OBS server.
      url:       the URL to fetch for the GBS tree 
                  (ex: http://download.tizen.org/releases/2.0alpha/daily/latest
                   or  rsync://download.tizen.org/snapshots/2.0alpha/common/latest)
      name:      the name to give to the project after it has 
                  been grabbed.
      targets:    a list of build targets to grab
                  (ex: "ia32")
      archs:     a list of architectures to grab
                  (ex: ["i586", "armv7el"])
      orders:    a list of sub projets order
                  (ex: ["tizen-base", "tizen-main"] means that tizen-main depends on tizen-base)
      verbose:   a flag to have verbose messages
      rsynckeep: a flag to keep any rsync data for futur use
    """
    if verbose:
	print "entering grabGBStree(uri={}, name={}, targets={}, archs={}, orders={}, True)".format(uri, name, targets, archs, orders)

    # Test that the project exists not already
    if not force:
	failIfProjectExists(name)

    def localname(n):
	"Compute the local name"
	return n.replace(":", "_")

    # connect to the GbsTree
    options = {
	"verbose":      verbose,
	"should_raise": False,
	"rsynckeep":    True, # FIXME: transmit it correctly
	"archs":	archs,
	"noarchs":	[ "noarch" ]
    }
    gbstree = GbsTree.GbsTree(uri, verbose=verbose, rsynckeep=True, archs=archs)
    if not gbstree.connect():
	raise ValueError(gbstree.error_message)

    # check the archs
    #for a in archs:
    #	if a not in gbstree.built_archs:
    #	    gbstree.disconnect()
    #	    raise ValueError("arch mismatch: '{}' isn't built in {}".format(a,uri))

    # get config data
    conf = getConfig()

    # iterate on GBS repositories: each repository is a subproject
    for repo in gbstree.built_repos:

	# connect to the GBS repository
	gbstree.set_repo(repo)

	# Perform renaming
	subprj = localname(repo)
	prj = name if not subprj else "{}:{}".format(name, subprj)
	if verbose:
	    print "scanning project {} ({}) from repo {}".format(prj, subprj, repo)

	# get root directories
	projectDir = conf.getProjectDir(prj)
	fullDir = conf.getProjectFullDir(prj)
	packagesDir = conf.getProjectPackagesDir(prj)
	repoDir = conf.getProjectRepositoryDir(prj)

	# create the directories
	for d in [ projectDir, fullDir, packagesDir, repoDir ]:
	    if not os.path.isdir(d):
		os.makedirs(d)

	# connect to the source package
	gbstree.set_package("source")
	gbstree.extract_package_rpms_to(packagesDir, prj, True)

	# all archs
	allarchs = archs

	metarepos = []
	# iterate on GBS archs: each arch is a target
	for rtarget in targets:

	    # connect to the GBS acrh
	    gbstree.set_target(rtarget)

	    # Perform renaming
	    ltarget = localname(rtarget)
	    if verbose:
		print "   for target {} (was arch {})".format(ltarget, rtarget)

	    # connect to the DEBUG sub-package
	    gbstree.set_package("debug")
	    dbgdir = os.path.join(repoDir, ltarget, "debug")

	    # download the DEBUG sub-package
	    if not os.path.isdir(dbgdir):
		os.makedirs(dbgdir)
	    gbstree.download_package_to(dbgdir, True) # accept errors for debug and no arch
	    updateRepositoryMetadata(dbgdir) # FIXME: Is it really useful? 

	    # connect to the PACKAGES sub-package
	    gbstree.set_package("packages")
	    pkgdir = os.path.join(repoDir, ltarget, "packages")

	    # check the availables archs
	    (ok, miss, avail) = gbstree.check_package_archs()
	    if not ok:
		raise ValueError("unavailable archs: " + (", ".join(miss)))
	    else:
		if archs:
		    avail = archs
		if allarchs:
		    for a in avail:
			if a not in allarchs:
			    allarchs.append(a)
		else:
		    allarchs = [ a for a in avail ]

	    # download the PACKAGES sub-package
	    if not os.path.isdir(pkgdir):
		os.makedirs(pkgdir)
	    gbstree.download_package_to(pkgdir, False)
	    updateRepositoryMetadata(pkgdir) # FIXME: Is it really useful? 

	    # create the Live directories
	    for a in avail:
		# exract in pkdic the packages list
		knowledge = grabGBSKnowledge[a] if a in grabGBSKnowledge else [ "noarch", a ]
		pkdic = {}
		for pk in gbstree.current_pack_meta["pklist"]:
		    pkarch = pk.get_arch()
		    if pkarch in knowledge:
			n = pk.get_name()
			if n not in pkdic:
			    pkdic[n] = pk
			elif knowledge.index(pkarch) > knowledge.index(pkdic[n].get_arch()):
			    pkdic[n] = pk
		# create the main directory
		fdir = os.path.join(fullDir, ltarget, a)
		if not os.path.isdir(fdir):
		    os.makedirs(fdir)
		# link on packages
		for pk in pkdic.itervalues():
		    ffile = os.path.join(fdir, pk.get_name()) + ".rpm"
		    rfile = os.path.join(pkgdir, pk.get_location())
		    if os.path.lexists(ffile):
			os.unlink(ffile)
		    os.symlink(os.path.relpath(rfile, fdir), ffile)

	    # compute metas
	    metaarchs = "".join(["  <arch>{}</arch>\n".format(a) for a in avail])
	    metapath = []
	    for r in orders:
		r = localname(r)
		if r == subprj:
		    break
		p = name if not r else "{}:{}".format(name, r)
		metapath.append('  <path project="{}" repository="{}"/>\n'.format(p, ltarget))
	    metapath = "".join(metapath)
	    metarepos.append('<repository name="{REPO}">\n{PATHS}{ARCHS} </repository>\n'.format(
		    REPO=ltarget,
		    PATHS=metapath,
		    ARCHS=metaarchs,
		))

	# uri of the repo
	repouri = "{}/{}".format(uri, gbstree.path_repo)

	# Write the project informations
	# TODO: these informations should include the fact that it is a GBS import!
	writeProjectInfo("GBS", uri, prj, targets, archs, prj)

	# write the config file
	gbstree.download_config(os.path.join(projectDir, "_config"))

	# Write the project _meta file
	meta = """<project name="{NAME}">
 <title>GBS grab of {BASE}</title>
 <description>OBS output for GBS grabbed from {BASE}</description>
 <person role="maintainer" userid="unknown" />
 <person role="bugowner" userid="unknown" />
{REPOS}</project>""".format(
		NAME=prj,
		BASE=repouri,
		REPOS="".join(metarepos))
	metaname = os.path.join(projectDir, "_meta")
	f = open(metaname, "w")
	f.write(meta)
	f.close()

	updateLiveRepository(prj)

    try:
        # These operations will fail if program is not run
        # on an OBS server
        updateFakeObsDistributions()
        createFakeObsLink()
    except IOError:
        pass

    return name


def removeProject(project):
    """Remove `project` from fakeobs."""
    conf = getConfig()
    for myDir in {conf.getProjectDir(project),
              conf.getProjectRepositoryDir(project),
              conf.getProjectLiveDir(project)}:
        if os.path.isdir(myDir):
            shutil.rmtree(myDir)
    try:
        updateFakeObsDistributions()
    except IOError:
        pass

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
    replacements = {"archive": destPath, "fakeobs_root": fakeobsRootDir}
    tarCmd = [conf.getCommand("tar")]
    tarCmd += shlex.split(conf.getCommand("tar_create_options",
                                          vars=replacements))
    tarCmd += [projectRelPath, repoRelPath]
    res = Utils.callSubprocess(tarCmd)
    # TODO: check 'res'
    return destPath



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
        replacements = {"archive": archivePath, "fakeobs_root": stagingDir}
        tarCmd = [conf.getCommand("tar")]
        tarCmd += shlex.split(conf.getCommand("tar_extract_options",
                                              vars=replacements))
        res = Utils.callSubprocess(tarCmd)
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
        tmpProjectRepositoryDir = conf.getProjectRepositoryDir(project)
        tmpProjectRepositoryDir = tmpProjectRepositoryDir.replace(
                                                            fakeobsRootDir,
                                                            stagingDir)
        shutil.move(tmpProjectRepositoryDir, projectRepositoryDir)
    finally:
        shutil.rmtree(stagingDir)
    fixProjectMeta(newName)
    fixProjectPackagesMeta(newName)
    updateLiveRepository(newName)
    try:
        # These operations will fail if program is not run
        # on an OBS server
        updateFakeObsDistributions()
        createFakeObsLink()
    except IOError:
        pass
    return newName

def checkProjectConfigAndMeta(project):
    """
    Check for common errors in _meta and _config
    and return a list of error messages.
    """
    errorList = []
    projectDir = getConfig().getProjectDir(project)
    metaPath = os.path.join(projectDir, "_meta")
    if not os.path.exists(metaPath):
        errorList.append(Utils.colorize("Project meta does not exist!", "red"))
    else:
        if os.path.getsize(metaPath) == 0:
            errorList.append(Utils.colorize("Project meta is empty!", "red"))
        else:

            exp = re.compile(r'<path project="fakeobs:')
            found = False
            lineCount = 0
            with open(metaPath, "r") as myFile:
                for line in myFile:
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
                msg = Utils.colorize(msg, "red")
                errorList.append(msg % (lineCount, metaPath))

    configPath = os.path.join(projectDir, "_config")
    if not os.path.exists(configPath):
        errorList.append(Utils.colorize("Project config does not exist!",
                                        "red"))
    else:
        if os.path.getsize(configPath) == 0:
            msg = "Project config is empty, may be a problem "
            msg += "for top-level projects.\n"
            msg += "Please check %s" % configPath
            msg = Utils.colorize(msg, "yellow")
            errorList.append(msg)
    return errorList

def checkProjectFull(project):
    """
    Check for the integrity of project's :full directory.
    """
    errorList = []
    fullDir = getConfig().getProjectFullDir(project)
    if not os.path.isdir(fullDir):
        errorList.append(Utils.colorize("Project :full directory is missing!",
                                        "red"))
        return errorList
    for target in os.listdir(fullDir):
        targetDir = os.path.join(fullDir, target)
        for arch in os.listdir(targetDir):
            archDir = os.path.join(targetDir, arch)
            namesRawFilePath = os.path.join(archDir,
                                            "_repository?view=names")
            if not os.path.exists(namesRawFilePath):
                msg = "The file listing the RPMs is missing for %s %s"
                errorList.append(Utils.colorize(msg % (target, arch), "red"))
                break
            xmlContent = ""
            with open(namesRawFilePath, "r") as myFile:
                xmlContent = myFile.read()
            fileList = Utils.getEntryNameList(xmlContent,
                                              "binary", "filename")
            for fileName in fileList:
                if (fileName.endswith("debuginfo.rpm") or
                    fileName.endswith("debugsource.rpm")):
                    continue
                filePath = os.path.join(archDir, fileName)
                if not os.path.exists(filePath):
                    msg = Utils.colorize("%s is missing" % filePath, "red")
                    errorList.append(msg)
                    continue
                if not fileName.endswith(".rpm"):
                    # File may be a DEB package, 'rpm' doesn't like them...
                    continue
                res = Utils.callSubprocess(["rpm", "--checksig", filePath],
                                           stdout=subprocess.PIPE)
                if res != 0:
                    msg = "%s failed the integrity test" % filePath
                    errorList.append(Utils.colorize(msg, "red"))
    return errorList

def checkProjectRepository(project):
    """
    Check for the integrity of RPMs in project's repository.
    """
    errorList = []
    repoDir = getConfig().getProjectRepositoryDir(project)
    if not os.path.isdir(repoDir):
        msg = "No repository for project %s!" % project
        errorList.append(Utils.colorize(msg, "red"))
        return errorList
    targetList = os.listdir(repoDir)
    if len(targetList) == 0:
        msg = "Repository of %s is empty!" % project
        errorList.append(Utils.colorize(msg, "red"))
        return errorList
    for target in targetList:
        targetDir = os.path.join(repoDir, target)
        repoMdPath = os.path.join(targetDir, "packages",
                                  "repodata", "repomd.xml")
        # Check presence of repomd.xml (can be missing if createrepo failed)
        if not os.path.isfile(repoMdPath):
            msg = "Missing repository metadata file: %s" % repoMdPath
            errorList.append(Utils.colorize(msg, "red"))
        # Check integrity of all RPMs
        for (dirPath, _dirNames, fileNames) in os.walk(targetDir):
            for fileName in fileNames:
                if fileName.endswith(".rpm"):
                    filePath = os.path.join(dirPath, fileName)
                    cmd = ["rpm", "--checksig", filePath]
                    res = Utils.callSubprocess(cmd, stdout=subprocess.PIPE)
                    if res != 0:
                        msg = "%s failed the integrity test" % filePath
                        errorList.append(Utils.colorize(msg, "red"))
    return errorList

def checkPackageFilesByPath(packagePath):
    """
    Check consistency of all files of the package living in `packagePath`.
    Returns a list of tuples like (error_message, path).
    """
    errorList = []
    indexPath = os.path.join(packagePath, getConfig().PackageDescriptionFile)
    try:
        xmlContent = None
        with open(indexPath, "r") as indexFile:
            xmlContent = indexFile.read()
        entries = Utils.getEntriesAsDicts(xmlContent)
    except BaseException as myException:
        msg = "Cannot read file index %s: %s" % (indexPath, str(myException))
        errorList.append((Utils.colorize(msg, "red"), indexPath))
        return errorList

    for entry in entries:
        entryPath = os.path.join(packagePath, entry["name"])
        msg = None
        if not os.path.exists(entryPath):
            msg = "Missing file:\t%s" % entryPath
        elif os.path.getsize(entryPath) != int(entry["size"]):
            msg = "Unexpected file size (%d vs %d):\t%s"
            msg = msg % (os.path.getsize(entryPath),
                         int(entry["size"]),
                         entryPath)
        elif Utils.computeMd5(entryPath) != entry["md5"]:
            msg = "Corrupted file:\t%s" % entryPath
        if msg is not None:
            errorList.append((Utils.colorize(msg, "red"), entryPath))
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
    errorList = []
    for package in getPackageList(project):
        errors = checkPackageFiles(project, package)
        for error in errors:
            errorList.append(error[0])
    return errorList

def checkProjectDependencies(project):
    conf = getConfig()
    errorList = []
    projectList = getProjectList()
    for target in getTargetList(project):
        for dprj, dtarget in getProjectDependencies(project, target):
            if not dprj in projectList:
                msg = "Missing project '%s'" % dprj
                errorList.append(msg)
            elif not dtarget in getTargetList(dprj):
                msg = "Missing target '%s' of project '%s'" % (dtarget, dprj)
                errorList.append(msg)
    return errorList

def getProjectDependencies(project, target):
    """
    Returns the dependencies of `project` for `target`
    as a set of (project, target) tuples.
    """
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
    conf = getConfig()
    for target in getTargetList(project):
        prjLiveDir = conf.getProjectLiveDir(project)
        prjRepoDir = conf.getProjectRepositoryDir(project)
        if not os.path.isdir(prjLiveDir):
            os.makedirs(prjLiveDir)
        linkTarget = os.path.join(prjRepoDir, target, "packages")
        linkTarget = os.path.relpath(linkTarget, prjLiveDir)
        linkName = os.path.join(prjLiveDir, target)
        if os.path.lexists(linkName):
            os.unlink(linkName)
        os.symlink(linkTarget, linkName)

def updateLiveRepositories():
    """Call `updateLiveRepository(project)` on each installed project."""
    for project in getProjectList():
        updateLiveRepository(project)

def findDupes(project):
    """Find duplicates files of `project`, in :full and repository."""
    conf = getConfig()
    dupFinder = Dupes.dupfinder()
    dupFinder.add_dirs([conf.getProjectFullDir(project),
                conf.getProjectRepositoryDir(project)])
    dups = dupFinder.find_dups()
    return dups

def findDupes2(project):
    """
    Find duplicates files of `project`, in :full and repository,
    (by calling fdupes).
    """
    conf = getConfig()
    proc = subprocess.Popen(["fdupes", "-rn",
                             conf.getProjectFullDir(project),
                             conf.getProjectRepositoryDir(project)],
                            stdout=subprocess.PIPE)
    result = proc.communicate()[0]
    lineBlocks = result.split("\n\n")
    dups = []
    for block in lineBlocks:
        dups.append(block.splitlines())
    return dups

def shrinkProject(project, useSymbolicLinks=False):
    """
    Find duplicates files of `project`, in :full and repository,
    and make hard links between them (or symbolic links if
    `useSymbolicLinks` is True).
    """
    conf = getConfig()
    prjFullDir = conf.getProjectFullDir(project)
    prjRepoDir = conf.getProjectRepositoryDir(project)
    dups = findDupes(project)
    linkedRpms = []
    for dup in dups:
        dup1 = [x for x in dup if x.endswith(".rpm")]
        # Check that one RPM comes from :full and
        # the other from repository
        if (len(dup1) >= 2 and
            dup1[0].startswith(prjFullDir) and
            dup1[1].startswith(prjRepoDir)):
            os.remove(dup1[0])
            if useSymbolicLinks:
                os.symlink(dup1[1], dup1[0])
            else:
                os.link(dup1[1], dup1[0])
            linkedRpms.append((dup1[1], dup1[0], os.path.getsize(dup1[1])))
    return linkedRpms

def updateProjectRsyncUrl(project, rsyncUrl=None, oldName=None):
    # TODO: use getUpdateInformations()
    if rsyncUrl is None:
        # User did not provide rsyncUrl.
        # Check if there is one in project_info file
        if not os.path.exists(projectInfoPath):
            msg = "Project '%s' does not have a 'project_info' file."
            msg += " Please specify rsync url."
            msg = msg % project
            raise ValueError(msg)

        msg = "No 'rsync_update_url' parameter in section"
        msg += " 'UpdateInfo' of %s. Please specify rsync url."
        if not confParser.has_option("UpdateInfo", "rsync_update_url"):
            raise ValueError(msg % projectInfoPath)
        rsyncUrl = confParser.get("UpdateInfo", "rsync_update_url")
        if not Utils.isNonEmptyString(rsyncUrl):
            raise ValueError(msg % projectInfoPath)

    testRsyncUrl(rsyncUrl)

    if oldName is None:
        # User may have renamed the project when importing.
        # Check if we know the original name.
        if confParser.has_option("UpdateInfo", "project"):
            tmpOldName = confParser.get("UpdateInfo", "project")
            if Utils.isNonEmptyString(tmpOldName):
                oldName = tmpOldName

    if oldName is None:
        # We did not find old project name,
        # so we guess it's the same
        oldName = project

    rsyncBase = [conf.getCommand("rsync", "rsync")]
    rsyncBase += shlex.split(conf.getCommand("rsync_options", "-acHrx"))

    if oldName == project:
        # Do everything with just one rsync call
        with tempfile.NamedTemporaryFile() as fileListFile:
            # Write the list of directories to synchronize
            # to a temporary file
            prjDir = conf.getProjectDir(project)
            prjRepoDir = conf.getProjectRepositoryDir(project)
            relPrjDir = prjDir[len(fakeObsRoot) + 1:]
            relRepoDir = prjRepoDir[len(fakeObsRoot) + 1:]
            fileListFile.write(relPrjDir + "\n")
            fileListFile.write(relRepoDir + "\n")
            fileListFile.flush()

            # Call rsync using temporary file as input
            rsync = rsyncBase + ["--files-from", fileListFile.name,
                                 '--exclude=project_info',
                                 rsyncUrl, "."]
            res = Utils.callSubprocess(rsync, cwd=fakeObsRoot)
    else:
        # Use separate rsync calls for project and project repositories
        prjDir = conf.getProjectDir(project)
        prjRepoDir = conf.getProjectRepositoryDir(project)
        oldPrjDir = conf.getProjectDir(oldName)
        oldPrjRepoDir = conf.getProjectRepositoryDir(oldName)
        relOldPrjDir = oldPrjDir[len(fakeObsRoot) + 1:]
        relOldPrjRepoDir = oldPrjRepoDir[len(fakeObsRoot) + 1:]
        prjRsync = rsyncBase + ['--exclude=project_info',
                                "%s/%s/" % (rsyncUrl, relOldPrjDir),
                                prjDir]
        repoRsync = rsyncBase + ["%s/%s/" % (rsyncUrl, relOldPrjRepoDir),
                                 prjRepoDir]
        res1 = Utils.callSubprocess(prjRsync, cwd=fakeObsRoot)
        res2 = Utils.callSubprocess(repoRsync, cwd=fakeObsRoot)
        res = res1 or res2
    return res

def updateProject(project, rsyncUrl=None, oldName=None):
    """
    Update a local project from a remote project, using rsync.
    `rsyncUrl` should be a URL to the Fake OBS root ("fakeobs_root"
    parameter of configuration file) of the remote host.
    `oldName` should be the name of the remote project to do the
    update from (local project may have been renamed at import).
    """
    conf = getConfig()
    fakeObsRoot = conf.getFakeObsRootDir()
    projectInfoPath = conf.getProjectInfoPath(project)
    confParser = ConfigParser.SafeConfigParser()
    confParser.read(projectInfoPath)

    res = updateProjectRsyncUrl(project, rsyncUrl, oldName)

    fixProjectMeta(project)
    fixProjectPackagesMeta(project)
    updateLiveRepository(project)

    updateTime = time.asctime()
    confParser.set("UpdateInfo", "last_update", updateTime)
    with open(projectInfoPath, "wb") as configFile:
        confParser.write(configFile)

    return res

def findOrphanRpmsOfTarget(project, target):
    """
    Find RPMs which are in :full but not in repositories,
    for `target` only.
    Yields tuples of (rpm_path_in_full, wanted_rpm_path_in_repo).
    """
    fullDir = getConfig().getProjectFullDir(project)
    repoDir = getConfig().getProjectRepositoryDir(project)
    targetDir = os.path.join(fullDir, target)
    targetRepoDir = os.path.join(repoDir, target, "packages")
    orphans = []
    for arch in os.listdir(targetDir):
        archDir = os.path.join(targetDir, arch)
        namesRawFilePath = os.path.join(archDir,
                                        "_repository?view=names")
        xmlContent = ""
        with open(namesRawFilePath, "r") as myFile:
            xmlContent = myFile.read()
        fileList = Utils.getEntryNameList(xmlContent,
                                          "binary", "filename")
        for fileName in fileList:
            if (fileName.endswith("debuginfo.rpm") or
                fileName.endswith("debugsource.rpm")):
                continue
            filePath = os.path.join(archDir, fileName)
            cmd = ["rpm", "-q", "-p", filePath]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            # remove ending '\n'
            completeName = proc.communicate()[0][:-1]
            rpmArch = completeName.rsplit(".", 1)[-1]
            wantedPath = os.path.join(targetRepoDir, rpmArch, completeName) + ".rpm"
            if not os.path.exists(wantedPath):
                yield (filePath, wantedPath)

def findOrphanRpms(project, useSymbolicLinks=False, dryRun=False):
    """
    Find RPMs which are in :full but not in repositories
    and hardlink them in repositories.
    Yields the RPM names.
    """
    linkFunc = os.symlink if useSymbolicLinks else os.link
    repoDir = getConfig().getProjectRepositoryDir(project)
    for target in getTargetList(project):
        for orphan in findOrphanRpmsOfTarget(project, target):
            if not dryRun:
                linkFunc(orphan[0], orphan[1])
            rpmName = orphan[1].rsplit('/', 1)[-1]
            yield rpmName

        if not dryRun:
            targetRepoDir = os.path.join(repoDir, target, "packages")
            updateRepositoryMetadata(targetRepoDir)
