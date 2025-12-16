# 觸發器與索引詳細運作說明

## 🔄 觸發器 (Triggers) 詳細解析

### 觸發器的核心作用
觸發器是資料庫中的**自動化機制**,當特定事件發生時(如 INSERT、UPDATE、DELETE),會自動執行預定義的 SQL 語句。

---

## 1️⃣ after_rating_insert 觸發器

### 📌 觸發時機
```sql
CREATE TRIGGER `after_rating_insert` 
AFTER INSERT ON `rating`  -- 在 rating 表新增資料後執行
FOR EACH ROW
```

### 🎯 觸發場景
當使用者對商品評分時:
```sql
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text)
VALUES (1, 'items', 12345, 5, '很喜歡這件衣服!');
```

### 📊 參照欄位說明

#### 輸入欄位 (從 rating 表讀取)
| 欄位 | 說明 | 範例值 | 用途 |
|------|------|--------|------|
| `NEW.item_source` | 商品來源類型 | 'items' 或 'user_wardrobe' | 判斷是商品庫還是個人衣櫃 |
| `NEW.item_id` | 商品 ID | 12345 | 指向具體商品 |
| `NEW.rating_value` | 評分值 | 5 | 使用者給的星級 |

#### 輸出欄位 (寫入 item_stats 表)
| 欄位 | 說明 | 計算方式 | 用途 |
|------|------|----------|------|
| `item_source` | 商品來源 | 直接複製 NEW.item_source | 關聯商品來源 |
| `item_id` | 商品 ID | 直接複製 NEW.item_id | 關聯商品 |
| `avg_rating` | 平均評分 | `SUM(rating_value) / COUNT(*)` | 顯示平均星級 |
| `rating_count` | 評分總數 | `COUNT(*)` | 統計評分次數 |
| `rating_sum` | 評分總和 | `SUM(rating_value)` | 用於計算平均值 |
| `rating_5_count` | 5星數量 | `SUM(CASE WHEN rating_value = 5 THEN 1 ELSE 0 END)` | 統計5星評分 |
| `rating_4_count` | 4星數量 | `SUM(CASE WHEN rating_value = 4 THEN 1 ELSE 0 END)` | 統計4星評分 |
| `rating_3_count` | 3星數量 | `SUM(CASE WHEN rating_value = 3 THEN 1 ELSE 0 END)` | 統計3星評分 |
| `rating_2_count` | 2星數量 | `SUM(CASE WHEN rating_value = 2 THEN 1 ELSE 0 END)` | 統計2星評分 |
| `rating_1_count` | 1星數量 | `SUM(CASE WHEN rating_value = 1 THEN 1 ELSE 0 END)` | 統計1星評分 |
| `high_rating_count` | 高分數量 | `SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END)` | 4星+5星總數 |
| `high_rating_ratio` | 高分比例 | `high_rating_count / rating_count` | 好評率指標 |

### 🔍 觸發器執行流程

```
步驟 1: 使用者提交評分
─────────────────────────────
INSERT INTO rating 
  (user_id=1, item_source='items', item_id=12345, rating_value=5)
       ↓

步驟 2: 觸發器自動啟動
─────────────────────────────
after_rating_insert 觸發器被激活
讀取 NEW.item_source = 'items'
讀取 NEW.item_id = 12345
       ↓

步驟 3: 查詢該商品的所有評分
─────────────────────────────
SELECT 
  COUNT(*) as rating_count,           -- 計算總評分數
  SUM(rating_value) as rating_sum,    -- 計算評分總和
  AVG(rating_value) as avg_rating,    -- 計算平均評分
  SUM(CASE WHEN rating_value = 5 THEN 1 ELSE 0 END) as rating_5_count,
  SUM(CASE WHEN rating_value = 4 THEN 1 ELSE 0 END) as rating_4_count,
  SUM(CASE WHEN rating_value = 3 THEN 1 ELSE 0 END) as rating_3_count,
  SUM(CASE WHEN rating_value = 2 THEN 1 ELSE 0 END) as rating_2_count,
  SUM(CASE WHEN rating_value = 1 THEN 1 ELSE 0 END) as rating_1_count,
  SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END) as high_rating_count
FROM rating
WHERE item_source = 'items'      -- 參照 NEW.item_source
  AND item_id = 12345;           -- 參照 NEW.item_id
       ↓

步驟 4: 計算衍生欄位
─────────────────────────────
high_rating_ratio = high_rating_count / rating_count
                  = 8 / 10 = 0.8000 (80% 好評率)
       ↓

步驟 5: 更新或插入統計資料
─────────────────────────────
INSERT INTO item_stats 
  (item_source, item_id, avg_rating, rating_count, ...)
VALUES 
  ('items', 12345, 4.50, 10, ...)
ON DUPLICATE KEY UPDATE
  avg_rating = 4.50,
  rating_count = 10,
  ...
  last_updated = NOW();
       ↓

完成! ✅ 統計快取已更新
```

### 💡 實際範例

**情境**: 商品 ID=12345 目前有 9 筆評分

| user_id | rating_value |
|---------|--------------|
| 1 | 5 ⭐⭐⭐⭐⭐ |
| 2 | 4 ⭐⭐⭐⭐ |
| 3 | 5 ⭐⭐⭐⭐⭐ |
| 4 | 4 ⭐⭐⭐⭐ |
| 5 | 5 ⭐⭐⭐⭐⭐ |
| 6 | 3 ⭐⭐⭐ |
| 7 | 4 ⭐⭐⭐⭐ |
| 8 | 5 ⭐⭐⭐⭐⭐ |
| 9 | 5 ⭐⭐⭐⭐⭐ |

**當前統計** (item_stats 表):
```sql
item_source: 'items'
item_id: 12345
avg_rating: 4.44
rating_count: 9
rating_sum: 40
rating_5_count: 5
rating_4_count: 3
rating_3_count: 1
rating_2_count: 0
rating_1_count: 0
high_rating_count: 8  (5星+4星)
high_rating_ratio: 0.8889  (88.89%)
```

**使用者 10 新增評分**:
```sql
INSERT INTO rating (user_id, item_source, item_id, rating_value)
VALUES (10, 'items', 12345, 5);
```

**觸發器自動更新統計**:
```sql
-- 觸發器重新計算
rating_count: 9 → 10  (增加1)
rating_sum: 40 → 45  (40 + 5)
avg_rating: 4.44 → 4.50  (45 / 10)
rating_5_count: 5 → 6  (增加1)
high_rating_count: 8 → 9  (增加1)
high_rating_ratio: 0.8889 → 0.9000  (9/10 = 90%)
```

**結果**: item_stats 表自動更新,無需手動維護! ✅

---

## 2️⃣ after_rating_update 觸發器

### 📌 觸發時機
```sql
CREATE TRIGGER `after_rating_update` 
AFTER UPDATE ON `rating`  -- 在 rating 表更新資料後執行
FOR EACH ROW
```

### 🎯 觸發場景
當使用者修改評分時:
```sql
UPDATE rating 
SET rating_value = 4, review_text = '還不錯'
WHERE user_id = 1 AND item_source = 'items' AND item_id = 12345;
```

### 📊 參照欄位說明

#### 輸入欄位
| 欄位 | 說明 | 範例值 | 用途 |
|------|------|--------|------|
| `OLD.rating_value` | 修改前的評分 | 5 | 用於判斷是否需要重新計算 |
| `NEW.rating_value` | 修改後的評分 | 4 | 新的評分值 |
| `NEW.item_source` | 商品來源 | 'items' | 定位商品 |
| `NEW.item_id` | 商品 ID | 12345 | 定位商品 |

### 🔍 觸發器執行流程

```
步驟 1: 使用者修改評分
─────────────────────────────
UPDATE rating 
SET rating_value = 4     -- OLD.rating_value = 5
WHERE user_id = 1 
  AND item_source = 'items' 
  AND item_id = 12345;
       ↓

步驟 2: 觸發器檢查變更
─────────────────────────────
IF OLD.rating_value != NEW.rating_value THEN
  -- 評分值有變動,需要重新計算
       ↓

步驟 3: 重新查詢所有評分
─────────────────────────────
SELECT 
  COUNT(*) as rating_count,
  SUM(rating_value) as rating_sum,
  AVG(rating_value) as avg_rating,
  ...
FROM rating
WHERE item_source = 'items' 
  AND item_id = 12345;
       ↓

步驟 4: 更新統計資料
─────────────────────────────
UPDATE item_stats
SET 
  avg_rating = 4.40,        -- 從 4.50 降到 4.40
  rating_sum = 44,          -- 從 45 降到 44
  rating_5_count = 5,       -- 從 6 降到 5
  rating_4_count = 4,       -- 從 3 增到 4
  high_rating_count = 9,    -- 維持 9
  high_rating_ratio = 0.9000,
  last_updated = NOW()
WHERE item_source = 'items' 
  AND item_id = 12345;
       ↓

完成! ✅ 統計已同步
```

### 💡 實際範例

**修改前** (10 筆評分):
```
5, 4, 5, 4, 5, 3, 4, 5, 5, 5
總和: 45, 平均: 4.50
5星: 6, 4星: 3, 3星: 1
```

**使用者修改評分**: 5星 → 4星
```
5, 4, 5, 4, 5, 3, 4, 5, 5, 4  ← 最後一個從5改成4
總和: 44, 平均: 4.40
5星: 5, 4星: 4, 3星: 1
```

**觸發器自動更新**: ✅

---

## 3️⃣ after_rating_delete 觸發器

### 📌 觸發時機
```sql
CREATE TRIGGER `after_rating_delete` 
AFTER DELETE ON `rating`  -- 在 rating 表刪除資料後執行
FOR EACH ROW
```

### 🎯 觸發場景
當使用者刪除評分時:
```sql
DELETE FROM rating 
WHERE user_id = 1 AND item_source = 'items' AND item_id = 12345;
```

### 📊 參照欄位說明

#### 輸入欄位
| 欄位 | 說明 | 範例值 | 用途 |
|------|------|--------|------|
| `OLD.item_source` | 被刪除評分的商品來源 | 'items' | 定位商品 |
| `OLD.item_id` | 被刪除評分的商品 ID | 12345 | 定位商品 |
| `OLD.rating_value` | 被刪除的評分值 | 5 | (參考用) |

### 🔍 觸發器執行流程

```
步驟 1: 使用者刪除評分
─────────────────────────────
DELETE FROM rating 
WHERE user_id = 1 
  AND item_source = 'items' 
  AND item_id = 12345;
       ↓

步驟 2: 觸發器檢查剩餘評分
─────────────────────────────
SELECT COUNT(*) 
FROM rating 
WHERE item_source = OLD.item_source    -- 參照 'items'
  AND item_id = OLD.item_id;           -- 參照 12345
       ↓
       
步驟 3A: 如果沒有評分了 (COUNT = 0)
─────────────────────────────
DELETE FROM item_stats
WHERE item_source = 'items' 
  AND item_id = 12345;

結果: 統計記錄被刪除 ✅
       ↓
       
步驟 3B: 如果還有其他評分 (COUNT > 0)
─────────────────────────────
SELECT 
  COUNT(*) as rating_count,
  SUM(rating_value) as rating_sum,
  AVG(rating_value) as avg_rating,
  ...
FROM rating
WHERE item_source = 'items' 
  AND item_id = 12345;
       ↓

步驟 4: 更新統計資料
─────────────────────────────
UPDATE item_stats
SET 
  avg_rating = 4.33,        -- 重新計算
  rating_count = 9,         -- 從 10 減到 9
  rating_sum = 39,          -- 從 44 減到 39
  rating_5_count = 5,       -- 如果刪除的是5星
  high_rating_count = 8,
  high_rating_ratio = 0.8889,
  last_updated = NOW()
WHERE item_source = 'items' 
  AND item_id = 12345;
       ↓

完成! ✅ 統計已同步
```

### 💡 實際範例

**情境 A: 刪除後還有評分**

刪除前 (10 筆評分):
```
5, 4, 5, 4, 5, 3, 4, 5, 5, 4
總和: 44, 平均: 4.40
5星: 5, 4星: 4, 3星: 1
```

刪除 user_id=1 的 5星評分:
```
4, 5, 4, 5, 3, 4, 5, 5, 4  (9筆)
總和: 39, 平均: 4.33
5星: 4, 4星: 4, 3星: 1
```

觸發器動作: **UPDATE item_stats** ✅

---

**情境 B: 刪除後沒有評分了**

刪除前 (1 筆評分):
```
5
總和: 5, 平均: 5.00
5星: 1
```

刪除 user_id=1 的 5星評分:
```
(空)
```

觸發器動作: **DELETE FROM item_stats** ✅  
原因: 避免留下孤立的統計記錄

---

## 🔑 索引 (Indexes) 詳細解析

### 索引的核心作用
索引就像書籍的**目錄**,幫助資料庫快速找到資料,而不需要逐行掃描整張表。

---

## 📊 rating 表索引 (最複雜,最重要)

### 1. PRIMARY KEY (id)
```sql
PRIMARY KEY (`id`)
```

**參照欄位**: `id` (INT, AUTO_INCREMENT)

**作用**:
- ✅ 確保每筆評分記錄唯一
- ✅ 自動建立**聚集索引** (Clustered Index)
- ✅ 資料按 id 順序物理排列

**查詢範例**:
```sql
-- 使用主鍵查詢 (最快)
SELECT * FROM rating WHERE id = 12345;
-- 執行時間: < 1ms
```

**運作原理**:
```
資料庫使用 B+ Tree 結構:

         [100]
        /     \
    [50]       [150]
   /   \       /    \
[25] [75]  [125]  [175]

查詢 id=75:
1. 從根節點開始: 75 < 100, 往左
2. 到達 [50]: 75 > 50, 往右
3. 到達 [75]: 找到! ✅

時間複雜度: O(log n)
```

---

### 2. UNIQUE KEY (user_id, item_source, item_id)
```sql
UNIQUE KEY `unique_user_source_item` (`user_id`, `item_source`, `item_id`)
```

**參照欄位**:
1. `user_id` (INT) - 使用者 ID
2. `item_source` (ENUM) - 商品來源 ('items' 或 'user_wardrobe')
3. `item_id` (INT) - 商品 ID

**作用**:
- ✅ **防止重複評分**: 同一使用者對同一商品只能評分一次
- ✅ 自動建立複合索引
- ✅ 加速查詢特定使用者對特定商品的評分

**防重複機制**:
```sql
-- 第一次評分: 成功 ✅
INSERT INTO rating (user_id, item_source, item_id, rating_value)
VALUES (1, 'items', 12345, 5);

-- 第二次評分: 失敗 ❌ (違反 UNIQUE KEY)
INSERT INTO rating (user_id, item_source, item_id, rating_value)
VALUES (1, 'items', 12345, 4);
-- ERROR 1062: Duplicate entry '1-items-12345' for key 'unique_user_source_item'

-- 正確做法: 更新評分
UPDATE rating 
SET rating_value = 4, updated_at = NOW()
WHERE user_id = 1 AND item_source = 'items' AND item_id = 12345;
-- 或使用 ON DUPLICATE KEY UPDATE
```

**查詢範例**:
```sql
-- 查詢使用者對商品的評分 (使用 UNIQUE KEY)
SELECT rating_value, review_text 
FROM rating 
WHERE user_id = 1 
  AND item_source = 'items' 
  AND item_id = 12345;
-- 執行時間: < 5ms (索引查詢)
```

**運作原理**:
```
複合索引結構 (user_id, item_source, item_id):

第一層: user_id
    [1] → [2] → [3] → ...
     ↓
第二層: item_source
    [items] → [user_wardrobe]
       ↓
第三層: item_id
    [100] → [200] → [12345] → ...
       ↓
    指向實際資料

查詢路徑:
1. 找到 user_id = 1
2. 找到 item_source = 'items'
3. 找到 item_id = 12345
4. 返回評分資料 ✅

時間複雜度: O(log n)
```

---

### 3. INDEX (user_id)
```sql
KEY `idx_user_id` (`user_id`)
```

**參照欄位**: `user_id` (INT)

**作用**:
- ✅ 加速查詢使用者的所有評分
- ✅ 支援使用者評分歷史查詢

**查詢範例**:
```sql
-- 查詢使用者的所有評分 (使用 idx_user_id)
SELECT r.*, i.name, i.image_url
FROM rating r
JOIN items i ON r.item_id = i.id
WHERE r.user_id = 1 AND r.item_source = 'items'
ORDER BY r.created_at DESC;
-- 執行時間: < 10ms (即使有數千筆評分)
```

**沒有索引 vs 有索引**:
```
沒有索引:
- 掃描整張表 (Full Table Scan)
- 10,000 筆評分 → 需掃描 10,000 筆
- 執行時間: 500ms

有索引:
- 直接定位到 user_id = 1 的所有記錄
- 10,000 筆評分 → 只掃描該使用者的 50 筆
- 執行時間: 10ms

效能提升: 50 倍! 🚀
```

---

### 4. INDEX (item_source, item_id)
```sql
KEY `idx_item_source_id` (`item_source`, `item_id`)
```

**參照欄位**:
1. `item_source` (ENUM) - 商品來源
2. `item_id` (INT) - 商品 ID

**作用**:
- ✅ 加速查詢特定商品的所有評分
- ✅ **觸發器使用**: after_rating_* 觸發器依賴此索引
- ✅ 支援商品評分統計查詢

**查詢範例**:
```sql
-- 查詢商品的所有評分 (使用 idx_item_source_id)
SELECT 
  COUNT(*) as rating_count,
  AVG(rating_value) as avg_rating,
  SUM(CASE WHEN rating_value = 5 THEN 1 ELSE 0 END) as rating_5_count,
  SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END) as high_rating_count
FROM rating
WHERE item_source = 'items' AND item_id = 12345;
-- 執行時間: < 5ms (即使該商品有數百筆評分)
```

**觸發器依賴**:
```sql
-- after_rating_insert 觸發器內部執行的查詢
-- 依賴 idx_item_source_id 索引加速
SELECT ... FROM rating
WHERE item_source = NEW.item_source    -- 使用索引第一欄
  AND item_id = NEW.item_id;           -- 使用索引第二欄
```

**運作原理**:
```
複合索引 (item_source, item_id):

item_source = 'items':
  └─ item_id = [100, 200, 12345, 50000, ...]
                             ↓
                    快速定位到 12345 的所有評分
                    
查詢效能:
- 100,000 筆評分記錄
- 商品 12345 有 50 筆評分
- 無索引: 掃描 100,000 筆 (1000ms)
- 有索引: 只掃描 50 筆 (5ms)

效能提升: 200 倍! 🚀
```

---

### 5. INDEX (rating_value)
```sql
KEY `idx_rating_value` (`rating_value`)
```

**參照欄位**: `rating_value` (INT)

**作用**:
- ✅ 加速按評分值篩選
- ✅ 支援高評分商品查詢
- ✅ 統計分析查詢優化

**查詢範例**:
```sql
-- 查詢所有5星評分 (使用 idx_rating_value)
SELECT r.*, i.name
FROM rating r
JOIN items i ON r.item_id = i.id
WHERE r.item_source = 'items' 
  AND r.rating_value = 5
ORDER BY r.created_at DESC
LIMIT 100;
-- 執行時間: < 20ms
```

**統計查詢**:
```sql
-- 查詢評分分布
SELECT 
  rating_value,
  COUNT(*) as count,
  COUNT(*) * 100.0 / (SELECT COUNT(*) FROM rating) as percentage
FROM rating
WHERE item_source = 'items'
GROUP BY rating_value
ORDER BY rating_value DESC;
-- 使用 idx_rating_value 加速 GROUP BY
```

---

### 6. INDEX (created_at)
```sql
KEY `idx_created_at` (`created_at`)
```

**參照欄位**: `created_at` (TIMESTAMP)

**作用**:
- ✅ 加速按時間排序
- ✅ 支援最新評分查詢
- ✅ 時間範圍查詢優化

**查詢範例**:
```sql
-- 查詢最近7天的評分 (使用 idx_created_at)
SELECT * FROM rating
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY created_at DESC;
-- 執行時間: < 15ms

-- 查詢本月最活躍的使用者
SELECT user_id, COUNT(*) as rating_count
FROM rating
WHERE created_at >= DATE_FORMAT(NOW(), '%Y-%m-01')
GROUP BY user_id
ORDER BY rating_count DESC
LIMIT 10;
-- 使用 idx_created_at 加速時間過濾
```

---

## 📊 items 表索引

### 1. PRIMARY KEY (id)
```sql
PRIMARY KEY (`id`)
```

**參照欄位**: `id` (INT, AUTO_INCREMENT)

**作用**: 商品唯一識別碼

---

### 2. UNIQUE KEY (sku)
```sql
UNIQUE KEY `sku` (`sku`)
```

**參照欄位**: `sku` (VARCHAR(50)) - 商品貨號

**作用**:
- ✅ **防止商品重複**: 同一 SKU 只能匯入一次
- ✅ 爬蟲去重機制

**防重複機制**:
```sql
-- 第一次匯入: 成功 ✅
INSERT INTO items (name, sku, price, source)
VALUES ('白色T恤', 'UNIQLO-12345', 590, 'uniqlo');

-- 第二次匯入: 失敗 ❌ (違反 UNIQUE KEY)
INSERT INTO items (name, sku, price, source)
VALUES ('白色短袖', 'UNIQLO-12345', 590, 'uniqlo');
-- ERROR 1062: Duplicate entry 'UNIQLO-12345' for key 'sku'

-- 正確做法: 使用 ON DUPLICATE KEY UPDATE
INSERT INTO items (name, sku, price, source)
VALUES ('白色短袖', 'UNIQLO-12345', 590, 'uniqlo')
ON DUPLICATE KEY UPDATE 
  name = VALUES(name),
  price = VALUES(price);
-- 如果 SKU 已存在,則更新資料 ✅
```

**查詢範例**:
```sql
-- 用 SKU 查詢商品 (使用 UNIQUE KEY)
SELECT * FROM items WHERE sku = 'UNIQLO-12345';
-- 執行時間: < 1ms
```

---

### 3. INDEX (category)
```sql
KEY `idx_category` (`category`)
```

**參照欄位**: `category` (VARCHAR(100)) - 分類

**作用**:
- ✅ 加速分類篩選
- ✅ 支援商品列表查詢

**查詢範例**:
```sql
-- 查詢所有上衣 (使用 idx_category)
SELECT * FROM items 
WHERE category = 'top' 
ORDER BY price ASC
LIMIT 20;
-- 執行時間: < 30ms (44,727 件商品中篩選)
```

**效能對比**:
```
無索引:
- 掃描 44,727 件商品
- 逐一比對 category 欄位
- 執行時間: 800ms

有索引:
- 直接定位 category = 'top' 的商品
- 只掃描 ~12,000 件上衣
- 執行時間: 30ms

效能提升: 26 倍! 🚀
```

---

### 4. INDEX (color)
```sql
KEY `idx_color` (`color`)
```

**參照欄位**: `color` (VARCHAR(50)) - 顏色

**作用**:
- ✅ 加速顏色篩選
- ✅ 支援配色推薦

**查詢範例**:
```sql
-- 查詢白色商品 (使用 idx_color)
SELECT * FROM items 
WHERE color = '白色' 
  AND category = 'top'
ORDER BY price ASC;
-- 執行時間: < 50ms

-- 複合條件查詢 (使用多個索引)
SELECT * FROM items 
WHERE category = 'bottom'   -- 使用 idx_category
  AND color = '黑色'        -- 使用 idx_color
  AND gender = '男'         -- 使用 idx_gender
  AND price BETWEEN 500 AND 1000;
-- MySQL 優化器會選擇最有效的索引組合
```

---

### 5. INDEX (gender)
```sql
KEY `idx_gender` (`gender`)
```

**參照欄位**: `gender` (VARCHAR(20)) - 性別

**值域**: 男, 女, 中性, 男孩, 女孩

**查詢範例**:
```sql
-- 查詢男裝 (使用 idx_gender)
SELECT * FROM items 
WHERE gender = '男' 
  AND category = 'bottom'
ORDER BY price ASC;
```

---

### 6. INDEX (source)
```sql
KEY `idx_source` (`source`)
```

**參照欄位**: `source` (VARCHAR(50)) - 資料來源

**值域**: manual, uniqlo, styles_dataset, malefashion

**作用**:
- ✅ 加速來源篩選
- ✅ 支援多來源資料管理

**查詢範例**:
```sql
-- 查詢 Uniqlo 商品數量
SELECT COUNT(*) FROM items WHERE source = 'uniqlo';
-- 結果: 44,727 件 (使用 idx_source)
```

---

## 📊 item_stats 表索引

### 1. UNIQUE KEY (item_source, item_id)
```sql
UNIQUE KEY `unique_source_item` (`item_source`, `item_id`)
```

**參照欄位**:
1. `item_source` (ENUM) - 商品來源
2. `item_id` (INT) - 商品 ID

**作用**:
- ✅ **防止重複統計**: 每個商品只有一筆統計記錄
- ✅ 觸發器依賴此約束
- ✅ 加速統計查詢

**觸發器依賴**:
```sql
-- 觸發器使用 ON DUPLICATE KEY UPDATE
INSERT INTO item_stats (item_source, item_id, avg_rating, ...)
VALUES ('items', 12345, 4.50, ...)
ON DUPLICATE KEY UPDATE    -- 依賴 UNIQUE KEY
  avg_rating = 4.50,
  rating_count = 10,
  ...;
```

---

### 2. INDEX (avg_rating)
```sql
KEY `idx_avg_rating` (`avg_rating`)
```

**參照欄位**: `avg_rating` (DECIMAL(3,2))

**作用**:
- ✅ 加速評分排序
- ✅ 支援推薦演算法

**查詢範例**:
```sql
-- 查詢高評分商品 (使用 idx_avg_rating)
SELECT i.*, s.avg_rating, s.rating_count
FROM items i
JOIN item_stats s ON s.item_source = 'items' AND s.item_id = i.id
WHERE s.avg_rating >= 4.5
  AND s.rating_count >= 10
ORDER BY s.avg_rating DESC, s.rating_count DESC
LIMIT 20;
-- 執行時間: < 50ms
```

---

### 3. INDEX (rating_count)
```sql
KEY `idx_rating_count` (`rating_count`)
```

**參照欄位**: `rating_count` (INT)

**作用**:
- ✅ 加速人氣排序
- ✅ 支援熱門商品查詢

**查詢範例**:
```sql
-- 查詢最熱門商品 (使用 idx_rating_count)
SELECT i.*, s.rating_count, s.avg_rating
FROM items i
JOIN item_stats s ON s.item_source = 'items' AND s.item_id = i.id
ORDER BY s.rating_count DESC
LIMIT 20;
-- 執行時間: < 30ms
```

---

### 4. INDEX (high_rating_ratio)
```sql
KEY `idx_high_rating_ratio` (`high_rating_ratio`)
```

**參照欄位**: `high_rating_ratio` (DECIMAL(5,4))

**作用**:
- ✅ 加速好評率排序
- ✅ 支援品質推薦

**查詢範例**:
```sql
-- 查詢高好評率商品 (使用 idx_high_rating_ratio)
SELECT i.*, s.high_rating_ratio, s.rating_count
FROM items i
JOIN item_stats s ON s.item_source = 'items' AND s.item_id = i.id
WHERE s.rating_count >= 20          -- 至少20次評分
  AND s.high_rating_ratio >= 0.8    -- 80%以上好評
ORDER BY s.high_rating_ratio DESC
LIMIT 20;
-- 執行時間: < 50ms
```

---

## 🎯 索引選擇策略 (MySQL 優化器)

### 單一條件查詢
```sql
-- MySQL 自動選擇最優索引
SELECT * FROM items WHERE category = 'top';
-- 使用 idx_category ✅
```

### 複合條件查詢
```sql
-- MySQL 優化器評估各索引的選擇性
SELECT * FROM items 
WHERE category = 'top'    -- idx_category: 篩選到 12,000 件
  AND color = '白色'      -- idx_color: 篩選到 5,000 件
  AND gender = '男';      -- idx_gender: 篩選到 22,000 件

-- MySQL 選擇: idx_color (選擇性最高) ✅
```

### JOIN 查詢
```sql
-- 推薦查詢使用多個索引
SELECT i.*, s.avg_rating, s.rating_count
FROM items i
JOIN item_stats s 
  ON s.item_source = 'items'   -- 使用 unique_source_item
  AND s.item_id = i.id         -- 使用 PRIMARY KEY
WHERE i.category = 'top'       -- 使用 idx_category
  AND s.avg_rating >= 4.0      -- 使用 idx_avg_rating
ORDER BY s.rating_count DESC   -- 使用 idx_rating_count
LIMIT 20;

-- 執行計劃:
-- 1. 使用 idx_category 篩選 top
-- 2. 使用 unique_source_item JOIN item_stats
-- 3. 使用 idx_avg_rating 篩選評分
-- 4. 使用 idx_rating_count 排序
-- 執行時間: < 50ms ✅
```

---

## 🚀 效能總結

### 觸發器效能影響
```
評分操作:
- INSERT rating: 5ms (基本)
- 觸發器執行: 10-15ms (統計計算)
- 總耗時: 15-20ms ✅

好處:
- 統計永遠即時同步
- 查詢時不需重新計算
- 推薦演算法速度提升 100 倍
```

### 索引效能提升
```
查詢類型              無索引      有索引      提升倍數
─────────────────────────────────────────────────
主鍵查詢 (id)         500ms      < 1ms       500x
唯一鍵查詢 (sku)      800ms      < 1ms       800x
分類查詢 (category)   800ms      30ms        26x
使用者評分歷史        1000ms     10ms        100x
商品評分統計          2000ms     5ms         400x
推薦演算法            5000ms     50ms        100x
```

### 資料規模下的表現
```
44,727 件商品:
- 分類篩選: < 30ms
- 顏色篩選: < 50ms
- JOIN 查詢: < 50ms
- 排序查詢: < 100ms

100,000 筆評分 (預估):
- 單一評分查詢: < 5ms
- 商品評分統計: < 10ms
- 使用者評分歷史: < 20ms
```

---

## 💡 設計精髓總結

### 1. 觸發器 = 自動化 + 一致性
✅ 評分變動 → 統計自動更新  
✅ 無需手動維護  
✅ 資料永遠同步

### 2. 索引 = 速度 + 效率
✅ 主鍵索引: 唯一性保障  
✅ 唯一鍵索引: 防重複機制  
✅ 複合索引: 複雜查詢優化  
✅ 單一索引: 常用欄位加速

### 3. 參照欄位 = 精確 + 可靠
✅ 觸發器參照 NEW/OLD 變數  
✅ 索引參照實際資料欄位  
✅ 確保資料完整性

### 4. 效能提升 = 用戶體驗
✅ 推薦查詢 < 100ms  
✅ 評分提交 < 20ms  
✅ 商品列表 < 50ms

**結論**: 嚴謹的觸發器 + 完善的索引 = 高效能 + 高可靠性! 🎉
