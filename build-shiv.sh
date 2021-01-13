#!/usr/bin/env bash

cd $(dirname $0)
pwd

if [ ! -d "dist" ];then
  mkdir dist
fi

# pip install -r <(pip freeze) --target .pkg/
cp -r .venv/lib .pkg
cp -r main.py README.md transport .pkg
shiv --site-packages .pkg --compressed -p '/usr/bin/env python3' -o dist/transport.pyz -e transport.cli:main
rm -r .pkg