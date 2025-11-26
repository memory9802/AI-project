#!/bin/bash
# ========================================
# 爬蟲組員專用:一鍵上傳資料腳本
# ========================================
# 
# ⚠️ 重要規則:
#   - 統一匯出到: init/outfit_db_with_data.sql
#   - 不要改檔名! Git 會處理版本控制
# 
# 口訣: 爬完 → 匯出 → Commit → Push → 通知
# 
# ========================================

echo "╔════════════════════════════════════════════╗"
echo "║  🕷️  爬蟲資料上傳助手                      ║"
echo "║  📄 統一匯出: outfit_db_with_data.sql     ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# 檢查是否在專案根目錄
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 錯誤:請在專案根目錄執行此腳本"
    echo "   cd /path/to/AI-project-crawler-test"
    exit 1
fi

# 檢查 Docker 是否運行
if ! docker ps | grep -q outfit-mysql; then
    echo "❌ 錯誤: outfit-mysql 容器未運行"
    echo "   請執行: docker-compose up -d"
    exit 1
fi

echo "步驟 1/5: 檢查資料庫內容"
echo "────────────────────────────────"
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT '📊 當前資料統計' as info;
SELECT '' as blank;
SELECT source, COUNT(*) as count FROM items GROUP BY source ORDER BY count DESC;
" 2>/dev/null

echo ""
read -p "❓ 確認以上資料無誤,要繼續匯出嗎? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消"
    exit 0
fi

echo ""
echo "步驟 2/5: 匯出資料庫"
echo "────────────────────────────────"
docker exec outfit-mysql mysqldump \
  -uroot -prootpassword \
  --databases outfit_db \
  --no-create-db \
  --single-transaction \
  --default-character-set=utf8mb4 \
  > init/outfit_db_with_data.sql 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ 匯出失敗"
    exit 1
fi

echo "✅ 匯出完成"

echo ""
echo "步驟 3/5: 檢查檔案"
echo "────────────────────────────────"
FILE_SIZE=$(ls -lh init/outfit_db_with_data.sql | awk '{print $5}')
INSERT_COUNT=$(grep -c "INSERT INTO" init/outfit_db_with_data.sql)

echo "檔案大小: $FILE_SIZE"
echo "INSERT 語句數量: $INSERT_COUNT"

if [ "$INSERT_COUNT" -eq 0 ]; then
    echo "⚠️  警告:沒有 INSERT 語句,檔案可能有問題"
    read -p "是否繼續? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

echo ""
echo "步驟 4/5: Git 提交"
echo "────────────────────────────────"

# 檢查 Git 狀態
if ! git diff --quiet init/outfit_db_with_data.sql 2>/dev/null; then
    echo "📝 outfit_db_with_data.sql 有變更"
    
    echo ""
    read -p "📝 請輸入 commit message (例: 新增 500 個 H&M 商品): " COMMIT_MSG
    
    if [ -z "$COMMIT_MSG" ]; then
        COMMIT_MSG="更新資料庫"
    fi
    
    # Git 操作
    git add init/outfit_db_with_data.sql
    git commit -m "更新資料庫: $COMMIT_MSG"
    
    echo ""
    read -p "是否要 push 到 GitHub? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin Crawler&Detection
        
        if [ $? -eq 0 ]; then
            echo "✅ 已 push 到 GitHub"
        else
            echo "❌ Push 失敗,請檢查網路或權限"
            exit 1
        fi
    else
        echo "⏸️  稍後請手動執行: git push origin Crawler&Detection"
    fi
else
    echo "ℹ️  資料庫沒有變更,無需提交"
fi

echo ""
echo "步驟 5/5: 生成通知訊息"
echo "────────────────────────────────"
echo ""
echo "請複製以下訊息,傳送給組員:"
echo ""
echo "┌─────────────────────────────────────────┐"
echo "│ 📢 資料庫已更新!                         │"
echo "│                                         │"
echo "│ 更新內容: $COMMIT_MSG"
echo "│                                         │"
echo "│ 請執行以下指令同步:                      │"
echo "│ 1. git pull origin Crawler&Detection   │"
echo "│ 2. docker exec -i outfit-mysql mysql \\ │"
echo "│    -uroot -prootpassword outfit_db \\   │"
echo "│    < init/outfit_db_with_data.sql      │"
echo "│                                         │"
echo "│ 或使用一鍵腳本:                          │"
echo "│ ./scripts/setup_database_for_teammates.sh │"
echo "└─────────────────────────────────────────┘"

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║  ✅ 完成!                                  ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "下次上傳資料,直接執行此腳本即可:"
echo "  ./scripts/crawler_upload_helper.sh"
