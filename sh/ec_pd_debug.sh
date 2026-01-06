#!/bin/sh

mkdir -p "/tmp/ec_pd_debug"
logfile="/tmp/ec_pd_debug/$(date -Iseconds).txt"
date -Iseconds > $logfile

echo "####### ectool uptimeinfo" >> $logfile
ectool uptimeinfo >> $logfile
echo "####### ectool usbpdmuxinfo" >> $logfile
ectool usbpdmuxinfo >> $logfile
echo "####### ectool console" >> $logfile
ectool console >> $logfile
echo "####### ectool pdlog" >> $logfile
ectool pdlog >> $logfile
echo "####### ectool usbpdpower 0" >> $logfile
ectool usbpdpower 0 >> $logfile
echo "####### ectool usbpd 0" >> $logfile
ectool usbpd 0 >> $logfile
echo "####### ectool usbpdpower 1" >> $logfile
ectool usbpdpower 1 >> $logfile
echo "####### ectool usbpd 1" >> $logfile
ectool usbpd 1 >> $logfile
echo "####### lsusb -t" >> $logfile
lsusb -t >> $logfile

echo "created $logfile"
