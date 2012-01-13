#!/bin/sh

rm src/dist/obslight*.tar.gz
cd src
python setup.py sdist
echo "Compressed tar in src/dist/"

