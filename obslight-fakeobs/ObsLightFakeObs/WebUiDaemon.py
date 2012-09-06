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
Small web UI for FakeOBS.

@author: Florent Vennetier
"""

import os.path
import sys
import time
import traceback
import urllib2
import urlparse
from xml.etree import ElementTree
import SocketServer
import BaseHTTPServer

from Config import getConfig, loadConfig
from Utils import getEntryNameList, getEntriesAsDicts, httpQueryToDict
from Utils import getLocalHostIpAddress

GET = "GET"

BINARY_CONTENTTYPE = "application/octet-stream"
HTML_CONTENTTYPE = "text/html"
PLAINTEXT_CONTENTTYPE = "text/plain"

FIRST_PAGE = """
<br/>
<p>
This is a web interface allowing you to browse the content
of your fake OBS server.
</p>
"""
GLOBAL_HEADER = """
<html>
 <head>
<!--   <link rel="stylesheet" type="text/css" href="/theme/fakeobswebui.css" /> -->
  <title>OBS Light's Fake OBS Web Interface</title>
 </head>
 <body>
 <h1><img alt="obslight-logo" src="/theme/fakeobs.png" />OBS Light Fake OBS Web UI</h1>
<!-- <div id="navbar"> -->
 <table border="1px" cellpadding="4px">
  <tr>
   <th><a href="/">Home</a></th>
   <th><a href="/project/list_public">Project list</a></th>
  </tr>
 </table>
<!-- </div> -->
"""
GLOBAL_FOOTER = """
 </body>
</html>
"""
PACKAGE_FILES_HEADER = """
<h3>Files of %(package)s</h3>
<!-- <div id="filetable"> -->
<table border="1px" cellpadding="2px">
 <tr>
  <th>File</th>
  <th>Size</th>
  <th>MD5</th>
  <th>Modification time</th>
 </tr>
"""
PACKAGE_FILES_FOOTER = """
</table>
<!-- </div> -->
"""
PACKAGE_FILE_TEMPLATE = """
 <tr>
  <td align="left"><a href="%(fileUrl)s">%(name)s</a></td>
  <td align="right">%(size)s</td>
  <td align="right">%(md5)s</td>
  <td align="right">%(readableTime)s</td>
 </tr>
"""
PROJECT_LIST_HEADER = """
<h3>Projects</h3>
<p>
 <ul>
"""
PROJECT_LIST_FOOTER = """
 </ul>
</p>
"""
PROJECT_ENTRY_TEMPLATE = """
  <li>
   <a href="%(packageListUrl)s">%(project)s</a> (<a href="%(prjconfUrl)s">config</a>, <a href="%(metaUrl)s">meta</a>)
  </li>
"""
PACKAGE_LIST_HEADER = """
<h3>Packages of %(project)s</h3>
<p>
 <ul>
"""
PACKAGE_LIST_FOOTER = """
 </ul>
</p>
"""
PACKAGE_ENTRY_TEMPLATE = """
  <li><a href="%(packageFilesUrl)s">%(package)s</a></li>
"""
TEXT_FILE_TEMPLATE = """
<h3>%(title)s</h3>
<pre>%(content)s</pre>
"""


class FakeObsWebUiRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            content, contentType, code = self.get_content(GET)
            self.send_response(code)
            self.send_header("Content-type", contentType)
            self.end_headers()
            self.wfile.write(content)
        except:
            self.send_response(500)
            print "500: " + self.path
            traceback.print_exc(file=sys.stdout)
            self.end_headers()

    def get_content(self, action):
        pathToMethod = {"project": self.handleProjectRequest,
                        "package": self.handlePackagesRequest,
                        "theme": self.handleThemeRequest,
                        "favicon.ico": self.handleFaviconRequest}

        parsedPath = urlparse.urlparse(self.path)
        if parsedPath[2] == "/":
            content, contentType, code = self.getDefaultPage()
        else:
            # path starts with '/' so first splitted element is always empty
            pathParts = parsedPath[2].split('/')[1:]
            queryDict = httpQueryToDict(parsedPath[4])
            try:
                content, contentType, code = pathToMethod[pathParts[0]](pathParts[1:], queryDict)
            except KeyError as ke:
                return self.unknownRequest(pathParts[0])
        if contentType == HTML_CONTENTTYPE:
            return GLOBAL_HEADER + content + GLOBAL_FOOTER, contentType, code
        else:
            return content, contentType, code

    def getDefaultPage(self, *args, **kwargs):
        return FIRST_PAGE, HTML_CONTENTTYPE, 200

    def unknownRequest(self, request):
        message = "Unknown request: %s" % request
        return message, PLAINTEXT_CONTENTTYPE, 400

    def missingParameters(self, params):
        message = "Missing parameters: %s" % ", ".join(params)
        return message, PLAINTEXT_CONTENTTYPE, 400

    def fileNotFound(self, path):
        message = "File not found: %s" % path
        return message, PLAINTEXT_CONTENTTYPE, 404

    def sendFile(self, path):
        if not os.path.exists(path):
            return self.fileNotFound(path)
        with open(path, "r") as f:
            content = f.read()
        return content, BINARY_CONTENTTYPE, 200

    def handleFaviconRequest(self, *args):
        path = getConfig().getPath("theme_dir", "/srv/fakeobs/theme")
        return self.sendFile(os.path.join(path, "favicon.ico"))

    def handleThemeRequest(self, pathParts, queryDict):
        path = getConfig().getPath("theme_dir", "/srv/fakeobs/theme")
        return self.sendFile(os.path.join(path, *pathParts))

    def handleProjectRequest(self, pathParts, queryDict):
        # {"request": (function_to_call, [query_parameters], [other_parameters])}
        funcMap = {"list_public": (self.getPrettyProjectList, [], []),
                   "packages": (self.getPrettyPackageList, ["project"], []),
                   "prjconf": (self.getProjectConfigOrMeta, ["project"], ["config"]),
                   "meta": (self.getProjectConfigOrMeta, ["project"], ["meta"])}
        funcTuple = funcMap.get(pathParts[0])
        if funcTuple is None:
            return self.unknownRequest("/project/%s" % pathParts[0])
        else:
            # funcTuple[0] -> function
            # funcTuple[1] -> list of arguments to take in queryDict
            # funcTuple[2] -> list of extra arguments
            try:
                myArgs = [queryDict[x][0] for x in funcTuple[1]]
            except KeyError as ke:
                return self.missingParameters([ke.args[0]])
            myArgs.extend(funcTuple[2])
            content, contentType, code = funcTuple[0](*myArgs)
            return content, contentType, code

    def handlePackagesRequest(self, pathParts, queryDict):
        if pathParts[0] == "files":
            try:
                return self.getPrettyFilesList(queryDict["project"][0],
                                               queryDict["package"][0])
            except KeyError as ke:
                return self.missingParameters([ke.args[0]])
        else:
            return self.unknownRequest("/package/" + pathParts[0])

    def getPrettyProjectList(self):
        """call /source, parse the result, format to HTML code"""
        url = "%s/source" % (getConfig().getFakeObsApiUrl())
        xmlRes = urllib2.urlopen(url).read()
        projectList = getEntryNameList(xmlRes)
        formattedList = PROJECT_LIST_HEADER
        for project in projectList:
            projectDict = {"project": project,
                           "packageListUrl": "/project/packages?project=%s" % project,
                           "prjconfUrl": "/project/prjconf?project=%s" % project,
                           "metaUrl": "/project/meta?project=%s" % project}
            formattedList += PROJECT_ENTRY_TEMPLATE % projectDict
        formattedList += PROJECT_LIST_FOOTER
        return formattedList, HTML_CONTENTTYPE, 200

    def getPrettyPackageList(self, project):
        """call /source/<project>, parse the result, format to HTML code"""
        url = "%s/source/%s" % (getConfig().getFakeObsApiUrl(), project)
        xmlRes = urllib2.urlopen(url).read()
        packageList = getEntryNameList(xmlRes)
        formattedList = PACKAGE_LIST_HEADER % {"project": project}
        for package in packageList:
            packageFilesUrl = "/package/files?package=%s&project=%s" % (package, project)
            formattedList += PACKAGE_ENTRY_TEMPLATE % {"packageFilesUrl": packageFilesUrl,
                                                       "package": package}
        formattedList += PACKAGE_LIST_FOOTER
        return formattedList, HTML_CONTENTTYPE, 200

    def getProjectConfigOrMeta(self, project, what="config"):
        readableWhat = {"config": "project configuration",
                        "meta": "project meta informations"}
        url = "%s/source/%s/_%s" % (getConfig().getFakeObsApiUrl(), project, what)
        fileContent = urllib2.urlopen(url).read()
        fileContent = fileContent.replace("<", "&lt").replace(">", "&gt")
        title = "%s %s" % (project, readableWhat[what])
        content = TEXT_FILE_TEMPLATE % {"title": title,
                                        "content": fileContent}
        return content, HTML_CONTENTTYPE, 200

    def getPrettyFilesList(self, project, package):
        """call /source/<project>/<package>, parse the result, format to HTML code"""
        url = "%s/source/%s/%s" % (getConfig().getFakeObsApiUrl(), project, package)
        xmlRes = urllib2.urlopen(url).read()
        files = getEntriesAsDicts(xmlRes)
        content = PACKAGE_FILES_HEADER % {"project": project, "package": package}
        fakeObsApiUrl = getConfig().getFakeObsApiUrl()
        localIp = Utils.getLocalHostIpAddress()
        if localIp != "127.0.0.1" and "/localhost:" in fakeObsApiUrl:
            fakeObsApiUrl = fakeObsApiUrl.replace("/localhost:", "/%s:" % localIp)
        for fileDict in files:
            fileUrl = "%s/source/%s/%s/%s" % (fakeObsApiUrl,
                                              project, package, fileDict["name"])
            fileDict["fileUrl"] = fileUrl
            readableTime = time.ctime(float(fileDict["mtime"]))
            fileDict["readableTime"] = readableTime
            content += PACKAGE_FILE_TEMPLATE % fileDict
        content += PACKAGE_FILES_FOOTER
        return content, HTML_CONTENTTYPE, 200

class XFSPWebServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass

if __name__ == '__main__':
    # TODO: use an option parser and add quiet/verbose modes
    if len(sys.argv) > 1:
        loadConfig(sys.argv[1])
    else:
        loadConfig()
    conf = getConfig()

    httpd = XFSPWebServer(("0.0.0.0", conf.getPort("webui_port", 8000)),
                          FakeObsWebUiRequestHandler)
    httpd.serve_forever()
