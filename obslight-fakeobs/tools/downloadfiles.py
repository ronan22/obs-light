
import sys
import subprocess
import xml.dom.minidom
from urllib import quote

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
    url_path = quote("source/%s/%s/%s" % (project, pkg, file_name))
    url = "%s/%s" % (api_url, url_path)
    print "URL: %s" % url
    wget_args = ["wget"] + wget_options + [url]
    print "wget args: ", wget_args
    for i in range(retries):
        retcode = subprocess.call(wget_args)
        if retcode == 0:
            md5_args = ["md5sum", file_name]
            real_md5 = subprocess.Popen(md5_args, stdout=subprocess.PIPE).communicate()[0][:32]
            if real_md5 != file_md5:
                retcode = 1
                msg = "Error in downloaded file (md5 %s should be %s)"
                print msg % (real_md5, file_md5)
                subprocess.call(["rm", "-f", file_name])
                continue
            break
    if retcode != 0:
        msg = "Failed to retrieve file '%s' of package '%s'" % (file_name, pkg)
        print "\033[31;1m%s\033[0m" % msg
        exit_status = 1

sys.exit(exit_status)
