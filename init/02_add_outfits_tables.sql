-- =============================================
-- 創建 outfits 和 outfit_items 表
-- 用於穿搭組合推薦功能
-- =============================================

-- 創建 outfits 表 (穿搭組合)
CREATE TABLE IF NOT EXISTS `outfits` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '穿搭名稱',
  `occasion` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '適合場合',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '穿搭描述',
  `image_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '穿搭圖片',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_occasion` (`occasion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='穿搭組合表';

-- 創建 outfit_items 表 (穿搭與單品的關聯表)
CREATE TABLE IF NOT EXISTS `outfit_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `outfit_id` int NOT NULL COMMENT '穿搭ID',
  `item_id` int NOT NULL COMMENT '單品ID',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_outfit_item` (`outfit_id`,`item_id`),
  KEY `fk_outfit_items_outfit` (`outfit_id`),
  KEY `fk_outfit_items_item` (`item_id`),
  CONSTRAINT `fk_outfit_items_outfit` FOREIGN KEY (`outfit_id`) REFERENCES `outfits` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_outfit_items_item` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='穿搭單品關聯表';

-- 插入示範數據
INSERT INTO `outfits` (`name`, `occasion`, `description`, `image_url`) VALUES
('休閒約會裝', '約會', '輕鬆自在的約會穿搭,白T搭配牛仔褲,舒適又有型', '/static/pic/png1.png'),
('商務正裝', '上班', '專業商務look,西裝外套配襯衫,展現專業形象', '/static/pic/png2.png'),
('運動健身裝', '運動', '透氣運動服飾,適合健身房或戶外運動', '/static/pic/png3.png'),
('週末休閒裝', '休閒', '舒適的週末穿搭,T恤配休閒褲,輕鬆逛街', '/static/pic/png0.png'),
('派對造型', '派對', '時尚派對裝,展現個人風格與魅力', '/static/pic/png1.png')
ON DUPLICATE KEY UPDATE `name`=VALUES(`name`);
