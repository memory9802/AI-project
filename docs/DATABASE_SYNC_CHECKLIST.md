# ✅ 資料庫共享檢查清單

## 🎯 給開發者 (負責匯出資料的人)

在通知組員之前,請確認:

### 1. 匯出資料庫
```bash
# 執行匯出腳本
./scripts/export_database.sh

# 或手動執行
docker exec outfit-mysql mysqldump \
  -uroot -prootpassword \
  --databases outfit_db \
  --no-create-db \
  --single-transaction \
  --default-character-set=utf8mb4 \
  > init/outfit_db_with_data.sql
```

- [ ] ✅ 檔案已生成: `init/outfit_db_with_data.sql`
- [ ] ✅ 檔案大小合理 (約 8 MB)

### 2. 驗證匯出內容
```bash
# 檢查是否有 INSERT 語句
grep -c "INSERT INTO" init/outfit_db_with_data.sql
```

- [ ] ✅ 有 INSERT 語句 (應該看到數字 > 0)
- [ ] ✅ 檔案開頭有 character set 設定

### 3. 提交到 Git
```bash
git add init/outfit_db_with_data.sql
git add docs/
git add scripts/setup_database_for_teammates.sh
git add SETUP_FOR_TEAMMATES.md
git commit -m "更新資料庫備份:包含 50 個用戶和 49,707 筆商品"
git push origin Crawler&Detection
```

- [ ] ✅ 已 commit
- [ ] ✅ 已 push 到 GitHub

### 4. 通知組員
```
📢 組員們好!

資料庫已更新,請執行以下步驟同步:

1. git pull origin Crawler&Detection
2. ./scripts/setup_database_for_teammates.sh

或手動執行:
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

測試帳號: admin / admin123

詳細說明: SETUP_FOR_TEAMMATES.md
```

- [ ] ✅ 已通知組員 (Slack/Discord/Line)

---

## 🎯 給組員 (要同步資料的人)

### 1. 更新程式碼
```bash
cd AI-project-crawler-test
git pull origin Crawler&Detection
```

- [ ] ✅ 看到 `outfit_db_with_data.sql` 檔案更新
- [ ] ✅ 沒有 merge conflict

### 2. 檢查 Docker
```bash
# 確認 Docker Desktop 已開啟
docker ps
```

- [ ] ✅ Docker 正在運行
- [ ] ✅ outfit-mysql 容器存在

### 3. 匯入資料庫 (選擇一種方式)

**方式 A: 一鍵腳本 (推薦)**
```bash
./scripts/setup_database_for_teammates.sh
```

**方式 B: 手動執行**
```bash
docker exec -i outfit-mysql mysql \
  -uroot -prootpassword outfit_db \
  < init/outfit_db_with_data.sql
```

- [ ] ✅ 沒有錯誤訊息
- [ ] ✅ 看到匯入完成訊息

### 4. 驗證資料
```bash
docker exec outfit-mysql mysql \
  -uroot -prootpassword outfit_db \
  -e "SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM items;"
```

- [ ] ✅ users: 50 筆
- [ ] ✅ items: 49,707 筆

### 5. 測試登入
```bash
# 連接 DBeaver 並執行
SELECT * FROM users WHERE username = 'admin';
```

- [ ] ✅ 看到 admin 用戶
- [ ] ✅ 有 email 和 favorite_style 欄位

---

## 🔧 故障排除檢查清單

### 問題: 找不到 outfit_db_with_data.sql

**檢查:**
- [ ] 是否在專案根目錄?
- [ ] 是否執行了 `git pull`?
- [ ] 檔案路徑: `init/outfit_db_with_data.sql`

**解決:**
```bash
# 確認檔案存在
ls -lh init/outfit_db_with_data.sql
```

---

### 問題: Docker 容器不存在

**檢查:**
- [ ] Docker Desktop 是否開啟?
- [ ] 是否執行 `docker-compose up -d`?

**解決:**
```bash
# 啟動容器
docker-compose up -d
sleep 15

# 檢查狀態
docker ps | grep outfit-mysql
```

---

### 問題: 匯入失敗 (ERROR 2002)

**檢查:**
- [ ] MySQL 是否啟動完成?
- [ ] 是否等待足夠時間?

**解決:**
```bash
# 等待 MySQL 啟動
sleep 20

# 檢查 MySQL 日誌
docker logs outfit-mysql | tail -20

# 重新匯入
docker exec -i outfit-mysql mysql \
  -uroot -prootpassword outfit_db \
  < init/outfit_db_with_data.sql
```

---

### 問題: 資料量不對

**檢查:**
- [ ] 是否完整匯入?
- [ ] 是否有錯誤訊息?

**解決:**
```bash
# 清空資料庫重新匯入
docker exec outfit-mysql mysql -uroot -prootpassword -e "
DROP DATABASE IF EXISTS outfit_db;
CREATE DATABASE outfit_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
"

# 重新匯入
docker exec -i outfit-mysql mysql \
  -uroot -prootpassword outfit_db \
  < init/outfit_db_with_data.sql

# 驗證
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'items' as table_name, COUNT(*) as count FROM items;
"
```

---

### 問題: DBeaver 顯示亂碼

**檢查:**
- [ ] 連接屬性是否設定 UTF-8?

**解決:**
參考 `docs/DBEAVER_CONNECTION_GUIDE.md`

在 DBeaver 連接設定加入:
- characterEncoding = UTF-8
- useUnicode = true

---

## 📊 最終驗證清單

所有人應該看到相同的結果:

```sql
-- 1. 用戶數量
SELECT COUNT(*) FROM users;
-- 預期: 50

-- 2. 商品數量  
SELECT COUNT(*) FROM items;
-- 預期: 49,707

-- 3. 測試帳號
SELECT username, email FROM users WHERE username IN ('admin', 'demo', 'test');
-- 預期: 3 筆資料

-- 4. 資料來源分佈
SELECT source, COUNT(*) FROM items GROUP BY source ORDER BY COUNT(*) DESC;
-- 預期:
--   styles_dataset: 44,407
--   fashion_small: 4,999
--   uniqlo: 221
--   malefashion: 80
```

- [ ] ✅ 所有數字都一致
- [ ] ✅ 可以用 admin/admin123 登入
- [ ] ✅ 中文顯示正常

---

## 🎉 完成!

如果所有檢查都通過,恭喜!你們的資料庫已經同步成功。

**下一步:**
- [ ] 開始開發前端/後端功能
- [ ] 使用測試帳號進行登入測試
- [ ] 參考 `docs/TEST_ACCOUNTS.md` 查看完整帳號列表

---

## 📚 相關文件

- 📖 [資料庫運作原理圖解](docs/DATABASE_CONCEPTS_EXPLAINED.md)
- 📖 [完整共享指南](docs/DATABASE_SHARING_GUIDE.md)
- 🚀 [組員快速上手](SETUP_FOR_TEAMMATES.md)
- 🔑 [測試帳號列表](docs/TEST_ACCOUNTS.md)

---

**更新日期:** 2025-11-26
