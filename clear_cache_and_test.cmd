@echo off
echo ========================================
echo Clearing Python Cache and Testing
echo ========================================
echo.

echo Step 1: Clearing Python bytecode cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
echo Done!
echo.

echo Step 2: Deleting .pyc files...
del /s /q *.pyc 2>nul
echo Done!
echo.

echo Step 3: Instructions to test:
echo ========================================
echo 1. Stop your Django server (Ctrl+C)
echo 2. Start it again: python manage.py runserver
echo 3. Open browser in INCOGNITO/PRIVATE mode
echo 4. Go to: http://localhost:8000/order-tag/
echo 5. Fill the form and submit
echo 6. You should see Rs 1 now!
echo ========================================
echo.
pause
