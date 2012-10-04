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


class GbsTree:
	"""
	Management of a GBS Tree
	"""

	# name of the builddir
	dir_build = "/builddata" 
	dir_repos = "/repos" 

	# name of the build xml file
	file_buildxml = dir_build + "/build.xml"


	def __init__(self,url,should_raise=False):
		"""
		attach the current object to a given URL
		"""
		self.clear_error()
		self.should_raise = should_raise
		self.connected = None
		self.url = url.strip()
		rm = re.match("^(\w+:)?(.*)$",self.url)
		assert rm
		self.protocol = rm.group(1).lower()
		self.path = rm.group(2)

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
		self.connected = schema
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
		print "scanning "+xmlstr
		doc = xml.dom.minidom.parseString(xmlstr)
		archs = as_str_list(doc,"arch")
		print "  retrieved archs: "+str(archs)
		repos = as_str_list(doc,"repo")
		print "  retrieved repos: "+str(repos)
		confs = as_str_list(doc,"buildconf")
		print "  retrieved confs: "+str(confs)
		ids = as_str_list(doc,"id")
		print "  retrieved confs: "+str(ids)
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

	# internal utils
	# --------------
	def _http_read(self,uri):
		"""
		return the document at the given 'uri' or None in case of error
		"""
		try:
			f = urllib2.urlopen(uri)
			result = f.read()
			f.close()
			return result
		except Exception as e:
			self._original_error("exception "+str(e)+" when fetching "+uri)
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
		
	def _error(self,string):
		"""
		set the 'has_error' status and the 'error_message'
		also raise an exception if 'should_raise' is True
		(see __init__ constructor)
		"""
		self.has_error = True
		if self._original_error_message:
			self.error_message = string + "\ndetail:"+self._original_error_message
			self._original_error_message = ""
		else:
			self.error_message = string
		if self.should_raise:
			raise Exception(self.error_message)
		return False

	def _original_error(self,msg):
		"""
		set the original error message from e
		"""
		self._original_error_message = self._original_error_message + "\n... " + msg



