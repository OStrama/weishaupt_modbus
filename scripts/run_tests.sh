#!/usr/bin/env bash
source "$VIRTUAL_ENV/bin/activate"

pytest tests/ --cov=custom_components  --cov-report=xml
