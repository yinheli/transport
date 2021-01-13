#!/bin/bash
set -e

cd $(dirname $0)
pwd

rm -rf dist
pyinstaller --clean --onefile --name transport --add-data transport/template:template ./main.py
