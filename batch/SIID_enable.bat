@echo off
REM ====================================================================
REM SIID_enable.bat - Manage System Information ID (SIID) functionality
REM 
REM Description: This batch script enables or clears SIID (System Information ID) 
REM              functionality in the system
REM
REM Usage: SIID_enable.bat [enable|clear]
REM   enable - Enable SIID functionality (default)
REM   clear  - Clear SIID functionality
REM
REM Author: Tool Script Collection
REM Date: 2025-01-16
REM ====================================================================

setlocal enabledelayedexpansion

REM Check argument
set "action=%~1"
if "%action%"=="" set "action=enable"
if /i "%action%"=="enable" goto :enable
if /i "%action%"=="clear" goto :clear
if /i "%action%"=="help" goto :help
if /i "%action%"=="/?" goto :help
if /i "%action%"=="-h" goto :help
if /i "%action%"=="--help" goto :help

REM Invalid argument
echo.
echo ERROR: Invalid argument '%action%'
echo.
goto :help

:help
echo.
echo ====================================================================
echo                      SIID Management Script
echo ====================================================================
echo.
echo Description:
echo   This script manages System Information ID (SIID) functionality
echo   using MWTMSET1.exe tool.
echo.
echo Usage: %~nx0 [enable^|clear^|help]
echo.
echo Arguments:
echo   enable - Enable SIID functionality (default)
echo            Sets JE:ACUEDSTEP, &J:TPM4, K3:MSCAE
echo   clear  - Clear SIID functionality
echo            Clears JE:, &J:, K3: values
echo   help   - Show this help message
echo.
echo Examples:
echo   %~nx0           ^(Enable SIID - default^)
echo   %~nx0 enable    ^(Enable SIID^)
echo   %~nx0 clear     ^(Clear SIID^)
echo   %~nx0 help      ^(Show help^)
echo.
exit /b 0

:enable
title SIID Enable Script

echo.
echo ====================================================================
echo                      SIID Enable Script
echo ====================================================================
echo.

echo Enabling SIID functionality...
echo.

echo Setting JE:ACUEDSTEP...
MWTMSET1.exe /SIID /W JE:ACUEDSTEP
if %errorlevel% neq 0 (
    echo ERROR: Failed to set JE:ACUEDSTEP
    goto :error
)

echo Setting &J:TPM4...
MWTMSET1.exe /SIID /W &J:TPM4
if %errorlevel% neq 0 (
    echo ERROR: Failed to set &J:TPM4
    goto :error
)

echo Setting K3:MSCAE...
MWTMSET1.exe /SIID /W K3:MSCAE
if %errorlevel% neq 0 (
    echo ERROR: Failed to set K3:MSCAE
    goto :error
)

echo.
echo SIID functionality has been enabled successfully.
echo   - JE:ACUEDSTEP set
echo   - &J:TPM4 set
echo   - K3:MSCAE set
goto :end

:clear
title SIID Clear Script

echo.
echo ====================================================================
echo                      SIID Clear Script
echo ====================================================================
echo.

echo Clearing SIID functionality...
echo.

echo Clearing JE value...
MWTMSET1.exe /SIID /W JE:
if %errorlevel% neq 0 (
    echo ERROR: Failed to clear JE value
    goto :error
)

echo Clearing &J value...
MWTMSET1.exe /SIID /W &J:
if %errorlevel% neq 0 (
    echo ERROR: Failed to clear &J value
    goto :error
)

echo Clearing K3 value...
MWTMSET1.exe /SIID /W K3:
if %errorlevel% neq 0 (
    echo ERROR: Failed to clear K3 value
    goto :error
)

echo.
echo SIID functionality has been cleared successfully.
echo   - JE value cleared
echo   - &J value cleared
echo   - K3 value cleared
goto :end

:error
echo.
echo SIID operation failed!
echo Please check MWTMSET1.exe is available and try again.
exit /b 1

:end
echo.

pause