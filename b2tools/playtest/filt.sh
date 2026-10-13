#!/bin/zsh
# run a python tool with the venv, hiding DeSmuME's boot chatter
cd ~/Documents/GitHub/HoennB2/work/agents/playthrough
../../../.venv/bin/python -u "$@" 2>&1 | grep --line-buffered -v "^BackupDevice\|^Already\|^WIFI\|^Autodetect\|^$\|^ROM\|^Slot\|^Micro\|^DeSmuME\|^SoftRas\|^MC9: Unverified"
