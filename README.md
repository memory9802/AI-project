# AI-Project - 智能穿搭推薦系統

一個基於 AI 的穿搭推薦系統，支援多模型備援（Gemini/Groq/DeepSeek）和完整的環境隔離機制。

## 🚀 快速開始

### 1. 環境需求
- Docker 和 Docker Compose
- Git

### 2. 設定環境

**方法 A：使用自動設定腳本（推薦）**
```powershell
.\setup-env.ps1
```

**方法 B：手動設定**
```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 填入你的 API Keys 和 Port 設定
# 詳見 SETUP_GUIDE.md
```

### 3. 啟動服務
```bash
docker-compose up -d
```

### 4. 訪問應用
- **主應用**: http://localhost:5001
- **資料庫管理**: http://localhost:8080

## 📚 詳細文件

- **[環境設定指南](SETUP_GUIDE.md)** - 完整的多設備設定說明
- **[Port 設定說明](PORT_CONFIG.md)** - Port 衝突處理方法

## 🎯 主要功能

- ✅ AI 對話式穿搭推薦
- ✅ 多 AI 模型自動備援
- ✅ RAG 關鍵字檢索
- ✅ 對話記憶功能
- ✅ 完整的環境隔離
- ✅ Port 自動配置

## 🛠️ 技術棧

- **後端**: Flask + LangChain
- **資料庫**: MySQL 8.0
- **AI 模型**: Gemini / Groq / DeepSeek
- **容器化**: Docker + Docker Compose

## 🔧 常用指令

```bash
# 查看運行狀態
docker-compose ps

# 查看日誌
docker logs outfit-flask

# 重啟服務
docker-compose restart

# 停止服務
docker-compose down

# 完全清除（包含資料）
docker-compose down -v
```

## 🤝 多人協作

本專案支援多設備同時開發，每個開發者可以：
- 設定不同的 port
- 使用獨立的容器前綴
- 擁有獨立的資料庫和對話記錄

詳見 [環境設定指南](SETUP_GUIDE.md)

## 📝 授權

此專案為學校專題作品。
