@echo off
echo Setting up daily Aare temperature email task at 18:00...
echo.

schtasks /create /tn "AareTempEmail" /tr "node \"%~dp0index.js\"" /sc daily /st 18:00 /f

if %errorlevel% equ 0 (
    echo.
    echo Task created successfully! The email will be sent daily at 18:00.
    echo.
    echo To remove the task later:  schtasks /delete /tn "AareTempEmail" /f
    echo To run it now for testing:  schtasks /run /tn "AareTempEmail"
) else (
    echo.
    echo Failed to create task. Try running this script as Administrator.
)

pause
