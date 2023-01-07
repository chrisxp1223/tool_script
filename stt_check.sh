#!/bin/bash
# Text STYLE variables
BOLD="\033[1m"
RED='\033[38;5;9m'
GREEN='\033[38;5;2m'
ORANGE_RED="\033[38;5;202m"
C_DODGERBLUE2="\033[38;5;27m"
NC='\033[0m' # No Color
VERSION="1.0.0"

logfile="$(pwd)/suspend_result-$(date -Iseconds).log"
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

print_info () {
   
   echo "1. SttAlphaAPU "
   echo "2. SttSkinTempLimitAPU"
   echo "3. SttErrCoeff"
   echo "4. SttErrRateCoeff"
   echo "5. SttM1Coeff"
   echo "6. SttM2Coeff"
   echo "7. SttCAPUCoeffg"
   echo "8. SttMinLimit"

}

stt_main () {

    agt -i=2 -SttAlphaAPU -SttSkinTempLimitAPU -SttErrCoeff -SttErrCoeff -SttM1Coeff -SttM2Coeff -SttCAPUCoeffg -SttMinLimit
}



main () {
   
   _printf_color "${GREEN}" "Usage: /usr/local/sbin/stt_check_set.sh [option_parameter] STT_PARAMETER_ID  [Default : all]"
    echo ""
    echo ""
   
    stt_main 

    exit 0
}

main "$@"
