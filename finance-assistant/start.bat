@echo off
echo Checking for processes on required ports...

REM Kill any processes using our ports
for %%p in (8000 8001 6002 6003 6004 6005 6006) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%%p" ^| findstr "LISTENING"') do (
        echo Killing process on port %%p (PID: %%a)
        taskkill /PID %%a /F > nul 2>&1
    )
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call .\venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Check environment
echo Checking Python environment...
python check_env.py
if errorlevel 1 (
    echo Environment check failed. Please fix the issues above.
    pause
    exit /b 1
)

REM Start the services
echo Starting services...
python run_services.py

pause 