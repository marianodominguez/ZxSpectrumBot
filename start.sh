#!/bin/bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

#avoid to get all twitters, update this to a real ID
echo '1567969714969911296' > /home/zxspectrum/bot/sinceFile.txt
nohup Xvfb :99 > /dev/null 2>&1 &
python3 SpeccyBot.py
