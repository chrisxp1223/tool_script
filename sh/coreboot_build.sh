#!/bin/sh
# Copyright (c) 2019 chris.wang@amd.com Authors. All rights reserved.
# Distributed under the terms of the GNU General Public License v2
#
# Propuse :
#  For coreboot image building.
# 
# Environment :
#   POSIX shell.
#
# Input: board name
# Output: coreboot_$(board).rom

ENV_TOOLCHAIN=0
COREBOOT_GENTOOL_VERSION=0
FILESDIR=$(pwd)

BOLD="\033[1m"
RED='\033[38;5;9m'
BLUE='\033[38;5;12m'
GREEN='\033[38;5;2m'
ORANGERED="\033[38;5;202m"
C_DODGERBLUE2="\033[38;5;27m"
C_TURQUOISE2="\033[38;5;45m"
NC='\033[0m' # No Color


_echo_color() {
	printf "${1}%s${NC}\n" "$2"
}
_printf_color() {
	printf "${1}%s" "$2"
	_echo_color "${NC}" ""
}

env_prepare ()
{
    echo "Environment preparing"
    BOARD="$1"
    CONFIG=".config"
    CONFIG_SERIAL=".config_serial"
    BUILD_DIR="build"
    BUILD_DIR_SERIAL="build_serial" 
  
    set_build_env  
    set_config ${BOARD} 
}

set_build_env () {

    sudo apt-get install -y bison build-essential curl flex git libncurses5-dev m4 zlib1g-dev
    make crossgcc-i386 CPUS=$(nproc)
}

set_config()
{
    if [ -s "${FILESDIR}/configs/config.${BOARD}" ]; then
        cp -v "${FILESDIR}/configs/config.${BOARD}" ${CONFIG}
    else 
       echo "Could not find existing config for ${BOARD}." 
    fi
}

make_coreboot () {

    make clean
    make olddefconfig
    if ! make -j; then
      _echo_error "Error: coreboot build did not complete successfully"
      exit 1
    fi

    cp "${BUILD_DIR}/coreboot.rom" "${FILESDIR}/coreboot_${BOARD}.rom"

}

main () {

    local build_target="$1" 

    env_prepare ${build_target}

    make_coreboot
}

main "$@"
