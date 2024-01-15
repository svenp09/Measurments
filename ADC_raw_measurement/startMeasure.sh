#!/bin/bash -e

export IDF_TOOLS_PATH="/proj/i4watwa/bin/esp-idf-tools"
export PATH="$PATH:$IDF_TOOLS_PATH"
. /proj/i4watwa/src/esp-idf/export.sh
[ $# -eq 1 ] && pushd "${ESPBASE}/projects/$1"

python3 /proj/i4watwa/projects/playground/measurements/fusion_tool.py --csv ~/Documents/Measurements/ADC_raw_measurement/adc.csv --count 800 --mindiff 0.01 --start_cond rising --end_cond falling --sampling_frequency 100000

cd ..
cd ../oasis 

#idf.py monitor

#cat > ../Measurements/ADC_raw_measurement/esp.txt

#I (48879) main_task: Returned from app_main()