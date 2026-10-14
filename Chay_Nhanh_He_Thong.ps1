# ===================================================================
#    🔥 FIREEYES AI - QUY TRÌNH 4 BƯỚC KHỞI ĐỘNG HỆ THỐNG (POWERSHELL)
# ===================================================================
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "FireEyes AI - Khoi Dong He Thong 4 Buoc"

# Bước 1: Đặt thư mục làm việc tại thư mục dự án
Set-Location -Path $PSScriptRoot

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "   🔥 FIREEYES AI - QUY TRÌNH 4 BƯỚC KHỞI ĐỘNG HỆ THỐNG" -ForegroundColor Yellow
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host " • [Bước 1] Thư mục làm việc: $PSScriptRoot" -ForegroundColor Green

# Xác định Python ảo
$pyExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pyExe)) {
    $pyExe = "python"
}

# Khởi tạo CSDL nếu cần
& $pyExe -m backend.main init 2>$null

# Bước 3 & Bước 4: Tự động mở trình duyệt sau 2 giây
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://127.0.0.1:8000/health"
    Start-Sleep -Seconds 1
    Start-Process "http://127.0.0.1:8000/"
} | Out-Null

Write-Host " • [Bước 2] Kích hoạt máy chủ FastAPI (Host: 127.0.0.1, Port: 8000)" -ForegroundColor Green
Write-Host " • [Bước 3] Tự động kiểm tra trạng thái: http://127.0.0.1:8000/health" -ForegroundColor Green
Write-Host " • [Bước 4] Tự động mở Giao diện Web SPA: http://127.0.0.1:8000/" -ForegroundColor Green
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "🚀 Đang chạy máy chủ FastAPI & Uvicorn... Nhấn Ctrl+C để dừng." -ForegroundColor Yellow
Write-Host ""

& $pyExe -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 --reload
