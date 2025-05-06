# Kill all python processes running RIP_daemon.py
Write-Host "Killing all RIP_daemon.py processes..."

# Get all python processes that include RIP_daemon.py in the command line
Get-CimInstance Win32_Process | Where-Object {
    $_.Name -like "python*" -and $_.CommandLine -match "RIP_daemon.py"
} | ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force
}

Write-Host "All RIP_daemon.py processes killed."