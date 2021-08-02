@echo off
pip install pyinstaller
pyinstaller --onefile inceptor\inceptor.py
del inceptor.spec > NUL
del /S /Q /F build > NUL
