#!/usr/bin/env bash

set -eoux pipefail

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate

pip install -r tests/requirements_dev.txt
python -m pytest
