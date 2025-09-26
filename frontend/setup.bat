@echo off
REM Video Meeting Minutes Frontend Setup Script for Windows
REM This script sets up the micro frontend architecture

echo 🚀 Setting up Video Meeting Minutes Frontend...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ first.
    pause
    exit /b 1
)

echo ✅ Node.js version: 
node --version

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm is not installed. Please install npm 8+ first.
    pause
    exit /b 1
)

echo ✅ npm version: 
npm --version

REM Install root dependencies
echo 📦 Installing root dependencies...
call npm install

REM Install shell dependencies
echo 📦 Installing shell dependencies...
cd shell
call npm install
cd ..

REM Install shared module dependencies
echo 📦 Installing shared module dependencies...
cd modules\shared
call npm install
cd ..\..

REM Install video processing module dependencies
echo 📦 Installing video processing module dependencies...
cd modules\video-processing
call npm install
cd ..\..

REM Install transcription module dependencies
echo 📦 Installing transcription module dependencies...
cd modules\transcription
call npm install
cd ..\..

REM Install meeting minutes module dependencies
echo 📦 Installing meeting minutes module dependencies...
cd modules\meeting-minutes
call npm install
cd ..\..

REM Build shared module first (required by other modules)
echo 🔨 Building shared module...
cd modules\shared
call npm run build
cd ..\..

REM Build all modules
echo 🔨 Building all modules...
call npm run build

echo ✅ Setup completed successfully!
echo.
echo 🎯 Next steps:
echo 1. Start the backend services:
echo    cd .. ^&^& python start_services.py
echo.
echo 2. Start the frontend development servers:
echo    npm run dev
echo.
echo 3. Open your browser and navigate to:
echo    http://localhost:3000
echo.
echo 📚 For more information, see the README.md file
pause
