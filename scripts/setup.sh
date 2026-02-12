#!/bin/bash

# Hotel Review Analyzer - Setup Script
# This script sets up the development environment

set -e  # Exit on error

echo "🏨 Hotel Review Analyzer - Setup Script"
echo "========================================"

# Check Python version
echo ""
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "❌ Error: Python 3.10+ is required (found: $python_version)"
    exit 1
fi
echo "✅ Python version: $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null
echo "✅ pip upgraded"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create .env file if it doesn't exist
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please edit .env file and add your API credentials"
else
    echo "ℹ️  .env file already exists"
fi

# Create necessary directories
echo ""
echo "Creating data directories..."
mkdir -p data/cache data/temp output
echo "✅ Data directories created"

# Check if FastAPI can start
echo ""
echo "Checking FastAPI installation..."
python3 -c "from fastapi import FastAPI; print('✅ FastAPI is installed correctly')"

# Check if Streamlit can start
echo ""
echo "Checking Streamlit installation..."
python3 -c "import streamlit; print('✅ Streamlit is installed correctly')"

echo ""
echo "========================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API credentials"
echo "2. Start backend: uvicorn backend.main:app --reload --port 8000"
echo "3. Start frontend: streamlit run streamlit_app.py"
echo ""
echo "For more information, see README.md"
