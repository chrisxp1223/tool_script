#!/bin/bash

# Initialize variables
flash=false
board=""
file=""

# Parse command line options
while getopts ":df:b:" opt; do
  case "${opt}" in
    d)
      flash=true
      ;;
    f)
      file="${OPTARG}"
      ;;
    b)
      board="${OPTARG}"
      ;;
    \?)
      echo "Invalid option: -${OPTARG}" >&2
      exit 1
      ;;
    :)
      echo "Option -${OPTARG} requires an argument." >&2
      exit 1
      ;;
  esac
done

# Check if board name is provided
if [[ -z "${board}" ]]; then
  echo "Board name is required. Use -b option to specify the board name." >&2
  exit 1
fi

# Check if file exists
if [[ -z "${file}" ]]; then
  if [[ "${flash}" = true ]]; then
    file="/build/${board}/firmware/image-${board}.serial.bin"
  else
    file="/build/${board}/firmware/image-${board}.bin"
  fi
  if [[ ! -f "${file}" ]]; then
    echo "File ${file} does not exist." >&2
    exit 1
  fi
fi

# Increase the coreboot file size
sudo truncate "${file}" --size 33554432

# Flash the coreboot .bin.
sudo futility update --servo --wp=0 -v -i "${file}"