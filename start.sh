#!/usr/bin/env bash
set -e

echo "=============================="
echo "  Job Search Agent - Setup"
echo "=============================="
echo ""

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "First-time setup! I need your OpenAI API key."
    echo "You can find it at: https://platform.openai.com/api-keys"
    echo ""
    read -p "Paste your OpenAI API key: " api_key
    echo ""

    cp .env.example .env
    sed -i "s|sk-your-key-here|$api_key|" .env
    echo "Saved! Your key is stored in .env (this file is git-ignored and private)."
    echo ""
else
    echo "Found existing .env file - using saved settings."
    echo ""
fi

# Set up Python virtual environment if needed
if [ ! -d .venv ]; then
    echo "Setting up Python environment (one-time)..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing dependencies..."
pip install -q . 2>/dev/null

echo ""
echo "Starting the app..."
echo "Open this link in your browser:"
echo ""
echo "  http://127.0.0.1:8000"
echo ""
echo "Press Ctrl+C to stop the app."
echo ""

python -m app.main
