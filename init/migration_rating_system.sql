-- ============================================================
-- 評分權重系統資料庫遷移腳本
-- 方案 B: 完整擴展,支援 items 和 user_wardrobe 兩個來源
-- ============================================================
-- 專案: stylerec 穿搭推薦系統
-- 日期: 2025-12-09
-- 用途: 擴展 rating 表格支援多態關聯,新增統計表和視圖
-- ============================================================

USE outfit_db;

-- ============================================================
-- STEP 1: 備份現有 rating 表格資料 (如果有的話)
-- ============================================================

-- 建立臨時備份表
CREATE TABLE IF NOT EXISTS rating_backup AS SELECT * FROM rating;

-- ============================================================
-- STEP 2: 刪除舊的 rating 表格並重建
-- ============================================================

-- 刪除舊表格 (CASCADE 會自動處理外鍵約束)
DROP TABLE IF EXISTS rating;

-- 重建 rating 表格 (支援多態關聯)
CREATE TABLE rating (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL COMMENT '用戶ID',
  
  -- 多態關聯: 支援兩種來源
  item_source ENUM('items', 'user_wardrobe') NOT NULL COMMENT '商品來源: items 或 user_wardrobe',
  item_id INT NOT NULL COMMENT '商品ID (對應 items.id 或 user_wardrobe.id)',
  
  -- 評分資料
  rating_value INT NOT NULL COMMENT '評分值 (1-5 星)',
  review_text TEXT DEFAULT NULL COMMENT '評論文字',
  
  -- 時間戳記
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
  
  -- 外鍵約束
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  
  -- 索引優化
  INDEX idx_user_id (user_id),
  INDEX idx_item_source (item_source),
  INDEX idx_item_id (item_id),
  INDEX idx_item_source_id (item_source, item_id),
  INDEX idx_rating_value (rating_value),
  INDEX idx_created_at (created_at),
  
  -- 唯一約束: 同一用戶對同一來源的同一商品只能評分一次
  UNIQUE KEY unique_user_source_item (user_id, item_source, item_id),
  
  -- 檢查約束
  CHECK (rating_value BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='商品評分表 (支援 items 和 user_wardrobe)';

-- ============================================================
-- STEP 3: 還原備份資料 (如果有的話)
-- ============================================================

-- 如果原本有資料,轉換後插入新表格
INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text, created_at, updated_at)
SELECT 
  user_id, 
  'items' as item_source,  -- 舊資料預設為 items 來源
  item_id, 
  rating_value, 
  review_text, 
  created_at, 
  updated_at
FROM rating_backup
WHERE EXISTS (SELECT 1 FROM rating_backup LIMIT 1);

-- ============================================================
-- STEP 4: 建立 item_stats 統計表 (快取計算結果)
-- ============================================================

DROP TABLE IF EXISTS item_stats;

CREATE TABLE item_stats (
  id INT AUTO_INCREMENT PRIMARY KEY,
  item_source ENUM('items', 'user_wardrobe') NOT NULL COMMENT '商品來源',
  item_id INT NOT NULL COMMENT '商品ID',
  
  -- 統計資料
  avg_rating DECIMAL(3,2) DEFAULT 0.00 COMMENT '平均評分 (0.00-5.00)',
  rating_count INT DEFAULT 0 COMMENT '評分次數',
  rating_sum INT DEFAULT 0 COMMENT '評分總和 (用於快速計算平均)',
  
  -- 評分分布
  rating_5_count INT DEFAULT 0 COMMENT '5星數量',
  rating_4_count INT DEFAULT 0 COMMENT '4星數量',
  rating_3_count INT DEFAULT 0 COMMENT '3星數量',
  rating_2_count INT DEFAULT 0 COMMENT '2星數量',
  rating_1_count INT DEFAULT 0 COMMENT '1星數量',
  
  -- 高分統計
  high_rating_count INT DEFAULT 0 COMMENT '高分數量 (4-5星)',
  high_rating_ratio DECIMAL(5,4) DEFAULT 0.0000 COMMENT '高分比例 (0.0000-1.0000)',
  
  -- 時間戳記
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最後更新時間',
  
  -- 索引優化
  INDEX idx_item_source_id (item_source, item_id),
  INDEX idx_avg_rating (avg_rating DESC),
  INDEX idx_rating_count (rating_count DESC),
  INDEX idx_high_rating_ratio (high_rating_ratio DESC),
  
  -- 唯一約束
  UNIQUE KEY unique_source_item (item_source, item_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='商品評分統計表 (快取計算結果)';

-- ============================================================
-- STEP 5: 建立統一評分統計視圖
-- ============================================================

DROP VIEW IF EXISTS v_item_ratings;

CREATE VIEW v_item_ratings AS
SELECT 
  item_source,
  item_id,
  AVG(rating_value) as avg_rating,
  COUNT(*) as rating_count,
  SUM(rating_value) as rating_sum,
  
  -- 評分分布
  SUM(CASE WHEN rating_value = 5 THEN 1 ELSE 0 END) as rating_5_count,
  SUM(CASE WHEN rating_value = 4 THEN 1 ELSE 0 END) as rating_4_count,
  SUM(CASE WHEN rating_value = 3 THEN 1 ELSE 0 END) as rating_3_count,
  SUM(CASE WHEN rating_value = 2 THEN 1 ELSE 0 END) as rating_2_count,
  SUM(CASE WHEN rating_value = 1 THEN 1 ELSE 0 END) as rating_1_count,
  
  -- 高分統計
  SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END) as high_rating_count,
  SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END) / COUNT(*) as high_rating_ratio,
  
  -- 最新評分時間
  MAX(created_at) as latest_rating_time,
  MIN(created_at) as first_rating_time
  
FROM rating
GROUP BY item_source, item_id;

-- ============================================================
-- STEP 6: 建立帶權重的推薦查詢視圖 (items 來源)
-- ============================================================

DROP VIEW IF EXISTS v_items_with_ratings;

CREATE VIEW v_items_with_ratings AS
SELECT 
  i.*,
  COALESCE(s.avg_rating, 0) as avg_rating,
  COALESCE(s.rating_count, 0) as rating_count,
  COALESCE(s.high_rating_count, 0) as high_rating_count,
  COALESCE(s.high_rating_ratio, 0) as high_rating_ratio,
  
  -- 計算評分權重 (0.5 - 1.5)
  CASE 
    WHEN s.avg_rating IS NULL THEN 1.0
    WHEN s.avg_rating >= 4.5 THEN 1.5
    WHEN s.avg_rating >= 3.5 THEN 1.2
    WHEN s.avg_rating >= 2.5 THEN 0.9
    ELSE 0.5
  END as rating_weight,
  
  -- 計算熱度權重 (1.0 - 1.3)
  CASE 
    WHEN s.rating_count >= 10 THEN 1.3
    WHEN s.rating_count >= 5 THEN 1.2
    WHEN s.rating_count >= 1 THEN 1.1
    ELSE 1.0
  END as popularity_weight,
  
  -- 計算最終評分 (綜合權重)
  (CASE 
    WHEN s.avg_rating IS NULL THEN 1.0
    WHEN s.avg_rating >= 4.5 THEN 1.5
    WHEN s.avg_rating >= 3.5 THEN 1.2
    WHEN s.avg_rating >= 2.5 THEN 0.9
    ELSE 0.5
  END * 
  CASE 
    WHEN s.rating_count >= 10 THEN 1.3
    WHEN s.rating_count >= 5 THEN 1.2
    WHEN s.rating_count >= 1 THEN 1.1
    ELSE 1.0
  END) as final_score
  
FROM items i
LEFT JOIN item_stats s ON s.item_source = 'items' AND s.item_id = i.id;

-- ============================================================
-- STEP 7: 建立帶權重的推薦查詢視圖 (user_wardrobe 來源)
-- ============================================================

DROP VIEW IF EXISTS v_wardrobe_with_ratings;

CREATE VIEW v_wardrobe_with_ratings AS
SELECT 
  w.*,
  COALESCE(s.avg_rating, 0) as avg_rating,
  COALESCE(s.rating_count, 0) as rating_count,
  COALESCE(s.high_rating_count, 0) as high_rating_count,
  COALESCE(s.high_rating_ratio, 0) as high_rating_ratio,
  
  -- 計算評分權重 (0.5 - 1.5)
  CASE 
    WHEN s.avg_rating IS NULL THEN 1.0
    WHEN s.avg_rating >= 4.5 THEN 1.5
    WHEN s.avg_rating >= 3.5 THEN 1.2
    WHEN s.avg_rating >= 2.5 THEN 0.9
    ELSE 0.5
  END as rating_weight,
  
  -- 計算熱度權重 (1.0 - 1.3)
  CASE 
    WHEN s.rating_count >= 10 THEN 1.3
    WHEN s.rating_count >= 5 THEN 1.2
    WHEN s.rating_count >= 1 THEN 1.1
    ELSE 1.0
  END as popularity_weight,
  
  -- 計算最終評分 (綜合權重)
  (CASE 
    WHEN s.avg_rating IS NULL THEN 1.0
    WHEN s.avg_rating >= 4.5 THEN 1.5
    WHEN s.avg_rating >= 3.5 THEN 1.2
    WHEN s.avg_rating >= 2.5 THEN 0.9
    ELSE 0.5
  END * 
  CASE 
    WHEN s.rating_count >= 10 THEN 1.3
    WHEN s.rating_count >= 5 THEN 1.2
    WHEN s.rating_count >= 1 THEN 1.1
    ELSE 1.0
  END) as final_score
  
FROM user_wardrobe w
LEFT JOIN item_stats s ON s.item_source = 'user_wardrobe' AND s.item_id = w.id;

-- ============================================================
-- STEP 8: 建立觸發器 (自動更新統計表)
-- ============================================================

-- 插入評分時自動更新統計
DROP TRIGGER IF EXISTS after_rating_insert;

DELIMITER $$
CREATE TRIGGER after_rating_insert
AFTER INSERT ON rating
FOR EACH ROW
BEGIN
  -- 更新或插入統計表
  INSERT INTO item_stats (item_source, item_id, avg_rating, rating_count, rating_sum,
    rating_5_count, rating_4_count, rating_3_count, rating_2_count, rating_1_count,
    high_rating_count, high_rating_ratio)
  SELECT 
    NEW.item_source,
    NEW.item_id,
    AVG(rating_value),
    COUNT(*),
    SUM(rating_value),
    SUM(CASE WHEN rating_value = 5 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value = 4 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value = 3 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value = 2 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value = 1 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END) / COUNT(*)
  FROM rating
  WHERE item_source = NEW.item_source AND item_id = NEW.item_id
  GROUP BY item_source, item_id
  ON DUPLICATE KEY UPDATE 
    avg_rating = VALUES(avg_rating),
    rating_count = VALUES(rating_count),
    rating_sum = VALUES(rating_sum),
    rating_5_count = VALUES(rating_5_count),
    rating_4_count = VALUES(rating_4_count),
    rating_3_count = VALUES(rating_3_count),
    rating_2_count = VALUES(rating_2_count),
    rating_1_count = VALUES(rating_1_count),
    high_rating_count = VALUES(high_rating_count),
    high_rating_ratio = VALUES(high_rating_ratio),
    last_updated = CURRENT_TIMESTAMP;
END$$
DELIMITER ;

-- 更新評分時自動更新統計
DROP TRIGGER IF EXISTS after_rating_update;

DELIMITER $$
CREATE TRIGGER after_rating_update
AFTER UPDATE ON rating
FOR EACH ROW
BEGIN
  -- 更新統計表
  INSERT INTO item_stats (item_source, item_id, avg_rating, rating_count, rating_sum,
    rating_5_count, rating_4_count, rating_3_count, rating_2_count, rating_1_count,
    high_rating_count, high_rating_ratio)
  SELECT 
    NEW.item_source,
    NEW.item_id,
    AVG(rating_value),
    COUNT(*),
    SUM(rating_value),
    SUM(CASE WHEN rating_value = 5 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value = 4 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value = 3 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value = 2 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value = 1 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END) / COUNT(*)
  FROM rating
  WHERE item_source = NEW.item_source AND item_id = NEW.item_id
  GROUP BY item_source, item_id
  ON DUPLICATE KEY UPDATE 
    avg_rating = VALUES(avg_rating),
    rating_count = VALUES(rating_count),
    rating_sum = VALUES(rating_sum),
    rating_5_count = VALUES(rating_5_count),
    rating_4_count = VALUES(rating_4_count),
    rating_3_count = VALUES(rating_3_count),
    rating_2_count = VALUES(rating_2_count),
    rating_1_count = VALUES(rating_1_count),
    high_rating_count = VALUES(high_rating_count),
    high_rating_ratio = VALUES(high_rating_ratio),
    last_updated = CURRENT_TIMESTAMP;
END$$
DELIMITER ;

-- 刪除評分時自動更新統計
DROP TRIGGER IF EXISTS after_rating_delete;

DELIMITER $$
CREATE TRIGGER after_rating_delete
AFTER DELETE ON rating
FOR EACH ROW
BEGIN
  -- 檢查是否還有其他評分
  IF (SELECT COUNT(*) FROM rating WHERE item_source = OLD.item_source AND item_id = OLD.item_id) = 0 THEN
    -- 沒有評分了,刪除統計記錄
    DELETE FROM item_stats WHERE item_source = OLD.item_source AND item_id = OLD.item_id;
  ELSE
    -- 還有評分,更新統計
    INSERT INTO item_stats (item_source, item_id, avg_rating, rating_count, rating_sum,
      rating_5_count, rating_4_count, rating_3_count, rating_2_count, rating_1_count,
      high_rating_count, high_rating_ratio)
    SELECT 
      OLD.item_source,
      OLD.item_id,
      AVG(rating_value),
      COUNT(*),
      SUM(rating_value),
      SUM(CASE WHEN rating_value = 5 THEN 1 ELSE 0 END),
      SUM(CASE WHEN rating_value = 4 THEN 1 ELSE 0 END),
      SUM(CASE WHEN rating_value = 3 THEN 1 ELSE 0 END),
      SUM(CASE WHEN rating_value = 2 THEN 1 ELSE 0 END),
      SUM(CASE WHEN rating_value = 1 THEN 1 ELSE 0 END),
      SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END),
      SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END) / COUNT(*)
    FROM rating
    WHERE item_source = OLD.item_source AND item_id = OLD.item_id
    GROUP BY item_source, item_id
    ON DUPLICATE KEY UPDATE 
      avg_rating = VALUES(avg_rating),
      rating_count = VALUES(rating_count),
      rating_sum = VALUES(rating_sum),
      rating_5_count = VALUES(rating_5_count),
      rating_4_count = VALUES(rating_4_count),
      rating_3_count = VALUES(rating_3_count),
      rating_2_count = VALUES(rating_2_count),
      rating_1_count = VALUES(rating_1_count),
      high_rating_count = VALUES(high_rating_count),
      high_rating_ratio = VALUES(high_rating_ratio),
      last_updated = CURRENT_TIMESTAMP;
  END IF;
END$$
DELIMITER ;

-- ============================================================
-- STEP 9: 清理備份表 (可選)
-- ============================================================

-- 如果資料已成功遷移,可以刪除備份表
-- DROP TABLE IF EXISTS rating_backup;

-- ============================================================
-- 遷移完成!驗證表格結構
-- ============================================================

-- 顯示新建的表格和視圖
SHOW TABLES LIKE '%rating%';
SHOW TABLES LIKE '%item_stats%';

-- 顯示 rating 表格結構
DESCRIBE rating;

-- 顯示 item_stats 表格結構
DESCRIBE item_stats;

-- 顯示觸發器
SHOW TRIGGERS WHERE `Table` = 'rating';

-- ============================================================
-- 測試查詢範例
-- ============================================================

-- 查看所有評分
SELECT * FROM rating LIMIT 10;

-- 查看統計表
SELECT * FROM item_stats LIMIT 10;

-- 查看評分統計視圖
SELECT * FROM v_item_ratings LIMIT 10;

-- 查看帶權重的 items 推薦
SELECT id, name, category, avg_rating, rating_count, rating_weight, popularity_weight, final_score
FROM v_items_with_ratings
WHERE category = 'top'
ORDER BY final_score DESC
LIMIT 10;

-- ============================================================
-- 腳本結束
-- ============================================================
