#!/usr/bin/env bash
# Home Assistant development environment
export VIRTUAL_ENV="$HOME/.local/ha-venv"
export PATH="$VIRTUAL_ENV/bin:$PATH"

# Auto-activate on shell start (optional)
if [ -f "$VIRTUAL_ENV/bin/activate" ]; then
    source "$VIRTUAL_ENV/bin/activate"
fi