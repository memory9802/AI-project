# Design: Docker/Docker Compose 環境標準化

## 架構概覽

### 🎯 設計目標
- **一致性**: 所有環境使用相同的技術棧版本
- **可重現性**: 任何地方都能快速重建相同環境
- **可擴展性**: 支援未來功能和服務擴展
- **安全性**: 遵循容器安全最佳實踐
- **效能**: 最佳化開發和生產環境效能

### 🏗️ 服務架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                        Docker Host                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   Nginx     │    │   Flask     │    │   MySQL     │    │
│  │   1.29.3    │◄───┤   3.1.2     │◄───┤   8.0       │    │
│  │             │    │   Python    │    │             │    │
│  │   Port: 80  │    │   3.12+     │    │   Port:3306 │    │
│  │             │    │   Port:5000 │    │             │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│         │                   │                   │          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   Static    │    │   App Code  │    │   Data      │    │
│  │   Files     │    │   Volume    │    │   Volume    │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 技術規格

### 🐳 容器配置

#### Nginx 1.29.3
```yaml
# 基礎映像
FROM nginx:1.29.3-alpine

# 配置特點
- Alpine Linux 基底 (輕量化)
- 反向代理到 Flask 應用
- 靜態資源直接服務
- Gzip 壓縮啟用
- 安全標頭配置
```

#### Flask 3.1.2
```yaml
# 基礎映像  
FROM python:3.12-slim

# 配置特點
- Python 3.12+ 官方映像
- Flask 3.1.2 框架
- Gunicorn WSGI 服務器
- 開發模式熱重載
- 生產模式最佳化
```

#### MySQL 8.0
```yaml
# 基礎映像
FROM mysql:8.0

# 配置特點
- 官方 MySQL 8.0 映像
- UTF-8 字符集配置
- 自動初始化腳本
- 資料持久化
- 效能調優參數
```

### 🌐 網路架構

#### 網路設計
```yaml
networks:
  ai-project-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

#### 服務 IP 分配
- **Nginx**: 172.20.0.10
- **Flask**: 172.20.0.20  
- **MySQL**: 172.20.0.30

#### 端口映射
- **外部 80** → Nginx 80 (HTTP)
- **外部 5000** → Flask 5000 (開發直連)
- **外部 3306** → MySQL 3306 (資料庫管理)

### 💾 資料卷設計

#### 持久化策略
```yaml
volumes:
  mysql_data:
    driver: local
  nginx_logs:
    driver: local  
  flask_uploads:
    driver: local
```

#### 開發綁定掛載
```yaml
# 程式碼熱重載
- ./app:/app
- ./nginx/conf.d:/etc/nginx/conf.d
- ./init:/docker-entrypoint-initdb.d
```

## 配置檔案設計

### 📝 docker-compose.yml 結構

```yaml
version: '3.8'

services:
  # Nginx 反向代理
  nginx:
    image: nginx:1.29.3-alpine
    container_name: ai-project-nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./app/static:/var/www/static:ro
      - nginx_logs:/var/log/nginx
    depends_on:
      - flask
    networks:
      ai-project-network:
        ipv4_address: 172.20.0.10
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Flask 應用
  flask:
    build:
      context: .
      dockerfile: Dockerfile
      target: development  # 或 production
    container_name: ai-project-flask
    ports:
      - "5000:5000"  # 開發環境直接存取
    volumes:
      - ./app:/app
      - flask_uploads:/app/uploads
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
      - DATABASE_URL=mysql://root:${DB_PASS}@mysql:3306/${DB_NAME}
    depends_on:
      mysql:
        condition: service_healthy
    networks:
      ai-project-network:
        ipv4_address: 172.20.0.20
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # MySQL 資料庫
  mysql:
    image: mysql:8.0
    container_name: ai-project-mysql
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init:/docker-entrypoint-initdb.d:ro
    environment:
      - MYSQL_ROOT_PASSWORD=${DB_PASS}
      - MYSQL_DATABASE=${DB_NAME}
      - MYSQL_USER=${DB_USER}
      - MYSQL_PASSWORD=${DB_PASS}
    networks:
      ai-project-network:
        ipv4_address: 172.20.0.30
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
    command: >
      --default-authentication-plugin=mysql_native_password
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_unicode_ci
      --innodb-buffer-pool-size=256M
```

### 🐋 Dockerfile 設計

```dockerfile
# 多階段建置支援開發和生產環境
FROM python:3.12-slim as base

# 系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 工作目錄
WORKDIR /app

# Python 依賴
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 開發環境階段
FROM base as development
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
COPY app/ .
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]

# 生產環境階段  
FROM base as production
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0
COPY app/ .
RUN pip install gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

### ⚙️ Nginx 配置

```nginx
# /nginx/conf.d/default.conf
upstream flask_app {
    server flask:5000;
}

server {
    listen 80;
    server_name localhost;
    
    # 安全標頭
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Gzip 壓縮
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    
    # 靜態資源
    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 代理到 Flask
    location / {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 健康檢查
    location /nginx-health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

## 環境管理

### 🔑 環境變數設計

```bash
# .env.example 更新
# 資料庫配置
DB_HOST=mysql
DB_NAME=ai_project
DB_USER=ai_user  
DB_PASS=secure_password_2024

# Flask 配置
FLASK_ENV=development
FLASK_SECRET_KEY=your-secret-key-here
FLASK_DEBUG=1

# AI 服務配置
LLM_API_KEY=your-gemini-api-key

# Docker 配置
COMPOSE_PROJECT_NAME=ai-project
```

### 🔧 個人適配支援

```yaml
# docker-compose.override.yml.example 更新
version: '3.8'

services:
  nginx:
    ports:
      - "8080:80"  # 修改端口避免衝突
      
  flask:
    ports:
      - "5001:5000"  # 修改端口避免衝突
    environment:
      - FLASK_DEBUG=0  # 關閉除錯模式
      
  mysql:
    ports:
      - "3307:3306"  # 修改端口避免衝突
    environment:
      - MYSQL_ROOT_PASSWORD=my_custom_password
```

## 安全考量

### 🛡️ 容器安全
- **非 root 用戶**: Flask 容器使用非 root 用戶運行
- **最小權限**: 容器只包含必要的套件
- **網路隔離**: 服務間透過內部網路通信
- **秘密管理**: 敏感資訊透過環境變數管理

### 🔒 資料安全
- **資料庫權限**: 建立專用的資料庫用戶
- **SSL/TLS**: 生產環境支援 HTTPS
- **備份策略**: 自動化資料備份機制
- **存取控制**: 限制對資料庫的直接存取

## 效能最佳化

### ⚡ 啟動最佳化
- **映像快取**: 利用 Docker 層快取
- **並行啟動**: 服務間依賴關係最佳化
- **資源限制**: 合理設定記憶體和 CPU 限制

### 📈 執行時最佳化
- **連接池**: 資料庫連接池配置
- **靜態資源**: Nginx 直接服務靜態檔案
- **快取策略**: 應用層和 HTTP 快取
- **監控指標**: 建立效能監控機制

---

**設計版本**: 1.0  
**最後更新**: 2025年11月20日  
**設計師**: AI-project 開發團隊