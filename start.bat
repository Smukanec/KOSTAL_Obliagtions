@echo off
setlocal

rem Ensure admin password is provided
if not defined ADMIN_PASS (
    echo ADMIN_PASS not defined – set it before running
    exit /b 1
)

rem Navigate to project root
cd /d "%~dp0.."

rem Activate virtual environment if present
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)

rem Terminate any process using port 5000
for /f "tokens=5" %%P in ('netstat -ano ^| findstr :5000') do (
    taskkill /F /PID %%P >nul 2>&1
)

rem Launch the Flask server
cd app
python main.py > ..\flask.log 2>&1
cd ..

endlocal
