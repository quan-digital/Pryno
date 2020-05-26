#!/usr/bin/env bash
while true;
do
PID=`cat pyno.pid`

if ! ps -p $PID > /dev/null
then
  rm pyno.pid
  python3 util/megamail.py
  python3 main.py & echo $! >>pyno.pid
fi
sleep 3; 
done