@echo off
echo.
echo ================================
echo   JELAJAH WISATA - FORCE PUSH
echo ================================
echo.

:: Masuk ke folder project (sesuaikan jika perlu)
cd /d "%~dp0"

:: Stage semua perubahan
git add -A

:: Buat commit dengan timestamp otomatis
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set d=%%c-%%b-%%a
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set t=%%a%%b
git commit -m "update: deploy %d% %t%"

:: Force push ke main
git push origin main --force

echo.
echo ================================
echo   PUSH SELESAI!
echo ================================
pause
