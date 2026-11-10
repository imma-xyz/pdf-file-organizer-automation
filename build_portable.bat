
@echo off
setlocal
title BUILD TPS-FILE-ORGANIZER

cd /d "%~dp0"

echo ==========================================
echo       BUILD TPS-FILE-ORGANIZER
echo ==========================================
echo.

echo [1/4] Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 goto failed

echo.
echo [2/4] Installing PyInstaller...
python -m pip install pyinstaller
if errorlevel 1 goto failed

echo.
echo [3/4] Packaging application...
python -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onedir ^
    --name TPS-FILE-ORGANIZER ^
    --paths "_TPS_ORGANIZER" ^
    --collect-all pypdf ^
    --distpath "_BUILD\dist" ^
    --workpath "_BUILD\work" ^
    --specpath "_BUILD" ^
    "_TPS_ORGANIZER\app\start.py"

if errorlevel 1 goto failed

echo.
echo [4/4] Creating distribution...

if exist "RELEASE" rmdir /s /q "RELEASE"

mkdir "RELEASE"
mkdir "RELEASE\_TPS_ORGANIZER"

xcopy "_BUILD\dist\TPS-FILE-ORGANIZER" ^
    "RELEASE\_TPS_ORGANIZER\runtime\" /E /I /Y

if errorlevel 1 goto failed

copy "TPS-ORGANIZER.bat" "RELEASE\TPS-FILE-ORGANIZER.bat" /Y
if errorlevel 1 goto failed

echo # TPS-FILE-ORGANIZER > "RELEASE\README.txt"
echo. >> "RELEASE\README.txt"
echo Aplikasi Otomatisasi Pengelolaan Dokumen TPS >> "RELEASE\README.txt"
echo. >> "RELEASE\README.txt"
echo TPS-FILE-ORGANIZER membantu mengelola dokumen PDF pemilu secara batch berdasarkan nomor TPS. >> "RELEASE\README.txt"
echo. >> "RELEASE\README.txt"
echo FITUR >> "RELEASE\README.txt"
echo - Membuat folder TPS secara otomatis. >> "RELEASE\README.txt"
echo - Memecah PDF berdasarkan rentang halaman. >> "RELEASE\README.txt"
echo - Mengelompokkan dokumen berdasarkan jenis pemilihan. >> "RELEASE\README.txt"
echo - Mengubah nama file secara otomatis. >> "RELEASE\README.txt"
echo - Membuat backup dokumen sumber. >> "RELEASE\README.txt"
echo - Menampilkan progress pemrosesan. >> "RELEASE\README.txt"
echo - Menghasilkan laporan CSV dan Excel. >> "RELEASE\README.txt"
echo. >> "RELEASE\README.txt"
echo CARA MENGGUNAKAN >> "RELEASE\README.txt"
echo 1. Ekstrak seluruh isi file ZIP. >> "RELEASE\README.txt"
echo 2. Buka folder aplikasi. >> "RELEASE\README.txt"
echo 3. Jalankan TPS-FILE-ORGANIZER.bat. >> "RELEASE\README.txt"
echo 4. Ikuti petunjuk pada terminal. >> "RELEASE\README.txt"
echo 5. Masukkan folder sumber PDF dan lokasi penyimpanan hasil. >> "RELEASE\README.txt"
echo 6. Tentukan nama wilayah, jumlah TPS, dan rentang halaman setiap jenis dokumen. >> "RELEASE\README.txt"
echo 7. Konfirmasi proses dan tunggu hingga selesai. >> "RELEASE\README.txt"
echo. >> "RELEASE\README.txt"
echo CATATAN >> "RELEASE\README.txt"
echo - Jangan memisahkan file BAT, EXE, dan folder _internal. >> "RELEASE\README.txt"
echo - Gunakan salinan dokumen sumber untuk pengujian awal. >> "RELEASE\README.txt"
echo - Simpan salinan paket ZIP sebagai cadangan. >> "RELEASE\README.txt"

if errorlevel 1 goto failed

echo.
echo ==========================================
echo          BUILD SUCCESSFUL
echo ==========================================
echo.
echo Distribution folder: RELEASE
echo.
pause
exit /b 0

:failed
echo.
echo BUILD FAILED.
echo Check the error message above.
echo.
pause
exit /b 1
