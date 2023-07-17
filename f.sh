#!/bin/bash

# Parse command line options
while getopts ":df:b:" opt; do
  case $opt in
    d)
      flash=true
      ;;
    f)
      file=$OPTARG
      ;;
    b)
      board=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

# Determine file name based on -d option
if [ "$flash" = true ]; then
  file="image.$board.serial.bin"
else
  file="image.$board.bin"
fi

# Increase the coreboot file size
sudo truncate $file --size 33554432

# Flash the coreboot .bin file if -d option is specified
if [ "$flash" = true ]; then
  sudo futility update --quiet --servo --wp=0 -v -d -i $file
fi