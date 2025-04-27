#!/bin/bash

# Path to your router script
ROUTER_SCRIPT="RIP_daemon.py"

# Path to your config folder
CONFIG_FOLDER="figure_1"

# Check if router.py exists
if [ ! -f "$ROUTER_SCRIPT" ]; then
    echo "Error: $ROUTER_SCRIPT not found!"
    exit 1
fi

# Launch each router in a new terminal window
for config_file in "$CONFIG_FOLDER"/*.txt; do
    gnome-terminal -- bash -c "python3 $ROUTER_SCRIPT $config_file; exec bash"
done
