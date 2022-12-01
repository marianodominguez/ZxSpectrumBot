#!/bin/bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

#avoid to get all twitters, update this to a real ID
#echo '1568012337696874497' > /home/zxspectrum/bot/sinceFile.txt

touch  /home/zxspectrum/.fuserc
echo '109429915290829699' > /home/zxspectrum/bot/sinceFile.txt
nohup Xvfb :99 > /dev/null 2>&1 &
python3 SpeccyBot.py
