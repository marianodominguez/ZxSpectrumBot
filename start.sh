#!/bin/bash

nohup xvfb :99 > /dev/null 2>&1 &
python3 SpeccyBot.py
