@echo off
chcp 65001 >nul
title FireEyes AI - Khoi Dong Giao Dien Web
echo =======================================================
echo 🔥 HE THONG PHAT HIEN CHAY & KHOI FIREEYES AI
echo =======================================================
echo Dang khoi dong may chu web tren cong 3000...
cd /d "%~dp0"
start "" "http://localhost:3000"
node server.js
pause
