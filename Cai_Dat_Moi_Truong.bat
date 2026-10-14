@echo off
chcp 65001 >nul
title FireEyes AI - Cai Dat Moi Truong
echo =======================================================
echo 🔥 CAI DAT MOI TRUONG PYTHON CHO FIREEYES AI
echo =======================================================
cd /d "%~dp0"

echo [1/4] Kiem tra phien ban Python...
python --version
if %errorlevel% neq 0 (
    echo [!] Chua tim thay Python tren may cua ban.
    echo Vui long truy cap: https://www.python.org/downloads/
    echo Tai va cai dat Python 3.12 (nho tick vao o "Add python.exe to PATH").
    echo.
    echo Luu y: Neu chi muon xem va test Giao Dien Web ngay, ban chi can
    echo click dup vao file "Mo_Giao_Dien_Web.bat" ma KHONG can Python!
    pause
    exit /b 1
)

echo [2/4] Dang tao moi truong ao (.venv)...
if not exist ".venv" (
    python -m venv .venv
    echo Da tao thu muc .venv thanh cong.
) else (
    echo Thu muc .venv da ton tai, tiep tuc...
)

echo [3/4] Dang cai dat thu vien tu requirements.txt...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo [4/4] Khoi tao co so du lieu SQLite FireEyes...
python -m backend.main init

echo.
echo =======================================================
echo ✅ CAI DAT HOAN TAT THANH CONG!
echo.
echo Cach khoi dong he thong:
echo 1. Chay Backend: Click dup "Chay_FastAPI_Backend.bat"
echo 2. Chay Web:     Click dup "Mo_Giao_Dien_Web.bat"
echo =======================================================
pause
