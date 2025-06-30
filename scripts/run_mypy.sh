#!/usr/bin/env bash
python3 -m pip install --upgrade pip
python3 -m pip install mypy==1.16.1
# Run your standardised mypy invocation, e.g.
mypy custom_components/weishaupt_modbus/
