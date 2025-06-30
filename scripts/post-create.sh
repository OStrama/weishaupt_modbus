#!/usr/bin/env bash
# requirements_dev is already loaded by Dockerfile.dev
# pip3 install -r requirements_dev.txt
# Home Assistant development environment
export VIRTUAL_ENV="$HOME/.local/ha-venv"
export PATH="$VIRTUAL_ENV/bin:$PATH"

# Auto-activate on shell start (optional)
if [ -f "$VIRTUAL_ENV/bin/activate" ]; then
    source "$VIRTUAL_ENV/bin/activate"
fi

source .venv/bin/activate
pip show pymodbus
