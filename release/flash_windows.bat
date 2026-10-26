@echo off
rem POCO F4 5G (munch) - HyperOS 4 / Android 17 unofficial port: install script (Windows).
rem   flash_windows.bat          clean install: firmware + kernel + system, ERASES ALL DATA (first install)
rem   flash_windows.bat update   update an existing install of this ROM: system images only, keeps data
rem Needs: unlocked bootloader, phone in fastboot mode (Power + Volume down), platform-tools (fastboot.exe) in this
rem folder or in PATH, Xiaomi/Google USB driver. ONLY for POCO F4 5G (munch). At your own risk.
setlocal EnableDelayedExpansion
cd /d "%~dp0"
set FB=fastboot
if exist "%~dp0fastboot.exe" set FB="%~dp0fastboot.exe"
set FW=abl aop bluetooth cmnlib cmnlib64 devcfg dsp featenabler hyp imagefv keymaster modem qupfw tz uefisecapp xbl xbl_config
set KERNEL=boot dtbo vendor_boot
set LOGICAL=system system_ext product vendor odm mi_ext

echo Checking image files (SHA256SUMS) ...
powershell -NoProfile -Command "$bad=0; Get-Content SHA256SUMS | ForEach-Object { $h,$f=$_ -split '\s+',2; $f=$f.TrimStart('*'); if ((Get-FileHash -Algorithm SHA256 ('images\'+$f)).Hash -ne $h.ToUpper()) { Write-Host ('BAD: '+$f); $bad=1 } }; exit $bad"
if errorlevel 1 ( echo ERROR: checksum mismatch, download again. & goto :fail )

echo Waiting for the phone in fastboot mode ...
%FB% getvar product 2>&1 | findstr /r /c:"^product: *munch" >nul
if errorlevel 1 ( echo ERROR: this is not a POCO F4 5G ^(munch^). Nothing was flashed. & goto :fail )
%FB% getvar unlocked 2>&1 | findstr /r /c:"^unlocked: *yes" >nul
if errorlevel 1 ( echo ERROR: bootloader is locked. Unlock it first, see INSTALL.md. & goto :fail )

if /i "%~1"=="update" goto :logical
echo.
echo CLEAN INSTALL: this ERASES ALL DATA on the phone.
set /p ok=Type YES to continue: 
if not "!ok!"=="YES" ( echo cancelled & goto :fail )
for %%p in (%FW% %KERNEL%) do (
  call :run flash %%p_a images\%%p.img || goto :fail
  call :run flash %%p_b images\%%p.img || goto :fail
)
call :run --disable-verity --disable-verification flash vbmeta_a images\vbmeta.img || goto :fail
call :run --disable-verity --disable-verification flash vbmeta_b images\vbmeta.img || goto :fail
call :run flash vbmeta_system_a images\vbmeta_system.img || goto :fail
call :run flash vbmeta_system_b images\vbmeta_system.img || goto :fail
call :run --set-active=a || goto :fail

:logical
call :run reboot fastboot || goto :fail
timeout /t 8 >nul
%FB% getvar is-userspace 2>&1 | findstr /r /c:"^is-userspace: *yes" >nul
if errorlevel 1 ( echo ERROR: phone did not reach fastbootd & goto :fail )
set slot=a
%FB% getvar current-slot 2>&1 | findstr /r /c:"^current-slot: *b" >nul && set slot=b
if "!slot!"=="a" ( set other=b ) else ( set other=a )
for %%p in (%LOGICAL%) do (
  %FB% delete-logical-partition %%p_!slot!-cow >nul 2>&1
  %FB% delete-logical-partition %%p_!other! >nul 2>&1
)
for %%p in (%LOGICAL%) do ( call :run flash %%p images\%%p.img || goto :fail )

if /i "%~1"=="update" goto :boot
call :run reboot bootloader || goto :fail
timeout /t 8 >nul
call :run erase metadata || goto :fail
call :run erase userdata || goto :fail
:boot
call :run reboot
echo.
echo Done. First boot takes 3-5 minutes. Then see INSTALL.md: "After the first boot".
pause
exit /b 0

:run
echo ^> fastboot %*
%FB% %*
exit /b %errorlevel%

:fail
echo Stopped. Read the message above; see INSTALL.md "Troubleshooting".
pause
exit /b 1
