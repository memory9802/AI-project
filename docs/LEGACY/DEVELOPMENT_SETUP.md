# 開發環境設置指南

> **🎯 目標**：建立統一且穩定的團隊開發環境，確保所有組員都能順利運行 AI 服裝推薦系統，同時允許必要的個人環境適配。

## 📋 快速檢查清單

**開始之前，請確認以下項目：**

- [ ] ✅ Docker Desktop 已安裝並正在運行
- [ ] ✅ Node.js (v20+) 和 npm 已安裝
- [ ] ✅ Python 3.12+ 已安裝
- [ ] ✅ Git 已配置（用戶名和郵箱）
- [ ] ✅ 端口 5001、3306、8080 未被佔用
- [ ] ✅ 已獲得 Google Gemini API Key

---

## 🚀 環境設置步驟

### 第一階段：基礎環境準備

#### 1.1 克隆專案倉庫

```bash
# 克隆專案
git clone https://github.com/memory9802/AI-project.git
cd AI-project

# 切換到開發分支
git checkout system
```

#### 1.2 環境變數設置

```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 檔案，填入您的 API Key
# macOS/Linux:
nano .env
# Windows:
notepad .env
```

**⚠️ 重要：填入實際的 API Key**
```env
LLM_API_KEY=your_actual_gemini_api_key_here
```

### 第二階段：個人環境適配（如需要）

#### 2.1 檢查端口佔用

**macOS/Linux:**
```bash
# 檢查端口佔用情況
lsof -i :5001 -i :3306 -i :8080
```

**Windows:**
```bash
# PowerShell 中檢查端口
netstat -ano | findstr "5001 3306 8080"
```

#### 2.2 創建個人配置覆蓋（如有端口衝突）

```bash
# 如果有端口衝突，創建個人配置
cp docker-compose.override.yml.example docker-compose.override.yml
```

**編輯 `docker-compose.override.yml` 範例：**
```yaml
services:
  mysql:
    ports:
      - "3307:3306"  # 改用 3307 端口
  flask:
    ports:
      - "5002:5000"  # 改用 5002 端口
  phpmyadmin:
    ports:
      - "8081:80"    # 改用 8081 端口
```

### 第三階段：啟動開發環境

#### 3.1 安裝前端依賴

```bash
# 安裝 Node.js 依賴
npm install
```

#### 3.2 啟動 Docker 服務

```bash
# 構建並啟動所有服務
docker-compose up --build

# 或者在背景運行
docker-compose up -d --build
```

#### 3.3 驗證服務運行

等待所有服務啟動後，在瀏覽器中訪問：

- **🌐 AI 服裝推薦系統**: http://localhost:5001
- **🗄️ 資料庫管理**: http://localhost:8080 (phpMyAdmin)
- **📊 應用程式 API**: http://localhost:5001/api/health

---

## 🛠️ 平台特定設置

### 🍎 macOS 用戶

#### 依賴安裝（使用 Homebrew）
```bash
# 安裝 Homebrew（如果尚未安裝）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安裝必要依賴
brew install docker docker-compose node python@3.12

# 安裝 Docker Desktop
brew install --cask docker
```

#### 效能優化設置
```bash
# Docker Desktop 設置建議
# - Memory: 4GB 或更多
# - CPUs: 2 或更多  
# - Swap: 1GB
# - Disk image size: 64GB 或更多
```

### 🪟 Windows 用戶

#### 環境準備
```powershell
# 確保 WSL2 已啟用
wsl --install

# 安裝 Docker Desktop for Windows
# 下載地址：https://www.docker.com/products/docker-desktop

# 使用 Chocolatey 安裝 Node.js 和 Python（可選）
choco install nodejs python
```

#### Windows 特定配置
```powershell
# 在 PowerShell 中設置執行策略
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 如果使用 Git Bash，確保路徑正確
git config --global core.autocrlf true
```

---

## 🔧 VS Code 設置

### 自動配置

專案已包含 VS Code 配置檔案，開啟專案後會自動：

- 📝 **統一程式碼格式化**：Python (Black)、JavaScript (Prettier)
- 🔧 **建議擴充套件**：會自動提示安裝必要的擴充套件
- 🐛 **除錯配置**：預配置的 Flask 除錯設定
- ⚡ **常用任務**：Docker 管理、依賴安裝等

### 建議的擴充套件

VS Code 會自動建議安裝以下擴充套件：

**Python 開發：**
- Python
- Black Formatter  
- Flake8
- isort

**Web 開發：**
- HTML CSS Support
- Auto Rename Tag
- Thunder Client (API 測試)

**Docker & 配置：**
- Docker
- YAML Support
- DotEnv

---

## 🚨 常見問題排除

### Q1: Docker 容器啟動失敗

**症狀**: `docker-compose up` 失敗或容器異常退出

**解決方案**:
```bash
# 1. 檢查 Docker Desktop 是否正在運行
docker --version

# 2. 清理舊的容器和映像
docker-compose down
docker system prune -f

# 3. 重新構建
docker-compose up --build --force-recreate
```

### Q2: 端口被佔用

**症狀**: 啟動時出現 "port already in use" 錯誤

**解決方案**:
```bash
# 1. 找出佔用端口的進程
# macOS/Linux:
sudo lsof -i :5001
# Windows:
netstat -ano | findstr :5001

# 2. 創建 docker-compose.override.yml 使用不同端口
# (參考上面的個人環境適配步驟)
```

### Q3: API Key 相關錯誤

**症狀**: AI 功能無法正常工作，出現 API 認證錯誤

**解決方案**:
```bash
# 1. 檢查 .env 檔案是否正確配置
cat .env | grep LLM_API_KEY

# 2. 確認 API Key 有效性
# 訪問 https://aistudio.google.com/ 檢查 API Key 狀態

# 3. 重啟 Docker 服務讓環境變數生效
docker-compose restart flask
```

### Q4: 前端資源載入失敗

**症狀**: 網頁樣式異常或 JavaScript 錯誤

**解決方案**:
```bash
# 1. 重新安裝 npm 依賴
rm -rf node_modules package-lock.json
npm install

# 2. 檢查 Webpack 編譯
npm run build

# 3. 清除瀏覽器快取並重新載入
```

### Q5: 資料庫連接失敗

**症狀**: Flask 應用無法連接到 MySQL 資料庫

**解決方案**:
```bash
# 1. 確認 MySQL 容器正在運行
docker-compose ps

# 2. 檢查資料庫初始化日誌
docker-compose logs mysql

# 3. 重置資料庫資料卷
docker-compose down -v
docker-compose up --build
```

---

## 📊 環境驗證腳本

**運行環境檢查腳本：**

```bash
# 給腳本執行權限（macOS/Linux）
chmod +x scripts/check-environment.sh

# 運行環境檢查
./scripts/check-environment.sh
```

**Windows PowerShell：**
```powershell
# 運行環境檢查
.\scripts\check-environment.ps1
```

---

## 🤝 團隊協作指南

### Git 工作流程

```bash
# 1. 開始新功能開發前，先同步最新代碼
git pull origin system

# 2. 創建功能分支
git checkout -b feature/your-feature-name

# 3. 開發完成後提交（避免提交個人配置）
git add .
git commit -m "feat: add new feature description"

# 4. 推送並創建 Pull Request
git push origin feature/your-feature-name
```

### ⚠️ 重要提醒

**不要提交的檔案：**
- ❌ `.env` (包含 API Keys)
- ❌ `docker-compose.override.yml` (個人配置)  
- ❌ `node_modules/` (npm 依賴)
- ❌ `__pycache__/` (Python 快取)
- ❌ `mysql_data/` (資料庫資料)

**可以提交的檔案：**
- ✅ `.env.example` (環境變數範本)
- ✅ `docker-compose.override.yml.example` (個人配置範本)
- ✅ 所有原始程式碼檔案
- ✅ `package.json` 和 `package-lock.json`
- ✅ 文檔和設置檔案

---

## 📞 獲得幫助

如果遇到問題：

1. **查看常見問題排除**（上方）
2. **運行環境檢查腳本**
3. **查看 Docker 日誌**：`docker-compose logs`
4. **聯絡團隊成員**或在團隊討論群組發問
5. **創建 GitHub Issue** 描述具體問題

---

## 🎯 下一步

環境設置完成後，您可以：

- 🔍 **探索 AI 功能**：測試服裝推薦和對話功能  
- 🛠️ **開始開發**：參考 `README.md` 了解專案結構
- 📚 **查看 API 文檔**：了解可用的 API 端點
- 🧪 **運行測試**：確保所有功能正常運作

**祝您開發順利！** 🚀