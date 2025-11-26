# 📢 給爬蟲組員的重要提醒

## ⚠️ 為什麼只有你有資料?

如果你執行了爬蟲腳本,但其他組員看不到你爬的資料,這是**正常的**!

**原因:**
- 爬蟲資料儲存在**你電腦的 MySQL 資料庫**裡
- Git **不會自動同步**資料庫內容
- 你需要**手動匯出**資料庫並 commit

---

## ✅ 你的理解完全正確!

```
「將資料庫匯出成 .sql 檔,用 git 同步給其他人」

✅ 就是這樣!
```

---

## 🚀 最簡單的方法:一鍵腳本

```bash
# 執行這個腳本,會自動幫你完成所有步驟
./scripts/crawler_upload_helper.sh
```

這個腳本會:
1. ✅ 顯示當前資料統計
2. ✅ 匯出資料庫
3. ✅ 檢查檔案完整性
4. ✅ Git commit & push
5. ✅ 生成通知訊息給組員

---

## 📋 或手動執行 4 步驟

### 1️⃣ 匯出資料庫
```bash
./scripts/export_database.sh
```

### 2️⃣ 檢查檔案
```bash
ls -lh init/outfit_db_with_data.sql
grep -c "INSERT INTO" init/outfit_db_with_data.sql
```

### 3️⃣ Git 提交
```bash
git add init/outfit_db_with_data.sql
git commit -m "更新資料庫:新增 XXX 個商品 (來源: XXX)"
git push origin Crawler&Detection
```

### 4️⃣ 通知組員
在 Line/Discord 群組發送:
```
📢 資料庫已更新!

請執行:
1. git pull origin Crawler&Detection
2. docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

新增: XXX 個商品
```

---

## ⚠️ 常見錯誤

### ❌ 錯誤 1: 只 push 程式碼
```bash
# 這樣做是錯的!
git add pipeline/01_crawl_xxx.py
git commit -m "新增爬蟲"
git push

# 結果: 組員有你的程式碼,但沒有你爬的資料
```

### ✅ 正確做法
```bash
# 1. 先匯出資料庫
./scripts/export_database.sh

# 2. 一起 commit
git add pipeline/01_crawl_xxx.py
git add init/outfit_db_with_data.sql
git commit -m "新增爬蟲 + 資料庫更新"
git push
```

---

### ❌ 錯誤 2: 只上傳 CSV
```bash
# 這樣做不夠!
git add dataset/new_items.csv
git commit -m "新增商品 CSV"
git push

# 問題: 組員下載後還需要執行匯入腳本
```

### ✅ 正確做法
```bash
# 同時上傳 CSV 和資料庫
git add dataset/new_items.csv
git add init/outfit_db_with_data.sql
git commit -m "新增商品資料 (CSV + 資料庫)"
git push
```

---

## 📊 流程圖

```
你爬完資料
    ↓
💾 資料在你的 MySQL
    ↓
📤 匯出成 .sql 檔
    ↓
📝 Git commit
    ↓
⬆️  Git push
    ↓
📢 通知組員
    ↓
✅ 組員 pull & 匯入
    ↓
🎉 大家資料一致!
```

---

## 🔍 驗證清單

上傳前確認:

- [ ] ✅ 已執行 `./scripts/export_database.sh`
- [ ] ✅ `init/outfit_db_with_data.sql` 檔案已更新
- [ ] ✅ 檔案大小 > 0 (不是空的)
- [ ] ✅ 有 INSERT 語句 (執行 `grep -c "INSERT INTO" init/outfit_db_with_data.sql` > 0)
- [ ] ✅ Commit message 清楚說明新增了什麼
- [ ] ✅ 已 push 到 GitHub
- [ ] ✅ 已通知組員

---

## 💡 記住這個口訣

```
爬完 → 匯出 → Commit → Push → 通知

🕷️  →  💾  →   📝   →  ⬆️  →  📢
```

---

## 📚 詳細文件

- 📖 [完整上傳指南](docs/CRAWLER_TEAM_UPLOAD_GUIDE.md) ⭐
- 📊 [視覺化流程圖](docs/CRAWLER_UPLOAD_FLOWCHART.txt)
- 📖 [資料庫概念說明](docs/DATABASE_CONCEPTS_EXPLAINED.md)

---

## 🆘 需要幫助?

如果遇到問題:

1. 查看 [常見問題](docs/CRAWLER_TEAM_UPLOAD_GUIDE.md#-遇到問題)
2. 詢問組員
3. 檢查 Docker 是否運行: `docker ps | grep outfit-mysql`
4. 確認檔案是否存在: `ls -lh init/outfit_db_with_data.sql`

---

**重點:** 爬完資料後,記得**立即匯出並 commit**!

不然就只有你看得到資料 😊
