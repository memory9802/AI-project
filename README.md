# 👗 AI 穿搭推薦網站

> 基於 Google Gemini + LangChain 的智能穿搭推薦系統  
> **🚀 新組員請直接閱讀：[規格化開發指南](### 🆕 新組員開始
1. 📖 閱讀 [規格化開發指南](SPEC_GUIDE.md)
2. 📚 查看 [完整技術文檔](docs/README.md) 了解開發環境和工具
3. ⚡ 快速啟動：使用 Docker 一鍵部署
4. 🔧 參考技術文檔進行深度配置

### 💻 日常開發
1. 🔍 使用 OpenSpec 規格驅動開發  
2. 📚 查閱 [技術文檔中心](docs/README.md) 獲取詳細指引
3. 🤝 按照團隊協作流程提交代碼
4. 🐛 參考文檔故障排除章節解決問題md)**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Multi--Stage-blue.svg)](https://www.docker.com/)
[![Environment](https://img.shields.io/badge/Environment-Standardized-success.svg)](#)

---

## 📖 專案簡介

結合 AI 技術的穿搭建議網站，透過對話式互動提供個性化穿搭建議。

**核心功能**: AI 聊天 | 資料庫推薦 | 對話記憶 | 多模型備援  
**技術棧**: Flask 3.1.2 + MySQL 8.0 + Docker Multi-stage + Gemini 2.0 Lite  
**開發模式**: OpenSpec 規格驅動開發 | **環境標準化完成** ✅

---

## 🚀 快速啟動

### ⚡ 一分鐘設置

```bash
# 1. 克隆並進入專案
git clone https://github.com/memory9802/AI-project.git
cd AI-project && git checkout system

# 2. 設置環境變數（必要！）
cp .env.example .env
# 編輯 .env 並添加您的 Gemini API Key

# 3. 啟動服務
docker-compose up --build

# 4. 訪問服務
# 網站: http://localhost:5001
# 資料庫管理: http://localhost:8080
```

### 🔑 API Key 申請
1. 訪問 [Google AI Studio](https://aistudio.google.com/)
2. 登入並創建 API Key
3. 添加到 `.env` 檔案：`LLM_API_KEY=your_key_here`

---

## 🏗️ 專案架構

```
AI-project/
├── 📱 app/                    # Flask 應用程式
│   ├── ai_agent.py           # AI 對話引擎
│   ├── langchain_agent.py    # LangChain 整合
│   ├── requirements.txt      # 核心生產依賴 ✨
│   ├── requirements-dev.txt  # 開發環境依賴 ✨
│   ├── requirements-prod.txt # 生產環境依賴 ✨
│   └── blueprints/           # 功能模組
├── 🗄️ init/                   # 資料庫初始化
├── 🐳 Dockerfile             # 多階段容器建置 ✨
├── 🐳 docker-compose.yml     # 容器編排
├── 📚 docs/                   # 技術文檔 (標準化指南) ✨
├── 📋 SPEC_GUIDE.md          # 規格化開發指南
└── 📂 openspec/              # OpenSpec 規格管理
```

**✨ = 環境標準化新增/更新**

### 🔧 技術選型理由

| 技術 | 選擇理由 | 替代方案 |
|------|----------|----------|
| **Gemini 2.0 Lite** | 免費、速度快、中文支援好 | OpenAI GPT、Claude |
| **LangChain** | 記憶管理、多模型切換 | 直接 API 呼叫 |
| **Flask** | 輕量、易學習、彈性高 | Django、FastAPI |
| **Docker** | 環境一致、部署簡單 | 本機安裝 |
| **MySQL** | 關聯式資料、穩定成熟 | PostgreSQL、MongoDB |

---

## 🎯 開發指南

### 🆕 新組員開始
1. 📖 閱讀 [規格化開發指南](SPEC_GUIDE.md)
2. ⚙️ 按照 [環境配置指南](docs/ENVIRONMENT_SETUP.md) 設置開發環境  
3. 📦 參考 [套件管理指南](docs/PACKAGE_MANAGEMENT.md) 安裝依賴
4. � 使用 [快速參考卡片](docs/QUICK_REFERENCE.md) 開始開發

### 💻 日常開發
1. 🔍 使用 OpenSpec 規格驅動開發  
2. 🔧 參考 [快速參考卡片](docs/QUICK_REFERENCE.md) 
3. 🤝 按照團隊協作流程提交代碼
4. 🐛 查看 [環境配置指南](docs/ENVIRONMENT_SETUP.md) 排除問題

### 📋 重要文件

| 文件 | 用途 | 目標讀者 |
|------|------|----------|
| [SPEC_GUIDE.md](SPEC_GUIDE.md) | 統一開發指南 | 所有開發者 |
| [docs/README.md](docs/README.md) | **完整技術文檔中心** | 開發團隊 |
| [openspec/](openspec/) | 規格管理 | 功能開發者 |
| [docker-compose.yml](docker-compose.yml) | 容器編排配置 | DevOps |

---

## 📁 專案結構

```
AI-project/
├── 📱 app/                    # Flask 應用程式
│   ├── app.py                # 主應用程式入口
│   ├── ai_agent.py           # AI 智能代理
│   ├── langchain_agent.py    # LangChain 整合
│   ├── requirements*.txt     # 三層式套件管理 ✨
│   ├── blueprints/           # Flask 模組化路由
│   ├── lib/                  # 共用函式庫
│   ├── static/               # 靜態資源 (CSS, JS, 圖片)
│   └── templates/            # Jinja2 HTML 樣板
├── 🐳 Dockerfile             # 多階段容器建置 ✨
├── 🐳 docker-compose.yml     # 容器編排
├── 📚 docs/                   # 技術文檔
├── 🗄️ init/                  # 資料庫初始化
├── 🚀 scripts/               # 啟動腳本
├── 📂 openspec/               # OpenSpec 規格管理
└── 📋 SPEC_GUIDE.md          # 規格化開發指南
```

**✨ = 環境標準化後更新**

---

## 🔐 安全須知

- **API Keys**: 使用 `.env` 管理，絕不提交到 Git
- **個人配置**: 使用 `docker-compose.override.yml`
- **Git 保護**: 強化 `.gitignore` 規則

---

## 📞 需要幫助？

### 快速支援
- **🆘 緊急問題**: 查看 [SPEC_GUIDE.md - 問題排除](SPEC_GUIDE.md#問題排除)
- **� 技術文檔**: 參考 [完整技術文檔中心](docs/README.md)
- **🐛 Bug 回報**: [GitHub Issues](https://github.com/memory9802/AI-project/issues)
- **💬 團隊討論**: 團隊群組

### 聯繫資訊
- **專案維護**: AI-project 5人開發團隊
- **最後更新**: 2025年11月20日

---

*這是專案的簡化概覽。詳細的開發指引、環境設置、團隊協作流程請參考 [規格化開發指南](SPEC_GUIDE.md)。*