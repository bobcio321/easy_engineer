@echo off
echo Building EasyEngineer.exe...
pip install pyinstaller websockets
pyinstaller --onefile --noconsole --name EasyEngineer host.py
echo.
echo Done! Executable: dist\EasyEngineer.exe
pause
