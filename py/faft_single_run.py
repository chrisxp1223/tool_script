#!/usr/bin/env python
import os
import subprocess 
import sys

SCR="/usr/bin/test_that"

task_list = [
    #"platform_ServoPowerStateController_USBPluggedin",
    #"firmware_FwScreenPressPower",
    #"firmware_FwScreenCloseLid",
    #"firmware_RecoveryButton.dev",  
    #"firmware_CorruptFwSigA.dev",
    #"firmware_RollbackFirmware.dev",
    #"firmware_SelfSignedBoot",
    #"firmware_EventLog",
    #"firmware_RollbackKernel.dev",
    #"firmware_CorruptFwSigB",
    "firmware_TPMExtend",
    #"firmware_InvalidUSB",
    #"firmware_CorruptKernelA",
    #"firmware_CorruptFwSigB.dev",
    #"firmware_DevMode",
    #"firmware_RONormalBoot.dev",
    #"firmware_CorruptKernelB.dev",
    #"firmware_CorruptFwBodyA",
    #"firmware_UpdateFirmwareDataKeyVersion",
    #"firmware_RecoveryButton",
    #"firmware_FWtries",
    #"firmware_CorruptBothFwBodyAB.dev",
    #"firmware_CorruptBothFwBodyAB",
    #"firmware_CorruptFwSigA",
    #"firmware_CorruptKernelA.dev",
    "firmware_TPMVersionCheck.dev",
    #"firmware_UpdateKernelSubkeyVersion",
    #"firmware_UpdateKernelDataKeyVersion",
    #"firmware_DevBootUSB",
    #"firmware_FMap",
    #"firmware_FWtries.dev",
    #"firmware_CorruptKernelB",
    #"firmware_CorruptFwBodyB.dev",
    #"firmware_Mosys",
    "firmware_TPMKernelVersion",
    #"firmware_UpdateFirmwareVersion",
    #"firmware_UserRequestRecovery.dev",
    #"firmware_UserRequestRecovery",
    "firmware_TPMVersionCheck",
    #"firmware_RollbackKernel",
    #"firmware_CorruptBothFwSigAB",
    "firmware_TPMNotCorruptedDevMode",
    #"firmware_CorruptBothKernelAB",
    #"firmware_CorruptFwBodyB",
    #"firmware_TryFwB",
    #"firmware_CorruptFwBodyA.dev",
    #"firmware_UpdateKernelVersion",
    #"firmware_CorruptBothFwSigAB.dev",
    #"firmware_RollbackFirmware"
    #"firmware_LegacyRecovery",
    #"firmware_FAFTSetup",
    #"firmware_CorruptBothKernelAB",
    #"firmware_RONormalBoot",
    #"firmware_TryFwB.dev",
    #"firmware_DevScreenTimeout"
]

board=" -b coral"
ip=" 172.16.40.219"

def dut_cleanup():
    subprocess.call(["dut-control", "power_state:reset",])
    print "Dut reset....."
    subprocess.call(["sleep", "10",])



def main():
    
    for index in task_list:
        print "test %s now" %(index)
        os.system(SCR + board+ ip + " "+index)        
        dut_cleanup()

main()
