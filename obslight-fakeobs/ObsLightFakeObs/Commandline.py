#!/usr/bin/python
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
Commandline client for FakeOBS.

@author: Florent Vennetier
@author: José Bollo
"""

import sys
import cmdln

import Config
import Converter
import DistributionsManager
import ObsManager
import ProjectManager
import Utils

class FakeObsCommandline(cmdln.Cmdln):
    name = "obslight-fakeobs"


    def print_version(self, *args, **kwargs):
        """Print version and exit. `args` and `kwargs` not used."""
        version = Utils.getFakeObsVersion()
        print version
        sys.exit(0)

    # Overrides cmdln.Cmdln.get_optparser()
    def get_optparser(self):
        # FVE: I wanted to use super(FakeObsCommandline, self).get_optparser()
        #      but cmdln.Cmdln is not a new-style class
        op = cmdln.Cmdln.get_optparser(self)
        op.add_option("-c", "--config", dest="config",
                      help=("specify an alternative configuration file\n" +
                            "(by default: %s)" % Config.DEFAULT_CONFIG_PATH))
        op.add_option("-V", "--version", nargs=0, action="callback",
                      callback=self.print_version,
                      help="show version and exit")
        return op

    # Implements cmdln.Cmdln.postoptparse()
    def postoptparse(self):
        # Don't load config if help or version asked
        if (len(self.optparser.rargs) > 0 and
            (self._get_canonical_cmd_name(self.optparser.rargs[0]) not in
             ["help", "version"])):
            if self.options.config is None:
                Config.loadConfig()
            else:
                Config.loadConfig(self.options.config)

    @cmdln.alias("ls")
    @cmdln.option("-d", "--dependencies", action="store_true",
                  help="list also project dependencies for each target")
    @cmdln.option("-t", "--targets", action="store_true",
                  help="list targets for each project")
    @cmdln.option("-u", "--update-info", action="store_true",
                  help="show update informations for each project")
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

            if opts.update_info:
                infos = ProjectManager.getUpdateInformations(prj)
                print "  Update informations:"
                print "    Original name:\t%(project)s" % infos
                print "    Update URL:\t\t%(rsync_update_url)s" % infos
                print "    Last update:\t%(last_update)s" % infos

            if opts.targets or opts.dependencies:
                print "  Targets:"
                for target in ProjectManager.getTargetList(prj):
                    archList = ProjectManager.getArchList(prj, target)
                    print "    %s (%s)" % (target, ", ".join(archList)),
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
                  help="rsync URL to fetch repositories from. If rsync server is not available, you can use http(s) URL instead.")
    @cmdln.option("--repo-user", dest="repo_user",
                  default=None,
                  help="set the http(s) user name for repositories")
    @cmdln.option("--repo-password", dest="repo_password",
                  default=None,
                  help="set the http(s) user password for repositories")
    @cmdln.option("-A", "--api",
                  help="API URL of the OBS server to import project from")
    @cmdln.option("--api-user", dest="api_user",
                  default=None,
                  help="set the API user name for OBS")
    @cmdln.option("--api-password", dest="api_password",
                  default=None,
                  help="set the API user password for OBS")
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
                                                   opts.archs, new_name,
                                                   opts.api_user, opts.api_password,
                                                   opts.repo_user, opts.repo_password)
        msg = "Project '%s' grabbed" % effectiveName
        print Utils.colorize(msg, "green")
        packageList = ProjectManager.getPackageList(effectiveName)
        msg = "It contains %d packages" % len(packageList)
        print Utils.colorize(msg, "green")
        print
        return self.do_check(subcmd, opts, effectiveName)

    @cmdln.alias("fromgbs")
    @cmdln.option("-n", "--name", dest="name",
                  help="set the project to NAME (mandatory option")
    @cmdln.option("-t", "--target", action="append", dest="targets",
                  default=[],
                  help="the name of a build target to grab (caution, targets are also named 'conf' in build.xml)")
    @cmdln.option("-a", "--arch", action="append", dest="archs",
                  default=[],
                  help="architecture(s) to grab, dont put anything for all archs")
    @cmdln.option("-o", "--order", action="append", dest="orders",
                  default=[],
                  help="the name of a sub project ordering the dependencies.")
    @cmdln.option("-v", "--verbose", action="store_true", dest="verbose",
                  help="print extra informations")
    @cmdln.option("-f", "--force", action="store_true", dest="force",
                  help="perform the grab even if he project aleady exists")
    @cmdln.option("-k", "--rsynckeep", action="store_false", dest="rsynckeep",
                  help="dont remove the rsync data at the end of the grab")
    @cmdln.option("--repo-user", dest="repo_user",
                  default=None,
                  help="set the http(s) user name for repositories")
    @cmdln.option("--repo-password", dest="repo_password",
                  default=None,
                  help="set the http(s) user password for repositories")
    def do_grabgbs(self, subcmd, opts, url):
        """${cmd_name}: import a project from a GBS tree
        
        You need to be root to run this.
        The option --name is MANDATORY.
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        Utils.failIfUserIsNotRoot()
        if opts.name is None:
            raise ValueError("You must provide a NAME! (use -n or --name)")
        name = opts.name
	if not opts.archs:
	    opts.archs = None
	elif len(opts.archs) == 1 and opts.archs[0] == "*":
	    opts.archs = None
        effectiveName = ProjectManager.grabGBSTree(url, name, opts.targets, opts.archs, opts.orders, opts.verbose, opts.force,opts.repo_user,opts.repo_password)
        msg = "Project '%s' grabbed" % effectiveName
        print Utils.colorize(msg, "green")
        #packageList = ProjectManager.getPackageList(effectiveName)
        #msg = "It contains %d packages" % len(packageList)
        #print Utils.colorize(msg, "green")
        #print
        #return self.do_check(subcmd, opts, effectiveName)
        return True

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
            if isinstance(x, (int, long, float, complex)):
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

    @cmdln.option("-n", "--new-name", dest="new_name",
                  help="rename project to NEW_NAME while converting")
    def do_convert(self, subcmd, opts, project, release):
        """${cmd_name}: convert a project from the old Fake OBS format (< 1.0.0)
        to the new format (>= 1.0.0).

        You need to be root to run this.

        ${cmd_usage}
         PROJECT is the name of the project
         RELEASE is the release number of the project

        ${cmd_option_list}
        """
        Utils.failIfUserIsNotRoot()
        effectiveName = Converter.convertProject(project, release, opts.new_name)
        msg = "Project '%s' correctly converted" % effectiveName
        print Utils.colorize(msg, "green")
        return self.do_check(subcmd, opts, effectiveName)

    @cmdln.option("-r", "--rsync",
                  help="rsync URL to do the update from")
    @cmdln.option("-o", "--original-project",
                  help="name of the project to do the update from")
    def do_update(self, subcmd, opts, project):
        """${cmd_name}: update a project using rsync

        If you don't specify RSYNC or ORIGINAL_PROJECT options,
        they will be taken from the 'project_info' file of the project.

        You need to be root to run this.

        ${cmd_usage}
        ${cmd_option_list}
        """
        Utils.failIfUserIsNotRoot()
        res = ProjectManager.updateProject(project, opts.rsync,
                                           opts.original_project)
        if res == 0:
            msg = "Project '%s' correctly updated" % project
        else:
            msg = "Errors happened whil updating '%s'" % project
        print Utils.colorize(msg, "green" if res == 0 else "red")
        return self.do_check(subcmd, opts, project)

    @cmdln.option("-s", "--symbolic", action="store_true",
                  help="make symbolic links instead of hard links")
    @cmdln.option("-n", "--dry-run", action="store_true",
                  help="don't link orphan RPMs, just list them")
    def do_findorphanrpms(self, subcmd, opts, project):
        """${cmd_name}: find RPMs which are in :full but not in repositories
        and hardlink them in repositories.
        This is automatically run after a grab.

        You need to be root to run this.

        ${cmd_usage}
        ${cmd_option_list}
        """
        Utils.failIfUserIsNotRoot()
        counter = 0
        for orphan in ProjectManager.findOrphanRpms(project, opts.symbolic,
                                                    opts.dry_run):
            print orphan
            counter += 1
        msg = "Found %d orphan RPMs in '%s'" % (counter, project)
        print Utils.colorize(msg, "green")

def main():
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


if __name__ == "__main__":
    main()
