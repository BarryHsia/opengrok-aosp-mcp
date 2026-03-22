#!/bin/bash
set -e

echo "🚀 Installing OpenGrok AOSP MCP Server..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $PYTHON_VERSION found, but $REQUIRED_VERSION+ required"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Install uv if not present
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

echo "✅ uv package manager ready"

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Create config if not exists
if [ ! -f config.json ]; then
    echo "⚙️  Creating config.json..."
    cp config.example.json config.json
    echo "⚠️  Please edit config.json with your OpenGrok URL and token"
fi

# Test run
echo "🧪 Testing server..."
timeout 5 uv run python server.py || true

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit config.json with your OpenGrok settings"
echo "2. Add to Kiro config (~/.kiro/settings/mcp.json):"
echo ""
echo '{'
echo '  "mcpServers": {'
echo '    "opengrok-aosp": {'
echo '      "command": "uv",'
echo '      "args": ['
echo '        "--directory",'
echo "        \"$(pwd)\","
echo '        "run",'
echo '        "python",'
echo '        "server.py"'
echo '      ],'
echo '      "env": {'
echo '        "OPENGROK_BASE_URL": "http://your-opengrok:8080/source",'
echo '        "OPENGROK_TOKEN": "your-token"'
echo '      }'
echo '    }'
echo '  }'
echo '}'
echo ""
echo "3. Restart Kiro CLI"
echo "4. Use /tools trust-all to avoid confirmation prompts"
