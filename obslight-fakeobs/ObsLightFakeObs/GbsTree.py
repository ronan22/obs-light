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
#import hashlib
#from xml.etree import ElementTree
import shutil

#import Utils
import Config

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

    def __init__(self,url,should_raise=False,verbose=False):
	"""
	attach the current object to a given URL
	"""
	self.should_raise = should_raise
	self.verbose = verbose
	self.clear_error()
	self.connected = False
	self.url = url.strip()
	self._connector = None
	rm = re.match("^(\w+:)?(.*)$",self.url)
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

    def iterate_on_entries(self):
	"""
	"""
	assert self.connected
	assert self.current_package
	for e in self.current_pack_meta["pklist"]:
	    yield e

    def download_package_to(self,rootdir,addarch=True,dont_fail=False):
	"""
	do
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
	if addarch:
	    ad = {}
	    for e in self.current_pack_meta["pklist"]:
		a = e.get_arch()
		r = e.get_rpm_name()
		u = "{}/{}/{}".format(root,a,r)
		d = ad.get(a)
		if not d:
		    d = os.path.join(rootdir,a)
		    ad[a] = d
		    if not os.path.isdir(d):
			os.makedirs(d)
		n = os.path.join(d,r)
		if not self._connector.download_to(u,n):
		    if dont_fail:
			print "WARNING: can't get RPM {} in {}/{}".format(r,root,a)
		    else:
			return False
	else:
	    for e in self.current_pack_meta["pklist"]:
		r = e.get_rpm_name()
		u = "{}/{}".format(root,r)
		n = os.path.join(d,r)
		if not self._connector.download_to(u,n):
		    if dont_fail:
			print "WARNING: can't get RPM {} in {}".format(r,root)
		    else:
			return False
	return True

    def extract_package_rpms_to(self,rootdir,addarch=True,dont_fail=False):
	"""
	do
	"""
	assert self.connected
	assert self.current_package
	assert os.path.isdir(rootdir)

	# root
	root = self.path_package

	# copy the packages of the list
	if addarch:
	    ad = {}
	    for e in self.current_pack_meta["pklist"]:
		n = e.get_name()
		a = e.get_arch()
		r = e.get_rpm_name()
		u = "{}/{}/{}".format(root,a,r)
		d = ad.get(a)
		if not d:
		    d = os.path.join(rootdir,a)
		    ad[a] = d
		    if not os.path.isdir(d):
			os.makedirs(d)
		d = os.path.join(d,n)
		if not os.path.isdir(d):
		    os.makedirs(d)
		if not self._extract_rpm_to(u,d):
		    if dont_fail:
			print "WARNING: can't extract RPM {} in {}/{}".format(r,root,a)
		    else:
			return False
	else:
	    for e in self.current_pack_meta["pklist"]:
		n = e.get_name()
		r = e.get_rpm_name()
		u = "{}/{}".format(root,r)
		d = os.path.join(rootdir,n)
		if not os.path.isdir(d):
		    os.makedirs(d)
		if not self._extract_rpm_to(u,d):
		    if dont_fail:
			print "WARNING: can't extract RPM {} in {}".format(r,root)
		    else:
			return False
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
	doc = xml.dom.minidom.parseString(fpri)
	pklist = []
	archlst = {}
	for p in doc.getElementsByTagName("package"):
	    assert p.nodeType==p.ELEMENT_NODE
	    t = p.getAttribute("type")
	    if t and t=="rpm":
		pn = p.getElementsByTagName("name")
		pa = p.getElementsByTagName("arch")
		pv = p.getElementsByTagName("version")
		if pn and pa and pv and len(pn)==1 and len(pa)==1 and len(pv) == 1:
		    pn = pn[0]
		    pa = pa[0]
		    pv = pv[0]
		    assert pn.nodeType==pn.ELEMENT_NODE
		    assert pn.firstChild and pn.firstChild.nodeType == pn.TEXT_NODE
		    name = pn.firstChild.data.strip()
		    assert pa.nodeType==pa.ELEMENT_NODE
		    assert pa.firstChild and pa.firstChild.nodeType == pa.TEXT_NODE
		    arch = pa.firstChild.data.strip()
		    assert pv.nodeType==pv.ELEMENT_NODE
		    epoch = pv.getAttribute("epoch")
		    ver = pv.getAttribute("ver")
		    rel = pv.getAttribute("rel")
		    # records the item
		    if name and arch and ver and rel:
			pklist.append(self._ListEntry(name,arch,epoch,ver,rel))
		    # records the arch
		    archlst[arch] = True

	self.current_pack_meta = {
		    "repomd": repomd,
		    "data":   data,
		    "pklist": pklist,
		    "archs": archlst.keys()
		    }
	return True

    # internal utils
    # --------------

    def _unzip(self,data):
	"""
	return an unzipped version of a given content
	"""
	while True:
	    if data[0]==chr(31) or data[1]==chr(139):
		data = self._filter(data,["gunzip","-"])
	    else:
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
	    err = self._connector.message
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
	base = schema + self.path
	connector = GbsTree.ConnectorHttp(base,self.nrtry,self.should_raise,self.verbose)
	bxml = connector.read("{}/{}".format(self.dir_build,self.file_buildxml))
	if bxml is  None:
	    return False
	if not self._read_build_xml(bxml):
	    return False
	self.connected = True
	self._connector = connector
	return True

    # internal rsync
    # --------------
    def _connect_rsync(self):
	"""
	connect to the URL using the rsync protocol
	"""
	# TODO: currently not implemented
	self._original_error("rsync protocol not yet implemented")
	return False
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
    class ErrorManager:
	"""
	"""
	def __init__(self,should_raise=False,verbose=False):
	    """
	    Initialisation
	    """
	    self.should_raise = should_raise
	    self.verbose = verbose
	    self.is_set = False
	    self.message = ""
	    self._original = ""

	def clear(self):
	    """
	    clear any pending error
	    """
	    self.error_message = ""
	    self.has_error = False
	    self._original_error_message = ""

	def error(self,message):
	    """
	    set the 'is_set' status and the 'message'
	    also raise an exception if 'should_raise' is True
	    """
	    self.is_set = True
	    if self._original:
		self.message = message + "\ndetail:" + self._original
		self._original = ""
	    else:
		self.message = message
	    if self.verbose:
		print "GbsTree ERROR:"
		print "=============="
		print self.message
	    if self.should_raise:
		raise Exception(self.message)
	    return False
    
	def error_from_exception(self, exception, message):
	    """
	    set the 'is_set' status and the 'message'
	    according to the exception and the given message.
	    also raise an exception if 'should_raise' is True
	    """
	    self.error("when {}\nexception catched:\n{}".format(message, str(exception)))

	def error_from(self,other):
	    """
	    set the error from an 'other' instance of ErrorManager
	    """
	    assert other.is_set
	    self.error(other.message)
    
	def set_original(self,message):
	    """
	    append 'message' to the original error
	    """
	    self._original = self._original + "\n... " + message
    
    
	def set_original_from_exception(self, exception, message):
	    """
	    append 'message' and 'exception' to the original error
	    """
	    self.set_original("when {}\nexception catched:\n{}".format(message, str(exception)))
    
    class _ListEntry:
	"""
	Classe for instances of the list of rpms
	"""
	def __init__(self,name,arch,epoch,ver,rel):
	    """
	    Init the current instance for the given 'name', 'arch', 'ver' and 'rel'
	    """
	    self.name = name
	    self.arch = arch
	    self.epoch = epoch
	    self.version = ver
	    self.release = rel
	def get_name(self):
	    """
	    Return the name
	    """
	    return self.name
	def get_arch(self):
	    """
	    Return the arch
	    """
	    return self.arch
	def get_epoch(self):
	    """
	    Return the epoch
	    """
	    return self.epoch
	def get_version(self):
	    """
	    Return the version
	    """
	    return self.version
	def get_release(self):
	    """
	    Return the release
	    """
	    return self.release
	def get_rpm_name(self):
	    """
	    Return the name of the rpm
	    """
	    if self.epoch != "0" and False: # FIXME: how is epoch to be treated
	    	return "{}-{}:{}-{}.{}.rpm".format(self.name,self.epoch,self.version,self.release,self.arch)
	    else:
		return "{}-{}-{}.{}.rpm".format(self.name,self.version,self.release,self.arch)
	def __repr__(self):
	    return self.get_rpm_name()


    class Connector(ErrorManager):
	"""
	Base class for connectors
	"""
	def __init__(self,should_raise=False,verbose=False):
	    """
	    """
	    GbsTree.ErrorManager.__init__(self,should_raise,verbose)
	def disconnect(self):
	    """
	    """
	    pass

    class ConnectorHttp(Connector):
	"""
	The HTTP/HTTPS connector
	"""
	def __init__(self,uri,nrtry=1,should_raise=False,verbose=False):
	    """
	    init current instance
	    """
	    GbsTree.Connector.__init__(self,should_raise,verbose)
	    self.uri = uri
	    self.nrtry = nrtry
	    self.blocksize = 10000000 # 10 megabyte block

	def read(self,fname):
	    """
	    return the document at the given 'fname' or None in case of error
	    """
	    uri = "{}/{}".format(self.uri,fname)
	    if self.verbose:
		print "accessing {}".format(uri)
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
		    self.set_original_from_exception(e, "when fetching {}".format(uri))
		    return None

	def download_to(self,fname,filename):
	    """
	    http get of the 'fname' and save it into the given 'filename'
	    """
	    assert os.path.isdir(os.path.dirname(filename)), "the directory for '{}' must exists".format(filename)
	    uri = "{}/{}".format(self.uri,fname)
	    if self.verbose:
		print "downloading {} to {}".format(uri,filename)
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
			return self.error_from_exception(e,"when downloading {}".format(uri))

	def stream_to(self,fname,fout):
	    """
	    http get of the 'fname' and write to the stream 'fout'
	    """
	    uri = "{}/{}".format(self.uri,fname)
	    if self.verbose:
		print "streaming {}".format(uri)
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
			return self.error_from_exception(e,"when streaming {}".format(uri))
	    
    class ConnectorRsync(Connector):
	"""
	The RSYNC connector
	"""
	def __init__(self,target,nrtry=1,should_raise=False,verbose=False):
	    """
	    init current instance
	    """
	    GbsTree.Connector.__init__(self,should_raise,verbose)
	    self.target = target
	    self.rootdir = None
	    self.blocksize = 10000000 # 10 megabyte block

	def connect_at(self,rootdir):
	    """
	    """
	    #TODO
	    return False
	    self.rootdir = rootdir
	    return True

	def disconnect(self):
	    """
	    """
	    shutil.rmtree(self.rootdir)
	    self.rootdir = None

	def read(self,fname):
	    """
	    return the document at the given 'fname' or None in case of error
	    """
	    assert(self.rootdir)
	    src = os.path.join(self.rootdir,fname)
	    try:
	        fin = open(src,"r")
		result = fin.read()
		fin.close()
		return result
	    except Excepion as e:
		self.error_from_exception(e, "when reading {}".format(src))
		return None

	def download_to(self,fname,filename):
	    """
	    get of the 'fname' and save it into the given 'filename'
	    """
	    assert(self.rootdir)
	    assert os.path.isdir(os.path.dirname(filename)), "the directory for '{}' must exists".format(filename)
	    src = os.path.join(self.rootdir,fname)
	    if self.verbose:
		print "downloading {} to {}".format(src,filename)
	    try:
		os.link(src, filename)
		return True
	    except Exception as e:
		try:
		    shutil.copy(src, filename)
		    return True
		except Exception as e:
		    return self.error_from_exception(e,"when downloading {}".format(src))

	def stream_to(self,fname,fout):
	    """
	    get of the 'fname' and write to the stream 'fout'
	    """
	    assert(self.rootdir)
	    src = os.path.join(self.rootdir,fname)
	    if self.verbose:
		print "streaming {}".format(src)
	    size = self.blocksize
	    fin = None
	    try:
	        fin = open(src,"r")
		data = fin.read(size)
		while data:
		    fout.write(data)
		    data = fin.read(size)
		fin.close()
		return True
	    except Excepion as e:
		self.error_from_exception(e, "when streaming {}".format(src))
		return None
	    

