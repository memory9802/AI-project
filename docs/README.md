# 📚 AI-project 技術文檔中心

> **完整開發指南**：環境標準化 | Python 3.12+ | Flask 3.1.2 | Docker Multi-stage

---

## 🚀 快速啟動

### ⚡ **一分鐘設置**
```bash
# 1. 建立虛擬環境
python3.12 -m venv venv && source venv/bin/activate

# 2. 安裝開發依賴
pip install -r app/requirements-dev.txt

# 3. 啟動開發服務器
python app/app.py
```

### � **Docker 開發**
```bash
# 建置開發映像
docker build --target development -t ai-project:dev .

# 啟動容器 (熱重載)
docker run -p 5000:5000 -v $(pwd)/app:/app ai-project:dev
```

---

## 📦 套件管理

### 🎯 **三層式依賴結構**
```
app/
├── requirements.txt          # 核心生產依賴
├── requirements-dev.txt      # 開發環境專用  
├── requirements-prod.txt     # 生產環境最佳化
└── requirements-test.txt     # 測試專用 (可選)
```

### 🔧 **版本管理策略**

| 套件類型 | 版本策略 | 範例 | 理由 |
|----------|----------|------|------|
| **核心框架** | 精確版本 | `Flask==3.1.2` | 環境一致性 |
| **AI 框架** | 精確版本 | `langchain==0.3.26` | API 穩定性 |
| **開發工具** | 相容版本 | `pytest>=7.4.0,<8.0` | 開發彈性 |

### 📋 **關鍵套件版本**
```python
# Web 框架 (符合標準化)
Flask==3.1.2
Werkzeug>=3.1.0

# 資料庫 ORM
SQLAlchemy==2.0.23
PyMySQL==1.1.1

# AI 引擎 (版本鎖定)
langchain==0.3.26
langchain-google-genai==2.0.4

# 開發工具
pytest>=7.4.0,<8.0
black==23.11.0
flake8==6.1.0
```

---

## ⚙️ 環境配置

### 🖥️ **本機開發環境**

#### **macOS 設置**
```bash
# 1. 安裝 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 安裝 Python 3.12+
brew install python@3.12 && brew link python@3.12

# 3. 安裝 MySQL 客戶端
brew install mysql-client
echo 'export PATH="/opt/homebrew/opt/mysql-client/bin:$PATH"' >> ~/.zshrc

# 4. 安裝 Git 和 Docker
brew install git docker
```

#### **Windows 設置**
```powershell
# 使用 Chocolatey
choco install python312 git docker-desktop mysql.workbench
```

### 🐍 **Python 虛擬環境**
```bash
# 建立虛擬環境 (Python 3.12+)
python3.12 -m venv venv

# 啟用虛擬環境
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate     # Windows

# 升級 pip 並安裝依賴
pip install --upgrade pip
pip install -r app/requirements-dev.txt
```

### 🛠️ **VS Code 整合**
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.flake8Enabled": true,
  "python.testing.pytestEnabled": true,
  "editor.formatOnSave": true
}
```

---

## 🐳 Docker 配置

### 🏗️ **多階段建置**
```dockerfile
# 開發階段 - 包含開發工具
FROM python:3.12-slim as development
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt
CMD ["python", "app.py"]

# 生產階段 - 最小化映像  
FROM python:3.12-slim as production
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

### � **快速命令**
```bash
# 開發環境
docker build --target development -t ai-project:dev .
docker run -p 5000:5000 -v $(pwd)/app:/app ai-project:dev

# 生產環境
docker build --target production -t ai-project:prod .
docker run -p 5000:5000 ai-project:prod
```

---

## 🗄️ 資料庫配置

### 🐬 **MySQL 8.0 設置**

#### **Docker 容器方式 (推薦)**
```bash
# 建置自訂 MySQL 映像 (解決 macOS 權限問題)
docker-compose build mysql

# 啟動 MySQL 服務
docker-compose up -d mysql

# 使用管理腳本 (更方便)
./scripts/mysql-manager.sh build   # 建置映像
./scripts/mysql-manager.sh start   # 啟動服務
./scripts/mysql-manager.sh reset   # 重置資料庫
```

#### **本機安裝方式**
```bash
# macOS 本機安裝
brew install mysql@8.0
brew services start mysql@8.0

# 建立開發資料庫
mysql -u root -p
CREATE DATABASE outfit_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'apppass';
GRANT ALL PRIVILEGES ON outfit_db.* TO 'appuser'@'localhost';
```

### 🔗 **連線配置**
```python
# Docker 環境配置 (預設)
DATABASE_URL = 'mysql://root:rootpassword@mysql:3306/outfit_db'

# 本機環境配置
DATABASE_URL = 'mysql://appuser:apppass@localhost:3306/outfit_db'

# Flask 應用設定
SQLALCHEMY_DATABASE_URI = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

---

## 🧪 測試與品質

### 📊 **測試執行**
```bash
# 執行所有測試
pytest

# 測試覆蓋率
pytest --cov=app --cov-report=html

# 程式碼品質檢查
black app/ && isort app/ && flake8 app/
```

### 🔍 **除錯工具**
```bash
# 互動式除錯
python -m ipdb app.py

# 記憶體分析
python -m memory_profiler app.py
```

---

## 🤖 AI 功能配置

### 🔑 **API Keys 設置**
```bash
# .env 文件配置
GOOGLE_AI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-key
DATABASE_URL=mysql://appuser:apppass@localhost/ai_fashion
```

### 💬 **LangChain 整合**
```python
# AI Agent 基本配置
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# 穿搭推薦提示範本
template = """你是專業的穿搭顧問。
用戶問題: {user_message}
場合: {occasion}
風格: {style}
預算: {budget}

請提供專業穿搭建議:"""
```

---

## ⚡ 快速參考

### 🎯 **常用指令**

| 功能 | 指令 | 說明 |
|------|------|------|
| **環境啟用** | `source venv/bin/activate` | 啟用虛擬環境 |
| **安裝依賴** | `pip install -r app/requirements-dev.txt` | 開發環境 |
| **啟動應用** | `python app/app.py` | Flask 開發服務器 |
| **執行測試** | `pytest` | 運行所有測試 |
| **程式碼格式化** | `black app/` | 自動格式化 |

### 🌐 **常用端點**

| 端點 | 用途 | 範例 URL |
|------|------|----------|
| `GET /` | 主頁 | http://localhost:5000/ |
| `POST /chat` | AI 聊天 | http://localhost:5000/chat |
| `GET /api/health` | 健康檢查 | http://localhost:5000/api/health |

### 🚨 **故障排除**

| 錯誤 | 解決方案 |
|------|----------|
| **ImportError** | 檢查虛擬環境是否啟用 |
| **MySQL 連線錯誤** | 檢查資料庫服務狀態 |
| **Docker 建置失敗** | 清除快取 `docker system prune -a` |

---

## 🔄 開發流程

### 👥 **團隊協作**
1. **功能開發**: 遵循 OpenSpec 規格
2. **程式碼提交**: 使用統一的 commit 格式
3. **測試驗證**: 確保所有測試通過
4. **文檔更新**: 同步更新相關文檔

### 📈 **品質標準**
- **測試覆蓋率**: > 80%
- **程式碼品質**: Black + Flake8 檢查通過
- **效能要求**: API 回應時間 < 500ms
- **安全性**: 定期掃描套件漏洞

---

## 🎯 專案標準化狀態

### ✅ **已完成項目**

| 組件 | 標準化目標 | 當前版本 | 狀態 |
|------|------------|----------|------|
| **Python** | 3.12+ | 3.12+ | ✅ 完成 |
| **Flask** | 3.1.2 | 3.1.2 | ✅ 完成 |
| **LangChain** | 0.3.26 | 0.3.26 | ✅ 完成 |
| **MySQL** | 8.0 | 8.0 | ✅ 完成 |
| **Docker** | 多階段建置 | 支援 | ✅ 完成 |
| **套件管理** | 三層式結構 | 實施 | ✅ 完成 |

### 🚀 **下一階段**
- Docker 環境實施 (50+ 任務待執行)
- CI/CD 管道建設
- 生產環境部署優化

---

## 📞 支援與聯絡

### 🆘 **問題求助**
- **技術問題**: 查看本文檔故障排除章節
- **環境設置**: 參考環境配置章節  
- **Bug 回報**: [GitHub Issues](https://github.com/memory9802/AI-project/issues)

### � **文檔維護**
- **更新頻率**: 隨功能更新
- **維護團隊**: AI-project 開發團隊
- **最後更新**: 2025年11月20日

---

*返回專案根目錄: [README.md](../README.md) | 查看規格指南: [SPEC_GUIDE.md](../SPEC_GUIDE.md)*