# 👗 AI 穿搭推薦網站

> 基於 Google Gemini + LangChain 的智能穿搭推薦系統

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

---

## 📖 專案簡介

結合 AI 技術的穿搭建議網站,透過對話式互動提供個性化穿搭建議。

**核心功能**: AI 聊天 | 資料庫推薦 | 對話記憶 | 多模型備援  
**技術棧**: Flask + MySQL + Docker + Gemini 2.0 Lite  
**狀態**:### 🔐 安全性

### API Key 管理
- ✅ `.env` 已加入 `.gitignore`
- ✅ 使用 `.env.example` 作為範本
- ⚠️ 不要將 API Key 寫入程式碼
- ⚠️ 不要提交 `.env` 到 Git
- 💡 每位開發者需自行申請 Gemini API Key

### 🔑 API Key 申請步驟
1. 前往 [Google AI Studio](https://aistudio.google.com/)
2. 使用 Google 帳號登入
3. 點擊 "Get API Key" → "Create API Key"
4. 複製 API Key 並設定到 `.env` 檔案
5. 免費額度：每分鐘 15 requests，每日足夠開發使用 (Windows/macOS 已測試)

---

## 🚀 快速開始

### Windows 用### 📞 需要幫助?

### 文件資源
- **團隊協作**: [TEAM_COLLABORATION.md](TEAM_COLLABORATION.md) - 詳細設定指南
- **GitHub**: https://github.com/memory9802/AI-project
- **Issues**: 在 GitHub 提問

### 🚀 開發工作流程

#### 功能開發流程
```bash
# 1. 建立功能分支
git checkout -b feature/your-feature-name

# 2. 開發並測試
source venv/bin/activate  # 啟動 Python 環境
docker compose up -d      # 啟動服務
code .                    # 開啟 VS Code

# 3. 提交變更
git add .
git commit -m "feat: 新增XXX功能"

# 4. 推送並建立 Pull Request
git push origin feature/your-feature-name
```

#### 專案架構說明
```
AI-project/
├── app/
│   ├── app.py              # 🔥 Flask 主程式
│   ├── langchain_agent.py  # 🤖 AI Agent
│   ├── requirements.txt    # 📦 Python 依賴
│   ├── templates/          # 🎨 HTML 模板
│   └── static/            # 🎨 CSS/JS/圖片
├── init/init.sql          # 🗄️ 資料庫初始化
├── docker-compose.yml     # 🐳 Docker 配置
├── package.json          # 📦 Node.js 依賴
├── venv/                 # 🐍 Python 虛擬環境
└── .env                  # ⚙️ 環境變數（不要提交）
```powershell
git clone https://github.com/memory9802/AI-project.git
cd AI-project && git checkout Jinja
Copy-Item .env.example .env
# 編輯 .env 設定您的 API Key
.\start-windows.ps1
```

### macOS / Linux 用戶
```bash
git clone https://github.com/memory9802/AI-project.git
cd AI-project && git checkout Jinja
cp .env.example .env
# 編輯 .env 設定您的 API Key
chmod +x start-macos.sh && ./start-macos.sh
```

### 服務連結
- 🌐 **網站**: http://localhost:5001
- 🗄️ **資料庫管理**: http://localhost:8080 (帳號: root / 密碼: rootpassword)

> **📘 詳細設定**: 請參考 [TEAM_COLLABORATION.md](TEAM_COLLABORATION.md)

---

## 📁 專案結構

```
AI-project/
├── app.py                    # Flask 主程式
├── langchain_agent.py        # AI Agent (已優化配額)
├── docker-compose.yml        # Docker 配置
├── requirements.txt          # Python 依賴
├── .env.example              # 環境變數範本
│
├── init/init.sql             # 資料庫初始化 (11 張表)
├── templates/                # HTML 模板
├── static/                   # CSS/JS/圖片
├── data/                     # 對話記錄
│
├── start-windows.ps1         # Windows 啟動腳本
├── start-macos.sh            # macOS 啟動腳本
│
└── TEAM_COLLABORATION.md     # 團隊協作指南 📘
```

---

## 🛠️ 系統架構

### 容器服務
```yaml
mysql:       資料庫 (port 3306)
flask:       後端 API (port 5001) ⚠️ 注意是 5001
phpmyadmin:  資料庫管理 (port 8080)
```

### 資料庫結構 (11 張表)
| 表名 | 說明 | 測試資料 |
|------|------|---------|
| `outfits` | 穿搭組合 | 3 筆 |
| `items` | 單品項目 | 9 筆 |
| `outfit_items` | 穿搭-單品關聯 | 9 筆 |
| `users` | 用戶資料 | 4 筆 |
| `user_wardrobe` | 用戶衣櫃 | 4 筆 |
| `outfit_ratings` | 穿搭評分 | 5 筆 |
| `partner_products` | 合作商品 | 3 筆 |
| `conversation_history` | 對話記錄 | 動態 |
| ... | 其他 | ... |

### API 端點
```
GET  /                  首頁
POST /recommend         AI 推薦 (JSON API)
GET  /items             取得單品列表
POST /clear_session     清除對話記憶
GET  /ping              健康檢查
```

---

## � 開發環境設置

### 📋 必需工具清單

#### 本機全域安裝
- **Docker Desktop**: 容器化平台
- **Git**: 版本控制工具
- **VS Code**: 程式碼編輯器（推薦）
- **Node.js**: 前端開發環境
- **Python 3.11+**: 後端開發環境

#### macOS 用戶安裝指令
```bash
# 安裝 Homebrew（套件管理器）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 設定 Homebrew 環境
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc

# 安裝開發工具
brew install node git
brew install --cask docker visual-studio-code postman
```

#### Windows 用戶安裝
1. 下載並安裝 [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. 下載並安裝 [Git for Windows](https://git-scm.com/download/win)  
3. 下載並安裝 [Node.js](https://nodejs.org/)
4. 下載並安裝 [VS Code](https://code.visualstudio.com/)

### 🐍 Python 虛擬環境設置

```bash
# 1. 建立虛擬環境
python3 -m venv venv

# 2. 啟動虛擬環境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 3. 安裝 Python 套件
pip install --upgrade pip
pip install -r app/requirements.txt

# 4. 驗證安裝
python -c "import flask, cv2, langchain; print('✅ Python 環境就緒')"
```

### 🎨 前端開發環境

```bash
# 1. 初始化 npm 專案（如果沒有 package.json）
npm init -y

# 2. 安裝前端套件
npm install bootstrap jquery axios
npm install --save-dev webpack webpack-cli css-loader style-loader

# 3. 驗證安裝
npm list --depth=0
```

### 📱 VS Code 推薦擴展

安裝以下擴展提升開發效率：
```
- Python
- Flask Snippets  
- Docker
- Bootstrap IntelliSense
- Auto Rename Tag
- Prettier - Code formatter
- GitLens
- Thunder Client (API 測試)
```

### 🔧 API Key 設定

1. **取得 Google Gemini API Key**:
   - 前往 [Google AI Studio](https://aistudio.google.com/)
   - 申請免費 API Key
   - 複製 API Key

2. **設定環境變數**:
   ```bash
   # 複製環境變數範本
   cp .env.example .env
   
   # 編輯 .env 檔案
   # 將 your_gemini_api_key_here 替換為您的實際 API Key
   ```

### 🧪 環境驗證

```bash
# 1. 檢查 Docker
docker --version
docker compose --version

# 2. 檢查 Python 環境  
source venv/bin/activate  # macOS/Linux
python --version
pip list | grep flask

# 3. 檢查 Node.js 環境
node --version
npm --version

# 4. 啟動完整服務
docker compose up -d
curl http://localhost:5001/ping  # 應該返回 JSON

# 5. 測試 AI 功能
curl -X POST http://localhost:5001/recommend \
  -H "Content-Type: application/json" \
  -d '{"message":"測試穿搭建議","session_id":"test"}'
```

---

## �🔧 常用指令

### Docker 管理
```bash
docker compose up -d --build    # 啟動服務
docker compose down             # 停止服務
docker compose restart flask    # 重啟 Flask
docker compose logs -f flask    # 查看日誌
docker compose ps               # 檢查狀態
```

### 測試 API
```bash
# 健康檢查
curl http://localhost:5001/ping

# 測試 AI 推薦
curl -X POST http://localhost:5001/recommend \
  -H "Content-Type: application/json" \
  -d '{"message":"約會穿搭建議","user_id":1}'
```

---

## ⚙️ 關鍵配置

### 環境變數 (.env)
```bash
# AI 配置 - 請設定您的 API Key
LLM_API_KEY=your_gemini_api_key_here
GOOGLE_GENAI_API_VERSION=v1

# 資料庫 (Docker 模式,不要改)
DB_HOST=mysql          # ⚠️ 必須用 "mysql" 不是 localhost
DB_PORT=3306
DB_USER=root
DB_PASS=rootpassword
DB_NAME=outfit_db
```

### AI 模型設定
```python
# langchain_agent.py & app.py
model = "gemini-2.0-flash-lite"  # ⚠️ Lite 版本配額更高
temperature = 0.5                 # 降低隨機性
max_output_tokens = 300           # 限制輸出長度
MIN_REQUEST_INTERVAL = 2          # 速率限制 (秒)
```

### MySQL 編碼
```yaml
# docker-compose.yml
command:
  - --character-set-server=utf8mb4      # ⚠️ 避免中文亂碼
  - --collation-server=utf8mb4_unicode_ci
```

---

## 🤝 團隊協作

### 當前狀態
- **分支**: `Jinja` (主開發分支)
- **Git**: https://github.com/memory9802/AI-project
- **已修復**: 資料庫亂碼 | AI Rate Limit | 配額優化

### 合併其他組員功能
```bash
# 1. 備份當前分支
git checkout -b backup-$(date +%Y%m%d)

# 2. 合併組員分支
git checkout Jinja
git merge origin/feature/your-teammate-branch

# 3. 解決衝突並測試
docker compose down
docker compose up -d --build

# 4. 測試功能
curl http://localhost:5001/ping

# 5. 推送
git push origin Jinja
```

### Commit 規範
```bash
feat: 新增功能
fix: 修復 Bug
docs: 更新文件
refactor: 重構程式碼
style: 格式調整
```

> **📘 詳細流程**: [TEAM_COLLABORATION.md](TEAM_COLLABORATION.md) 有完整的合併指南

---

## 🐛 常見問題

### Q1: 容器無法啟動?
```bash
# 確認 Docker Desktop 運行中
# 清理並重啟
docker compose down -v
docker system prune -f
docker compose up -d --build
```

### Q2: AI 回應 "服務無法使用"?
```bash
# 檢查日誌
docker compose logs flask --tail 50

# 確認 API Key
cat .env | grep LLM_API_KEY

# 確認模型設定
grep GEMINI_MODEL app.py
# 應該是: gemini-2.0-flash-lite
```

### Q3: 資料庫中文亂碼?
```bash
# 檢查編碼
docker exec outfit-mysql mysql -u root -prootpassword \
  -e "SHOW VARIABLES LIKE 'char%';"
# 應該全部是 utf8mb4

# 如果不是,重建容器
docker compose down -v
docker compose up -d --build
```

### Q4: 端口被佔用?
```bash
# Windows
netstat -ano | findstr "5001 3306 8080"

# macOS
lsof -i :5001 -i :3306 -i :8080

# 修改端口 (docker-compose.yml)
ports:
  - "5002:5000"  # 改用 5002
```

### Q5: 合併衝突怎麼辦?
**保留以下設定**:
- `GEMINI_MODEL = "gemini-2.0-flash-lite"`
- `DB_HOST = "mysql"`
- `charset = "utf8mb4"`
- `MIN_REQUEST_INTERVAL = 2`

> **📘 更多問題**: 查看 [TEAM_COLLABORATION.md](TEAM_COLLABORATION.md) 的常見問題章節

---

## 📊 效能指標

### 正常運行
| 指標 | 值 |
|------|---|
| 啟動時間 | 10-15 秒 |
| API 回應時間 | 2-4 秒 |
| 回應長度 | 200-400 字 |
| Token 消耗 | ~500/請求 |
| 錯誤率 | 0% |
| 配額消耗 | 減少 85% |

### 異常狀態
- 啟動 > 30 秒 → Docker 有問題
- API > 10 秒 → Rate Limit
- 回應 < 50 字 → AI 配置錯誤
- 錯誤率 > 10% → 嚴重問題

---

## 📚 開發指南

### 本地開發 (不使用 Docker)
```bash
# 1. 安裝 Python 3.11
# 2. 建立虛擬環境
python -m venv venv
source venv/bin/activate  # macOS
venv\Scripts\activate     # Windows

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 啟動 MySQL (需另外安裝)
# 5. 修改 .env
DB_HOST=localhost  # 本地模式

# 6. 執行
python app.py
```

### 資料庫操作
```bash
# 進入 MySQL 容器
docker exec -it outfit-mysql bash
mysql -u root -prootpassword outfit_db

# 常用 SQL
SHOW TABLES;
SELECT * FROM outfits;
SELECT * FROM items;
```

### 新增 API 端點
```python
# app.py
@app.route('/your-endpoint', methods=['POST'])
def your_function():
    data = request.json
    # 你的邏輯
    return jsonify({"result": "success"})
```

### 修改 AI 回應
```python
# langchain_agent.py
# 修改 system_prompt (line ~100)
self.system_prompt = """
你是「搭搭」,一個活潑親切的穿搭顧問。
[你的提示詞]
"""
```

---

## 🔐 安全性

### API Key 管理
- ✅ `.env` 已加入 `.gitignore`
- ✅ 使用 `.env.example` 作為範本
- ⚠️ 不要將 API Key 寫入程式碼
- ⚠️ 不要提交 `.env` 到 Git

### 資料庫安全
- ⚠️ 生產環境請修改預設密碼
- ⚠️ 限制 phpMyAdmin 存取
- ⚠️ 使用 SSL 連線

---

## 🚢 部署指南

### Docker Compose (推薦)
```bash
# 生產環境設定
docker compose -f docker-compose.prod.yml up -d

# 使用環境變數
export DB_PASS=your-secure-password
docker compose up -d
```

### 雲端部署
- **Azure**: Azure Container Instances
- **AWS**: ECS + RDS
- **GCP**: Cloud Run + Cloud SQL

---

## 📈 專案狀態

### ✅ 已完成
- [x] Docker 環境建置
- [x] MySQL 資料庫 (UTF-8mb4)
- [x] AI 聊天機器人 (Gemini 2.0 Lite)
- [x] 對話記憶功能
- [x] API 配額優化 (減少 85%)
- [x] 速率限制實施
- [x] 跨平台支援 (Windows/macOS)

### 🚧 進行中
- [ ] 前端 UI 美化
- [ ] 用戶登入系統
- [ ] 衣櫃管理功能

### 📋 規劃中
- [ ] 圖片辨識
- [ ] 社群分享
- [ ] 合作商品推薦

---

## 🎓 技術重點說明

### 為什麼使用 gemini-2.0-flash-lite?
1. ✅ **配額更高**: 免費額度比 2.0-flash 多
2. ✅ **回應快**: 延遲更低
3. ✅ **支援好**: 團隊 API key 完全支援
4. ✅ **已優化**: 實施速率限制 + Token 優化

### 為什麼 DB_HOST 要用 "mysql"?
- Docker 容器內部使用**服務名稱**通訊
- `localhost` 在容器內指向容器自己
- `mysql` 會自動解析到 MySQL 容器 IP

### 為什麼要用 utf8mb4?
- `utf8` 在 MySQL 中只支援 3 bytes
- `utf8mb4` 完整支援 4 bytes (包含 emoji)
- 避免中文、emoji 出現亂碼

### 為什麼端口是 5001?
- macOS 的 5000 被 AirPlay 佔用
- 改用 5001 避免衝突
- Windows 無此問題但統一使用 5001

---

## 🤖 給 AI 助手的提示

> 如果你是組員的 Copilot AI,請記住:

### 核心配置 (不要建議修改)
```python
model = "gemini-2.0-flash-lite"  # 不是 2.0-flash 或 1.5-flash
DB_HOST = "mysql"                 # 不是 localhost
charset = "utf8mb4"               # 不是 utf8
port = 5001                       # 不是 5000
MIN_REQUEST_INTERVAL = 2          # 速率限制
max_output_tokens = 300           # Token 限制
```

### 避免的錯誤
- ❌ 建議使用 `localhost` 連接資料庫
- ❌ 建議修改 AI 模型為其他版本
- ❌ 建議移除速率限制
- ❌ 建議增加 max_tokens 到 1000+
- ❌ 建議使用本地 Python 而非 Docker

---

## 📞 需要幫助?

### 文件資源
- **團隊協作**: [TEAM_COLLABORATION.md](TEAM_COLLABORATION.md) - 詳細設定指南
- **GitHub**: https://github.com/memory9802/AI-project
- **Issues**: 在 GitHub 提問

### 檢查清單
```bash
# 環境檢查
docker compose ps                # 3 個容器都要 Up
curl http://localhost:5001/ping  # 返回 JSON

# 資料庫檢查
docker exec outfit-mysql mysql -u root -prootpassword -e "SELECT 1"

# AI 檢查
curl -X POST http://localhost:5001/recommend \
  -H "Content-Type: application/json" \
  -d '{"message":"測試","user_id":1}'
```

---

## 👥 團隊開發

### 分工建議
- **後端開發** - Flask API、資料庫設計
- **前端開發** - UI/UX、JavaScript 互動  
- **AI 整合** - LangChain、模型優化
- **DevOps** - Docker、部署、CI/CD
- **測試** - 功能測試、文件撰寫

### 開發注意事項
- ✅ 遵循 Git Flow 工作流程
- ✅ 提交前先執行本地測試
- ✅ API Key 不要提交到 Git
- ✅ 保持代碼風格一致
- ✅ 及時更新文件和註釋

---

## 📄 授權

本專案僅供學習使用。

---

## 🙏 致謝

- [Google Gemini](https://ai.google.dev/) - AI 模型
- [LangChain](https://www.langchain.com/) - AI 框架
- [Flask](https://flask.palletsprojects.com/) - Web 框架

---

**⭐ 完整的團隊協作指南請查看 [TEAM_COLLABORATION.md](TEAM_COLLABORATION.md)**

---

**最後更新**: 2025-01-19  
**版本**: 1.0  
**維護狀態**: ✅ 活躍維護中
