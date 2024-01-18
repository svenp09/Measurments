#!/bin/bash -e

export IDF_TOOLS_PATH="/proj/i4watwa/bin/esp-idf-tools"
export PATH="$PATH:$IDF_TOOLS_PATH"
. /proj/i4watwa/src/esp-idf/export.sh
[ $# -eq 1 ] && pushd "${ESPBASE}/projects/$1"

python3 /proj/i4watwa/projects/playground/measurements/fusion_tool.py --csv ~/Documents/Measurements/VoltageDrop_measurement/voltageDrop.csv --start_cond switch --dump dump.csv --sampling_frequency 100000 --capture_duration 10 --end duration


