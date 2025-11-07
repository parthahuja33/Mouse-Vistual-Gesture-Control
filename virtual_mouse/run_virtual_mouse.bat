@echo off
REM Virtual Mouse Launcher Script for Windows
title Virtual Mouse

echo ========================================
echo   Virtual Mouse - Gesture Control
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [WARN] Virtual environment not found. Using system Python.
    echo [INFO] To create one, run: python -m venv venv
    echo.
)

REM Parse command line arguments
set ARGS=
set SHOW_DEBUG=0

:parse_args
if "%~1"=="" goto run
if /i "%~1"=="--debug" set SHOW_DEBUG=1
if /i "%~1"=="--show-debug" set SHOW_DEBUG=1
if /i "%~1"=="-d" set SHOW_DEBUG=1
set ARGS=%ARGS% %1
shift
goto parse_args

:run
echo [INFO] Starting Virtual Mouse...
echo [INFO] - Press ENTER when prompted to activate gesture control
echo [INFO] - Press 'q' in debug window to exit
echo [INFO] - Press Ctrl+C here to force stop
echo.

REM Run the application
if %SHOW_DEBUG%==1 (
    python -m src.main --show-debug --auto-start %ARGS%
) else (
    python -m src.main --auto-start %ARGS%
)

REM Check exit code
if errorlevel 1 (
    echo.
    echo [ERROR] Application exited with an error.
    echo.
    pause
    exit /b 1
)

echo.
echo [INFO] Virtual Mouse stopped.
echo.
pause

