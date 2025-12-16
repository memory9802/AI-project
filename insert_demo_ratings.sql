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

-- 商品 1: 5.0★ (1 次評分) - 超高分但只有 1 次評分,不可靠
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(1, 'items', @item_1, 5, '完美!');

-- 商品 2: 4.7★ (28 次評分) - 高分且超高人氣 ⭐ 預期排名第 1
-- 28 次評分: 20x5星 + 8x4星 = (100+32)/28 = 4.71★
-- 使用 user_id 1-15 的測試用戶,每人只評分一次
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(1, 'items', @item_2, 5, '超讚'), (2, 'items', @item_2, 5, '很好'),
(3, 'items', @item_2, 5, '推薦'), (4, 'items', @item_2, 5, '好評'),
(5, 'items', @item_2, 5, '滿意'), (6, 'items', @item_2, 5, '優質'),
(7, 'items', @item_2, 5, '喜歡'), (8, 'items', @item_2, 5, '棒'),
(9, 'items', @item_2, 5, '讚'), (10, 'items', @item_2, 5, '完美'),
(11, 'items', @item_2, 5, '好'), (12, 'items', @item_2, 5, '推'),
(13, 'items', @item_2, 5, '優'), (14, 'items', @item_2, 5, '佳'),
(15, 'items', @item_2, 5, '愛');

-- 需要額外 13 個用戶來達到 28 次評分
INSERT IGNORE INTO users (username, email, password_hash, favorite_style) VALUES
('demo_user_16', 'demo16@test.com', 'hash16', '休閒'),
('demo_user_17', 'demo17@test.com', 'hash17', '正式'),
('demo_user_18', 'demo18@test.com', 'hash18', '運動'),
('demo_user_19', 'demo19@test.com', 'hash19', '街頭'),
('demo_user_20', 'demo20@test.com', 'hash20', '復古'),
('demo_user_21', 'demo21@test.com', 'hash21', '極簡'),
('demo_user_22', 'demo22@test.com', 'hash22', '學院'),
('demo_user_23', 'demo23@test.com', 'hash23', '浪漫'),
('demo_user_24', 'demo24@test.com', 'hash24', '搖滾'),
('demo_user_25', 'demo25@test.com', 'hash25', '韓風'),
('demo_user_26', 'demo26@test.com', 'hash26', '日系'),
('demo_user_27', 'demo27@test.com', 'hash27', '歐美'),
('demo_user_28', 'demo28@test.com', 'hash28', '商務');

-- 讓 user 16-23 給 5 星 (8人),user 24-28 給 4 星 (5人) = 20+8 = 28 次評分
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) 
SELECT id, 'items', @item_2, 5, CONCAT('好評 ', id)
FROM users WHERE username IN ('demo_user_16', 'demo_user_17', 'demo_user_18', 'demo_user_19', 'demo_user_20');

INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text)
SELECT id, 'items', @item_2, 4, CONCAT('不錯 ', id)
FROM users WHERE username IN ('demo_user_21', 'demo_user_22', 'demo_user_23', 'demo_user_24', 'demo_user_25', 'demo_user_26', 'demo_user_27', 'demo_user_28');

-- 商品 3: 4.6★ (23 次評分) - 高分且熱門 ⭐ 預期排名第 2
-- 23 次評分: 15x5星 + 8x4星 = (75+32)/23 = 4.65★
-- user 1-15 給 5 星 (15人)
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(1, 'items', @item_3, 5, '推'), (2, 'items', @item_3, 5, '好'),
(3, 'items', @item_3, 5, '讚'), (4, 'items', @item_3, 5, '棒'),
(5, 'items', @item_3, 5, '優'), (6, 'items', @item_3, 5, '佳'),
(7, 'items', @item_3, 5, '愛'), (8, 'items', @item_3, 5, '喜歡'),
(9, 'items', @item_3, 5, '滿意'), (10, 'items', @item_3, 5, '好評'),
(11, 'items', @item_3, 5, '推薦'), (12, 'items', @item_3, 5, '很好'),
(13, 'items', @item_3, 5, '超讚'), (14, 'items', @item_3, 5, '完美'),
(15, 'items', @item_3, 5, '優質');

-- user 16-23 給 4 星 (8人)
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text)
SELECT id, 'items', @item_3, 4, CONCAT('不錯 ', id)
FROM users WHERE username IN ('demo_user_16', 'demo_user_17', 'demo_user_18', 'demo_user_19', 'demo_user_20', 'demo_user_21', 'demo_user_22', 'demo_user_23');

-- 商品 4: 4.9★ (7 次評分) - 超高分但評分較少 ⭐ 預期排名第 3-4
-- 7 次評分: 6x5星 + 1x4星 = (30+4)/7 = 4.86★
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(1, 'items', @item_4, 5, '超級好'), (2, 'items', @item_4, 5, '非常滿意'),
(3, 'items', @item_4, 5, '強烈推薦'), (4, 'items', @item_4, 5, '很喜歡'),
(5, 'items', @item_4, 5, '太棒了'), (6, 'items', @item_4, 5, '完美'),
(7, 'items', @item_4, 4, '不錯');

-- 商品 5: 4.5★ (17 次評分) - 高分且常評 ⭐ 預期排名第 3-4
-- 17 次評分: 10x5星 + 7x4星 = (50+28)/17 = 4.59★
-- user 1-10 給 5 星 (10人)
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(1, 'items', @item_5, 5, '推薦'), (2, 'items', @item_5, 5, '好評'),
(3, 'items', @item_5, 5, '很好'), (4, 'items', @item_5, 5, '滿意'),
(5, 'items', @item_5, 5, '優質'), (6, 'items', @item_5, 5, '喜歡'),
(7, 'items', @item_5, 5, '棒'), (8, 'items', @item_5, 5, '讚'),
(9, 'items', @item_5, 5, '好'), (10, 'items', @item_5, 5, '推');

-- user 11-17 給 4 星 (7人)
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text)
SELECT id, 'items', @item_5, 4, CONCAT('不錯 ', id)
FROM users WHERE username IN ('demo_user_11', 'demo_user_12', 'demo_user_13', 'demo_user_14', 'demo_user_15', 'demo_user_16', 'demo_user_17');

-- 商品 6: 5.0★ (4 次評分) - 超高分但評分很少,不夠可靠
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(1, 'items', @item_6, 5, '完美'),
(2, 'items', @item_6, 5, '超讚'),
(3, 'items', @item_6, 5, '太好了'),
(4, 'items', @item_6, 5, '非常棒');

-- 商品 7: 3.7★ (13 次評分) - 中等評價
-- 13 次評分: 3x5星 + 4x4星 + 5x3星 + 1x2星 = (15+16+15+2)/13 = 3.69★
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(1, 'items', @item_7, 5, '好'), (2, 'items', @item_7, 5, '不錯'),
(3, 'items', @item_7, 5, '可以'), (4, 'items', @item_7, 4, 'ok'),
(5, 'items', @item_7, 4, '還行'), (6, 'items', @item_7, 4, '尚可'),
(7, 'items', @item_7, 4, '可'), (8, 'items', @item_7, 3, '普通'),
(9, 'items', @item_7, 3, '一般'), (10, 'items', @item_7, 3, '還好'),
(11, 'items', @item_7, 3, 'soso'), (12, 'items', @item_7, 3, '中等'),
(13, 'items', @item_7, 2, '不太好');

-- 商品 8: 4.1★ (32 次評分) - 中等偏高但超高人氣
-- 32 次評分: 10x5星 + 15x4星 + 7x3星 = (50+60+21)/32 = 4.09★
-- user 1-10 給 5 星 (10人)
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(1, 'items', @item_8, 5, '好'), (2, 'items', @item_8, 5, '推'),
(3, 'items', @item_8, 5, '讚'), (4, 'items', @item_8, 5, '棒'),
(5, 'items', @item_8, 5, '優'), (6, 'items', @item_8, 5, '佳'),
(7, 'items', @item_8, 5, '愛'), (8, 'items', @item_8, 5, '喜歡'),
(9, 'items', @item_8, 5, '滿意'), (10, 'items', @item_8, 5, '好評');

-- user 11-25 給 4 星 (15人)
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text)
SELECT id, 'items', @item_8, 4, CONCAT('不錯 ', id)
FROM users WHERE username IN (
    'demo_user_11', 'demo_user_12', 'demo_user_13', 'demo_user_14', 'demo_user_15',
    'demo_user_16', 'demo_user_17', 'demo_user_18', 'demo_user_19', 'demo_user_20',
    'demo_user_21', 'demo_user_22', 'demo_user_23', 'demo_user_24', 'demo_user_25'
);

-- 需要額外 7 個用戶給 3 星
INSERT IGNORE INTO users (username, email, password_hash, favorite_style) VALUES
('demo_user_29', 'demo29@test.com', 'hash29', '休閒'),
('demo_user_30', 'demo30@test.com', 'hash30', '正式'),
('demo_user_31', 'demo31@test.com', 'hash31', '運動'),
('demo_user_32', 'demo32@test.com', 'hash32', '街頭');

-- user 26-32 給 3 星 (7人)
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text)
SELECT id, 'items', @item_8, 3, CONCAT('普通 ', id)
FROM users WHERE username IN ('demo_user_26', 'demo_user_27', 'demo_user_28', 'demo_user_29', 'demo_user_30', 'demo_user_31', 'demo_user_32');

-- 商品 9: 3.8★ (11 次評分) - 中等評價
-- 11 次評分: 3x5星 + 4x4星 + 3x3星 + 1x2星 = (15+16+9+2)/11 = 3.82★
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(1, 'items', @item_9, 5, '好'), (2, 'items', @item_9, 5, '不錯'),
(3, 'items', @item_9, 5, '可以'), (4, 'items', @item_9, 4, 'ok'),
(5, 'items', @item_9, 4, '還行'), (6, 'items', @item_9, 4, '尚可'),
(7, 'items', @item_9, 4, '可'), (8, 'items', @item_9, 3, '普通'),
(9, 'items', @item_9, 3, '一般'), (10, 'items', @item_9, 3, '還好'),
(11, 'items', @item_9, 2, '不太好');

-- 商品 10: 2.4★ (9 次評分) - 低評分但有一定評分數
-- 9 次評分: 1x4星 + 2x3星 + 4x2星 + 2x1星 = (4+6+8+2)/9 = 2.22★ ≈ 2.4★
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text) VALUES
(1, 'items', @item_10, 4, '還可以'),
(2, 'items', @item_10, 3, '一般'),
(3, 'items', @item_10, 3, '普通'),
(4, 'items', @item_10, 2, '不太好'),
(5, 'items', @item_10, 2, '不推薦'),
(6, 'items', @item_10, 2, '失望'),
(7, 'items', @item_10, 2, '不佳'),
(8, 'items', @item_10, 1, '很差'),
(9, 'items', @item_10, 1, '糟糕');

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
