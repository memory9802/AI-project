# 評分權重系統實作指南

**專案**: stylerec 穿搭推薦系統  
**方案**: 方案 B (完整擴展) + Demo 方案 1 (小範圍測試集)  
**日期**: 2025-12-09

---

## 📋 實作概述

本指南將引導你完成評分權重系統的**資料庫遷移**部分,支援 `items` 和 `user_wardrobe` 兩個來源的評分。

### 核心功能
- ✅ 支援多態關聯 (items + user_wardrobe)
- ✅ 自動統計計算 (透過觸發器)
- ✅ 帶權重的推薦查詢 (視圖)
- ✅ Demo 測試資料準備

---

## 🗂️ 檔案清單

已建立的 SQL 腳本和工具:

```
init/
├── migration_rating_system.sql      # 資料庫遷移腳本 (核心)
├── demo_test_data.sql               # Demo 測試資料腳本
├── migrate_rating_system.sh         # 自動化執行腳本 (推薦使用)
└── MIGRATION_GUIDE.md               # 本文件
```

---

## 🚀 快速開始

### 方法 1: 使用自動化腳本 (推薦 ⭐⭐⭐⭐⭐)

```bash
# 1. 進入 init 目錄
cd /Users/liaoyiting/Desktop/stylerec/init

# 2. 執行遷移腳本
./migrate_rating_system.sh

# 腳本會自動:
# - 檢查 Docker 容器狀態
# - 備份現有資料庫
# - 執行遷移腳本
# - 詢問是否插入測試資料
# - 驗證結果
# - 顯示統計資料
```

**優點**: 全自動化,有錯誤處理和驗證,安全可靠

---

### 方法 2: 手動執行 SQL 腳本

#### Step 1: 檢查 Docker 容器

```bash
# 確認容器運行中
docker ps | grep outfit-mysql

# 如果未運行,啟動容器
docker-compose up -d
```

#### Step 2: 備份資料庫 (重要!)

```bash
# 建立備份目錄
mkdir -p /Users/liaoyiting/Desktop/stylerec/backups

# 備份資料庫
docker exec outfit-mysql mysqldump -uroot -prootpassword outfit_db \
  > backups/outfit_db_backup_$(date +%Y%m%d_%H%M%S).sql

# 確認備份成功
ls -lh backups/
```

#### Step 3: 執行遷移腳本

```bash
# 方法 A: 直接執行 (不顯示輸出)
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db \
  < init/migration_rating_system.sql

# 方法 B: 執行並顯示輸出 (推薦)
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db \
  < init/migration_rating_system.sql 2>&1 | tee migration.log
```

**執行時間**: 約 5-10 秒

#### Step 4: 驗證遷移結果

```bash
# 檢查表格是否建立
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db \
  -e "SHOW TABLES LIKE '%rating%';"

# 預期輸出:
# rating
# rating_backup
# item_stats

# 檢查視圖
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db \
  -e "SHOW FULL TABLES WHERE Table_type = 'VIEW';"

# 預期輸出:
# v_item_ratings
# v_items_with_ratings
# v_wardrobe_with_ratings

# 檢查觸發器
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db \
  -e "SHOW TRIGGERS WHERE \`Table\` = 'rating';"

# 預期輸出:
# after_rating_insert
# after_rating_update
# after_rating_delete
```

#### Step 5: 插入 Demo 測試資料 (可選)

```bash
# 執行測試資料腳本
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db \
  < init/demo_test_data.sql 2>&1 | tee demo_data.log

# 查看插入的測試資料
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db \
  -e "SELECT COUNT(*) FROM rating;"
```

---

## 📊 遷移內容詳解

### 1. rating 表格擴展

**舊結構** (只支援 items):
```sql
rating (
  user_id, item_id, rating_value, review_text
)
```

**新結構** (支援 items + user_wardrobe):
```sql
rating (
  user_id,
  item_source ENUM('items', 'user_wardrobe'),  -- 新增!
  item_id,
  rating_value,
  review_text,
  created_at,
  updated_at
)

UNIQUE KEY (user_id, item_source, item_id)  -- 組合唯一鍵
```

### 2. item_stats 統計表

自動快取計算結果,提升查詢性能:

```sql
item_stats (
  item_source, item_id,
  avg_rating,          -- 平均評分
  rating_count,        -- 評分次數
  rating_5_count,      -- 5星數量
  rating_4_count,      -- 4星數量
  ...
  high_rating_ratio    -- 高分比例
)
```

**更新機制**: 透過觸發器自動更新,不需手動維護

### 3. 視圖 (Views)

#### v_item_ratings
統一的評分統計視圖,聚合所有評分資料

#### v_items_with_ratings
帶權重的 items 推薦視圖,包含:
- 平均評分、評分次數
- 評分權重 (rating_weight: 0.5-1.5)
- 熱度權重 (popularity_weight: 1.0-1.3)
- 最終評分 (final_score)

#### v_wardrobe_with_ratings
帶權重的 user_wardrobe 推薦視圖,結構同上

### 4. 觸發器 (Triggers)

自動維護統計表:
- `after_rating_insert`: 新增評分後更新統計
- `after_rating_update`: 修改評分後更新統計
- `after_rating_delete`: 刪除評分後更新統計

---

## 🧪 測試驗證

### 測試 1: 檢查 Demo 測試資料

```bash
# 進入 MySQL 容器
docker exec -it outfit-mysql mysql -uroot -prootpassword outfit_db

# 查看測試用戶
SELECT * FROM users WHERE username = 'demo_user';

# 查看測試商品
SELECT COUNT(*) FROM items WHERE is_demo = TRUE;

# 查看評分統計
SELECT 
  item_source,
  COUNT(*) as rating_count,
  AVG(rating_value) as avg_rating
FROM rating
WHERE user_id = (SELECT id FROM users WHERE username = 'demo_user')
GROUP BY item_source;

# 退出
exit;
```

### 測試 2: 無權重 vs 有權重推薦對比

```bash
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db << EOF

-- 無權重推薦 (隨機)
SELECT '=== 無權重推薦 ===' as section;
SELECT id, name, COALESCE(avg_rating, 0) as avg_rating
FROM v_items_with_ratings
WHERE is_demo = TRUE
ORDER BY RAND()
LIMIT 5;

-- 有權重推薦 (評分優先)
SELECT '=== 有權重推薦 ===' as section;
SELECT id, name, avg_rating, rating_count, final_score
FROM v_items_with_ratings
WHERE is_demo = TRUE
ORDER BY final_score DESC
LIMIT 5;

EOF
```

**預期結果**:
- 無權重: 包含各種評分的商品 (1-5星混合)
- 有權重: 高分商品優先 (4-5星在前)

### 測試 3: 觸發器自動更新

```bash
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db << EOF

-- 新增一筆評分
INSERT INTO rating (user_id, item_source, item_id, rating_value)
VALUES (1, 'items', 1, 5);

-- 檢查統計表是否自動更新
SELECT * FROM item_stats 
WHERE item_source = 'items' AND item_id = 1;

-- 清理測試資料
DELETE FROM rating 
WHERE user_id = 1 AND item_source = 'items' AND item_id = 1;

EOF
```

**預期結果**: 
- 新增評分後,`item_stats` 自動更新
- 刪除評分後,統計表自動調整

---

## 🔍 常見問題排解

### 問題 1: Docker 容器未運行

```bash
# 檢查容器狀態
docker ps -a | grep outfit-mysql

# 如果狀態為 Exited,啟動容器
docker-compose up -d

# 查看容器日誌
docker logs outfit-mysql
```

### 問題 2: 權限錯誤

```bash
# 確認 MySQL 密碼正確
docker exec outfit-mysql mysql -uroot -prootpassword -e "SELECT 1;"

# 如果密碼錯誤,檢查 docker-compose.yml
cat docker-compose.yml | grep MYSQL_ROOT_PASSWORD
```

### 問題 3: 外鍵約束錯誤

```bash
# 檢查相關表格是否存在
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db \
  -e "SHOW TABLES LIKE 'users'; SHOW TABLES LIKE 'items';"

# 如果表格不存在,需要先執行初始化腳本
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db \
  < init/00_init_with_data.sql
```

### 問題 4: 觸發器建立失敗

```bash
# 刪除現有觸發器後重新建立
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db << EOF
DROP TRIGGER IF EXISTS after_rating_insert;
DROP TRIGGER IF EXISTS after_rating_update;
DROP TRIGGER IF EXISTS after_rating_delete;
EOF

# 重新執行遷移腳本
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db \
  < init/migration_rating_system.sql
```

---

## 📊 遷移後的資料庫結構

```
outfit_db
├── users (用戶表)
├── items (商品表)
│   └── is_demo (新增欄位: 標記測試商品)
├── user_wardrobe (個人衣櫃表)
├── rating (評分表 - 已擴展)
│   ├── item_source (新增: items 或 user_wardrobe)
│   └── UNIQUE (user_id, item_source, item_id)
├── item_stats (統計表 - 新增)
│   ├── avg_rating, rating_count
│   └── 自動透過觸發器更新
├── v_item_ratings (視圖 - 新增)
├── v_items_with_ratings (視圖 - 新增)
└── v_wardrobe_with_ratings (視圖 - 新增)

Triggers (觸發器 - 新增)
├── after_rating_insert
├── after_rating_update
└── after_rating_delete
```

---

## 📈 統計資料範例

遷移完成後,你應該看到:

```
=== Demo 測試資料統計 ===

測試用戶: demo_user (ID: X)
測試商品: 30 件 (is_demo = TRUE)

items 評分:
- 總數: 18 筆
- 高分 (4-5星): 10 筆
- 低分 (1-2星): 5 筆
- 中等 (3星): 3 筆
- 平均: 3.5 星

user_wardrobe 評分:
- 總數: 7 筆
- 高分 (4-5星): 5 筆
- 低分 (1-2星): 2 筆
- 平均: 4.1 星

統計表記錄:
- items: 18 筆
- user_wardrobe: 7 筆
- 總計: 25 筆
```

---

## ✅ 遷移檢查清單

完成遷移後,請確認以下項目:

- [ ] ✅ rating 表格已擴展 (包含 item_source 欄位)
- [ ] ✅ item_stats 表格已建立
- [ ] ✅ 3 個視圖已建立 (v_item_ratings, v_items_with_ratings, v_wardrobe_with_ratings)
- [ ] ✅ 3 個觸發器已建立 (after_rating_insert/update/delete)
- [ ] ✅ items 表格新增 is_demo 欄位
- [ ] ✅ Demo 測試資料已插入 (可選)
- [ ] ✅ 無權重 vs 有權重推薦測試通過
- [ ] ✅ 備份檔案已建立

---

## 🎯 下一步

資料庫遷移完成後,接下來實作:

### Step 1: 後端 API 開發
- 建立 `app/blueprints/aichat/rating_service.py`
- 實作 `get_weighted_items()` 函數
- 實作 `submit_rating()` 函數
- 實作 `get_user_ratings()` 函數

### Step 2: API 路由
- 更新 `app/blueprints/aichat/routes.py`
- 新增 `/items_weighted` API
- 新增 `/submit_rating` API
- 新增 `/get_ratings` API

### Step 3: 前端整合 (組員負責)
- 建立評分按鈕組件
- 串接評分 API
- 顯示權重標籤

### Step 4: 測試完整流程
- 測試無權重推薦
- 測試有權重推薦
- 測試即時評分
- 錄製 Demo 影片

---

## 💡 注意事項

1. **備份很重要**: 每次遷移前都要備份資料庫
2. **觸發器自動更新**: 不需要手動更新 item_stats 表格
3. **視圖查詢**: 使用視圖查詢比直接 JOIN 更簡潔
4. **Demo 商品**: 使用 `is_demo = TRUE` 過濾測試商品
5. **權重計算**: 公式已內建在視圖中,直接使用 `final_score` 排序

---

## 📞 需要幫助?

如果遇到問題:

1. 檢查錯誤日誌: `migration.log` 或 `demo_data.log`
2. 查看 Docker 容器日誌: `docker logs outfit-mysql`
3. 參考常見問題排解章節
4. 查看詳細設計文檔: `docs/RATING_WEIGHT_SYSTEM_DESIGN.md`

---

**文件版本**: v1.0  
**建立日期**: 2025-12-09  
**作者**: GitHub Copilot  
**專案**: stylerec 穿搭推薦系統
