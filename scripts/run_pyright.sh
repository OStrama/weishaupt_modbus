#!/usr/bin/env bash
# filepath: /workspaces/sax_battery_ha/scripts/run_pyright.sh

set -e

# Activate virtual environment if available
if [ -n "$VIRTUAL_ENV" ]; then
    source "$VIRTUAL_ENV/bin/activate"
fi

# Install pyright if not already installed
if ! command -v pyright &> /dev/null; then
    echo "Installing pyright..."
    python3 -m pip install pyright
fi

# Run pyright on the source code only (exclude tests for now due to missing fixtures)
echo "Running pyright on custom_components..."
pyright custom_components/sax_battery/

echo "Pyright check completed"
