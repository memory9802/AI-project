# 評分權重推薦系統設計方案

**專案**: 穿搭推薦聊天機器人  
**目標**: 根據使用者評分調整推薦權重  
**限制**: 學生專案、MVP 模式、需要可錄影的 Demo  
**日期**: 2025-12-09

---

## 📋 目錄

1. [系統概述](#系統概述)
2. [資料庫結構設計](#資料庫結構設計)
3. [權重計算邏輯](#權重計算邏輯)
4. [Demo 展示方案](#demo-展示方案)
5. [實作步驟](#實作步驟)
6. [技術細節](#技術細節)

---

## 🎯 系統概述

### 核心需求
- ✅ 使用者對推薦的單品評分 (1-5 星)
- ✅ 評分影響後續推薦權重
- ✅ 支援 `items` 和 `user_wardrobe` 兩個來源
- ✅ 維持 MVP (最小可行性)
- ✅ 展示時能直觀呈現權重影響

### 挑戰
- ❌ 數萬筆資料難以在短時間內顯示權重變化
- ❌ 需要多次互動才能累積評分
- ❌ 算力和時間有限

### 解決策略
✅ **小範圍測試集 + 加權查詢**  
✅ **模擬歷史評分資料**  
✅ **視覺化權重變化**

---

## 📊 資料庫結構設計

### 方案 A: 最小調整 (推薦 ⭐⭐⭐⭐⭐)

**優點**: 現有 `rating` 表格已足夠,只需新增查詢邏輯  
**實作難度**: ⭐⭐ (簡單)  
**Demo 效果**: ⭐⭐⭐⭐ (良好)

#### 1. 現有 `rating` 表格 (已存在,無需修改)

```sql
CREATE TABLE rating (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  item_id INT NOT NULL,                    -- 關鍵: 只支援 items 表格
  rating_value INT NOT NULL,               -- 1-5 星
  review_text TEXT DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
  
  UNIQUE KEY unique_user_item (user_id, item_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**⚠️ 限制**: 只能評分 `items` 表格的商品,無法評分 `user_wardrobe` 的個人衣物

#### 2. 新增 `item_stats` 統計表 (輔助查詢性能)

```sql
-- 商品統計表 (快取平均分和評分次數)
CREATE TABLE item_stats (
  item_id INT PRIMARY KEY,
  avg_rating DECIMAL(3,2) DEFAULT 0.00,   -- 平均評分
  rating_count INT DEFAULT 0,              -- 評分次數
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
  INDEX idx_avg_rating (avg_rating DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**用途**: 避免每次查詢都計算平均分,提升性能

---

### 方案 B: 完整擴展 (支援 user_wardrobe)

**優點**: 支援評分個人衣櫃的衣物  
**實作難度**: ⭐⭐⭐ (中等)  
**Demo 效果**: ⭐⭐⭐⭐⭐ (完美)

#### 1. 擴展 `rating` 表格

```sql
DROP TABLE IF EXISTS rating;
CREATE TABLE rating (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  
  -- 多態關聯: 支援兩種來源
  item_source VARCHAR(20) NOT NULL COMMENT 'items 或 user_wardrobe',
  item_id INT NOT NULL,                    -- items.id 或 user_wardrobe.id
  
  rating_value INT NOT NULL CHECK (rating_value BETWEEN 1 AND 5),
  review_text TEXT DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  
  INDEX idx_user_id (user_id),
  INDEX idx_item_source_id (item_source, item_id),
  INDEX idx_rating_value (rating_value),
  
  UNIQUE KEY unique_user_source_item (user_id, item_source, item_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**關鍵設計**:
- `item_source`: 標記來源 (`'items'` 或 `'user_wardrobe'`)
- `item_id`: 對應的商品 ID
- 組合唯一鍵: 同一用戶對同一來源的同一商品只能評分一次

#### 2. 統一統計視圖 (View)

```sql
-- 統一的商品評分統計視圖
CREATE VIEW v_item_ratings AS
SELECT 
  item_source,
  item_id,
  AVG(rating_value) as avg_rating,
  COUNT(*) as rating_count,
  SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END) as high_rating_count
FROM rating
GROUP BY item_source, item_id;
```

---

## 🧮 權重計算邏輯

### 推薦排序公式

```python
# 綜合評分 = 基礎相關度 × 評分權重 × 熱度權重
final_score = base_relevance * rating_weight * popularity_weight

# 1. 基礎相關度 (0-100)
#    - 類別匹配: +40
#    - 顏色匹配: +20
#    - 關鍵字匹配: +20
#    - 場合匹配: +20

# 2. 評分權重 (0.5 - 1.5)
#    - 無評分: 1.0 (中性)
#    - 1-2星: 0.5 (降低)
#    - 3星: 0.9 (略降)
#    - 4星: 1.2 (提升)
#    - 5星: 1.5 (大幅提升)

# 3. 熱度權重 (1.0 - 1.3)
#    - 評分次數 >= 10: 1.3
#    - 評分次數 5-9: 1.2
#    - 評分次數 1-4: 1.1
#    - 無評分: 1.0
```

### SQL 查詢範例

```sql
-- 帶權重的推薦查詢
SELECT 
  i.*,
  COALESCE(s.avg_rating, 0) as avg_rating,
  COALESCE(s.rating_count, 0) as rating_count,
  
  -- 計算評分權重
  CASE 
    WHEN s.avg_rating IS NULL THEN 1.0
    WHEN s.avg_rating >= 4.5 THEN 1.5
    WHEN s.avg_rating >= 3.5 THEN 1.2
    WHEN s.avg_rating >= 2.5 THEN 0.9
    ELSE 0.5
  END as rating_weight,
  
  -- 計算熱度權重
  CASE 
    WHEN s.rating_count >= 10 THEN 1.3
    WHEN s.rating_count >= 5 THEN 1.2
    WHEN s.rating_count >= 1 THEN 1.1
    ELSE 1.0
  END as popularity_weight

FROM items i
LEFT JOIN item_stats s ON i.id = s.item_id
WHERE i.category = 'top'
ORDER BY 
  (rating_weight * popularity_weight) DESC,  -- 權重優先
  i.created_at DESC                          -- 新品次之
LIMIT 10;
```

---

## 🎬 Demo 展示方案

### 方案 1: 小範圍測試集 (推薦 ⭐⭐⭐⭐⭐)

**策略**: 建立 20-30 件精選測試集,預先設定評分

#### Step 1: 建立測試用戶

```sql
-- 插入 Demo 測試用戶
INSERT INTO users (username, email, password_hash, favorite_style) VALUES
('demo_user', 'demo@test.com', '$2b$12$dummy', '休閒');

SET @demo_user_id = LAST_INSERT_ID();
```

#### Step 2: 建立精選測試集 (標記 Demo 用商品)

```sql
-- 方法 A: 在 items 表格新增 is_demo 欄位
ALTER TABLE items ADD COLUMN is_demo BOOLEAN DEFAULT FALSE;

-- 標記 30 件測試商品
UPDATE items 
SET is_demo = TRUE 
WHERE category = 'top' 
  AND color IN ('白色', '黑色', '藍色')
LIMIT 30;
```

#### Step 3: 插入預設評分資料

```sql
-- 插入模擬的歷史評分
-- 10 件高分商品 (4-5星)
INSERT INTO rating (user_id, item_id, rating_value, review_text)
SELECT 
  @demo_user_id,
  id,
  FLOOR(4 + RAND() * 2),  -- 4-5星
  '很喜歡這件!'
FROM items 
WHERE is_demo = TRUE AND category = 'top' 
ORDER BY RAND() 
LIMIT 10;

-- 5 件低分商品 (1-2星)
INSERT INTO rating (user_id, item_id, rating_value, review_text)
SELECT 
  @demo_user_id,
  id,
  FLOOR(1 + RAND() * 2),  -- 1-2星
  '不太適合'
FROM items 
WHERE is_demo = TRUE 
  AND category = 'top'
  AND id NOT IN (SELECT item_id FROM rating WHERE user_id = @demo_user_id)
ORDER BY RAND() 
LIMIT 5;

-- 更新統計表
INSERT INTO item_stats (item_id, avg_rating, rating_count)
SELECT item_id, AVG(rating_value), COUNT(*)
FROM rating
WHERE user_id = @demo_user_id
GROUP BY item_id
ON DUPLICATE KEY UPDATE 
  avg_rating = VALUES(avg_rating),
  rating_count = VALUES(rating_count);
```

#### Step 4: Demo 錄影腳本

```markdown
📹 錄影流程 (約 3-5 分鐘)

1. **開場**: 展示測試集 (30 件上衣)
   - 顯示 phpMyAdmin 中的 items 表格 (is_demo = TRUE)
   - 說明: "我們準備了 30 件測試商品"

2. **查看初始評分**:
   - 執行 SQL: `SELECT * FROM rating WHERE user_id = @demo_user_id;`
   - 展示: 10 件高分、5 件低分

3. **第一次推薦 (無權重)**:
   - API: `/aichat/items?category=top&use_rating=false`
   - 結果: 隨機 10 件商品

4. **第二次推薦 (有權重)**:
   - API: `/aichat/items?category=top&use_rating=true`
   - 結果: 高分商品優先出現!

5. **即時評分測試**:
   - 選擇一件未評分的商品
   - 前端評分 5 星
   - 再次查詢 → 該商品排名上升!

6. **統計資料展示**:
   - 執行 SQL: 
     ```sql
     SELECT 
       i.name, 
       s.avg_rating, 
       s.rating_count,
       CASE WHEN s.avg_rating >= 4 THEN '高分推薦' ELSE '一般' END as tag
     FROM items i
     LEFT JOIN item_stats s ON i.id = s.item_id
     WHERE i.is_demo = TRUE
     ORDER BY s.avg_rating DESC;
     ```
```

---

### 方案 2: 視覺化對比 (推薦 ⭐⭐⭐⭐)

**策略**: 建立對比頁面,並排顯示有/無權重的推薦結果

#### 前端介面設計

```
┌────────────────────────────────────────────────────────┐
│         聊天機器人推薦系統 - 權重影響測試              │
├────────────────────────┬───────────────────────────────┤
│   無權重推薦 (隨機)     │    有權重推薦 (評分優先)      │
├────────────────────────┼───────────────────────────────┤
│ 1. 商品 A (未評分)      │ 1. 商品 X (5星, ⭐⭐⭐⭐⭐)     │
│ 2. 商品 B (2星)         │ 2. 商品 Y (5星, ⭐⭐⭐⭐⭐)     │
│ 3. 商品 C (5星)         │ 3. 商品 Z (4星, ⭐⭐⭐⭐)       │
│ 4. 商品 D (未評分)      │ 4. 商品 W (4星, ⭐⭐⭐⭐)       │
│ ...                     │ ...                           │
└────────────────────────┴───────────────────────────────┘

      ↓ 點擊商品 B 評分為 5 星後重新查詢 ↓

┌────────────────────────────────────────────────────────┐
│ 1. 商品 D (未評分)      │ 1. 商品 X (5星, ⭐⭐⭐⭐⭐)     │
│ 2. 商品 A (未評分)      │ 2. 商品 B (5星, ⭐⭐⭐⭐⭐) ⬆️  │ <- 排名上升!
│ 3. 商品 E (3星)         │ 3. 商品 Y (5星, ⭐⭐⭐⭐⭐)     │
│ 4. 商品 C (5星)         │ 4. 商品 Z (4星, ⭐⭐⭐⭐)       │
└────────────────────────┴───────────────────────────────┘
```

---

### 方案 3: 極簡 Demo (推薦 ⭐⭐⭐)

**策略**: 只測試 5 件商品,完全手動控制

#### 超級精簡流程

```sql
-- 1. 準備 5 件商品
CREATE TEMPORARY TABLE demo_items AS
SELECT * FROM items 
WHERE category = 'top' 
ORDER BY RAND() 
LIMIT 5;

-- 2. 給 3 件商品評高分
INSERT INTO rating (user_id, item_id, rating_value)
SELECT 1, id, 5 FROM demo_items LIMIT 3;

-- 3. 查詢對比
-- 無權重
SELECT name FROM demo_items ORDER BY RAND();

-- 有權重
SELECT i.name, COALESCE(r.rating_value, 0) as rating
FROM demo_items i
LEFT JOIN rating r ON i.id = r.item_id
ORDER BY rating DESC;
```

---

## 🔧 實作步驟

### 階段 1: 資料庫調整 (1-2 小時)

```bash
# 1. 備份現有資料庫
docker exec outfit-mysql mysqldump -uroot -prootpassword outfit_db > backup_$(date +%Y%m%d).sql

# 2. 執行新增統計表 (方案 A)
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < add_item_stats.sql

# 3. 插入測試資料
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < demo_data.sql
```

### 階段 2: 後端 API 開發 (2-3 小時)

**新增檔案**: `app/blueprints/aichat/rating_service.py`

```python
"""評分權重推薦服務"""

def get_weighted_items(category: str, user_id: int = None, limit: int = 10):
    """
    帶權重的商品推薦
    
    Args:
        category: 商品類別
        user_id: 用戶ID (可選)
        limit: 回傳數量
    
    Returns:
        List[dict]: 加權排序的商品列表
    """
    conn = get_db_conn()
    try:
        with conn.cursor() as cur:
            sql = """
            SELECT 
              i.*,
              COALESCE(s.avg_rating, 0) as avg_rating,
              COALESCE(s.rating_count, 0) as rating_count,
              
              -- 評分權重
              CASE 
                WHEN s.avg_rating IS NULL THEN 1.0
                WHEN s.avg_rating >= 4.5 THEN 1.5
                WHEN s.avg_rating >= 3.5 THEN 1.2
                WHEN s.avg_rating >= 2.5 THEN 0.9
                ELSE 0.5
              END as rating_weight,
              
              -- 熱度權重
              CASE 
                WHEN s.rating_count >= 10 THEN 1.3
                WHEN s.rating_count >= 5 THEN 1.2
                WHEN s.rating_count >= 1 THEN 1.1
                ELSE 1.0
              END as popularity_weight,
              
              -- 最終評分
              (CASE 
                WHEN s.avg_rating IS NULL THEN 1.0
                WHEN s.avg_rating >= 4.5 THEN 1.5
                WHEN s.avg_rating >= 3.5 THEN 1.2
                WHEN s.avg_rating >= 2.5 THEN 0.9
                ELSE 0.5
              END * 
              CASE 
                WHEN s.rating_count >= 10 THEN 1.3
                WHEN s.rating_count >= 5 THEN 1.2
                WHEN s.rating_count >= 1 THEN 1.1
                ELSE 1.0
              END) as final_score
              
            FROM items i
            LEFT JOIN item_stats s ON i.id = s.item_id
            WHERE i.category = %s
            ORDER BY final_score DESC, i.created_at DESC
            LIMIT %s
            """
            cur.execute(sql, (category, limit))
            return cur.fetchall()
    finally:
        conn.close()


def submit_rating(user_id: int, item_id: int, rating_value: int, review_text: str = None):
    """提交評分"""
    conn = get_db_conn()
    try:
        with conn.cursor() as cur:
            # 插入或更新評分
            sql = """
            INSERT INTO rating (user_id, item_id, rating_value, review_text)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
              rating_value = VALUES(rating_value),
              review_text = VALUES(review_text),
              updated_at = CURRENT_TIMESTAMP
            """
            cur.execute(sql, (user_id, item_id, rating_value, review_text))
            
            # 更新統計表
            sql = """
            INSERT INTO item_stats (item_id, avg_rating, rating_count)
            SELECT item_id, AVG(rating_value), COUNT(*)
            FROM rating
            WHERE item_id = %s
            GROUP BY item_id
            ON DUPLICATE KEY UPDATE 
              avg_rating = VALUES(avg_rating),
              rating_count = VALUES(rating_count)
            """
            cur.execute(sql, (item_id,))
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 評分失敗: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()
```

**新增 API 端點**: `app/blueprints/aichat/routes.py`

```python
@aichat_bp.route("/items_weighted", methods=["GET"])
def get_items_weighted():
    """帶權重的商品查詢 API"""
    category = request.args.get("category")
    user_id = request.args.get("user_id", type=int)
    use_rating = request.args.get("use_rating", "true").lower() == "true"
    
    if use_rating:
        items = get_weighted_items(category, user_id, limit=10)
    else:
        # 無權重查詢 (原邏輯)
        items = get_items_random(category, limit=10)
    
    return jsonify(items)


@aichat_bp.route("/submit_rating", methods=["POST"])
def submit_rating_api():
    """提交評分 API"""
    data = request.json
    user_id = data.get("user_id")
    item_id = data.get("item_id")
    rating_value = data.get("rating_value")
    review_text = data.get("review_text")
    
    if not all([user_id, item_id, rating_value]):
        return jsonify({"error": "缺少必要參數"}), 400
    
    if not (1 <= rating_value <= 5):
        return jsonify({"error": "評分必須在 1-5 之間"}), 400
    
    success = submit_rating(user_id, item_id, rating_value, review_text)
    
    if success:
        return jsonify({"success": True, "message": "評分成功"})
    else:
        return jsonify({"error": "評分失敗"}), 500
```

### 階段 3: 前端整合 (組員負責,2-3 小時)

**評分按鈕組件**:
```javascript
// 評分按鈕 (1-5星)
function RatingButton({ itemId, currentRating, onRate }) {
  return (
    <div className="rating-stars">
      {[1, 2, 3, 4, 5].map(star => (
        <button 
          key={star}
          className={star <= currentRating ? 'star-filled' : 'star-empty'}
          onClick={() => onRate(itemId, star)}
        >
          ⭐
        </button>
      ))}
    </div>
  );
}

// 提交評分
async function submitRating(itemId, ratingValue) {
  const response = await fetch('/aichat/submit_rating', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      user_id: getCurrentUserId(),
      item_id: itemId,
      rating_value: ratingValue
    })
  });
  
  if (response.ok) {
    alert('評分成功!');
    refreshRecommendations(); // 重新查詢推薦
  }
}
```

---

## 📈 Demo 錄影建議

### 完整 Demo 流程 (5 分鐘)

```markdown
🎬 場景 1: 系統介紹 (30秒)
- 展示聊天機器人介面
- 說明: "我們的系統會根據使用者評分調整推薦優先順序"

🎬 場景 2: 查看測試資料 (1分鐘)
- 打開 phpMyAdmin
- 展示 rating 表格: "我們預先插入了 15 筆測試評分"
- 展示 item_stats 表格: "統計了每件商品的平均分和評分次數"

🎬 場景 3: 無權重推薦 (1分鐘)
- 輸入: "推薦上衣"
- API: /aichat/items?category=top&use_rating=false
- 結果: 顯示 10 件隨機商品 (包含低分商品)
- 說明: "注意第 3 件是 2 星商品"

🎬 場景 4: 有權重推薦 (1分鐘)
- 輸入: "推薦上衣"
- API: /aichat/items?category=top&use_rating=true
- 結果: 顯示 10 件高分優先商品
- 說明: "現在前 5 件都是 4-5 星商品!低分商品被排到後面了"

🎬 場景 5: 即時評分測試 (1.5分鐘)
- 選擇一件未評分的商品
- 點擊評分: 5 星
- 再次查詢推薦
- 說明: "剛評分的商品從第 8 名上升到第 2 名!"

🎬 場景 6: 統計資料展示 (30秒)
- 執行 SQL 查詢統計
- 展示評分分布圖表
- 總結: "評分系統成功影響推薦排序"
```

---

## ✅ 優勢分析

### 方案 A (推薦)

✅ **實作簡單**: 只需新增 1 個統計表 + 2 個 API  
✅ **性能優良**: 使用快取統計,查詢速度快  
✅ **Demo 效果好**: 小範圍測試集容易展示  
✅ **維持 MVP**: 不影響現有功能  
✅ **可錄影性高**: 清晰的前後對比

### 相較於複雜方案

❌ 不需要機器學習模型 (節省算力)  
❌ 不需要大量歷史資料 (手動模擬即可)  
❌ 不需要複雜的協同過濾 (簡單加權足夠)

---

## 🚀 快速啟動指南

### 1 小時 Quick Start

```bash
# 1. 建立統計表 (2 分鐘)
cat > add_stats.sql << EOF
CREATE TABLE item_stats (
  item_id INT PRIMARY KEY,
  avg_rating DECIMAL(3,2) DEFAULT 0.00,
  rating_count INT DEFAULT 0,
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
  INDEX idx_avg_rating (avg_rating DESC)
);
EOF

docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < add_stats.sql

# 2. 插入測試評分 (5 分鐘)
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
INSERT INTO rating (user_id, item_id, rating_value)
SELECT 1, id, FLOOR(4 + RAND() * 2)
FROM items WHERE category = 'top' ORDER BY RAND() LIMIT 10;

INSERT INTO item_stats (item_id, avg_rating, rating_count)
SELECT item_id, AVG(rating_value), COUNT(*)
FROM rating GROUP BY item_id;
"

# 3. 測試查詢 (3 分鐘)
curl "http://localhost:5001/aichat/items?category=top&use_rating=false"
curl "http://localhost:5001/aichat/items?category=top&use_rating=true"

# 4. 開始錄影! 🎬
```

---

## 💡 補充建議

### 評分來源多樣化

```python
# 除了手動評分,還可以:
# 1. 點擊次數作為隱式評分
# 2. 加入購物車 = 自動 4 星
# 3. 分享商品 = 自動 5 星
# 4. 停留時間 > 10秒 = +1 星
```

### 視覺化增強

```javascript
// 前端顯示權重標籤
<div className="item-card">
  <img src={item.image_url} />
  <h3>{item.name}</h3>
  
  {/* 評分標籤 */}
  {item.avg_rating >= 4 && (
    <span className="badge-hot">🔥 高分推薦</span>
  )}
  
  {/* 權重提示 */}
  <p className="weight-info">
    權重: {item.final_score.toFixed(2)}
    (評分 {item.rating_weight.toFixed(1)}x × 熱度 {item.popularity_weight.toFixed(1)}x)
  </p>
</div>
```

---

## 📝 總結

### 推薦採用: **方案 A + Demo 方案 1**

**理由**:
1. ✅ 實作時間短 (1-2 天完成)
2. ✅ Demo 效果直觀 (小範圍測試集)
3. ✅ 不影響現有系統 (MVP 維持)
4. ✅ 可錄影性高 (清晰對比)
5. ✅ 符合學生專案限制

**時程規劃**:
- Day 1: 資料庫調整 + 後端 API (3-4 小時)
- Day 2: 前端整合 + 測試資料 (3-4 小時)
- Day 3: Demo 錄影 + 微調 (2-3 小時)

**預期成果**:
- ✅ 完整的評分權重系統
- ✅ 可錄影的 Demo 影片
- ✅ 清晰的前後對比效果
- ✅ 維持系統穩定性

---

**文件版本**: v1.0  
**建立日期**: 2025-12-09  
**作者**: GitHub Copilot  
**專案**: stylerec 穿搭推薦系統
