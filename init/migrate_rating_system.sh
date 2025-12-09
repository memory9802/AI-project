#!/bin/bash

# ============================================================
# 評分權重系統資料庫遷移執行腳本
# ============================================================
# 專案: stylerec 穿搭推薦系統
# 日期: 2025-12-09
# 用途: 自動化執行資料庫遷移和測試資料插入
# ============================================================

set -e  # 遇到錯誤立即停止

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Docker 容器和資料庫配置
CONTAINER_NAME="outfit-mysql"
DB_NAME="outfit_db"
DB_USER="root"
DB_PASSWORD="rootpassword"

# 腳本路徑
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATION_SQL="$SCRIPT_DIR/migration_rating_system.sql"
DEMO_DATA_SQL="$SCRIPT_DIR/demo_test_data.sql"
BACKUP_DIR="$SCRIPT_DIR/../backups"

# ============================================================
# 函數定義
# ============================================================

print_header() {
    echo -e "${BLUE}"
    echo "============================================================"
    echo "$1"
    echo "============================================================"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 檢查 Docker 容器是否運行
check_docker() {
    print_header "檢查 Docker 容器狀態"
    
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        print_error "Docker 容器 $CONTAINER_NAME 未運行!"
        print_info "請先啟動容器: docker-compose up -d"
        exit 1
    fi
    
    print_success "Docker 容器 $CONTAINER_NAME 正在運行"
}

# 檢查 SQL 腳本是否存在
check_scripts() {
    print_header "檢查 SQL 腳本"
    
    if [ ! -f "$MIGRATION_SQL" ]; then
        print_error "找不到遷移腳本: $MIGRATION_SQL"
        exit 1
    fi
    print_success "遷移腳本存在: $MIGRATION_SQL"
    
    if [ ! -f "$DEMO_DATA_SQL" ]; then
        print_error "找不到測試資料腳本: $DEMO_DATA_SQL"
        exit 1
    fi
    print_success "測試資料腳本存在: $DEMO_DATA_SQL"
}

# 備份資料庫
backup_database() {
    print_header "備份資料庫"
    
    # 建立備份目錄
    mkdir -p "$BACKUP_DIR"
    
    # 生成備份檔案名稱 (包含時間戳記)
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_FILE="$BACKUP_DIR/outfit_db_backup_$TIMESTAMP.sql"
    
    print_info "開始備份資料庫到: $BACKUP_FILE"
    
    if docker exec "$CONTAINER_NAME" mysqldump -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" > "$BACKUP_FILE" 2>/dev/null; then
        print_success "資料庫備份完成: $BACKUP_FILE"
        
        # 顯示備份檔案大小
        BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        print_info "備份檔案大小: $BACKUP_SIZE"
    else
        print_error "資料庫備份失敗!"
        exit 1
    fi
}

# 執行遷移腳本
run_migration() {
    print_header "執行資料庫遷移"
    
    print_info "正在執行遷移腳本..."
    
    if docker exec -i "$CONTAINER_NAME" mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$MIGRATION_SQL" 2>&1 | tee /tmp/migration.log; then
        print_success "資料庫遷移完成!"
    else
        print_error "資料庫遷移失敗!請檢查錯誤訊息"
        print_info "錯誤日誌: /tmp/migration.log"
        exit 1
    fi
}

# 執行測試資料插入
run_demo_data() {
    print_header "插入 Demo 測試資料"
    
    print_info "正在插入測試資料..."
    
    if docker exec -i "$CONTAINER_NAME" mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$DEMO_DATA_SQL" 2>&1 | tee /tmp/demo_data.log; then
        print_success "測試資料插入完成!"
    else
        print_error "測試資料插入失敗!請檢查錯誤訊息"
        print_info "錯誤日誌: /tmp/demo_data.log"
        exit 1
    fi
}

# 驗證資料庫結構
verify_database() {
    print_header "驗證資料庫結構"
    
    # 檢查 rating 表格
    print_info "檢查 rating 表格..."
    RATING_CHECK=$(docker exec "$CONTAINER_NAME" mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SHOW TABLES LIKE 'rating';" 2>/dev/null | grep -c rating || echo 0)
    
    if [ "$RATING_CHECK" -eq 1 ]; then
        print_success "rating 表格存在"
        
        # 顯示表格結構
        docker exec "$CONTAINER_NAME" mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "DESCRIBE rating;" 2>/dev/null
    else
        print_error "rating 表格不存在!"
        exit 1
    fi
    
    # 檢查 item_stats 表格
    print_info "檢查 item_stats 表格..."
    STATS_CHECK=$(docker exec "$CONTAINER_NAME" mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SHOW TABLES LIKE 'item_stats';" 2>/dev/null | grep -c item_stats || echo 0)
    
    if [ "$STATS_CHECK" -eq 1 ]; then
        print_success "item_stats 表格存在"
    else
        print_error "item_stats 表格不存在!"
        exit 1
    fi
    
    # 檢查視圖
    print_info "檢查視圖..."
    VIEW_COUNT=$(docker exec "$CONTAINER_NAME" mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SHOW FULL TABLES WHERE Table_type = 'VIEW';" 2>/dev/null | grep -c rating || echo 0)
    print_success "找到 $VIEW_COUNT 個評分相關視圖"
    
    # 檢查觸發器
    print_info "檢查觸發器..."
    TRIGGER_COUNT=$(docker exec "$CONTAINER_NAME" mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SHOW TRIGGERS WHERE \`Table\` = 'rating';" 2>/dev/null | grep -c rating || echo 0)
    print_success "找到 $TRIGGER_COUNT 個觸發器"
}

# 顯示統計資料
show_statistics() {
    print_header "資料庫統計"
    
    print_info "評分統計:"
    docker exec "$CONTAINER_NAME" mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "
        SELECT 
            item_source,
            COUNT(*) as rating_count,
            AVG(rating_value) as avg_rating,
            MIN(rating_value) as min_rating,
            MAX(rating_value) as max_rating
        FROM rating
        GROUP BY item_source;
    " 2>/dev/null
    
    print_info "統計表記錄數:"
    docker exec "$CONTAINER_NAME" mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "
        SELECT 
            item_source,
            COUNT(*) as stats_count,
            AVG(avg_rating) as overall_avg
        FROM item_stats
        GROUP BY item_source;
    " 2>/dev/null
    
    print_info "測試商品數:"
    docker exec "$CONTAINER_NAME" mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "
        SELECT COUNT(*) as demo_items_count 
        FROM items 
        WHERE is_demo = TRUE;
    " 2>/dev/null
}

# 測試查詢
test_queries() {
    print_header "測試帶權重的查詢"
    
    print_info "測試無權重推薦 (隨機 5 件):"
    docker exec "$CONTAINER_NAME" mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "
        SELECT 
            id,
            name,
            COALESCE(avg_rating, 0) as avg_rating,
            COALESCE(rating_count, 0) as rating_count
        FROM v_items_with_ratings
        WHERE is_demo = TRUE
        ORDER BY RAND()
        LIMIT 5;
    " 2>/dev/null
    
    print_info "測試有權重推薦 (評分優先 5 件):"
    docker exec "$CONTAINER_NAME" mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "
        SELECT 
            id,
            name,
            avg_rating,
            rating_count,
            rating_weight,
            popularity_weight,
            final_score
        FROM v_items_with_ratings
        WHERE is_demo = TRUE
        ORDER BY final_score DESC
        LIMIT 5;
    " 2>/dev/null
}

# ============================================================
# 主程式
# ============================================================

main() {
    echo ""
    print_header "🚀 評分權重系統資料庫遷移腳本"
    echo ""
    
    # 步驟 1: 檢查環境
    check_docker
    check_scripts
    
    # 步驟 2: 備份資料庫
    backup_database
    
    # 步驟 3: 執行遷移
    run_migration
    
    # 步驟 4: 插入測試資料
    print_info "是否要插入 Demo 測試資料? (y/n)"
    read -r RESPONSE
    if [[ "$RESPONSE" =~ ^[Yy]$ ]]; then
        run_demo_data
    else
        print_warning "跳過測試資料插入"
    fi
    
    # 步驟 5: 驗證結果
    verify_database
    
    # 步驟 6: 顯示統計
    show_statistics
    
    # 步驟 7: 測試查詢
    test_queries
    
    # 完成
    echo ""
    print_header "✅ 資料庫遷移完成!"
    echo ""
    print_success "接下來的步驟:"
    echo "  1. 開發後端 API (rating_service.py)"
    echo "  2. 更新 API 路由 (routes.py)"
    echo "  3. 前端整合評分按鈕"
    echo "  4. 測試完整流程"
    echo ""
}

# 執行主程式
main
