-- =========================================================
--   init.sql － for outfit_db
--   統一全部小寫表名：outfits, items, outfit_items
--   並加入假資料（3 套穿搭、9 件單品）
-- =========================================================

-- 確保資料庫存在
CREATE DATABASE IF NOT EXISTS outfit_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE outfit_db;

-- =========================================================
-- 1. outfits（穿搭主表）
-- =========================================================
DROP TABLE IF EXISTS outfits;

CREATE TABLE outfits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,       -- 穿搭名稱
    description TEXT,                 -- 描述
    occasion VARCHAR(100),            -- 適用場合：上班、約會、運動...
    style VARCHAR(100),               -- 風格
    season VARCHAR(50),               -- 季節：春/夏/秋/冬
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 2. items（單品）
-- =========================================================
DROP TABLE IF EXISTS items;

CREATE TABLE items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,       -- 單品名稱
    category VARCHAR(100),            -- 類別：上衣/下身/鞋子/配件
    color VARCHAR(50),
    size VARCHAR(20),
    price DECIMAL(10,2),
    image_url VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 3. outfit_items（穿搭與單品的關聯表）
-- =========================================================
DROP TABLE IF EXISTS outfit_items;

CREATE TABLE outfit_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    outfit_id INT NOT NULL,
    item_id INT NOT NULL,
    role VARCHAR(50),                 -- 例如 top/bottom/shoes/accessory

    CONSTRAINT fk_outfit_items_outfit
        FOREIGN KEY (outfit_id) REFERENCES outfits(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_outfit_items_item
        FOREIGN KEY (item_id) REFERENCES items(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 4. 插入 outfits 假資料（3 套）
-- =========================================================
INSERT INTO outfits (name, description, occasion, style, season) VALUES
('約會小清新',
 '白襯衫搭牛仔褲與小白鞋，乾淨俐落適合第一次約會或喝咖啡。',
 '約會', '休閒', '春夏'),

('商務上班日常',
 '白色襯衫搭配黑色西裝褲與皮鞋，再加上一支簡約手錶，專業又穩重。',
 '上班', '正式', '四季'),

('週末運動穿搭',
 '排汗 T-shirt、運動短褲、跑步鞋，輕鬆舒適適合健身房或慢跑。',
 '運動', '運動', '四季');


-- =========================================================
-- 5. 插入 items 假資料（9 件）
-- =========================================================
INSERT INTO items (name, category, color, size, price, image_url, description) VALUES
('白色襯衫', '上衣', '白', 'M', 890, NULL, '基本款白襯衫'),
('深藍牛仔褲', '下身', '深藍', 'M', 990, NULL, '直筒百搭牛仔褲'),
('白色休閒鞋', '鞋子', '白', '27', 1800, NULL, '百搭小白鞋'),

('灰色針織上衣', '上衣', '灰', 'M', 790, NULL, '微合身針織上衣'),
('黑色西裝褲', '下身', '黑', 'M', 1200, NULL, '正式場合西裝褲'),
('黑色皮鞋', '鞋子', '黑', '27', 2200, NULL, '商務皮鞋'),

('運動排汗T-shirt', '上衣', '灰', 'M', 450, NULL, '透氣排汗'),
('運動短褲', '下身', '黑', 'M', 550, NULL, '運動短褲'),
('跑步鞋', '鞋子', '灰', '27', 2100, NULL, '輕量避震跑鞋');


-- =========================================================
-- 6. 插入 outfit_items（將 9 件單品分配到 3 套穿搭）
-- =========================================================
INSERT INTO outfit_items (outfit_id, item_id, role) VALUES
-- 套裝 1：約會小清新
(1, 1, 'top'),
(1, 2, 'bottom'),
(1, 3, 'shoes'),

-- 套裝 2：商務上班日常
(2, 4, 'top'),
(2, 5, 'bottom'),
(2, 6, 'shoes'),

-- 套裝 3:運動套裝
(3, 7, 'top'),
(3, 8, 'bottom'),
(3, 9, 'shoes');


-- =========================================================
-- 7. users（使用者表 - 專題功能1：我的衣櫃）
-- =========================================================
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),       -- 實際專題可用 bcrypt 加密
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入測試使用者
INSERT INTO users (username, email, password_hash) VALUES
('test_user', 'test@example.com', 'hashed_password_placeholder'),
('alice', 'alice@example.com', 'hashed_password_placeholder'),
('bob', 'bob@example.com', 'hashed_password_placeholder');


-- =========================================================
-- 8. user_wardrobe（使用者衣櫃 - 專題功能1：我的衣櫃）
-- =========================================================
DROP TABLE IF EXISTS user_wardrobe;

CREATE TABLE user_wardrobe (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),            -- 上衣/下身/鞋子/配件
    color VARCHAR(50),
    material VARCHAR(100),            -- 材質：棉/麻/聚酯纖維等
    tags VARCHAR(255),                -- 標籤，例如：休閒,正式,運動（逗號分隔）
    image_url VARCHAR(255),           -- 使用者上傳的照片 URL
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_wardrobe_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入測試使用者衣櫃資料
INSERT INTO user_wardrobe (user_id, item_name, category, color, material, tags, image_url) VALUES
(1, '我的藍色襯衫', '上衣', '藍', '棉', '正式,上班', NULL),
(1, '黑色牛仔褲', '下身', '黑', '丹寧', '休閒,百搭', NULL),
(1, '紅色運動T恤', '上衣', '紅', '聚酯纖維', '運動,休閒', NULL),
(2, '白色洋裝', '上衣', '白', '麻', '約會,正式', NULL);


-- =========================================================
-- 9. outfit_ratings（穿搭評分 - 專題功能3：評分互動）
-- =========================================================
DROP TABLE IF EXISTS outfit_ratings;

CREATE TABLE outfit_ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    outfit_id INT NOT NULL,           -- 關聯到 outfits 表
    user_id INT,                      -- NULL 表示匿名評分
    rating INT NOT NULL,              -- 評分 1-5
    is_owner BOOLEAN DEFAULT FALSE,   -- 是否為穿搭擁有者的自評
    comment TEXT,                     -- 評語（選填）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_rating_outfit
        FOREIGN KEY (outfit_id) REFERENCES outfits(id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_rating_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE SET NULL,
    
    CONSTRAINT chk_rating_range
        CHECK (rating BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入測試評分資料
INSERT INTO outfit_ratings (outfit_id, user_id, rating, is_owner, comment) VALUES
(1, 1, 5, TRUE, '我自己很滿意這套約會穿搭'),
(1, 2, 4, FALSE, '很清爽！但可以加個配件'),
(2, 1, 4, TRUE, '商務場合很合適'),
(2, NULL, 5, FALSE, '非常專業的穿搭'),  -- 匿名評分
(3, 1, 5, TRUE, '運動起來很舒適');


-- =========================================================
-- 10. partner_products（合作商家商品 - 專題功能2：商品推薦）
-- =========================================================
DROP TABLE IF EXISTS partner_products;

CREATE TABLE partner_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    color VARCHAR(50),
    price DECIMAL(10,2),
    partner_name VARCHAR(255),        -- 合作商家名稱
    product_url VARCHAR(512),         -- 商品頁面連結
    image_url VARCHAR(512),           -- 商品圖片
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入測試商品資料
INSERT INTO partner_products (product_name, category, color, price, partner_name, product_url, image_url, description) VALUES
('Uniqlo 白色 T-shirt', '上衣', '白', 390, 'Uniqlo', 'https://www.uniqlo.com/example', NULL, '經典基本款'),
('Zara 黑色長褲', '下身', '黑', 1290, 'Zara', 'https://www.zara.com/example', NULL, '修身版型'),
('Nike Air 運動鞋', '鞋子', '白', 3200, 'Nike', 'https://www.nike.com/example', NULL, '舒適氣墊');


-- =========================================================
-- 11. conversation_history（對話記錄表 - 供 AI 分析用）
-- =========================================================
DROP TABLE IF EXISTS conversation_history;

CREATE TABLE conversation_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id INT,
    user_message TEXT,
    ai_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_conversation_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE SET NULL,
    
    INDEX idx_session (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
