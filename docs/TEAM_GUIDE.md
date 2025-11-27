# 🤝 團隊協作完整指南

> **統整文檔**: 包含環境設定、協作流程、開發規範等所有團隊相關內容  
> **更新日期**: 2025年11月26日

---

## 📖 目錄

1. [專案資訊](#專案資訊)
2. [環境設定](#環境設定)
3. [開發流程](#開發流程)
4. [協作規範](#協作規範)
5. [測試帳號](#測試帳號)

---

## 📌 專案資訊

### 基本資訊

- **專案名稱**: AI 穿搭推薦網站
- **Repository**: https://github.com/memory9802/AI-project
- **當前分支**: `develop` (所有人都在這裡開發)
- **技術棧**: Python Flask + MySQL + Docker + Google Gemini API

### 核心功能

1. ✅ AI 聊天機器人 (Google Gemini)
2. ✅ 資料庫穿搭推薦系統
3. ✅ 用戶衣櫃管理
4. ✅ 對話記憶功能
5. ✅ 50 個測試用戶 + 49,707 個商品

### 專案結構

```
AI-project-crawler-test/
├── app/                      # Flask 應用
│   ├── app.py               # 主程式
│   ├── requirements.txt     # Python 依賴
│   ├── static/              # 前端靜態檔案
│   │   ├── *.html          # HTML 頁面
│   │   ├── *.css           # 樣式
│   │   └── *.js            # JavaScript
│   └── templates/           # Jinja2 模板
│
├── pipeline/                # 爬蟲流程
│   ├── 01_crawl_uniqlo.py
│   ├── 02_detect_colors.py
│   ├── 03_gemini_verify.py
│   ├── 04_data_processing.py
│   └── 05_database_import.py
│
├── init/                    # 資料庫初始化
│   ├── outfit_db.sql       # 結構定義
│   └── uniqlo_175_colored.csv
│
├── scripts/                 # 自動化腳本
│   ├── export_database.sh
│   ├── crawler_upload_helper.sh
│   └── check_database.py
│
├── docs/                    # 文檔
│   ├── DATABASE_GUIDE.md
│   ├── CRAWLER_GUIDE.md
│   ├── TEAM_GUIDE.md (本文)
│   └── TEST_ACCOUNTS.md
│
├── docker-compose.yml       # Docker 配置
├── GIT_GUIDE.md            # Git 指南
├── QUICK_START.md          # 快速開始
└── README.md               # 專案說明
```

---

## ⚙️ 環境設定

### 前置需求

| 軟體 | 版本 | 用途 | 安裝方式 |
|------|------|------|----------|
| **Docker Desktop** | 最新版 | 容器管理 | [官網下載](https://www.docker.com/products/docker-desktop) |
| **Git** | 2.0+ | 版本控制 | macOS:`brew install git` / Windows: [官網](https://git-scm.com/) |
| **Python** | 3.12+ | 開發語言 | macOS:`brew install python@3.12` |
| **VS Code** | 最新版 | 編輯器 (推薦) | [官網下載](https://code.visualstudio.com/) |

### macOS 完整設定

```bash
# 1. 安裝 Homebrew (如果還沒有)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 安裝必要軟體
brew install git python@3.12 docker

# 3. 克隆專案
git clone https://github.com/memory9802/AI-project.git
cd AI-project

# 4. 切換到 develop 分支
git checkout develop
git pull origin develop

# 5. 啟動 Docker Desktop
open -a Docker

# 6. 等待 Docker 啟動 (查看 Docker 圖示)

# 7. 啟動容器
docker-compose up -d

# 8. 匯入資料庫
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db.sql

# 9. 設定 Python 環境 (可選)
python3.12 -m venv venv
source venv/bin/activate
pip install -r app/requirements.txt

# 10. 測試
python3 app/app.py
# 或
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "SELECT COUNT(*) FROM items;"
```

### Windows 完整設定

```powershell
# 1. 安裝 Chocolatey (以管理員身份執行 PowerShell)
Set-ExecutionPolicy Bypass -Scope Process -Force; 
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; 
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 2. 安裝必要軟體
choco install git python312 docker-desktop

# 3. 重啟電腦 (重要!)
# Restart-Computer

# 4. 克隆專案
git clone https://github.com/memory9802/AI-project.git
cd AI-project

# 5. 切換分支
git checkout develop
git pull origin develop

# 6. 啟動 Docker Desktop (等待啟動完成)

# 7. 啟動容器
docker-compose up -d

# 8. 匯入資料庫
Get-Content init\outfit_db.sql | docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db

# 9. 設定 Python 環境 (可選)
python -m venv venv
.\venv\Scripts\Activate
pip install -r app\requirements.txt

# 10. 測試
python app\app.py
```

### 驗證環境

```bash
# 1. 檢查 Docker 版本
docker --version
docker-compose --version

# 2. 檢查容器運行狀態
docker ps
# 應該看到: outfit-mysql (Up)

# 3. 檢查 Python 版本
python3 --version
# 應該 >= 3.12

# 4. 檢查 Git 設定
git config --global user.name
git config --global user.email

# 5. 測試資料庫連接
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "SELECT COUNT(*) FROM items;"
# 應該顯示數字 (例如: 49707)
```

---

## 🔄 開發流程

### 每日工作流程

```bash
# ☀️ 早上開始工作

# 1. 啟動 Docker
docker-compose up -d

# 2. 獲取最新代碼
git checkout develop
git pull origin develop

# 3. 同步資料庫 (如果有更新)
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

# 4. 啟動開發伺服器
python3 app/app.py
# 訪問 http://localhost:5000

# 5. 開發... 💻

# 🌙 下班前提交

# 6. 查看修改
git status
git diff

# 7. 提交代碼
git add .
git commit -m "feat: 新增用戶個人資料頁面"
git push origin develop

# 8. 如果有修改資料庫
./scripts/export_database.sh
git add init/outfit_db_with_data.sql
git commit -m "更新資料庫: 新增測試資料"
git push origin develop

# 9. 通知組員 (在群組)
```

### 功能開發流程

```bash
# 1. 確保在最新的 develop
git checkout develop
git pull origin develop

# 2. 創建功能分支 (可選但推薦)
git checkout -b feature_user_profile

# 3. 開發功能
# 編輯檔案...

# 4. 測試功能
python3 app/app.py
# 測試 http://localhost:5000/profile

# 5. 提交到功能分支
git add .
git commit -m "feat: 完成用戶個人資料頁面"

# 6. 合併回 develop
git checkout develop
git pull origin develop
git merge feature_user_profile

# 7. 解決衝突 (如果有)
# 編輯衝突檔案...
git add .
git commit -m "merge: 合併用戶個人資料功能"

# 8. 推送
git push origin develop

# 9. 刪除功能分支 (可選)
git branch -d feature_user_profile
```

---

## 📋 協作規範

### Git Commit 規範

**格式:**
```
<type>: <subject>

<body>
```

**Type 類型:**
- `feat`: 新功能
- `fix`: 修復 bug
- `docs`: 文檔更新
- `style`: 代碼格式調整
- `refactor`: 代碼重構
- `test`: 測試相關
- `chore`: 其他修改

**範例:**
```bash
# 簡短版本
git commit -m "feat: 新增用戶登入功能"
git commit -m "fix: 修復資料庫連接錯誤"
git commit -m "docs: 更新 README"

# 詳細版本
git commit -m "feat: 新增用戶登入功能

- 實作 /api/login API
- 新增 bcrypt 密碼驗證
- 新增 session 管理
- 更新前端登入表單
測試: 已通過所有 50 個測試帳號的登入測試
"
```

### 分支命名規範

```bash
# ✅ 正確 (小寫 + 底線)
feature_user_login
bugfix_database_error
hotfix_api_timeout

# ❌ 錯誤
Feature-User-Login    # 不要大寫
feature/user/login    # 不要用 /
feature&user&login    # 不要特殊符號
```

### 代碼審查原則

**合併前檢查:**
- [ ] 代碼可以正常運行
- [ ] 沒有明顯的 bug
- [ ] 遵循專案的代碼風格
- [ ] 有適當的註解
- [ ] Commit message 清楚

**審查重點:**
1. **功能正確性** - 是否達成目標
2. **代碼品質** - 是否易讀易維護
3. **效能考量** - 是否有明顯瓶頸
4. **安全性** - 是否有安全漏洞

### 衝突解決原則

**一般規則:**
1. **功能代碼** - 兩邊都保留,合併功能
2. **配置檔案** - 保留較新的版本
3. **資料庫** - 不要手動編輯 SQL,參考 `docs/DATABASE_GUIDE.md`
4. **文檔** - 合併內容

**解決步驟:**
```bash
# 1. 拉取最新代碼
git pull origin develop
# CONFLICT...

# 2. 查看衝突檔案
git status

# 3. 打開衝突檔案
# 會看到:
<<<<<<< HEAD
你的代碼
=======
遠端的代碼
>>>>>>> origin/develop

# 4. 手動編輯,保留需要的代碼

# 5. 標記為已解決
git add <file>

# 6. 完成合併
git commit -m "解決衝突: 合併XXX功能"
git push origin develop
```

### 溝通規範

**每日同步 (推薦):**
- 早上: 說明今天要做什麼
- 晚上: 說明今天做了什麼,遇到什麼問題

**重要通知:**
- 📢 資料庫更新 - 必須立即通知
- 🔧 重大代碼變更 - 提前通知
- 🐛 發現嚴重 bug - 立即通知
- ✅ 完成重要功能 - 通知測試

**通知範本:**

```
# 資料庫更新通知
📢 資料庫已更新

更新內容: 新增 500 個商品
更新人: @你的名字
請執行:
1. git pull origin develop
2. docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

# 功能完成通知
✅ 功能完成: 用戶登入

完成內容:
- 前端登入表單
- 後端 API
- 密碼驗證
測試: http://localhost:5000/login
測試帳號: admin / admin123

# Bug 通知
🐛 發現 Bug

問題: 資料庫連接偶爾失敗
影響: 可能導致頁面載入錯誤
狀態: 正在修復中
預計: 今天下班前解決
```

---

## 👥 測試帳號

### 快速測試帳號

| 用戶名 | 密碼 | 用途 |
|--------|------|------|
| admin | admin123 | 管理員測試 |
| demo | demo123 | 展示用 |
| test | test123 | 一般測試 |

### 完整測試帳號列表

**總計 50 個測試用戶**

詳細列表請參考: `docs/TEST_ACCOUNTS.md`

所有虛擬用戶的統一密碼: `password123`

### 測試資料統計

```sql
-- 用戶數量
SELECT COUNT(*) FROM users;
-- 50

-- 商品數量
SELECT COUNT(*) FROM items;
-- 49,707

-- 穿搭數量
SELECT COUNT(*) FROM outfits;
-- 3

-- 各類別商品數量
SELECT category, COUNT(*) as count 
FROM items 
GROUP BY category;
```

---

## 🆘 常見問題

### Q1: Docker 容器啟動失敗?

**檢查:**
```bash
# 1. 查看 Docker Desktop 是否運行
docker --version

# 2. 查看錯誤訊息
docker-compose up

# 3. 清理並重新啟動
docker-compose down
docker-compose up -d
```

---

### Q2: 資料庫連接失敗?

**檢查:**
```bash
# 1. 容器是否運行
docker ps | grep outfit-mysql

# 2. 測試連接
docker exec outfit-mysql mysql -uroot -prootpassword -e "SELECT 1;"

# 3. 查看日誌
docker logs outfit-mysql
```

---

### Q3: Git push 被拒絕?

**原因:** 遠端有新的 commit

**解決:**
```bash
# 1. 先 pull
git pull origin develop

# 2. 解決衝突 (如果有)

# 3. 再 push
git push origin develop
```

---

### Q4: Python 模組找不到?

**解決:**
```bash
# 1. 確認虛擬環境
source venv/bin/activate  # macOS
# venv\Scripts\Activate    # Windows

# 2. 重新安裝依賴
pip install -r app/requirements.txt

# 3. 檢查已安裝
pip list
```

---

### Q5: 前端頁面無法訪問?

**檢查:**
```bash
# 1. Flask 是否運行
ps aux | grep python

# 2. 端口是否被佔用
lsof -i :5000  # macOS
# netstat -ano | findstr :5000  # Windows

# 3. 查看 Flask 日誌
# 在終端查看輸出
```

---

## 📊 開發進度追蹤

### 功能清單

- [x] ✅ 資料庫結構設計
- [x] ✅ 50 個測試用戶生成
- [x] ✅ 爬蟲 pipeline 建立
- [x] ✅ 商品資料收集 (49,707 個)
- [x] ✅ 前端基礎頁面
- [ ] ⏳ 用戶登入功能
- [ ] ⏳ AI 聊天功能
- [ ] ⏳ 穿搭推薦演算法
- [ ] ⏳ 用戶衣櫃管理
- [ ] ⏳ 評分系統

### 剩餘時間

**專題截止日期:** (根據實際情況填寫)  
**剩餘天數:** 15 天 (截至 2025-11-26)

---

## 🎯 最佳實踐

### ✅ 推薦做法

1. **每天同步** - 開始工作前 pull,結束時 push
2. **小步提交** - 完成小功能就提交
3. **清楚註解** - 複雜邏輯加註解
4. **測試後推送** - 確保代碼可運行
5. **主動溝通** - 有問題立即詢問

### ❌ 避免做法

1. ❌ 累積大量修改才提交
2. ❌ 直接修改 main 分支
3. ❌ 忽略衝突強制推送
4. ❌ 不測試就提交
5. ❌ 獨自解決問題太久

---

## 🔗 相關文檔

- **快速開始**: 參考主目錄 `QUICK_START.md`
- **Git 指南**: 參考主目錄 `GIT_GUIDE.md`
- **資料庫指南**: 參考 `docs/DATABASE_GUIDE.md`
- **爬蟲指南**: 參考 `docs/CRAWLER_GUIDE.md`
- **測試帳號**: 參考 `docs/TEST_ACCOUNTS.md`

---

**更新日期:** 2025年11月26日  
**維護人:** liaoyiting

