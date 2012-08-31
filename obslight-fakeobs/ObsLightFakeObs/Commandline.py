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
Commandline client for FakeOBS.

@author: Florent Vennetier
"""

import os
import sys
import cmdln
import Config
import ProjectManager

class FakeObsCommandline(cmdln.Cmdln):
    name = "obslight-fakeobs"

    # Overrides cmdln.Cmdln.get_optparser()
    def get_optparser(self):
        # FVE: I wanted to use super(FakeObsCommandline, self).get_optparser()
        #      but cmdln.Cmdln is not a new-style class
        op = cmdln.Cmdln.get_optparser(self)
        op.add_option("-c", "--config", dest="config",
                      help=("specify an alternative configuration file\n" +
                            "(%s by default)" % Config.DEFAULT_CONFIG_PATH))
        return op

    # Implements cmdln.Cmdln.postoptparse()
    def postoptparse(self):
        if self.options.config is None:
            Config.loadConfig()
        else:
            Config.loadConfig(self.options.config)

    @cmdln.alias("ls")
    @cmdln.option("-d", "--dependencies", action="store_true",
                  help="list also project dependencies for each target")
    @cmdln.option("-t", "--targets", action="store_true",
                  help="list targets for each project")
    def do_list(self, subcmd, opts):
        """${cmd_name}: get the list of installed projects
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        for prj in ProjectManager.getProjectList():
            print prj
            if opts.targets or opts.dependencies:
                for target in ProjectManager.getTargetList(prj):
                    archList = ProjectManager.getArchList(prj, target)
                    print "  %s (%s)" % (target, ", ".join(archList)),
                    if opts.dependencies:
                        deps = ProjectManager.getProjectDependencies(prj,
                                                                     target)
                        deps = ["%s(%s)" % (x[0], x[1]) for x in deps
                                if x != (prj, target)]
                        print "depends on " + (", ".join(deps) or "itself")
                    else:
                        print
                print

    @cmdln.alias("delete", "del", "rm")
    def do_remove(self, subcmd, opts, project):
        """${cmd_name}: remove a project
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        ProjectManager.failIfProjectDoesNotExist(project)
        ProjectManager.removeProject(project)

    @cmdln.alias("import-from-server")
    @cmdln.option("-n", "--new-name", dest="new_name",
                  help="rename project to NEW_NAME")
    @cmdln.option("-a", "--arch", action="append", dest="archs",
                  default=[],
                  help="an architecture type to grab")
    @cmdln.option("-t", "--target", action="append", dest="targets",
                  default=[],
                  help="the name of a build target to grab")
    @cmdln.option("-r", "--rsync",
                  help="rsync URL to fetch repositories from")
    @cmdln.option("-A", "--api",
                  help="API URL of the OBS server to import project from")
    def do_grab(self, subcmd, opts, project):
        """${cmd_name}: import a project from server
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        new_name = opts.new_name or project
        ProjectManager.grabProject(opts.api, opts.rsync, project,
                                   opts.targets, opts.archs, new_name)

    @cmdln.alias("verify")
    def do_check(self, subcmd, opts, project):
        """${cmd_name}: check the integrity of a project,
                        search for common errors
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        ProjectManager.failIfProjectDoesNotExist(project)

        testList = [(ProjectManager.checkProjectConfigAndMeta,
                     "Checking _config and _meta..."),
                    (ProjectManager.checkProjectFull,
                     "Checking :full..."),
                    (ProjectManager.checkProjectRepository,
                     "Checking repository..."),
                    (ProjectManager.checkAllPackagesFiles,
                     "Checking packages files...")]

        gotError = False
        for test, message in testList:
            print message,
            sys.stdout.flush()
            errors = test(project)
            if len(errors) > 0:
                gotError = True
                print "Error"
                for error in errors:
                    print >> sys.stderr, error
                print
            else:
                print "OK"

        if gotError:
            return 1
        else:
            print "OK"

    @cmdln.alias("archive")
    @cmdln.option("-o", "--output-file",
                  help="name of the archive to create")
    def do_export(self, subcmd, opts, project):
        """${cmd_name}: export a project to an archive
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        ProjectManager.failIfProjectDoesNotExist(project)
        ProjectManager.exportProject(project, opts.output_file)

    @cmdln.alias("extract")
    @cmdln.option("-n", "--new-name", dest="new_name",
                  help="rename project to NEW_NAME")
    def do_import(self, subcmd, opts, archive):
        """${cmd_name}: import a project from an archive
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        ProjectManager.importProject(archive, opts.new_name)


if __name__ == "__main__":
    commandline = FakeObsCommandline()
    try:
        res = commandline.main()
    except ValueError as ve:
        print >> sys.stderr, ve
        res = 1
    except IOError as ioe:
        commandline.do_help([sys.argv[0]])
        print
        print >> sys.stderr, ioe
        res = 1
    sys.exit(res)
