#
# Copyright 2011-2012, Intel Inc.
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
'''
Created on 30 May 2011

@author: Ronan Le Martret
'''
import rpm
import zypp
import obslight_zypp

from zypppkgmgr import Zypp as _Zypp
from mic.utils.errors import CreatorError

class Zypp(_Zypp):
    name = 'zypp-obslight'
    def __init__(self, target_arch, instroot, cachedir):
        _Zypp.__init__(self, target_arch, instroot, cachedir)
        self.listCmp = ["<=", ">=", "=", "<", ">"]

        self.dicoCmp = {}
        self.dicoCmp["<="] = self.cmpLE
        self.dicoCmp[">="] = self.cmpGE
        self.dicoCmp["="] = self.cmpEQ
        self.dicoCmp["<"] = self.cmpLT
        self.dicoCmp[">"] = self.cmpGT

    def cmpGT(self, val):
        return (val == 1)

    def cmpEQ(self, val):
        return (val == 0)

    def cmpLT(self, val):
        return (val == -1)

    def cmpGE(self, val):
        return (val == 1) or (val == 0)

    def cmpLE(self, val):
        return (val == -1) or (val == 0)

    def testIfInstall(self, name):
        q = zypp.PoolQuery()
        q.addKind(zypp.ResKind.package)

        q.setMatchExact()
        q.addAttribute(zypp.SolvAttr.name, name)

        resQuery = q.queryResults(self.Z.pool())

        if len(resQuery) == 0:
            return False

        res = []
        for item in resQuery:
            if (item.status().wasInstalled() or item.status().isToBeInstalled ()):
                return True

        return False

    def selectPackage(self, name, arch=None, version=None, release=None, epoch=None, rel=None):
        """Select a given package or package pattern, can be specified
        with name.arch or name* or *name
        """

        if not self.Z:
            self.__initialize_zypp()

        def markPoolItem(obs, pi):

            if obs == None:
#                print "set to be install", pi.name(), "arch", pi.arch(), "epoch", pi.edition().epoch(), "version", pi.edition().version(), "release", pi.edition().release()
                pi.status().setToBeInstalled (zypp.ResStatus.USER)
            else:
#                print "set to be install", obs.name(), "arch", obs.arch(), "epoch", obs.edition().epoch(), "version", obs.edition().version(), "release", obs.edition().release()
                obs.status().setToBeInstalled (zypp.ResStatus.USER)

        def cmpEVR(ed1, ed2):
            (e1, v1, r1) = map(str, [ed1.epoch(), ed1.version(), ed1.release()])
            (e2, v2, r2) = map(str, [ed2.epoch(), ed2.version(), ed2.release()])
            return rpm.labelCompare((e1, v1, r1), (e2, v2, r2))

#        print "try to install ", name, "arch", arch, "version", version, "release", release, "epoch", epoch, "rel", rel

        found = False


        q = zypp.PoolQuery()
        q.addKind(zypp.ResKind.package)

        q.setMatchExact()
        q.addAttribute(zypp.SolvAttr.name, name)

        resQuery = q.queryResults(self.Z.pool())

        tmpRes = sorted(
                        resQuery,
                        cmp=lambda x, y: cmpEVR(x.edition(), y.edition()),
                        reverse=True)

        if len(tmpRes) == 0:
#            print "no package"
            return 1

        isInstalled = False

        if (version != None) and (release != None):
            if epoch != None:
                edition = zypp.Edition(version, release, epoch)
            else:
                edition = zypp.Edition(version, release)
        else:
            edition = None

        res = []
        for item in tmpRes:
#            print "\tfind ", item.name(), "arch", item.arch(), "epoch", item.edition().epoch(), "version", item.edition().version(), "release", item.edition().release(),
            isInstall = item.status().wasInstalled() or item.status().isToBeInstalled ()
#            print isInstall
            if arch != None:
                isArch = (str(item.arch()) == arch)
            else:
                isArch = True

            if (rel != None) and (edition != None) :
                if release == "":
                    tmpEdition = zypp.Edition(item.edition().version(), "", item.edition().epoch())
                    isRel = self.dicoCmp[rel](tmpEdition.compare(edition))
                else:
                    isRel = self.dicoCmp[rel](item.edition().compare(edition))
            else:
                isRel = True

#            print "\tisInstall", isInstall, "isArch", isArch, "isRel", isRel

            if isInstall and isArch and isRel:
#                print "already install item.name()", item.name(), "was/tobeInstalled()", isInstall
                return 0

            elif isInstall and not (isArch and isRel):
#                print "to uninstall item.name()", item.name(), "was/tobeInstalled()", isInstall
                item.status().isToBeUninstalled()
            elif isArch and isRel:
                res.append(item)

        for item in res:
            found = True
            obspkg = self.whatObsolete(item.name())
            markPoolItem(obspkg, item)
            pkgCapa = self._getRequirePackage(item)

#            print "find requires"
            for name in pkgCapa.keys():
                if pkgCapa[name] == None:
#                    print "\t", name
                    pass
                else:
                    pkg = pkgCapa[name]
                    epoch = pkg["epoch"]
                    version = pkg["version"]
                    release = pkg["release"]
                    rel = pkg["rel"]
#                    print "\t", name, "epoch", epoch, "version", version, "release", release

            noPkgList = []

            for name in pkgCapa.keys():
                if pkgCapa[name] == None:
                    res = self.selectPackage(name)
                else:
                    pkg = pkgCapa[name]
                    epoch = pkg["epoch"]
                    version = pkg["version"]
                    release = pkg["release"]
                    rel = pkg["rel"]
                    res = self.selectPackage(name, None, version, release, epoch, rel)

                if res != 0:
                    noPkgList.append(name)

#            print "This is not package"
            for name in noPkgList:
                if pkgCapa[name] == None:
                    provideRes = self._whoProvide(name)
#                    print "\t", name
                else:
                    pkg = pkgCapa[name]
                    epoch = pkg["epoch"]
                    version = pkg["version"]
                    release = pkg["release"]
                    rel = pkg["rel"]
#                    provideRes = self._whoProvide(name + " " + rel + " " + str(zypp.Edition(version, release, epoch)))
                    provideRes = self._whoProvide(name , zypp.Edition(version, release, epoch), rel)
#                    print "\t", name, "epoch", epoch, "version", version, "release", release, "rel", rel

#                print "\t is provide by:"
                res = set()
                for j in provideRes:
                    res.add(j.name())
#                print "\t\t require 1"
#                for i in res:
#                    print "\t\t\t", i

                if len(res) > 1:
                    for item in provideRes:
                        tmpPkgCapa = self._getRequirePackage(item)
#                        print "\t\t\tfor item.name", item.name()
                        for name in tmpPkgCapa.keys():
#                            print "\t\t\t\t", name, name in res, item.name() in res
                            if name in res:
                                if item.name() in res:
#                                    print "\t\t\t\t Remove:", item.name()
                                    res.remove(item.name())
#                                    print "\t\t\t\t res:", res

                if len(res) > 1:
                    for r in res:
                        if self.testIfInstall(r):
                            return 0

#                print "\t\t require 2"
#                for i in res:
#                    print "\t\t\t", i

                if len(res) == 0:
                    raise CreatorError("No package to provide : %s" % (name))
                elif len(res) > 1:
                    raise CreatorError("More than 1 package (" + ",".join(res) + ") to provide: %s" % (name))
                else:
                    self.selectPackage(res.pop())
#                print "__________________________________________________________"
            return 0

        if not found:
           raise CreatorError("Unable to find package: %s" % (name))

    def _whoProvide(self, service, edition=None, rel=None):
        service = service.strip().rstrip()
#        print "+++++service", service, "rel", edition, "rel", rel
        q = obslight_zypp.PoolQuery()
        q.addKind(zypp.ResKind.package)
        q.setMatchExact()
        q.addAttribute(zypp.SolvAttr.name, service)
        q.addAttribute(zypp.SolvAttr.provides, service)
#        q.addAttribute(zypp.SolvAttr.name, '')
#        if (edition != None) and (rel != None) :
#            q.setEdition2(edition, rel)

        tmpRes = q.queryResults(self.Z.pool())

        if (edition != None) and (rel != None) :
            tmpRes2 = []
            for i in tmpRes:
                for k in self._getprovidesPackage(i):
                    res = None
                    for c in self.listCmp:
                        if c in k:
                            tmpService, tmpEdition = i.split(c)
                            tmpService = tmpService.strip().rstrip()
                            if service == tmpService:
                                tmpEdition2 = zypp.Edition(tmpEdition.strip().rstrip())

                                if self.dicoCmp[rel](tmpEdition.compare(edition)):
                                    res = k
                                    break
                    if res != None:
                        tmpRes2.append(res)
                        break
        else:
            return tmpRes

#        print "service:", service,
#        if  edition != None:
#            print " (epoch", edition.epoch(), "version", edition.version(), "release", edition.release(), ") rel", rel
#        else:
#            print
#        for i in tmpRes: print "\t" + i.name()
#        print
#        print "(edition != None) and (rel != None)", (edition != None) and (rel != None)

#        if (edition != None) and (rel != None) :
#            res = []
#            for i in tmpRes:
##                print "\t\t", i.name(), " (epoch", i.edition().epoch(), "version", i.edition().version(), "release", i.edition().release(), ")"
##                print "edition.release() == ", i.edition().release() == ""
#                if edition.release() == "":
#                    tmpEdition = zypp.Edition(i.edition().version(), rel, i.edition().epoch())
#                else:
#                    tmpEdition = i.edition()
##                print "self.dicoCmp[rel](tmpEdition.compare(edition))", self.dicoCmp[rel](tmpEdition.compare(edition))
#                if self.dicoCmp[rel](tmpEdition.compare(edition)):
#                    res.append(i)
#
#            return res
#        else:

        return tmpRes

    def _getRequirePackage(self, item):
        capa = item.requires()
        tmpCapa = obslight_zypp.Capabilities()
        res = tmpCapa.getList(capa)
        listRequire = _splitCapNames(res)
        result = {}

        for i in listRequire:
            service = None
            for c in self.listCmp:
                if c in i:
                    service, edition = i.split(c)
                    tmpEdition = zypp.Edition(edition.strip().rstrip())
                    pkg = {}
                    pkg["epoch"] = tmpEdition.epoch()
                    pkg["version"] = tmpEdition.version()
                    pkg["release"] = tmpEdition.release()
                    pkg["rel"] = c
                    result[service.strip().rstrip()] = pkg
                    break

            if service == None:
                result[i] = None

        return result

    def _getprovidesPackage(self, item):
        capa = item.provides()
        tmpCapa = obslight_zypp.Capabilities()
        res = tmpCapa.getList(capa)
        listRequire = _splitCapNames(res)
        result = {}

        for i in listRequire:
            service = None
            for c in self.listCmp:
                if c in i:
                    service, edition = i.split(c)
                    tmpEdition = zypp.Edition(edition.strip().rstrip())
                    pkg = {}
                    pkg["epoch"] = tmpEdition.epoch()
                    pkg["version"] = tmpEdition.version()
                    pkg["release"] = tmpEdition.release()
                    pkg["rel"] = c
                    result[service.strip().rstrip()] = pkg
                    break

            if service == None:
                result[i] = None

        return result


def _splitCapNames(capName):
    res = []
#    print capName
    capName = capName.strip(";")
#    for i in capName.split(";"):
#        print i
    return capName.split(";")
#    while(len(capName) > 0):
#        
#        capName = capName.strip(":")
#        splitIndex = capName.find(":")
#        print "__________________________________________"
#        if splitIndex != -1:
#            subIndex = capName.find("(")
#            print "capName", capName
#            print "splitIndex : ", splitIndex
#            print "subIndex ( ", subIndex
#
#            if (subIndex != -1) and (subIndex < splitIndex):
#                splitIndex = capName.find(")") + 1
#
#
#            subIndex = capName.find(":", splitIndex)
#            if splitIndex != subIndex:
#                splitIndex = subIndex
#
#            tmp = capName[:splitIndex ]
#            print "tmp", tmp
#            res.append(tmp)
#            capName = capName[splitIndex :]
#        else:
#            res.append(capName)
#            capName = ""
#            break
#    return res

#    def testPkgs(self, package_objects):
#        if not self.ts:
#            self.__initialize_transaction()
#
#        # Set filters
#        probfilter = 0
#        for flag in self.probFilterFlags:
#            probfilter |= flag
#        self.ts.setProbFilter(probfilter)
#        self.ts_pre.setProbFilter(probfilter)
#
#        localpkgs = self.localpkgs.keys()
#        for po in package_objects:
#            pkgname = po.name()
#            if pkgname in localpkgs:
#                rpmpath = self.localpkgs[pkgname]
#            else:
#                rpmpath = self.getLocalPkgPath(po)
#
#            if not os.path.exists(rpmpath):
#                # Maybe it is a local repo
#                baseurl = str(po.repoInfo().baseUrls()[0])
#                baseurl = baseurl.strip()
#
#                location = zypp.asKindPackage(po).location()
#                location = str(location.filename())
#
#                if baseurl.startswith("file:/"):
#                    rpmpath = baseurl[5:] + "/%s" % (location)
#
#            if not os.path.exists(rpmpath):
#                raise RpmError("Error: %s doesn't exist" % rpmpath)
#
#            h = rpmmisc.readRpmHeader(self.ts, rpmpath)
#
#            if pkgname in self.pre_pkgs:
#                msger.verbose("pre-install package added: %s" % pkgname)
#                self.ts_pre.addInstall(h, rpmpath, 'u')
#
#            self.ts.addInstall(h, rpmpath, 'u')
#        unresolved_dependencies = self.ts.check()
#        import sys
#        if not unresolved_dependencies:
#            if self.pre_pkgs:
#                self.preinstallPkgs()
#            sys.stderr.flush()
#            self.ts.order()
#            cb = rpmmisc.RPMInstallCallback(self.ts)
#            installlogfile = "%s/__catched_stderr.buf" % (self.instroot)
#            sys.stderr.flush()
#            # start to catch stderr output from librpm
#            msger.enable_logstderr(installlogfile)
#            sys.stderr.flush()
#            sys.stderr.flush()
#            errors = self.ts.run(cb.callback, '')
#            sys.stderr.flush()
#            # stop catch
#            msger.disable_logstderr()
#            self.ts.closeDB()
#            self.ts = None
#            if errors is not None:
#                if len(errors) == 0:
#                    msger.warning('scriptlet or other non-fatal errors occurred '
#                                  'during transaction.')
#
#                else:
#                    for e in errors:
#                        msger.warning(e[0])
#                    raise RepoError('Could not run transaction.')
#
#        else:
#            for pkg, need, needflags, sense, key in unresolved_dependencies:
#                package = '-'.join(pkg)
#
#                if needflags == rpm.RPMSENSE_LESS:
#                    deppkg = ' < '.join(need)
#                elif needflags == rpm.RPMSENSE_EQUAL:
#                    deppkg = ' = '.join(need)
#                elif needflags == rpm.RPMSENSE_GREATER:
#                    deppkg = ' > '.join(need)
#                else:
#                    deppkg = '-'.join(need)
#
#                if sense == rpm.RPMDEP_SENSE_REQUIRES:
#                    msger.warning("[%s] Requires [%s], which is not provided" \
#                                  % (package, deppkg))
#
#                elif sense == rpm.RPMDEP_SENSE_CONFLICTS:
#                    msger.warning("[%s] Conflicts with [%s]" % (package, deppkg))
#
#            raise RepoError("Unresolved dependencies, transaction failed.")
















