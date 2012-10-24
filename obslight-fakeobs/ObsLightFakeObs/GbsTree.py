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
Objects to manage the GBS tree exported by OBS of the Tizen Project for Tizen GBS

@author: José Bollo
"""

# CAUTION: the way the paths are managed is not good because there is a mix
# between built paths and read paths.
# Here are two points identified:
#      - the location of packages read in primary is used as-is
#      - the location for rsync ae used directly to point on local synchronized dir

import sys
import os
import re
import subprocess
import urllib2
import xml.dom.minidom
import hashlib
import shutil
import shlex
import Config
import Utils

class GbsTree:
    """
    Management of a GBS Tree
    """

    # name of the builddir
    dir_build = "builddata" 
    dir_repos = "repos" 
    dir_repo_data = "repodata" 

    # name of the build xml file
    file_buildxml = "build.xml"
    file_repomd = "repomd.xml"

    def __init__(self,url,**options):
	"""
	Create an instance attached to a given 'URL'
	The options are given by names. 
	Here are the options:
	    NAME	    TYPE	DEFAULT	    COMMENT
	    verbose	    bool	False	    if true, details are printed to stdout
	    should_raise    bool	False	    if true, exceptions are raised
	    rsynckeep	    bool	False	    if true, rsynced data aren't removed
	    archs	    [string]	None	    what archs are wanted, list of names, None if any arch wanted
	    noarchs	    [string]	["noarch"]  what archs are always taken (even if absent of achs)
	"""
	self.should_raise = bool(options.setdefault("should_raise",False))
	self.verbose = bool(options.setdefault("verbose",False))
	self.rsynckeep = bool(options.setdefault("rsynckeep",False))
	self.archs = options.setdefault("archs",None)
	self.noarchs = options.setdefault("noarchs",[ "noarch" ])
	if self.noarchs is None:
	    self.noarchs = []
	self.clear_error()
	self.connected = False
	self.url = url.strip()
	self._connector = None
	rm = re.match("^(\w+:)?(.*)$",self.url) # TODO: remove 're' and use a URI manager
	assert rm
	self.protocol = rm.group(1).lower()
	p = rm.group(2)
	if p[-1] == "/":
	    p = p[:-1]
	self.path = p
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
	assert self._connector
	return True

    def disconnect(self):
	"""
	disconnect to the connected GBS tree
	"""
	assert self.connected
	assert self._connector
	self._connector.disconnect()
	self._connector = None
	self.connected = None

    def download_config(self,filename):
	"""
	download the config file to the given 'filename'
	"""
	assert self.connected
	uri = "{}/{}".format(self.dir_build, self.built_conf)
	return self._connector.download_to(uri,filename)

    def unset_repo(self):
	"""
	Unset the currently browsed repository.
	It also unset the currently browsed target and package
	"""
	self.current_repo = None
	self.current_target = None
	self.current_package = None

    def set_repo(self,repo):
	"""
	Set the current browsed repository to 'repo' that must exist
	It unset the currently browsed target and package
	"""
	assert self.connected
	assert repo in self.built_repos
	self.current_repo = repo
	self.current_target = None
	self.current_package = None
	self.path_repo = "{}/{}".format(self.dir_repos,repo)
	return True

    def unset_target(self):
	"""
	Unset the currently browsed target
	It also unset the currently browsed package
	"""
	self.current_target = None
	self.current_package = None

    def set_target(self,target):
	"""
	Set the current browsed target to 'target' that must exist.
	The repo must be set.
	"""
	assert self.connected
	assert self.current_repo
	assert target in self.built_targets
	self.current_target = target
	self.path_target = "{}/{}".format(self.path_repo,target)
	return True

    def unset_package(self):
	"""
	Unset the currently browsed package.
	It also unset the currently browsed target and package
	"""
	self.current_repo = None
	self.current_target = None
	self.current_package = None

    def set_package(self,package):
	"""
	Set the current package
	"""
	assert self.connected
	assert self.current_repo
	if self.current_target:
	    path = "{}/{}".format(self.path_target,package)
	else:
	    path = "{}/{}".format(self.path_repo,package)
	self.path_package = path
	if not self._read_repodata():
	    self.current_package = None
	    return False
	self.current_package = package
	return True

    def check_package_archs(self):
	"""
	Checks the archs of the package against the required archs
	The required archs are set at the creation of the instance, see __init__
	Return the tuple (status, missing, supported)
	Where
	    - status: is false if missing archs is detected, true otherwise
	    - missing: if the list of missing archs (we have status=not bool(missing))
	    - supported: is the list of the supported archs
	"""
	assert self.connected
	assert self.current_package
	supported = self.current_pack_meta["archs"]
	missing = []
	if self.archs:
	    for a in self.archs:
		if a not in supported:
		    missing.append(a)
	return (not bool(missing), missing, supported)

    def download_package_to(self,rootdir,dont_fail=False):
	"""
	Download the package to 'rootdir'
	The flags 'adarch' and 'dont_fail' controls the behaviour:
	    - 'addarg' means that if true, the arch is added as directory
	    - 'dont_fail' means that if an error occurs, the download continue
	"""
	assert self.connected
	assert self.current_package
	assert os.path.isdir(rootdir)

	# root
	root = self.path_package

	# copy the repomd
	d = os.path.join(rootdir,self.dir_repo_data)
	if not os.path.isdir(d):
	    os.makedirs(d)
	n = os.path.join(d,self.file_repomd)
	if self.verbose:
	    print "creating repomd: "+n
	f = open(n,"w")
	f.write(self.current_pack_meta["repomd"])
	f.close()

	# copy the repomd data files
	for n in self.current_pack_meta["data"].values():
	    u = "{}/{}".format(root,n)
	    n = os.path.join(rootdir,n) # TODO: FIXME: not clear is 'pa' uri or fs? should be checked
	    d = os.path.dirname(n)
	    if not os.path.isdir(d):
		os.makedirs(d)
	    if not self._connector.download_to(u,n):
		return False

	# copy the packages of the list
	for e in self.current_pack_meta["pklist"]:
	    if self.archs:
		a = e.get_arch()
		if a not in self.archs and a not in self.noarchs:
		    continue
	    l = e.get_location()
	    u = "{}/{}".format(root,l)
	    n = os.path.join(rootdir,l)
	    d = os.path.dirname(n)
	    if not os.path.isdir(d):
		os.makedirs(d)
	    if not self._connector.download_to(u,n):
		if dont_fail:
		    print "WARNING: can't get RPM {} in {}".format(r,root)
		else:
		    return False
	return True

    def extract_package_rpms_to(self,rootdir,meta_project=None,dont_fail=False):
	"""
	Extracts the source packages to the 'rootdir'
	If 'meta_project' isn't None, the _meta file is created with the given poject name
	If 'dont_fail' isn't False, individuals failures dont stop the extracting
	"""
	assert self.connected
	assert self.current_package
	assert os.path.isdir(rootdir)

	# root
	root = self.path_package

	# copy the packages of the list
	for e in self.current_pack_meta["pklist"]:
	    if self.archs:
		a = e.get_arch()
		if a not in self.archs and a not in self.noarchs:
		    continue
	    n = e.get_name()
	    l = e.get_location()
	    u = "{}/{}".format(root,l)
	    d = os.path.join(rootdir,n)
	    if not os.path.isdir(d):
		os.makedirs(d)
	    if not self._extract_rpm_to(u,d):
		if dont_fail:
		    print "WARNING: can't extract RPM {} in {}".format(r,root)
		else:
		    return False

	    # add meta data if requested
	    if meta_project:
		# create the _directory file
		entries = []
		md5src = hashlib.md5()
		for fn in sorted(os.listdir(d)):
		    if fn not in [ "_meta", "_directory" ]:
			f = os.path.join(d,fn)
			md5 = Utils.computeMd5(f)
			md5src.update("{}  {}\n".format(md5,fn))
			s = os.stat(f)
			entries.append('  <entry name="{NAME}" md5="{MD5}" size="{SIZE}" mtime="{MTIME}" />\n'.format(
			    NAME=fn, MD5=md5, SIZE=s.st_size, MTIME=s.st_mtime))
		c = '<directory name="{NAME}" rev="1" srcmd5="{SRCMD5}">\n{ENTRIES}</directory>\n'.format(
			NAME=e.get_name(),ENTRIES="".join(entries),SRCMD5=md5src.hexdigest())
		f = open(os.path.join(d,"_directory"),"w")
		f.write(c)
		f.close()

		# create the _meta file
		c = """<package name="{NAME}" project="{PROJ}">
  <title>{TITLE}</title>
  <description>
{DESC}
  </description>
</package>""".format(NAME=e.get_name(),PROJ=meta_project,TITLE=e.get_summary(),DESC=e.get_description())
		f = open(os.path.join(d,"_meta"),"w")
		f.write(c)
		f.close()
	    
	return True

    # internal connection methods
    # ---------------------------

    def _read_build_xml(self,xmlstr):
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
	targets = as_str_list(doc,"arch")
	if self.verbose: print "  retrieved targets: "+str(targets)
	repos = as_str_list(doc,"repo")
	if self.verbose: print "  retrieved repos: "+str(repos)
	confs = as_str_list(doc,"buildconf")
	if self.verbose: print "  retrieved confs: "+str(confs)
	ids = as_str_list(doc,"id")
	if self.verbose: print "  retrieved confs: "+str(ids)
	if len(targets) < 1:
	    self._original_error("No target in build file")
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
	self.built_targets = targets
	self.built_repos = repos
	self.built_conf = confs[0]
	self.built_id = ids[0]
	return True

    def _read_repodata(self):
	"""
	Reads the descriptions of the package from the repodata/repomd.xml
	"""
	assert self.connected
	assert self.current_repo
	assert self.path_package
	if self.verbose:
	    print "reading repomd for repo:{} target:{} package:{}".format(self.current_repo, self.current_target, self.current_package)
	
	# reads the repodata/repomd.xml
	pathmd = "{}/{}/{}".format(self.path_package,self.dir_repo_data,self.file_repomd)
	repomd = self._connector.read(pathmd)
	if not repomd:
	    self._error("not able to acces repomd for repo:{} target:{} package:{}".format(self.current_repo, self.current_target, self.current_package))
	doc = xml.dom.minidom.parseString(repomd)

	# fills data with locations of listed data
	data = {}
	for n in doc.getElementsByTagName("data"):
	    assert n.nodeType==n.ELEMENT_NODE
	    t = n.getAttribute("type")
	    if t:
		l = n.getElementsByTagName("location")
		if l and len(l) == 1:
		    l = l[0]
		    assert l.nodeType==n.ELEMENT_NODE
		    h = l.getAttribute("href")
		    if h:
			data[t] = h

	# check the existance of the "primary" data
	npri = data.get("primary")
	if not npri:
	    return self._error("not able to locate a primary in "+pathmd)

	# read the file list
	upri = "{}/{}".format(self.path_package,npri)
	fpri = self._connector.read(upri)
	if not fpri:
	    return self._error("not able to acces primary for repo:{} target:{} package:{}".format(self.current_repo, self.current_target, self.current_package))
	fpri = self._unzip(fpri)

	# create the list of repositories from the primary.xml
	primary = xml.dom.minidom.parseString(fpri)
	pklist = []
	archlst = {}
	for p in primary.getElementsByTagName("package"):
	    assert p.nodeType==p.ELEMENT_NODE
	    t = p.getAttribute("type")
	    if t and t=="rpm":
		# got a <package type="rpm"> node! use it!
		pk = self._Package(p)
		pklist.append(pk)
		a = pk.get_arch()
		if a not in self.noarchs:
		    archlst[a] = True

	self.current_pack_meta = {
		    "repomd": repomd,
		    "data":   data,
		    "primary": primary,
		    "pklist": pklist,
		    "archs": archlst.keys()
		    }
	return True

    # internal utils
    # --------------

    def _unzip(self,data):
	"""
	return an unzipped version of a given 'data'
	"""
	while True:
	    if data[0]==chr(31) or data[1]==chr(139):
		data = self._filter(data,["gunzip","-"])
	    else: # TODO: only gziped file is detected: enought but one could add other types
		return data

    def _filter(self,data,command):
	"""
	Execute the 'command' as a process filtering data in its stdin and 
	writing the result on its stdout.
	"""
	proc = subprocess.Popen(command,
		stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	(data,err) = proc.communicate(data)
	proc.wait()
	return data

    def _extract_rpm_to(self,fname,directory):
	"""
	Extract the RPM named 'fname' to the 'directory' that must exist
	"""
	assert os.path.isdir(directory)
	r2c = subprocess.Popen(["rpm2cpio", "-"],
		stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	cpio = subprocess.Popen(["cpio","-idvm"],
		cwd = directory,
		stdin = r2c.stdout, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	stsco = self._connector.stream_to(fname,r2c.stdin)
	r2c.stdin.close()
	r2c.wait()
	cpio.wait()
	stsr2c = r2c.returncode
	stscpio = cpio.returncode
	if not stsco:
	    err = self.error_message
	elif stsr2c != 0:
	    err = r2c.stderr.read()
	elif stscpio != 0:
	    err = cpio.stderr.read()
	else:
	    err = None
	r2c.stderr.close()
	cpio.stderr.close()
	cpio.stdout.close()
	if err:
	    self._original_error(err)
	    return self._error("error while unpacking {}".fname)
	return True

    # internal http
    # --------------
    def _connect_http(self,schema):
	"""
	connect to the URL using the http protocol
	"""
	assert not self.connected
	assert not self._connector

	# clears the errors
	self.clear_error()

	# compute the http base
	base = schema + self.path

	# create the connector
	connector = GbsTree.ConnectorHTTP(self,base,self.nrtry)

	# terminate connexion
	return self._connect_terminate(connector)

    # internal rsync
    # --------------
    def _connect_rsync(self):
	"""
	connect to the URL using the rsync protocol
	"""

	# clears the errors
	self.clear_error()

	# create the rsync directory
	conf = Config.getConfig()
	rsyncdir = conf.getRsyncPath()
	if not os.path.isdir(rsyncdir):
	    os.makedirs(rsyncdir)

	# compute the rsync base
	base = "rsync:{}/".format(self.path)

	# create the connector
	connector = GbsTree.ConnectorRSYNC(self,base,rsyncdir,self.rsynckeep)

	# connect
	if not connector.connect():
	    return False

	# terminate connexion
	return self._connect_terminate(connector)

    def _connect_terminate(self,connector):
	"""
	terminate to connect by reading build.xml
	"""
	bxml = connector.read("{}/{}".format(self.dir_build,self.file_buildxml))
	if bxml is  None:
	    connector.disconnect()
	    return False
	if not self._read_build_xml(bxml):
	    connector.disconnect()
	    return False
	self.connected = True
	self._connector = connector
	return True

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


    # internal classes
    # ----------------
    class _Package:
	"""
	Classe for instances of the package in the primary.xml
	"""
	def __init__(self,node):
	    """
	    initialisation
	    """
	    self.set_node(node)

	def set_node(self,node):
	    """
	    Change the node to 'node'
	    """
	    assert node.nodeType == node.ELEMENT_NODE
	    assert node.getAttribute("type") == "rpm"
	    self.node = node

	def _subnode1(self,n,name):
	    """
	    The first subnode of the node 'n' of tagname 'name' 
	    None if no subnode of 'name'
	    """
	    if n:
		n = n.getElementsByTagName(name)
		if n:
		    return n[0]
	    return None
	    
	def _txtof(self,n):
	    """
	    Text content of the node 'n' (must be the first child node)
	    None if no text
	    """
	    if n:
		n = n.firstChild
		if n and n.nodeType == n.TEXT_NODE:
		    return n.data.strip()
	    return None
	    
	def _attr(self,n,name):
	    """
	    Value of the attribute of 'name' of the node 'n'
	    None if no such attribute
	    """
	    if n:
		return n.getAttribute(name)
	    return None
	    
	def get_name(self):
	    """
	    Return the name
	    """
	    return self._txtof(self._subnode1(self.node,"name"))
	    
	def get_arch(self):
	    """
	    Return the arch
	    """
	    return self._txtof(self._subnode1(self.node,"arch"))
	    
	def get_epoch(self):
	    """
	    Return the epoch
	    """
	    return self._attr(self._subnode1(self.node,"version"),"epoch")

	def get_version(self):
	    """
	    Return the version
	    """
	    return self._attr(self._subnode1(self.node,"version"),"ver")
	    
	def get_release(self):
	    """
	    Return the release
	    """
	    return self._attr(self._subnode1(self.node,"version"),"rel")
	    
	def get_location(self):
	    """
	    Return the location of the package
	    """
	    return self._attr(self._subnode1(self.node,"location"),"href")

	def get_summary(self):
	    """
	    Return the summary of the package
	    """
	    return self._txtof(self._subnode1(self.node,"summary"))

	def get_description(self):
	    """
	    Return the description of the package
	    """
	    return self._txtof(self._subnode1(self.node,"description"))

    class Connector():
	"""
	Base class for connectors
	"""
	def __init__(self,owner):
	    """
	    Init curret to point on an owner for error management
	    """
	    self._owner = owner
	    self.verbose = self._owner.verbose
	def disconnect(self):
	    """
	    Disconnect and purge any temporary data
	    """
	    pass
	def scheme(self):
	    """
	    Returns the protocol scheme
	    Valid results are None, "http", "https", "rsync"
	    """
	    return None

    class ConnectorHTTP(Connector):
	"""
	The HTTP/HTTPS connector
	"""
	def __init__(self,owner,uri,nrtry=1):
	    """
	    init current instance
	    """
	    assert uri.startswith("http:") or uri.startswith("https:")
	    GbsTree.Connector.__init__(self,owner)
	    self.uri = uri
	    self.nrtry = nrtry
	    self._scheme = "https" if self.uri.startswith("https:") else "http"
	    self.blocksize = 10000000 # 10 megabyte block

	def scheme(self):
	    """
	    Returns the protocol scheme
	    Results is "http" or "https"
	    """
	    return self._scheme

	def read(self,fname):
	    """
	    return the document at the given 'fname' or None in case of error
	    """
	    uri = "{}/{}".format(self.uri,fname)
	    if self.verbose:
		print "accessing {}".format(fname)
	    fin = None
	    nrtry = self.nrtry
	    while True:
		try:
		    fin = urllib2.urlopen(uri)
		    result = fin.read()
		    fin.close()
		    return result
		except Exception as e:
		    if fin:
		        fin.close()
		    if nrtry > 1:
			nrtry = nrtry - 1
			fin = None
		    self._owner._original_error_from_exception(e, "when fetching {}".format(uri))
		    return None

	def download_to(self,fname,filename):
	    """
	    http get of the 'fname' and save it into the given 'filename'
	    """
	    assert os.path.isdir(os.path.dirname(filename)), "the directory for '{}' must exists".format(filename)
	    uri = "{}/{}".format(self.uri,fname)
	    if self.verbose:
		print "downloading {}".format(fname)
	    nrtry = self.nrtry
	    size = self.blocksize
	    fin = None
	    fout = None
	    while True:
		try:
		    fin = urllib2.urlopen(uri)
		    fout = open(filename,"w")
		    data = fin.read(size)
		    while data:
			fout.write(data)
			data = fin.read(size)
		    fin.close()
		    fout.close()
		    return True
		except Exception as e:
		    if fin:
			fin.close()
		    if fout:
			fout.close()
		    if nrtry > 1:
			nrtry = nrtry - 1
			fin = None
		        fout = None
		    else:
			return self._owner._error_from_exception(e,"when downloading {}".format(uri))

	def stream_to(self,fname,fout):
	    """
	    http get of the 'fname' and write to the stream 'fout'
	    """
	    uri = "{}/{}".format(self.uri,fname)
	    if self.verbose:
		print "streaming {}".format(fname)
	    nrtry = 1
	    size = self.blocksize
	    fin = None
	    while True:
		try:
		    fin = urllib2.urlopen(uri)
		    data = fin.read(size)
		    while data:
			fout.write(data)
			data = fin.read(size)
		    fin.close()
		    return True
		except Exception as e:
		    if fin:
			fin.close()
		    if nrtry > 1:
			nrtry = nrtry - 1
			fin = None
		        fout = None
		    else:
			return self._owner._error_from_exception(e,"when streaming {}".format(uri))
	    
    class ConnectorRSYNC(Connector):
	"""
	The RSYNC connector
	"""
	def __init__(self,owner,target,rsyncdir,remove_at_disconnect):
	    """
	    init current instance
	    """
	    GbsTree.Connector.__init__(self,owner)
	    self.target = target
	    self.rsyncdir = rsyncdir
	    key = hashlib.md5(target).hexdigest()
	    self.connected = False
	    self.rootdir = os.path.join(rsyncdir,key)
	    self.rootinfo = self.rootdir + ".info"
	    self.remove_at_disconnect = remove_at_disconnect
	    self._sync_done = []

	def scheme(self):
	    """
	    Returns the protocol scheme
	    Result is "rsync"
	    """
	    return "rsync"

	def connect(self):
	    """
	    make the rsync
	    """
	    assert not self.connected

	    # creates the directory if needed
	    try:
		if not os.path.isdir(self.rootdir):
		    os.makedirs(self.rootdir)
		if not os.path.exists(self.rootinfo):
		    f = open(self.rootinfo,"w")
		    f.write(self.target)
		    f.close()
	    except Exception as e:
		return self._owner._error_from_exception(e,"when preparing rsync")

	    self.connected = True
	    return True

	def disconnect(self):
	    """
	    """
	    assert self.connected
	    if self.remove_at_disconnect:
		try:
		    shutil.rmtree(self.rootdir)
		    os.remove(self.rootinfo)
		except Exception:
		    pass # FIXME what to do?
	    self.connected = False
	    self._sync_done = []

	def _sync(self,directory):
	    """
	    Rsync the 'directory'
	    """
	    assert self.connected

	    # get names
	    local = os.path.join(self.rootdir,directory)
	    remote = os.path.join(self.target,directory)+"/"
	    if self.verbose:
		print "rsyncing "+remote

	    # creates the directory if needed
	    if not os.path.isdir(local):
		try:
		    os.makedirs(local)
		except Exception as e:
		    return self._owner._error_from_exception(e,"when preparing rsync")
	    
	    # compose the command
	    command = [ "rsync",
		    "--archive",
		    "--hard-links",
		    "--delete",
		    "--checksum",
		    # "--inplace",   # FIXME: check it, removed to improve updating
		    "--chmod=u+w",
		    "--progress",
		    "--exclude=image-configs.xml", 
		    "--exclude=images", 
		    "--exclude=buildlogs", 
		    "--exclude=image-configs", 
		    "--exclude=reports",
		    remote,
		    "." ]

	    # make the rsync
	    sys.stdout.flush() # as output of rsync goes to stdout, flush it before
	    rsync = subprocess.Popen(command, cwd = local, stderr = subprocess.PIPE)
	    rsync.wait()
	    if rsync.returncode != 0:
		self._owner._error("rsync error for {}: {}".format(remote,rsync.stderr.read()))
		rsync.stderr.close()
		return False

	    self._sync_done.append(directory)
	    rsync.stderr.close()
	    return True

	def _ensure(self,fname):
	    """
	    Ensure tat the file 'fname' is rsynced
	    Curently, it works by directory
	    """
	    assert self.connected
	    for d in self._sync_done:
		if fname.startswith(d):
		    return True
	    return self._sync(os.path.dirname(fname))

	def read(self,fname):
	    """
	    return the document at the given 'fname' or None in case of error
	    """
	    assert self.connected
	    if not self._ensure(fname):
		return None
	    src = os.path.join(self.rootdir,fname)
	    try:
	        fin = open(src,"r")
		result = fin.read()
		fin.close()
		return result
	    except Excepion as e:
		self._owner._error_from_exception(e, "when reading {}".format(fname))
		return None

	def download_to(self,fname,filename):
	    """
	    get of the 'fname' and save it into the given 'filename'
	    """
	    assert self.connected
	    assert os.path.isdir(os.path.dirname(filename)), "the directory for '{}' must exists".format(filename)
	    if not self._ensure(fname):
		return False
	    src = os.path.join(self.rootdir,fname)
	    if self.verbose:
		print "downloading {}".format(fname)
	    try:
		if os.path.exists(filename):
		    os.remove(filename)
		os.link(src, filename)
		return True
	    except Exception as e:
		try:
		    shutil.copy(src, filename)
		    return True
		except Exception as e:
		    return self._owner._error_from_exception(e,"when downloading {}".format(src))

	def stream_to(self,fname,fout):
	    """
	    get of the 'fname' and write to the stream 'fout'
	    """
	    assert self.connected
	    if not self._ensure(fname):
		return False
	    src = os.path.join(self.rootdir,fname)
	    if self.verbose:
		print "streaming {}".format(fname)
	    size = 65500
	    fin = None
	    try:
	        fin = open(src,"r")
		data = fin.read(size)
		while data:
		    fout.write(data)
		    data = fin.read(size)
		fin.close()
		return True
	    except Exception as e:
		self._owner._error_from_exception(e, "when streaming {}".format(src))
		return False
	    

