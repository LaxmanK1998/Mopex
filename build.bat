@echo off
REM ============================================================
REM  Mopex – Standalone Build Script
REM  Produces: dist\Mopex\Mopex.exe
REM ============================================================
echo.
echo  Building Mopex standalone executable...
echo  ----------------------------------------

REM Use full path to pyinstaller in case Scripts is not on PATH
set PYI=%LOCALAPPDATA%\Python\pythoncore-3.14-64\Scripts\pyinstaller.exe
if not exist "%PYI%" (
    REM Fallback: try pyinstaller on PATH
    set PYI=pyinstaller
)

REM Clean previous build artifacts
if exist "build" (
    echo  Cleaning previous build folder...
    rmdir /s /q build
)
if exist "dist" (
    echo  Cleaning previous dist folder...
    rmdir /s /q dist
)

REM Run PyInstaller with the spec file
"%PYI%" mopex.spec --noconfirm

if errorlevel 1 (
    echo.
    echo  [ERROR] Build failed. See output above for details.
    pause
    exit /b 1
)

echo.
echo  ============================================================
echo   Build complete!
echo   Executable: dist\Mopex\Mopex.exe
echo.
echo   User data is stored at:
echo   %%USERPROFILE%%\Documents\Mopex\mopex.db
echo   (separate from this executable - safe to share the dist folder)
echo  ============================================================
echo.
pause
