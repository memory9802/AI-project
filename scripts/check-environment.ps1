# AI 專案環境檢查腳本 - Windows PowerShell 版本
# 此腳本會檢查開發環境的必要組件和配置

Write-Host "🔍 AI 專案環境檢查開始..." -ForegroundColor Blue
Write-Host "==================================" -ForegroundColor Blue

# 檢查結果計數
$Script:Checks = 0
$Script:Passed = 0
$Script:Warnings = 0

# 輔助函數
function Test-Command {
    param(
        [string]$Command,
        [string]$Name,
        [string]$VersionFlag = ""
    )
    
    $Script:Checks++
    
    try {
        $null = Get-Command $Command -ErrorAction Stop
        
        if ($VersionFlag) {
            $version = & $Command $VersionFlag 2>$null | Select-Object -First 1
        } else {
            $version = "已安裝"
        }
        
        Write-Host "✅ $Name" -ForegroundColor Green -NoNewline
        Write-Host ": $version"
        $Script:Passed++
    }
    catch {
        Write-Host "❌ $Name" -ForegroundColor Red -NoNewline
        Write-Host ": 未安裝或不在 PATH 中"
    }
}

function Test-Port {
    param(
        [int]$Port,
        [string]$Service
    )
    
    $Script:Checks++
    
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    
    if ($connection) {
        $processId = $connection.OwningProcess
        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        $processName = if ($process) { $process.ProcessName } else { "未知進程" }
        
        Write-Host "⚠️  端口 $Port" -ForegroundColor Yellow -NoNewline
        Write-Host " ($Service): 被 $processName 佔用"
        $Script:Warnings++
    }
    else {
        Write-Host "✅ 端口 $Port" -ForegroundColor Green -NoNewline
        Write-Host " ($Service): 可用"
        $Script:Passed++
    }
}

function Test-File {
    param(
        [string]$FilePath,
        [string]$Description,
        [string]$Required = "optional"
    )
    
    $Script:Checks++
    
    if (Test-Path $FilePath) {
        Write-Host "✅ $Description" -ForegroundColor Green -NoNewline
        Write-Host ": $FilePath 存在"
        $Script:Passed++
    }
    else {
        if ($Required -eq "required") {
            Write-Host "❌ $Description" -ForegroundColor Red -NoNewline
            Write-Host ": $FilePath 不存在（必需）"
        }
        else {
            Write-Host "⚠️  $Description" -ForegroundColor Yellow -NoNewline
            Write-Host ": $FilePath 不存在（可選）"
            $Script:Warnings++
        }
    }
}

# 1. 檢查基本開發工具
Write-Host "`n📦 基本開發工具" -ForegroundColor Blue
Write-Host "--------------------------------" -ForegroundColor Blue
Test-Command "docker" "Docker" "--version"
Test-Command "docker-compose" "Docker Compose" "--version"
Test-Command "node" "Node.js" "--version"
Test-Command "npm" "NPM" "--version"
Test-Command "python" "Python 3" "--version"
Test-Command "git" "Git" "--version"

# 2. 檢查 Python 版本詳細信息
Write-Host "`n🐍 Python 環境" -ForegroundColor Blue
Write-Host "--------------------------------" -ForegroundColor Blue

try {
    $pythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>$null
    if ($pythonVersion) {
        Write-Host "✅ Python 版本" -ForegroundColor Green -NoNewline
        Write-Host ": $pythonVersion"
        
        # 檢查是否滿足最低版本要求 (3.12+)
        $versionCheck = python -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Python 版本檢查" -ForegroundColor Green -NoNewline
            Write-Host ": 滿足最低需求 (3.12+)"
        }
        else {
            Write-Host "⚠️  Python 版本檢查" -ForegroundColor Yellow -NoNewline
            Write-Host ": 建議升級至 3.12+"
            $Script:Warnings++
        }
    }
}
catch {
    Write-Host "❌ Python 版本檢查失敗" -ForegroundColor Red
}

# 3. 檢查 Docker 狀態
Write-Host "`n🐳 Docker 服務" -ForegroundColor Blue
Write-Host "--------------------------------" -ForegroundColor Blue

$Script:Checks++
try {
    docker info >$null 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker 狀態" -ForegroundColor Green -NoNewline
        Write-Host ": 正在運行"
        $Script:Passed++
        
        # 檢查 Docker Compose 檔案
        if (Test-Path "docker-compose.yml") {
            Write-Host "✅ Docker Compose 配置" -ForegroundColor Green -NoNewline
            Write-Host ": docker-compose.yml 存在"
            
            # 檢查 Docker Compose 語法
            docker-compose config >$null 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Docker Compose 語法" -ForegroundColor Green -NoNewline
                Write-Host ": 配置檔案有效"
            }
            else {
                Write-Host "❌ Docker Compose 語法" -ForegroundColor Red -NoNewline
                Write-Host ": 配置檔案有誤"
            }
        }
    }
    else {
        Write-Host "❌ Docker 狀態" -ForegroundColor Red -NoNewline
        Write-Host ": 未運行或無權限訪問"
    }
}
catch {
    Write-Host "❌ Docker 狀態" -ForegroundColor Red -NoNewline
    Write-Host ": Docker 未安裝或無法訪問"
}

# 4. 檢查端口佔用情況
Write-Host "`n🔌 端口檢查" -ForegroundColor Blue
Write-Host "--------------------------------" -ForegroundColor Blue
Test-Port 5001 "Flask 應用"
Test-Port 3306 "MySQL 資料庫"
Test-Port 8080 "phpMyAdmin"

# 5. 檢查專案檔案結構
Write-Host "`n📁 專案檔案" -ForegroundColor Blue
Write-Host "--------------------------------" -ForegroundColor Blue
Test-File ".env" "環境變數檔案" "required"
Test-File ".env.example" "環境變數範本" "required"
Test-File "docker-compose.yml" "Docker Compose 配置" "required"
Test-File "docker-compose.override.yml" "個人 Docker 配置" "optional"
Test-File "package.json" "NPM 配置" "required"
Test-File "app\requirements.txt" "Python 依賴" "required"

# 6. 檢查環境變數配置
Write-Host "`n🔑 環境變數檢查" -ForegroundColor Blue
Write-Host "--------------------------------" -ForegroundColor Blue

if (Test-Path ".env") {
    $Script:Checks += 3
    
    $envContent = Get-Content ".env" -Raw
    
    # 檢查關鍵環境變數
    if (($envContent -match "LLM_API_KEY=") -and ($envContent -notmatch "LLM_API_KEY=your_")) {
        Write-Host "✅ LLM_API_KEY" -ForegroundColor Green -NoNewline
        Write-Host ": 已配置"
        $Script:Passed++
    }
    else {
        Write-Host "⚠️  LLM_API_KEY" -ForegroundColor Yellow -NoNewline
        Write-Host ": 未配置或使用預設值"
        $Script:Warnings++
    }
    
    if ($envContent -match "DB_HOST=mysql") {
        Write-Host "✅ DB_HOST" -ForegroundColor Green -NoNewline
        Write-Host ": 正確配置為 'mysql'"
        $Script:Passed++
    }
    else {
        Write-Host "⚠️  DB_HOST" -ForegroundColor Yellow -NoNewline
        Write-Host ": 應該設為 'mysql' 用於 Docker 環境"
        $Script:Warnings++
    }
    
    if ($envContent -match "DB_PASS=rootpassword") {
        Write-Host "✅ DB_PASS" -ForegroundColor Green -NoNewline
        Write-Host ": 與 docker-compose.yml 一致"
        $Script:Passed++
    }
    else {
        Write-Host "⚠️  DB_PASS" -ForegroundColor Yellow -NoNewline
        Write-Host ": 可能與 docker-compose.yml 不一致"
        $Script:Warnings++
    }
}

# 7. 檢查 VS Code 設定
Write-Host "`n💻 VS Code 設定" -ForegroundColor Blue
Write-Host "--------------------------------" -ForegroundColor Blue
Test-File ".vscode\settings.json" "VS Code 設定" "optional"
Test-File ".vscode\extensions.json" "擴充套件建議" "optional"
Test-File ".vscode\launch.json" "除錯配置" "optional"

# 8. 檢查 Git 設定
Write-Host "`n📚 Git 設定" -ForegroundColor Blue
Write-Host "--------------------------------" -ForegroundColor Blue

$Script:Checks += 2

try {
    $gitUser = git config --get user.name 2>$null
    if ($gitUser) {
        Write-Host "✅ Git 用戶名" -ForegroundColor Green -NoNewline
        Write-Host ": $gitUser"
        $Script:Passed++
    }
    else {
        Write-Host "⚠️  Git 用戶名" -ForegroundColor Yellow -NoNewline
        Write-Host ": 未配置"
        $Script:Warnings++
    }
}
catch {
    Write-Host "⚠️  Git 用戶名" -ForegroundColor Yellow -NoNewline
    Write-Host ": 檢查失敗"
    $Script:Warnings++
}

try {
    $gitEmail = git config --get user.email 2>$null
    if ($gitEmail) {
        Write-Host "✅ Git 郵箱" -ForegroundColor Green -NoNewline
        Write-Host ": $gitEmail"
        $Script:Passed++
    }
    else {
        Write-Host "⚠️  Git 郵箱" -ForegroundColor Yellow -NoNewline
        Write-Host ": 未配置"
        $Script:Warnings++
    }
}
catch {
    Write-Host "⚠️  Git 郵箱" -ForegroundColor Yellow -NoNewline
    Write-Host ": 檢查失敗"
    $Script:Warnings++
}

# 9. 系統資訊
Write-Host "`n💽 系統資訊" -ForegroundColor Blue
Write-Host "--------------------------------" -ForegroundColor Blue

$osVersion = [System.Environment]::OSVersion.VersionString
$architecture = [System.Environment]::GetEnvironmentVariable("PROCESSOR_ARCHITECTURE")
$computerName = $env:COMPUTERNAME

Write-Host "🖥️  作業系統: $osVersion"
Write-Host "🏗️  架構: $architecture"
Write-Host "💻 電腦名稱: $computerName"

# 檢查記憶體
try {
    $memory = Get-CimInstance Win32_ComputerSystem
    $totalMemoryGB = [math]::Round($memory.TotalPhysicalMemory / 1GB, 2)
    Write-Host "💾 總記憶體: ${totalMemoryGB}GB"
}
catch {
    Write-Host "💾 記憶體資訊: 無法獲取"
}

# 10. 總結
$Failed = $Script:Checks - $Script:Passed - $Script:Warnings

Write-Host "`n📊 檢查總結" -ForegroundColor Blue
Write-Host "==================================" -ForegroundColor Blue
Write-Host "總檢查項目: $($Script:Checks)"
Write-Host "✅ 通過: $($Script:Passed)" -ForegroundColor Green
Write-Host "⚠️  警告: $($Script:Warnings)" -ForegroundColor Yellow
Write-Host "❌ 失敗: $Failed" -ForegroundColor Red

# 建議
Write-Host "`n💡 建議" -ForegroundColor Blue
Write-Host "==================================" -ForegroundColor Blue

if ($Failed -gt 0) {
    Write-Host "❗ 有關鍵組件未安裝，請參考 docs\DEVELOPMENT_SETUP.md" -ForegroundColor Red
}

if ($Script:Warnings -gt 0) {
    Write-Host "⚠️  有警告項目，建議檢查並修復" -ForegroundColor Yellow
}

if ($Failed -eq 0 -and $Script:Warnings -eq 0) {
    Write-Host "🎉 環境檢查完全通過！可以開始開發了" -ForegroundColor Green
}
elseif ($Failed -eq 0) {
    Write-Host "✅ 基本環境正常，建議處理警告項目" -ForegroundColor Green
}

Write-Host "`n📖 詳細設置指南: docs\DEVELOPMENT_SETUP.md"
Write-Host "🚀 啟動專案: docker-compose up --build"

# 返回適當的退出碼
if ($Failed -gt 0) {
    exit 1
}
else {
    exit 0
}