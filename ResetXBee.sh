#!/bin/sh

while :
do
  python3 ControlXBeeLoop.py
  last_pid=$!
  sleep 10m
  pkill $last_pid
  wait $last_pid
done
