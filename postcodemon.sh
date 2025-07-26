#!/bin/bash
cd "$(dirname "$0")"
source py/PostCodeMon/venv/bin/activate
PYTHONPATH=py python -m PostCodeMon.cli.main "$@"