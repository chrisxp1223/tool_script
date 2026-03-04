@echo off
setlocal enabledelayedexpansion

:: ============================================================
:: rename.bat - BIOS Binary Copy & Rename Script
:: Usage: rename.bat <SKU> <BUILD_TYPE> <SOURCE_ROOT>
:: Example: rename.bat XB ext C:\Users\chri\Firmware-Dev\StxKrkGpt\Gorgon\PI_1002a
:: ============================================================

set SKU=%1
set BUILD_TYPE=%2
set SOURCE_ROOT=%3

if "%SKU%"=="" (
    echo [ERROR] SKU is required.
    echo Usage: rename.bat ^<SKU^> ^<BUILD_TYPE^> ^<SOURCE_ROOT^>
    exit /b 1
)
if "%BUILD_TYPE%"=="" (
    echo [ERROR] BUILD_TYPE is required. ^(ext or int^)
    exit /b 1
)
if "%SOURCE_ROOT%"=="" (
    echo [ERROR] SOURCE_ROOT is required.
    exit /b 1
)

:: ============================================================
:: Step 1: SKU -> Platform Name Mapping
:: ============================================================
set PLATFORM=unknown

if /i "%SKU%"=="XB"     set PLATFORM=birmanplus
if /i "%SKU%"=="XB1"    set PLATFORM=birmanplus
if /i "%SKU%"=="XB6"    set PLATFORM=birmanplus
if /i "%SKU%"=="XBP"    set PLATFORM=birmanplus
if /i "%SKU%"=="XBT"    set PLATFORM=birmanplus
if /i "%SKU%"=="X2"     set PLATFORM=birmanplus
if /i "%SKU%"=="X3"     set PLATFORM=birmanplus
if /i "%SKU%"=="X8"     set PLATFORM=birmanplus
if /i "%SKU%"=="XG"     set PLATFORM=birmanplus
if /i "%SKU%"=="XG3SET" set PLATFORM=birmanplus
if /i "%SKU%"=="XL"     set PLATFORM=birmanplus
if /i "%SKU%"=="XLK"    set PLATFORM=birmanplus
if /i "%SKU%"=="XC"     set PLATFORM=koratplus
if /i "%SKU%"=="XK"     set PLATFORM=koratplus
if /i "%SKU%"=="K8"     set PLATFORM=koratplus
if /i "%SKU%"=="KG"     set PLATFORM=koratplus
if /i "%SKU%"=="KG3SET" set PLATFORM=koratplus
if /i "%SKU%"=="KS"     set PLATFORM=koratplus
if /i "%SKU%"=="D5"     set PLATFORM=koratplus
if /i "%SKU%"=="S8"     set PLATFORM=somali
if /i "%SKU%"=="P3"     set PLATFORM=somali
if /i "%SKU%"=="SS"     set PLATFORM=somali
if /i "%SKU%"=="SD"     set PLATFORM=somali
if /i "%SKU%"=="SA"     set PLATFORM=aransas
if /i "%SKU%"=="XJ"     set PLATFORM=jaguar
if /i "%SKU%"=="KJ"     set PLATFORM=jaguar
if /i "%SKU%"=="P5"     set PLATFORM=birmanplus
if /i "%SKU%"=="RMSTEST" set PLATFORM=somali

if "%PLATFORM%"=="unknown" (
    echo [ERROR] Unknown SKU: %SKU%
    echo Please update the SKU mapping in rename.bat
    exit /b 1
)

:: ============================================================
:: Step 2: Read Version from manifest.xml (under .repo)
:: ============================================================
set MANIFEST_FILE=%SOURCE_ROOT%\.repo\manifest.xml

if not exist "%MANIFEST_FILE%" (
    echo [ERROR] manifest.xml not found at: %MANIFEST_FILE%
    exit /b 1
)

:: Extract the include name attribute value
set INCLUDE_NAME=
for /f "tokens=2 delims==" %%A in ('findstr /i "include name" "%MANIFEST_FILE%"') do set "RAW=%%A"
:: RAW is: "GorgonPI_FP8_PI1002a_RC1.xml" />
:: Remove double quotes
set "RAW=!RAW:"=!"
:: Remove trailing />
set "INCLUDE_NAME=!RAW: />=!"

if "!INCLUDE_NAME!"=="" (
    echo [ERROR] Could not parse include name from manifest.xml
    exit /b 1
)

:: Extract version segment: find PIxxxx pattern (e.g. PI1002a)
set VERSION=
for /f "tokens=1* delims=_" %%A in ("%INCLUDE_NAME%") do (
    call :extract_version "%INCLUDE_NAME%"
)

if "%VERSION%"=="" (
    echo [ERROR] Could not extract version from: %INCLUDE_NAME%
    exit /b 1
)

echo [INFO] Parsed version: %VERSION%

:: ============================================================
:: Step 3: Locate source binary (.FD) in SOURCE_ROOT
:: ============================================================
set BINARY_FILE=
for %%F in ("%SOURCE_ROOT%\*.FD") do (
    set BINARY_FILE=%%F
)
if "!BINARY_FILE!"=="" (
    for %%F in ("%SOURCE_ROOT%\*.bin") do (
        set BINARY_FILE=%%F
    )
)

if "!BINARY_FILE!"=="" (
    echo [ERROR] No .FD or .bin file found in: %SOURCE_ROOT%
    exit /b 1
)

echo [INFO] Found binary: !BINARY_FILE!

:: ============================================================
:: Step 4: Create Firmware_image folder
:: ============================================================
set OUTPUT_DIR=%SOURCE_ROOT%\Firmware_image

if not exist "%OUTPUT_DIR%" (
    mkdir "%OUTPUT_DIR%"
    echo [INFO] Created folder: %OUTPUT_DIR%
)

:: ============================================================
:: Step 5: Copy & Rename
:: ============================================================
set NEW_NAME=image.%PLATFORM%_%VERSION%_%BUILD_TYPE%.bin
set DEST=%OUTPUT_DIR%\%NEW_NAME%

copy /Y "%BINARY_FILE%" "%DEST%" >nul

if %errorlevel%==0 (
    echo.
    echo [SUCCESS] BIOS binary renamed and copied.
    echo   Source : %BINARY_FILE%
    echo   Output : %DEST%
    echo   Name   : %NEW_NAME%
) else (
    echo [ERROR] Failed to copy binary to: %DEST%
    exit /b 1
)

endlocal
exit /b 0

:: ============================================================
:: Subroutine: Extract PIxxxx segment from include name
:: Input: full include name string
:: ============================================================
:extract_version
set STR=%~1
set RESULT=

:token_loop
for /f "tokens=1* delims=_" %%A in ("%STR%") do (
    set TOKEN=%%A
    set REST=%%B
    echo !TOKEN! | findstr /r "^PI" >nul
    if !errorlevel!==0 (
        set VERSION=!TOKEN!
        goto :eof
    )
    set STR=!REST!
    if not "!REST!"=="" goto token_loop
)
goto :eof