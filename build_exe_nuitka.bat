@echo off
REM ============================================================================
REM Master Refreshing App - Nuitka Build Script (Alternative)
REM Version: 1.0.0
REM Author: ENG. Saeed Al-moghrabi
REM
REM This script builds using Nuitka for maximum performance and lowest
REM antivirus false-positive rate. Nuitka compiles Python to C, then to
REM native machine code.
REM
REM Prerequisites:
REM   - Python 3.9+
REM   - Nuitka: pip install nuitka
REM   - C Compiler: MinGW64 or MSVC (Visual Studio Build Tools)
REM ============================================================================

echo.
echo ========================================
echo  Master Refreshing App v1.0.0
echo  Nuitka Build Script (Low Detection)
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Nuitka is installed
python -c "import nuitka" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Nuitka not found. Installing...
    echo        This may take several minutes...
    pip install nuitka ordered-set
    if errorlevel 1 (
        echo [ERROR] Failed to install Nuitka
        pause
        exit /b 1
    )
)

echo [1/5] Cleaning previous build artifacts...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "MasterRefreshingApp.dist" rmdir /s /q "MasterRefreshingApp.dist"
if exist "MasterRefreshingApp.build" rmdir /s /q "MasterRefreshingApp.build"
if exist "*.pyi" del /q "*.pyi"
echo       Done.
echo.

echo [2/5] Verifying C compiler...
echo       Checking for MinGW64 or MSVC...
python -c "from nuitka.utils.WindowsResources import *" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] C compiler may not be properly configured
    echo           Nuitka will attempt to download MinGW64 automatically
)
echo.

echo [3/5] Building with Nuitka...
echo       This will take 5-15 minutes on first run...
echo       Please be patient...
echo.

python -m nuitka ^
    --standalone ^
    --onefile ^
    --enable-plugin=pyqt6 ^
    --windows-console-mode=disable ^
    --windows-icon-from-ico=resources/icon.png ^
    --company-name="Master Tools" ^
    --product-name="Master Refreshing App" ^
    --file-version=1.0.0.0 ^
    --product-version=1.0.0 ^
    --file-description="Professional Excel Automation Tool" ^
    --copyright="ENG. Saeed Al-moghrabi" ^
    --include-data-dir=resources=resources ^
    --nofollow-import-to=tkinter ^
    --nofollow-import-to=test ^
    --nofollow-import-to=unittest ^
    --nofollow-import-to=numpy ^
    --nofollow-import-to=matplotlib ^
    --remove-output ^
    --assume-yes-for-downloads ^
    --output-dir=dist ^
    --output-filename=MasterRefreshingApp.exe ^
    main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Nuitka build failed!
    echo.
    echo Common solutions:
    echo 1. Install Visual Studio Build Tools
    echo 2. Install MinGW64
    echo 3. Run: pip install --upgrade nuitka
    echo.
    pause
    exit /b 1
)

echo.
echo [4/5] Verifying build output...
if not exist "dist\MasterRefreshingApp.exe" (
    echo [ERROR] Executable not found!
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

echo [5/5] Post-build verification...
python -c "import os; exe='dist/MasterRefreshingApp.exe'; print(f'  - File exists: {os.path.exists(exe)}'); print(f'  - File size: {os.path.getsize(exe):,} bytes')"
echo.

echo ========================================
echo  NUITKA BUILD COMPLETED!
echo ========================================
echo.
echo Executable: dist\MasterRefreshingApp.exe
echo.
echo ADVANTAGES OF NUITKA BUILD:
echo  + Lowest antivirus false-positive rate
echo  + Best performance (native machine code)
echo  + Smaller executable size
echo  + Better code protection
echo.
echo NEXT STEPS:
echo 1. Test the executable
echo 2. (Optional) Sign with certificate
echo 3. Distribute to users
echo.

pause
