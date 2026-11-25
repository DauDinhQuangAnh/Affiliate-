@echo off
chcp 65001 >nul
echo Dang khoi dong Affiliate Voice ^& Script Studio...
start "" http://127.0.0.1:8088
if exist "D:\hoctap\python\python.exe" (
    "D:\hoctap\python\python.exe" web\app.py
) else (
    python web\app.py
)
pause
