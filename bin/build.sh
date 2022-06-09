#!/bin/bash
py -m pip install --upgrade pygame pyinstaller pillow zstd
py -m PyInstaller -Fwn tinyrpg src/demo.py $(py bin/build_datas.py)
mv dist/tinyrpg.exe dist/tinyrpg-$(cat VERSION).exe
