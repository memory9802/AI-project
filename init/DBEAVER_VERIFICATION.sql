-- ========================================
-- DBeaver 驗證腳本
-- 請在 DBeaver 中依序執行這些 SQL
-- ========================================

-- 1️⃣ 驗證連接和資料庫
-- ========================================
USE outfit_db;

SELECT 'Database connection OK!' as status;


-- 2️⃣ 檢查所有表格
-- ========================================
SHOW TABLES;


-- 3️⃣ 檢查 items 表結構
-- ========================================
DESCRIBE items;

-- ✅ 應該看到 12 個欄位：
-- id, name, category, color, image_url, created_at, 
-- sku, gender, clothing_type, length, price (DECIMAL!), source


-- 4️⃣ 查看前 10 筆資料
-- ========================================
SELECT 
  id, 
  name, 
  category, 
  color, 
  price,          -- 應該是數字格式
  source 
FROM items 
LIMIT 10;


-- 5️⃣ 統計空值情況
-- ========================================
SELECT 
  'Total Items' as metric,
  COUNT(*) as count,
  '-' as percentage
FROM items

UNION ALL

SELECT 
  'NULL category' as metric,
  SUM(CASE WHEN category IS NULL THEN 1 ELSE 0 END) as count,
  CONCAT(ROUND(SUM(CASE WHEN category IS NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1), '%') as percentage
FROM items

UNION ALL

SELECT 
  'NULL color' as metric,
  SUM(CASE WHEN color IS NULL THEN 1 ELSE 0 END) as count,
  CONCAT(ROUND(SUM(CASE WHEN color IS NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1), '%') as percentage
FROM items

UNION ALL

SELECT 
  'NULL price' as metric,
  SUM(CASE WHEN price IS NULL THEN 1 ELSE 0 END) as count,
  CONCAT(ROUND(SUM(CASE WHEN price IS NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1), '%') as percentage
FROM items

UNION ALL

SELECT 
  'NULL image_url' as metric,
  SUM(CASE WHEN image_url IS NULL THEN 1 ELSE 0 END) as count,
  CONCAT(ROUND(SUM(CASE WHEN image_url IS NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1), '%') as percentage
FROM items;


-- 6️⃣ 按來源統計資料
-- ========================================
SELECT 
  source,
  COUNT(*) as count,
  SUM(CASE WHEN price IS NOT NULL THEN 1 ELSE 0 END) as has_price,
  SUM(CASE WHEN image_url IS NOT NULL THEN 1 ELSE 0 END) as has_image
FROM items
GROUP BY source
ORDER BY count DESC;


-- 7️⃣ 查看還有哪些 clothing_type 缺少 category
-- ========================================
SELECT 
  clothing_type,
  COUNT(*) as count
FROM items
WHERE category IS NULL
GROUP BY clothing_type
ORDER BY count DESC
LIMIT 20;


-- 8️⃣ 驗證 price 欄位格式
-- ========================================
SELECT 
  id,
  name,
  price,
  ROUND(price, 2) as rounded_price,
  source
FROM items
WHERE price IS NOT NULL
LIMIT 10;

-- ✅ 確認 price 是數字格式（不是文字）


-- 9️⃣ 檢查 partner_products 是否為空
-- ========================================
SELECT COUNT(*) as partner_products_count FROM partner_products;

-- ✅ 應該顯示 0（空表）


-- 🔟 驗證所有表格的資料量
-- ========================================
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'items', COUNT(*) FROM items
UNION ALL
SELECT 'partner_products', COUNT(*) FROM partner_products
UNION ALL
SELECT 'user_wardrobe', COUNT(*) FROM user_wardrobe
UNION ALL
SELECT 'conversation_history', COUNT(*) FROM conversation_history
UNION ALL
SELECT 'rating', COUNT(*) FROM rating;

-- ✅ 預期結果：
-- users: 50
-- items: 44,708
-- partner_products: 0
-- user_wardrobe: 0
-- conversation_history: 0
-- rating: 0


-- ========================================
-- 🎉 驗證完成！
-- ========================================
-- 如果所有查詢都成功執行，資料庫就正常了！
