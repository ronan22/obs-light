#!/usr/bin/python
"""Simple HTTP Server.

This module builds on BaseHTTPServer by implementing the standard GET
and HEAD requests in a fairly straightforward manner.

"""


__version__ = "0.6"

__all__ = ["SimpleHTTPRequestHandler"]

MAPPINGS_FILE = "mappings.xml"
DEFAULT_DIR = "/srv/fakeobs"

import os, sys
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
import gitmer
import subprocess
import xml.dom.minidom
import os
import traceback
import rpmManager
import tempfile

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
        def lookup_path(projectname):
            doc = xml.dom.minidom.parse(MAPPINGS_FILE)
            for x in doc.getElementsByTagName("mapping"):
                if x.attributes["project"].value == projectname:
                    return x.attributes["path"].value
            return None
        def lookup_binariespath(projectname):
            doc = xml.dom.minidom.parse(MAPPINGS_FILE)
            for x in doc.getElementsByTagName("mapping"):
                if x.attributes["project"].value == projectname:
                    return x.attributes["binaries"].value
            return None
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
            localProjectNamePath = lookup_path(projectName)
            metaPath = localProjectNamePath + "/_meta"
            projects = rpmManager.getProjectDependency(metaPath, targetName)

            for (project, target) in  projects:
                res = getProjectDependency(project, target)
                result.extend(res)

            return result

        content = None
        contentsize = 0
        contentmtime = 0
        contenttype = None
        response = None

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
        #GET /lastevents
        #TODO: Write lastevents Query.
        #GET /lastevents?filter=XXX&start=YYY
        if path.startswith("/lastevents"):
            if query.has_key("start"):
                if int(query["start"][0]) == gitmer.get_next_event():
                        # Normally OBS would block here, but we just 503 and claim we're busy, 
                        # hoping it comes back
                        self.send_response(503)
                        self.end_headers()
                        return None

                filters = []
                #GET /lastevents?filter=XXX
                if query.has_key("filter"):
                    for x in query["filter"]:
                        spl = x.split('/')
                        if len(spl) == 2:
                            filters.append((urllib.unquote(spl[0]), urllib.unquote(spl[1]), None))
                        else:
                            filters.append((urllib.unquote(spl[0]), urllib.unquote(spl[1]), urllib.unquote(spl[2])))
                contentsize, content = string2stream(gitmer.get_events_filtered(int(query["start"][0]), filters))
                contenttype = "text/html"
                contentmtime = time.time()
            else:
                #GET /lastevents
                output = '<events next="' + str(gitmer.get_next_event()) + '" sync="lost" />\n'

                contentsize, content = string2stream(output)
                contenttype = "text/html"
                contentmtime = time.time()

        #Architectures
        #    GET /architecture
        #    GET /architecture/<name>


        #Issue Trackers
        #
        #    GET /issue_trackers
        #    GET /issue_trackers/<name>
        #    PUT /issue_tracker/<name>
        #    POST /issue_tracker/<name>
        #    DELETE /issue_tracker/<name>
        #    GET /issue_trackers/show_url_for

        #Distribution List
        #
        #    GET /distributions

        #User data
        #
        #    GET /person/<userid>
        #    PUT /person/<userid>
        #    GET /person/<userid>/<groupid>
        #    POST /person/register
        #    PUT /person/register
        #    PUT /person/changepasswd
        #    POST /person/changepasswd

        #Requests
        #
        #    GET /request
        #    GET /request/<id>
        #    POST /request
        #    PUT /request/<id>
        #    POST /request/<id>?cmd=diff
        #    POST /request/<id>
        #    DELETE /request/<id>

        #Attribute definition api
        #
        #    GET /attribute/
        #    GET /attribute/<namespace>/
        #    GET /attribute/<namespace>/_meta
        #    DELETE /attribute/<namespace>/_meta
        #    PUT /attribute/<namespace>/_meta
        #    GET /attribute/<namespace>/<name>/_meta
        #    DELETE /attribute/<namespace>/<name>/_meta
        #    PUT /attribute/<namespace>/<name>/_meta

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
                    #Only used for OBS Light
                    contentsize, content = string2stream(gitmer.build_fake_OBS_search(MAPPINGS_FILE))
                    contenttype = "text/xml"
                    contentmtime = time.time()
                #GET /search/package
                elif pathparts[1] == "package":
                    content = None # 404 
                #GET /search/request
                elif pathparts[1] == "request":
                    content = None # 404 it
                #GET /search/issue
                elif pathparts[1] == "issue":
                    content = None # 404 it
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

            #GET /source/
            if len(pathparts) == 1:
                contentsize, content = string2stream(gitmer.build_fake_OBS_index(MAPPINGS_FILE))
                contenttype = "text/xml"
                contentmtime = time.time()

            elif len(pathparts) >= 2:
                # find <project>
                realproject = pathparts[1]
                realprojectPath = lookup_path(pathparts[1])

                if realprojectPath is None:
                     realprojectPath = "--UNKNOWNPROJECT"

                #GET /source/<project> 
                if len(pathparts) == 2:
                    path = realprojectPath + "/packages.xml"
                    if os.path.isfile(path):
                          contentsize, content = string2stream(gitmer.build_project_index(realprojectPath))
                          contenttype = "text/xml"
                          contentmtime = time.time()
                # package or metadata for project
                #GET /source/<project>/_meta 
                #GET /source/<project>/_config
                #GET /source/<project>/_pattern
                #GET /source/<project>/_pubkey
                #GET /source/<project>/<package>
                elif len(pathparts) == 3:
                    #GET /source/<project>/_meta
                    if pathparts[2] == "_meta":
                        contentsize, content = string2stream(gitmer.adjust_meta(realprojectPath, realproject))
                        contenttype = "text/xml"
                        contentmtime = time.time()
                    #GET /source/<project>/_config
                    elif pathparts[2] == "_config":
                        contentsize, contentmtime, content = file2stream(realprojectPath + "/_config")
                        contenttype = "text/plain"
                    #GET /source/<project>/_pubkey
                    elif pathparts[2] == "_pubkey":
                        content = None # 404 it
                    #GET /source/<project>/_pattern
                    elif pathparts[2] == "_pattern":
                        content = None # 404 it
                    #GET /source/<project>/<package>
                    else:
                        packageName = pathparts[2]
                        expand = 0
                        rev = None
                        #GET /source/<project>/<package>?expand=[0 1]
                        if query.has_key("expand"):
                            expand = int(query["expand"][0])
                        #GET /source/<project>/<package>?rev=XX
                        if query.has_key("rev"):
                            rev = query["rev"][0]

                        contentsize, content = string2stream(gitmer.get_package_index_supportlink(realprojectPath, packageName , rev, expand))
                        contenttype = "text/xml"
                        contentmtime = time.time()
                # GET /source/<project>/_attribute/<attribute> 
                # GET /source/<project>/_pattern/<patternfile>            
                # GET /source/<project>/<package>/_meta 
                # GET /source/<project>/<package>/_history 
                # GET /source/<project>/<package>/<filename> 
                elif len(pathparts) == 4:
                    # GET /source/<project>/_attribute/<attribute>
                    if pathparts[2] == "_attribute":
                        attribute = pathparts[3]
                        content = None # 404 it
                    # GET /source/<project>/_pattern/<patternfile> 
                    elif pathparts[2] == "_pattern":
                        patternfile = pathparts[3]
                        content = None # 404 it
                    # GET /source/<project>/<package>/_meta 
                    # GET /source/<project>/<package>/_history 
                    # GET /source/<project>/<package>/<filename> 
                    else:
                        packageName = pathparts[2]
                        # GET /source/<project>/<package>/_meta

                        if pathparts[3] == "_meta":
                            contentsize, content = string2stream(gitmer.get_package_meta(realprojectPath, packageName))
                            contenttype = "text/xml"
                            contentmtime = time.time()

                        # GET /source/<project>/<package>/_history
                        elif pathparts[3] == "_history":
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

                            contentsize, contentst = gitmer.get_package_file(realproject, realprojectPath, packageName, filename, rev)
                            if contentsize is None:
                                content = None
                            else:
                                contentz, content = string2stream(contentst)
                                contenttype = "application/octet-stream"
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
                    contentsize, content = string2stream(gitmer.build_fake_OBS_repo(MAPPINGS_FILE, projectName))
                    contenttype = "text/xml"
                    contentmtime = time.time()

            if len(pathparts) >= 3:
                projectName = pathparts[1]
                projectNamePath = lookup_binariespath(projectName)
                localProjectNamePath = lookup_path(projectName)

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
                        pathMeta = os.path.join(localProjectNamePath, "_meta")
                        contentsize, content = string2stream(gitmer.build_fake_OBS_arch(pathMeta, repository))
                        contenttype = "text/xml"
                        contentmtime = time.time()

                if len(pathparts) >= 4:
                    repository = pathparts[2]
                    # GET /build/<project>/<repository/<arch>
                    # GET /build/<project>/<repository>/_buildconfig
                    if len(pathparts) == 4:
                        if pathparts[3] == "_buildconfig":
                           _config = ""
                           for (prj, target) in getProjectDependency(projectName, repository):
                               localPrjNamePath = lookup_path(prj)
                               with open(localPrjNamePath + "/_config", 'r') as f:
                                   _config += f.read() + "\n"

                           contentsize, content = string2stream(_config)
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
                                filePath = os.path.join(projectNamePath ,
                                                         repository ,
                                                         arch ,
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
                                    filePath = os.path.join(projectNamePath ,
                                                             repository ,
                                                             arch ,
                                                             os.path.basename(x) + ".rpm")
                                    if os.path.isfile(filePath):
                                        assert filePath + " was not found"
                                    binaries = binaries + os.path.basename(x) + ".rpm\n"

                                path = os.path.join(projectNamePath , repository , arch)
                                cpiooutput = subprocess.Popen(["tools/createcpio", path],
                                                               stdin=subprocess.PIPE,
                                                               stdout=subprocess.PIPE).communicate(binaries)[0]
#                               cpiooutput = subprocess.Popen(["/usr/bin/curl", "http://192.168.100.213:81/public/build/Core:i586/Core_i586/i586/_repository?" + pathparsed[4]], stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
                                contentsize, content = string2stream(cpiooutput)
                                print contentsize
                                contentmtime = time.time()
                                contenttype = "application/x-cpio"
                                ##
                            # GET /build/<project>/<repository>/<arch>/_repository?view=names&binary=XXX
                            elif query.has_key("binary") and\
                                 query.has_key("view") and\
                                 query["view"][0] == "names":
                                filePath = os.path.join(projectNamePath ,
                                                        repository ,
                                                        arch ,
                                                        "_repository?view=names")
                                if os.path.isfile(filePath):
                                    print filePath
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
                                contentsize, content = string2stream('<status package="%s" code="Unknown"><details></details></status>' % projectName)
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
                                   specfile = data
                                   #TODO:Find Spec file Name.
                                   specFile = None
                                   rev = None
                                   srcmd5 = None
                               else:
                                   specfile = gitmer.getSpecFile(localProjectNamePath, packageName)
                                   specFile = gitmer.getSpecName(localProjectNamePath, packageName)
                                   rev, srcmd5 = gitmer.getPackageLastRevSrcmd5(localProjectNamePath, packageName)


                               with tempfile.NamedTemporaryFile("w", delete=False, suffix=".spec") as specWriter:
                                    specWriter.write(specfile)

                               repo = rpmManager.getLocalRepoHost()

                               listRepository = []
                               with tempfile.NamedTemporaryFile("w", delete=False, suffix=".config") as confWriter:
                                   for (prj, target) in getProjectDependency(projectName, repository):
                                       listRepository.append(repo + "/" + prj.replace(":", ":/") + "/" + target)
                                       localPrjNamePath = lookup_path(prj)
                                       with  open(localPrjNamePath + "/_config", 'r') as f:
                                           _configStr = f.read()
                                           confWriter.write(_configStr + "\n")

                               if query.has_key("add"):
                                   addPackages = query["add"]
                               else:
                                   addPackages = []
                               xmlRes = rpmManager.getbuildInfo(rev,
                                                                srcmd5,
                                                                specFile,
                                                                listRepository,
                                                                confWriter.name,
                                                                localProjectNamePath + "/_rpmcache",
                                                                arch,
                                                                projectName,
                                                                packageName,
                                                                repository,
                                                                specWriter.name,
                                                                addPackages)
                               specWriter.close()
                               os.unlink(specWriter.name)
                               confWriter.close()
                               os.unlink(confWriter.name)

                               contentsize, content = string2stream(xmlRes)
                               contentmtime = time.time()
                               contenttype = "text/html"

                            # GET /build/<project>/<repository>/<arch>/<package>/<binaryname>
                            # GET /build/<project>/<repository>/<arch>/<package>/<binaryname>?view=fileinfo
                            # GET /build/<project>/<repository>/<arch>/<package>/<binaryname>?view=fileinfo_ext
                            else:
                                binaryname = pathparts[5]
                                content = None # 404 it

        #Published binary package tree
        #
        #    GET /published
        #    GET /published/<project>
        #    GET /published/<project>/<repository>
        #    GET /published/<project>/<repository>/<arch>
        #    GET /published/<project>/<repository>/<arch>/<binary>
        #    GET /published/<project>/<repository>/<arch>/<binary>?view=ymp

        #Tags
        #
        #    GET /source/<project>/_tags
        #    GET /source/<project>/<package>/_tags
        #    GET /tag/<tag>/_projects
        #    GET /tag/<tag>/_packages
        #    GET /tag/<tag>/_all
        #    GET /user/<user>/tags/_projects
        #    GET /user/<user>/tags/_packages
        #    GET /user/<user>/tags/_tagcloud
        #    GET /tag/_tagcloud
        #    GET user/<user>/tags/<project>
        #    PUT user/<user>/tags/<project>
        #    GET user/<user>/tags/<project>/<package>
        #    PUT user/<user>/tags/<project>/<package>

        #Build Results (Legacy)
        #
        #    RPMs
        #        GET /rpm/<project>/<platform>/<package>/<arch>/<rpmname>
        #        GET /rpm/<project>/<repo>/<arch>/<package>/history
        #        GET /rpm/<project>/<repo>/<arch>/<package>/buildinfo
        #        POST /rpm/<project>/<repo>/<arch>/<package>/buildinfo
        #        GET /rpm/<project>/<repo>/<arch>/<package>/status
        #    Build Results
        #        GET /result/<project>/<platform>/result
        #        GET /result/<project>/<platform>/<package>/result
        #        GET /result/<project>/<platform>/<package>/<arch>/log

        #Statistics
        #
        #    GET /statistics/latest_added?limit=<limit>
        #    GET /statistics/added_timestamp/<project>/<package>
        #    GET /statistics/latest_updated?limit=<limit>
        #    GET /statistics/updated_timestamp/<project>/<package>
        #    GET /statistics/activity/<project>/<package>
        #    GET /statistics/most_active?type=<type>&limit=<limit>
        #    GET /statistics/highest_rated?limit=<limit>
        #    GET /statistics/rating/<project>/<package>
        #    PUT /statistics/rating/<project>/<package>
        #    GET /statistics/download_counter?limit=<limit>
        #    GET /statistics/download_counter?group_by=<group_by>&limit=<limit>
        #    PUT /statistics/redirect_stats
        #    GET /statistics/newest_stats

        #Status Messages
        #
        #    GET /status_message/?limit=<limit>
        #    PUT /status_message/

        #Messages (for projects/packages)
        #
        #    GET /message/<id>
        #    GET /message/?limit=<limit>
        #    GET /message/?project=<project>
        #    GET /message/?project=<project>&package=<package>
        #    PUT /message/?project=<project>&package=<package>


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

if len(sys.argv) > 1:
    PORT = int(sys.argv[1])
else:
    PORT = 8001
    print "No port specified, using %d" % PORT

# Search mappings file in current directory and in DEFAULT_DIR
if not os.path.exists(MAPPINGS_FILE):
    os.chdir(DEFAULT_DIR)
if not os.path.exists(MAPPINGS_FILE):
    msg = "Error: %s not found neither in current directory nor in %s"
    print >> sys.stderr, msg % (MAPPINGS_FILE, DEFAULT_DIR)
    exit(1)

updateRepositories()

httpd = XFSPWebServer(("0.0.0.0", PORT), SimpleHTTPRequestHandler)
httpd.serve_forever()
