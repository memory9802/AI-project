# 🚀 組員快速上手指南

## 第一次使用 (完整步驟)

### 1️⃣ Clone 專案
```bash
git clone <repository-url>
cd AI-project-crawler-test
```

### 2️⃣ 確認 Docker 已安裝並運行
- macOS: 開啟 Docker Desktop
- Windows: 開啟 Docker Desktop

### 3️⃣ 執行一鍵設定腳本
```bash
./scripts/setup_database_for_teammates.sh
```

**就這麼簡單!** 🎉

---

## 已經 Clone 過,要更新資料

```bash
# 1. 更新程式碼
git pull origin Crawler&Detection

# 2. 重新匯入資料庫
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql
```

---

## 測試帳號

| 用戶名 | 密碼 |
|--------|------|
| admin | admin123 |
| demo | demo123 |
| test | test123 |

其他 47 個帳號密碼都是: `password123`

**完整帳號列表:** `docs/TEST_ACCOUNTS.md` (請找負責資料庫的組員要)

---

## DBeaver 連接設定

```
Host: localhost
Port: 3306
Database: outfit_db
Username: root
Password: rootpassword
```

在「驅動程式屬性」加入:
- characterEncoding = UTF-8
- useUnicode = true

---

## 檢查資料是否正確

```bash
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT COUNT(*) as users_count FROM users;
SELECT COUNT(*) as items_count FROM items;
"
```

應該看到:
- users_count: 50
- items_count: 49,707

---

## 遇到問題?

### Docker 容器沒有運行
```bash
docker-compose up -d
```

### 資料庫連不上
```bash
# 檢查容器狀態
docker ps | grep outfit-mysql

# 重啟容器
docker-compose restart
```

### 資料不對
```bash
# 重新匯入
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql
```

---

## 📚 詳細文件

- 📖 [完整資料庫共享指南](docs/DATABASE_SHARING_GUIDE.md)
- 🔑 [測試帳號列表](docs/TEST_ACCOUNTS.md) (找組員要)
- 📊 [DBeaver 連接指南](docs/DBEAVER_CONNECTION_GUIDE.md)

---

## 📞 需要幫助?

請提供:
1. 作業系統 (macOS/Windows)
2. 錯誤訊息截圖
3. `docker ps` 的輸出
