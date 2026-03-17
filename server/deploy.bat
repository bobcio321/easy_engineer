@echo off
echo === Easy Engineer — Prepare Deploy Package ===
echo.

set DEPLOY_DIR=%~dp0..\deploy
if exist "%DEPLOY_DIR%" rmdir /s /q "%DEPLOY_DIR%"
mkdir "%DEPLOY_DIR%"
mkdir "%DEPLOY_DIR%\server"
mkdir "%DEPLOY_DIR%\public"

:: Copy server files
copy "%~dp0server.js" "%DEPLOY_DIR%\server\"
copy "%~dp0sessionManager.js" "%DEPLOY_DIR%\server\"
copy "%~dp0wsHandler.js" "%DEPLOY_DIR%\server\"
copy "%~dp0package.json" "%DEPLOY_DIR%\server\"
copy "%~dp0package-lock.json" "%DEPLOY_DIR%\server\"
copy "%~dp0.env.example" "%DEPLOY_DIR%\server\"

:: Copy public (frontend)
xcopy "%~dp0..\public\*" "%DEPLOY_DIR%\public\" /s /e /q

:: Copy start scripts from templates
copy "%~dp0templates\start.bat" "%DEPLOY_DIR%\start.bat"
copy "%~dp0templates\start.sh" "%DEPLOY_DIR%\start.sh"

echo.
echo Done! Deploy package: %DEPLOY_DIR%
echo.
echo Contents:
echo   deploy\
echo     server\       - Node.js backend
echo     public\       - Web frontend
echo     start.bat     - Windows: double-click to run
echo     start.sh      - Linux: bash start.sh
echo.
echo To deploy:
echo   1. Copy the 'deploy' folder to your server
echo   2. Make sure Node.js is installed
echo   3. Run start.bat (Windows) or start.sh (Linux)
echo.
pause
