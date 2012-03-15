#!/usr/bin/python

__all__ = ["SimpleHTTPRequestHandler"]

import os
import posixpath
import BaseHTTPServer
import urllib
import cgi
import sys
import shutil

import ConfigParser

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class ObsLightHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = "OBS Light HTTP test"
    currentDir = ""

    def do_GET(self):
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_HEAD(self):
        f = self.send_head()
        if f:
            f.close()

    def send_head(self):
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def list_directory(self, path):
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<title>Directory listing for %s</title>\n" % displaypath)
        f.write("<body>\n<h2>Directory listing for %s</h2>\n" % displaypath)
        f.write("<hr>\n<ul>\n")
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write('<li><a href="%s">%s</a>\n'
                    % (urllib.quote(linkname), cgi.escape(displayname)))
        f.write("</ul>\n<hr>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def translate_path(self, path):
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = self.currentDir
        #path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    extensions_map = {
        '.a'      : 'application/octet-stream',
        '.ai'     : 'application/postscript',
        '.aif'    : 'audio/x-aiff',
        '.aifc'   : 'audio/x-aiff',
        '.aiff'   : 'audio/x-aiff',
        '.au'     : 'audio/basic',
        '.avi'    : 'video/x-msvideo',
        '.bat'    : 'text/plain',
        '.bcpio'  : 'application/x-bcpio',
        '.bin'    : 'application/octet-stream',
        '.bmp'    : 'image/x-ms-bmp',
        '.c'      : 'text/plain',
        # Duplicates :(
        '.cdf'    : 'application/x-cdf',
        '.cdf'    : 'application/x-netcdf',
        '.cpio'   : 'application/x-cpio',
        '.csh'    : 'application/x-csh',
        '.css'    : 'text/css',
        '.dll'    : 'application/octet-stream',
        '.doc'    : 'application/msword',
        '.dot'    : 'application/msword',
        '.dvi'    : 'application/x-dvi',
        '.eml'    : 'message/rfc822',
        '.eps'    : 'application/postscript',
        '.etx'    : 'text/x-setext',
        '.exe'    : 'application/octet-stream',
        '.gif'    : 'image/gif',
        '.gtar'   : 'application/x-gtar',
        '.h'      : 'text/plain',
        '.hdf'    : 'application/x-hdf',
        '.htm'    : 'text/html',
        '.html'   : 'text/html',
        '.ief'    : 'image/ief',
        '.jpe'    : 'image/jpeg',
        '.jpeg'   : 'image/jpeg',
        '.jpg'    : 'image/jpeg',
        '.js'     : 'application/x-javascript',
        '.ksh'    : 'text/plain',
        '.latex'  : 'application/x-latex',
        '.m1v'    : 'video/mpeg',
        '.man'    : 'application/x-troff-man',
        '.me'     : 'application/x-troff-me',
        '.mht'    : 'message/rfc822',
        '.mhtml'  : 'message/rfc822',
        '.mif'    : 'application/x-mif',
        '.mov'    : 'video/quicktime',
        '.movie'  : 'video/x-sgi-movie',
        '.mp2'    : 'audio/mpeg',
        '.mp3'    : 'audio/mpeg',
        '.mp4'    : 'video/mp4',
        '.mpa'    : 'video/mpeg',
        '.mpe'    : 'video/mpeg',
        '.mpeg'   : 'video/mpeg',
        '.mpg'    : 'video/mpeg',
        '.ms'     : 'application/x-troff-ms',
        '.nc'     : 'application/x-netcdf',
        '.nws'    : 'message/rfc822',
        '.o'      : 'application/octet-stream',
        '.obj'    : 'application/octet-stream',
        '.oda'    : 'application/oda',
        '.p12'    : 'application/x-pkcs12',
        '.p7c'    : 'application/pkcs7-mime',
        '.pbm'    : 'image/x-portable-bitmap',
        '.pdf'    : 'application/pdf',
        '.pfx'    : 'application/x-pkcs12',
        '.pgm'    : 'image/x-portable-graymap',
        '.pl'     : 'text/plain',
        '.png'    : 'image/png',
        '.pnm'    : 'image/x-portable-anymap',
        '.pot'    : 'application/vnd.ms-powerpoint',
        '.ppa'    : 'application/vnd.ms-powerpoint',
        '.ppm'    : 'image/x-portable-pixmap',
        '.pps'    : 'application/vnd.ms-powerpoint',
        '.ppt'    : 'application/vnd.ms-powerpoint',
        '.ps'     : 'application/postscript',
        '.pwz'    : 'application/vnd.ms-powerpoint',
        '.py'     : 'text/x-python',
        '.pyc'    : 'application/x-python-code',
        '.pyo'    : 'application/x-python-code',
        '.qt'     : 'video/quicktime',
        '.ra'     : 'audio/x-pn-realaudio',
        '.ram'    : 'application/x-pn-realaudio',
        '.ras'    : 'image/x-cmu-raster',
        '.rdf'    : 'application/xml',
        '.rgb'    : 'image/x-rgb',
        '.roff'   : 'application/x-troff',
        '.rtx'    : 'text/richtext',
        '.sgm'    : 'text/x-sgml',
        '.sgml'   : 'text/x-sgml',
        '.sh'     : 'application/x-sh',
        '.shar'   : 'application/x-shar',
        '.snd'    : 'audio/basic',
        '.so'     : 'application/octet-stream',
        '.src'    : 'application/x-wais-source',
        '.sv4cpio': 'application/x-sv4cpio',
        '.sv4crc' : 'application/x-sv4crc',
        '.swf'    : 'application/x-shockwave-flash',
        '.t'      : 'application/x-troff',
        '.tar'    : 'application/x-tar',
        '.tcl'    : 'application/x-tcl',
        '.tex'    : 'application/x-tex',
        '.texi'   : 'application/x-texinfo',
        '.texinfo': 'application/x-texinfo',
        '.tif'    : 'image/tiff',
        '.tiff'   : 'image/tiff',
        '.tr'     : 'application/x-troff',
        '.tsv'    : 'text/tab-separated-values',
        '.txt'    : 'text/plain',
        '.ustar'  : 'application/x-ustar',
        '.vcf'    : 'text/x-vcard',
        '.wav'    : 'audio/x-wav',
        '.wiz'    : 'application/msword',
        '.wsdl'   : 'application/xml',
        '.xbm'    : 'image/x-xbitmap',
        '.xlb'    : 'application/vnd.ms-excel',
        # Duplicates :(
        '.xls'    : 'application/excel',
        '.xls'    : 'application/vnd.ms-excel',
        '.xml'    : 'text/xml',
        '.xpdl'   : 'application/xml',
        '.xpm'    : 'image/x-xpixmap',
        '.xsl'    : 'application/xml',
        '.xwd'    : 'image/x-xwindowdump',
        '.zip'    : 'application/zip',
        }
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })

def server():
    configParser = ConfigParser.ConfigParser()
    configFile = open("/etc/obslight/obslight.conf", 'rw')
    configParser.readfp(configFile)

    if ('webserver' in configParser.sections()):
        if ('port' in configParser.options('webserver')):
            port = int(configParser.get('webserver', 'port', raw=True))
        else:
            port = 8000
        if ('port' in configParser.options('webserver')):
            currentDir = configParser.get('webserver', 'directory', raw=True)
        else:
            currentDir = "/home"

        print "port", port, "currentDir", currentDir
        server_address = ('', port)
        ObsLightHTTPRequestHandler.protocol_version = "HTTP/1.0"
        ObsLightHTTPRequestHandler.currentDir = currentDir

        httpd = BaseHTTPServer.HTTPServer(server_address, ObsLightHTTPRequestHandler)
        sa = httpd.socket.getsockname()
        print "Serving HTTP on", sa[0], "port", sa[1], "..."
        httpd.serve_forever()

if __name__ == '__main__':
    server()









