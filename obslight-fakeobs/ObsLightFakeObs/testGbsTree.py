#!/usr/bin/python

import sys
import GbsTree

verbose = True

uri = "http://download.tizen.org/releases/2.0alpha/daily/latest/"

#doraise = False
#gt = GbsTree.GbsTree(uri, doraise, verbose)
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
targets = [ "standard" ]
archs = [ "ia32" ]
orders = [ "tizen-base", "tizen-main" ]
alias = [ "tizen-base=Base", "tizen-main=Main", "ia32=standard" ]

n = ProjectManager.grabGBSTree(uri, name, targets, archs, orders, alias, verbose)
print n



