# Stop any existing Python processes using our ports
$ports = @(8000, 8001, 6002, 6003, 6004, 6005, 6006)
foreach ($port in $ports) {
    $processId = netstat -ano | findstr ":$port" | findstr "LISTENING"
    if ($processId) {
        $pid = $processId.Split()[-1]
        taskkill /PID $pid /F
        Write-Host "Killed process on port $port"
    }
}

# Create and activate virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate virtual environment
.\venv\Scripts\Activate

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs"
}

# Start the services
Write-Host "Starting services..."
python run_services.py 