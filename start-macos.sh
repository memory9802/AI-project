#!/bin/bash
# ====================================
# macOS 快速啟動腳本
# ====================================
# 使用方式: 在 Terminal 中執行
# chmod +x start-macos.sh
# ./start-macos.sh
# ====================================

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

echo -e "${CYAN}=====================================${NC}"
echo -e "${CYAN}  穿搭推薦 AI 專案 - macOS 啟動    ${NC}"
echo -e "${CYAN}=====================================${NC}"
echo ""

# 檢查 Docker Desktop 是否運行
echo -e "${YELLOW}[1/6] 檢查 Docker Desktop...${NC}"
if ! pgrep -x "Docker" > /dev/null; then
    echo -e "${RED}❌ Docker Desktop 未運行!${NC}"
    echo -e "${RED}請先啟動 Docker Desktop,然後重新執行此腳本${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Desktop 正在運行${NC}"
echo ""

# 檢查 docker 指令
echo -e "${YELLOW}[2/6] 檢查 Docker 指令...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ docker 指令不可用!${NC}"
    echo -e "${RED}請確保 Docker Desktop 已正確安裝${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker 指令可用${NC}"
echo ""

# 檢查 .env 檔案
echo -e "${YELLOW}[3/6] 檢查環境變數檔案...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env 檔案不存在!${NC}"
    echo -e "${YELLOW}正在從 .env.example 建立 .env...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env 檔案已建立,請檢查並填入正確的 API Key${NC}"
else
    echo -e "${GREEN}✅ .env 檔案存在${NC}"
fi
echo ""

# 檢查端口佔用
echo -e "${YELLOW}[4/6] 檢查端口佔用...${NC}"
PORTS=(5001 3306 8080)
PORTS_IN_USE=()

for port in "${PORTS[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        PORTS_IN_USE+=($port)
    fi
done

if [ ${#PORTS_IN_USE[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  以下端口被佔用: ${PORTS_IN_USE[*]}${NC}"
    echo -e "${YELLOW}如果是舊容器佔用,將會被停止${NC}"
else
    echo -e "${GREEN}✅ 所有端口都可用${NC}"
fi
echo ""

# 停止舊容器
echo -e "${YELLOW}[5/6] 停止舊容器...${NC}"
docker compose down >/dev/null 2>&1
echo -e "${GREEN}✅ 舊容器已停止${NC}"
echo ""

# 重建並啟動容器
echo -e "${YELLOW}[6/6] 重建並啟動容器 (這可能需要 1-2 分鐘)...${NC}"
if ! docker compose up -d --build; then
    echo -e "${RED}❌ 容器啟動失敗!${NC}"
    echo -e "${RED}請檢查 Docker Desktop 日誌${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 容器啟動成功${NC}"
echo ""

# 等待服務就緒
echo -e "${YELLOW}等待服務就緒 (15 秒)...${NC}"
sleep 15

# 測試服務
echo ""
echo -e "${CYAN}=====================================${NC}"
echo -e "${CYAN}  測試服務狀態                       ${NC}"
echo -e "${CYAN}=====================================${NC}"
echo ""

# 測試 Flask API
echo -e "${YELLOW}測試 Flask API...${NC}"
if curl -s -f http://localhost:5001/ping > /tmp/ping_response.json 2>&1; then
    echo -e "${GREEN}✅ Flask API 運行正常${NC}"
    
    # 解析 JSON 回應
    if command -v python3 &> /dev/null; then
        STATUS=$(python3 -c "import json; print(json.load(open('/tmp/ping_response.json'))['status'])" 2>/dev/null)
        AI_ENABLED=$(python3 -c "import json; print(json.load(open('/tmp/ping_response.json'))['ai_enabled'])" 2>/dev/null)
        MODEL=$(python3 -c "import json; print(json.load(open('/tmp/ping_response.json'))['gemini_model'])" 2>/dev/null)
        
        echo -e "${GRAY}   - 狀態: $STATUS${NC}"
        echo -e "${GRAY}   - AI 啟用: $AI_ENABLED${NC}"
        echo -e "${GRAY}   - 模型: $MODEL${NC}"
    fi
else
    echo -e "${RED}❌ Flask API 無法連線${NC}"
fi
echo ""

# 測試 MySQL
echo -e "${YELLOW}測試 MySQL...${NC}"
if docker exec outfit-mysql mysql -u root -prootpassword -e "SELECT 1" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ MySQL 運行正常${NC}"
else
    echo -e "${RED}❌ MySQL 連線失敗${NC}"
fi
echo ""

# 顯示容器狀態
echo -e "${CYAN}=====================================${NC}"
echo -e "${CYAN}  容器狀態                           ${NC}"
echo -e "${CYAN}=====================================${NC}"
docker compose ps
echo ""

# 顯示存取資訊
echo -e "${CYAN}=====================================${NC}"
echo -e "${CYAN}  服務存取資訊                       ${NC}"
echo -e "${CYAN}=====================================${NC}"
echo -e "${GREEN}🌐 網站主頁:     http://localhost:5001${NC}"
echo -e "${GREEN}🤖 AI API:       http://localhost:5001/recommend${NC}"
echo -e "${GREEN}🗄️  phpMyAdmin:  http://localhost:8080${NC}"
echo -e "${GRAY}   (帳號: root / 密碼: rootpassword)${NC}"
echo ""

# 顯示常用指令
echo -e "${CYAN}=====================================${NC}"
echo -e "${CYAN}  常用指令                           ${NC}"
echo -e "${CYAN}=====================================${NC}"
echo -e "${YELLOW}查看日誌:       docker compose logs -f flask${NC}"
echo -e "${YELLOW}停止服務:       docker compose down${NC}"
echo -e "${YELLOW}重啟服務:       docker compose restart${NC}"
echo -e "${YELLOW}重建容器:       docker compose up -d --build${NC}"
echo ""

echo -e "${GREEN}✨ 啟動完成! 可以開始使用了${NC}"
echo ""

# 清理臨時檔案
rm -f /tmp/ping_response.json
