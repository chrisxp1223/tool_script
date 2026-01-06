#!/bin/bash

VERSION="0.02"
PROGRAM=$0
PROGNAME="$(basename "${PROGRAM}")"

ROOT_DIR="silverback"
COREBOOT_DIR="coreboot"
FSP_DIR="fsp"

FSP_BRANCH="silverback-code-drop-20190614"
COREBOOT_BRANCH="silverback-code-drop-20190614"
COREBOOT_BLOBS_BRANCH="marshall-blobs"
UPDATE_GIT_REPOS=0
BUILD_FSP=1
BUILD_COREBOOT=1
PRINT_USAGE=0
CLEAN=0
ENV_TOOLCHAIN=0
SHOW_STATUS=0

BOLD="\033[1m"
RED='\033[38;5;9m'
BLUE='\033[38;5;12m'
GREEN='\033[38;5;2m'
ORANGERED="\033[38;5;202m"
C_DODGERBLUE2="\033[38;5;27m"
C_TURQUOISE2="\033[38;5;45m"
NC='\033[0m' # No Color

################################################################################

usage() {
  retval="$1"

  echo "Usage: ${PROGNAME} [options]"
  echo
  echo "Options:"
  echo " -V | --version            Print the version and exit"
  echo " -h | --help               Print this usage information"
  echo " -N | --nocolor            Don't use color codes"
  echo " -D | --debug              Print debug information.  Use -DD to show all commands"
  echo " -U | --update             Update coreboot and fsp directories and all submodules"
  echo " -F | --fsp                Just build FSP"
  echo " -c | --coreboot           Just build coreboot"
  echo " -C | --clean              Clean both FSP & coreboot"
  echo " -E | --envtoolchain       Use environment toolchain for build."
  echo " -s | --status             Show repo status"

  echo
  exit "${retval}"
}

_echo_color() {
  local color
  if [[ -z ${NOCOLOR} ]]; then
    color="$1"
  else
    unset NC
  fi
  local text=$2
  local cr=$3

  if [[ -z ${cr} ]]; then
    printf "${color}%s${NC}\n" "${text}"
  else
    printf "${color}%s${NC}" "${text}"
  fi
}

_echo_debug() {
  if [[ -z ${VERBOSE} ]]; then
    return
  fi
  printf "${ORANGERED}%s${NC}\n" "$2" >&2
}

_echo_error() {
  (_echo_color >&2 "${RED}" "$*")
}

# shellcheck disable=SC2016
ssh_warning() {
  echo "If this fails because of a public key failure, make sure you've added"
  echo 'your public ssh key to the silverback repo and run "$KEY".'
  echo
  echo "ssh-add needs to be run outside of your chroot so your private key can be"
  echo "accessed inside the chroot.  Add this to your .bashrc or .zshrc file."
  echo
}

version() {
  echo
  _echo_color "${BOLD}${GREEN}" "${PROGNAME} version ${VERSION}"
  echo
}

check_env() {
  if [[ ${ENV_TOOLCHAIN} != "0" ]]; then
    _echo_color "${ORANGERED}" "Using local build environment instead of cros coreboot toolchain"
    echo
    return
  fi
  if [[ -z ${CHROMEOS_CACHEDIR} ]]; then
    _echo_error "Error: This script is designed to run under the ChromeOS chroot"
    _echo_error "If you haven't set up the chroot previously, please follow the"
    _echo_error "directions here:"
    _echo_color "${C_DODGERBLUE2}" "https://chromium.googlesource.com/chromiumos/docs/+/master/developer_guide.md"
    echo
    echo "If you have set it up before, please copy this script to the chroot's src"
    echo "directory, enter the chroot and run it from there."
    echo
    _echo_color "${BLUE}" "NOTE: To build with your local toolchain use the '-E' parameter."
    exit 1
  fi
}

do_clean() {

  (
    cd "${ROOT_DIR}/${FSP_DIR}" || exit 1
    _echo_color "${BLUE}" "Cleaning FSP..." 1
    rm -f edk2/Conf/*
    rm -rf build
    rm -f ./*.fd
    _echo_color "${BLUE}" "Done"
  ) || exit 1

  (
    cd "${ROOT_DIR}/${COREBOOT_DIR}" || exit 1
    _echo_color "${BLUE}" "Cleaning Coreboot..." 1
    make clean && _echo_color "${BLUE}" "Done"
  ) || exit 1
}

init() {
  # Get arguments
  args=$(getopt -l version,help,nocolor,debug,update,fsp,coreboot,clean,envtoolchain,status -o VhDNUFcCEs -- "$@")
  getopt_ret=$?
  eval set -- "${args}"

  if [ ${getopt_ret} != 0 ]; then
    usage 1
  fi

  while true; do
    case "$1" in
    -V | --version)
      version
      exit 0
      ;;
    -h | --help)
      shift
      PRINT_USAGE=1
      ;;
    -N | --nocolor)
      shift
      NOCOLOR=1
      ;;
    -D | --debug)
      shift
      # -D prints extra debug info
      # -DD prints all script steps
      if [[ -n ${VERBOSE} ]]; then
        set -x
      else
        VERBOSE=-V
      fi
      ;;
    -U | --update)
      UPDATE_GIT_REPOS=1
      shift
      ;;
    -F | --fsp)
      BUILD_COREBOOT=0
      shift
      ;;
    -c | --coreboot)
      BUILD_FSP=0
      shift
      ;;
    -C | --clean)
      CLEAN=1
      shift
      ;;
    -E | --envtoolchain)
      ENV_TOOLCHAIN=1
      shift
      ;;
    -s | --status)
      SHOW_STATUS=1
      shift
      ;;
    --)
      shift
      break
      ;;
    *) break ;;
    esac
  done

  version

  if [[ ${PRINT_USAGE} != "0" ]]; then
    usage 0
  fi

  if [[ ${UPDATE_GIT_REPOS} == "1" ]]; then
    update_repos
    exit 0
  fi

  if [[ ${CLEAN} == "1" ]]; then
    do_clean
    exit 0
  fi

  if [[ ${SHOW_STATUS} == "1" ]]; then
    show_status
    exit 0
  fi
}

show_status() {
  (
    echo
    cd "${ROOT_DIR}/${FSP_DIR}" || exit 1
    _echo_color "${BLUE}" "AMD-FSP repos in ${PWD}"
    git status
    echo
    _echo_color "${BLUE}" "AMD-FSP submodules"
    git submodule foreach 'echo "$path: $(git status)"; echo'
  ) || exit 1

  (
    echo
    cd "${ROOT_DIR}/${COREBOOT_DIR}" || exit 1
    _echo_color "${BLUE}" "coreboot repos in ${PWD}"
    git status
    echo
    _echo_color "${BLUE}" "coreboot submodules"
    git submodule foreach 'echo "$path: $(git status)"; echo'

  ) || exit 1
}

set_up_repos() {
  (
    mkdir -p "${ROOT_DIR}"
    cd "${ROOT_DIR}" || exit 1

    # Clone the top level repos
    ssh_warning
    git clone git@github.silverbackltd.com:amd-fsp/picasso-blob-pkg.git "${FSP_DIR}"

    # shellcheck disable=SC2181
    if [[ $? -ne 0 ]]; then
      ssh_warning
      exit 1
    fi

    git clone git@github.silverbackltd.com:amd-fsp/coreboot.git "${COREBOOT_DIR}"

    # Get AMD-FSP repos
    echo
    _echo_color "${BLUE}" "Downloading AMD-FSP submodules"
    cd "${FSP_DIR}" || exit 1
    git checkout "${FSP_BRANCH}"
    git submodule init
    git submodule update
    make -C edk2/BaseTools/Source/C/ -j
    cd .. || exit 1

    echo
    _echo_color "${BLUE}" "Downloading coreboot submodules"
    cd "${COREBOOT_DIR}" || exit 1
    git checkout "${COREBOOT_BRANCH}"
    git submodule init
    git submodule update
    cd 3rdparty/blobs || exit 1
    git checkout "${COREBOOT_BLOBS_BRANCH}"
    cd ../.. || exit 1

    echo
    _echo_color "${BLUE}" "Setting coreboot configuration for mandolin"
    cp configs/config.mandolin-hardcore .config
    make olddefconfig
  ) || exit 1
}

update_repos() {
  (
    echo
    cd "${ROOT_DIR}/${FSP_DIR}" || exit 1
    _echo_color "${BLUE}" "Updating AMD-FSP repos in ${PWD}"
    if ! git fetch; then
      ssh_warning
      exit 1
    fi
    if ! git rebase "${FSP_BRANCH}"; then
      _echo_error "Error.  Please take care of any issues and rerun the script"
      exit 1
    fi

    _echo_color "${BLUE}" "Updating AMD-FSP submodules in ${PWD}"
    git submodule status
    if ! git submodule update --rebase; then
      _echo_error "Error.  Please take care of any issues and rerun the script"
      exit 1
    fi
  ) || exit 1

  (
    echo
    cd "${ROOT_DIR}/${COREBOOT_DIR}" || exit 1
    _echo_color "${BLUE}" "Updating coreboot repos in ${PWD}"
    if ! git fetch; then
      ssh_warning
      exit 1
    fi
    if ! git rebase "${COREBOOT_BRANCH}"; then
      _echo_error "Error.  Please take care of any issues and rerun the script"
      exit 1
    fi
    _echo_color "${BLUE}" "Updating coreboot submodules in ${PWD}"
    git submodule status
    if ! git submodule update --rebase; then
      _echo_error "Error.  Please take care of any issues and rerun the script"
      exit 1
    fi

  ) || exit 1
}

update_repos() {
  (
    echo
    cd "${ROOT_DIR}/${FSP_DIR}" || exit 1
    _echo_color "${BLUE}" "Updating AMD-FSP repos in ${PWD}"
    if ! git fetch; then
      ssh_warning
      exit 1
    fi
    if ! git rebase "${FSP_BRANCH}"; then
      _echo_error "Error.  Please take care of any issues and rerun the script"
      exit 1
    fi

    _echo_color "${BLUE}" "Updating AMD-FSP submodules in ${PWD}"
    git submodule status
    if ! git submodule update --rebase; then
      _echo_error "Error.  Please take care of any issues and rerun the script"
      exit 1
    fi
  ) || exit 1

  (
    echo
    cd "${ROOT_DIR}/${COREBOOT_DIR}" || exit 1
    _echo_color "${BLUE}" "Updating coreboot repos in ${PWD}"
    if ! git fetch; then
      ssh_warning
      exit 1
    fi
    if ! git rebase "${COREBOOT_BRANCH}"; then
      _echo_error "Error.  Please take care of any issues and rerun the script"
      exit 1
    fi
    _echo_color "${BLUE}" "Updating coreboot submodules in ${PWD}"
    git submodule status
    if ! git submodule update --rebase; then
      _echo_error "Error.  Please take care of any issues and rerun the script"
      exit 1
    fi

  ) || exit 1
}

build_fsp() {
  check_env

  (
    _echo_color "${BLUE}" "Building AMD-FSP"
    # Build the AMD-FSP
    cd "${ROOT_DIR}/${FSP_DIR}" || exit 1

    rm -f edk2/Conf/*
    rm -rf build
    rm -f ./*.fd

    if [[ ${ENV_TOOLCHAIN} == "0" ]]; then
      #  export UNIXGCC_IA32_PETOOLS_PREFIX="i686-pc-linux-gnu-"
      export UNIXGCC_IA32_PETOOLS_PREFIX="/opt/coreboot-sdk/bin/i386-elf-"
      export UNIXGCC_X64_PETOOLS_PREFIX="/opt/coreboot-sdk/bin/x86_64-elf-"
    fi
    ./AmdPicassoBlobPkg/BuildFsp2_0.sh
    if [[ ! -f PICASSO_M.fd || ! -f PICASSO_S.fd ]]; then
      _echo_error "Error: FSP build did not complete successfully"
      exit 1
    fi

    cp PICASSO_?.fd "../${COREBOOT_DIR}"
  ) || exit 1
}

build_coreboot() {
  check_env

  (
    _echo_color "${BLUE}" "Building coreboot"
    if [[ ${ENV_TOOLCHAIN} == "0" ]]; then
      export XGCCPATH="/opt/coreboot-sdk/bin/"
    fi
    cd "${ROOT_DIR}/${COREBOOT_DIR}" || exit 1
    make clean
    make olddefconfig

    if ! make -j; then
      _echo_error "Error: coreboot build did not complete successfully"
      exit 1
    fi

  ) || exit 1
}

main() {
  init "$@"
  if [[ ! -d ${ROOT_DIR} || ! -d "${ROOT_DIR}/${FSP_DIR}" || ! -d "${ROOT_DIR}/${COREBOOT_DIR}" ]]; then
    set_up_repos
  fi

  if [[ ${BUILD_FSP} == "1" ]]; then
    build_fsp
  fi

  if [[ ${BUILD_COREBOOT} == "1" ]]; then
    build_coreboot
  fi

}

main "$@"
