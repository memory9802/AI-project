# ====================================
# Windows 快速啟動腳本
# ====================================
# 使用方式: 在 PowerShell 中執行
# .\start-windows.ps1
# ====================================

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  穿搭推薦 AI 專案 - Windows 啟動    " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 檢查 Docker Desktop 是否運行
Write-Host "[1/6] 檢查 Docker Desktop..." -ForegroundColor Yellow
$dockerProcess = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
if ($null -eq $dockerProcess) {
    Write-Host "❌ Docker Desktop 未運行!" -ForegroundColor Red
    Write-Host "請先啟動 Docker Desktop,然後重新執行此腳本" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker Desktop 正在運行" -ForegroundColor Green
Write-Host ""

# 檢查 .env 檔案
Write-Host "[2/6] 檢查環境變數檔案..." -ForegroundColor Yellow
if (-Not (Test-Path ".env")) {
    Write-Host "❌ .env 檔案不存在!" -ForegroundColor Red
    Write-Host "正在從 .env.example 建立 .env..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✅ .env 檔案已建立,請檢查並填入正確的 API Key" -ForegroundColor Green
}
else {
    Write-Host "✅ .env 檔案存在" -ForegroundColor Green
}
Write-Host ""

# 檢查端口佔用
Write-Host "[3/6] 檢查端口佔用..." -ForegroundColor Yellow
$ports = @(5001, 3306, 8080)
$portsInUse = @()

foreach ($port in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        $portsInUse += $port
    }
}

if ($portsInUse.Count -gt 0) {
    Write-Host "⚠️  以下端口被佔用: $($portsInUse -join ', ')" -ForegroundColor Yellow
    Write-Host "如果是舊容器佔用,將會被停止" -ForegroundColor Yellow
}
else {
    Write-Host "✅ 所有端口都可用" -ForegroundColor Green
}
Write-Host ""

# 停止舊容器
Write-Host "[4/6] 停止舊容器..." -ForegroundColor Yellow
docker compose down 2>&1 | Out-Null
Write-Host "✅ 舊容器已停止" -ForegroundColor Green
Write-Host ""

# 重建並啟動容器
Write-Host "[5/6] 重建並啟動容器 (這可能需要 1-2 分鐘)..." -ForegroundColor Yellow
docker compose up -d --build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 容器啟動失敗!" -ForegroundColor Red
    Write-Host "請檢查 Docker Desktop 日誌" -ForegroundColor Red
    exit 1
}
Write-Host "✅ 容器啟動成功" -ForegroundColor Green
Write-Host ""

# 等待服務就緒
Write-Host "[6/6] 等待服務就緒 (15 秒)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# 測試服務
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  測試服務狀態                       " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 測試 Flask API
Write-Host "測試 Flask API..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5001/ping" -TimeoutSec 5
    Write-Host "✅ Flask API 運行正常" -ForegroundColor Green
    Write-Host "   - 狀態: $($response.status)" -ForegroundColor Gray
    Write-Host "   - AI 啟用: $($response.ai_enabled)" -ForegroundColor Gray
    Write-Host "   - 模型: $($response.gemini_model)" -ForegroundColor Gray
}
catch {
    Write-Host "❌ Flask API 無法連線" -ForegroundColor Red
    Write-Host "   錯誤: $_" -ForegroundColor Red
}
Write-Host ""

# 測試 MySQL
Write-Host "測試 MySQL..." -ForegroundColor Yellow
$mysqlTest = docker exec outfit-mysql mysql -u root -prootpassword -e "SELECT 1" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ MySQL 運行正常" -ForegroundColor Green
}
else {
    Write-Host "❌ MySQL 連線失敗" -ForegroundColor Red
}
Write-Host ""

# 顯示容器狀態
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  容器狀態                           " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
docker compose ps
Write-Host ""

# 顯示存取資訊
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  服務存取資訊                       " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "🌐 網站主頁:     http://localhost:5001" -ForegroundColor Green
Write-Host "🤖 AI API:       http://localhost:5001/recommend" -ForegroundColor Green
Write-Host "🗄️  phpMyAdmin:  http://localhost:8080" -ForegroundColor Green
Write-Host "   (帳號: root / 密碼: rootpassword)" -ForegroundColor Gray
Write-Host ""

# 顯示常用指令
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  常用指令                           " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "查看日誌:       docker compose logs -f flask" -ForegroundColor Yellow
Write-Host "停止服務:       docker compose down" -ForegroundColor Yellow
Write-Host "重啟服務:       docker compose restart" -ForegroundColor Yellow
Write-Host "重建容器:       docker compose up -d --build" -ForegroundColor Yellow
Write-Host ""

Write-Host "✨ 啟動完成! 可以開始使用了" -ForegroundColor Green
Write-Host ""
