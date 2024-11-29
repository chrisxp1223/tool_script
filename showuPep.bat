@echo off
REM ============================================
REM Batch File: showuPep.bat
REM Description: Modify multiple registry keys
REM Author: C.C
REM Date: 2024-11-28
REM ============================================

REM add or update default value of a registry key
reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\CI\Config\Default" /f

REM update CLSID value 
reg add "HKEY_CURRENT_USER\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /ve /t REG_SZ /d "" /f

REM update value of a registry key for power 
reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Power" /v SleepStudySessionThresholdSeconds /t REG_DWORD /d 30 /f

REM update value of a registry key for system policies
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v PromptOnSecureDesktop /t REG_DWORD /d 0 /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v EnableLUA /t REG_DWORD /d 1 /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v ConsentPromptBehaviorAdmin /t REG_DWORD /d 0 /f

REM update value of a registry key for AMD MicroPEP
reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\AmdMicroPEP\Parameters" /v PrintOutPostCode /t REG_DWORD /d 1 /f
reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\AmdMicroPEP\Parameters" /v DumpRuntimeDeviceList /t REG_DWORD /d 1 /f
reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\AmdMicroPEP\Parameters" /v UseSoCSubsystemAlias /t REG_DWORD /d 0 /f
reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\AmdMicroPEP\Parameters" /v EnableSoCSubSystemAccounting /t REG_DWORD /d 1 /f

REM done 
echo done, please restart system.
pause
