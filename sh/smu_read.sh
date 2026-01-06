#!/bin/bash

#scalr timeconstant PPT
#echo "               ****************************************************************************************"
#echo "               * STAPM edit Tool "
#echo "               * Run as :" $0 "<Skin Control Scalar> <STAPM Time Constant> <Package Power Tracking Limit>"
#echo "               *****************************************************************************************"

val1=
val2=
val3=


if [ -z "$1" ]
  then
    echo "No argument supplied : Please run as" $0 "<scalar in %> <Timeconstant in sec> <PPT in w>"
    echo "             Example : "$0 "68 2500 7.8"
    exit
fi

echo "Skin Control Scalar :" $1
echo "STAPM Time Constant :" $2
echo "Package Power Tracking Limit :" $3

# check the SMU busy

iotools pci_write32 0 0 0 0xB8 0x13000010
iotools pci_read32 0 0 0 0xBC

iotools pci_write32 0 0 0 0xB8 0x13000020
iotools pci_write32 0 0 0 0xBc $1

val=$(($2*1000));
iotools pci_write32 0 0 0 0xB8 0x13000028
iotools pci_write32 0 0 0 0xBc $val
iotools pci_write32 0 0 0 0xB8 0x13000000
iotools pci_write32 0 0 0 0xBc 0x6C


val=$(echo "$3*1000" |bc)
iotools pci_write32 0 0 0 0xB8 0x13000020
iotools pci_write32 0 0 0 0xBc $val
iotools pci_write32 0 0 0 0xB8 0x13000024
iotools pci_write32 0 0 0 0xBc $val
iotools pci_write32 0 0 0 0xB8 0x13000000
iotools pci_write32 0 0 0 0xBc 0x6A

# check the SMU busy
iotools pci_write32 0 0 0 0xB8 0x13000010
iotools pci_read32 0 0 0 0xBC

echo "Successfully set the STAPM parameters"
