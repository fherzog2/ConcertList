@echo off
setlocal

if not exist main.pyw (
    echo main.pyw is missing
    exit /b 0
)

pip install PyInstaller

for %%F in ("%cd%") do set CURRENT_DIR_NAME=%%~nxF
set INSTALL_DIR=%userprofile%\pyinstaller_%CURRENT_DIR_NAME%
if not exist %INSTALL_DIR% mkdir %INSTALL_DIR%
cd /d %INSTALL_DIR%
python -m PyInstaller --name %CURRENT_DIR_NAME% "%~dp0main.pyw"