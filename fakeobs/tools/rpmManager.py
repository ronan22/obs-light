import xml.dom.minidom
from subprocess import Popen, PIPE
from xml.dom.minidom import getDOMImplementation
import re
import shlex
HOST_IP = None
import gitmer



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

def getbuildInfo(rev, srcmd5, specFile, listRepository, dist, depfile, arch, projectName, packageName, repository, spec, addPackages):
    if arch in archHierarchyMap.keys():
        longArch = archHierarchyMap[arch]
    else:
        longArch = arch

    #TODO: We need to rewrite the spec FIle!
    buildDir = "/usr/lib/build"

    command = '%s/substitutedeps --root %s --dist "%s" --archpath "%s" --configdir "%s" %s %s'
    command = command % (buildDir,
                         "/",
                         dist,
                         longArch,
                         "/usr/lib/build/configs",
                         spec,
                         spec + ".spec")

    splittedCommand = shlex.split(str(command))
    Popen(splittedCommand).communicate()[0]

    repo = getLocalRepoHost()
    ouputFile = "ouputFile"
    errFile = "errFile"
    cmd = []
    cmd.append("/srv/fakeobs/tools/create-rpm-list-from-spec.sh")
    for aRepo in listRepository:
        cmd.append("--repository")
        cmd.append(aRepo)

    cmd.append("--dist")
    cmd.append(dist)

    cmd.append("--depfile")
    cmd.append(depfile)

    cmd.append("--spec")
    cmd.append(spec + ".spec")

    cmd.append("--archpath")
    cmd.append(longArch)

    for p in addPackages:
        cmd.append("--addPackages")
        cmd.append(p)

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

    preinstallList = preinstallRes[len("preinstall:"):].split()
    vminstallList = vminstallRes[len("vminstall:"):].split()
    cbpreinstallList = cbpreinstallRes[len("cbpreinstall:"):].split()
    cbinstallList = cbinstallRes[len("cbinstall:"):].split()
    runscriptsList = runscriptsRes[len("runscripts:"):].split()

    impl = getDOMImplementation()

    indexbuildinfo = impl.createDocument(None, "buildinfo", None)
    indexbuildinfo.childNodes[0].setAttribute("project", projectName)
    indexbuildinfo.childNodes[0].setAttribute("repository", repository)
    indexbuildinfo.childNodes[0].setAttribute("package", packageName)
    indexbuildinfo.childNodes[0].setAttribute("downloadurl", repo)

    srcmd5 = srcmd5
    verifymd5 = srcmd5
    rev = rev
    specfile = specFile
    aFile = specFile
    #TODO:find version and release
    versrel = "1-1"
    bcnt = "1"
    #TODO:find version and release
    release = "1"
    debuginfo = "0"

    buildinfoArch = indexbuildinfo.createElement("arch")
    buildinfoArchText = indexbuildinfo.createTextNode(arch)
    buildinfoArch.appendChild(buildinfoArchText)
    indexbuildinfo.childNodes[0].appendChild(buildinfoArch)

    if srcmd5 is not None:
        buildinfoSrcmd5 = indexbuildinfo.createElement("srcmd5")
        buildinfoSrcmd5Text = indexbuildinfo.createTextNode(srcmd5)
        buildinfoSrcmd5.appendChild(buildinfoSrcmd5Text)
        indexbuildinfo.childNodes[0].appendChild(buildinfoSrcmd5)

    if verifymd5 is not None:
        buildinfoVerifymd5 = indexbuildinfo.createElement("verifymd5")
        buildinfoVerifymd5Text = indexbuildinfo.createTextNode(verifymd5)
        buildinfoVerifymd5.appendChild(buildinfoVerifymd5Text)
        indexbuildinfo.childNodes[0].appendChild(buildinfoVerifymd5)

    if rev is not None:
        buildinfoRev = indexbuildinfo.createElement("rev")
        buildinfoRevText = indexbuildinfo.createTextNode(rev)
        buildinfoRev.appendChild(buildinfoRevText)
        indexbuildinfo.childNodes[0].appendChild(buildinfoRev)

    if specfile is not None:
        buildinfoSpecfile = indexbuildinfo.createElement("specfile")
        buildinfoSpecText = indexbuildinfo.createTextNode(specfile)
        buildinfoSpecfile.appendChild(buildinfoSpecText)
        indexbuildinfo.childNodes[0].appendChild(buildinfoSpecfile)

    if aFile is not None:
        buildinfoFile = indexbuildinfo.createElement("file")
        buildinfoFileText = indexbuildinfo.createTextNode(aFile)
        buildinfoFile.appendChild(buildinfoFileText)
        indexbuildinfo.childNodes[0].appendChild(buildinfoFile)

    if versrel is not None:
        buildinfoVersrel = indexbuildinfo.createElement("versrel")
        buildinfoVersrelText = indexbuildinfo.createTextNode(versrel)
        buildinfoVersrel.appendChild(buildinfoVersrelText)
        indexbuildinfo.childNodes[0].appendChild(buildinfoVersrel)

    if bcnt is not None:
        buildinfoBcnt = indexbuildinfo.createElement("bcnt")
        buildinfoBcntText = indexbuildinfo.createTextNode(bcnt)
        buildinfoBcnt.appendChild(buildinfoBcntText)
        indexbuildinfo.childNodes[0].appendChild(buildinfoBcnt)

    if release is not None:
        buildinfoRelease = indexbuildinfo.createElement("release")
        buildinfoReleaseText = indexbuildinfo.createTextNode(release)
        buildinfoRelease.appendChild(buildinfoReleaseText)
        indexbuildinfo.childNodes[0].appendChild(buildinfoRelease)

    buildinfoDebuginfo = indexbuildinfo.createElement("debuginfo")
    buildinfoDebuginfoText = indexbuildinfo.createTextNode(debuginfo)
    buildinfoDebuginfo.appendChild(buildinfoDebuginfoText)
    indexbuildinfo.childNodes[0].appendChild(buildinfoDebuginfo)

    for i in range(len(resultDep)):
        bdepelement = indexbuildinfo.createElement("bdep")
        dep = resultDep[i]
        rpmid = resultDepRPMid[i]

#autoconf http://128.224.218.236:8002/MeeGoTV:/oss.1.2.0.90/MeeGo_1.2_oss/noarch/autoconf-2.68-1.1.noarch.rpm
#rpmid: autoconf:autoconf-2.68-1.1 1340640610
        rpmName, rpmUrl = dep.split()
        project, repository, rpmName, rpmEpoch, rpmVersion, rpmRelease, rpmArch = parseRpmUrl(repo, rpmUrl)

#        RpmName, rpmFullName = rpmid.split()[1].split(":")

        bdepelement.setAttribute("name", rpmName)

        if rpmName in preinstallList:
             bdepelement.setAttribute("preinstall", "1")
        if rpmName in vminstallList:
            bdepelement.setAttribute("vminstall", "1")
        if rpmName in cbpreinstallList:
            bdepelement.setAttribute("cbpreinstall", "1")
        if rpmName in cbinstallList:
            bdepelement.setAttribute("cbinstall", "1")

        if rpmEpoch:
            bdepelement.setAttribute("epoch", rpmEpoch)

        bdepelement.setAttribute("version", rpmVersion)
        bdepelement.setAttribute("release", rpmRelease)
        bdepelement.setAttribute("arch", rpmArch)

        bdepelement.setAttribute("project", project)
        bdepelement.setAttribute("repository", repository)

        indexbuildinfo.childNodes[0].appendChild(bdepelement)

    pathelement = indexbuildinfo.createElement("path")
    pathelement.setAttribute("project", project)
    pathelement.setAttribute("repository", repository)
    indexbuildinfo.childNodes[0].appendChild(pathelement)

    return indexbuildinfo.childNodes[0].toxml()
#    return indexbuildinfo.childNodes[0].toprettyxml()


def parseRpmUrl(repo, rpmUrl):
    url = rpmUrl[len(repo + "/"):]
    splitedUrl = url.split("/")
    rpmfullName = splitedUrl[-1]
    repository = splitedUrl[-3]
    project = "/".join(splitedUrl[:-3])

    rpmName, rpmEpoch, rpmVersion, rpmRelease, rpmArch = parseRpmFullName(rpmfullName)
    project = project.replace(":/", ":")
    return project, repository, rpmName, rpmEpoch, rpmVersion, rpmRelease, rpmArch

def parseRpmFullName(rpmfullName):
    rpmfullName = rpmfullName[:-len(".rpm")]
    rpmArch = rpmfullName[rpmfullName.rfind(".") + 1:]
    rpmfullName = rpmfullName[:rpmfullName.rfind(".")]

    rpmRelease = rpmfullName[rpmfullName.rfind("-") + 1:]
    rpmfullName = rpmfullName[:rpmfullName.rfind("-")]

    rpmEpochVersion = rpmfullName[rpmfullName.rfind("-") + 1:]
    rpmName = rpmfullName[:rpmfullName.rfind("-")]

    if ":" in rpmEpochVersion:
        rpmEpoch, rpmVersion = rpmEpochVersion.split(":")
    else:
        rpmEpoch, rpmVersion = None, rpmEpochVersion

    return rpmName, rpmEpoch, rpmVersion, rpmRelease, rpmArch


