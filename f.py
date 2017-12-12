#!/usr/bin/env python
import os
import subprocess
import sys


def scan_arg(argv):
    for cmd in argv:
        if (argv == '-b'):
            BOARD = cmd
            print str(cmd)

def flashrom():
        
    print "---------> Flashing ......"
    subprocess.call(["dut-control","spi2_buf_en:on","spi2_buf_on_flex_en:on","spi2_vref:pp3300","cold_reset:on"])
    subprocess.call(["sudo","flashrom","-p","ft2232_spi:type=servo-v2","-w","/build/nautilus/firmware/image.serial.bin" ])
    subprocess.call(["dut-control","spi2_buf_en:on","spi2_buf_on_flex_en:on","spi2_vref:pp3300","cold_reset:off"])

def main(argv):
#    scan_arg(argv)
        flashrom()

if __name__ == '__main__':
    main(sys.argv)

