#!/bin/bash
# ========================================
# 資料庫匯出腳本
# ========================================
# 
# ⚠️ 重要規則:
#   - 所有人都匯出到同一個檔名: init/outfit_db_with_data.sql
#   - 不要自創檔名! (如 outfit_db_20251126.sql)
#   - Git 會自動追蹤檔案變更歷史
# 
# 工作流程:
#   1. 修改資料庫內容
#   2. 執行此腳本匯出
#   3. git add + commit + push
#   4. 通知組員同步
# 
# ========================================

echo "🔄 開始匯出資料庫到統一檔案..."
echo "📄 目標檔案: init/outfit_db_with_data.sql"
echo ""

# 匯出完整資料庫 (結構 + 所有資料)
docker exec outfit-mysql mysqldump \
  -uroot -prootpassword \
  --databases outfit_db \
  --no-create-db \
  --single-transaction \
  --routines \
  --triggers \
  --default-character-set=utf8mb4 \
  > init/outfit_db_with_data.sql

echo "✅ 匯出完成: init/outfit_db_with_data.sql"
echo ""
echo "📊 檔案資訊:"
ls -lh init/outfit_db_with_data.sql
echo ""
echo "📝 下一步: 提交到 Git"
echo "  git add init/outfit_db_with_data.sql"
echo "  git commit -m \"更新資料庫:新增/修改 XX 筆資料\""
echo "  git push origin Crawler&Detection"
echo ""
echo "� 通知組員:"
echo "  「資料庫已更新!請執行: git pull 並重新匯入」"
echo ""
echo "⚠️ 重要提醒:"
echo "  - 所有人都使用同一個檔名: outfit_db_with_data.sql"
echo "  - 不要自創新檔名 (如 outfit_db_20251126.sql)"
echo "  - Git 會保留完整的版本歷史,不用擔心覆蓋"
