# ========================================
# AI-Project 環境快速設定腳本 (PowerShell)
# ========================================

Write-Host "🚀 AI-Project 環境設定工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查 .env 是否存在
if (Test-Path ".env") {
    Write-Host "⚠️  偵測到 .env 檔案已存在" -ForegroundColor Yellow
    $overwrite = Read-Host "是否要覆蓋? (y/N)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "❌ 已取消設定" -ForegroundColor Red
        exit
    }
}

Write-Host ""
Write-Host "📝 請輸入以下資訊：" -ForegroundColor Green
Write-Host ""

# 輸入 API Keys
Write-Host "1️⃣  Gemini API Key (必填):" -ForegroundColor Yellow
$geminiKey = Read-Host "   "

Write-Host ""
Write-Host "2️⃣  Groq API Key (選填，按 Enter 跳過):" -ForegroundColor Yellow
$groqKey = Read-Host "   "

Write-Host ""
Write-Host "3️⃣  DeepSeek API Key (選填，按 Enter 跳過):" -ForegroundColor Yellow
$deepseekKey = Read-Host "   "

Write-Host ""
Write-Host "4️⃣  容器名稱前綴 (選填，避免衝突，例如: ian):" -ForegroundColor Yellow
$containerPrefix = Read-Host "   "

Write-Host ""
Write-Host "5️⃣  Port 設定 (直接按 Enter 使用預設值)" -ForegroundColor Yellow
Write-Host ""

$flaskPort = Read-Host "   Flask Port (預設 5001)"
if ([string]::IsNullOrWhiteSpace($flaskPort)) { $flaskPort = "5001" }

$mysqlPort = Read-Host "   MySQL Port (預設 3306)"
if ([string]::IsNullOrWhiteSpace($mysqlPort)) { $mysqlPort = "3306" }

$phpMyAdminPort = Read-Host "   phpMyAdmin Port (預設 8080)"
if ([string]::IsNullOrWhiteSpace($phpMyAdminPort)) { $phpMyAdminPort = "8080" }

# 建立 .env 檔案
Write-Host ""
Write-Host "💾 正在建立 .env 檔案..." -ForegroundColor Cyan

$envContent = @"
# ========================================
# AI API Keys
# ========================================
LLM_API_KEY=$geminiKey
GROQ_API_KEY=$groqKey
DEEPSEEK_API_KEY=$deepseekKey

# ========================================
# Port 設定
# ========================================
FLASK_PORT=$flaskPort
MYSQL_PORT=$mysqlPort
PHPMYADMIN_PORT=$phpMyAdminPort

# ========================================
# 容器名稱前綴
# ========================================
CONTAINER_PREFIX=$containerPrefix
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8

Write-Host "✅ .env 檔案已建立！" -ForegroundColor Green
Write-Host ""
Write-Host "📋 你的設定：" -ForegroundColor Cyan
Write-Host "   Flask:      http://localhost:$flaskPort" -ForegroundColor White
Write-Host "   MySQL:      localhost:$mysqlPort" -ForegroundColor White
Write-Host "   phpMyAdmin: http://localhost:$phpMyAdminPort" -ForegroundColor White
if ($containerPrefix) {
    Write-Host "   容器前綴:    $containerPrefix" -ForegroundColor White
}
Write-Host ""
Write-Host "🐳 下一步：執行以下指令啟動服務" -ForegroundColor Yellow
Write-Host "   docker-compose up -d" -ForegroundColor White
Write-Host ""
