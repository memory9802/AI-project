-- ===================================
-- 測試用戶資料插入腳本
-- 創建 5 個測試帳號供開發測試使用
-- ===================================

-- 密碼都是 "password123"，使用 bcrypt 加密
-- bcrypt hash for "password123": $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr3xCjP3i

INSERT INTO users (username, email, password_hash, favorite_style) VALUES
('testuser1', 'test1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr3xCjP3i', '休閒'),
('testuser2', 'test2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr3xCjP3i', '正式'),
('testuser3', 'test3@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr3xCjP3i', '運動'),
('testuser4', 'test4@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr3xCjP3i', '街頭'),
('testuser5', 'test5@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr3xCjP3i', '韓風')
ON DUPLICATE KEY UPDATE username=username;

-- 顯示測試帳號資訊
SELECT '測試帳號已創建完成！' as message;
SELECT '使用以下帳號登入：' as info;
SELECT 
    username as '用戶名',
    email as '電子郵件',
    'password123' as '密碼',
    favorite_style as '偏好風格'
FROM users 
WHERE username IN ('testuser1', 'testuser2', 'testuser3', 'testuser4', 'testuser5')
ORDER BY username;
