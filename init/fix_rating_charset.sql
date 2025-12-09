-- ============================================================
-- 修正 user_wardrobe 評論亂碼問題
-- 在 DBeaver 中執行此腳本
-- ============================================================

USE outfit_db;

-- ============================================================
-- 方法 1: 直接更新現有的亂碼評論為正確的中文
-- ============================================================

-- 獲取 demo_user 的 ID
SET @demo_user_id = (SELECT id FROM users WHERE username = 'demo_user' LIMIT 1);

-- 更新所有 user_wardrobe 的評論
UPDATE rating 
SET review_text = CASE 
    WHEN rating_value >= 4 THEN '我的衣櫃最愛!'
    WHEN rating_value <= 2 THEN '買錯了,不常穿'
    ELSE '還不錯'
END
WHERE user_id = @demo_user_id 
  AND item_source = 'user_wardrobe';

-- 查看更新結果
SELECT 
  r.id,
  r.item_source,
  r.item_id,
  w.item_name,
  r.rating_value,
  r.review_text,
  HEX(r.review_text) as hex_value  -- 顯示十六進位編碼
FROM rating r
LEFT JOIN user_wardrobe w ON r.item_source = 'user_wardrobe' AND r.item_id = w.id
WHERE r.user_id = @demo_user_id 
  AND r.item_source = 'user_wardrobe'
ORDER BY r.rating_value DESC;

-- ============================================================
-- 方法 2: 檢查並修正表格字符集 (如果方法1無效)
-- ============================================================

-- 查看當前 rating 表格的字符集
SELECT 
  TABLE_NAME,
  TABLE_COLLATION,
  CCSA.CHARACTER_SET_NAME
FROM information_schema.TABLES T,
     information_schema.COLLATION_CHARACTER_SET_APPLICABILITY CCSA
WHERE CCSA.collation_name = T.table_collation
  AND T.table_schema = 'outfit_db'
  AND T.table_name = 'rating';

-- 查看 review_text 欄位的字符集
SELECT 
  COLUMN_NAME,
  CHARACTER_SET_NAME,
  COLLATION_NAME,
  DATA_TYPE
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'outfit_db'
  AND TABLE_NAME = 'rating'
  AND COLUMN_NAME = 'review_text';

-- 如果字符集不是 utf8mb4,修正它
ALTER TABLE rating 
MODIFY COLUMN review_text TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL;

-- ============================================================
-- 方法 3: 刪除並重新插入正確編碼的資料
-- ============================================================

-- 刪除 user_wardrobe 的評分
DELETE FROM rating 
WHERE user_id = @demo_user_id 
  AND item_source = 'user_wardrobe';

-- 重新插入 (使用 utf8mb4 編碼)
SET NAMES utf8mb4;

-- 為 5 件衣櫃商品評分 (高分)
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text)
SELECT 
  @demo_user_id,
  'user_wardrobe',
  id,
  5,
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
  1,
  '買錯了,不常穿'
FROM user_wardrobe
WHERE user_id = @demo_user_id
  AND id NOT IN (SELECT item_id FROM rating WHERE user_id = @demo_user_id AND item_source = 'user_wardrobe')
ORDER BY RAND() 
LIMIT 2;

-- ============================================================
-- 驗證修正結果
-- ============================================================

-- 查看所有評分 (按來源分組)
SELECT 
  item_source,
  COUNT(*) as count,
  GROUP_CONCAT(DISTINCT review_text SEPARATOR ' | ') as sample_reviews
FROM rating
WHERE user_id = @demo_user_id
GROUP BY item_source;

-- 詳細檢查 user_wardrobe 評論
SELECT 
  r.id,
  r.item_source,
  r.item_id,
  w.item_name,
  r.rating_value,
  r.review_text,
  LENGTH(r.review_text) as text_length,
  CHAR_LENGTH(r.review_text) as char_length  -- 如果不同表示有多位元字符
FROM rating r
LEFT JOIN user_wardrobe w ON r.item_source = 'user_wardrobe' AND r.item_id = w.id
WHERE r.user_id = @demo_user_id 
  AND r.item_source = 'user_wardrobe'
ORDER BY r.rating_value DESC;

-- 對比 items 評論
SELECT 
  r.id,
  r.item_source,
  r.item_id,
  i.name,
  r.rating_value,
  r.review_text,
  LENGTH(r.review_text) as text_length,
  CHAR_LENGTH(r.review_text) as char_length
FROM rating r
LEFT JOIN items i ON r.item_source = 'items' AND r.item_id = i.id
WHERE r.user_id = @demo_user_id 
  AND r.item_source = 'items'
ORDER BY r.rating_value DESC
LIMIT 5;

-- ============================================================
-- 完成!
-- ============================================================

SELECT '✅ 字符集修正完成!' as status;
SELECT CONCAT('user_wardrobe 評分: ', COUNT(*), ' 筆') as info 
FROM rating 
WHERE user_id = @demo_user_id AND item_source = 'user_wardrobe';
