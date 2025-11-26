# 用戶資料生成報告

## 📊 執行摘要

成功生成 **50 個虛擬用戶**資料,採用業界標準的 bcrypt 加密方式儲存密碼,適用於課程專題的前端登入測試。

**執行時間:** 2025-11-26  
**資料庫:** outfit_db  
**表格:** users

---

## ✅ 完成項目

### 1. 資料庫結構更新

更新 `users` 表格結構如下:

```sql
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE DEFAULT NULL,
  password_hash VARCHAR(255) DEFAULT NULL COMMENT 'bcrypt 加密密碼',
  favorite_style VARCHAR(50) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**主要欄位說明:**
- `username`: 用戶名 (唯一)
- `email`: 電子郵件 (唯一)
- `password_hash`: bcrypt 加密後的密碼
- `favorite_style`: 喜好風格 (休閒、街頭、正式等 24 種)
- `created_at`: 註冊時間 (自動生成)

---

### 2. 用戶資料生成

✅ **總計: 50 個用戶**

#### 主要測試帳號 (前 3 個)

| 用戶名 | 密碼 | Email | 用途 |
|--------|------|-------|------|
| admin | `admin123` | admin@example.com | 管理員測試帳號 |
| demo | `demo123` | demo@example.com | 展示用帳號 |
| test | `test123` | test@example.com | 一般測試帳號 |

#### 虛擬用戶 (47 個)

- 用戶名: fashion_lover, style_icon, trendy_guy, chic_lady... 等 47 個
- 統一密碼: `password123`
- Email: {username}@example.com
- 風格: 隨機分配 24 種風格

---

### 3. 風格分佈統計

```
工裝         █████ (5)
復古         ████ (4)
正式         ████ (4)
運動         ████ (4)
學院風       ███ (3)
波希米亞     ███ (3)
其他風格     ██ 或 █ (1-2)
```

**總計 24 種不同風格**,分佈合理,適合測試各種情境。

---

### 4. 密碼加密方式

✅ **採用 bcrypt 加密演算法**

**優點:**
1. ✅ 業界標準的密碼加密方式
2. ✅ 單向雜湊,無法反向解密
3. ✅ 內建 salt,防止彩虹表攻擊
4. ✅ 符合 OWASP 安全標準
5. ✅ 適合課程專題展示專業能力

**加密示例:**
```python
import bcrypt

# 加密
password = "admin123"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
# 結果: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lW9BZlnNHbBm

# 驗證
is_valid = bcrypt.checkpw(password.encode('utf-8'), hashed)
# 結果: True
```

---

## 📁 生成的檔案

### 1. 測試帳號文件
**位置:** `docs/TEST_ACCOUNTS.md`  
**狀態:** ✅ 已生成 (已加入 .gitignore)

**內容包含:**
- 📋 完整 50 個測試帳號列表 (用戶名 + 明文密碼)
- 🔐 後端登入 API 範例 (Python/Flask)
- 🌐 前端登入範例 (JavaScript/Fetch)
- ✅ 密碼驗證說明

⚠️ **安全提醒:** 此文件已加入 `.gitignore`,不會被 push 到 GitHub

---

### 2. 用戶生成腳本
**位置:** `scripts/generate_users_with_bcrypt.py`  
**狀態:** ✅ 已創建

**功能:**
- 清空現有用戶資料
- 生成 50 個用戶 (含 bcrypt 加密密碼)
- 自動生成測試帳號文件
- 驗證密碼正確性

**使用方式:**
```bash
python3 scripts/generate_users_with_bcrypt.py
```

---

### 3. SQL 初始化檔案
**位置:** `init/outfit_db.sql`  
**狀態:** ✅ 已更新

**更新內容:**
- 修正 users 表格結構 (新增 email, 改為 password_hash)
- 移除 INSERT 語句 (改用 Python 腳本生成)
- 新增註解說明使用方式

---

## 🔐 前端登入實作指南

### 後端 API 範例 (Flask)

```python
import bcrypt
import pymysql
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/login', methods=['POST'])
def login():
    """用戶登入 API"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # 驗證輸入
    if not username or not password:
        return jsonify({
            'success': False,
            'message': '請輸入帳號和密碼'
        }), 400
    
    # 連接資料庫
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='rootpassword',
        database='outfit_db',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    
    try:
        # 查詢用戶
        cursor.execute(
            "SELECT id, username, email, password_hash, favorite_style FROM users WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()
        
        if not user:
            return jsonify({
                'success': False,
                'message': '用戶不存在'
            }), 401
        
        user_id, username, email, password_hash, favorite_style = user
        
        # 驗證密碼
        if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            return jsonify({
                'success': True,
                'message': '登入成功',
                'user': {
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'favorite_style': favorite_style
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '密碼錯誤'
            }), 401
            
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

---

### 前端範例 (JavaScript)

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>登入測試</title>
</head>
<body>
    <h2>用戶登入</h2>
    <form id="loginForm">
        <input type="text" id="username" placeholder="用戶名" required><br>
        <input type="password" id="password" placeholder="密碼" required><br>
        <button type="submit">登入</button>
    </form>
    <div id="result"></div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('result').innerHTML = 
                        `<p style="color: green;">✅ 登入成功!</p>
                         <p>用戶: ${data.user.username}</p>
                         <p>風格: ${data.user.favorite_style}</p>`;
                    
                    // 儲存用戶資訊
                    localStorage.setItem('user', JSON.stringify(data.user));
                } else {
                    document.getElementById('result').innerHTML = 
                        `<p style="color: red;">❌ ${data.message}</p>`;
                }
            } catch (error) {
                console.error('登入錯誤:', error);
                document.getElementById('result').innerHTML = 
                    `<p style="color: red;">❌ 連接失敗</p>`;
            }
        });
    </script>
</body>
</html>
```

---

## 🧪 測試方式

### 1. 在 DBeaver 中查看用戶

```sql
-- 查看所有用戶
SELECT id, username, email, favorite_style, created_at 
FROM users 
ORDER BY id;

-- 查看風格分佈
SELECT favorite_style, COUNT(*) as count 
FROM users 
WHERE favorite_style IS NOT NULL
GROUP BY favorite_style 
ORDER BY count DESC;

-- 查看特定用戶
SELECT * FROM users WHERE username = 'admin';
```

---

### 2. 使用 Python 測試密碼驗證

```python
import bcrypt
import pymysql

# 連接資料庫
conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='rootpassword',
    database='outfit_db',
    charset='utf8mb4'
)
cursor = conn.cursor()

# 測試登入
username = 'admin'
password = 'admin123'

cursor.execute(
    "SELECT password_hash FROM users WHERE username = %s",
    (username,)
)
result = cursor.fetchone()

if result:
    password_hash = result[0]
    is_valid = bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    print(f"密碼驗證結果: {'✅ 成功' if is_valid else '❌ 失敗'}")
else:
    print("❌ 用戶不存在")

conn.close()
```

---

## 📝 注意事項

### ✅ 優點

1. **專業性高** - 使用業界標準的 bcrypt 加密
2. **安全性佳** - 密碼無法反向解密
3. **易於測試** - 提供完整的測試帳號列表
4. **文檔完整** - 包含前後端實作範例
5. **適合展示** - 可作為課程專題加分項

---

### ⚠️ 重要提醒

1. **TEST_ACCOUNTS.md 已加入 .gitignore**
   - 不會被 push 到 GitHub
   - 僅供本地開發測試使用
   
2. **正式環境注意事項**
   - 不要在正式環境使用相同密碼
   - 建議加入 JWT token 機制
   - 加入登入失敗次數限制
   - 加入 HTTPS 加密傳輸

3. **課程報告建議**
   - 強調使用 bcrypt 加密的專業性
   - 說明符合 OWASP 安全標準
   - 展示完整的登入流程設計

---

## 📊 資料庫最終狀態

```
資料庫: outfit_db
表格: users
總用戶數: 50

欄位結構:
- id (INT, PRIMARY KEY)
- username (VARCHAR(100), UNIQUE)
- email (VARCHAR(255), UNIQUE)
- password_hash (VARCHAR(255))
- favorite_style (VARCHAR(50))
- created_at (TIMESTAMP)

主要測試帳號:
✅ admin / admin123
✅ demo / demo123
✅ test / test123

虛擬用戶: 47 個
統一密碼: password123
```

---

## 🎯 下一步建議

1. ✅ **查看測試帳號** - 開啟 `docs/TEST_ACCOUNTS.md`
2. ✅ **實作後端 API** - 參考文件中的 Flask 範例
3. ✅ **測試登入功能** - 使用提供的測試帳號
4. ✅ **前端整合** - 實作登入表單和驗證邏輯
5. ✅ **準備展示** - 在報告中說明安全設計

---

## ✅ 總結

成功完成方案 A 的所有要求:
- ✅ 保持密碼加密 (bcrypt)
- ✅ 生成 50 個測試用戶 (3 個主要 + 47 個虛擬)
- ✅ 提供完整測試帳號文件
- ✅ 包含前後端實作範例
- ✅ 符合專業開發標準
- ✅ 適合課程專題使用

**所有密碼都可以正常用於前端登入驗證!** 🎉
