#!/usr/bin/python

import sys
import xml.dom.minidom

distributions_file = sys.argv[1]
project_name = sys.argv[2]

doc1 = xml.dom.minidom.parse(distributions_file)

project_id = "fakeobs-%s" % project_name.replace(":", "-").lower()
node_to_remove = None

for distrib in doc1.getElementsByTagName("distribution"):
    if distrib.attributes["id"].value == project_id:
        node_to_remove = distrib
        break

if node_to_remove is not None:
    doc1.firstChild.removeChild(distrib)
    with open(distributions_file, "w+") as output_file:
        doc1.writexml(output_file, encoding="UTF-8")
    msg = "  \\[\\e[32;1m\\]Distribution '%s' removed from %s\\[\\e[0m\\]"
else:
    msg = "  \\[\\e[32;1m\\]Distribution '%s' not found in %s\\[\\e[0m\\]"

print msg % (project_id, distributions_file)
