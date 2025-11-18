# Port 管理腳本 - 快速切換不同 port 配置

param(
    [Parameter(Position=0)]
    [ValidateSet('dev-a', 'dev-b', 'dev-c', 'auto', 'custom', 'list', 'stop')]
    [string]$Profile = 'list'
)

$ErrorActionPreference = "Stop"

# 配置定義
$profiles = @{
    'dev-a' = @{
        FLASK_PORT = 5001
        MYSQL_PORT = 3306
        PHPMYADMIN_PORT = 8080
        CONTAINER_PREFIX = 'dev-a'
        Description = '開發者 A'
    }
    'dev-b' = @{
        FLASK_PORT = 5002
        MYSQL_PORT = 3307
        PHPMYADMIN_PORT = 8081
        CONTAINER_PREFIX = 'dev-b'
        Description = '開發者 B'
    }
    'dev-c' = @{
        FLASK_PORT = 5003
        MYSQL_PORT = 3308
        PHPMYADMIN_PORT = 8082
        CONTAINER_PREFIX = 'dev-c'
        Description = '開發者 C'
    }
}

function Show-Banner {
    Write-Host @"
╔════════════════════════════════════════╗
║   AI-Project Port 管理工具            ║
╚════════════════════════════════════════╝
"@ -ForegroundColor Cyan
}

function Show-Profiles {
    Write-Host "`n可用的配置：`n" -ForegroundColor Yellow
    foreach ($key in $profiles.Keys | Sort-Object) {
        $p = $profiles[$key]
        Write-Host "  [$key]" -ForegroundColor Green -NoNewline
        Write-Host " - $($p.Description)"
        Write-Host "    Flask: $($p.FLASK_PORT) | MySQL: $($p.MYSQL_PORT) | phpMyAdmin: $($p.PHPMYADMIN_PORT)" -ForegroundColor Gray
    }
    Write-Host "`n其他選項：`n" -ForegroundColor Yellow
    Write-Host "  [auto]   - 使用 Docker 自動分配 port" -ForegroundColor Green
    Write-Host "  [custom] - 自訂 port" -ForegroundColor Green
    Write-Host "  [stop]   - 停止所有容器" -ForegroundColor Green
    Write-Host ""
}

function Start-Profile {
    param($ProfileName)
    
    $config = $profiles[$ProfileName]
    
    Write-Host "`n🚀 啟動配置: $ProfileName ($($config.Description))" -ForegroundColor Cyan
    Write-Host "   Flask:      http://localhost:$($config.FLASK_PORT)" -ForegroundColor White
    Write-Host "   phpMyAdmin: http://localhost:$($config.PHPMYADMIN_PORT)" -ForegroundColor White
    Write-Host ""
    
    # 設定環境變數
    $env:FLASK_PORT = $config.FLASK_PORT
    $env:MYSQL_PORT = $config.MYSQL_PORT
    $env:PHPMYADMIN_PORT = $config.PHPMYADMIN_PORT
    $env:CONTAINER_PREFIX = $config.CONTAINER_PREFIX
    
    # 啟動
    Write-Host "正在啟動容器..." -ForegroundColor Yellow
    docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ 啟動成功！" -ForegroundColor Green
        Write-Host "`n查看狀態：" -ForegroundColor Cyan
        Start-Sleep -Seconds 2
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Select-String "outfit|dev-"
    } else {
        Write-Host "`n❌ 啟動失敗" -ForegroundColor Red
    }
}

function Start-AutoPort {
    Write-Host "`n🎲 使用自動 port 分配模式" -ForegroundColor Cyan
    Write-Host "   Docker 會自動選擇可用的 port`n" -ForegroundColor Gray
    
    docker-compose -f docker-compose.auto-port.yml up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ 啟動成功！查看分配的 port：`n" -ForegroundColor Green
        Start-Sleep -Seconds 2
        docker ps --format "table {{.Names}}\t{{.Ports}}" | Select-String "outfit"
    }
}

function Start-CustomPort {
    Write-Host "`n🔧 自訂 port 配置`n" -ForegroundColor Cyan
    
    $flaskPort = Read-Host "Flask Port (預設 5001)"
    if ([string]::IsNullOrWhiteSpace($flaskPort)) { $flaskPort = "5001" }
    
    $mysqlPort = Read-Host "MySQL Port (預設 3306)"
    if ([string]::IsNullOrWhiteSpace($mysqlPort)) { $mysqlPort = "3306" }
    
    $phpMyAdminPort = Read-Host "phpMyAdmin Port (預設 8080)"
    if ([string]::IsNullOrWhiteSpace($phpMyAdminPort)) { $phpMyAdminPort = "8080" }
    
    $prefix = Read-Host "容器前綴 (選填)"
    
    $env:FLASK_PORT = $flaskPort
    $env:MYSQL_PORT = $mysqlPort
    $env:PHPMYADMIN_PORT = $phpMyAdminPort
    $env:CONTAINER_PREFIX = $prefix
    
    Write-Host "`n正在啟動..." -ForegroundColor Yellow
    docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ 啟動成功！" -ForegroundColor Green
    }
}

function Stop-Containers {
    Write-Host "`n🛑 停止所有容器..." -ForegroundColor Yellow
    docker-compose down
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ 已停止所有容器" -ForegroundColor Green
    }
}

# 主邏輯
Show-Banner

switch ($Profile) {
    'list' {
        Show-Profiles
    }
    'auto' {
        Start-AutoPort
    }
    'custom' {
        Start-CustomPort
    }
    'stop' {
        Stop-Containers
    }
    default {
        if ($profiles.ContainsKey($Profile)) {
            Start-Profile $Profile
        } else {
            Write-Host "❌ 未知的配置: $Profile" -ForegroundColor Red
            Show-Profiles
        }
    }
}

# 使用範例：
# .\manage-ports.ps1           # 顯示所有可用配置
# .\manage-ports.ps1 dev-a     # 使用 dev-a 配置啟動
# .\manage-ports.ps1 dev-b     # 使用 dev-b 配置啟動
# .\manage-ports.ps1 auto      # 自動分配 port
# .\manage-ports.ps1 custom    # 自訂 port
# .\manage-ports.ps1 stop      # 停止所有容器
