@echo off
setlocal

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

rem Backup memory directory
for /f %%t in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TS=%%t
set BACKUP_DIR=memory_backup\%TS%
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
if exist memory (
    xcopy memory "%BACKUP_DIR%" /E /I /Y >nul
)

rem Update repository
git pull
pip install -r requirements.txt

rem Restart the Flask server
cd app
python main.py > ..\flask.log 2>&1
cd ..

endlocal
