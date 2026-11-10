
@echo off
setlocal
title TPS-FILE-ORGANIZER

cd /d "%~dp0"

set "APP=%~dp0_TPS_ORGANIZER\runtime\TPS-FILE-ORGANIZER.exe"

echo ==================================================
echo              TPS-FILE-ORGANIZER
echo ==================================================
echo.

if not exist "%APP%" (
    echo Aplikasi belum tersedia.
    echo Silakan siapkan paket aplikasi terlebih dahulu.
    echo.
    pause
    exit /b 1
)

"%APP%"

set "RESULT=%ERRORLEVEL%"

echo.
if "%RESULT%"=="0" (
    echo Proses berhasil diselesaikan.
) else (
    echo Proses tidak berhasil.
)

echo.
pause
exit /b %RESULT%
