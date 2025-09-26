#!/bin/bash

# Video Meeting Minutes Frontend Setup Script
# This script sets up the micro frontend architecture

set -e

echo "🚀 Setting up Video Meeting Minutes Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm 8+ first."
    exit 1
fi

echo "✅ npm version: $(npm -v)"

# Install root dependencies
echo "📦 Installing root dependencies..."
npm install

# Install shell dependencies
echo "📦 Installing shell dependencies..."
cd shell
npm install
cd ..

# Install shared module dependencies
echo "📦 Installing shared module dependencies..."
cd modules/shared
npm install
cd ../..

# Install video processing module dependencies
echo "📦 Installing video processing module dependencies..."
cd modules/video-processing
npm install
cd ../..

# Install transcription module dependencies
echo "📦 Installing transcription module dependencies..."
cd modules/transcription
npm install
cd ../..

# Install meeting minutes module dependencies
echo "📦 Installing meeting minutes module dependencies..."
cd modules/meeting-minutes
npm install
cd ../..

# Build shared module first (required by other modules)
echo "🔨 Building shared module..."
cd modules/shared
npm run build
cd ../..

# Build all modules
echo "🔨 Building all modules..."
npm run build

echo "✅ Setup completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Start the backend services:"
echo "   cd .. && python start_services.py"
echo ""
echo "2. Start the frontend development servers:"
echo "   npm run dev"
echo ""
echo "3. Open your browser and navigate to:"
echo "   http://localhost:3000"
echo ""
echo "📚 For more information, see the README.md file"
