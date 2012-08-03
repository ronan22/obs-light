import sys
import os
import gitmer

repos_lst_file = sys.argv[1]
mappingscache_xml_file = sys.argv[2]

f = open(repos_lst_file, "r")
repos = []
for x in f.readlines():
    x = x.strip('\r')
    x = x.strip('\n')
    repos.append(x)
f.close()

if os.path.isfile(mappingscache_xml_file):
    mappings = gitmer.generate_mappings(repos, mappingscache_xml_file)
else:
    mappings = gitmer.generate_mappings(repos)

f = open(mappingscache_xml_file, "w+")

f.write(mappings)
f.close()
