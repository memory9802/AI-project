-- 初始化穿搭資料庫
CREATE DATABASE IF NOT EXISTS outfit_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE outfit_db;

-- =============================
-- 衣物表 items
-- =============================
CREATE TABLE IF NOT EXISTS items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sku VARCHAR(50) UNIQUE,
  name VARCHAR(100) NOT NULL,
  category ENUM('top','bottom','outer','shoes','accessory') NOT NULL,
  color VARCHAR(50),
  size VARCHAR(10),
  price DECIMAL(10,2),
  image_url VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 範例衣物資料
INSERT INTO items (sku, name, category, color, size, price, image_url)
VALUES
('TSHIRT-001', '白色T恤', 'top', 'white', 'M', 15.00, 'https://cdn-icons-png.flaticon.com/512/892/892458.png'),
('JEANS-001', '深藍牛仔褲', 'bottom', 'navy', 'L', 40.00, 'https://cdn-icons-png.flaticon.com/512/892/892458.png'),
('SNEAKERS-001', '白色球鞋', 'shoes', 'white', '42', 60.00, 'https://cdn-icons-png.flaticon.com/512/892/892458.png'),
('COAT-001', '淺灰色外套', 'outer', 'grey', 'L', 80.00, 'https://cdn-icons-png.flaticon.com/512/892/892458.png');

-- =============================
-- 穿搭表 outfits
-- =============================
CREATE TABLE IF NOT EXISTS outfits (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  occasion ENUM('casual','formal','street','sport','date') DEFAULT 'casual',
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 範例穿搭資料
INSERT INTO outfits (name, occasion, description)
VALUES
('白T + 牛仔 + 白球鞋', 'casual', '經典日常穿搭'),
('灰外套 + 牛仔褲', 'formal', '簡約正式感'),
('白T + 灰外套', 'street', '街頭風混搭');

-- =============================
-- 穿搭與衣物關聯表 outfit_items
-- =============================
CREATE TABLE IF NOT EXISTS outfit_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  outfit_id INT NOT NULL,
  item_id INT NOT NULL,
  FOREIGN KEY (outfit_id) REFERENCES outfits(id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
);

-- 關聯：outfit 1 -> 白T + 牛仔 + 白鞋
INSERT INTO outfit_items (outfit_id, item_id) VALUES
(1, 1), (1, 2), (1, 3);

-- 關聯：outfit 2 -> 灰外套 + 牛仔褲
INSERT INTO outfit_items (outfit_id, item_id) VALUES
(2, 4), (2, 2);

-- 關聯：outfit 3 -> 白T + 灰外套
INSERT INTO outfit_items (outfit_id, item_id) VALUES
(3, 1), (3, 4);

-- =============================
-- 標籤表 tags（可選，用於AI分類）
-- =============================
CREATE TABLE IF NOT EXISTS tags (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) UNIQUE
);

INSERT INTO tags (name) VALUES
('休閒'), ('正式'), ('街頭'), ('運動'), ('約會');

-- =============================
-- 使用者表 users
-- =============================
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  favorite_style VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 預設使用者
INSERT INTO users (username, password, favorite_style)
VALUES
('ian', 'test123', '休閒'),
('guest', '1234', '街頭');

-- =============================
-- 收藏表 user_favorites
-- =============================
CREATE TABLE IF NOT EXISTS user_favorites (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  outfit_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (outfit_id) REFERENCES outfits(id) ON DELETE CASCADE
);

-- 收藏範例
INSERT INTO user_favorites (user_id, outfit_id) VALUES
(1, 1),
(1, 3),
(2, 2);

-- =============================
-- 完成訊息
-- =============================
SELECT '✅ Outfit database initialized successfully!' AS status;
