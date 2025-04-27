#!/bin/bash

# Kill all python processes running RIP_daemon.py
# Looks specifically for 'RIP_daemon.py' in the command

echo "Killing all RIP_daemon.py processes..."

ps aux | grep "[R]IP_daemon.py" | awk '{print $2}' | xargs -r kill -9

echo "All RIP_daemon.py processes killed."
