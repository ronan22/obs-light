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

import sys
import cmdln
import Config
import ObsManager
import ProjectManager
import DistributionsManager
import Utils

class FakeObsCommandline(cmdln.Cmdln):
    name = "obslight-fakeobs"

    # Overrides cmdln.Cmdln.get_optparser()
    def get_optparser(self):
        # FVE: I wanted to use super(FakeObsCommandline, self).get_optparser()
        #      but cmdln.Cmdln is not a new-style class
        op = cmdln.Cmdln.get_optparser(self)
        op.add_option("-c", "--config", dest="config",
                      help=("specify an alternative configuration file\n" +
                            "(by default: %s)" % Config.DEFAULT_CONFIG_PATH))
        return op

    # Implements cmdln.Cmdln.postoptparse()
    def postoptparse(self):
        # Don't load config if help asked
        if (len(self.optparser.rargs) > 0 and
            self._get_canonical_cmd_name(self.optparser.rargs[0]) != "help"):
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
        projectList = ProjectManager.getProjectList()

        def projectAndTargetExists(project, target):
            return (project in projectList and
                    target in ProjectManager.getTargetList(project))

        if opts.dependencies:
            msg = "Dependencies in " + Utils.colorize("red", "red")
            msg += " are missing\n"
            print msg

        for prj in projectList:
            print Utils.colorize(prj, "green")
            if opts.targets or opts.dependencies:
                for target in ProjectManager.getTargetList(prj):
                    archList = ProjectManager.getArchList(prj, target)
                    print "  %s (%s)" % (target, ", ".join(archList)),
                    if opts.dependencies:
                        deps = ProjectManager.getProjectDependencies(prj,
                                                                     target)
                        realDeps = []
                        for dprj, dtarget in deps:
                            if (dprj, dtarget) == (prj, target):
                                continue
                            dep = "%s(%s)" % (dprj, dtarget)
                            if not projectAndTargetExists(dprj, dtarget):
                                dep = Utils.colorize(dep, "red")
                            realDeps.append(dep)
                        print "depends on " + (", ".join(realDeps) or "itself")
                    else:
                        print
                print

    @cmdln.alias("delete", "del", "rm")
    def do_remove(self, subcmd, opts, project):
        """${cmd_name}: remove a project

        You need to be root to run this.
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        Utils.failIfUserIsNotRoot()
        ProjectManager.failIfProjectDoesNotExist(project)
        ProjectManager.removeProject(project)

    @cmdln.alias("importfromserver")
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
        
        API and RSYNC parameters are mandatory.
        You need to be root to run this.
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        Utils.failIfUserIsNotRoot()
        new_name = opts.new_name or project
        if opts.api is None:
            raise ValueError("You must provide an API! (use -A or --api)")
        if opts.rsync is None:
            raise ValueError("You must provide an rsync URL! (use -r or --rsync)")
        effectiveName = ProjectManager.grabProject(opts.api, opts.rsync,
                                                   project, opts.targets,
                                                   opts.archs, new_name)
        msg = "Project '%s' grabbed" % effectiveName
        print Utils.colorize(msg, "green")
        packageList = ProjectManager.getPackageList(effectiveName)
        msg = "It contains %d packages" % len(packageList)
        print Utils.colorize(msg, "green")
        print
        return self.do_check(subcmd, opts, effectiveName)

    @cmdln.alias("verify")
    def do_check(self, subcmd, opts, project):
        """${cmd_name}: check the integrity of a project,
                        search for common errors
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        ProjectManager.failIfProjectDoesNotExist(project)

        testList = [(ProjectManager.checkProjectConfigAndMeta,
                     " --- Step 1: checking _config and _meta..."),
                    (ProjectManager.checkProjectFull,
                     " --- Step 2: checking :full..."),
                    (ProjectManager.checkProjectRepository,
                     " --- Step 3: checking repository..."),
                    (ProjectManager.checkAllPackagesFiles,
                     " --- Step 4: checking packages files..."),
                    (ProjectManager.checkProjectDependencies,
                     " --- Step 5: checking project dependencies...")]

        print Utils.colorize("Checking project '%s'" % project, "green")
        gotError = False
        for test, message in testList:
            print Utils.colorize(message, "green"),
            sys.stdout.flush()
            errors = test(project)
            if len(errors) > 0:
                gotError = True
                print Utils.colorize("Error", "red")
                for error in errors:
                    print >> sys.stderr, error
                print
            else:
                print Utils.colorize("OK", "green")

        if gotError:
            return 1
        else:
            print "OK"

    @cmdln.alias("archive")
    @cmdln.option("-o", "--output-file",
                  help="name of the archive to create")
    def do_export(self, subcmd, opts, project):
        """${cmd_name}: export a project to an archive
        
        Default compression format is gzip. You may override by
        giving '.tar.bz2' or '.tar.xz' suffix to the archive.
        
        You should consider running 'shrink' before exporting.
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        ProjectManager.failIfProjectDoesNotExist(project)
        archive = ProjectManager.exportProject(project, opts.output_file)
        if archive is not None:
            msg = "Project '%s' exported to %s" % (project, archive)
            print Utils.colorize(msg, "green")

    @cmdln.alias("extract")
    @cmdln.option("-n", "--new-name", dest="new_name",
                  help="rename project to NEW_NAME")
    def do_import(self, subcmd, opts, archive):
        """${cmd_name}: import a project from an archive
        
        You need to be root to run this.
        ${cmd_usage}
        ${cmd_option_list}
        """
        Utils.failIfUserIsNotRoot()
        effectiveName = ProjectManager.importProject(archive, opts.new_name)
        msg = "Project '%s' correctly imported" % effectiveName
        print Utils.colorize(msg, "green")

    @cmdln.option("-s", "--symbolic", action="store_true",
                  help="make symbolic links instead of hard links")
    def do_shrink(self, subcmd, opts, project):
        """${cmd_name}: reduce disk usage by making hard links between RPMs
        
        You need to be root to run this.
        ${cmd_usage}
        ${cmd_option_list}
        """
        def mySum(x, y):
            if isinstance(x, int):
                return x + y[2]
            else:
                return x[2] + y[2]

        Utils.failIfUserIsNotRoot()
        msg = "Shrinking project '%s' using %s links"
        msg = msg % (project, "symbolic" if opts.symbolic else "hard")
        print Utils.colorize(msg, "green")
        linkedRpms = ProjectManager.shrinkProject(project, opts.symbolic)
        sizeSaved = reduce(mySum, linkedRpms, 0)
        msg = "%d RPMs linked, saving %d bytes" % (len(linkedRpms), sizeSaved)
        print Utils.colorize(msg, "green")

    @cmdln.option("-c", "--osc-config-file",
                  help="specify a configuration file for osc")
    def do_createlink(self, subcmd, opts):
        """${cmd_name}: create the link to the fakeobs API
        on the OBS running on localhost

        You need to be on an OBS Light server appliance to run this
        command without argument. If you run it on another kind of
        OBS server, you will need to specify the osc configuration
        file of an administrator (simple users are not allowed
        to create project links).

        ${cmd_usage}
        ${cmd_option_list}
        """
        warnMsg = ObsManager.createFakeObsLink(opts.osc_config_file)
        if warnMsg is not None:
            print Utils.colorize(warnMsg, "yellow")

    def do_updatedistributions(self, subcmd, opts):
        """${cmd_name}: update OBS' pre-configured distributions
        (build targets) with currently installed FakeOBS projects.
        This command is automatically run after grab, import and remove.

        You need to be root to run this.

        ${cmd_usage}
        ${cmd_option_list}
        """
        Utils.failIfUserIsNotRoot()
        DistributionsManager.updateFakeObsDistributions()

if __name__ == "__main__":
    commandline = FakeObsCommandline()
    try:
        res = commandline.main()
    except ValueError as ve:
        print >> sys.stderr, Utils.colorize(str(ve), "red")
        res = 1
    except EnvironmentError as ioe:
#        commandline.do_help([sys.argv[0]])
        print
        print >> sys.stderr, Utils.colorize(str(ioe), "red")
        if hasattr(ioe, "fakeobs_config_error"):
            msg = "See '--config' option"
            print >> sys.stderr, Utils.colorize(msg, "red")
        res = 1
    sys.exit(res)
