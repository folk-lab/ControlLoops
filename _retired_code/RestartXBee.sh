#!/bin/sh

ps aux | grep ControlLoopXBee
if [ $? -eq 0 ]; then
  echo "Process is running."
else
  echo "Process is not running."
fi
