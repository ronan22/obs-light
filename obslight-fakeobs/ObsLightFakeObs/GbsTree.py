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

@author: jobollo@nonadev.net
"""

import os
import re
import subprocess
import urllib2
import xml.dom.minidom
import hashlib
from xml.etree import ElementTree

import Utils
import Config

class GbsTree:
    """
    Management of a GBS Tree
    CAUTION:
	The meaning of "arch" is not the same as from OBSLIGHT
	In OBSLIGHT, the arch stands for i586, i686, x86_64 and so on
	Here, arch has a slightly different scope: it is a main arch for
	wich the project is built. For example: ia32, armv7l.
	The terms used here comes from the build.xml vocabulary.
    """

    # name of the builddir
    dir_build = "/builddata" 
    dir_repos = "/repos" 
    dir_repo_data = "repodata" 

    # name of the build xml file
    file_buildxml = dir_build + "/build.xml"
    file_repomd = "repomd.xml"

    def __init__(self,url,should_raise=False,verbose=False):
	"""
	attach the current object to a given URL
	"""
	self.should_raise = should_raise
	self.verbose = verbose
	self.clear_error()
	self.connected = False
	self.url = url.strip()
	rm = re.match("^(\w+:)?(.*)$",self.url)
	assert rm
	self.protocol = rm.group(1).lower()
	self.path = rm.group(2)
	self.nrtry = 2
	conf = Config.getConfig()
	if conf:
	    self.nrtry = max(1,conf.getIntLimit("max_download_retries", 2))

    def connect(self):
	"""
	Connect to the GBS tree using the specified protocol
	"""
	# must not be already connected
	assert not self.connected 

	self.clear_error()

	# discover the protocol
	if self.protocol is None or self.protocol == "":
	    if not self._connect_rsync():
		if not self._connect_http("https:"):
		    if not self._connect_http("http:"):
			return self._error("Can't connect using any known protocol")

	# use rsync protocol
	elif self.protocol == "rsync:":
	    if not self._connect_rsync():
		    return self._error("Can't connect using rsync protocol")

	# use https protocol
	elif self.protocol == "https:":
	    if not self._connect_http("https:"):
		    return self._error("Can't connect using https protocol")

	# use http protocol
	elif self.protocol == "http:":
	    if not self._connect_http("http:"):
		    return self._error("Can't connect using http protocol")

	# Check that it is connected
	assert self.connected 
	return True

    def disconnect(self):
	"""
	disconnect to the connected GBS tree
	"""
	assert self.connected
	# TODO make some cleaning actions here
	self.connected = None

    def download_config(self,filename):
	"""
	download the config file to the given 'filename'
	"""
	assert self.connected
	if self.is_http:
	    uri = "{}{}/{}".format(self.uri_base, self.dir_build, self.built_conf)
	    try:
		return Utils.httpDownloadTo(uri,filename,self.nrtry)
	    except Exception as e:
		return self._error_from_exception(e, "while downloading %s"%uri)
	else:
	    return self._unimplemented()

    def unset_repo(self):
	"""
	Unset the currently browsed repository.
	It also unset the currently browsed arch and package
	"""
	self.current_repo = None
	self.current_arch = None
	self.current_package = None

    def set_repo(self,repo):
	"""
	Set the current browsed repository to 'repo' that must exist
	It unset the currently browsed arch and package
	"""
	assert self.connected
	assert repo in self.built_repos
	self.current_repo = repo
	self.current_arch = None
	self.current_package = None
	if self.is_http:
	    self.uri_repo = "{}{}/{}".format(self.uri_base,self.dir_repos,repo)
	return True

    def unset_arch(self):
	"""
	Unset the currently browsed arch
	It also unset the currently browsed package
	"""
	self.current_arch = None
	self.current_package = None

    def set_arch(self,arch):
	"""
	Set the current browsed arch to 'arch' that must exist.
	The repo must be set.
	"""
	assert self.connected
	assert self.current_repo
	assert arch in self.built_archs
	self.current_arch = arch
	if self.is_http:
	    self.uri_arch = "{}/{}".format(self.uri_repo,arch)
	return True

    def unset_package(self):
	"""
	Unset the currently browsed package.
	It also unset the currently browsed arch and package
	"""
	self.current_repo = None
	self.current_arch = None
	self.current_package = None

    def set_package(self,package):
	"""
	Set the current package
	"""
	assert self.connected
	assert self.current_repo
	if self.is_http:
	    if self.current_arch:
		uripck = "{}/{}".format(self.uri_arch,package)
	    else:
		uripck = "{}/{}".format(self.uri_repo,package)
	    self.uri_pack_base = uripck
	    self.uri_pack_data = "{}/{}".format(uripck,self.dir_repo_data)
	    if not self._read_repomd():
		return False
	    self.current_package = package
	    return True
	return self._unimplemented()

    # internal connection methods
    # ---------------------------

    def _connect_rsync(self):
	"""
	connect to the URL using the rsync protocol
	"""
	# TODO: currently not implemented
	self._original_error("rsync protocol not yet implemented")
	return False

    def _connect_http(self,schema):
	"""
	connect to the URL using the rsync protocol
	"""
	base = schema + self.path
	bxml = self._http_read(base + self.file_buildxml)
	if bxml is  None:
	    return False
	if not self._connect_xml(bxml):
	    return False
	self.connected = True
	self.is_http = True
	self.is_rsync = False
	self.uri_base = base
	return True

    def _connect_xml(self,xmlstr):
	"""
	end phase of connect by scanning the XML build file
	"""
	def as_str_list(doc,tag):
	    """
	    returns a list of the TEXT content of element of type tag
	    """
	    result = []
	    for n in doc.getElementsByTagName(tag):
		assert n is not None
		assert n.nodeType == n.ELEMENT_NODE
		t = n.firstChild
		if t is not None and t.nodeType == t.TEXT_NODE:
		    result.append(t.data.strip())
	    return result
	if self.verbose: print "scanning "+xmlstr
	doc = xml.dom.minidom.parseString(xmlstr)
	archs = as_str_list(doc,"arch")
	if self.verbose: print "  retrieved archs: "+str(archs)
	repos = as_str_list(doc,"repo")
	if self.verbose: print "  retrieved repos: "+str(repos)
	confs = as_str_list(doc,"buildconf")
	if self.verbose: print "  retrieved confs: "+str(confs)
	ids = as_str_list(doc,"id")
	if self.verbose: print "  retrieved confs: "+str(ids)
	if len(archs) < 1:
	    self._original_error("No arch in build file")
	    return False
	if len(repos) < 1:
	    self._original_error("No repo in build file")
	    return False
	if len(confs) < 1:
	    self._original_error("No buildconf in build file")
	    return False
	if len(ids) < 1:
	    self._original_error("No id in build file")
	    return False
	if len(confs) > 1:
	    self._original_error("More than one buildconf in build file")
	    return False
	if len(ids) > 1:
	    self._original_error("More than one id in build file")
	    return False
	self.built_archs = archs
	self.built_repos = repos
	self.built_conf = confs[0]
	self.built_id = ids[0]
	return True

    def _read_repomd(self):
	"""
	"""
	if self.verbose:
	    print "reading repomd for repo:{} arch:{} package:{}".format(self.current_repo, self.current_arch, self.current_package)
	uri = "{}/{}".format(self.uri_pack_data,self.file_repomd)
	repomd = self._http_read(uri)
	if not repomd:
	    self._error("not able to acces repomd for repo:{} arch:{} package:{}".format(self.current_repo, self.current_arch, self.current_package))
	if self.verbose:
	    print "REPOMD:"
	    print repomd
	meta = { "repomd": repomd }
	doc = xml.dom.minidom.parseString(repomd)
	
	self.current_pack_meta = meta
	return True

    # internal utils
    # --------------
    def _http_read(self,uri):
	"""
	return the document at the given 'uri' or None in case of error
	"""
	try:
	    if self.verbose:
		print "accessing "+uri
	    f = urllib2.urlopen(uri)
	    result = f.read()
	    f.close()
	    return result
	except Exception as e:
	    self._original_error_from_exception(e,"when fetching %s"%uri)
	    return None


    # section of error handling
    #--------------------------

    def clear_error(self):
	"""
	clear any pending error
	"""
	self.error_message = ""
	self.has_error = False
	self._original_error_message = ""
	
    def _error(self,message):
	"""
	set the 'has_error' status and the 'error_message'
	also raise an exception if 'should_raise' is True
	(see __init__ constructor)
	"""
	self.has_error = True
	if self._original_error_message:
	    self.error_message = message + "\ndetail:"+self._original_error_message
	    self._original_error_message = ""
	else:
	    self.error_message = message
	if self.verbose:
	    print "GbsTree ERROR:"
	    print "=============="
	    print self.error_message
	if self.should_raise:
	    raise Exception(self.error_message)
	return False

    def _error_from_exception(self, exception, message):
	"""
	set the 'has_error' status and the 'error_message'
	according to the exception and the given message.
	also raise an exception if 'should_raise' is True
	(see __init__ constructor)
	"""
	self._error("when {}\nexception catched:\n{}".format(message, str(exception)))

    def _original_error(self,message):
	"""
	append 'message' to the original error
	"""
	self._original_error_message = self._original_error_message + "\n... " + message


    def _original_error_from_exception(self, exception, message):
	"""
	append 'message' and 'exception' to the original error
	"""
	self._original_error("when {}\nexception catched:\n{}".format(message, str(exception)))

    def _unimplemented(self):
	"""
	emit the unimplemented error
	"""
	return self._error("Error, called feature is UNIMPLEMENTED")



