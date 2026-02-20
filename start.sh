#!/usr/bin/env bash
set -e

echo "=============================="
echo "  Job Search Agent - Setup"
echo "=============================="
echo ""

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env

    if [ -t 0 ]; then
        echo "First-time setup! I need your OpenAI API key."
        echo "You can find it at: https://platform.openai.com/api-keys"
        echo ""
        read -p "Paste your OpenAI API key (or press Enter to skip): " api_key
        echo ""

        if [ -n "$api_key" ]; then
            sed -i "s|sk-your-key-here|$api_key|" .env
            echo "Saved! Your key is stored in .env (this file is git-ignored and private)."
        else
            echo "No API key entered. Continuing in fallback mode."
        fi
        echo ""
    else
        echo "No .env file found and no interactive terminal detected."
        echo "Created .env from .env.example and continuing in fallback mode."
        echo ""
    fi
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
