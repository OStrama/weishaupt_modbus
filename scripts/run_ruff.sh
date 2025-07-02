#!/usr/bin/env bash
source "$VIRTUAL_ENV/bin/activate"
ruff format --check custom_components/weishaupt_modbus/
ruff check custom_components/weishaupt_modbus/