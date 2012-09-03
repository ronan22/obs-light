#!/usr/bin/python
"""Simple HTTP Server.

This module builds on BaseHTTPServer by implementing the standard GET
and HEAD requests in a fairly straightforward manner.

"""


__version__ = "0.6"

__all__ = ["SimpleHTTPRequestHandler"]

MAPPINGS_FILE = "mappings.xml"
DEFAULT_DIR = "/srv/fakeobs"

import os
import sys
import posixpath
import SocketServer
import BaseHTTPServer
import urllib
import cgi
import time
import shutil
import mimetypes
import urlparse
import uuid

import tempfile
import traceback
import xml.dom.minidom

import Backend
from Config import getConfig, loadConfig
from Utils import createCpio
import BuildInfoManager

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

POST = "POST"
GET = "GET"
HEAD = "HEAD"

DEBUG = 0



class SimpleHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = "fakeobs/" + __version__

    def do_GET(self):
        """Serve a GET request."""
        f = None
        try:
            f = self.send_head(GET)
        except:
            self.send_response(500)
            print "500: " + self.path
            traceback.print_exc(file=sys.stdout)
            self.end_headers()
        if f:
            self.copyfile(f, self.wfile)
            if hasattr(f, "close"):
                f.close()

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head(HEAD)
        if f:
            if hasattr(f, "close"):
                f.close()

    def do_POST(self):
        f = self.send_head(POST)
        if f:
            self.copyfile(f, self.wfile)
            if hasattr(f, "close"):
                f.close()

    # Always returns a stream
    def send_head(self, action):

        def string2stream(thestr):
            content = StringIO()
            content.write(thestr)
            content.seek(0, os.SEEK_END)
            contentsize = content.tell()
            content.seek(0, os.SEEK_SET)
            return contentsize, content

        def file2stream(path):
            f = open(path, 'rb')
            fs = os.fstat(f.fileno())
            # return contentsize, contentmtime, content
            return fs[6], fs.st_mtime, f

        def getCleanPathParts(path):
            pathparts = path.split("/")
            for x in range(0, len(pathparts)):
                pathparts[x] = urllib.unquote(pathparts[x])

            if len(pathparts[0]) == 0:
                pathparts = pathparts[1:]
            if len(pathparts[-1]) == 0:
                pathparts = pathparts[:-1]

            return pathparts

        def getProjectDependency(projectName, targetName):
            result = []
            result.append((projectName, targetName))
            localProjectNamePath = getConfig().getProjectDir(projectName)
            metaPath = localProjectNamePath + "/_meta"
            projects = BuildInfoManager.getProjectDependency(metaPath, targetName)

            for (project, target) in  projects:
                res = getProjectDependency(project, target)
                result.extend(res)

            return result

        content = None
        contentsize = 0
        contentmtime = 0
        contenttype = None
        response = None
        conf = getConfig()

        pathparsed = urlparse.urlparse(self.path)
        path = pathparsed[2]
        if path.startswith("/public"):
            path = path[len("/public"):]

        if self.headers.getheader('Content-Length') is not None:
            data = self.rfile.read(int(self.headers.getheader('Content-Length')))
            query = urlparse.parse_qs(data)
        elif pathparsed[4] is not None:
            query = urlparse.parse_qs(pathparsed[4])
        else:
            query = {}

        #GET /about
        if path.startswith("/about"):
            contentsize, content = string2stream("Fake OBS\n")
            contenttype = "text/html"
            contentmtime = time.time()
        # GET /lastevents
        # TODO: Write lastevents Query.
        # GET /lastevents?filter=XXX&start=YYY
        if path.startswith("/lastevents"):
            if query.has_key("start"):
                if int(query["start"][0]) == Backend.getNextEvent():
                    # Normally OBS would block here, but we just 503 and claim we're busy, 
                    # hoping it comes back
                    self.send_response(503)
                    self.end_headers()
                    return None

                filters = []
                # GET /lastevents?filter=XXX
                if query.has_key("filter"):
                    for x in query["filter"]:
                        spl = x.split('/')
                        if len(spl) == 2:
                            filters.append((urllib.unquote(spl[0]),
                                            urllib.unquote(spl[1]),
                                            None))
                        else:
                            filters.append((urllib.unquote(spl[0]),
                                            urllib.unquote(spl[1]),
                                            urllib.unquote(spl[2])))
                start = int(query["start"][0])
                contentsize, content = string2stream(Backend.getEventsFiltered(start,
                                                                               filters))
                contenttype = "text/html"
                contentmtime = time.time()
            else:
                # GET /lastevents
                output = '<events next="' + str(Backend.getNextEvent()) + '" sync="lost" />\n'

                contentsize, content = string2stream(output)
                contenttype = "text/html"
                contentmtime = time.time()

        #Search
        #
        #    GET /search/project
        #    GET /search/project/id
        #    GET /search/package
        #    GET /search/package/id
        #    GET /search/published/binary/id
        #    GET /search/published/pattern/id
        #    GET /search/request
        #    GET /search/issue
        elif path.startswith("/search"):
            pathparts = getCleanPathParts(path)
            #GET /search/project
            #GET /search/package
            #GET /search/request
            #GET /search/issue
            if len(pathparts) == 2:
                #GET /search/project
                if pathparts[1] == "project":
                    # Only used by OBS Light
                    contentsize, content = string2stream(Backend.buildSearchIndex())
                    contenttype = "text/xml"
                    contentmtime = time.time()
                #GET /search/package
                elif pathparts[1] in {"package", "request", "issue"}:
                    content = None # 404 
            #GET /search/project/id
            #GET /search/package/id
            elif len(pathparts) == 3:
                id = pathparts[2]
                #GET /search/project/id
                if pathparts[1] == "project":
                    content = None # 404 it
                #GET /search/package/id
                elif pathparts[1] == "package":
                    content = None # 404 
            #GET /search/published/binary/id
            #GET /search/published/pattern/id
            elif len(pathparts) == 4:
                id = pathparts[3]
                #GET /search/published/binary/id
                if pathparts[2] == "binary":
                    content = None # 404 it
                #GET /search/published/pattern/id
                elif pathparts[2] == "pattern":
                    content = None # 404

        #Sources 
        #    Projects 
        #        GET /source/ 
        #        GET /source/<project>/_meta 
        #        GET /source/<project>/_attribute/<attribute> 
        #        GET /source/<project>/_config 
        #        GET /source/<project>/_pattern 
        #        GET /source/<project>/_pattern/<patternfile> 
        #        GET /source/<project>/_pubkey 
        #    Packages 
        #        GET /source/<project> 
        #        GET /source/<project>/<package> 
        #        GET /source/<project>/<package>/_meta 
        #        GET /source/<project>/<package>/_attribute/<attribute> 
        #        GET /source/<project>/<package>/_history 
        #    Source files 
        #        GET /source/<project>/<package>/<filename> 
        #        GET /source/<project>/<package>/<binary>/_attribute/<attribute> 
        elif path.startswith("/source"):

            pathparts = getCleanPathParts(path)
            realproject = None

            # GET /source/
            if len(pathparts) == 1:
                contentsize, content = string2stream(Backend.buildProjectIndex())
                contenttype = "text/xml"
                contentmtime = time.time()

            elif len(pathparts) >= 2:
                # find <project>
                realproject = pathparts[1]
                realprojectPath = conf.getProjectDir(realproject)

                if realprojectPath is None:
                    realprojectPath = "--UNKNOWNPROJECT"

                # GET /source/<project> 
                if len(pathparts) == 2:
                    if Backend.projectExists(realproject):
                        contentsize, content = string2stream(Backend.buildPackageIndex(realproject))
                        contenttype = "text/xml"
                        contentmtime = time.time()
                # package or metadata for project
                #GET /source/<project>/_meta 
                #GET /source/<project>/_config
                #GET /source/<project>/_pattern
                #GET /source/<project>/_pubkey
                #GET /source/<project>/<package>
                elif len(pathparts) == 3:
                    # GET /source/<project>/_meta
                    if pathparts[2] == "_meta":
                        contentsize, content = string2stream(Backend.getProjectMeta(realproject))
                        contenttype = "text/xml"
                        contentmtime = time.time()
                    # GET /source/<project>/_config
                    elif pathparts[2] == "_config":
                        contentsize, contentmtime, content = file2stream(realprojectPath + "/_config")
                        contenttype = "text/plain"
                    # GET /source/<project>/_pubkey
                    # GET /source/<project>/_pattern
                    elif pathparts[2] in {"_pubkey", "_pattern"}:
                        content = None # 404 it
                    # GET /source/<project>/<package>
                    else:
                        packageName = pathparts[2]
                        expand = 0
                        rev = None
                        # GET /source/<project>/<package>?expand=[0 1]
                        if query.has_key("expand"):
                            expand = int(query["expand"][0])
                        # GET /source/<project>/<package>?rev=XX
                        if query.has_key("rev"):
                            rev = query["rev"][0]

                        contentsize, content = string2stream(Backend.buildFileIndex(realproject,
                                                                                    packageName))
                        contenttype = "text/xml"
                        contentmtime = time.time()
                # GET /source/<project>/_attribute/<attribute> 
                # GET /source/<project>/_pattern/<patternfile>            
                # GET /source/<project>/<package>/_meta 
                # GET /source/<project>/<package>/_history 
                # GET /source/<project>/<package>/<filename> 
                elif len(pathparts) == 4:
                    # GET /source/<project>/_attribute/<attribute>
                    # GET /source/<project>/_pattern/<patternfile>
                    if pathparts[2] in {"_attribute", "_pattern"}:
                        attribute = pathparts[3]
                        content = None # 404 it

                    # GET /source/<project>/<package>/_meta 
                    # GET /source/<project>/<package>/_history 
                    # GET /source/<project>/<package>/<filename> 
                    else:
                        packageName = pathparts[2]

                        # GET /source/<project>/<package>/_history
                        if pathparts[3] == "_history":
                            content = None # 404 it
                        # GET /source/<project>/<package>/<filename> 
                        else:
                            filename = pathparts[3]
                            rev = None
                            expand = 0
                            #GET /source/<project>/<package>/<filename>?expand=[0 1]
                            if query.has_key("expand"):
                                expand = int(query["expand"][0])
                            #GET /source/<project>/<package>/<filename>?rev=XX
                            if query.has_key("rev"):
                                rev = query["rev"][0]

                            filePath = Backend.getPackageFilePath(realproject,
                                                                  packageName,
                                                                  filename)
                            if os.path.isfile(filePath):
                                contentsize, contentmtime, content = file2stream(filePath)
                            else:
                                content = None

                            if filename == "_meta":
                                contenttype = "text/xml"
                                # XXX: do we need to update contentmtime ?
                                contentmtime = time.time()

                # GET /source/<project>/<package>/_attribute/<attribute>
                elif len(pathparts) == 5:
                    content = None # 404 it
                # GET /source/<project>/<package>/<binary>/_attribute/<attribute>
                elif len(pathparts) == 6:
                    content = None # 404 it

        #Build Results
        #    GET /build/
        #    GET /build/_workerstatus
        #    GET /build/<project>
        #    GET /build/<project>/<repository>
        #    GET /build/<project>/<repository/<arch>
        #    Binaries
        #        GET /build/<project>/<repository>/<arch>/<package>
        #        GET /build/<project>/<repository>/<arch>/<package>/<binaryname>
        #        GET /build/<project>/<repository>/<arch>/<package>/<binaryname>?view=fileinfo
        #        GET /build/<project>/<repository>/<arch>/<package>/<binaryname>?view=fileinfo_ext
        #        GET /build/<project>/<repository>/<arch>/_builddepinfo?package=<package>
        #        GET /build/<project>/<repository>/<arch>/_jobhistory?package=<package>&code=succeeded&limit=10
        #        GET /build/<project>/<repository>/<arch>/_repository
        #        GET /build/<project>/<repository>/<arch>/_repository/<binaryname>
        #    Status
        #        GET /build/<project>/_result
        #        GET /build/<project>/<repository>/<arch>/<package>/_history
        #        GET /build/<project>/<repository>/<arch>/<package>/_reason
        #        GET /build/<project>/<repository>/<arch>/<package>/_status
        #        GET /build/<project>/<repository>/<arch>/<package>/_log
        #    Local Build
        #        GET /build/<project>/<repository>/<arch>/<package>/_buildinfo
        #        POST /build/<project>/<repository>/<arch>/<package>/_buildinfo
        #    Repository Information
        #        GET /build/<project>/<repository>/<arch>/_repository/<binaryname>
        #        GET /build/<project>/<repository>/<arch>/_builddepinfo
        elif path.startswith("/build"):
            pathparts = getCleanPathParts(path)
            #/public/build/Mer:Trunk:Base/standard/i586/_repository?view=cache
            # GET /build/
            if len(pathparts) == 1:
                content = None # 404 it
            # GET /build/_workerstatus
            # GET /build/<project>
            if len(pathparts) == 2:
                # GET /build/_workerstatus
                if pathparts[1] == "_workerstatus":
                    content = None # 404 it
                # GET /build/<project>
                else:
                    projectName = pathparts[1]
                    contentsize, content = string2stream(Backend.buildTargetIndex(projectName))
                    contenttype = "text/xml"
                    contentmtime = time.time()

            if len(pathparts) >= 3:
                projectName = pathparts[1]
                projectNamePath = conf.getProjectFullDir(projectName)
                localProjectNamePath = conf.getProjectDir(projectName)

                if projectNamePath is None:
                    projectNamePath = "--UNKNOWNPROJECT"

                # GET /build/<project>/_result
                # GET /build/<project>/<repository>
                if len(pathparts) == 3:
                    # GET /build/<project>/_result
                    if pathparts[2] == "_result":
                        content = None # 404 it
                    # GET /build/<project>/<repository>
                    else:
                        repository = pathparts[2]
                        contentsize, content = string2stream(Backend.buildArchIndex(projectName,
                                                                                    repository))
                        contenttype = "text/xml"
                        contentmtime = time.time()

                if len(pathparts) >= 4:
                    repository = pathparts[2]
                    # GET /build/<project>/<repository>/<arch>
                    # GET /build/<project>/<repository>/_buildconfig
                    if len(pathparts) == 4:
                        if pathparts[3] == "_buildconfig":
                            buildconfig = Backend.getRecursiveProjectConfig(projectName,
                                                                            repository)
                            contentsize, content = string2stream(buildconfig)
                            contenttype = "text/plain"
                            contentmtime = time.time()
                        else:
                            arch = pathparts[3]
                            content = None # 404 it

                    # GET /build/<project>/<repository>/<arch>/_repository
                    # GET /build/<project>/<repository>/<arch>/_builddepinfo
                    # GET /build/<project>/<repository>/<arch>/_builddepinfo?package=<package>
                    # GET /build/<project>/<repository>/<arch>/_jobhistory?package=<package>&code=succeeded&limit=10
                    # GET /build/<project>/<repository>/<arch>/<package>
                    elif len(pathparts) == 5:
                        arch = pathparts[3]
                        # GET /build/<project>/<repository>/<arch>/_repository
                        if pathparts[4] == "_repository":
                            arch = pathparts[3]
                            emptyrepositorycache = "tools/emptyrepositorycache.cpio"
                            # GET /build/<project>/<repository>/<arch>/_repository?view=cache
                            if query.has_key("view") and query["view"][0] == "cache":
                                filePath = os.path.join(projectNamePath,
                                                        repository,
                                                        arch,
                                                        "_repository?view=cache")

                                if os.path.isfile(filePath):
                                    contentsize, contentmtime, content = file2stream(filePath)
                                    contenttype = "application/octet-stream"
                                else:
                                    contentsize, contentmtime, content = file2stream(emptyrepositorycache)
                                    contenttype = "application/octet-stream"
                            # GET /build/<project>/<repository>/<arch>/_repository?view=solvstate
                            elif query.has_key("view") and query["view"][0] == "solvstate":
                                filePath = os.path.join(projectNamePath ,
                                                         repository ,
                                                         arch ,
                                                         "_repository?view=solvstate")
                                if os.path.isfile(filePath):
                                    contentsize, contentmtime, content = file2stream(filePath)
                                    contenttype = "application/octet-stream"
                                else:
                                    contentsize, contentmtime, content = file2stream(emptyrepositorycache)
                                    contenttype = "application/octet-stream"
                            # GET /build/<project>/<repository>/<arch>/_repository?view=cpio&binary=XXX
                            elif query.has_key("binary") and query.has_key("view") and query["view"][0] == "cpio":
                                binaries = ""
                                for x in query["binary"]:
                                    filePath = os.path.join(projectNamePath,
                                                            repository,
                                                            arch,
                                                            os.path.basename(x) + ".rpm")
                                    if os.path.isfile(filePath):
                                        assert filePath + " was not found"
                                    binaries = binaries + os.path.basename(x) + ".rpm\n"

                                path = os.path.join(projectNamePath , repository , arch)
                                with tempfile.NamedTemporaryFile("w", suffix=".cpio") as cpioFile:
                                    res = createCpio(cpioFile, binaries, path)
                                    # cpioFile is delete after this block but it is still open
                                    # and readable ('content' is a file-object)
                                    contentsize, contentmtime, content = file2stream(cpioFile.name)
                                contenttype = "application/x-cpio"
                                ##
                            # GET /build/<project>/<repository>/<arch>/_repository?view=names&binary=XXX
                            elif (query.has_key("binary") and
                                  query.has_key("view") and
                                  query["view"][0] == "names"):
                                filePath = os.path.join(projectNamePath ,
                                                        repository ,
                                                        arch ,
                                                        "_repository?view=names")
                                if os.path.isfile(filePath):
                                    doc = xml.dom.minidom.parse(filePath)
                                    removables = []
                                    for x in doc.getElementsByTagName("binary"):
                                        if not os.path.splitext(x.attributes["filename"].value)[0] in query["binary"]:
                                            removables.append(x)
                                    for x in removables:
                                        doc.childNodes[0].removeChild(x)
                                    contentsize, content = string2stream(doc.childNodes[0].toxml())
                                    contentmtime = time.time()
                                    contenttype = "text/html"
                                else:
                                    contentsize, content = string2stream("<binarylist />")
                                    contenttype = "text/html"
                                    contentmtime = time.time()
                            # GET /build/<project>/<repository>/<arch>/_repository?view=binaryversions&binary=XXX
                            elif query.has_key("binary") and\
                                 query.has_key("view") and\
                                 query["view"][0] == "binaryversions":
                                filePathCache = os.path.join(projectNamePath ,
                                                             repository ,
                                                             arch ,
                                                             "_repository?view=cache")
                                filePathBin = os.path.join(projectNamePath ,
                                                           repository ,
                                                           arch ,
                                                           "_repository?view=binaryversions")
                                if os.path.isfile(filePathCache):
                                    doc = xml.dom.minidom.parse(filePathBin)
                                    removables = []
                                    for x in doc.getElementsByTagName("binary"):
                                        if not os.path.splitext(x.attributes["name"].value)[0] in query["binary"]:
                                            removables.append(x)
                                    for x in removables:
                                        doc.childNodes[0].removeChild(x)
                                    contentsize, content = string2stream(doc.childNodes[0].toxml())
                                    contentmtime = time.time()
                                    contenttype = "text/html"
                                else:
                                    contentsize, content = string2stream("<binaryversionlist />")
                                    contenttype = "text/html"
                                    contentmtime = time.time()
                            else:
                                filePath = os.path.join(projectNamePath ,
                                                         repository ,
                                                         arch ,
                                                         "_repository?view=names")
                                if os.path.isfile(filePath):
                                    contentsize, contentmtime, content = file2stream(filePath)
                                    contenttype = "application/octet-stream"
                                else:
                                    contentsize, contentmtime, content = file2stream(emptyrepositorycache)
                                    contenttype = "application/octet-stream"
                        # GET /build/<project>/<repository>/<arch>/_builddepinfo
                        # GET /build/<project>/<repository>/<arch>/_builddepinfo?package=<package>
                        elif pathparts[4] == "_builddepinfo":
                            content = None # 404 it
                        # GET /build/<project>/<repository>/<arch>/_jobhistory?package=<package>&code=succeeded&limit=10
                        elif pathparts[4] == "_jobhistory":
                            content = None # 404 it
                        # GET /build/<project>/<repository>/<arch>/<package>
                        else:
                            package = pathparts[4]
                            content = None # 404 it
                    # GET /build/<project>/<repository>/<arch>/_repository/<binaryname>
                    # GET /build/<project>/<repository>/<arch>/<package>/_history
                    # GET /build/<project>/<repository>/<arch>/<package>/_reason
                    # GET /build/<project>/<repository>/<arch>/<package>/_status
                    # GET /build/<project>/<repository>/<arch>/<package>/_log
                    # GET /build/<project>/<repository>/<arch>/<package>/_buildinfo
                    # POST /build/<project>/<repository>/<arch>/<package>/_buildinfo
                    # GET /build/<project>/<repository>/<arch>/<package>/<binaryname>
                    # GET /build/<project>/<repository>/<arch>/<package>/<binaryname>?view=fileinfo
                    # GET /build/<project>/<repository>/<arch>/<package>/<binaryname>?view=fileinfo_ext
                    elif len(pathparts) == 6:
                        arch = pathparts[3]
                        # GET /build/<project>/<repository>/<arch>/_repository/<binaryname>
                        if pathparts[4] == "_repository" and pathparts[5] != "_buildinfo":
                            binaryname = pathparts[5]
                            content = None # 404 it
                        else:
                            packageName = pathparts[4]
                            # GET /build/<project>/<repository>/<arch>/<package>/_history
                            if pathparts[5] == "_history":
                                content = None # 404 it
                            # GET /build/<project>/<repository>/<arch>/<package>/_reason
                            elif pathparts[5] == "_reason":
                                content = None # 404 it
                            # GET /build/<project>/<repository>/<arch>/<package>/_status
                            elif pathparts[5] == "_status":
                                msg = '<status package="%s" code="Unknown"><details></details></status>'
                                contentsize, content = string2stream(msg % projectName)
                                contentmtime = time.time()
                                contenttype = "text/html"

                            # GET /build/<project>/<repository>/<arch>/<package>/_log
                            elif pathparts[5] == "_log":
                                content = None # 404 it
                            # GET /build/<project>/<repository>/<arch>/<package>/_buildinfo
                            # GET /build/<project>/<repository>/<arch>/<package>/_buildinfo?add=package
                            # POST /build/<project>/<repository>/<arch>/<package>/_buildinfo
                            # POST /build/<project>/<repository>/<arch>/<package>/_buildinfo?add=package
                            elif pathparts[5] == "_buildinfo":
                                if action == POST:
                                    specFileContent = data
                                    #TODO:Find Spec file Name.
                                    specFileName = None
                                    rev = None
                                    srcmd5 = None
                                else:
                                    specFileName = Backend.getProjectSpecFile(projectName,
                                                                              packageName)
                                    specFilePath = Backend.getPackageFilePath(projectName,
                                                                              packageName,
                                                                              specFileName)
                                    specFileContent = ""
                                    with open(specFilePath, "r") as f:
                                        specFileContent = f.read()

                                    rev, srcmd5 = Backend.getPackageLastRevSrcmd5(projectName,
                                                                                  packageName)

                                with tempfile.NamedTemporaryFile("w",
                                                                 delete=False,
                                                                 suffix=".spec") as tmpSpecFile:
                                    tmpSpecFile.write(specFileContent)

                                repo = BuildInfoManager.getLocalRepositoryUrl()

                                repositoryList = []
                                with tempfile.NamedTemporaryFile("w",
                                                                 delete=False,
                                                                 suffix=".config") as tmpConfFile:
                                    configStr = Backend.getRecursiveProjectConfig(projectName,
                                                                                  repository)
                                    tmpConfFile.write(configStr)

                                for (prj, target) in Backend.getProjectDependencies(projectName,
                                                                                    repository):
                                    extPrj = prj.replace(":", ":/")
                                    repositoryList.append(repo + "/" + extPrj + "/" + target)

                                if query.has_key("add"):
                                    addPackages = query["add"]
                                else:
                                    addPackages = []
                                xmlRes = BuildInfoManager.getbuildInfo(rev,
                                                                       srcmd5,
                                                                       specFileName,
                                                                       repositoryList,
                                                                       tmpConfFile.name,
                                                                       localProjectNamePath + "/_rpmcache",
                                                                       arch,
                                                                       projectName,
                                                                       packageName,
                                                                       repository,
                                                                       tmpSpecFile.name,
                                                                       addPackages)
                                os.unlink(tmpSpecFile.name)
                                os.unlink(tmpConfFile.name)

                                contentsize, content = string2stream(xmlRes)
                                contentmtime = time.time()
                                contenttype = "text/html"

                            # GET /build/<project>/<repository>/<arch>/<package>/<binaryname>
                            # GET /build/<project>/<repository>/<arch>/<package>/<binaryname>?view=fileinfo
                            # GET /build/<project>/<repository>/<arch>/<package>/<binaryname>?view=fileinfo_ext
                            else:
                                binaryname = pathparts[5]
                                content = None # 404 it

        if content is None:
            print "404: path"
            self.send_error(404, "File not found")
            return None

        if response is None:
            self.send_response(200)
        else:
            self.send_response(response)
        self.send_header("Content-type", contenttype)
        self.send_header("Content-Length", contentsize)
        self.send_header("Last-Modified", self.date_time_string(contentmtime))
        self.end_headers()
        return content

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        shutil.copyfileobj(source, outputfile)

class XFSPWebServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass

def getProjectsTargetsAndReleases():
    """
    Get a list of tuples of the form
      ("extended:/project:/name", "target", "release")
    """
    PTRList = []
    for release in os.listdir("releases"):
        releasePath = os.path.join("releases", release)
        if (releasePath in ["repositories", "latest", "latest-release"] or
                not os.path.isdir(releasePath)):
            continue
        buildsPath = os.path.join(releasePath, "builds")
        for entry in os.walk(releasePath):
            if not "packages" in entry[1]:
                continue
            project = os.path.dirname(entry[0][len(buildsPath) + 1:])
            target = os.path.basename(entry[0])
            PTRList.append((project, target, release))
    return PTRList

def updateRepository(extProject, target, release):
    """
    Create/update a directory hierarchy suitable for use as an OBS live
    RPM repository, based on actual repositories, suitables for image
    generation by MIC.
    """
    extPrjRepo = os.path.join("releases", "repositories", extProject)
    if not os.path.isdir(extPrjRepo):
        os.makedirs(extPrjRepo)
    linkTarget = "../" * (extProject.count(':/') + 2)
    linkTarget = os.path.join(linkTarget, release, "builds", extProject, target, "packages")
    linkName = os.path.join(extPrjRepo, target)
    print linkName, " -> ", linkTarget
    if os.path.lexists(linkName):
        os.unlink(linkName)
    os.symlink(linkTarget, linkName)

def updateRepositories():
    for ptr in getProjectsTargetsAndReleases():
        updateRepository(*ptr)

if __name__ == "__main__":
    # TODO: use an option parser and add quiet/verbose modes
    if len(sys.argv) > 1:
        loadConfig(sys.argv[1])
    else:
        loadConfig()
    conf = getConfig()
    Backend.updateLiveRepositories()

    httpd = XFSPWebServer(("0.0.0.0", conf.getPort("api_port", 8001)),
                          SimpleHTTPRequestHandler)
    httpd.serve_forever()
