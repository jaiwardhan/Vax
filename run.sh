#!/bin/bash

PWD_TRIGGER=$(pwd)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd "$SCRIPT_DIR"
python3 "$SCRIPT_DIR/Vax.py" $@
cd "$PWD_TRIGGER"