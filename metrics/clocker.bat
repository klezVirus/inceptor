@echo off
pushd ..\inceptor
cloc.exe --exclude-dir venv,drop,artifacts,certs,.idea,tests,temp,libs,dist,sywhisper,syswhispers2,build --exclude-ext exe,def,png,md,json,asm,xml,js,pl .
popd