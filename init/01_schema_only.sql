-- ========================================
-- 穿搭資料庫初始化腳本 (僅結構定義 - 無測試資料)
-- ========================================
-- 
-- 📋 此檔案用途:建立資料庫結構 (不含任何資料)
-- 
-- ⚠️ 重要提醒:
--   - 此檔案不包含任何測試資料或範例資料
--   - 適合用於建立乾淨的資料庫架構
--   - 如需資料,請使用 00_init_with_data.sql
-- 
-- ========================================

-- 設定字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

CREATE DATABASE IF NOT EXISTS outfit_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE outfit_db;

-- =============================
-- 使用者表 users
-- =============================
DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE DEFAULT NULL,
  password_hash VARCHAR(255) DEFAULT NULL COMMENT 'bcrypt 加密密碼',
  favorite_style VARCHAR(50) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='使用者表 - 使用 bcrypt 加密密碼';

-- =============================
-- 衣物表 items
-- =============================
DROP TABLE IF EXISTS items;
CREATE TABLE items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  category VARCHAR(100) DEFAULT NULL COMMENT 'top, bottom, shoes, accessories',
  color VARCHAR(50) DEFAULT NULL,
  image_url VARCHAR(255) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  sku VARCHAR(50) UNIQUE DEFAULT NULL,
  gender VARCHAR(20) DEFAULT NULL COMMENT '男, 女, 中性, 男孩, 女孩',
  clothing_type VARCHAR(50) DEFAULT NULL,
  length VARCHAR(20) DEFAULT NULL COMMENT '短, 長, 中',
  price_text VARCHAR(20) DEFAULT NULL,
  source VARCHAR(50) DEFAULT 'manual' COMMENT 'manual, uniqlo, styles_dataset, malefashion',
  
  INDEX idx_category (category),
  INDEX idx_color (color),
  INDEX idx_gender (gender),
  INDEX idx_source (source),
  INDEX idx_sku (sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='單品表 - 支援多來源資料';

-- =============================
-- 使用者衣櫃表 user_wardrobe
-- =============================
DROP TABLE IF EXISTS user_wardrobe;
CREATE TABLE user_wardrobe (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  item_name VARCHAR(255) NOT NULL,
  category VARCHAR(100) DEFAULT NULL,
  color VARCHAR(50) DEFAULT NULL,
  material VARCHAR(100) DEFAULT NULL,
  tags VARCHAR(255) DEFAULT NULL,
  image_url VARCHAR(255) DEFAULT NULL,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='使用者個人衣櫃';

-- =============================
-- 合作品牌商品表 partner_products
-- =============================
DROP TABLE IF EXISTS partner_products;
CREATE TABLE partner_products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_name VARCHAR(255) NOT NULL,
  category VARCHAR(100) DEFAULT NULL,
  color VARCHAR(50) DEFAULT NULL,
  price DECIMAL(10,2) DEFAULT NULL,
  partner_name VARCHAR(255) DEFAULT NULL,
  product_url VARCHAR(512) DEFAULT NULL,
  image_url VARCHAR(512) DEFAULT NULL,
  description TEXT DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='合作品牌商品資訊';

-- =============================
-- AI 對話歷史表 conversation_history
-- =============================
DROP TABLE IF EXISTS conversation_history;
CREATE TABLE conversation_history (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT DEFAULT NULL,
  session_id VARCHAR(100) NOT NULL,
  message_type ENUM('user', 'assistant', 'system') NOT NULL,
  content TEXT NOT NULL,
  metadata JSON DEFAULT NULL COMMENT '額外資訊(如推薦的 outfit_ids, item_ids 等)',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
  INDEX idx_session (session_id),
  INDEX idx_user (user_id),
  INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='AI 聊天對話記錄';

-- =============================
-- 商品評分表 rating
-- =============================
DROP TABLE IF EXISTS rating;
CREATE TABLE rating (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL COMMENT '評分的使用者ID',
  item_id INT NOT NULL COMMENT '被評分的商品ID',
  rating_value INT NOT NULL COMMENT '評分值 (建議 1-5 星)',
  review_text TEXT DEFAULT NULL COMMENT '評論內容',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '評分時間',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
  
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
  
  INDEX idx_user_id (user_id),
  INDEX idx_item_id (item_id),
  INDEX idx_rating_value (rating_value),
  INDEX idx_created_at (created_at),
  
  UNIQUE KEY unique_user_item (user_id, item_id) COMMENT '同一使用者對同一商品只能評分一次'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='商品評分表 - 記錄使用者對商品的評分和評論';

-- =============================
-- 完成訊息
-- =============================
SELECT '✅ Database schema created successfully!' AS status;
SELECT '📝 Note: This is a clean schema without any test data' AS info;
