@echo off
echo ========================================
echo RESTARTING DJANGO SERVER FOR TIMEZONE
echo ========================================
echo.
echo Timezone changed to: Asia/Kolkata (IST)
echo Server must be restarted for changes to take effect
echo.
echo Press Ctrl+C to stop the current server first
echo Then run this script to restart
echo.
echo ========================================
echo.

python manage.py runserver

pause
