# Path to your router script
$ROUTER_SCRIPT = "RIP_daemon.py"

# Path to your config folder
$CONFIG_FOLDER = "figure_1"

# Check if the router script exists
if (-Not (Test-Path $ROUTER_SCRIPT)) {
    Write-Host "Error: $ROUTER_SCRIPT not found!"
    exit 1
}

# Launch each router in a new terminal window (Command Prompt)
Get-ChildItem "$CONFIG_FOLDER\*.txt" | ForEach-Object {
    $configFile = $_.FullName
    Start-Process powershell -ArgumentList "-Command", "python $ROUTER_SCRIPT '$configFile'"
}