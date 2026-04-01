#!/bin/bash
# WaveSync Quick Start Script for Linux/macOS

echo ""
echo "🚀 WaveSync - Cloud Migration Control Center"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✅ Python found:"
python3 --version

# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "========================================"
echo "🎯 WaveSync is ready!"
echo "========================================"
echo ""
echo "To start the API server:"
echo "  python src/wavesync/frontend/app.py"
echo ""
echo "To start the Streamlit dashboard:"
echo "  streamlit run frontend/dashboard.py"
echo ""
echo "========================================"
echo ""
