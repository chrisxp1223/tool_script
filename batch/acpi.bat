@echo off
REM ******************************************************************
REM * Batch File: acpi.bat
REM * Description: This script configures ACPI settings in the registry.
REM * Author: Frok from BAE team and copilot XD
REM * Date: 2024-11-12
REM ******************************************************************

reg add "HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\WMI\Autologger\ACPI" /v BufferSize /t REG_DWORD /d 0x00000200 /f 
reg add "HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\WMI\Autologger\ACPI" /v ClockType /t REG_DWORD /d 0x00000001 /f 
reg add "HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\WMI\Autologger\ACPI" /v FileName /t REG_SZ /d "c:\Data\SystemData\ETW\ACPI.etl" /f 
reg add "HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\WMI\Autologger\ACPI" /v FlushTimer /t REG_DWORD /d 0x00000001 /f 
reg add "HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\WMI\Autologger\ACPI" /v GUID /t REG_SZ /d "{c514638f-7723-485b-bcfc-96565d735d4a}" /f 
reg add "HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\WMI\Autologger\ACPI" /v LogFileMode /t REG_DWORD /d 0x10080005 /f 
reg add "HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\WMI\Autologger\ACPI" /v MaxFileSize /t REG_DWORD /d 0x00000200 /f 
reg add "HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\WMI\Autologger\ACPI" /v FileMax /t REG_DWORD /d 0x0000000F /f 
reg add "HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\WMI\Autologger\ACPI" /v MinimumBuffers /t REG_DWORD /d 0x00000032 /f 
reg add "HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\WMI\Autologger\ACPI" /v Start /t REG_DWORD /d 0x00000001 /f 
reg add "HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\WMI\Autologger\ACPI" /v Status /t REG_DWORD /d 0x00000000 /f 
reg add "HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\WMI\Autologger\ACPI\{c514638f-7723-485b-bcfc-96565d735d4a}" /v Enabled /t REG_DWORD /d 0x00000001 /f 
reg add "HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\WMI\Autologger\ACPI\{c514638f-7723-485b-bcfc-96565d735d4a}" /v EnableLevel /t REG_DWORD /d 0x00000005 /f 
reg add "HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\WMI\Autologger\ACPI\{c514638f-7723-485b-bcfc-96565d735d4a}" /v MatchAnyKeyword /t REG_QWORD /d 0x0FFFFFFF /f 
reg add "HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\WMI\Autologger\ACPI\{c514638f-7723-485b-bcfc-96565d735d4a}" /v Status /t REG_DWORD /d 0x00000000 /f 
reg add "HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\WMI\Autologger\ACPI\{c514638f-7723-485b-bcfc-96565d735d4a}" /v EnableProperty /t REG_DWORD /d 0x00000000 /f

echo ACPI settings have been configured.
pause
exit /b 0