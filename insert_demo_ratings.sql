-- =============================================
-- RAG 評分系統 Demo 測試資料
-- 快速執行版本
-- =============================================

-- 步驟 1: 新增測試用戶 (如果不足)
-- =============================================
INSERT IGNORE INTO users (username, email, password_hash, favorite_style)
VALUES 
    ('demo_user_1', 'demo1@test.com', 'hash1', '休閒'),
    ('demo_user_2', 'demo2@test.com', 'hash2', '正式'),
    ('demo_user_3', 'demo3@test.com', 'hash3', '運動'),
    ('demo_user_4', 'demo4@test.com', 'hash4', '街頭'),
    ('demo_user_5', 'demo5@test.com', 'hash5', '復古'),
    ('demo_user_6', 'demo6@test.com', 'hash6', '極簡'),
    ('demo_user_7', 'demo7@test.com', 'hash7', '學院'),
    ('demo_user_8', 'demo8@test.com', 'hash8', '浪漫'),
    ('demo_user_9', 'demo9@test.com', 'hash9', '搖滾'),
    ('demo_user_10', 'demo10@test.com', 'hash10', '韓風'),
    ('demo_user_11', 'demo11@test.com', 'hash11', '日系'),
    ('demo_user_12', 'demo12@test.com', 'hash12', '歐美'),
    ('demo_user_13', 'demo13@test.com', 'hash13', '商務'),
    ('demo_user_14', 'demo14@test.com', 'hash14', '休閒'),
    ('demo_user_15', 'demo15@test.com', 'hash15', '運動');

-- 步驟 2: 選擇測試商品 (選前 10 件上衣)
-- =============================================

-- 設定測試商品變數
SET @item_1 = (SELECT id FROM items WHERE category = 'top' ORDER BY id LIMIT 1 OFFSET 0);
SET @item_2 = (SELECT id FROM items WHERE category = 'top' ORDER BY id LIMIT 1 OFFSET 1);
SET @item_3 = (SELECT id FROM items WHERE category = 'top' ORDER BY id LIMIT 1 OFFSET 2);
SET @item_4 = (SELECT id FROM items WHERE category = 'top' ORDER BY id LIMIT 1 OFFSET 3);
SET @item_5 = (SELECT id FROM items WHERE category = 'top' ORDER BY id LIMIT 1 OFFSET 4);
SET @item_6 = (SELECT id FROM items WHERE category = 'top' ORDER BY id LIMIT 1 OFFSET 5);
SET @item_7 = (SELECT id FROM items WHERE category = 'top' ORDER BY id LIMIT 1 OFFSET 6);
SET @item_8 = (SELECT id FROM items WHERE category = 'top' ORDER BY id LIMIT 1 OFFSET 7);
SET @item_9 = (SELECT id FROM items WHERE category = 'top' ORDER BY id LIMIT 1 OFFSET 8);
SET @item_10 = (SELECT id FROM items WHERE category = 'top' ORDER BY id LIMIT 1 OFFSET 9);

-- 驗證商品 ID
SELECT @item_1, @item_2, @item_3, @item_4, @item_5, @item_6, @item_7, @item_8, @item_9, @item_10;

-- 步驟 3: 插入測試評分資料
-- =============================================

-- 商品 1: 5.0★ (3 次評分) - 高分但評分少
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(1, 'items', @item_1, 5, '超級好!'),
(2, 'items', @item_1, 5, '很棒!'),
(3, 'items', @item_1, 5, '推薦!');

-- 商品 2: 4.8★ (25 次評分) - 高分且熱門 ⭐ 預期排名第 1
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(1, 'items', @item_2, 5, '好評'), (2, 'items', @item_2, 5, '好評'),
(3, 'items', @item_2, 5, '好評'), (4, 'items', @item_2, 5, '好評'),
(5, 'items', @item_2, 5, '好評'), (6, 'items', @item_2, 5, '好評'),
(7, 'items', @item_2, 5, '好評'), (8, 'items', @item_2, 5, '好評'),
(9, 'items', @item_2, 5, '好評'), (10, 'items', @item_2, 5, '好評'),
(11, 'items', @item_2, 5, '好評'), (12, 'items', @item_2, 5, '好評'),
(13, 'items', @item_2, 5, '好評'), (14, 'items', @item_2, 5, '好評'),
(15, 'items', @item_2, 5, '好評'), (1, 'items', @item_2 + 1000000, 5, '好評'),
(2, 'items', @item_2 + 2000000, 5, '好評'), (3, 'items', @item_2 + 3000000, 5, '好評'),
(4, 'items', @item_2 + 4000000, 5, '好評'), (5, 'items', @item_2 + 5000000, 5, '好評'),
(1, 'items', @item_2 + 6000000, 4, '不錯'), (2, 'items', @item_2 + 7000000, 4, '不錯'),
(3, 'items', @item_2 + 8000000, 4, '不錯'), (4, 'items', @item_2 + 9000000, 4, '不錯'),
(5, 'items', @item_2 + 10000000, 4, '不錯');

-- 商品 3: 4.6★ (18 次評分) - 高分常評 ⭐ 預期排名第 2
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(1, 'items', @item_3, 5, '讚'), (2, 'items', @item_3, 5, '讚'),
(3, 'items', @item_3, 5, '讚'), (4, 'items', @item_3, 5, '讚'),
(5, 'items', @item_3, 5, '讚'), (6, 'items', @item_3, 5, '讚'),
(7, 'items', @item_3, 5, '讚'), (8, 'items', @item_3, 5, '讚'),
(9, 'items', @item_3, 5, '讚'), (10, 'items', @item_3, 5, '讚'),
(11, 'items', @item_3, 5, '讚'), (12, 'items', @item_3, 5, '讚'),
(13, 'items', @item_3, 4, '好'), (14, 'items', @item_3, 4, '好'),
(15, 'items', @item_3, 4, '好'), (1, 'items', @item_3 + 1000000, 4, '好'),
(2, 'items', @item_3 + 2000000, 4, '好'), (3, 'items', @item_3 + 3000000, 4, '好');

-- 商品 4: 4.5★ (15 次評分) - 高分常評 ⭐ 預期排名第 3
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(1, 'items', @item_4, 5, '推'), (2, 'items', @item_4, 5, '推'),
(3, 'items', @item_4, 5, '推'), (4, 'items', @item_4, 5, '推'),
(5, 'items', @item_4, 5, '推'), (6, 'items', @item_4, 5, '推'),
(7, 'items', @item_4, 5, '推'), (8, 'items', @item_4, 5, '推'),
(9, 'items', @item_4, 5, '推'), (10, 'items', @item_4, 4, '好'),
(11, 'items', @item_4, 4, '好'), (12, 'items', @item_4, 4, '好'),
(13, 'items', @item_4, 4, '好'), (14, 'items', @item_4, 4, '好'),
(15, 'items', @item_4, 4, '好');

-- 商品 5: 4.0★ (30 次評分) - 中分但超高人氣 ⭐ 預期排名第 4
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(1, 'items', @item_5, 5, '5'), (2, 'items', @item_5, 5, '5'), (3, 'items', @item_5, 5, '5'),
(4, 'items', @item_5, 5, '5'), (5, 'items', @item_5, 5, '5'), (6, 'items', @item_5, 5, '5'),
(7, 'items', @item_5, 5, '5'), (8, 'items', @item_5, 5, '5'), (9, 'items', @item_5, 5, '5'),
(10, 'items', @item_5, 5, '5'), (11, 'items', @item_5, 4, '4'), (12, 'items', @item_5, 4, '4'),
(13, 'items', @item_5, 4, '4'), (14, 'items', @item_5, 4, '4'), (15, 'items', @item_5, 4, '4'),
(1, 'items', @item_5 + 1000000, 4, '4'), (2, 'items', @item_5 + 2000000, 4, '4'),
(3, 'items', @item_5 + 3000000, 4, '4'), (4, 'items', @item_5 + 4000000, 4, '4'),
(5, 'items', @item_5 + 5000000, 4, '4'), (6, 'items', @item_5 + 6000000, 3, '3'),
(7, 'items', @item_5 + 7000000, 3, '3'), (8, 'items', @item_5 + 8000000, 3, '3'),
(9, 'items', @item_5 + 9000000, 3, '3'), (10, 'items', @item_5 + 10000000, 3, '3'),
(11, 'items', @item_5 + 11000000, 3, '3'), (12, 'items', @item_5 + 12000000, 3, '3'),
(13, 'items', @item_5 + 13000000, 3, '3'), (14, 'items', @item_5 + 14000000, 3, '3'),
(15, 'items', @item_5 + 15000000, 3, '3');

-- 商品 6: 4.9★ (2 次評分) - 超高分但極少評分
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(1, 'items', @item_6, 5, '完美'),
(2, 'items', @item_6, 5, '超讚');

-- 商品 7: 3.5★ (10 次評分) - 中等評價
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(1, 'items', @item_7, 4, 'ok'), (2, 'items', @item_7, 4, 'ok'),
(3, 'items', @item_7, 4, 'ok'), (4, 'items', @item_7, 4, 'ok'),
(5, 'items', @item_7, 4, 'ok'), (6, 'items', @item_7, 3, 'ok'),
(7, 'items', @item_7, 3, 'ok'), (8, 'items', @item_7, 3, 'ok'),
(9, 'items', @item_7, 3, 'ok'), (10, 'items', @item_7, 3, 'ok');

-- 商品 8: 3.0★ (20 次評分) - 低分但高人氣
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(1, 'items', @item_8, 3, '普通'), (2, 'items', @item_8, 3, '普通'),
(3, 'items', @item_8, 3, '普通'), (4, 'items', @item_8, 3, '普通'),
(5, 'items', @item_8, 3, '普通'), (6, 'items', @item_8, 3, '普通'),
(7, 'items', @item_8, 3, '普通'), (8, 'items', @item_8, 3, '普通'),
(9, 'items', @item_8, 3, '普通'), (10, 'items', @item_8, 3, '普通'),
(11, 'items', @item_8, 3, '普通'), (12, 'items', @item_8, 3, '普通'),
(13, 'items', @item_8, 3, '普通'), (14, 'items', @item_8, 3, '普通'),
(15, 'items', @item_8, 3, '普通'), (1, 'items', @item_8 + 1000000, 3, '普通'),
(2, 'items', @item_8 + 2000000, 3, '普通'), (3, 'items', @item_8 + 3000000, 3, '普通'),
(4, 'items', @item_8 + 4000000, 3, '普通'), (5, 'items', @item_8 + 5000000, 3, '普通');

-- 商品 9: 3.8★ (12 次評分) - 中等評價
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(1, 'items', @item_9, 5, 'ok'), (2, 'items', @item_9, 5, 'ok'),
(3, 'items', @item_9, 5, 'ok'), (4, 'items', @item_9, 5, 'ok'),
(5, 'items', @item_9, 4, 'ok'), (6, 'items', @item_9, 4, 'ok'),
(7, 'items', @item_9, 4, 'ok'), (8, 'items', @item_9, 4, 'ok'),
(9, 'items', @item_9, 3, 'ok'), (10, 'items', @item_9, 3, 'ok'),
(11, 'items', @item_9, 3, 'ok'), (12, 'items', @item_9, 3, 'ok');

-- 商品 10: 2.0★ (5 次評分) - 低評分
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(1, 'items', @item_10, 2, '不好'),
(2, 'items', @item_10, 2, '不好'),
(3, 'items', @item_10, 2, '不好'),
(4, 'items', @item_10, 2, '不好'),
(5, 'items', @item_10, 2, '不好');

-- 步驟 4: 驗證資料插入
-- =============================================
SELECT '✅ 測試資料插入完成!' as 狀態;

-- 查看評分統計
SELECT 
    item_id,
    COUNT(*) as 評分次數,
    ROUND(AVG(rating_value), 2) as 平均評分
FROM rating
WHERE item_source = 'items'
GROUP BY item_id
ORDER BY item_id;

-- 查看 item_stats 表 (觸發器自動生成)
SELECT 
    item_id,
    avg_rating as 平均評分,
    rating_count as 評分次數,
    high_rating_ratio as 好評率
FROM item_stats
WHERE item_source = 'items'
ORDER BY item_id;
