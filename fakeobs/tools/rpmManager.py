import xml.dom.minidom
from subprocess import Popen, PIPE
from xml.dom.minidom import getDOMImplementation
import re
import shlex
HOST_IP = None



archHierarchyMap = {}
archHierarchyMap["i686"] = "i686:i586:i486:i386"
archHierarchyMap["i586"] = "i686:i586:i486:i386"
archHierarchyMap["i486"] = "i486:i386"
archHierarchyMap["i386"] = "i386"
archHierarchyMap["x86_64"] = "x86_64:i686:i586:i486:i386"
archHierarchyMap["sparc64v"] = "sparc64v:sparc64:sparcv9v:sparcv9:sparcv8:sparc"
archHierarchyMap["sparc64"] = "sparc64:sparcv9:sparcv8:sparc"
archHierarchyMap["sparcv9v"] = "sparcv9v:sparcv9:sparcv8:sparc"
archHierarchyMap["sparcv9"] = "sparcv9:sparcv8:sparc"
archHierarchyMap["sparcv8"] = "sparcv8:sparc"
archHierarchyMap["sparc"] = "sparc"

def isNonEmptyString(theString):
    return isinstance(theString, basestring) and len(theString) > 0

def getLocalRepoHost():
    cmd = "/sbin/ifconfig"
    global HOST_IP
    localhostIp = "127.0.0.1"
    if HOST_IP is None:
        try:
            res = Popen(cmd, stdout=PIPE).communicate()[0]

            for ip in re.findall(".*inet.*?:([\d.]*)[\s]+.*", res):
                if isNonEmptyString(ip) and ip != localhostIp:
                    HOST_IP = ip
                    break
        except:
            HOST_IP = localhostIp
    if HOST_IP is None:
        HOST_IP = localhostIp
    return "http://%s:8002" % HOST_IP

def getbuildInfo(repo, listRepository, dist, depfile, arch, projectName, packageName, repository, spec):
    if arch in archHierarchyMap.keys():
        longArch = archHierarchyMap[arch]
    else:
        longArch = arch
    #TODO: We need to rewrite the spec FIle!
#    buildDir = "/usr/lib/build"
#
#    command = '%s/substitutedeps --root %s --dist "%s" --archpath "%s" --configdir "%s" %s %s'
#    command = command % (buildDir,
#                         "/",
#                         dist,
#                         longArch,
#                         "/usr/lib/build/configs",
#                         spec,
#                         spec + ".spec")
#    print command
#    splittedCommand = shlex.split(str(command))
#    Popen(splittedCommand).communicate()[0]

    ouputFile = "ouputFile"
    errFile = "errFile"
    cmd = []
    cmd.append("/srv/fakeobs/tools/create-rpm-list-from-spec.sh")
    for repo in listRepository:
        cmd.append("--repository")
        cmd.append(repo)

    cmd.append("--dist")
    cmd.append(dist)

    cmd.append("--depfile")
    cmd.append(depfile)

    cmd.append("--spec")
    cmd.append(spec)

    cmd.append("--archpath")
    cmd.append(longArch)

    cmd.append("--stderr")
    cmd.append(errFile)

    cmd.append("--stdout")
    cmd.append(ouputFile)

    print " ".join(cmd)
    rpmlist = Popen(cmd).communicate()[0]
#    print rpmlist
    resultDep = []
    resultDepRPMid = []
    preinstallRes = None
    vminstallRes = None
    cbpreinstallRes = None
    cbinstallRes = None
    runscriptsRes = None
    distRes = None

    with open(ouputFile, 'r') as f:
        cout = 0
        for line in f:
            if line.startswith("preinstall"):
                preinstallRes = line
            elif line.startswith("vminstall"):
                  vminstallRes = line
            elif line.startswith("cbpreinstall"):
                cbpreinstallRes = line
            elif line.startswith("cbinstall"):
                cbinstallRes = line
            elif line.startswith("runscripts"):
                runscriptsRes = line
            elif line.startswith("dist"):
                distRes = line
            else:
                if cout % 2:
                    resultDepRPMid.append(line)
                else:
                    resultDep.append(line)

                cout += 1

    preinstallList = preinstallRes[len("preinstall: "):].split()
    impl = getDOMImplementation()

    indexbuildinfo = impl.createDocument(None, "buildinfo", None)
    indexbuildinfo.childNodes[0].setAttribute("project", projectName)
    indexbuildinfo.childNodes[0].setAttribute("repository", repository)
    indexbuildinfo.childNodes[0].setAttribute("package", packageName)
    indexbuildinfo.childNodes[0].setAttribute("downloadurl", repo)

    buildinfoArch = indexbuildinfo.createElement("arch")
    buildinfoArchText = indexbuildinfo.createTextNode(arch)

    buildinfoArch.appendChild(buildinfoArchText)
    indexbuildinfo.childNodes[0].appendChild(buildinfoArch)
#      <srcmd5>107502023cc9d9259034170728b3060e</srcmd5>
#      <verifymd5>107502023cc9d9259034170728b3060e</verifymd5>
#      <rev>1</rev>
#      <specfile>tzdata.spec</specfile>
#      <file>tzdata.spec</file>
#      <versrel>2011e-1</versrel>
#      <bcnt>1</bcnt>
#      <release>1.1</release>
#      <debuginfo>0</debuginfo>
#      <subpack>tzdata</subpack>
#      <subpack>tzdata-timed</subpack>
#      <subpack>tzdata-calendar</subpack>

    for i in range(len(resultDep)):
        bdepoelement = indexbuildinfo.createElement("bdep")
        dep = resultDep[i]
        rpmid = resultDepRPMid[i]
        print "____________________________________________________"
        print "i:", i
        print "dep:", dep
        print "rpmid:", rpmid

#autoconf http://128.224.218.236:8002/MeeGoTV:/oss.1.2.0.90/MeeGo_1.2_oss/noarch/autoconf-2.68-1.1.noarch.rpm
#rpmid: autoconf:autoconf-2.68-1.1 1340640610
        rpmFullName = rpmid.split()[1]
        rpmFullName = "test"
        bdepoelement.setAttribute("name", rpmFullName)
        bdepoelement.setAttribute("preinstall", rpmFullName)
        bdepoelement.setAttribute("vminstall", rpmFullName)
        bdepoelement.setAttribute("cbpreinstall", rpmFullName)
        bdepoelement.setAttribute("cbinstall", rpmFullName)
        bdepoelement.setAttribute("runscripts", rpmFullName)
        bdepoelement.setAttribute("epoch", rpmFullName)
        bdepoelement.setAttribute("version", rpmFullName)
        bdepoelement.setAttribute("release", rpmFullName)
        bdepoelement.setAttribute("arch", rpmFullName)
        bdepoelement.setAttribute("project", rpmFullName)
        bdepoelement.setAttribute("repository", rpmFullName)

        indexbuildinfo.childNodes[0].appendChild(bdepoelement)

    return indexbuildinfo.childNodes[0].toprettyxml()
