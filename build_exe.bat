@echo off
REM ============================================================================
REM Master Refreshing App - Production Build Script
REM Version: 1.0.0
REM Author: ENG. Saeed Al-moghrabi
REM
REM This script builds a clean, optimized, low-detection Windows executable
REM using PyInstaller with antivirus-friendly settings.
REM ============================================================================

echo.
echo ========================================
echo  Master Refreshing App v1.0.0
echo  Clean EXE Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9+ and try again
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo [1/6] Cleaning previous build artifacts...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "*.pyc" del /q "*.pyc"
echo       Done.
echo.

echo [2/6] Verifying resources...
if not exist "resources" (
    echo [ERROR] resources folder not found!
    pause
    exit /b 1
)
if not exist "resources\icon.png" (
    echo [WARNING] icon.png not found in resources folder
    echo           Build will continue without icon
)
if not exist "app.manifest" (
    echo [ERROR] app.manifest not found!
    echo         Please ensure app.manifest exists in project root
    pause
    exit /b 1
)
echo       All required files verified.
echo.

echo [3/6] Converting PNG icon to ICO format...
python -c "from PIL import Image; img=Image.open('resources/icon.png'); img.save('resources/icon.ico', format='ICO', sizes=[(256,256)])" 2>nul
if errorlevel 1 (
    echo [WARNING] Could not convert icon (Pillow not installed)
    echo           Install with: pip install Pillow
    echo           Build will continue with PNG icon
) else (
    echo       Icon converted successfully.
)
echo.

echo [4/6] Building executable with PyInstaller...
echo       This may take 2-5 minutes...
echo.

pyinstaller ^
    --clean ^
    --onefile ^
    --noconsole ^
    --name "MasterRefreshingApp" ^
    --icon "resources/icon.png" ^
    --manifest "app.manifest" ^
    --add-data "resources;resources" ^
    --hidden-import win32com ^
    --hidden-import win32com.client ^
    --hidden-import pythoncom ^
    --hidden-import pywintypes ^
    --hidden-import PyQt6.QtCore ^
    --hidden-import PyQt6.QtWidgets ^
    --hidden-import PyQt6.QtGui ^
    --exclude-module tkinter ^
    --exclude-module tkinter.test ^
    --exclude-module pip ^
    --exclude-module setuptools ^
    --exclude-module distutils ^
    --exclude-module test ^
    --exclude-module unittest ^
    --exclude-module _bootlocale ^
    --exclude-module doctest ^
    --exclude-module pdb ^
    --exclude-module numpy ^
    --exclude-module matplotlib ^
    --exclude-module scipy ^
    --exclude-module pandas ^
    --strip ^
    --noupx ^
    main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo [5/6] Verifying build output...
if not exist "dist\MasterRefreshingApp.exe" (
    echo [ERROR] Executable not found in dist folder!
    pause
    exit /b 1
)

REM Get file size
for %%A in ("dist\MasterRefreshingApp.exe") do set size=%%~zA
set /a sizeMB=%size% / 1048576
echo       Build successful!
echo       Size: %sizeMB% MB
echo       Location: dist\MasterRefreshingApp.exe
echo.

echo [6/6] Running post-build verification...
python -c "import os; exe='dist/MasterRefreshingApp.exe'; print(f'  - File exists: {os.path.exists(exe)}'); print(f'  - File size: {os.path.getsize(exe):,} bytes')"
echo.

echo ========================================
echo  BUILD COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo Executable location: dist\MasterRefreshingApp.exe
echo.
echo NEXT STEPS:
echo 1. Test the executable thoroughly
echo 2. (Optional) Sign with digital certificate
echo 3. Run antivirus scan with Windows Defender
echo 4. Distribute to end users
echo.
echo For signing instructions, see: BUILD_DOCUMENTATION.md
echo.

pause
