# 🗄️ 資料庫管理完整指南

> **統整文檔**: 包含資料庫結構、同步方法、概念說明等所有資料庫相關內容  
> **更新日期**: 2025年11月26日

---

## 📖 目錄

1. [資料庫結構](#資料庫結構)
2. [資料庫同步規則](#資料庫同步規則)
3. [基礎概念說明](#基礎概念說明)
4. [標準工作流程](#標準工作流程)
5. [常見問題](#常見問題)

---

## 📊 資料庫結構

### 基本資訊

- **資料庫名稱**: `outfit_db`
- **MySQL 版本**: 8.0
- **字符集**: utf8mb4
- **容器名稱**: `outfit-mysql`
- **連接資訊**:
  - Host: localhost
  - Port: 3306
  - User: root
  - Password: rootpassword

### 資料表結構 (11 張表)

```sql
1. users              -- 用戶資料 (50 個測試用戶)
   ├── id (主鍵)
   ├── username (用戶名)
   ├── email (電子郵件)
   ├── password_hash (bcrypt 加密密碼)
   ├── favorite_style (喜好風格)
   └── created_at (註冊時間)

2. items              -- 單品項目 (49,707 個商品)
   ├── id (主鍵)
   ├── name (商品名稱)
   ├── category (類別)
   ├── color (顏色)
   ├── price (價格)
   ├── image_url (圖片連結)
   └── source (來源: uniqlo/gu 等)

3. outfits            -- 穿搭組合
   ├── id (主鍵)
   ├── name (穿搭名稱)
   ├── style (風格)
   ├── season (季節)
   └── description (描述)

4. outfit_items       -- 穿搭與單品關聯表
   ├── outfit_id (外鍵 → outfits)
   └── item_id (外鍵 → items)

5. user_wardrobe      -- 用戶衣櫃
   ├── user_id (外鍵 → users)
   └── item_id (外鍵 → items)

6. outfit_ratings     -- 穿搭評分
   ├── user_id (外鍵 → users)
   ├── outfit_id (外鍵 → outfits)
   └── rating (評分 1-5)

7. partner_products   -- 合作商品
8. user_preferences   -- 用戶偏好
9. user_body_info     -- 用戶體型資料
10. conversation_history  -- 對話記錄
11. sessions          -- 對話 session
```

### 當前資料統計

```sql
-- 查詢資料量
SELECT 
  'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'items', COUNT(*) FROM items
UNION ALL
SELECT 'outfits', COUNT(*) FROM outfits;

-- 結果:
-- users: 50
-- items: 49,707
-- outfits: 3
```

---

## ⚠️ 資料庫同步黃金規則

### 規則 1: 統一檔名 (最重要!)

**所有人必須遵守:**
```
✅ 正確: init/outfit_db_with_data.sql
❌ 錯誤: init/outfit_db_<任何其他名字>.sql
```

**為什麼?**
- Git 自動追蹤版本,不需要檔名加日期
- 避免團隊成員搞混「哪個是最新版本」
- 腳本和文檔都指向同一個檔案

### 規則 2: 兩個 SQL 檔案的區別

| 檔案 | 用途 | 內容 | 使用時機 |
|------|------|------|----------|
| `outfit_db.sql` | 結構定義 | 只有 CREATE TABLE | 第一次建立資料庫 |
| `outfit_db_with_data.sql` | 完整備份 | CREATE TABLE + INSERT | 同步完整資料 ⭐ |

**⚠️ 新組員請使用 `outfit_db_with_data.sql`!**

---

## 📚 基礎概念說明

### SQL 檔案 vs 資料庫實例

很多新手會搞混這兩個概念:

#### 1. SQL 檔案 (藍圖)

```
init/outfit_db.sql
├── 這是一個文字檔
├── 包含 SQL 指令
├── Git 可以追蹤
└── 不會自動更新
```

**類比:** 這像是「房屋設計圖」

#### 2. 資料庫實例 (建築物)

```
Docker 容器內的 MySQL
├── outfit-mysql (容器名稱)
├── 正在運行的資料庫
├── Git 不會追蹤
└── 會隨著使用而改變
```

**類比:** 這像是「實際的房子」

#### 視覺化說明

```
[SQL 檔案]                [資料庫實例]
   📄                         🏢
   ↓                          ↓
設計圖紙                   實際建築
  ↓                          ↓
用文字描述                 真實存在的資料
  ↓                          ↓
可以用 Git 同步            不能用 Git 同步
  ↓                          ↓
需要手動匯出                需要手動匯入
```

### 同步的正確理解

```
你的電腦                    組員的電腦
   ↓                          ↓
[MySQL 資料庫]            [MySQL 資料庫]
   ↓                          ↑
匯出成 SQL 檔              匯入 SQL 檔
   ↓                          ↑
   └──→ [Git push] ──→ [Git pull] ──┘
```

**關鍵點:**
- Git 只能同步「檔案」(SQL 檔)
- Git 不能同步「正在運行的程式」(MySQL 資料庫)
- 需要手動「匯出」和「匯入」

---

## 🔄 標準工作流程

### 情境 A: 你修改了資料庫

**適用時機:**
- 執行了爬蟲,新增了商品
- 手動修改了資料
- 執行了資料處理腳本

**步驟:**

```bash
# 1. 匯出資料庫 (自動覆蓋 outfit_db_with_data.sql)
./scripts/export_database.sh

# 輸出:
# ✅ 資料庫匯出成功!
# 📁 檔案: init/outfit_db_with_data.sql
# 📊 大小: 8.2 MB
# 📝 INSERT 語句數量: 11

# 2. 查看變更
git diff init/outfit_db_with_data.sql | head -50

# 3. 提交
git add init/outfit_db_with_data.sql
git commit -m "更新資料庫: 新增 500 個 UNIQLO 秋冬商品"

# 4. 推送
git push origin develop

# 5. 通知組員 (複製以下訊息到 Line/Discord)
```

**通知訊息範本:**
```
📢 資料庫已更新

更新內容: 新增 500 個 UNIQLO 秋冬商品
更新時間: 2025-11-26 14:30
更新人: @你的名字

請執行以下指令同步:
1. git pull origin develop
2. docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

驗證查詢:
SELECT COUNT(*) FROM items WHERE source='uniqlo';

預期結果: 721 (原 221 + 新增 500)
```

---

### 情境 B: 收到「資料庫已更新」通知

**步驟:**

```bash
# 1. 下載最新版本
git pull origin develop

# 輸出:
# remote: Counting objects: 3, done.
# Updating a1b2c3d..d4e5f6g
# Fast-forward
#  init/outfit_db_with_data.sql | 523 +++++++++++++++++++++++++++++++++++++++++++

# 2. 檢查檔案是否更新
ls -lh init/outfit_db_with_data.sql

# 應該看到更新時間是剛剛

# 3. 重新匯入資料庫
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

# 輸出:
# (MySQL 會顯示匯入進度)

# 4. 驗證 (使用通知訊息中的查詢)
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT COUNT(*) FROM items WHERE source='uniqlo';
"

# 應該看到:
# +----------+
# | COUNT(*) |
# +----------+
# |      721 |
# +----------+

# 5. 回報完成
# 在群組回覆:「✅ 已同步,資料正確」
```

---

### 情境 C: 兩人同時修改資料庫 (衝突處理)

**症狀:**
```bash
git push
# error: failed to push some refs
# hint: Updates were rejected because the remote contains work
```

**發生原因:**
- 張三匯出並 push 了 `outfit_db_with_data.sql`
- 李四也修改資料庫並嘗試 push
- Git 檢測到衝突

**解決方法 (重要!):**

```bash
# 1. 先下載最新版本
git pull origin develop
# 會顯示: CONFLICT (content): Merge conflict in init/outfit_db_with_data.sql

# 2. ⚠️ 不要手動編輯 SQL 檔案!
#    正確做法:決定「誰的資料比較完整」

# ────────────────────────────────────────
# 選項 A: 使用遠端版本 (張三的)
# ────────────────────────────────────────
git checkout --theirs init/outfit_db_with_data.sql
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

# 完成,李四的修改丟失


# ────────────────────────────────────────
# 選項 B: 使用本地版本 (李四的)
# ────────────────────────────────────────
git checkout --ours init/outfit_db_with_data.sql

# 完成,張三的修改被覆蓋


# ────────────────────────────────────────
# 選項 C: 合併兩人的資料 (推薦!)
# ────────────────────────────────────────

# C.1 使用遠端版本 (張三的資料)
git checkout --theirs init/outfit_db_with_data.sql
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

# C.2 再執行李四的 Python 腳本 (重新匯入李四的資料)
python3 pipeline/01_crawl_uniqlo.py
python3 pipeline/05_database_import.py

# C.3 重新匯出 (現在包含兩人的資料)
./scripts/export_database.sh

# C.4 提交
git add init/outfit_db_with_data.sql
git commit -m "解決衝突: 合併張三和李四的資料"
git push origin develop

# C.5 通知組員
# 「⚠️ 剛解決資料庫衝突,已合併所有資料,請重新同步」
```

---

## 🛠️ 實用腳本

### 1. 匯出資料庫

**位置:** `scripts/export_database.sh`

```bash
./scripts/export_database.sh
```

**功能:**
- 自動匯出到 `init/outfit_db_with_data.sql`
- 包含所有表結構和資料
- 顯示檔案大小和 INSERT 數量

### 2. 檢查資料庫

**位置:** `scripts/check_database.py`

```bash
python3 scripts/check_database.py
```

**功能:**
- 顯示所有表的資料量
- 檢查資料完整性
- 驗證連接狀態

### 3. 爬蟲上傳助手

**位置:** `scripts/crawler_upload_helper.sh`

```bash
./scripts/crawler_upload_helper.sh
```

**功能:**
- 互動式引導上傳流程
- 自動匯出資料庫
- 生成通知訊息
- 檢查檔案完整性

---

## ❓ 常見問題

### Q1: 為什麼我的資料其他人看不到?

**A:** 因為資料在你的 MySQL 資料庫裡,Git 不會自動同步資料庫。

**解決:**
```bash
./scripts/export_database.sh
git add init/outfit_db_with_data.sql
git commit -m "更新資料庫"
git push origin develop
```

---

### Q2: outfit_db.sql 和 outfit_db_with_data.sql 有什麼區別?

**A:** 

| 檔案 | 內容 | 使用時機 |
|------|------|----------|
| `outfit_db.sql` | 只有表結構 | 第一次建立空資料庫 |
| `outfit_db_with_data.sql` | 結構+資料 | 同步完整資料 ⭐ |

**新組員應該用 `outfit_db_with_data.sql`!**

---

### Q3: 匯入資料庫時出現錯誤怎麼辦?

**常見錯誤 1: 容器未運行**
```bash
# 錯誤訊息:
# Error: No such container: outfit-mysql

# 解決:
docker-compose up -d
```

**常見錯誤 2: 字符集問題**
```bash
# 錯誤訊息:
# ERROR 1366: Incorrect string value

# 解決: 檔案開頭已設定 utf8mb4
# 確認 init/outfit_db_with_data.sql 第一行:
SET NAMES utf8mb4;
```

**常見錯誤 3: 權限問題**
```bash
# 錯誤訊息:
# ERROR 1045: Access denied

# 解決: 檢查密碼
docker exec outfit-mysql mysql -uroot -prootpassword -e "SELECT 1;"
```

---

### Q4: 如何只匯出特定表的資料?

**A:**
```bash
# 只匯出 items 表
docker exec outfit-mysql mysqldump -uroot -prootpassword outfit_db items > items_only.sql

# 只匯出結構,不含資料
docker exec outfit-mysql mysqldump -uroot -prootpassword --no-data outfit_db > structure_only.sql
```

---

### Q5: 如何備份資料庫?

**A:**
```bash
# 方法 1: 使用腳本 (推薦)
./scripts/export_database.sh

# 方法 2: 手動備份
docker exec outfit-mysql mysqldump -uroot -prootpassword outfit_db > backup_$(date +%Y%m%d).sql

# 方法 3: 複製容器資料
docker cp outfit-mysql:/var/lib/mysql ./mysql_backup/
```

---

### Q6: 資料庫資料太多,Git 推送失敗?

**A:** GitHub 有單檔 100MB 限制,如果超過:

**選項 1: 使用 Git LFS (推薦)**
```bash
# 安裝 Git LFS
brew install git-lfs  # macOS
# choco install git-lfs  # Windows

# 初始化
git lfs install

# 追蹤大檔案
git lfs track "*.sql"

# 提交
git add .gitattributes init/outfit_db_with_data.sql
git commit -m "使用 Git LFS 管理資料庫檔案"
git push
```

**選項 2: 排除資料檔案**
```bash
# 加入 .gitignore
echo "init/outfit_db_with_data.sql" >> .gitignore

# 改用雲端分享 (Google Drive/Dropbox)
```

---

### Q7: 如何重置資料庫到初始狀態?

**A:**
```bash
# 1. 停止容器
docker-compose down

# 2. 刪除資料
rm -rf mysql_data/

# 3. 重新啟動
docker-compose up -d

# 4. 匯入初始資料
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db.sql
```

---

## 📋 快速檢查清單

### 匯出資料前

- [ ] Docker 容器正在運行 (`docker ps | grep outfit-mysql`)
- [ ] 資料已正確儲存到 MySQL
- [ ] 已驗證資料正確性 (SELECT COUNT(*) 查詢)

### 匯出後

- [ ] 檔案存在 (`ls -lh init/outfit_db_with_data.sql`)
- [ ] 檔案大小合理 (> 0)
- [ ] 有 INSERT 語句 (`grep -c "INSERT INTO" init/outfit_db_with_data.sql`)

### 推送前

- [ ] Git diff 查看變更
- [ ] Commit message 清楚說明
- [ ] 已通知組員

### 匯入後

- [ ] 執行驗證查詢
- [ ] 資料量正確
- [ ] 應用程式可正常運行

---

## 🔗 相關文檔

- **Git 版本管理**: 參考主目錄 `GIT_GUIDE.md`
- **爬蟲資料上傳**: 參考 `docs/CRAWLER_GUIDE.md`
- **團隊協作**: 參考 `docs/TEAM_GUIDE.md`
- **測試帳號**: 參考 `docs/TEST_ACCOUNTS.md`

---

**更新日期:** 2025年11月26日  
**維護人:** liaoyiting

