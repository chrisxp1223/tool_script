#!/usr/bin/env python
import os
import subprocess
import sys

def lid_off():
    subprocess.call(["dut-control", "lid_open:no",])
    print "lid off....."

def lid_open(): 
    subprocess.call(["dut-control", "lid_open:yes",])
    print "lid open...."

def check_ping():
    hostname = "172.16.40.221"
    response = os.system("ping -c 1 " + hostname)
    # and then check the response...
    if response == 0:
        pingstatus = "Network Active"
    else:
        pingstatus = "Network Error"

    return pingstatus


def main():
    test_count = 1000
    while (test_count > 0):
        
        lid_off()
        
        subprocess.call(["sleep", "15",])
        
        lid_open()
        
        subprocess.call(["sleep", "20",])
        
        if ("Network Error" == check_ping()):
            break
        
        test_count -= 1
        print "test count %d"%(test_count)

main()
