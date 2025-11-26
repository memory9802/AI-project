# 🔑 測試帳號快速參考

## 主要測試帳號

| 用戶名 | 密碼 | 用途 |
|--------|------|------|
| **admin** | `admin123` | 管理員測試 |
| **demo** | `demo123` | 展示用帳號 |
| **test** | `test123` | 一般測試 |

## 其他 47 個帳號

**用戶名:** fashion_lover, style_icon, trendy_guy, chic_lady... 等  
**統一密碼:** `password123`

## 📋 完整列表

查看完整 50 個測試帳號: [TEST_ACCOUNTS.md](./TEST_ACCOUNTS.md)

## 🔐 登入測試方式

### 1. 直接測試 (Python)

```python
# 測試帳號: admin / admin123
import pymysql
import bcrypt

conn = pymysql.connect(host='localhost', port=3306, user='root', 
                      password='rootpassword', database='outfit_db')
cursor = conn.cursor()

cursor.execute("SELECT password_hash FROM users WHERE username = 'admin'")
password_hash = cursor.fetchone()[0]

# 驗證密碼
is_valid = bcrypt.checkpw(b'admin123', password_hash.encode('utf-8'))
print(f"登入結果: {'✅ 成功' if is_valid else '❌ 失敗'}")
```

### 2. 前端測試

在前端登入表單輸入:
- 用戶名: `admin`
- 密碼: `admin123`

後端 API 會使用 bcrypt 驗證密碼。

## 📚 詳細文件

- [完整測試帳號列表](./TEST_ACCOUNTS.md) - 50 個帳號的詳細資訊
- [用戶生成報告](./USER_GENERATION_REPORT.md) - 完整的實作指南和 API 範例

## ⚠️ 安全提醒

✅ 所有密碼使用 bcrypt 加密  
✅ TEST_ACCOUNTS.md 已加入 .gitignore  
✅ 適合課程專題使用  
⚠️ 請勿將測試帳號文件上傳到公開 GitHub
