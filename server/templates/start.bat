@echo off
cd /d "%~dp0server"
if not exist node_modules (
    echo Installing dependencies...
    npm install --production
)
echo Starting Easy Engineer server...
node server.js
pause
