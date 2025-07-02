#!/usr/bin/env bash
export VIRTUAL_ENV="$HOME/.local/ha-venv"
source "$VIRTUAL_ENV/bin/activate"

# requirements_dev is already loaded by Dockerfile.dev
# pip3 install -r requirements_dev.txt
echo $VIRTUAL_ENV
which python3
python --version
pip show pymodbus
