#!/bin/bash
now=`date +"%m_%d_%Y"`
logfile="/home/root/suspend_result-$(now).log"
date -Iseconds > $logfile


echo "#################################" >> $logfile
echo "      Suspend test start "         >> $logfile
echo "#################################" >> $logfile

crossystem | grep "fwid" >> $logfile 
suspend_stress_test >> $logfile 
