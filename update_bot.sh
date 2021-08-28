#!/bin/sh
pwd
git fetch origin
git pull origin main
sleep 2
systemctl restart botd
