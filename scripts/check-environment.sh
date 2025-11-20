#!/bin/bash

# AI 專案環境檢查腳本 - macOS/Linux 版本
# 此腳本會檢查開發環境的必要組件和配置

echo "🔍 AI 專案環境檢查開始..."
echo "=================================="

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 檢查結果計數
CHECKS=0
PASSED=0
WARNINGS=0

# 輔助函數
check_command() {
    local cmd="$1"
    local name="$2"
    local version_flag="$3"
    
    CHECKS=$((CHECKS + 1))
    
    if command -v "$cmd" >/dev/null 2>&1; then
        local version
        if [ -n "$version_flag" ]; then
            version=$($cmd $version_flag 2>/dev/null | head -n1)
        else
            version="已安裝"
        fi
        echo -e "✅ ${GREEN}$name${NC}: $version"
        PASSED=$((PASSED + 1))
    else
        echo -e "❌ ${RED}$name${NC}: 未安裝或不在 PATH 中"
    fi
}

check_port() {
    local port="$1"
    local service="$2"
    
    CHECKS=$((CHECKS + 1))
    
    if lsof -i:$port >/dev/null 2>&1; then
        local process=$(lsof -ti:$port | head -1)
        local proc_name=$(ps -p $process -o comm= 2>/dev/null || echo "未知進程")
        echo -e "⚠️  ${YELLOW}端口 $port${NC} ($service): 被 $proc_name 佔用"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "✅ ${GREEN}端口 $port${NC} ($service): 可用"
        PASSED=$((PASSED + 1))
    fi
}

check_file() {
    local file="$1"
    local description="$2"
    local required="$3"
    
    CHECKS=$((CHECKS + 1))
    
    if [ -f "$file" ]; then
        echo -e "✅ ${GREEN}$description${NC}: $file 存在"
        PASSED=$((PASSED + 1))
    else
        if [ "$required" = "required" ]; then
            echo -e "❌ ${RED}$description${NC}: $file 不存在（必需）"
        else
            echo -e "⚠️  ${YELLOW}$description${NC}: $file 不存在（可選）"
            WARNINGS=$((WARNINGS + 1))
        fi
    fi
}

# 1. 檢查基本開發工具
echo -e "\n${BLUE}📦 基本開發工具${NC}"
echo "--------------------------------"
check_command "docker" "Docker" "--version"
check_command "docker-compose" "Docker Compose" "--version"
check_command "node" "Node.js" "--version"
check_command "npm" "NPM" "--version"
check_command "python3" "Python 3" "--version"
check_command "git" "Git" "--version"

# 2. 檢查 Python 版本詳細信息
echo -e "\n${BLUE}🐍 Python 環境${NC}"
echo "--------------------------------"
if command -v python3 >/dev/null 2>&1; then
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
    echo -e "✅ ${GREEN}Python 版本${NC}: $python_version"
    
    # 檢查是否滿足最低版本要求 (3.12+)
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)"; then
        echo -e "✅ ${GREEN}Python 版本檢查${NC}: 滿足最低需求 (3.12+)"
    else
        echo -e "⚠️  ${YELLOW}Python 版本檢查${NC}: 建議升級至 3.12+"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

# 3. 檢查 Docker 狀態
echo -e "\n${BLUE}🐳 Docker 服務${NC}"
echo "--------------------------------"
CHECKS=$((CHECKS + 1))
if docker info >/dev/null 2>&1; then
    echo -e "✅ ${GREEN}Docker 狀態${NC}: 正在運行"
    PASSED=$((PASSED + 1))
    
    # 檢查 Docker Compose 檔案
    if [ -f "docker-compose.yml" ]; then
        echo -e "✅ ${GREEN}Docker Compose 配置${NC}: docker-compose.yml 存在"
        
        # 檢查 Docker Compose 語法
        if docker-compose config >/dev/null 2>&1; then
            echo -e "✅ ${GREEN}Docker Compose 語法${NC}: 配置檔案有效"
        else
            echo -e "❌ ${RED}Docker Compose 語法${NC}: 配置檔案有誤"
        fi
    fi
else
    echo -e "❌ ${RED}Docker 狀態${NC}: 未運行或無權限訪問"
fi

# 4. 檢查端口佔用情況
echo -e "\n${BLUE}🔌 端口檢查${NC}"
echo "--------------------------------"
check_port 5001 "Flask 應用"
check_port 3306 "MySQL 資料庫"
check_port 8080 "phpMyAdmin"

# 5. 檢查專案檔案結構
echo -e "\n${BLUE}📁 專案檔案${NC}"
echo "--------------------------------"
check_file ".env" "環境變數檔案" "required"
check_file ".env.example" "環境變數範本" "required"
check_file "docker-compose.yml" "Docker Compose 配置" "required"
check_file "docker-compose.override.yml" "個人 Docker 配置" "optional"
check_file "package.json" "NPM 配置" "required"
check_file "app/requirements.txt" "Python 依賴" "required"

# 6. 檢查環境變數配置
echo -e "\n${BLUE}🔑 環境變數檢查${NC}"
echo "--------------------------------"
if [ -f ".env" ]; then
    CHECKS=$((CHECKS + 3))
    
    # 檢查關鍵環境變數
    if grep -q "LLM_API_KEY=" .env && ! grep -q "LLM_API_KEY=your_" .env; then
        echo -e "✅ ${GREEN}LLM_API_KEY${NC}: 已配置"
        PASSED=$((PASSED + 1))
    else
        echo -e "⚠️  ${YELLOW}LLM_API_KEY${NC}: 未配置或使用預設值"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    if grep -q "DB_HOST=mysql" .env; then
        echo -e "✅ ${GREEN}DB_HOST${NC}: 正確配置為 'mysql'"
        PASSED=$((PASSED + 1))
    else
        echo -e "⚠️  ${YELLOW}DB_HOST${NC}: 應該設為 'mysql' 用於 Docker 環境"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    if grep -q "DB_PASS=rootpassword" .env; then
        echo -e "✅ ${GREEN}DB_PASS${NC}: 與 docker-compose.yml 一致"
        PASSED=$((PASSED + 1))
    else
        echo -e "⚠️  ${YELLOW}DB_PASS${NC}: 可能與 docker-compose.yml 不一致"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

# 7. 檢查 VS Code 設定
echo -e "\n${BLUE}💻 VS Code 設定${NC}"
echo "--------------------------------"
check_file ".vscode/settings.json" "VS Code 設定" "optional"
check_file ".vscode/extensions.json" "擴充套件建議" "optional"
check_file ".vscode/launch.json" "除錯配置" "optional"

# 8. 檢查 Git 設定
echo -e "\n${BLUE}📚 Git 設定${NC}"
echo "--------------------------------"
CHECKS=$((CHECKS + 2))

git_user=$(git config --get user.name 2>/dev/null)
git_email=$(git config --get user.email 2>/dev/null)

if [ -n "$git_user" ]; then
    echo -e "✅ ${GREEN}Git 用戶名${NC}: $git_user"
    PASSED=$((PASSED + 1))
else
    echo -e "⚠️  ${YELLOW}Git 用戶名${NC}: 未配置"
    WARNINGS=$((WARNINGS + 1))
fi

if [ -n "$git_email" ]; then
    echo -e "✅ ${GREEN}Git 郵箱${NC}: $git_email"
    PASSED=$((PASSED + 1))
else
    echo -e "⚠️  ${YELLOW}Git 郵箱${NC}: 未配置"
    WARNINGS=$((WARNINGS + 1))
fi

# 9. 系統資訊
echo -e "\n${BLUE}💽 系統資訊${NC}"
echo "--------------------------------"
echo -e "🖥️  ${BLUE}作業系統${NC}: $(uname -s) $(uname -r)"
echo -e "🏗️  ${BLUE}架構${NC}: $(uname -m)"

if command -v sw_vers >/dev/null 2>&1; then
    echo -e "🍎 ${BLUE}macOS 版本${NC}: $(sw_vers -productVersion)"
fi

# 檢查記憶體（macOS）
if command -v vm_stat >/dev/null 2>&1; then
    mem_info=$(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
    if [ -n "$mem_info" ] && [ "$mem_info" -gt 0 ]; then
        free_gb=$((mem_info * 4096 / 1024 / 1024 / 1024))
        echo -e "💾 ${BLUE}可用記憶體${NC}: 約 ${free_gb}GB"
    fi
fi

# 10. 總結
echo -e "\n${BLUE}📊 檢查總結${NC}"
echo "=================================="
echo -e "總檢查項目: $CHECKS"
echo -e "✅ ${GREEN}通過: $PASSED${NC}"
echo -e "⚠️  ${YELLOW}警告: $WARNINGS${NC}"
echo -e "❌ ${RED}失敗: $((CHECKS - PASSED - WARNINGS))${NC}"

# 建議
echo -e "\n${BLUE}💡 建議${NC}"
echo "=================================="

if [ $((CHECKS - PASSED - WARNINGS)) -gt 0 ]; then
    echo -e "❗ 有關鍵組件未安裝，請參考 docs/DEVELOPMENT_SETUP.md"
fi

if [ $WARNINGS -gt 0 ]; then
    echo -e "⚠️  有警告項目，建議檢查並修復"
fi

if [ $((CHECKS - PASSED - WARNINGS)) -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "🎉 ${GREEN}環境檢查完全通過！可以開始開發了${NC}"
elif [ $((CHECKS - PASSED - WARNINGS)) -eq 0 ]; then
    echo -e "✅ ${GREEN}基本環境正常，建議處理警告項目${NC}"
fi

echo -e "\n📖 詳細設置指南: docs/DEVELOPMENT_SETUP.md"
echo -e "🚀 啟動專案: docker-compose up --build"

# 返回適當的退出碼
if [ $((CHECKS - PASSED - WARNINGS)) -gt 0 ]; then
    exit 1
else
    exit 0
fi