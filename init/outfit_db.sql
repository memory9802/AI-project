-- ========================================
-- 穿搭資料庫初始化腳本 (僅結構定義)
-- ========================================
-- 
-- 📋 此檔案用途:建立資料庫結構 (不含資料)
-- 
-- ⚠️ 重要提醒:
--   - 新組員請使用 outfit_db_with_data.sql (包含完整資料)
--   - 此檔案只適合「從零建立」時使用
-- 
-- 🚀 快速上手:
--   ./scripts/setup_database_for_teammates.sh
-- 
-- ========================================

-- 設定字符集 (解決中文亂碼)
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

CREATE DATABASE IF NOT EXISTS outfit_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE outfit_db;

-- =============================
-- 衣物表 items
-- =============================
-- 注意: category 和其他 ENUM 欄位已改為 VARCHAR 以支援更多資料來源
CREATE TABLE IF NOT EXISTS items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  category VARCHAR(100) DEFAULT NULL COMMENT 'top, bottom, shoes, accessories',
  color VARCHAR(50) DEFAULT NULL,
  size VARCHAR(20) DEFAULT NULL,
  price DECIMAL(10,2) DEFAULT NULL,
  image_url VARCHAR(255) DEFAULT NULL,
  description TEXT DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  sku VARCHAR(50) UNIQUE DEFAULT NULL,
  gender VARCHAR(20) DEFAULT NULL COMMENT '男, 女, 中性, 男孩, 女孩',
  clothing_type VARCHAR(50) DEFAULT NULL,
  length VARCHAR(20) DEFAULT NULL COMMENT '短, 長, 中',
  price_text VARCHAR(20) DEFAULT NULL,
  source VARCHAR(50) DEFAULT 'manual' COMMENT 'manual, uniqlo, styles_dataset, fashion_small, malefashion',
  
  INDEX idx_category (category),
  INDEX idx_color (color),
  INDEX idx_gender (gender),
  INDEX idx_source (source),
  INDEX idx_sku (sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='單品表 - 支援多來源資料(UNIQLO, 時尚資料集等)';

-- 注意: items 表格的資料請使用 Python 腳本匯入
-- 執行: python3 scripts/import_csv_to_db.py
-- 將會從以下來源匯入資料:
--   - init/uniqlo_175_colored.csv (222 筆)
--   - dataset/styles.csv (44,407 筆)
--   - dataset/items_fashion_small_clean.csv (4,999 筆)
--   - dataset/items_malefashion.csv (80 筆)

-- =============================
-- 使用者表 users
-- =============================
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE DEFAULT NULL,
  password_hash VARCHAR(255) DEFAULT NULL COMMENT 'bcrypt 加密密碼',
  favorite_style VARCHAR(50) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='使用者表 - 使用 bcrypt 加密密碼';

-- 注意: users 表格的資料請使用 Python 腳本生成
-- 執行: python3 scripts/generate_users_with_bcrypt.py
-- 將會生成 50 個測試用戶,包含:
--   - 3 個主要測試帳號: admin, demo, test (密碼: admin123, demo123, test123)
--   - 47 個虛擬用戶 (密碼: password123)
--   - 所有密碼使用 bcrypt 加密儲存
--
-- 測試帳號清單請查看: docs/TEST_ACCOUNTS.md (已加入 .gitignore)
-- 
-- 前端登入流程:
-- 1. 前端發送帳號密碼到後端 API: POST /api/login
-- 2. 後端使用 bcrypt.checkpw() 驗證密碼
-- 3. 驗證成功返回用戶資訊和 session/token

-- =============================
-- 使用者衣櫃表 user_wardrobe
-- =============================
CREATE TABLE IF NOT EXISTS user_wardrobe (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  item_id INT NOT NULL,
  nickname VARCHAR(100) DEFAULT NULL COMMENT '使用者自訂的衣物暱稱',
  purchase_date DATE DEFAULT NULL,
  notes TEXT DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
  UNIQUE KEY unique_user_item (user_id, item_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='使用者個人衣櫃';

-- =============================
-- 合作品牌商品表 partner_products
-- =============================
CREATE TABLE IF NOT EXISTS partner_products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  item_id INT NOT NULL,
  brand VARCHAR(100) NOT NULL,
  product_url VARCHAR(500) DEFAULT NULL,
  affiliate_link VARCHAR(500) DEFAULT NULL,
  current_price DECIMAL(10,2) DEFAULT NULL,
  original_price DECIMAL(10,2) DEFAULT NULL,
  discount_percent INT DEFAULT NULL,
  stock_status ENUM('in_stock', 'out_of_stock', 'pre_order') DEFAULT 'in_stock',
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
  INDEX idx_brand (brand),
  INDEX idx_stock (stock_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='合作品牌商品資訊(UNIQLO等)';

-- =============================
-- AI 對話歷史表 conversation_history
-- =============================
CREATE TABLE IF NOT EXISTS conversation_history (
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
-- 穿搭評分表 outfit_ratings
-- =============================
-- 注意: 此表格目前未使用,因為沒有 outfits 表格
-- 如需要穿搭功能,請重新設計表格結構
CREATE TABLE IF NOT EXISTS outfit_ratings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
  comment TEXT DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_user (user_id),
  INDEX idx_rating (rating)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='使用者對穿搭的評分(目前未使用)';

-- =============================
-- 完成訊息
-- =============================
SELECT '✅ Database structure created successfully!' AS status;
SELECT '📝 Note: Please import items data using: python3 scripts/import_csv_to_db.py' AS instruction;

-- =============================
-- 字符集修復 (如果遇到亂碼)
-- =============================
-- 如果 DBeaver 顯示中文亂碼,請執行以下指令:
-- 
-- ALTER DATABASE outfit_db CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- ALTER TABLE items CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- ALTER TABLE users CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- ALTER TABLE user_wardrobe CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- ALTER TABLE partner_products CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- ALTER TABLE conversation_history CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- ALTER TABLE outfit_ratings CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- 
-- DBeaver 連接設定也要加入:
--   characterEncoding = UTF-8
--   useUnicode = true
