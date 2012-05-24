#!/usr/bin/python

import sys
import xml.dom.minidom

fakeobs_link_name = "fakeobs"
distributions_file = sys.argv[1]
project_name = sys.argv[2]
repository = sys.argv[3] # aka "target"

doc1 = xml.dom.minidom.parse(distributions_file)

def append_text_element(parent, tag, text):
    node = doc1.createElement(tag)
    node.appendChild(doc1.createTextNode(text))
    parent.appendChild(node)

project_id = project_name.replace(":", "-").lower()
project_repo_name = project_name.replace(":", "_")
project_cleaned_name = project_name.replace(":", " ")

new_distrib = doc1.createElement("distribution")

new_distrib.setAttribute("vendor", "fakeobs")
new_distrib.setAttribute("version", "Testing")
new_distrib.setAttribute("id", "fakeobs-%s" % project_id)

append_text_element(new_distrib, "name", project_cleaned_name)
append_text_element(new_distrib, "project", "%s:%s" % (fakeobs_link_name, project_name))
append_text_element(new_distrib, "reponame", project_repo_name)
append_text_element(new_distrib, "repository", repository)
append_text_element(new_distrib, "link", "https://build.opensuse.org/")

doc1.firstChild.appendChild(new_distrib)

doc1.toprettyxml(indent=" ", encoding="UTF-8")
with open(distributions_file, "w+") as output_file:
#    doc1.writexml(output_file, indent=" ", addindent=" ", newl="\n", encoding="UTF-8")
    doc1.writexml(output_file, encoding="UTF-8")
