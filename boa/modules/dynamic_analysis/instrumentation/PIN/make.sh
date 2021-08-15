#!/bin/bash

usage()
{
  echo "usage: $(basename $0) -P <pin_path>"
  echo ""
  echo "OPTIONS:"
  echo "  -h                Show this help message and exit"
  echo "  -P <pin_path>     Path to PIN installation"
  echo "  -a <architecture> Target architecture (default is intel64)"
}

CURRENT_DIR=$(dirname "$0")
PIN_ROOT=""
TARGET_ARCH="intel64"

while getopts ":P:a:h" options
do
    case "${options}" in
        P) PIN_ROOT="$OPTARG";;
        a) TARGET_ARCH="$OPTARG";;
        h) usage
            exit 0;;
        \?) usage 1>&2
            exit 1;;
    esac
done

if [[ "$PIN_ROOT" == "" ]]; then
    usage 1>&2
    exit 1
fi
if [[ ! -d "$PIN_ROOT" ]] && [[ ! -L "$PIN_ROOT" ]]; then
    1>&2 echo "WARNING: '${PIN_ROOT}' is not a directory nor a soft link"
    exit 1
fi

for f in $(cat "${CURRENT_DIR}/modules.txt"); do
    echo "INFO: generating '$f' -> '${CURRENT_DIR}/obj-${TARGET_ARCH}/${f%.*}.so'"
    make PIN_ROOT=${PIN_ROOT} TARGET=${TARGET_ARCH} ${CURRENT_DIR}/obj-${TARGET_ARCH}/${f%.*}.so
done
