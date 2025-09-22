@echo off
echo Installing FFmpeg for Windows...
echo.

REM Check if ffmpeg is already installed
ffmpeg -version >nul 2>&1
if %errorlevel% == 0 (
    echo FFmpeg is already installed!
    pause
    exit /b 0
)

echo FFmpeg is not installed. Please follow these steps:
echo.
echo 1. Go to https://www.gyan.dev/ffmpeg/builds/
echo 2. Download the "release builds" - "ffmpeg-release-essentials.zip"
echo 3. Extract the zip file to C:\ffmpeg\
echo 4. Add C:\ffmpeg\bin to your system PATH environment variable
echo.
echo Alternatively, you can use one of these methods:
echo.
echo Method 1 - Using Chocolatey (if installed):
echo   choco install ffmpeg
echo.
echo Method 2 - Using winget (Windows 10/11):
echo   winget install ffmpeg
echo.
echo Method 3 - Using scoop (if installed):
echo   scoop install ffmpeg
echo.
echo After installation, restart your command prompt and try running the video splitter again.
echo.
pause
