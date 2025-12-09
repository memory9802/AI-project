-- ============================================================
-- Demo 測試資料插入腳本
-- ============================================================
-- 專案: stylerec 穿搭推薦系統
-- 日期: 2025-12-09
-- 用途: 為評分權重系統準備測試資料和 Demo 展示資料
-- ============================================================

USE outfit_db;

-- ============================================================
-- STEP 1: 建立 Demo 測試用戶
-- ============================================================

-- 插入測試用戶 (如果不存在)
INSERT IGNORE INTO users (username, email, password_hash, favorite_style, created_at)
VALUES 
('demo_user', 'demo@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5K/jNYi0i7FDO', '休閒', NOW());

-- 獲取 demo_user 的 ID
SET @demo_user_id = (SELECT id FROM users WHERE username = 'demo_user' LIMIT 1);

SELECT CONCAT('✅ Demo 用戶 ID: ', @demo_user_id) as status;

-- ============================================================
-- STEP 2: 在 items 表格新增 is_demo 欄位 (標記測試商品)
-- ============================================================

-- 檢查欄位是否存在
SET @column_exists = (
  SELECT COUNT(*)
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = 'outfit_db'
    AND TABLE_NAME = 'items'
    AND COLUMN_NAME = 'is_demo'
);

-- 如果欄位不存在,則新增
SET @sql = IF(@column_exists = 0,
  'ALTER TABLE items ADD COLUMN is_demo BOOLEAN DEFAULT FALSE COMMENT "是否為 Demo 測試商品"',
  'SELECT "欄位 is_demo 已存在" as status'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================
-- STEP 3: 標記 30 件測試商品 (上衣類別)
-- ============================================================

-- 重置所有 is_demo 標記
UPDATE items SET is_demo = FALSE;

-- 標記 30 件上衣作為測試商品
-- 選擇多種顏色,確保有足夠的多樣性
UPDATE items 
SET is_demo = TRUE 
WHERE category = 'top' 
  AND color IN ('白色', '黑色', '藍色', '灰色', '米色')
ORDER BY RAND() 
LIMIT 30;

-- 顯示標記的測試商品
SELECT COUNT(*) as demo_items_count FROM items WHERE is_demo = TRUE;

SELECT id, name, category, color, price, image_url
FROM items 
WHERE is_demo = TRUE 
ORDER BY color, id
LIMIT 10;

-- ============================================================
-- STEP 4: 插入模擬評分資料 (items 來源)
-- ============================================================

-- 清空現有的 Demo 用戶評分 (避免重複執行時出錯)
DELETE FROM rating WHERE user_id = @demo_user_id;

-- 插入 10 件高分商品 (4-5星)
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text)
SELECT 
  @demo_user_id,
  'items',
  id,
  FLOOR(4 + RAND() * 2),  -- 4 或 5 星
  CASE 
    WHEN FLOOR(4 + RAND() * 2) = 5 THEN '超級喜歡!質感很好!'
    ELSE '很不錯,推薦!'
  END
FROM items 
WHERE is_demo = TRUE AND category = 'top' 
ORDER BY RAND() 
LIMIT 10;

-- 插入 5 件低分商品 (1-2星)
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text)
SELECT 
  @demo_user_id,
  'items',
  id,
  FLOOR(1 + RAND() * 2),  -- 1 或 2 星
  CASE 
    WHEN FLOOR(1 + RAND() * 2) = 1 THEN '不適合我的風格'
    ELSE '質感一般'
  END
FROM items 
WHERE is_demo = TRUE 
  AND category = 'top'
  AND id NOT IN (SELECT item_id FROM rating WHERE user_id = @demo_user_id AND item_source = 'items')
ORDER BY RAND() 
LIMIT 5;

-- 插入 3 件中等評分商品 (3星)
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text)
SELECT 
  @demo_user_id,
  'items',
  id,
  3,
  '還可以,但不是最愛'
FROM items 
WHERE is_demo = TRUE 
  AND category = 'top'
  AND id NOT IN (SELECT item_id FROM rating WHERE user_id = @demo_user_id AND item_source = 'items')
ORDER BY RAND() 
LIMIT 3;

-- 顯示插入的評分統計
SELECT 
  rating_value,
  COUNT(*) as count,
  GROUP_CONCAT(SUBSTRING(review_text, 1, 20) SEPARATOR ', ') as sample_reviews
FROM rating 
WHERE user_id = @demo_user_id AND item_source = 'items'
GROUP BY rating_value
ORDER BY rating_value DESC;

-- ============================================================
-- STEP 5: 建立測試用的 user_wardrobe 資料
-- ============================================================

-- 插入一些用戶上傳的衣物到 demo_user 的個人衣櫃
INSERT IGNORE INTO user_wardrobe (user_id, item_name, category, color, image_url, uploaded_at)
VALUES 
  (@demo_user_id, '我的白色T恤', 'top', '白色', 'https://example.com/my_tshirt.jpg', NOW()),
  (@demo_user_id, '我的牛仔褲', 'bottom', '藍色', 'https://example.com/my_jeans.jpg', NOW()),
  (@demo_user_id, '我的黑色外套', 'top', '黑色', 'https://example.com/my_jacket.jpg', NOW()),
  (@demo_user_id, '我的運動鞋', 'shoes', '白色', 'https://example.com/my_sneakers.jpg', NOW()),
  (@demo_user_id, '我的休閒褲', 'bottom', '卡其色', 'https://example.com/my_pants.jpg', NOW()),
  (@demo_user_id, '我的條紋衫', 'top', '條紋', 'https://example.com/my_striped.jpg', NOW()),
  (@demo_user_id, '我的帆布鞋', 'shoes', '黑色', 'https://example.com/my_canvas.jpg', NOW()),
  (@demo_user_id, '我的衛衣', 'top', '灰色', 'https://example.com/my_hoodie.jpg', NOW()),
  (@demo_user_id, '我的短褲', 'bottom', '黑色', 'https://example.com/my_shorts.jpg', NOW()),
  (@demo_user_id, '我的皮鞋', 'shoes', '棕色', 'https://example.com/my_leather.jpg', NOW());

-- 顯示插入的衣櫃商品
SELECT COUNT(*) as wardrobe_items_count 
FROM user_wardrobe 
WHERE user_id = @demo_user_id;

-- ============================================================
-- STEP 6: 插入 user_wardrobe 的評分資料
-- ============================================================

-- 為 5 件衣櫃商品評分 (高分)
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text)
SELECT 
  @demo_user_id,
  'user_wardrobe',
  id,
  FLOOR(4 + RAND() * 2),  -- 4 或 5 星
  '我的衣櫃最愛!'
FROM user_wardrobe
WHERE user_id = @demo_user_id
ORDER BY RAND() 
LIMIT 5;

-- 為 2 件衣櫃商品評分 (低分)
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text)
SELECT 
  @demo_user_id,
  'user_wardrobe',
  id,
  FLOOR(1 + RAND() * 2),  -- 1 或 2 星
  '買錯了,不常穿'
FROM user_wardrobe
WHERE user_id = @demo_user_id
  AND id NOT IN (SELECT item_id FROM rating WHERE user_id = @demo_user_id AND item_source = 'user_wardrobe')
ORDER BY RAND() 
LIMIT 2;

-- 顯示 user_wardrobe 評分統計
SELECT 
  item_source,
  COUNT(*) as rating_count,
  AVG(rating_value) as avg_rating,
  MIN(rating_value) as min_rating,
  MAX(rating_value) as max_rating
FROM rating 
WHERE user_id = @demo_user_id
GROUP BY item_source;

-- ============================================================
-- STEP 7: 驗證統計表已自動更新 (透過觸發器)
-- ============================================================

-- 檢查 item_stats 表格
SELECT 
  item_source,
  COUNT(*) as stats_count,
  AVG(avg_rating) as overall_avg,
  SUM(rating_count) as total_ratings
FROM item_stats
GROUP BY item_source;

-- 顯示評分最高的 items 商品
SELECT 
  i.id,
  i.name,
  i.category,
  i.color,
  s.avg_rating,
  s.rating_count,
  s.high_rating_count
FROM items i
INNER JOIN item_stats s ON s.item_source = 'items' AND s.item_id = i.id
WHERE i.is_demo = TRUE
ORDER BY s.avg_rating DESC, s.rating_count DESC
LIMIT 10;

-- 顯示 user_wardrobe 評分最高的商品
SELECT 
  w.id,
  w.item_name,
  w.category,
  s.avg_rating,
  s.rating_count
FROM user_wardrobe w
INNER JOIN item_stats s ON s.item_source = 'user_wardrobe' AND s.item_id = w.id
WHERE w.user_id = @demo_user_id
ORDER BY s.avg_rating DESC, s.rating_count DESC
LIMIT 10;

-- ============================================================
-- STEP 8: 測試帶權重的查詢視圖
-- ============================================================

-- 測試 v_items_with_ratings 視圖 (帶權重的 items)
SELECT 
  id,
  name,
  category,
  color,
  price,
  avg_rating,
  rating_count,
  rating_weight,
  popularity_weight,
  final_score
FROM v_items_with_ratings
WHERE is_demo = TRUE
ORDER BY final_score DESC
LIMIT 10;

-- 測試 v_wardrobe_with_ratings 視圖 (帶權重的 user_wardrobe)
SELECT 
  w.id,
  w.item_name,
  w.category,
  w.avg_rating,
  w.rating_count,
  w.rating_weight,
  w.popularity_weight,
  w.final_score
FROM v_wardrobe_with_ratings w
WHERE w.user_id = @demo_user_id
ORDER BY w.final_score DESC
LIMIT 10;

-- ============================================================
-- STEP 9: 產生 Demo 對比資料
-- ============================================================

-- 無權重推薦 (隨機 10 件)
SELECT '=== 無權重推薦 (隨機) ===' as section;

SELECT 
  id,
  name,
  category,
  color,
  price,
  COALESCE(avg_rating, 0) as avg_rating,
  COALESCE(rating_count, 0) as rating_count
FROM v_items_with_ratings
WHERE is_demo = TRUE
ORDER BY RAND()
LIMIT 10;

-- 有權重推薦 (評分優先)
SELECT '=== 有權重推薦 (評分優先) ===' as section;

SELECT 
  id,
  name,
  category,
  color,
  price,
  avg_rating,
  rating_count,
  rating_weight,
  popularity_weight,
  final_score
FROM v_items_with_ratings
WHERE is_demo = TRUE
ORDER BY final_score DESC, avg_rating DESC
LIMIT 10;

-- ============================================================
-- STEP 10: 產生統計報告
-- ============================================================

SELECT '=== Demo 測試資料統計報告 ===' as section;

-- 測試用戶資訊
SELECT 
  '測試用戶' as type,
  @demo_user_id as user_id,
  (SELECT username FROM users WHERE id = @demo_user_id) as username,
  (SELECT email FROM users WHERE id = @demo_user_id) as email;

-- 測試商品統計
SELECT 
  '測試商品' as type,
  COUNT(*) as total_count,
  COUNT(DISTINCT category) as category_count,
  COUNT(DISTINCT color) as color_count
FROM items 
WHERE is_demo = TRUE;

-- 評分統計 (items)
SELECT 
  'items 評分' as type,
  COUNT(*) as rating_count,
  AVG(rating_value) as avg_rating,
  MIN(rating_value) as min_rating,
  MAX(rating_value) as max_rating,
  SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END) as high_rating_count,
  SUM(CASE WHEN rating_value <= 2 THEN 1 ELSE 0 END) as low_rating_count
FROM rating 
WHERE user_id = @demo_user_id AND item_source = 'items';

-- 評分統計 (user_wardrobe)
SELECT 
  'user_wardrobe 評分' as type,
  COUNT(*) as rating_count,
  AVG(rating_value) as avg_rating,
  MIN(rating_value) as min_rating,
  MAX(rating_value) as max_rating,
  SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END) as high_rating_count,
  SUM(CASE WHEN rating_value <= 2 THEN 1 ELSE 0 END) as low_rating_count
FROM rating 
WHERE user_id = @demo_user_id AND item_source = 'user_wardrobe';

-- 統計表記錄數
SELECT 
  '統計表記錄' as type,
  COUNT(*) as total_records,
  SUM(CASE WHEN item_source = 'items' THEN 1 ELSE 0 END) as items_records,
  SUM(CASE WHEN item_source = 'user_wardrobe' THEN 1 ELSE 0 END) as wardrobe_records
FROM item_stats;

-- ============================================================
-- Demo 測試資料插入完成!
-- ============================================================

SELECT '✅ Demo 測試資料插入完成!' as status;
SELECT '📊 你現在可以測試帶權重的推薦查詢了' as next_step;
