-- ============================================================
-- 手動插入 Demo 測試評分資料
-- 在 DBeaver 中執行此腳本
-- ============================================================

USE outfit_db;

-- 獲取 demo_user 的 ID
SET @demo_user_id = (SELECT id FROM users WHERE username = 'demo_user' LIMIT 1);

-- 顯示用戶 ID
SELECT CONCAT('Demo 用戶 ID: ', @demo_user_id) as info;

-- 清除現有的 items 評分 (避免重複)
DELETE FROM rating WHERE user_id = @demo_user_id AND item_source = 'items';

-- ============================================================
-- 插入 10 件高分商品 (4-5星)
-- ============================================================

INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(@demo_user_id, 'items', 5092, 5, '超級喜歡!質感很好!'),
(@demo_user_id, 'items', 5093, 5, '超級喜歡!質感很好!'),
(@demo_user_id, 'items', 5094, 4, '很不錯,推薦!'),
(@demo_user_id, 'items', 5095, 5, '超級喜歡!質感很好!'),
(@demo_user_id, 'items', 5096, 4, '很不錯,推薦!'),
(@demo_user_id, 'items', 5097, 5, '超級喜歡!質感很好!'),
(@demo_user_id, 'items', 5098, 4, '很不錯,推薦!'),
(@demo_user_id, 'items', 5099, 5, '超級喜歡!質感很好!'),
(@demo_user_id, 'items', 5100, 4, '很不錯,推薦!'),
(@demo_user_id, 'items', 5101, 5, '超級喜歡!質感很好!');

-- ============================================================
-- 插入 5 件低分商品 (1-2星)
-- ============================================================

INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(@demo_user_id, 'items', 5102, 2, '不適合我的風格'),
(@demo_user_id, 'items', 5103, 1, '質感一般'),
(@demo_user_id, 'items', 5104, 2, '不適合我的風格'),
(@demo_user_id, 'items', 5105, 1, '質感一般'),
(@demo_user_id, 'items', 5106, 2, '不適合我的風格');

-- ============================================================
-- 插入 3 件中等評分商品 (3星)
-- ============================================================

INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(@demo_user_id, 'items', 5107, 3, '還可以,但不是最愛'),
(@demo_user_id, 'items', 5108, 3, '還可以,但不是最愛'),
(@demo_user_id, 'items', 5109, 3, '還可以,但不是最愛');

-- ============================================================
-- 查看插入結果
-- ============================================================

-- 評分統計
SELECT 
  item_source,
  COUNT(*) as rating_count,
  AVG(rating_value) as avg_rating,
  MIN(rating_value) as min_rating,
  MAX(rating_value) as max_rating,
  SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END) as high_rating_count,
  SUM(CASE WHEN rating_value <= 2 THEN 1 ELSE 0 END) as low_rating_count
FROM rating 
WHERE user_id = @demo_user_id
GROUP BY item_source;

-- 評分詳細列表
SELECT 
  r.id,
  r.item_source,
  r.item_id,
  i.name,
  r.rating_value,
  r.review_text
FROM rating r
LEFT JOIN items i ON r.item_source = 'items' AND r.item_id = i.id
WHERE r.user_id = @demo_user_id AND r.item_source = 'items'
ORDER BY r.rating_value DESC, r.item_id;

-- 統計表狀態
SELECT 
  item_source,
  item_id,
  avg_rating,
  rating_count,
  high_rating_count
FROM item_stats
WHERE item_source = 'items'
ORDER BY avg_rating DESC
LIMIT 10;

-- ============================================================
-- 測試帶權重的推薦查詢
-- ============================================================

-- 無權重推薦 (隨機)
SELECT '=== 無權重推薦 (隨機 10 件) ===' as section;

SELECT 
  id,
  name,
  category,
  color,
  COALESCE(avg_rating, 0) as avg_rating,
  COALESCE(rating_count, 0) as rating_count
FROM v_items_with_ratings
WHERE is_demo = 1
ORDER BY RAND()
LIMIT 10;

-- 有權重推薦 (評分優先)
SELECT '=== 有權重推薦 (評分優先 10 件) ===' as section;

SELECT 
  id,
  name,
  category,
  color,
  avg_rating,
  rating_count,
  rating_weight,
  popularity_weight,
  final_score
FROM v_items_with_ratings
WHERE is_demo = 1
ORDER BY final_score DESC, avg_rating DESC
LIMIT 10;

-- ============================================================
-- 完成!
-- ============================================================

SELECT '✅ Demo 測試資料插入完成!' as status;
SELECT CONCAT('Items 評分: ', COUNT(*), ' 筆') as info 
FROM rating 
WHERE user_id = @demo_user_id AND item_source = 'items';
