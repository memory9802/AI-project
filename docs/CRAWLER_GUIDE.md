# 🕷️ 爬蟲開發完整指南

> **統整文檔**: 包含爬蟲流程、資料上傳、檢查清單等所有爬蟲相關內容  
> **更新日期**: 2025年11月26日

---

## 📖 目錄

1. [爬蟲 Pipeline 流程](#爬蟲-pipeline-流程)
2. [資料上傳流程](#資料上傳流程)
3. [重要提醒](#重要提醒)
4. [執行檢查清單](#執行檢查清單)
5. [常見問題](#常見問題)

---

## 🔄 爬蟲 Pipeline 流程

### Pipeline 架構

```
pipeline/
├── 01_crawl_uniqlo.py        # Step 1: 爬取 UNIQLO 商品
├── 02_detect_colors.py        # Step 2: 顏色檢測
├── 03_gemini_verify.py        # Step 3: AI 驗證
├── 04_data_processing.py      # Step 4: 資料處理
├── 05_database_import.py      # Step 5: 匯入資料庫
└── README.md                  # Pipeline 說明文檔
```

### Step 1: 爬取商品

**檔案:** `pipeline/01_crawl_uniqlo.py`

**功能:**
- 爬取 UNIQLO 網站商品資訊
- 下載商品圖片
- 儲存到 CSV

**使用:**
```bash
python3 pipeline/01_crawl_uniqlo.py

# 輸出:
# ✅ 成功爬取 500 個商品
# 📁 儲存到: dataset/uniqlo_items.csv
```

---

### Step 2: 顏色檢測

**檔案:** `pipeline/02_detect_colors.py`

**功能:**
- 分析商品圖片主要顏色
- 使用 OpenCV + K-means 演算法
- 標記 Pantone 色碼

**使用:**
```bash
python3 pipeline/02_detect_colors.py

# 輸出:
# 正在處理: item_001.jpg
# 檢測到顏色: #FF5733, #C70039, #900C3F
# ✅ 完成 500/500
```

---

### Step 3: AI 驗證

**檔案:** `pipeline/03_gemini_verify.py`

**功能:**
- 使用 Google Gemini API 驗證
- 確認性別分類
- 優化商品描述

**使用:**
```bash
python3 pipeline/03_gemini_verify.py

# 輸出:
# 正在驗證: UNIQLO 羽絨外套
# AI 分類: 男裝
# ✅ 完成驗證
```

---

### Step 4: 資料處理

**檔案:** `pipeline/04_data_processing.py`

**功能:**
- 清理資料
- 標準化格式
- 移除重複項目

**使用:**
```bash
python3 pipeline/04_data_processing.py

# 輸出:
# 原始資料: 500 筆
# 移除重複: 23 筆
# 清理完成: 477 筆
```

---

### Step 5: 匯入資料庫

**檔案:** `pipeline/05_database_import.py`

**功能:**
- 將 CSV 匯入 MySQL
- 檢查重複
- 生成匯入報告

**使用:**
```bash
python3 pipeline/05_database_import.py

# 輸出:
# 連接資料庫... ✅
# 匯入中: 477/477
# ✅ 成功匯入 477 筆商品
# 資料庫總計: 49,707 筆
```

---

### 完整執行流程

```bash
# 方法 1: 逐步執行 (推薦,方便除錯)
python3 pipeline/01_crawl_uniqlo.py
python3 pipeline/02_detect_colors.py
python3 pipeline/03_gemini_verify.py
python3 pipeline/04_data_processing.py
python3 pipeline/05_database_import.py

# 方法 2: 一鍵執行 (需要建立腳本)
./scripts/run_full_pipeline.sh

# 方法 3: 只執行特定步驟
python3 pipeline/05_database_import.py  # 只匯入已處理的資料
```

---

## 📤 資料上傳流程

### ⚠️ 為什麼只有你有資料?

如果你執行了爬蟲腳本,但其他組員看不到你爬的資料,這是**正常的**!

**原因:**
- 爬蟲資料儲存在**你電腦的 MySQL 資料庫**裡
- Git **不會自動同步**資料庫內容
- 你需要**手動匯出**資料庫並 commit

### 視覺化流程

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

### 方法 1: 使用一鍵腳本 (最簡單!)

```bash
./scripts/crawler_upload_helper.sh
```

**這個腳本會自動:**
1. ✅ 顯示當前資料統計
2. ✅ 匯出資料庫
3. ✅ 檢查檔案完整性
4. ✅ Git commit & push
5. ✅ 生成通知訊息給組員

**輸出範例:**
```
📊 當前資料統計
━━━━━━━━━━━━━━━━━━━━━━━━━━━
users    : 50 筆
items    : 49,707 筆 (+500 新增)
outfits  : 3 筆
━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 資料庫匯出成功!
📁 檔案: init/outfit_db_with_data.sql
📊 大小: 8.5 MB

📝 已提交: 更新資料庫: 新增 500 個 UNIQLO 秋冬商品
⬆️  已推送到 develop

📢 請複製以下訊息通知組員:
━━━━━━━━━━━━━━━━━━━━━━━━━━━
資料庫已更新!

更新內容: 新增 500 個 UNIQLO 秋冬商品
請執行:
1. git pull origin develop
2. docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

驗證: SELECT COUNT(*) FROM items; -- 應為 49,707
━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 方法 2: 手動執行 (4 步驟)

#### 1️⃣ 匯出資料庫
```bash
./scripts/export_database.sh
```

#### 2️⃣ 檢查檔案
```bash
# 查看檔案大小
ls -lh init/outfit_db_with_data.sql

# 確認有 INSERT 語句
grep -c "INSERT INTO" init/outfit_db_with_data.sql
# 應該 > 0
```

#### 3️⃣ Git 提交
```bash
git add init/outfit_db_with_data.sql
git commit -m "更新資料庫: 新增 500 個 UNIQLO 秋冬商品"
git push origin develop
```

#### 4️⃣ 通知組員
在 Line/Discord 群組發送:
```
📢 資料庫已更新!

更新內容: 新增 500 個 UNIQLO 秋冬商品
更新人: @你的名字
更新時間: 2025-11-26 15:30

請執行:
1. git pull origin develop
2. docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

驗證查詢:
SELECT COUNT(*) FROM items WHERE source='uniqlo';

預期結果: 721 (原 221 + 新增 500)
```

---

## ⚠️ 重要提醒

### ❌ 常見錯誤 1: 只 push 程式碼

```bash
# 這樣做是錯的!
git add pipeline/01_crawl_xxx.py
git commit -m "新增爬蟲"
git push

# 結果: 組員有你的程式碼,但沒有你爬的資料 ❌
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

### ❌ 常見錯誤 2: 只上傳 CSV

```bash
# 這樣做不夠!
git add dataset/new_items.csv
git commit -m "新增商品 CSV"
git push

# 問題: 組員下載後還需要執行匯入腳本 ⚠️
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

### ❌ 常見錯誤 3: 忘記通知組員

```bash
# 你 push 了,但沒通知
git push origin develop

# 結果: 組員不知道要 pull,繼續使用舊資料 ❌
```

### ✅ 正確做法

```bash
# 1. Push
git push origin develop

# 2. 立即通知
# 在群組發送更新訊息

# 3. 確認組員收到
# 等待組員回覆「✅ 已同步」
```

---

## 📋 執行檢查清單

### 爬蟲執行前

- [ ] Docker 容器正在運行 (`docker ps | grep outfit-mysql`)
- [ ] 已設定 API Key (如果需要)
- [ ] 網路連線正常
- [ ] 磁碟空間足夠 (至少 1GB)

### 爬蟲執行後

- [ ] 資料已儲存到 CSV (`ls dataset/`)
- [ ] CSV 檔案不是空的 (`wc -l dataset/*.csv`)
- [ ] 已執行資料處理腳本
- [ ] 已匯入資料庫

### 資料上傳前

- [ ] 已執行 `./scripts/export_database.sh`
- [ ] `init/outfit_db_with_data.sql` 檔案已更新
- [ ] 檔案大小 > 0 (不是空的)
- [ ] 有 INSERT 語句 (`grep -c "INSERT INTO" init/outfit_db_with_data.sql` > 0)

### 資料上傳後

- [ ] Commit message 清楚說明新增了什麼
- [ ] 已 push 到 GitHub
- [ ] 已通知組員
- [ ] 組員已回覆確認

---

## ❓ 常見問題

### Q1: 爬蟲執行到一半停止了?

**可能原因:**
1. 網路連線中斷
2. API 配額用完
3. 目標網站封鎖

**解決:**
```bash
# 查看錯誤訊息
python3 pipeline/01_crawl_uniqlo.py 2>&1 | tee crawl.log

# 從中斷處繼續 (如果腳本支援)
python3 pipeline/01_crawl_uniqlo.py --resume

# 或降低爬取速度
python3 pipeline/01_crawl_uniqlo.py --delay 3
```

---

### Q2: 顏色檢測結果不準確?

**可能原因:**
1. 圖片品質不佳
2. 背景干擾
3. 參數需要調整

**解決:**
```python
# 調整 K-means 集群數量
# 在 02_detect_colors.py 中修改:
n_clusters = 5  # 原本是 3,可以改為 5
```

---

### Q3: Gemini API 回應太慢?

**可能原因:**
1. 網路延遲
2. API 服務繁忙
3. Token 數量過多

**解決:**
```bash
# 減少每次處理的數量
python3 pipeline/03_gemini_verify.py --batch-size 10

# 增加超時時間
python3 pipeline/03_gemini_verify.py --timeout 60
```

---

### Q4: 匯入資料庫時出現重複資料?

**解決:**
```sql
-- 方法 1: 檢查重複 (在匯入前)
SELECT name, COUNT(*) as count 
FROM items 
GROUP BY name 
HAVING count > 1;

-- 方法 2: 刪除重複 (保留最新的)
DELETE t1 FROM items t1
INNER JOIN items t2 
WHERE t1.id < t2.id 
AND t1.name = t2.name;

-- 方法 3: 使用 INSERT IGNORE (在腳本中)
INSERT IGNORE INTO items (...) VALUES (...);
```

---

### Q5: 組員說「資料還是舊的」?

**檢查清單:**

```bash
# 1. 確認你有 push
git log -1

# 2. 確認組員有 pull
# (請組員執行)
git pull origin develop
git log -1  # 應該和你的一樣

# 3. 確認組員有匯入
# (請組員執行)
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT COUNT(*) FROM items;
"
# 應該顯示最新數量

# 4. 如果還是不對,重新匯入
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql
```

---

### Q6: 如何只爬取特定類別的商品?

**修改腳本:**
```python
# 在 01_crawl_uniqlo.py 中添加:
categories = ['上衣', '外套', '褲子']  # 只爬這些類別

for category in categories:
    crawl_category(category)
```

---

### Q7: 爬取的圖片要不要上傳到 Git?

**建議: 不要!**

**原因:**
- 圖片檔案大,會讓 repo 變很大
- Git 不適合管理二進制檔案
- GitHub 有容量限制

**替代方案:**
```bash
# 方案 1: 只儲存圖片 URL (推薦)
# 在資料庫中只存 image_url,不下載圖片

# 方案 2: 使用圖床
# 上傳到 Imgur/Cloudinary,儲存連結

# 方案 3: 使用雲端儲存
# 上傳到 Google Drive/AWS S3,分享連結

# .gitignore 中排除圖片資料夾
echo "images/" >> .gitignore
echo "dataset/*.jpg" >> .gitignore
echo "dataset/*.png" >> .gitignore
```

---

## 💡 最佳實踐

### ✅ 推薦做法

1. **小批次爬取** - 先測試 10 筆,確認無誤再大量爬取
2. **保留原始資料** - 每個 step 都儲存中間結果
3. **記錄日誌** - 使用 logging 記錄執行過程
4. **定期備份** - 重要資料多備份幾份
5. **禮貌爬蟲** - 加入延遲,不要對目標網站造成負擔

### ❌ 避免做法

1. ❌ 一次爬取上萬筆資料
2. ❌ 不檢查就直接匯入資料庫
3. ❌ 覆蓋原始資料
4. ❌ 短時間大量請求
5. ❌ 忽略錯誤訊息

---

## 🎯 記住這個口訣

```
爬完 → 處理 → 匯入 → 匯出 → Commit → Push → 通知

🕷️  →  🔧  →  📥  →  📤  →   📝   →  ⬆️  →  📢
```

---

## 🔗 相關文檔

- **資料庫同步**: 參考 `docs/DATABASE_GUIDE.md`
- **Git 版本管理**: 參考主目錄 `GIT_GUIDE.md`
- **團隊協作**: 參考 `docs/TEAM_GUIDE.md`
- **Pipeline 詳細說明**: 參考 `pipeline/README.md`

---

**更新日期:** 2025年11月26日  
**維護人:** liaoyiting
