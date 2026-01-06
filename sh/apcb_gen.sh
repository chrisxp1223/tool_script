#!/bin/bash

# Remove Build folder
rm -rf ~/trunk/src/third_party/amd-fsp/phoenix/Build

# Create APCB
cd ~/trunk/src/third_party/amd-fsp/phoenix/
Platform/AmdPhoenix2FspPkg/BuildApcb.sh --board=myst --debug --gcc-prefix=/usr/bin/

# Rename APCB_FP8_LPDDR5.bin to APCB_PHX_D5.bin
mv ~/trunk/src/third_party/amd-fsp/phoenix/Build/APCB_FP8_LPDDR5.bin ~/trunk/src/third_party/amd-fsp/phoenix/APCB_PHX_D5.bin