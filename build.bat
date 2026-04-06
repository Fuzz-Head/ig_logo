@echo off
echo ==============================
echo Building (Release Mode)
echo ==============================

call env\Scripts\activate

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

pyinstaller igTool.spec

echo.
echo Build Complete!
echo Output: ig_logo\
pause