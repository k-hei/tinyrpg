#!/bin/bash
py -m pip install -r requirements.txt
py -m PyInstaller -Fwn tinyrpg src/demo.py $(py bin/build_datas.py)
mv dist/tinyrpg.exe dist/tinyrpg-$(cat VERSION).exe
