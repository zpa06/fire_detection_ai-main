@echo off
chcp 65001 >nul
title FireEyes AI - Khoi Dong FastAPI Backend
cd /d "%~dp0"

echo ===================================================================
echo    🔥 FIREEYES AI - QUY TRÌNH 4 BƯỚC KHỞI ĐỘNG HỆ THỐNG
echo ===================================================================
echo  • [Bước 1] Thư mục dự án: %CD%
echo  • [Bước 2] Kích hoạt máy chủ FastAPI (Port 8000 --reload)
echo  • [Bước 3] Tự động kiểm tra trạng thái: http://127.0.0.1:8000/health
echo  • [Bước 4] Tự động mở Giao diện Web SPA: http://127.0.0.1:8000/
echo ===================================================================
echo.

set "PY_EXE=.venv\Scripts\python.exe"
if not exist "%PY_EXE%" (
    set "PY_EXE=python"
)

rem Khoi tao CSDL
"%PY_EXE%" -m backend.main init >nul 2>&1

rem Tu dong mo trinh duyet sau 2 giay (Buoc 3 va Buoc 4)
start "" /b powershell -NoProfile -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8000/health'; Start-Sleep -Seconds 1; Start-Process 'http://127.0.0.1:8000/'"

echo 🚀 May chu FastAPI dang chay tai: http://127.0.0.1:8000
echo 📖 API Documentation (Swagger UI): http://127.0.0.1:8000/docs
echo (Nhan Ctrl + C de dung may chu)
echo -------------------------------------------------------------------
echo.

"%PY_EXE%" -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 --reload

pause
