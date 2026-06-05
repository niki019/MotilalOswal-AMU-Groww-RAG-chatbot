# Get absolute paths of current folder and virtual environment Python interpreter
$ProjectDir = Get-Location
$PythonPath = Join-Path $ProjectDir ".venv\Scripts\python.exe"
$ScriptPath = Join-Path $ProjectDir "cron_job.py"

# Verify files exist
if (-not (Test-Path $PythonPath)) {
    Write-Error "Python interpreter not found at $PythonPath. Please ensure the virtual environment is set up."
    Exit 1
}

if (-not (Test-Path $ScriptPath)) {
    Write-Error "Script not found at $ScriptPath."
    Exit 1
}

# Task parameters
$TaskName = "GrowwFAQIngestion"
$Time = "09:45" # Runs daily at 9:45 AM local time (IST)

# Build schtasks command arguments
$Command = "schtasks.exe"
$Args = @(
    "/create",
    "/tn", $TaskName,
    "/tr", "`"$PythonPath`" `"$ScriptPath`"",
    "/sc", "DAILY",
    "/st", $Time,
    "/f"
)

Write-Host "Registering scheduled task '$TaskName' to run at $Time daily..."
Write-Host "Command: $Command $($Args -join ' ')"

# Execute schtasks
& $Command $Args

if ($LASTEXITCODE -eq 0) {
    Write-Host "Task '$TaskName' registered successfully."
} else {
    Write-Error "Failed to register task. Please check permissions."
}
