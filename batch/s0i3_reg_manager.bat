@echo off
setlocal enabledelayedexpansion

echo ========================================
echo AMD Platform Registry Manager
echo ========================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: This batch file requires administrator privileges
    echo Please run this batch file as administrator
    pause
    exit /b 1
)

REM Check command line arguments
if "%1"=="/set" (
    echo Setting AMD Platform Registry for Development...
    echo ========================================
    echo.
    
    echo Setting AMD MicroPEP Parameters...
    REM Configure AMD MicroPEP service parameters for debugging
    reg add "HKLM\SYSTEM\CurrentControlSet\Services\AmdMicroPEP\Parameters" /v "PrintOutPostCode" /t REG_DWORD /d 1 /f
    reg add "HKLM\SYSTEM\CurrentControlSet\Services\AmdMicroPEP\Parameters" /v "DumpRuntimeDeviceList" /t REG_DWORD /d 1 /f
    reg add "HKLM\SYSTEM\CurrentControlSet\Services\AmdMicroPEP\Parameters" /v "UseSoCSubsystemAlias" /t REG_DWORD /d 0 /f
    reg add "HKLM\SYSTEM\CurrentControlSet\Services\AmdMicroPEP\Parameters" /v "EnableSoCSubSystemAccounting" /t REG_DWORD /d 1 /f

    echo Setting Power Management Parameters...
    REM Configure sleep study session threshold
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power" /v "SleepStudySessionThresholdSeconds" /t REG_DWORD /d 30 /f

    echo Disabling System Maintenance...
    REM Disable automatic system maintenance
    reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\Maintenance" /v "MaintenanceDisabled" /t REG_DWORD /d 1 /f

    echo Disabling Windows Update...
    REM Disable Windows Update to prevent interference during development
    reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" /v "NoAutoUpdate" /t REG_DWORD /d 1 /f
    reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v "NoWindowsUpdate" /t REG_DWORD /d 1 /f

    echo Setting Keyboard Crash Dump Parameters...
    REM Disable Ctrl+Scroll crash functionality
    reg add "HKLM\SYSTEM\CurrentControlSet\services\i8042prt\Parameters" /v "CrashOnCtrlScroll" /t REG_DWORD /d 0 /f
    reg add "HKLM\SYSTEM\CurrentControlSet\services\kbdhid\Parameters" /v "CrashOnCtrlScroll" /t REG_DWORD /d 0 /f

    echo Setting Crash Dump Keyboard Combinations...
    REM Configure crash dump keyboard combinations for debugging
    reg add "HKLM\SYSTEM\CurrentControlSet\Services\i8042prt\crashdump" /v "Dump1Keys" /t REG_DWORD /d 16 /f
    reg add "HKLM\SYSTEM\CurrentControlSet\Services\i8042prt\crashdump" /v "Dump2Key" /t REG_DWORD /d 1 /f
    reg add "HKLM\SYSTEM\CurrentControlSet\Services\kbdhid\crashdump" /v "Dump1Keys" /t REG_DWORD /d 16 /f
    reg add "HKLM\SYSTEM\CurrentControlSet\Services\kbdhid\crashdump" /v "Dump2Key" /t REG_DWORD /d 1 /f

    echo.
    echo ========================================
    echo All registry settings completed!
    echo ========================================
    echo.
    echo Configured items include:
    echo - AMD MicroPEP Parameters (POST code output, device list dump)
    echo - Power Management Settings (sleep study threshold)
    echo - System Maintenance Control (disabled)
    echo - Windows Update Control (disabled)
    echo - Keyboard Crash Dump Settings (configured for debugging)
    echo.
    echo Some settings may require a system restart to take effect.
    echo.
    goto :end
)

if "%1"=="/restore" (
    echo Restoring AMD Platform Registry to Default...
    echo ========================================
    echo.
    
    echo Restoring AMD MicroPEP Parameters...
    REM Remove AMD MicroPEP registry parameters
    reg delete "HKLM\SYSTEM\CurrentControlSet\Services\AmdMicroPEP\Parameters" /v "PrintOutPostCode" /f >nul 2>&1
    reg delete "HKLM\SYSTEM\CurrentControlSet\Services\AmdMicroPEP\Parameters" /v "DumpRuntimeDeviceList" /f >nul 2>&1
    reg delete "HKLM\SYSTEM\CurrentControlSet\Services\AmdMicroPEP\Parameters" /v "UseSoCSubsystemAlias" /f >nul 2>&1
    reg delete "HKLM\SYSTEM\CurrentControlSet\Services\AmdMicroPEP\Parameters" /v "EnableSoCSubSystemAccounting" /f >nul 2>&1

    echo Restoring Power Management Parameters...
    REM Remove sleep study session threshold setting
    reg delete "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power" /v "SleepStudySessionThresholdSeconds" /f >nul 2>&1

    echo Enabling System Maintenance...
    REM Re-enable automatic system maintenance
    reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\Maintenance" /v "MaintenanceDisabled" /f >nul 2>&1

    echo Enabling Windows Update...
    REM Re-enable Windows Update
    reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" /v "NoAutoUpdate" /f >nul 2>&1
    reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v "NoWindowsUpdate" /f >nul 2>&1

    echo Restoring Keyboard Crash Dump Parameters...
    REM Restore default keyboard crash dump settings
    reg delete "HKLM\SYSTEM\CurrentControlSet\services\i8042prt\Parameters" /v "CrashOnCtrlScroll" /f >nul 2>&1
    reg delete "HKLM\SYSTEM\CurrentControlSet\services\kbdhid\Parameters" /v "CrashOnCtrlScroll" /f >nul 2>&1

    echo Restoring Crash Dump Keyboard Combinations...
    REM Remove crash dump keyboard combinations
    reg delete "HKLM\SYSTEM\CurrentControlSet\Services\i8042prt\crashdump" /v "Dump1Keys" /f >nul 2>&1
    reg delete "HKLM\SYSTEM\CurrentControlSet\Services\i8042prt\crashdump" /v "Dump2Key" /f >nul 2>&1
    reg delete "HKLM\SYSTEM\CurrentControlSet\Services\kbdhid\crashdump" /v "Dump1Keys" /f >nul 2>&1
    reg delete "HKLM\SYSTEM\CurrentControlSet\Services\kbdhid\crashdump" /v "Dump2Key" /f >nul 2>&1

    echo.
    echo ========================================
    echo All registry settings restored!
    echo ========================================
    echo.
    echo Restored items include:
    echo - AMD MicroPEP Parameters (removed custom settings)
    echo - Power Management Settings (restored to default)
    echo - System Maintenance Control (re-enabled)
    echo - Windows Update Control (re-enabled)
    echo - Keyboard Crash Dump Settings (restored to default)
    echo.
    echo Some settings may require a system restart to take effect.
    echo.
    goto :end
)

REM If no valid parameter provided, show usage
echo Usage: %0 [parameter]
echo.
echo Parameters:
echo   /set     - Apply AMD platform registry settings for development
echo   /restore - Restore registry settings to default values
echo.
echo Examples:
echo   %0 /set
echo   %0 /restore
echo.
echo Note: This tool requires administrator privileges.
echo.

:end
echo.
echo Registry manager operation completed.
pause 