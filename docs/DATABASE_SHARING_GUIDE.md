# 資料庫共享指南 - 給組員使用

## 🎯 目的

讓所有組員能夠在自己的電腦上建立**完全相同**的資料庫環境,包含所有資料。

---

## 📚 基礎概念

### SQL 腳本 vs 資料庫實例

```
📄 SQL 腳本檔案                    💾 MySQL 資料庫實例
────────────────────              ──────────────────────
• 文字檔案 (.sql)                  • 運行中的資料庫 server
• 可以用記事本打開                  • 需要 MySQL/Docker 執行
• 可以 git commit                 • 資料儲存在硬碟上
• 包含 SQL 指令                    • 可以查詢、新增、修改資料
                                  • 每台電腦需要分別建立

類比:
🏗️ 建築藍圖                       🏢 實際的建築物
📝 食譜                           🍕 做好的披薩
🎼 樂譜                           🎵 演奏的音樂
```

---

## 📁 專案中的資料庫相關檔案

```
/AI-project-crawler-test/
├─ 📄 docker-compose.yml          # Docker 配置 (MySQL 容器設定)
├─ init/
│   ├─ 📄 outfit_db.sql           # 資料庫結構 (只有表格定義,沒有資料)
│   └─ 📄 outfit_db_with_data.sql # 完整備份 (結構 + 所有資料) ⭐
├─ scripts/
│   ├─ 🐍 generate_users_with_bcrypt.py  # 生成 50 個用戶
│   ├─ 🐍 import_csv_to_db.py           # 匯入商品資料
│   └─ 🔧 export_database.sh            # 匯出資料庫腳本
└─ dataset/
    ├─ styles.csv                 # 時尚資料集 (44,407 筆)
    ├─ items_fashion_small_clean.csv  # 小型資料集 (4,999 筆)
    └─ ...
```

---

## ✅ 方法 1: 使用完整備份 (推薦) ⭐

### 適用情況
- ✅ 想要快速建立相同的資料庫
- ✅ 想要包含所有測試資料
- ✅ 不需要重新執行匯入腳本

### 步驟

#### 1️⃣ 下載最新版本

```bash
# 組員執行
cd /你的專案路徑/AI-project-crawler-test
git pull origin Crawler&Detection
```

#### 2️⃣ 啟動 Docker 容器

```bash
# 啟動 MySQL 容器
docker-compose up -d

# 等待 MySQL 啟動完成 (約 10-20 秒)
sleep 15
```

#### 3️⃣ 匯入完整資料庫

```bash
# 匯入資料庫 (包含所有資料)
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

echo "✅ 資料庫匯入完成!"
```

#### 4️⃣ 驗證資料

```bash
# 檢查資料是否正確
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT 'users 表' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'items 表' as table_name, COUNT(*) as count FROM items;
"
```

**預期結果:**
```
table_name | count
-----------|--------
users 表   | 50
items 表   | 49,707
```

---

## ✅ 方法 2: 從頭建立 (學習用)

### 適用情況
- ✅ 想要理解完整的建立流程
- ✅ 練習匯入資料的操作
- ✅ CSV 檔案有更新

### 步驟

#### 1️⃣ 啟動 Docker 容器

```bash
docker-compose up -d
sleep 15
```

#### 2️⃣ 建立資料庫結構

```bash
# 只建立表格結構 (不含資料)
docker exec -i outfit-mysql mysql -uroot -prootpassword < init/outfit_db.sql
```

#### 3️⃣ 匯入商品資料

```bash
# 匯入 CSV 資料 (49,707 筆商品)
python3 scripts/import_csv_to_db.py
```

#### 4️⃣ 生成用戶資料

```bash
# 生成 50 個測試用戶
python3 scripts/generate_users_with_bcrypt.py
```

---

## 🔄 更新流程 (當資料有變更時)

### 情況 1: 你新增了資料,想讓組員同步

#### A. 匯出最新資料庫

```bash
# 在你的電腦執行
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

#### B. 提交到 Git

```bash
git add init/outfit_db_with_data.sql
git commit -m "更新資料庫備份 (新增 XX 筆資料)"
git push origin Crawler&Detection
```

#### C. 通知組員

```
📢 通知組員:
「資料庫已更新!請執行:
1. git pull
2. docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql
」
```

---

## ⚠️ 常見問題

### Q1: 為什麼 outfit_db.sql 沒有用戶資料?

**A:** `outfit_db.sql` 是**初始化腳本**,只包含:
- ✅ 表格結構定義 (CREATE TABLE)
- ✅ 欄位定義
- ❌ **沒有實際資料** (需要執行 Python 腳本生成)

如果要包含資料,使用 `outfit_db_with_data.sql`。

---

### Q2: Git 會同步資料庫資料嗎?

**A:** ❌ **不會!** Git 只同步檔案,不同步資料庫:

```
✅ 會同步                      ❌ 不會同步
────────────                  ──────────────
.sql 檔案                     Docker 容器內的資料庫
.py 腳本                      MySQL 資料
.csv 檔案                     資料庫實例
程式碼                        運行中的服務
```

所以需要匯出 `.sql` 檔案,讓組員匯入。

---

### Q3: outfit_db_with_data.sql 太大怎麼辦?

**A:** 目前檔案大小約 **8.2 MB**,還可以接受。

如果超過 100MB:
1. **不要 commit 到 Git**,改用雲端硬碟分享
2. 只匯出必要的表格
3. 使用壓縮: `gzip init/outfit_db_with_data.sql`

---

### Q4: 組員匯入後資料還是不一樣?

**檢查清單:**

```bash
# 1. 確認檔案已更新
ls -lh init/outfit_db_with_data.sql

# 2. 確認 MySQL 容器運行中
docker ps | grep outfit-mysql

# 3. 清空資料庫重新匯入
docker exec outfit-mysql mysql -uroot -prootpassword -e "
DROP DATABASE IF EXISTS outfit_db;
CREATE DATABASE outfit_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
"

docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

# 4. 驗證資料
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM items;
"
```

---

### Q5: 我該用哪個 SQL 檔案?

| 檔案 | 用途 | 內容 |
|------|------|------|
| `outfit_db.sql` | 初始化結構 | 只有表格定義,沒有資料 |
| `outfit_db_with_data.sql` | 完整備份 | 結構 + 所有資料 (50 users + 49,707 items) |

**建議:**
- 👨‍💻 **開發時**: 用 `outfit_db_with_data.sql` (快速建立環境)
- 🏗️ **學習理解**: 用 `outfit_db.sql` + Python 腳本 (了解流程)

---

## 📝 快速指令參考

### 匯出資料庫
```bash
./scripts/export_database.sh
```

### 匯入資料庫
```bash
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql
```

### 檢查資料量
```bash
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT table_name, table_rows 
FROM information_schema.tables 
WHERE table_schema = 'outfit_db' 
ORDER BY table_rows DESC;
"
```

### 重新建立資料庫
```bash
# 1. 刪除舊資料庫
docker exec outfit-mysql mysql -uroot -prootpassword -e "DROP DATABASE IF EXISTS outfit_db;"

# 2. 建立新資料庫
docker exec outfit-mysql mysql -uroot -prootpassword -e "CREATE DATABASE outfit_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 3. 匯入資料
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql
```

---

## 🎯 組員快速上手流程

```bash
# 1. Clone 專案
git clone <repository-url>
cd AI-project-crawler-test

# 2. 啟動 Docker
docker-compose up -d
sleep 15

# 3. 匯入資料庫
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

# 4. 驗證
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "SELECT COUNT(*) FROM users;"

# 5. 使用 DBeaver 連接
# Host: localhost
# Port: 3306
# Database: outfit_db
# Username: root
# Password: rootpassword
```

---

## ✅ 檢查清單

組員完成後應該看到:

- ✅ users 表: 50 筆資料
- ✅ items 表: 49,707 筆資料
- ✅ 用戶名: admin, demo, test 等
- ✅ 商品來源: uniqlo, styles_dataset, fashion_small, malefashion
- ✅ 可以用 admin/admin123 登入測試

---

## 📞 需要幫助?

如果遇到問題,請提供:
1. 執行的指令
2. 錯誤訊息
3. `docker ps` 的輸出
4. `SELECT COUNT(*) FROM users;` 的結果

---

**更新日期:** 2025-11-26  
**資料庫版本:** outfit_db v1.0  
**總資料量:** 49,757 筆 (50 users + 49,707 items)
