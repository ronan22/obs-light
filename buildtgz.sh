#!/bin/sh

rm src/dist/obslight*.tar.gz
cd src
python setup.py sdist
cd ..
echo "Compressed tar in src/dist/"

