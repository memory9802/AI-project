# 🎨 AI 穿搭推薦系統

> 基於 AI 的智能服飾推薦與色彩分析平台

## 📚 目錄

- [專案架構](#專案架構)
- [快速開始](#快速開始)
- [資料庫同步](#資料庫同步)
- [開發須知](#開發須知)
- [測試帳號](#測試帳號)
- [團隊協作](#團隊協作)

---

## 📁 專案架構

```
AI-project-crawler-test/
├─ 📱 前端資源
│   ├─ app/                    # Flask 應用主程式
│   │   ├─ app.py             # Flask 主程式
│   │   ├─ ai_agent.py        # AI 代理邏輯
│   │   ├─ langchain_agent.py # LangChain 整合
│   │   ├─ static/            # CSS、JS、圖片
│   │   └─ templates/         # HTML 模板
│   └─ page/                   # 舊版前端頁面
│
├─ 🗄️ 資料庫相關
│   ├─ init/
│   │   ├─ outfit_db_with_data.sql    # 完整資料備份 ⭐ 新組員用這個!
│   │   ├─ outfit_db.sql              # 資料庫結構定義 (不含資料)
│   │   └─ README.md                  # 檔案使用說明 ⭐
│   └─ docker-compose.yml             # MySQL Docker 配置
│
├─ 🔧 開發工具腳本
│   ├─ scripts/
│   │   ├─ generate_users_with_bcrypt.py      # 生成測試用戶
│   │   ├─ export_database.sh                 # 匯出資料庫 (開發者用)
│   │   ├─ setup_database_for_teammates.sh    # 一鍵設定 (組員用) ⭐
│   │   └─ crawler_upload_helper.sh           # 爬蟲上傳助手 ⭐
│   └─ pipeline/                               # 資料處理流程
│       ├─ 01_crawl_uniqlo.py                 # UNIQLO 爬蟲
│       ├─ 02_detect_colors.py                # 色彩檢測
│       ├─ 03_gemini_verify.py                # AI 驗證
│       ├─ 04_data_processing.py              # 資料處理
│       └─ 05_database_import.py              # 匯入資料庫
│
├─ 📊 資料集
│   └─ dataset/
│       ├─ styles.csv                 # 時尚資料集 (44,407 筆)
│       ├─ items_fashion_small_clean.csv  # 清理後小型資料集
│       └─ items_malefashion.csv      # 男裝資料
│
└─ 📖 文檔 (詳細說明)
    └─ docs/
        ├─ DATABASE_GUIDE.md          # 資料庫完整指南 ⭐
        ├─ CRAWLER_GUIDE.md           # 爬蟲開發指南 ⭐
        ├─ TEAM_GUIDE.md              # 團隊協作指南 ⭐
        ├─ TEST_ACCOUNTS.md           # 測試帳號 (不會上傳)
        └─ USER_GENERATION_REPORT.md  # 用戶生成報告
```

---

## 🚀 快速開始

### 1️⃣ 首次設定 (新組員必看)

```bash
# 1. Clone 專案
git clone <repository-url>
cd AI-project-crawler-test

# 2. 啟動 Docker 容器 (MySQL)
docker-compose up -d

# 3. 一鍵匯入資料庫 ⭐ 
./scripts/setup_database_for_teammates.sh
```

**就這樣!資料庫已經建立完成 ✅**

### 2️⃣ 驗證安裝

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

### 3️⃣ 連接資料庫 (DBeaver/Workbench)

```
Host:     localhost
Port:     3306
Database: outfit_db
Username: root
Password: rootpassword
```

---

## 🔄 資料庫同步 (重要!)

### ⚠️ 黃金規則:統一檔名!

**所有人都必須匯出到同一個檔名:**
```
init/outfit_db_with_data.sql  ← 唯一的真相來源
```

**❌ 禁止做法:**
```bash
# ❌ 不要自創檔名!
init/outfit_db_20251126.sql
init/outfit_db_john.sql
init/outfit_db_final.sql
init/outfit_db_really_final_v3.sql  😱
```

**為什麼?**
- ✅ Git 會自動追蹤檔案變更歷史
- ✅ 組員永遠知道「最新版本」是哪個
- ✅ 不會有 10 個不同檔名造成混亂
- ✅ 腳本和文檔都指向同一個檔案

**查看歷史版本:**
```bash
# Git 保留所有版本歷史
git log init/outfit_db_with_data.sql
git show <commit-hash>:init/outfit_db_with_data.sql
```

---

### 📤 開發者:如何上傳資料

當你新增/修改資料後,需要讓其他人同步:

#### 方式 A: 一鍵腳本 (推薦)

```bash
# 執行互動式上傳助手
./scripts/export_database.sh

# 按照提示操作:
# 1. 匯出資料庫
# 2. 檢查檔案
# 3. Git commit & push
# 4. 通知組員
```

#### 方式 B: 手動操作

```bash
# 1. 匯出資料庫
docker exec outfit-mysql mysqldump \
  -uroot -prootpassword \
  --databases outfit_db \
  --single-transaction \
  --default-character-set=utf8mb4 \
  > init/outfit_db_with_data.sql

# 2. 提交到 Git
git add init/outfit_db_with_data.sql
git commit -m "更新資料庫:新增 XX 筆資料"
git push

# 3. 通知組員
# 「資料庫已更新,請執行 git pull 並重新匯入」
```

---

### 📥 組員:如何下載最新資料

當有人通知「資料庫已更新」時:

```bash
# 1. 下載最新版本
git pull

# 2. 重新匯入資料庫
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

# 3. 驗證 (確認數量正確)
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "SELECT COUNT(*) FROM items;"
```

---

### 🕷️ 爬蟲組專屬:上傳爬取的資料

爬蟲組每次爬完資料後,**必須**執行:

#### 使用自動化腳本 (推薦)

```bash
./scripts/crawler_upload_helper.sh
```

**腳本會自動幫你:**
1. ✅ 顯示目前資料量
2. ✅ 匯出資料庫
3. ✅ 驗證檔案完整性
4. ✅ Git commit (會提示你輸入訊息)
5. ✅ 推送到 GitHub
6. ✅ 生成通知訊息給組員

#### 記住口訣 🎯

```
爬完 → 匯出 → Commit → Push → 通知
```

**為什麼重要?**
- ❌ 不匯出 = 資料只在你電腦,其他人看不到
- ❌ 只上傳 CSV = 別人還要手動匯入,容易出錯
- ✅ 匯出 SQL = 其他人一鍵就能同步資料

詳細說明: [爬蟲組上傳指南](docs/CRAWLER_GUIDE.md)

---

## 💻 開發須知

### 資料庫重要觀念

```
📄 SQL 檔案 (.sql)              💾 MySQL 資料庫 (Docker 容器)
───────────────────            ──────────────────────────────
• 文字檔案                      • 運行中的服務
• 可以用記事本打開               • 儲存實際資料
• Git 可以同步 ✅                • Git 無法同步 ❌
• 類比:食譜                     • 類比:做好的菜

重點:資料存在「右邊」,所以要匯出成「左邊」才能用 Git 分享!
```

詳細圖解: [資料庫原理說明](docs/DATABASE_GUIDE.md)

---

### 資料庫結構

#### users 表 (用戶資料)

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | INT | 主鍵 |
| username | VARCHAR(100) | 用戶名 (唯一) |
| email | VARCHAR(255) | 電子郵件 |
| password_hash | VARCHAR(255) | bcrypt 加密密碼 |
| favorite_style | VARCHAR(50) | 喜好風格 |
| created_at | TIMESTAMP | 註冊時間 |

#### items 表 (商品資料)

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | INT | 主鍵 |
| item_id | VARCHAR(50) | 商品編號 |
| item_name | VARCHAR(255) | 商品名稱 |
| gender | VARCHAR(10) | 性別 |
| category | VARCHAR(50) | 類別 |
| color | VARCHAR(50) | 顏色 |
| season | VARCHAR(20) | 季節 |
| source | VARCHAR(50) | 資料來源 |
| image_url | TEXT | 圖片網址 |

---

### 密碼加密說明

✅ 使用 **bcrypt** 加密,業界標準安全演算法

**後端登入驗證範例:**

```python
import bcrypt
import pymysql

# 驗證用戶登入
def verify_login(username, password):
    conn = pymysql.connect(
        host='localhost', port=3306,
        user='root', password='rootpassword',
        database='outfit_db', charset='utf8mb4'
    )
    cursor = conn.cursor()
    
    # 查詢用戶
    cursor.execute(
        "SELECT password_hash FROM users WHERE username = %s",
        (username,)
    )
    result = cursor.fetchone()
    
    if result:
        password_hash = result[0]
        # bcrypt 驗證
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            password_hash.encode('utf-8')
        )
    return False
```

詳細實作: [用戶生成報告](docs/USER_GENERATION_REPORT.md)

---

## 🔑 測試帳號

### 主要測試帳號

| 用戶名 | 密碼 | 用途 |
|--------|------|------|
| **admin** | `admin123` | 管理員測試 |
| **demo** | `demo123` | 展示用帳號 |
| **test** | `test123` | 一般測試 |

### 其他帳號

- 📋 另有 47 個虛擬用戶 (fashion_lover, style_icon, trendy_guy...)
- 🔐 統一密碼: `password123`

**完整列表:** `docs/TEST_ACCOUNTS.md` (⚠️ 此檔案不會上傳到 GitHub)

---

## 👥 團隊協作

### Git 分支策略

```
main (穩定版本)
  ↓
develop (開發分支) ← 日常在這裡工作
  ↓
feature/* (功能分支) ← 開發新功能時使用
```

**詳細說明:** [Git 工作流程指南](GIT_GUIDE.md) ⭐

---

### 分工流程

```
🕷️ 爬蟲組                → 爬取資料 → 執行 crawler_upload_helper.sh → 通知組員
🎨 前端組                → git pull → 重新匯入資料庫 → 開發 UI
⚙️ 後端組                → git pull → 重新匯入資料庫 → 開發 API
🤖 AI/色彩分析組         → git pull → 重新匯入資料庫 → 開發演算法
```

### 常用指令參考

```bash
# ===== 日常開發 =====

# 1. 開始工作前
git pull                          # 同步最新程式碼
docker-compose up -d              # 啟動 MySQL

# 2. 檢查資料庫
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "SELECT COUNT(*) FROM items;"

# 3. 如果資料庫有更新
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

# ===== 爬蟲組專用 =====

# 爬完資料後執行
./scripts/crawler_upload_helper.sh

# ===== 前端組 =====

# 啟動 Flask 應用
cd app
python3 app.py
# 訪問 http://localhost:5000

# ===== 測試 =====

# 測試登入 API
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## ⚠️ 常見問題

### Q1: 為什麼我的資料其他人看不到?

**A:** 因為 Git 只同步「檔案」,不同步「資料庫實例」

**解決方法:**
1. 匯出資料庫: `./scripts/export_database.sh`
2. Git commit & push
3. 通知組員重新匯入

---

### Q2: init/ 資料夾有兩個 SQL 檔案,我該用哪個?

**A:** 
- ⭐ **`outfit_db_with_data.sql`** - 新組員用這個!(包含所有資料)
- 📋 **`outfit_db.sql`** - 只有結構定義,沒有資料(用來查看表格設計)

**詳細說明:** [init/README.md](init/README.md)

**常見錯誤:**
```bash
# ❌ 錯誤:匯入 outfit_db.sql
docker exec -i outfit-mysql mysql -uroot -prootpassword < init/outfit_db.sql
# 結果:資料庫是空的!

# ✅ 正確:匯入 outfit_db_with_data.sql
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql
# 結果:50 個用戶 + 49,707 筆商品 ✅
```

---

### Q3: outfit_db_with_data.sql 是什麼?

**A:** 完整的資料庫備份檔案,包含:
- ✅ 表格結構 (CREATE TABLE)
- ✅ 所有資料 (INSERT INTO)
- ✅ 50 個用戶 + 49,707 筆商品

組員只要匯入這個檔案,就能獲得**完全相同**的資料庫!

---

### Q4: 檔案太大怎麼辦?

**A:** 目前 8.2 MB,還可以接受

如果超過 100 MB:
- 📦 壓縮: `gzip init/outfit_db_with_data.sql`
- ☁️ 改用雲端分享 (Google Drive/OneDrive)
- 📋 只匯出必要的表格

---

### Q5: 我不小心刪除了資料怎麼辦?

**A:** 重新匯入即可恢復:

```bash
# 清空資料庫
docker exec outfit-mysql mysql -uroot -prootpassword -e "
DROP DATABASE IF EXISTS outfit_db;
CREATE DATABASE outfit_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
"

# 重新匯入
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql
```

---

### Q6: 爬蟲組忘記上傳資料怎麼辦?

**A:** 如果發現其他人沒有你的資料:

1. 確認資料在你的資料庫: `SELECT COUNT(*) FROM items;`
2. 執行上傳腳本: `./scripts/crawler_upload_helper.sh`
3. 通知組員: 「我剛上傳了 XX 筆新資料,請重新匯入」

---

## 📚 詳細文檔

如需更深入了解,請參考以下文檔:

### 🚀 快速上手
- [QUICK_START.md](QUICK_START.md) - 5 分鐘快速開始指南 ⭐ **新人必看!**

### 📖 完整指南
| 文檔 | 說明 | 適合對象 |
|------|------|---------|
| [GIT_GUIDE.md](GIT_GUIDE.md) | Git 版本控制完整指南 ⭐ | 所有人必讀! |
| [DATABASE_GUIDE.md](docs/DATABASE_GUIDE.md) | 資料庫管理完整指南 ⭐ | 所有人必讀! |
| [CRAWLER_GUIDE.md](docs/CRAWLER_GUIDE.md) | 爬蟲開發完整指南 | 爬蟲組 ⭐ |
| [TEAM_GUIDE.md](docs/TEAM_GUIDE.md) | 團隊協作完整指南 | 所有人 |

### 📋 參考資料
| 文檔 | 說明 |
|------|------|
| [TEST_ACCOUNTS.md](docs/TEST_ACCOUNTS.md) | 完整測試帳號列表 |
| [USER_GENERATION_REPORT.md](docs/USER_GENERATION_REPORT.md) | 用戶生成與登入實作 |
| [TECHNICAL_SETUP.md](docs/TECHNICAL_SETUP.md) | 技術規格與環境設定 (進階) |
| [PIPELINE_OVERVIEW.md](PIPELINE_OVERVIEW.md) | 爬蟲 Pipeline 概覽 |
| [SPEC_GUIDE.md](SPEC_GUIDE.md) | 專案規格說明 |

---

## ✅ 檢查清單

### 新組員加入時

- [ ] Clone 專案
- [ ] 安裝 Docker Desktop
- [ ] 執行 `docker-compose up -d`
- [ ] 執行 `./scripts/setup_database_for_teammates.sh`
- [ ] 驗證資料: `SELECT COUNT(*) FROM users;` 應為 50
- [ ] 測試登入: admin / admin123

### 爬蟲組每次爬完資料

- [ ] 檢查資料已匯入資料庫
- [ ] 執行 `./scripts/crawler_upload_helper.sh`
- [ ] 確認 Git push 成功
- [ ] 通知組員 (Line/Discord/Slack)

### 前端/後端組收到更新通知

- [ ] `git pull`
- [ ] 重新匯入: `docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql`
- [ ] 驗證資料量是否正確
- [ ] 繼續開發

---

## 🎯 快速連結

- 🐳 **啟動資料庫:** `docker-compose up -d`
- 📥 **同步資料:** `./scripts/setup_database_for_teammates.sh`
- 📤 **上傳資料:** `./scripts/crawler_upload_helper.sh`
- 🔍 **查看資料:** DBeaver 連接 `localhost:3306/outfit_db`
- 🧪 **測試帳號:** admin / admin123

---

## 📞 需要幫助?

如果遇到問題:
1. 📖 先查看 [常見問題](#常見問題)
2. 📚 閱讀 `docs/` 相關文檔
3. 💬 詢問組員或助教

---

## 📝 更新紀錄

- **2025-11-26** - 建立完整的資料庫共享機制
  - 新增 50 個測試用戶 (bcrypt 加密)
  - 匯入 49,707 筆商品資料
  - 建立自動化上傳/下載腳本
  - 完成所有文檔

---

**專案成員:** liaoyiting  
**資料庫版本:** outfit_db v1.0  
**最後更新:** 2025-11-26

🎉 **祝開發順利!**
