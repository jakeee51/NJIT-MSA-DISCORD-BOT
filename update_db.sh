#!/bin/sh
pwd
cd /home/jake/MSA-Bot
rm -f loot.txt
/usr/bin/python3 verify.py && /usr/bin/python3 put.py