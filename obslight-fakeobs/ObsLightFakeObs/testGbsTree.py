#!/usr/bin/python

import sys
import GbsTree

verbose = True
force = True

uri = "http://download.tizen.org/releases/2.0alpha/daily/latest/"
uri = "rsync://download.tizen.org/snapshots/2.0alpha/common/latest/"

options = {
    "verbose":      verbose,
    "should_raise": False,
    "rsynckeep":    True,
}

#doraise = False
#gt = GbsTree.GbsTree(uri, **options)
#c = gt.connect()
#
#if c:
#	print "CONNECTED to "+uri
#else:
#	print "ERROR!!! connection failed!!!!"
#	print gt.error_message
#	sys.exit(1)

import Config
import ProjectManager


Config.loadConfig("testGbsTreeCfg")

uri = uri
name = "Tizen:2.0"
targets = [ "ia32" ]
archs = None
orders = [ "tizen-base", "tizen-main" ]

n = ProjectManager.grabGBSTree(uri, name, targets, archs, orders, verbose, force)
print n



