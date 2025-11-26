# 🕷️ 爬蟲組員專用:資料上傳指南

## 🎯 給負責爬蟲衣服資料的組員

如果你剛爬完新的衣服資料,發現**只有你的本機資料庫有資料**,其他組員看不到,這是正常的!

**原因:** 你執行爬蟲腳本後,資料只儲存在**你電腦的 Docker 容器**裡,Git 不會自動同步資料庫內容。

---

## ✅ 你的理解正確!

```
你的理解:
「將資料庫匯出成 .sql 檔,用 git 同步給其他人」

✅ 完全正確!就是這樣!
```

---

## 📋 完整上傳流程 (4 步驟)

### 步驟 1️⃣: 匯出資料庫 (在你的電腦執行)

```bash
# 方法 A: 使用自動化腳本 (推薦)
./scripts/export_database.sh
```

或

```bash
# 方法 B: 手動執行 mysqldump
docker exec outfit-mysql mysqldump \
  -uroot -prootpassword \
  --databases outfit_db \
  --no-create-db \
  --single-transaction \
  --default-character-set=utf8mb4 \
  > init/outfit_db_with_data.sql
```

**這會做什麼?**
- 將你電腦 Docker 容器裡的資料庫
- 匯出成 `init/outfit_db_with_data.sql` 檔案
- 這個檔案包含所有表格結構和資料

---

### 步驟 2️⃣: 檢查匯出的檔案

```bash
# 檢查檔案是否生成
ls -lh init/outfit_db_with_data.sql

# 應該看到類似:
# -rw-r--r--  1 user  staff   8.2M  11月 26 13:27 init/outfit_db_with_data.sql
```

```bash
# 檢查是否有資料 (應該看到數字 > 0)
grep -c "INSERT INTO" init/outfit_db_with_data.sql
```

**如果看到數字 > 0,表示匯出成功!** ✅

---

### 步驟 3️⃣: 提交到 Git

```bash
# 1. 查看變更
git status

# 應該看到:
#   modified:   init/outfit_db_with_data.sql

# 2. 加入暫存區
git add init/outfit_db_with_data.sql

# 3. 提交 (記得寫清楚你爬了什麼資料)
git commit -m "更新資料庫:新增 XXX 個衣服資料 (來源: XXX網站)"

# 範例:
# git commit -m "更新資料庫:新增 500 個 ZARA 商品資料"
# git commit -m "更新資料庫:新增 1000 個淘寶女裝資料"

# 4. 推送到 GitHub
git push origin Crawler&Detection
```

---

### 步驟 4️⃣: 通知其他組員

在你們的群組 (Line/Discord/Slack) 發訊息:

```
📢 資料庫已更新!

我剛爬了 XXX 個新商品,已上傳到 GitHub。

請大家執行:
1. git pull origin Crawler&Detection
2. docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

資料來源: XXX 網站
商品數量: XXX 筆
```

---

## 🔄 完整流程圖解

```
┌──────────────────────────────────────────────────────────────┐
│  步驟 1: 你爬完資料                                            │
└──────────────────────────────────────────────────────────────┘

你的電腦:
  🕷️ 執行爬蟲腳本
     python3 pipeline/01_crawl_xxx.py
     
  💾 資料儲存到本機資料庫
     outfit-mysql 容器
     └─ items 表新增 500 筆 ← 只在你電腦!
     
     ❌ 其他組員看不到


┌──────────────────────────────────────────────────────────────┐
│  步驟 2: 匯出資料庫                                            │
└──────────────────────────────────────────────────────────────┘

  💾 MySQL 資料庫             →    📄 SQL 檔案
  ┌──────────────┐           →    ┌──────────────────┐
  │ items        │  mysqldump →    │ CREATE TABLE...  │
  │ ├─ 原有資料  │           →    │ INSERT INTO...   │
  │ └─ 新增 500  │           →    │ INSERT INTO...   │
  └──────────────┘           →    │ (所有資料)       │
                             →    └──────────────────┘
                                  outfit_db_with_data.sql


┌──────────────────────────────────────────────────────────────┐
│  步驟 3: Git 同步                                             │
└──────────────────────────────────────────────────────────────┘

  📄 outfit_db_with_data.sql
     │
     │ git add
     │ git commit
     │ git push
     ▼
  🌐 GitHub Repository
     └─ outfit_db_with_data.sql (已更新)


┌──────────────────────────────────────────────────────────────┐
│  步驟 4: 其他組員下載                                          │
└──────────────────────────────────────────────────────────────┘

組員 A 的電腦:                組員 B 的電腦:
  git pull                     git pull
  └─ 下載最新 SQL 檔           └─ 下載最新 SQL 檔
  
  匯入資料庫                    匯入資料庫
  └─ items 表有 500 筆新資料   └─ items 表有 500 筆新資料
  
  ✅ 資料一致!                 ✅ 資料一致!
```

---

## ⚠️ 常見錯誤和解決方法

### 錯誤 1: 忘記匯出就 commit

```
❌ 錯誤做法:
   1. 執行爬蟲 (資料存在資料庫)
   2. git commit (只提交了程式碼)
   3. git push
   
   結果: 其他組員下載後沒有你的資料

✅ 正確做法:
   1. 執行爬蟲
   2. 匯出資料庫 (./scripts/export_database.sh)
   3. git add init/outfit_db_with_data.sql
   4. git commit
   5. git push
```

---

### 錯誤 2: CSV 檔案 vs 資料庫

```
❌ 錯誤想法:
   「我把 CSV 檔案 commit 了,組員就有資料了」
   
   問題: 組員下載 CSV 後,還需要執行匯入腳本才能把資料放進資料庫

✅ 正確做法:
   同時提供:
   1. CSV 原始檔案 (放在 dataset/ 資料夾)
   2. 匯出的資料庫 (outfit_db_with_data.sql)
   
   這樣組員可以:
   - 選擇 A: 直接匯入資料庫 (快速)
   - 選擇 B: 從 CSV 重新匯入 (了解流程)
```

---

### 錯誤 3: 檔案太大無法 push

```
如果 outfit_db_with_data.sql 超過 100 MB:

方法 A: 壓縮檔案
  gzip init/outfit_db_with_data.sql
  # 會產生 outfit_db_with_data.sql.gz
  
  組員使用:
  gunzip init/outfit_db_with_data.sql.gz
  docker exec -i outfit-mysql mysql ... < init/outfit_db_with_data.sql

方法 B: 使用 Git LFS
  git lfs track "init/outfit_db_with_data.sql"
  git add .gitattributes
  git add init/outfit_db_with_data.sql
  git commit -m "使用 Git LFS 管理大檔案"

方法 C: 雲端分享
  上傳到 Google Drive / Dropbox
  在 README 提供下載連結
```

---

## 📊 範例:完整的爬蟲資料上傳流程

### 情境:你剛爬完 H&M 的 300 個商品

```bash
# 1. 執行爬蟲腳本 (假設你已經寫好)
python3 pipeline/01_crawl_hm.py

# 輸出:
# ✅ 爬取完成:300 個商品
# ✅ 已儲存到資料庫

# 2. 驗證資料是否在資料庫
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT COUNT(*) as total FROM items WHERE source = 'hm';
"

# 應該看到:
# +-------+
# | total |
# +-------+
# |   300 |
# +-------+

# 3. 匯出資料庫
./scripts/export_database.sh

# 輸出:
# 🔄 開始匯出資料庫...
# ✅ 匯出完成: init/outfit_db_with_data.sql

# 4. 檢查檔案大小
ls -lh init/outfit_db_with_data.sql

# 5. 提交到 Git
git add init/outfit_db_with_data.sql
git commit -m "更新資料庫:新增 300 個 H&M 商品資料"
git push origin Crawler&Detection

# 6. 通知組員
# (在 Line 群組發訊息)
```

---

## 🔍 驗證清單

在 push 之前,請確認:

- [ ] ✅ 執行了匯出腳本 (`./scripts/export_database.sh`)
- [ ] ✅ `init/outfit_db_with_data.sql` 檔案已更新
- [ ] ✅ 檔案大小合理 (不是 0 bytes)
- [ ] ✅ 檔案包含 INSERT 語句 (執行 `grep -c "INSERT INTO" init/outfit_db_with_data.sql` 應該 > 0)
- [ ] ✅ commit message 清楚說明新增了什麼資料
- [ ] ✅ 已通知組員更新

---

## 💡 最佳實踐

### 1. Commit Message 範例

```bash
# ✅ 好的 commit message
git commit -m "更新資料庫:新增 500 個 UNIQLO 秋冬新品"
git commit -m "更新資料庫:新增 1000 個淘寶女裝資料 (價格 100-500 元區間)"
git commit -m "更新資料庫:爬取 ZARA 全站上衣類商品 (共 800 筆)"

# ❌ 不好的 commit message
git commit -m "更新"
git commit -m "add data"
git commit -m "爬蟲完成"
```

### 2. 定期匯出

```
建議時機:
✅ 每次爬完新資料後立即匯出
✅ 每天工作結束前匯出一次
✅ 在開會前匯出,讓大家有最新資料

不要:
❌ 累積好幾天才匯出一次
❌ 等組員要用才匯出
```

### 3. 資料驗證

```bash
# 匯出前先驗證資料
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT source, COUNT(*) as count 
FROM items 
GROUP BY source 
ORDER BY count DESC;
"

# 確認新資料已經在資料庫裡
```

---

## 🆘 遇到問題?

### Q: 我執行 export_database.sh 失敗

**A: 檢查 Docker 是否運行**
```bash
docker ps | grep outfit-mysql

# 如果沒有,啟動它:
docker-compose up -d
sleep 15
```

---

### Q: 檔案太大,push 很慢

**A: 確認是否真的需要這麼多資料**
```bash
# 查看資料量
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT 
  table_name, 
  ROUND((data_length + index_length) / 1024 / 1024, 2) as 'Size (MB)' 
FROM information_schema.tables 
WHERE table_schema = 'outfit_db' 
ORDER BY (data_length + index_length) DESC;
"

# 如果 items 表太大,考慮:
# 1. 只匯出必要的表格
# 2. 壓縮檔案
# 3. 使用 Git LFS
```

---

### Q: Git push 被拒絕 (檔案太大)

**A: GitHub 有 100 MB 限制**
```bash
# 方法 1: 壓縮
gzip init/outfit_db_with_data.sql
git add init/outfit_db_with_data.sql.gz
git commit -m "壓縮資料庫檔案"

# 方法 2: 使用 Git LFS
git lfs install
git lfs track "*.sql"
git add .gitattributes
git add init/outfit_db_with_data.sql
git commit -m "使用 Git LFS 管理資料庫檔案"
```

---

### Q: 組員說匯入後還是沒有我的資料

**A: 請組員確認:**
```bash
# 1. 是否有 pull 最新版本?
git pull origin Crawler&Detection

# 2. 檔案是否有更新?
ls -lh init/outfit_db_with_data.sql
# 檢查時間戳記

# 3. 重新匯入
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

# 4. 驗證
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT source, COUNT(*) FROM items GROUP BY source;
"
```

---

## 📝 快速指令參考卡

```bash
# ═══════════════════════════════════════════
# 爬蟲組員專用指令
# ═══════════════════════════════════════════

# 1. 匯出資料庫
./scripts/export_database.sh

# 2. 檢查檔案
ls -lh init/outfit_db_with_data.sql
grep -c "INSERT INTO" init/outfit_db_with_data.sql

# 3. 提交到 Git
git add init/outfit_db_with_data.sql
git commit -m "更新資料庫:新增 XXX 個商品"
git push origin Crawler&Detection

# 4. 驗證資料庫內容
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT source, COUNT(*) as count FROM items GROUP BY source;
"
```

---

## 🎯 總結

### ✅ 你的理解完全正確!

```
正確流程:
1. 爬蟲存入本機資料庫
2. 匯出成 .sql 檔
3. Git 同步給其他人
4. 其他人匯入資料庫

就是這樣!🎉
```

### 記住這個口訣

```
爬完資料 → 匯出 SQL → Git 提交 → 通知組員

Export → Add → Commit → Push → Notify
```

---

## 📚 延伸閱讀

- 📖 [資料庫運作原理圖解](./DATABASE_CONCEPTS_EXPLAINED.md) - 理解 SQL 檔案 vs 資料庫
- 📖 [組員快速上手指南](../SETUP_FOR_TEAMMATES.md) - 給其他組員看的
- 📖 [完整資料庫共享指南](./DATABASE_SHARING_GUIDE.md) - 詳細說明

---

**有任何問題隨時問!** 🕷️💪

記得:爬完資料後一定要**匯出並 commit**,不然就只有你看得到! 😊
