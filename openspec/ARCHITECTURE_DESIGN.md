# AI 專案架構設計總覽

> **統一架構設計**：AI 穿搭推薦系統的完整環境架構設計  
> **涵蓋範圍**：開發環境 + Docker 容器環境的整合設計

---

## 🏗️ 整體架構概覽

### 🎯 設計原則

| 原則 | 開發環境 | Docker 環境 | 實現方式 |
|------|----------|-------------|----------|
| **一致性** | 統一開發工具鏈 | 標準化容器版本 | 版本鎖定 + 配置標準化 |
| **可重現性** | 環境檢查腳本 | 容器化部署 | 自動化驗證 + 映像管理 |
| **可擴展性** | 配置分離架構 | 微服務設計 | Override 機制 + 服務解耦 |
| **安全性** | Git 保護策略 | 容器安全實踐 | 權限控制 + 網路隔離 |
| **效能** | 本地開發最佳化 | 生產環境最佳化 | 熱重載 + 資源最佳化 |

### 🌐 整體系統架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                    開發者本機環境                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   VS Code   │    │    Git      │    │   Docker    │    │
│  │   統一設定   │◄───┤   保護策略   │◄───┤   Desktop   │    │
│  │             │    │             │    │             │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│         │                   │                   │          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │  個人配置    │    │  環境檢查    │    │  容器編排    │    │
│  │  Override   │    │  腳本       │    │  Compose    │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Docker 容器環境                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   Nginx     │    │   Flask     │    │   MySQL     │    │
│  │   1.29.3    │◄───┤   3.1.2     │◄───┤   8.0       │    │
│  │             │    │   Python    │    │             │    │
│  │   :80       │    │   3.12+     │    │   :3306     │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│         │                   │                   │          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   反向代理   │    │   應用程式   │    │   資料持久   │    │
│  │   靜態資源   │    │   熱重載    │    │   備份恢復   │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Phase 1: 開發環境設計

### 📋 配置分離架構

#### 三層配置體系
```yaml
# 層級 1: 核心配置 (團隊共享)
docker-compose.yml           # 🔒 不可修改
.vscode/settings.json        # 🔒 團隊統一
.gitignore                   # 🔒 保護策略

# 層級 2: 個人適配 (本機專屬)  
docker-compose.override.yml  # ⚙️ 端口/路徑調整
.env                         # ⚙️ 敏感資訊
.vscode/settings.local.json  # ⚙️ 個人偏好

# 層級 3: 範本和工具 (指導用)
.env.example                 # 📋 配置範本
check-environment.sh         # 🔍 環境驗證
```

#### VS Code 統一開發環境

```json
// .vscode/settings.json (團隊統一)
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "88"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}

// .vscode/extensions.json (推薦擴充套件)
{
  "recommendations": [
    "ms-python.python",
    "ms-vscode.vscode-docker",
    "redhat.vscode-yaml",
    "ms-vscode.vscode-json"
  ]
}
```

### 🛡️ Git 保護策略

```bash
# 強化 .gitignore 規則
# 環境變數保護
.env
.env.local
.env.*.local

# Docker 個人配置保護  
docker-compose.override.yml
docker-compose.*.yml
!docker-compose.override.yml.example

# VS Code 個人設定保護
.vscode/settings.local.json
.vscode/*.personal.json

# Python 環境保護
venv/
__pycache__/
*.pyc
```

### 🔍 自動化環境檢查

```bash
#!/bin/bash
# check-environment.sh 設計概念

echo "🔍 AI 專案環境檢查開始..."

# 基本工具檢查 (6 項)
check_docker_version
check_python_version  
check_node_version
check_git_config

# 端口檢查 (3 項)
check_port_availability 5000 3306 8080

# 檔案檢查 (8 項)
check_env_files
check_docker_configs
check_vscode_settings

# 權限檢查 (4 項)  
check_docker_permissions
check_file_permissions

# 整合檢查 (3 項)
check_service_connectivity
check_database_connection
```

---

## 🐳 Phase 2: Docker 容器設計

### 🌐 網路架構設計

#### 自訂網路拓撲
```yaml
networks:
  ai-project-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
          gateway: 172.20.0.1

# 固定 IP 分配策略
services:
  nginx:
    networks:
      ai-project-network:
        ipv4_address: 172.20.0.10
  flask:
    networks:
      ai-project-network:
        ipv4_address: 172.20.0.20
  mysql:
    networks:
      ai-project-network:
        ipv4_address: 172.20.0.30
```

#### 端口映射策略
```yaml
# 生產環境端口配置
nginx:
  ports: ["80:80"]           # HTTP 服務
flask:
  ports: ["5000:5000"]       # 開發直連（可選）
mysql:
  ports: ["3306:3306"]       # 資料庫管理

# 個人適配範例 (override)
nginx:
  ports: ["8080:80"]         # 避免端口衝突
flask:
  ports: ["5001:5000"]       # 自訂開發端口
mysql:
  ports: ["3307:3306"]       # 避免本機 MySQL 衝突
```

### 🐋 容器設計規格

#### Nginx 1.29.3 反向代理設計
```dockerfile
# 設計重點
FROM nginx:1.29.3-alpine

# 最佳化配置
- Gzip 壓縮啟用
- 安全標頭配置  
- 靜態資源快取
- 反向代理到 Flask
- 健康檢查端點
```

```nginx
# nginx.conf 設計片段
upstream flask_app {
    server flask:5000;
}

server {
    listen 80;
    
    # 安全標頭
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    
    # 靜態資源直接服務
    location /static/ {
        alias /var/www/static/;
        expires 1y;
    }
    
    # 代理到 Flask
    location / {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Flask 3.1.2 應用設計
```dockerfile
# 多階段建置設計
FROM python:3.12-slim as base

# 開發環境階段
FROM base as development
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]

# 生產環境階段
FROM base as production  
ENV FLASK_ENV=production
RUN pip install gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

#### MySQL 8.0 資料庫設計
```yaml
# 配置重點
mysql:
  image: mysql:8.0
  environment:
    MYSQL_ROOT_PASSWORD: ${DB_PASS}
    MYSQL_DATABASE: ${DB_NAME}
    MYSQL_USER: ${DB_USER}
  command: >
    --default-authentication-plugin=mysql_native_password
    --character-set-server=utf8mb4
    --collation-server=utf8mb4_unicode_ci
    --innodb-buffer-pool-size=256M
  volumes:
    - mysql_data:/var/lib/mysql
    - ./init:/docker-entrypoint-initdb.d:ro
```

### 💾 資料持久化設計

#### 資料卷策略
```yaml
volumes:
  # 命名卷 (Docker 管理)
  mysql_data:              # 資料庫資料
    driver: local
  nginx_logs:              # Nginx 日誌
    driver: local
  flask_uploads:           # 使用者上傳檔案
    driver: local

# 綁定掛載 (開發用)
services:
  flask:
    volumes:
      - ./app:/app         # 程式碼熱重載
  nginx:
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./app/static:/var/www/static:ro
```

---

## 🔄 整合設計考量

### 📊 環境間的一致性

| 環境類型 | 開發環境 | Docker 環境 | 生產環境 |
|----------|----------|-------------|----------|
| **Python** | 3.12+ (venv) | 3.12+ (容器) | 3.12+ (容器) |
| **Flask** | 3.1.2 | 3.1.2 | 3.1.2 |
| **資料庫** | 本機/Docker | MySQL 8.0 | MySQL 8.0 |
| **Web 服務器** | Flask dev | Nginx + Flask | Nginx + Gunicorn |
| **配置管理** | .env | .env + compose | 環境變數 |

### 🔧 開發工作流程整合

```bash
# 標準開發流程
1. 環境檢查腳本驗證
   └── check-environment.sh

2. 個人環境適配
   └── docker-compose.override.yml

3. 服務啟動
   └── docker-compose up --build

4. 開發和測試
   └── 熱重載 + 即時除錯

5. 程式碼提交
   └── Git 保護策略防護
```

### 🛡️ 安全設計整合

#### 開發環境安全
- **配置分離**: 敏感資訊與程式碼分離
- **Git 保護**: 防止意外提交個人配置
- **存取控制**: VS Code 設定控制開發權限

#### Docker 環境安全
- **非 root 使用者**: 應用程式容器使用非特權用戶
- **網路隔離**: 服務間通過內部網路通信
- **最小權限**: 容器只包含必要的套件和權限
- **秘密管理**: 敏感資訊透過環境變數管理

---

## 📈 效能設計最佳化

### ⚡ 啟動效能最佳化

```yaml
# Docker 層快取最佳化
dockerfile:
  - COPY requirements.txt .    # 依賴變更較少，優先快取
  - RUN pip install -r requirements.txt
  - COPY . .                   # 程式碼變更較頻繁，後複製

# 服務啟動順序最佳化  
depends_on:
  mysql:
    condition: service_healthy
```

### 🚀 執行時效能最佳化

#### Nginx 效能配置
```nginx
# Gzip 壓縮
gzip on;
gzip_types text/plain text/css application/json;

# 快取策略
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

#### Flask 效能配置
```python
# 生產環境配置
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'pool_recycle': -1,
    'pool_pre_ping': True
}
```

#### MySQL 效能調優
```sql
-- 配置最佳化
innodb_buffer_pool_size = 256M
max_connections = 100
query_cache_size = 16M
```

---

## 🔍 監控和維護設計

### 📊 健康檢查設計

```yaml
# 各服務健康檢查
nginx:
  healthcheck:
    test: ["CMD", "nginx", "-t"]
    interval: 30s
    timeout: 10s
    retries: 3

flask:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
    interval: 30s
    timeout: 10s
    retries: 3

mysql:
  healthcheck:
    test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
    interval: 10s
    timeout: 5s
    retries: 5
```

### 📝 日誌管理設計

```yaml
# 日誌收集策略
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"

# 持久化日誌
volumes:
  - nginx_logs:/var/log/nginx
  - flask_logs:/app/logs
```

---

## 🎯 架構演進路線圖

### Phase 1 → Phase 2 演進
```
開發環境標準化 (Phase 1)
├── 配置分離架構 
├── VS Code 統一環境
├── Git 保護策略
└── 自動化檢查工具
    ↓
Docker 容器標準化 (Phase 2)  
├── 服務容器化
├── 網路架構設計
├── 資料持久化
└── 效能最佳化
    ↓
未來擴展 (Phase 3+)
├── CI/CD 管線
├── Kubernetes 編排  
├── 微服務拆分
└── 雲端部署
```

### 技術債務管理
- **向後相容**: 新架構支援現有代碼
- **漸進遷移**: 分階段遷移，降低風險
- **回滾機制**: 每個階段都有回滾選項
- **文檔同步**: 架構變更與文檔同步更新

---

*架構設計版本: 1.0*  
*最後更新: 2025年11月20日*  
*架構師: AI-project 開發團隊*
