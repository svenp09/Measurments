#!/bin/bash -e




export IDF_TOOLS_PATH="/proj/i4watwa/bin/esp-idf-tools"
export PATH="$PATH:$IDF_TOOLS_PATH"
. /proj/i4watwa/src/esp-idf/export.sh
[ $# -eq 1 ] && pushd "${ESPBASE}/projects/$1"
