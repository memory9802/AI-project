# 評分權重推薦系統 - 完整指南

**專案**: 穿搭推薦聊天機器人  
**版本**: v1.0  
**日期**: 2024-12-09  
**狀態**: ✅ 評分調整權重開發中,已建立表格與欄位,待測試

---

## 📋 目錄

1. [系統概述](#系統概述)
2. [快速開始](#快速開始)
3. [資料庫設計](#資料庫設計)
4. [API 文檔](#api-文檔)
5. [測試指南](#測試指南)
6. [除錯與故障排除](#除錯與故障排除)
7. [開發總結](#開發總結)

---

## 🎯 系統概述

### 核心功能

評分權重推薦系統提供完整的 RESTful API 介面,支援:
- ✅ 提交/更新/刪除評分 (1-5 星)
- ✅ 帶權重的商品推薦查詢
- ✅ 用戶評分記錄管理
- ✅ 商品統計資料查詢
- ✅ 全站評分統計
- ✅ 支援 `items` 和 `user_wardrobe` 雙來源評分

### 權重計算邏輯

```
綜合評分 = rating_weight × popularity_weight

Rating Weight (0.5 - 1.5):
  5.0星 → 1.5
  4.0星 → 1.25
  3.0星 → 1.0
  2.0星 → 0.75
  1.0星 → 0.5

Popularity Weight (1.0 - 1.3):
  20+ 評分 → 1.3
  10-19 評分 → 1.2
  5-9 評分 → 1.1
  1-4 評分 → 1.0
  
Final Score = rating_weight × popularity_weight
```

### 技術特色

1. **多態關聯支援**
   - 統一評分表格
   - 支援 items 和 user_wardrobe
   - 靈活擴展其他來源

2. **自動統計更新**
   - 觸發器即時更新 item_stats
   - 視圖自動計算權重
   - 無需手動維護

3. **RESTful API 設計**
   - 語義化端點命名
   - 統一回應格式
   - 完整錯誤處理

4. **效能優化**
   - item_stats 統計快取
   - 視圖預計算權重
   - 索引優化查詢

---

## 🚀 快速開始

### 前置條件檢查

```bash
# 1. 檢查 MySQL 容器運行
docker ps | grep mysql

# 2. 檢查資料庫遷移完成
docker exec -it stylerec-mysql-1 mysql -u root -p outfit_db -e "
  SELECT COUNT(*) as rating_count FROM rating;
  SELECT COUNT(*) as stats_count FROM item_stats;
  SHOW TABLES LIKE 'v_%';
"

# 3. 檢查測試資料
docker exec -it stylerec-mysql-1 mysql -u root -p outfit_db -e "
  SELECT COUNT(*) FROM users WHERE id = 54;
  SELECT COUNT(*) FROM items WHERE is_demo = 1;
"
```

**預期結果**:
- ✅ rating 表格有評分資料
- ✅ item_stats 表格有統計資料
- ✅ 至少 3 個視圖 (v_item_ratings, v_items_with_ratings, v_wardrobe_with_ratings)
- ✅ demo_user (ID: 54) 存在
- ✅ 30 件測試商品 (is_demo = 1)

---

### 啟動步驟 (4 步驟)

#### 步驟 1: 啟動 Flask 應用程式

```bash
cd /Users/liaoyiting/Desktop/stylerec/app

# 方法 1: 直接啟動 (預設 port 5000)
python3 app.py

# 方法 2: 指定 port
PORT=5001 python3 app.py
```

**預期輸出**:
```
* Running on http://0.0.0.0:5000
* Restarting with stat
* Debugger is active!
```

---

#### 步驟 2: 驗證 API 可訪問

```bash
# 檢查應用程式是否運行
curl http://localhost:5000/

# 應該返回重定向或首頁 HTML
```

---

#### 步驟 3: 登入取得 Session Cookie

⚠️ **重要**: 所有 API 都需要認證,必須先登入!

**方法 A: 使用瀏覽器 (推薦)**
1. 打開 http://localhost:5000/login/login
2. 使用 demo_user 登入
3. 登入後瀏覽器會保存 session cookie

**方法 B: 使用 curl**
```bash
# 登入並保存 cookie
curl -c cookies.txt -X POST http://localhost:5000/login/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_user","password":"your_password"}'

# 之後的請求都帶上 cookie
curl -b cookies.txt http://localhost:5000/recommendation/api/recommendations
```

---

#### 步驟 4: 測試 API

**快速測試**:
```bash
# 1. 取得推薦 (帶權重)
curl "http://localhost:5000/recommendation/api/recommendations?item_source=items&limit=10"

# 2. 提交評分
curl -X POST http://localhost:5000/recommendation/api/rating \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": 5092,
    "item_source": "items",
    "rating_value": 5,
    "review_text": "超級喜歡!"
  }'

# 3. 查詢用戶評分
curl "http://localhost:5000/recommendation/api/ratings/user/54?limit=10"

# 4. 查詢全站統計
curl "http://localhost:5000/recommendation/api/statistics"
```

**使用測試腳本 (推薦)**:
```bash
cd /Users/liaoyiting/Desktop/stylerec/scripts

# Python 測試腳本
python3 test_rating_api.py

# 或 Bash 測試腳本
chmod +x test_rating_api.sh
./test_rating_api.sh
```

---

## 📊 資料庫設計

### 核心表格結構

#### 1. rating 表格 (擴展版,支援多態關聯)

```sql
CREATE TABLE rating (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  
  -- 多態關聯
  item_source ENUM('items', 'user_wardrobe') NOT NULL,
  item_id INT NOT NULL,
  
  rating_value INT NOT NULL CHECK (rating_value BETWEEN 1 AND 5),
  review_text TEXT DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE KEY unique_user_source_item (user_id, item_source, item_id),
  
  INDEX idx_user_id (user_id),
  INDEX idx_item_source_id (item_source, item_id),
  INDEX idx_rating_value (rating_value)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**關鍵設計**:
- `item_source`: 標記來源 (`'items'` 或 `'user_wardrobe'`)
- `item_id`: 對應的商品 ID
- 組合唯一鍵: 同一用戶對同一來源的同一商品只能評分一次

---

#### 2. item_stats 統計表 (快取計算結果)

```sql
CREATE TABLE item_stats (
  item_id INT NOT NULL,
  item_source ENUM('items', 'user_wardrobe') NOT NULL,
  
  -- 統計欄位
  avg_rating DECIMAL(3,2) DEFAULT 0.00,
  rating_count INT DEFAULT 0,
  rating_5_count INT DEFAULT 0,
  rating_4_count INT DEFAULT 0,
  rating_3_count INT DEFAULT 0,
  rating_2_count INT DEFAULT 0,
  rating_1_count INT DEFAULT 0,
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (item_id, item_source),
  INDEX idx_avg_rating (avg_rating DESC),
  INDEX idx_rating_count (rating_count DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**用途**: 避免每次查詢都計算平均分,提升性能

---

#### 3. 視圖 (自動帶入權重)

**v_items_with_ratings** - items 商品帶權重:
```sql
CREATE VIEW v_items_with_ratings AS
SELECT 
  i.*,
  COALESCE(s.avg_rating, 0) as avg_rating,
  COALESCE(s.rating_count, 0) as rating_count,
  COALESCE(s.rating_5_count, 0) as rating_5_count,
  COALESCE(s.rating_4_count, 0) as rating_4_count,
  
  -- 評分權重 (0.5 - 1.5)
  CASE 
    WHEN s.avg_rating IS NULL THEN 1.0
    WHEN s.avg_rating >= 4.5 THEN 1.5
    WHEN s.avg_rating >= 3.5 THEN 1.25
    WHEN s.avg_rating >= 2.5 THEN 1.0
    WHEN s.avg_rating >= 1.5 THEN 0.75
    ELSE 0.5
  END as rating_weight,
  
  -- 人氣權重 (1.0 - 1.3)
  CASE 
    WHEN s.rating_count >= 20 THEN 1.3
    WHEN s.rating_count >= 10 THEN 1.2
    WHEN s.rating_count >= 5 THEN 1.1
    ELSE 1.0
  END as popularity_weight,
  
  -- 綜合評分
  (CASE WHEN s.avg_rating >= 4.5 THEN 1.5
        WHEN s.avg_rating >= 3.5 THEN 1.25
        ELSE 1.0 END) *
  (CASE WHEN s.rating_count >= 20 THEN 1.3
        WHEN s.rating_count >= 10 THEN 1.2
        ELSE 1.0 END) as final_score
        
FROM items i
LEFT JOIN item_stats s ON i.id = s.item_id AND s.item_source = 'items';
```

**v_wardrobe_with_ratings** - user_wardrobe 商品帶權重 (結構類似)

---

#### 4. 觸發器 (自動更新統計)

```sql
-- 新增評分後更新統計
CREATE TRIGGER after_rating_insert
AFTER INSERT ON rating
FOR EACH ROW
BEGIN
  INSERT INTO item_stats (item_id, item_source, avg_rating, rating_count, ...)
  SELECT 
    NEW.item_id,
    NEW.item_source,
    AVG(rating_value),
    COUNT(*),
    SUM(CASE WHEN rating_value = 5 THEN 1 ELSE 0 END),
    ...
  FROM rating
  WHERE item_id = NEW.item_id AND item_source = NEW.item_source
  ON DUPLICATE KEY UPDATE
    avg_rating = VALUES(avg_rating),
    rating_count = VALUES(rating_count),
    ...;
END;
```

同樣的邏輯也應用於 `after_rating_update` 和 `after_rating_delete` 觸發器。

---

## 🌐 API 文檔

### 基礎資訊

- **基礎 URL**: `http://localhost:5000/recommendation/api`
- **認證方式**: Session Cookie (需先登入)
- **回應格式**: JSON

---

### API 端點列表

| 方法 | 端點 | 功能 | 需要認證 |
|------|------|------|----------|
| POST | `/rating` | 提交或更新評分 | ✅ |
| DELETE | `/rating/<item_id>` | 刪除評分 | ✅ |
| GET | `/recommendations` | 取得帶權重推薦 | ✅ |
| GET | `/recommendations/comparison` | 推薦比較 | ✅ |
| GET | `/ratings/user/<user_id>` | 查詢用戶評分 | ✅ |
| GET | `/ratings/user/<user_id>/summary` | 用戶評分摘要 | ✅ |
| GET | `/item-stats/<item_id>` | 商品統計資料 | ✅ |
| GET | `/rating/check/<item_id>` | 檢查是否已評分 | ✅ |
| GET | `/top-rated` | 高評分商品列表 | ✅ |
| GET | `/statistics` | 全站統計 | ✅ |

---

### 核心 API 詳解

#### 1. 提交或更新評分

**端點**: `POST /rating`

**Request Body**:
```json
{
  "item_id": 5092,
  "item_source": "items",
  "rating_value": 5,
  "review_text": "超級喜歡!"
}
```

**Response (成功)**:
```json
{
  "success": true,
  "message": "評分提交成功"
}
```

**Response (失敗)**:
```json
{
  "success": false,
  "error": "評分必須在 1-5 之間"
}
```

---

#### 2. 取得帶權重推薦

**端點**: `GET /recommendations`

**Query Parameters**:
- `item_source` (可選): 商品來源,預設 `items`
- `limit` (可選): 返回數量,預設 20
- `exclude_rated` (可選): 是否排除已評分,預設 `true`
- `min_rating` (可選): 最低平均評分過濾
- `category` (可選): 商品類別過濾

**範例**:
```bash
GET /recommendations?item_source=items&limit=10&exclude_rated=true&min_rating=4.0
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "item_id": 5092,
      "productDisplayName": "藍色牛仔褲",
      "avg_rating": 4.5,
      "rating_count": 10,
      "rating_weight": 1.25,
      "popularity_weight": 1.2,
      "final_score": 1.5,
      "imageURL": "...",
      "color": "藍色"
    }
  ],
  "count": 10
}
```

---

#### 3. 推薦比較 (無權重 vs 有權重)

**端點**: `GET /recommendations/comparison`

**功能**: 同時返回無權重和有權重的推薦結果,用於展示權重效果

**Response**:
```json
{
  "success": true,
  "data": {
    "without_weight": [
      { "item_id": 5092, "avg_rating": 5.0 },
      { "item_id": 5093, "avg_rating": 4.8 }
    ],
    "with_weight": [
      { "item_id": 5095, "final_score": 1.56 },
      { "item_id": 5092, "final_score": 1.50 }
    ]
  }
}
```

---

#### 4. 查詢用戶評分記錄

**端點**: `GET /ratings/user/<user_id>`

**範例**: `GET /ratings/user/54?limit=10`

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "user_id": 54,
      "item_source": "items",
      "item_id": 5092,
      "rating_value": 5,
      "review_text": "超級喜歡!",
      "created_at": "2024-12-09 10:30:00",
      "updated_at": "2024-12-09 10:30:00"
    }
  ],
  "count": 1
}
```

**權限控制**: 只能查詢自己的評分記錄

---

#### 5. 查詢全站統計

**端點**: `GET /statistics`

**Response**:
```json
{
  "success": true,
  "data": {
    "total_ratings": 250,
    "total_users": 15,
    "total_items": 100,
    "avg_rating": 4.1,
    "items_count": 180,
    "wardrobe_count": 70
  }
}
```

---

### 錯誤處理

#### HTTP 狀態碼

- `200 OK`: 請求成功
- `400 Bad Request`: 請求參數錯誤
- `403 Forbidden`: 無權限訪問
- `404 Not Found`: 資源不存在
- `500 Internal Server Error`: 伺服器錯誤

#### 錯誤回應格式

```json
{
  "success": false,
  "error": "錯誤訊息"
}
```

#### 常見錯誤

1. **缺少必要欄位**: `"缺少必要欄位: item_id"`
2. **評分值範圍錯誤**: `"評分必須在 1-5 之間"`
3. **商品不存在**: `"商品不存在 (ID: 9999, 來源: items)"`
4. **無權限**: `"無權限查詢其他用戶的評分"`

---

## 🧪 測試指南

### 方法 1: 使用測試腳本 (推薦)

#### Python 測試腳本

```bash
cd /Users/liaoyiting/Desktop/stylerec/scripts
python3 test_rating_api.py
```

**測試內容**:
- ✅ 提交評分 (新增/更新)
- ✅ 推薦查詢 (帶權重)
- ✅ 推薦比較 (無權重 vs 有權重)
- ✅ 用戶評分查詢
- ✅ 商品統計查詢
- ✅ 刪除評分

---

#### Bash 測試腳本

```bash
cd /Users/liaoyiting/Desktop/stylerec/scripts
chmod +x test_rating_api.sh
./test_rating_api.sh
```

---

### 方法 2: 手動測試

#### 測試 1: 提交評分

```bash
curl -X POST http://localhost:5000/recommendation/api/rating \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": 5092,
    "item_source": "items",
    "rating_value": 5,
    "review_text": "超級喜歡!"
  }'
```

**預期結果**:
```json
{
  "success": true,
  "message": "評分提交成功"
}
```

---

#### 測試 2: 取得推薦

```bash
curl "http://localhost:5000/recommendation/api/recommendations?item_source=items&limit=10"
```

**驗證重點**:
- ✅ 返回 10 件商品
- ✅ 每件商品包含 `rating_weight` 和 `popularity_weight`
- ✅ 按 `final_score` 降序排列

---

#### 測試 3: 推薦比較

```bash
curl "http://localhost:5000/recommendation/api/recommendations/comparison?item_source=items&limit=5"
```

**驗證重點**:
- ✅ `without_weight` 和 `with_weight` 結果不同
- ✅ 高分商品在 `with_weight` 中排名更前

---

#### 測試 4: 驗證統計自動更新

```bash
# 1. 查詢初始統計
curl "http://localhost:5000/recommendation/api/item-stats/5092?item_source=items"

# 2. 提交新評分
curl -X POST http://localhost:5000/recommendation/api/rating \
  -H "Content-Type: application/json" \
  -d '{"item_id": 5092, "item_source": "items", "rating_value": 5}'

# 3. 再次查詢統計 (應該已更新)
curl "http://localhost:5000/recommendation/api/item-stats/5092?item_source=items"
```

**預期**: `rating_count` 增加 1,`avg_rating` 重新計算

---

### 驗證清單

測試成功的標準:

- [ ] ✅ Flask 應用程式成功啟動
- [ ] ✅ 成功登入並取得 session cookie
- [ ] ✅ 提交評分成功 (返回 200)
- [ ] ✅ 取得推薦列表成功 (包含權重欄位)
- [ ] ✅ 推薦比較顯示差異 (無權重 vs 有權重)
- [ ] ✅ 商品統計自動更新 (觸發器運作)
- [ ] ✅ 用戶評分查詢成功
- [ ] ✅ 全站統計正確

---

## 🔍 除錯與故障排除

### 問題 1: API 返回 401 Unauthorized

**原因**: 未登入或 session 已過期

**解決方案**:
1. 確保已登入並取得 session cookie
2. 檢查 cookie 是否正確傳遞:
   ```bash
   # 使用瀏覽器開發者工具
   Application → Cookies → localhost → session
   ```
3. 重新登入

---

### 問題 2: API 返回 500 Internal Server Error

**原因**: 可能是資料庫連線或 SQL 錯誤

**解決方案**:

1. **檢查 Flask 日誌**:
   ```bash
   # 終端會顯示詳細錯誤訊息
   # 查找 Traceback 和 SQL 錯誤
   ```

2. **檢查資料庫連線**:
   ```bash
   docker ps | grep mysql
   docker exec -it stylerec-mysql-1 mysql -u root -p
   ```

3. **檢查視圖和觸發器**:
   ```sql
   USE outfit_db;
   SHOW TABLES LIKE 'v_%';
   SHOW TRIGGERS;
   ```

4. **檢查資料完整性**:
   ```sql
   SELECT COUNT(*) FROM rating;
   SELECT COUNT(*) FROM item_stats;
   SELECT COUNT(*) FROM items WHERE is_demo = 1;
   ```

---

### 問題 3: 找不到模組 'rating_service'

**原因**: Python 模組導入錯誤

**解決方案**:

1. **檢查檔案路徑**:
   ```bash
   ls -la /Users/liaoyiting/Desktop/stylerec/app/blueprints/recommendation/rating_service.py
   ```

2. **檢查 `__init__.py`**:
   ```bash
   ls -la /Users/liaoyiting/Desktop/stylerec/app/blueprints/recommendation/__init__.py
   ```

3. **重啟 Flask**:
   ```bash
   # Ctrl+C 停止
   # 重新啟動
   python3 app.py
   ```

---

### 問題 4: 推薦結果為空

**原因**: 測試資料未插入或已全部評分

**解決方案**:

1. **檢查測試資料**:
   ```sql
   SELECT COUNT(*) FROM items WHERE is_demo = 1;
   SELECT COUNT(*) FROM rating WHERE user_id = 54;
   ```

2. **使用 `exclude_rated=false` 測試**:
   ```bash
   curl "http://localhost:5000/recommendation/api/recommendations?exclude_rated=false&limit=10"
   ```

3. **重新插入測試資料**:
   ```sql
   -- 在 DBeaver 中執行 insert_demo_ratings.sql
   ```

---

### 問題 5: 權重計算結果異常

**原因**: 觸發器未正常運作或統計資料過舊

**解決方案**:

1. **手動重建統計**:
   ```sql
   -- 清空 item_stats
   TRUNCATE TABLE item_stats;
   
   -- 重新計算
   INSERT INTO item_stats (item_id, item_source, avg_rating, rating_count, ...)
   SELECT 
     item_id,
     item_source,
     AVG(rating_value),
     COUNT(*),
     SUM(CASE WHEN rating_value = 5 THEN 1 ELSE 0 END),
     SUM(CASE WHEN rating_value = 4 THEN 1 ELSE 0 END),
     SUM(CASE WHEN rating_value = 3 THEN 1 ELSE 0 END),
     SUM(CASE WHEN rating_value = 2 THEN 1 ELSE 0 END),
     SUM(CASE WHEN rating_value = 1 THEN 1 ELSE 0 END)
   FROM rating
   GROUP BY item_id, item_source;
   ```

2. **檢查觸發器**:
   ```sql
   SHOW TRIGGERS LIKE '%rating%';
   ```

3. **重建觸發器** (如果需要):
   ```bash
   # 重新執行 migration_rating_system.sql 中的觸發器部分
   ```

---

## 📈 開發總結

### 已完成項目

#### 1. 核心服務模組

**檔案**: `app/blueprints/recommendation/rating_service.py`

**代碼量**: 600+ 行

**核心函數** (10 個):
- `get_weighted_recommendations()` - 帶權重推薦
- `get_recommendations_comparison()` - 推薦比較
- `submit_rating()` - 提交評分
- `delete_rating()` - 刪除評分
- `get_user_ratings()` - 用戶評分記錄
- `get_user_rating_summary()` - 用戶評分摘要
- `get_item_stats()` - 商品統計
- `get_top_rated_items()` - 高評分商品
- `check_user_rated()` - 檢查評分狀態
- `get_rating_statistics()` - 全站統計

---

#### 2. API 端點

**檔案**: `app/blueprints/recommendation/routes.py`

**代碼量**: 400+ 行

**API 端點**: 10 個

**特色**:
- ✅ 完整的參數驗證
- ✅ 權限控制
- ✅ 統一的錯誤處理
- ✅ 詳細的日誌記錄

---

#### 3. 測試工具

- **test_rating_api.sh** - Bash 測試腳本
- **test_rating_api.py** - Python 測試腳本

**測試覆蓋**: 6 大區塊,涵蓋所有 API

---

#### 4. 資料庫遷移

- **migration_rating_system.sql** (436 行)
  - 擴展 rating 表格
  - 建立 item_stats 統計表
  - 建立 3 個視圖
  - 建立 3 個觸發器

- **demo_test_data.sql** - 測試資料腳本
- **insert_demo_ratings.sql** - 手動插入腳本
- **fix_rating_charset.sql** - 字符集修正腳本

---

### 技術亮點

1. **完整的權重系統**
   - 評分權重 + 人氣權重
   - 自動計算,無需手動維護
   - 觸發器即時更新

2. **多態關聯支援**
   - 統一評分表格
   - 支援 items 和 user_wardrobe
   - 靈活擴展其他來源

3. **RESTful API 設計**
   - 語義化端點命名
   - 統一回應格式
   - 完整錯誤處理

4. **效能優化**
   - item_stats 快取統計
   - 視圖預計算權重
   - 索引優化查詢

---

### 檔案清單

#### 新增檔案 (11 個)

```
後端代碼:
├── app/blueprints/recommendation/rating_service.py   (600+ 行)
├── app/blueprints/recommendation/routes.py           (400+ 行, 更新)

資料庫腳本:
├── init/migration_rating_system.sql                  (436 行)
├── init/demo_test_data.sql
├── init/insert_demo_ratings.sql                      (140 行)
├── init/fix_rating_charset.sql
├── init/migrate_rating_system.sh
├── init/MIGRATION_GUIDE.md

測試工具:
├── scripts/test_rating_api.sh
├── scripts/test_rating_api.py

文檔:
└── docs/RATING_SYSTEM_COMPLETE_GUIDE.md             (本檔案)
```

**總代碼量**: 2500+ 行

---

### 進度追蹤

```
✅ 資料庫遷移     ████████████████████ 100%
✅ 測試資料插入   ████████████████████ 100%
✅ 後端服務開發   ████████████████████ 100%
✅ API 端點開發   ████████████████████ 100%
✅ 測試工具建立   ████████████████████ 100%
✅ 文檔撰寫       ████████████████████ 100%
⏳ API 測試       ░░░░░░░░░░░░░░░░░░░░   0%
⏳ 前端整合       ░░░░░░░░░░░░░░░░░░░░   0%
```

**總體進度**: 75% (6/8)

---

## 🎯 下一步計劃

### 立即待辦 (高優先級)

1. **啟動並測試 API**
   - 啟動 Flask 應用程式
   - 執行測試腳本
   - 驗證所有 API

2. **前端整合**
   - recommendation.html 加入評分按鈕
   - wardrobe.html 加入評分 UI
   - 實作星級評分組件

3. **Demo 錄影準備**
   - 準備測試資料
   - 設計展示流程
   - 錄製 Demo 影片

---

### 後續優化 (中優先級)

4. **功能擴展**
   - 評分通知系統
   - 評分排行榜
   - 評分篩選和排序

5. **效能優化**
   - 新增查詢快取
   - 資料庫索引優化
   - API 回應壓縮

---

### 長期規劃 (低優先級)

6. **監控和日誌**
   - API 呼叫統計
   - 錯誤追蹤
   - 效能監控

7. **進階功能**
   - 協同過濾推薦
   - 機器學習模型整合
   - A/B 測試框架

---

## 📞 支援資訊

### 相關文件

- **資料庫遷移指南**: `init/MIGRATION_GUIDE.md`
- **系統設計文檔**: `docs/RATING_WEIGHT_SYSTEM_DESIGN.md`
- **測試腳本**: `scripts/test_rating_api.py`

### Git 資訊

- **最新 Commit**: `778474c`
- **分支**: 1202MVP
- **備份倉庫**: RosyL666/stylerec (develop)

### 技術支援

如果遇到問題:
1. 查看本文檔的[除錯與故障排除](#除錯與故障排除)章節
2. 檢查 Flask 終端日誌
3. 檢查資料庫連線和資料
4. 參考測試腳本範例

---

## 📝 注意事項

1. **認證**: 所有 API 需要先登入
2. **權限**: 只能操作自己的評分
3. **驗證**: 評分值必須 1-5
4. **字符集**: 支援 UTF-8 中文
5. **效能**: 視圖查詢已優化
6. **測試資料**: demo_user (ID: 54) 和測試商品 (ID: 5092-5121)

---

**文件版本**: v1.0  
**最後更新**: 2024-12-09  
**作者**: GitHub Copilot  
**狀態**: ✅ 後端開發完成,待測試  
**專案**: stylerec - 穿搭推薦系統
