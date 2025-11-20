# 🚀 團隊協作指南 - 穿搭推薦 AI 專案

> **適用對象**: 需要設定環境、合併分支、解決衝突的組員  
> **閱讀時間**: 15-20 分鐘  
> **更新日期**: 2025-01-19

---

## 🎯 使用指南

### 📖 閱讀順序
1. **新組員**: 先看 [README.md](README.md) 快速了解專案
2. **要設定環境**: 繼續看本文的 [環境設定](#環境設定) 章節
3. **要合併代碼**: 直接跳到 [分支合併指南](#分支合併指南)
4. **遇到問題**: 查看 [常見問題](#常見問題) 或 [README.md](README.md)

---

## 📋 目錄
1. [專案概述](#專案概述)
2. [技術架構](#技術架構)
3. [環境設定](#環境設定)
4. [重要修改記錄](#重要修改記錄)
5. [跨平台注意事項](#跨平台注意事項)
6. [分支合併指南](#分支合併指南)
7. [常見問題](#常見問題)

---

## 📌 專案概述

### 專案資訊
- **名稱**: 穿搭推薦 AI 網站
- **描述**: 使用 AI 提供個性化穿搭建議,支援對話式互動
- **技術棧**: Python Flask + MySQL + Docker + Google Gemini API
- **當前分支**: `Jinja`
- **部署方式**: Docker Compose

### 核心功能
1. ✅ AI 聊天機器人 (Google Gemini 2.0 Flash Lite)
2. ✅ 資料庫穿搭推薦系統
3. ✅ 用戶衣櫃管理
4. ✅ 對話記憶功能
5. ✅ 多 AI 模型備援 (Gemini/Groq/DeepSeek)

---

## 🏗️ 技術架構

### 系統架構圖
```
┌─────────────────────────────────────────────────────────┐
│                    使用者瀏覽器                          │
│              http://localhost:5001                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Flask Web Server (port 5001)                │
│  - 路由: /recommend, /items, /recommend_page            │
│  - 模板引擎: Jinja2                                      │
│  - JSON API + HTML 頁面                                  │
└────────────┬───────────────────────┬────────────────────┘
             │                       │
             ▼                       ▼
┌────────────────────────┐  ┌──────────────────────────┐
│  LangChain AI Agent    │  │   MySQL 8.0 Database     │
│  - Gemini 2.0 Lite     │  │   - outfit_db            │
│  - 速率限制: 2 秒      │  │   - 11 張資料表          │
│  - Token 優化          │  │   - UTF-8mb4 編碼        │
└────────────────────────┘  └──────────────────────────┘
```

### 資料庫結構 (11 張表)
```sql
1. outfits          -- 穿搭組合 (3 筆測試資料)
2. items            -- 單品項目 (9 筆測試資料)
3. outfit_items     -- 穿搭與單品關聯
4. users            -- 用戶資料 (4 筆測試用戶)
5. user_wardrobe    -- 用戶衣櫃
6. outfit_ratings   -- 穿搭評分
7. partner_products -- 合作商品
8. user_preferences -- 用戶偏好
9. user_body_info   -- 用戶體型資料
10. conversation_history -- 對話記錄
11. sessions        -- 對話 session
```

### Docker 容器架構
```yaml
services:
  mysql:        # 資料庫服務 (port 3306)
  flask:        # Python 後端 (port 5001)
  phpmyadmin:   # 資料庫管理介面 (port 8080)
```

---

## 🛠️ 環境設定

### 前置需求
| 軟體 | Windows | macOS | 用途 |
|------|---------|-------|------|
| Docker Desktop | ✅ 必須 | ✅ 必須 | 容器化部署 |
| Git | ✅ 必須 | ✅ 必須 | 版本控制 |
| 文字編輯器 | VS Code 推薦 | VS Code 推薦 | 開發工具 |

### 快速啟動步驟

#### Step 1: 克隆專案
```bash
# Windows (PowerShell 或 Git Bash)
git clone https://github.com/memory9802/AI-project.git
cd AI-project
git checkout Jinja

# macOS (Terminal)
git clone https://github.com/memory9802/AI-project.git
cd AI-project
git checkout Jinja
```

#### Step 2: 配置環境變數
```bash
# 複製範例檔案
# Windows (PowerShell)
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

編輯 `.env` 檔案:
```properties
# AI API Keys (必須設定)
LLM_API_KEY=AIzaSyAaDSYKxfoq_4nVKaN9_2PE8R4lmhWYMfQ  # 團隊共用
GROQ_API_KEY=                                        # 可選
DEEPSEEK_API_KEY=                                    # 可選

# Google Generative AI API 設定
GOOGLE_GENAI_API_VERSION=v1

# Database Configuration (Docker 模式 - 不要改)
DB_HOST=mysql          # 容器內部使用服務名稱
DB_PORT=3306
DB_USER=root
DB_PASS=rootpassword
DB_NAME=outfit_db
```

#### Step 3: 啟動服務
```bash
# Windows (PowerShell)
docker compose up -d --build

# macOS
docker compose up -d --build

# 等待 10-15 秒讓容器完全啟動
```

#### Step 4: 驗證運行
```bash
# 檢查容器狀態
docker compose ps

# 應該看到 3 個容器都是 "Up" 狀態:
# - outfit-mysql
# - outfit-flask
# - outfit-phpmyadmin
```

#### Step 5: 測試功能
```bash
# 測試 API 健康檢查
# Windows (PowerShell)
Invoke-WebRequest -Uri http://localhost:5001/ping | Select-Object -ExpandProperty Content

# macOS / Linux
curl http://localhost:5001/ping

# 預期輸出:
# {"ai_enabled":true,"db_host":"mysql","gemini_model":"gemini-2.0-flash-lite","status":"ok"}
```

```bash
# 測試 AI 聊天功能
# Windows (PowerShell)
$body = @{
    message = "推薦約會穿搭"
    user_id = 1
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:5001/recommend -Method Post -Body $body -ContentType "application/json"

# macOS / Linux
curl -X POST http://localhost:5001/recommend \
  -H "Content-Type: application/json" \
  -d '{"message":"推薦約會穿搭","user_id":1}'
```

### 存取服務
| 服務 | URL | 說明 |
|------|-----|------|
| 網站主頁 | http://localhost:5001 | 前端網頁 |
| API 端點 | http://localhost:5001/recommend | AI 推薦 API |
| phpMyAdmin | http://localhost:8080 | 資料庫管理 (帳號: root / rootpassword) |

---

## 📝 重要修改記錄

### 🔧 已修復的問題
1. ✅ **資料庫亂碼** → UTF-8mb4 編碼配置
2. ✅ **AI 服務無法使用** → API 配額優化
3. ✅ **Rate Limit 錯誤** → 速率限制實施
4. ✅ **模型不相容** → 切換到 gemini-2.0-flash-lite

### 🎯 核心修改檔案清單

#### 1. `langchain_agent.py` (AI 核心邏輯)
**修改原因**: API 配額優化、速率限制、模型切換

```python
# 🔴 關鍵修改:
MIN_REQUEST_INTERVAL = 2  # 速率限制: 每次請求間隔 2 秒

model="gemini-2.0-flash-lite"  # 模型從 2.0-flash 改為 lite
temperature=0.5                # 從 0.7 降到 0.5
max_output_tokens=300          # 從 500 降到 300

# 簡化的 system_prompt (從 ~1000 tokens 降到 ~200)
```

**功能說明**:
- 多模型備援 (Gemini → Groq → DeepSeek)
- 對話記憶管理 (每個用戶獨立 session)
- 速率限制防止 Rate Limit

#### 2. `app.py` (Flask 主程式)
**修改原因**: 資料庫編碼、模型設定

```python
# 🔴 關鍵修改:
GEMINI_MODEL = "gemini-2.0-flash-lite"  # 模型更新

app.config['JSON_AS_ASCII'] = False  # 支援中文 JSON

# 資料庫連線加入 charset
pymysql.connect(
    charset='utf8mb4',
    use_unicode=True
)
```

**路由清單**:
- `POST /recommend` - AI 推薦端點
- `GET /items` - 獲取單品資料
- `POST /clear_session` - 清除對話記憶
- `GET /ping` - 健康檢查

#### 3. `docker-compose.yml` (容器編排)
**修改原因**: UTF-8 編碼、端口映射

```yaml
# 🔴 關鍵修改:
mysql:
  command:
    - --character-set-server=utf8mb4      # UTF-8 編碼
    - --collation-server=utf8mb4_unicode_ci
  environment:
    MYSQL_CHARSET: utf8mb4

flask:
  ports:
    - "5001:5000"  # ⚠️ 外部端口是 5001,不是 5000
```

#### 4. `.env` (環境變數)
**修改原因**: Docker 模式配置、API 設定

```properties
# 🔴 關鍵修改:
LLM_API_KEY=AIzaSyAaDSYKxfoq_4nVKaN9_2PE8R4lmhWYMfQ  # 新 API key
DB_HOST=mysql  # Docker 模式使用服務名稱(不是 localhost)
GOOGLE_GENAI_API_VERSION=v1  # 強制使用 v1 API
```

#### 5. `init/init.sql` (資料庫初始化)
**修改原因**: 統一資料庫結構、新增測試資料

```sql
-- 🔴 關鍵修改:
CREATE DATABASE outfit_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 11 張表的完整結構
-- 3 組穿搭測試資料
-- 9 個單品測試資料
-- 4 個測試用戶
```

### 🗑️ 已刪除的衝突檔案
- ❌ `init/outfit_db.sql` (與 init.sql 重複,已刪除)

---

## 🖥️ 跨平台注意事項

### Docker 指令差異

| 操作 | Windows (PowerShell) | macOS / Linux |
|------|---------------------|---------------|
| 啟動容器 | `docker compose up -d` | `docker compose up -d` |
| 停止容器 | `docker compose down` | `docker compose down` |
| 查看日誌 | `docker compose logs -f flask` | `docker compose logs -f flask` |
| 重建容器 | `docker compose up -d --build` | `docker compose up -d --build` |

### 路徑表示法差異

```bash
# Windows (PowerShell)
C:\Users\YourName\Desktop\AI-project\app.py

# macOS / Linux
/Users/YourName/Desktop/AI-project/app.py

# ⚠️ 注意: 
# - Windows 使用反斜線 \
# - macOS/Linux 使用正斜線 /
# - Docker 內部統一使用 /
```

### 行尾符號 (Line Endings)

**問題**: Windows 使用 CRLF (`\r\n`),macOS/Linux 使用 LF (`\n`)

**解決方案**: Git 自動轉換
```bash
# 在 .gitattributes 已設定:
* text=auto
*.py text eol=lf
*.sh text eol=lf
```

### Docker Desktop 設定

#### Windows 注意事項:
1. ✅ 啟用 WSL2 後端 (Settings → General → Use WSL2)
2. ✅ 分配足夠資源 (Settings → Resources)
   - Memory: 最少 4GB
   - CPUs: 最少 2 核心
3. ✅ 檔案共享權限 (Settings → Resources → File Sharing)

#### macOS 注意事項:
1. ✅ Docker Desktop 版本 4.0+
2. ✅ 分配資源 (Preferences → Resources)
   - Memory: 最少 4GB
   - CPUs: 最少 2 核心

---

## 🔀 分支合併指南

### 當前開發狀態
```
main
 └── Jinja (你的分支 - macOS)
      ├── 已修復: 資料庫亂碼
      ├── 已修復: AI Rate Limit
      ├── 已優化: API 配額
      └── 已測試: ✅ 運行正常

組員分支 (假設: feature/xxx - Windows)
 └── 待合併功能
```

### 合併前檢查清單

#### 1️⃣ 環境一致性確認
```bash
# 兩邊都執行,確保使用相同設定
docker compose config | grep -E "(image|environment)" 

# 確認 .env 內容一致
cat .env
```

#### 2️⃣ 資料庫結構同步
```bash
# 匯出你目前的資料庫結構
docker exec outfit-mysql mysqldump -u root -prootpassword --no-data outfit_db > current_schema.sql

# 傳給組員比對
```

#### 3️⃣ API Key 統一
```bash
# 確保使用同一組 API Key
LLM_API_KEY=AIzaSyAaDSYKxfoq_4nVKaN9_2PE8R4lmhWYMfQ
```

### 合併步驟 (建議流程)

#### Step 1: 備份當前狀態
```bash
# 建立備份分支
git checkout -b backup-before-merge
git push origin backup-before-merge
```

#### Step 2: 拉取組員分支
```bash
# 切回 Jinja 分支
git checkout Jinja

# 拉取組員的變更 (假設組員分支是 feature/xxx)
git fetch origin feature/xxx
git merge origin/feature/xxx
```

#### Step 3: 解決衝突

**可能衝突的檔案**:
- `app.py` - 路由定義
- `templates/*.html` - 前端頁面
- `static/*.js` - 前端邏輯
- `init/init.sql` - 資料庫結構

**衝突解決原則**:
```python
# 例如在 app.py
<<<<<<< HEAD (你的版本)
GEMINI_MODEL = "gemini-2.0-flash-lite"
=======
GEMINI_MODEL = "gemini-1.5-flash"  # 組員的版本
>>>>>>> feature/xxx

# 📋 解決方式: 保留你的版本 (已測試過)
GEMINI_MODEL = "gemini-2.0-flash-lite"
```

#### Step 4: 測試合併結果
```bash
# 重建容器
docker compose down
docker compose up -d --build

# 等待啟動
sleep 10

# 測試所有功能
curl http://localhost:5001/ping
curl -X POST http://localhost:5001/recommend -H "Content-Type: application/json" -d '{"message":"測試","user_id":1}'

# 測試組員新增的功能
# ...
```

#### Step 5: 提交合併
```bash
# 確認所有測試通過後
git add .
git commit -m "合併組員功能 + 保留 API 優化"
git push origin Jinja
```

### 合併後驗證清單
- [ ] Docker 容器都能正常啟動
- [ ] 資料庫連線正常,無亂碼
- [ ] AI 聊天功能運作正常
- [ ] 組員新增的功能正常運作
- [ ] 無 Rate Limit 錯誤
- [ ] Windows 和 macOS 都測試過

---

## 🐛 常見問題

### Q1: 容器啟動失敗
```bash
# 檢查 Docker Desktop 是否運行
# Windows: 工作管理員查看 "Docker Desktop"
# macOS: 活動監視器查看 "Docker"

# 清理舊容器
docker compose down -v
docker system prune -f

# 重新啟動
docker compose up -d --build
```

### Q2: 資料庫連線失敗
```bash
# 確認 .env 設定
DB_HOST=mysql  # ⚠️ 必須是 "mysql" 不是 "localhost"

# 檢查 MySQL 容器
docker compose logs mysql

# 手動連線測試
docker exec -it outfit-mysql mysql -u root -prootpassword -e "SHOW DATABASES;"
```

### Q3: AI 回應 "服務無法使用"
```bash
# 檢查 API Key
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_KEY"

# 查看 Flask 日誌
docker compose logs flask | grep -E "(Gemini|error|Rate)"

# 確認模型設定
grep "GEMINI_MODEL" app.py langchain_agent.py
```

### Q4: 端口衝突
```bash
# 檢查端口佔用
# Windows
netstat -ano | findstr :5001
netstat -ano | findstr :3306
netstat -ano | findstr :8080

# macOS
lsof -i :5001
lsof -i :3306
lsof -i :8080

# 修改 docker-compose.yml 端口映射
ports:
  - "5002:5000"  # 改用 5002
```

### Q5: Windows 路徑問題
```bash
# ❌ 錯誤: Windows 路徑格式
DB_PATH=C:\data\outfit_db

# ✅ 正確: 使用正斜線或雙反斜線
DB_PATH=C:/data/outfit_db
# 或
DB_PATH=C:\\data\\outfit_db
```

### Q6: Rate Limit 仍然出現
```python
# 檢查 langchain_agent.py
grep "MIN_REQUEST_INTERVAL" langchain_agent.py
# 應該顯示: MIN_REQUEST_INTERVAL = 2

# 增加間隔時間
MIN_REQUEST_INTERVAL = 3  # 改為 3 秒

# 重啟容器
docker compose restart flask
```

### Q7: 中文亂碼問題
```bash
# 確認 docker-compose.yml MySQL 設定
docker compose exec mysql mysql -u root -prootpassword -e "SHOW VARIABLES LIKE 'char%';"

# 應該全部顯示 utf8mb4
# 如果不是,重建容器:
docker compose down -v
docker compose up -d --build
```

---

## 📚 參考文件

### 專案文件清單
| 檔案名稱 | 用途 | 適用對象 |
|---------|------|---------|
| `README.txt` | 專案簡介 | 所有人 |
| `DEVELOPMENT.md` | 開發指南 | 開發者 |
| `API_OPTIMIZATION.md` | API 優化指南 | 後端開發 |
| `QUOTA_SOLUTION.md` | 配額問題解決方案 | DevOps |
| `PROJECT_SUMMARY.md` | 專案總結報告 | PM/主管 |
| `TEAM_COLLABORATION.md` | 本文件 | 團隊協作 |

### 外部資源
- [Google Gemini API 文件](https://ai.google.dev/docs)
- [Flask 官方文件](https://flask.palletsprojects.com/)
- [Docker Compose 文件](https://docs.docker.com/compose/)
- [LangChain 文件](https://python.langchain.com/)

---

## 🤝 團隊溝通協議

### Git Commit 規範
```bash
# 格式: <type>: <description>

# 範例:
git commit -m "feat: 新增用戶評分功能"
git commit -m "fix: 修復資料庫亂碼問題"
git commit -m "refactor: 優化 API 配額使用"
git commit -m "docs: 更新團隊協作文件"

# Type 類型:
# feat     - 新功能
# fix      - 修復 bug
# refactor - 重構程式碼
# docs     - 文件更新
# style    - 格式調整
# test     - 測試相關
```

### Pull Request 流程
1. 建立功能分支: `git checkout -b feature/your-feature`
2. 開發並測試
3. 推送到遠端: `git push origin feature/your-feature`
4. 在 GitHub 建立 Pull Request
5. 等待團隊 Code Review
6. 修正建議後合併

### 聯絡方式
- **技術問題**: 在 GitHub Issues 討論
- **緊急問題**: 團隊群組即時溝通
- **文件問題**: 直接更新此文件並 commit

---

## ✅ 快速檢查表

### 開始開發前
- [ ] Docker Desktop 已啟動
- [ ] 已切換到正確分支 (`git branch`)
- [ ] 已拉取最新代碼 (`git pull`)
- [ ] `.env` 檔案已正確設定
- [ ] 容器都正常運行 (`docker compose ps`)

### 提交代碼前
- [ ] 本地測試通過
- [ ] Docker 容器能正常重建
- [ ] 無 console 錯誤或警告
- [ ] AI 功能正常運作
- [ ] Commit message 符合規範
- [ ] 已更新相關文件

### 合併代碼前
- [ ] 已與組員溝通合併計畫
- [ ] 已備份當前分支
- [ ] 已解決所有衝突
- [ ] 兩個平台都測試過
- [ ] 所有功能都正常運作

---

## 🎯 給 GitHub Copilot 的提示

> 如果你是另一位組員的 Copilot,請注意:

### 關鍵上下文
1. **這是 Docker 專案**: 所有服務都在容器內運行
2. **資料庫編碼**: 必須使用 UTF-8mb4
3. **API 配額限制**: Gemini 有速率限制,需要控制請求頻率
4. **端口號**: Flask 使用 5001 (不是 5000)
5. **模型版本**: gemini-2.0-flash-lite (不是 1.5 或 2.0)

### 避免的錯誤
```python
# ❌ 不要建議:
DB_HOST = "localhost"           # Docker 應該用 "mysql"
model = "gemini-2.0-flash"      # 會 Rate Limit
max_output_tokens = 1000        # 太高,會浪費配額
temperature = 1.0               # 太高,回應不穩定

# ✅ 正確的:
DB_HOST = "mysql"
model = "gemini-2.0-flash-lite"
max_output_tokens = 300
temperature = 0.5
```

### 檔案修改優先級
1. **高風險** (需團隊討論): 
   - `docker-compose.yml`
   - `init/init.sql`
   - `.env`

2. **中風險** (需測試):
   - `app.py`
   - `langchain_agent.py`

3. **低風險** (可直接修改):
   - `templates/*.html`
   - `static/*.js`
   - 文件檔案

---

## 📞 需要幫助?

### 問題回報流程
1. 檢查 [常見問題](#常見問題) 章節
2. 查看 Docker 日誌: `docker compose logs`
3. 在 GitHub Issues 建立問題單
4. 提供以下資訊:
   - 作業系統版本
   - Docker Desktop 版本
   - 錯誤訊息截圖
   - 相關日誌內容

### 文件更新
如果發現文件有誤或需要補充:
```bash
# 直接編輯此文件
vim TEAM_COLLABORATION.md

# 提交更新
git add TEAM_COLLABORATION.md
git commit -m "docs: 更新團隊協作文件"
git push
```

---

**最後更新**: 2025-01-19 08:15 (UTC+8)  
**維護者**: liaoyiting (macOS), [組員名稱] (Windows)  
**狀態**: ✅ 兩個平台都已驗證可運行
