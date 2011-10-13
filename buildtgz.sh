#!/bin/sh

cd src
python setup.py sdist
cd ..
echo "Compressed tar in src/dist/"
