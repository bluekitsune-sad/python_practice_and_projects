@echo off
cd /d "%~dp0"
echo ============================================
echo   HRMS - starting server...
echo   Open http://127.0.0.1:5000 in your browser
echo   Close this window when you are done.
echo ============================================
echo.
python app.py
pause
