
import sys
import subprocess
import xml.dom.minidom

retries = 5
wget_options = ["--no-check-certificate", "-nd", "-nH", "-nv", "-cr"]

index = sys.argv[1]
api_url = sys.argv[2]
project = sys.argv[3]

doc1 = xml.dom.minidom.parse(index)
doc1entries = []
exit_status = 0

for x in doc1.getElementsByTagName("directory"):
    rev1 = x.attributes["rev"].value
    pkg = x.attributes["name"].value

for x in doc1.getElementsByTagName("entry"):
    file_name = x.attributes["name"].value
    file_md5 = x.attributes["md5"].value
    url = "%s/source/%s/%s/%s" % (api_url, project, pkg, file_name)
    wget_args = ["wget"] + wget_options + [url]
    for i in range(retries):
        retcode = subprocess.call(wget_args)
        if retcode == 0:
            md5_args = ["md5sum", file_name]
            real_md5 = subprocess.Popen(md5_args, stdout=subprocess.PIPE).communicate()[0][:32]
            if real_md5 != file_md5:
                retcode = 1
                msg = "Error in downloaded file (md5 %s should be %s)"
                print msg % (real_md5, file_md5)
                subprocess.call(["rm", file_name])
                continue
            break
    if retcode != 0:
        msg = "Failed to retrieve file '%s' of package '%s'" % (file_name, pkg)
        print "\\[\\e[31;1m\\]%s\\[\\e[0m\\]" % msg
        exit_status = 1

sys.exit(exit_status)
