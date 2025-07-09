@echo off
setlocal EnableDelayedExpansion

rem Detect available Python interpreter
set "PYTHON="
for %%P in (python python3 py) do (
    where %%P >nul 2>&1 && (
        set "PYTHON=%%P"
        goto :found_python
    )
)
echo Python interpreter not found.
exit /b 1
:found_python

rem Use provided port or default to 5000
if not defined PORT set PORT=5000

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

rem Terminate any process using the chosen port
for /f "tokens=5" %%P in ('netstat -ano ^| findstr :%PORT%') do (
    taskkill /F /PID %%P >nul 2>&1
)

rem Launch the Flask server
cd app
%PYTHON% main.py > ..\flask.log 2>&1
cd ..

endlocal
