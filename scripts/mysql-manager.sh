#!/bin/bash

# =====================================
# MySQL 自訂建置快速操作腳本
# 解決 macOS 檔案權限問題的管理工具
# =====================================

set -e  # 錯誤時退出

echo "🐳 MySQL 自訂建置管理工具"
echo "============================="

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函數：顯示使用說明
show_help() {
    echo "使用方式："
    echo "  $0 [命令]"
    echo ""
    echo "可用命令："
    echo "  build     - 建置 MySQL 自訂映像"
    echo "  start     - 啟動 MySQL 服務"
    echo "  restart   - 重啟 MySQL 服務"
    echo "  reset     - 重置資料庫 (刪除資料卷)"
    echo "  logs      - 查看 MySQL 日誌"
    echo "  connect   - 連線到 MySQL"
    echo "  status    - 查看服務狀態"
    echo "  help      - 顯示此說明"
}

# 函數：建置映像
build_mysql() {
    echo -e "${YELLOW}🔨 建置 MySQL 自訂映像...${NC}"
    docker-compose build --no-cache mysql
    echo -e "${GREEN}✅ MySQL 映像建置完成${NC}"
}

# 函數：啟動服務
start_mysql() {
    echo -e "${YELLOW}🚀 啟動 MySQL 服務...${NC}"
    docker-compose up -d mysql
    echo -e "${GREEN}✅ MySQL 服務已啟動${NC}"
    
    # 等待服務準備就緒
    echo -e "${YELLOW}⏳ 等待服務準備就緒...${NC}"
    sleep 5
    
    # 檢查服務狀態
    if docker ps --filter "name=outfit-mysql" --filter "status=running" | grep -q outfit-mysql; then
        echo -e "${GREEN}✅ MySQL 服務運行正常${NC}"
    else
        echo -e "${RED}❌ MySQL 服務啟動失敗${NC}"
        exit 1
    fi
}

# 函數：重啟服務
restart_mysql() {
    echo -e "${YELLOW}🔄 重啟 MySQL 服務...${NC}"
    docker-compose restart mysql
    echo -e "${GREEN}✅ MySQL 服務已重啟${NC}"
}

# 函數：重置資料庫
reset_mysql() {
    echo -e "${RED}⚠️  警告：此操作將刪除所有資料庫資料！${NC}"
    read -p "確定要繼續嗎？(y/N): " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🗑️  停止並移除容器...${NC}"
        docker-compose down mysql
        
        echo -e "${YELLOW}🗑️  刪除資料卷...${NC}"
        docker volume rm ai-project_mysql_data 2>/dev/null || true
        
        echo -e "${YELLOW}🔨 重新建置並啟動...${NC}"
        build_mysql
        start_mysql
        
        echo -e "${GREEN}✅ 資料庫已重置完成${NC}"
    else
        echo -e "${YELLOW}❌ 操作已取消${NC}"
    fi
}

# 函數：查看日誌
show_logs() {
    echo -e "${YELLOW}📋 MySQL 服務日誌：${NC}"
    docker logs outfit-mysql --tail 30 -f
}

# 函數：連線資料庫
connect_mysql() {
    echo -e "${YELLOW}🔌 連線到 MySQL...${NC}"
    docker exec -it outfit-mysql mysql -u root -prootpassword outfit_db
}

# 函數：查看狀態
show_status() {
    echo -e "${YELLOW}📊 服務狀態：${NC}"
    docker ps --filter "name=outfit-mysql" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo -e "\n${YELLOW}📦 映像資訊：${NC}"
    docker images | grep -E "(ai-project-mysql|mysql)" | head -5
    
    echo -e "\n${YELLOW}💾 資料卷：${NC}"
    docker volume ls | grep mysql_data
}

# 主邏輯
case "${1:-help}" in
    "build")
        build_mysql
        ;;
    "start")
        start_mysql
        ;;
    "restart")
        restart_mysql
        ;;
    "reset")
        reset_mysql
        ;;
    "logs")
        show_logs
        ;;
    "connect")
        connect_mysql
        ;;
    "status")
        show_status
        ;;
    "help"|*)
        show_help
        ;;
esac