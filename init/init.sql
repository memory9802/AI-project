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

-- 套裝 3：運動套裝
(3, 7, 'top'),
(3, 8, 'bottom'),
(3, 9, 'shoes');
