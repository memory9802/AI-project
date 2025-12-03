# 登入系統說明文件

## 概述

已完成帳號密碼登入系統，包含前端介面、後端 API 以及資料庫整合。

## 功能特點

### ✅ 已實現功能

1. **用戶註冊**
   - 電子郵件和密碼註冊
   - 可選用戶名（若未提供則從電子郵件生成）
   - 密碼強度驗證（至少 6 個字元）
   - 電子郵件和用戶名唯一性檢查
   - 使用 bcrypt 加密密碼

2. **用戶登入**
   - 電子郵件和密碼登入
   - bcrypt 密碼驗證
   - Session 管理
   - 錯誤提示

3. **用戶登出**
   - 清除 Session
   - 安全登出

4. **Session 管理**
   - 基於 Flask Session
   - 儲存用戶 ID、用戶名、電子郵件

5. **API 端點**
   - `POST /api/login` - 登入
   - `POST /api/register` - 註冊
   - `POST /api/logout` - 登出
   - `GET /api/user` - 取得當前用戶資訊（需要登入）

## 測試帳號

已創建 5 個測試帳號，密碼統一為 `password123`：

| 用戶名 | 電子郵件 | 密碼 | 偏好風格 |
|--------|----------|------|----------|
| testuser1 | test1@example.com | password123 | 休閒 |
| testuser2 | test2@example.com | password123 | 正式 |
| testuser3 | test3@example.com | password123 | 運動 |
| testuser4 | test4@example.com | password123 | 街頭 |
| testuser5 | test5@example.com | password123 | 韓風 |

## 安裝與設定

### 1. 安裝依賴

```bash
cd app
pip install -r requirements.txt
```

### 2. 設定環境變數

在 `.env` 文件中添加（或使用環境變數）：

```bash
SECRET_KEY=your-secret-key-here
DB_HOST=mysql
DB_PORT=3306
DB_USER=root
DB_PASS=rootpassword
DB_NAME=outfit_db
```

### 3. 初始化資料庫

執行測試用戶 SQL 腳本：

```bash
# 如果使用 Docker
docker exec -i mysql_container mysql -uroot -prootpassword outfit_db < init/04_test_users.sql

# 如果本地 MySQL
mysql -uroot -p outfit_db < init/04_test_users.sql
```

### 4. 啟動應用

```bash
cd app
python app.py
```

## 使用方式

### 前端登入頁面

訪問：`http://localhost:5000/login`

### API 使用範例

#### 登入

```javascript
const response = await fetch('/api/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        email: 'test1@example.com',
        password: 'password123'
    })
});

const data = await response.json();
// 回應: { success: true, message: "登入成功", user: {...} }
```

#### 註冊

```javascript
const response = await fetch('/api/register', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        username: 'newuser',
        email: 'newuser@example.com',
        password: 'password123'
    })
});

const data = await response.json();
// 回應: { success: true, message: "註冊成功", user: {...} }
```

#### 登出

```javascript
const response = await fetch('/api/logout', {
    method: 'POST'
});

const data = await response.json();
// 回應: { success: true, message: "已成功登出" }
```

#### 取得當前用戶

```javascript
const response = await fetch('/api/user');
const data = await response.json();
// 回應: { success: true, user: { id, username, email, favorite_style } }
```

## 資料庫結構

### users 表

```sql
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE DEFAULT NULL,
  password_hash VARCHAR(255) DEFAULT NULL COMMENT 'bcrypt 加密密碼',
  favorite_style VARCHAR(50) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## 安全特性

1. **密碼加密**：使用 bcrypt 加密，成本因子為 12
2. **Session 管理**：使用 Flask Session，支援伺服器端 session
3. **輸入驗證**：前後端雙重驗證
4. **SQL 注入防護**：使用參數化查詢
5. **錯誤處理**：友善的錯誤提示，不洩露敏感資訊

## 裝飾器使用

### @login_required

保護需要登入的路由：

```python
@app.route('/api/protected')
@login_required
def protected_route():
    user = get_current_user()
    return jsonify({"user": user})
```

## 檔案結構

```
app/
├── app.py                      # 主應用，包含登入/註冊 API
├── requirements.txt            # 依賴套件（已添加 Flask-Session）
└── templates/
    └── login.html             # 登入/註冊頁面

init/
└── 04_test_users.sql          # 測試用戶 SQL 腳本
```

## 後續改進建議

1. **密碼重設功能**：實現忘記密碼的郵件發送功能
2. **OAuth 整合**：實現 Google、Facebook 第三方登入
3. **驗證碼**：添加圖形驗證碼或 reCAPTCHA
4. **記住我功能**：實現持久化登入
5. **用戶資料編輯**：允許用戶修改個人資料
6. **密碼強度指示器**：前端顯示密碼強度
7. **兩步驗證**：添加 2FA 支援
8. **登入歷史記錄**：記錄用戶登入時間和 IP

## 常見問題

### Q: 忘記密碼怎麼辦？
A: 目前尚未實現密碼重設功能，可以直接在資料庫中更新密碼 hash。

### Q: 如何生成新的密碼 hash？
A: 使用 Python：
```python
import bcrypt
password = "your_password"
hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print(hash.decode('utf-8'))
```

### Q: Session 存儲在哪裡？
A: 預設存儲在伺服器端的 `flask_session` 目錄中（filesystem 模式）。

### Q: 如何改用 Redis 存儲 Session？
A: 修改 `app.py`：
```python
from flask_session import Session
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
Session(app)
```

## 測試

### 手動測試

1. 訪問 `http://localhost:5000/login`
2. 使用測試帳號登入
3. 登入成功後會跳轉到 `/home`

### API 測試

使用 curl 測試登入 API：

```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test1@example.com","password":"password123"}'
```

## 技術棧

- **後端**：Flask 3.1.2
- **密碼加密**：bcrypt 4.2.1
- **Session 管理**：Flask-Session 0.8.0
- **資料庫**：MySQL 8.0
- **前端**：Tailwind CSS + Vanilla JavaScript

## 更新日誌

### 2025-12-03
- ✅ 實現基本登入註冊功能
- ✅ 添加 Session 管理
- ✅ 創建 5 個測試帳號
- ✅ 更新前端介面連接後端 API
- ✅ 添加錯誤提示和驗證

## 聯絡方式

如有問題或建議，請聯繫開發團隊。
