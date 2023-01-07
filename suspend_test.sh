#!/bin/bash
# Text STYLE variables
BOLD="\033[1m"
RED='\033[38;5;9m'
GREEN='\033[38;5;2m'
ORANGE_RED="\033[38;5;202m"
C_DODGERBLUE2="\033[38;5;27m"
NC='\033[0m' # No Color
VERSION="1.0.0"

logdir="/var/log/suspend_result"
logfile=$logdir/"suspend_result-$(date -Iseconds)".log
date -Iseconds > $logfile


_echo_color() {
	printf "${1}%s${NC}\n" "$2"
}
_printf_color() {
	printf "${1}%s" "$2"
	_echo_color "${NC}" ""
}
tool_version() {
	echo "suspend test script version ${VERSION}"
}
die() {
  echo "${0##*/}: error: $*" >&2
  exit 1
}
print_log_start () {
    logger "#########################################"
    logger "          Suspend test start             "
    logger "#########################################"
}

print_log_end () {
    logger "#########################################"
    logger "          Suspend test end              "
    logger "#########################################"
}

help_menu () {
    echo "Usage: suspend_test [cycle =c] [suspend/wake delay time=w/s]"
    echo "Commands:"
    echo "  v : suspend script version"
    echo "  w : wake up delay time"
    echo "  a : suspend delay time"
    echo "  b : suspend delay time"
    echo "  c : cycles [defalut : 2500]"
    echo "  h : help"
     exit 1
}

suspend_test_main () {

    echo "#################################" >> $logfile
    echo "      Suspend test start "         >> $logfile
    echo "#################################" >> $logfile

    print_log_start

    crossystem | grep "fwid" >> $logfile 
    echo "" >> $logfile
    echo "" >> $logfile
    echo "" >> $logfile

    _printf_color "${RED}" "Suspend stress testing...... press ctrl + c to stop "
    suspend_stress_test -c $1 --wake_min=$2 --suspend_min=$3 --suspend_max=$4 --record_dmesg_dir=$logdir | tee $logfile 


    cat /sys/kernel/debug/amd_pmc/s0ix_stats >> $logfile
    print_log_end
    

    echo "" >> $logfile
    echo "" >> $logfile
    echo "" >> $logfile
    echo "#################################" >> $logfile
    echo "      Suspend test end "         >> $logfile
    echo "#################################" >> $logfile
}



main () {

    local wake_delay_s="10"
    local suspend_min="15"
    local suspend_max="20"
    local cycles="2500"
    local show_help=""
    local getpot_ret=""

    while getopts 'vw:c:a:b:h' flag; do
    case ${flag} in
      v) tool_version ;;
      w) wake_delay_s="${OPTARG}" ;;
      a) suspend_min="${OPTARG}" ;;
      b) suspend_max="${OPTARG}" ;;
      c) cycles="${OPTARG}" ;;
      h) help_menu ;;
      *) die "invalid option found" ;;
     esac
    done

    _printf_color "${GREEN}" "wake_delay_s : ${wake_delay_s} "
    _printf_color "${GREEN}" "suspend_min : ${suspend_min} "
    _printf_color "${GREEN}" "suspend_max : ${suspend_max} "
    _printf_color "${GREEN}" "cycles : ${cycles} "
    
    if [ ! -d "$logdir" ]; then
        echo "$logdir does exist."
        mkdir $logdir
    fi
    suspend_test_main $cycles $wake_delay_s $suspend_min $suspend_max
    
}

main "$@"
