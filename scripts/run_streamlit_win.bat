@echo off
REM Windows batch script to run Streamlit app and handle port conflicts

where streamlit >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Streamlit is not installed. Please run: pip install -r config/requirements.txt
    exit /b 1
)

set PORT=8501
:find_port
netstat -ano | findstr :%PORT% >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Port %PORT% is in use, trying next port...
    set /a PORT+=1
    goto find_port
)

echo Cleaning up any existing Streamlit processes...
taskkill /IM streamlit.exe /F >nul 2>nul

REM Wait a moment for processes to clean up
ping 127.0.0.1 -n 3 >nul

echo Starting Streamlit on port %PORT%
streamlit run apps/streamlit_app.py --server.port %PORT% --server.address 0.0.0.0 