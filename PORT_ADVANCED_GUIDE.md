# 🔌 Port 配置完整指南

本專案提供 **5 種不同的 port 管理方案**，選擇最適合你的方式！

---

## 📋 方案比較

| 方案 | 難度 | 靈活性 | 適用場景 |
|------|------|--------|----------|
| 1. 環境變數 (.env) | ⭐ 簡單 | ⭐⭐⭐ 高 | 個人開發，需要固定 port |
| 2. 自動分配 port | ⭐ 最簡單 | ⭐⭐ 中 | 不在意 port 號碼，零衝突 |
| 3. Profile 模式 | ⭐⭐ 中等 | ⭐⭐⭐ 高 | 多人團隊，預設配置 |
| 4. Override 檔案 | ⭐⭐ 中等 | ⭐⭐⭐⭐ 很高 | 團隊協作，個人化設定 |
| 5. 管理腳本 | ⭐ 簡單 | ⭐⭐⭐⭐ 很高 | 快速切換環境 |

---

## 🎯 方案 1：環境變數配置 (目前使用)

**優點**：簡單直接，適合固定 port  
**缺點**：需要手動修改 .env 檔案

### 使用步驟：

1. **編輯 `.env` 檔案：**
   ```env
   FLASK_PORT=5001
   MYSQL_PORT=3306
   PHPMYADMIN_PORT=8080
   CONTAINER_PREFIX=my-name
   ```

2. **啟動服務：**
   ```bash
   docker-compose up -d
   ```

---

## 🎲 方案 2：自動分配 Port（零衝突）

**優點**：完全不會衝突，Docker 自動找可用 port  
**缺點**：每次啟動 port 可能不同

### 使用步驟：

1. **使用自動 port 配置檔啟動：**
   ```bash
   docker-compose -f docker-compose.auto-port.yml up -d
   ```

2. **查看分配的 port：**
   ```bash
   docker ps --format "table {{.Names}}\t{{.Ports}}"
   ```

   輸出範例：
   ```
   outfit-flask        0.0.0.0:49153->5000/tcp
   outfit-phpmyadmin   0.0.0.0:49154->80/tcp
   ```

3. **訪問應用：**
   - Flask: `http://localhost:49153`（實際 port 會不同）
   - phpMyAdmin: `http://localhost:49154`

---

## 👥 方案 3：Profile 模式（團隊推薦）

**優點**：預設多個環境配置，一鍵切換  
**缺點**：需要預先定義好配置

### 使用步驟：

**開發者 A：**
```bash
docker-compose --profile dev-a up -d
# Flask: http://localhost:5001
# phpMyAdmin: http://localhost:8080
```

**開發者 B：**
```bash
docker-compose --profile dev-b up -d
# Flask: http://localhost:5002
# phpMyAdmin: http://localhost:8081
```

**開發者 C：**
```bash
docker-compose --profile dev-c up -d
# Flask: http://localhost:5003
# phpMyAdmin: http://localhost:8082
```

### 修改 profile 配置：

編輯 `docker-compose.profiles.yml` 調整 port 設定。

---

## 🔧 方案 4：Override 檔案（最靈活）

**優點**：個人化設定，不影響團隊  
**缺點**：需要理解 Docker Compose 合併機制

### 使用步驟：

1. **複製範本：**
   ```bash
   cp docker-compose.override.yml.example docker-compose.override.yml
   ```

2. **編輯 `docker-compose.override.yml`：**
   ```yaml
   version: '3.8'
   
   services:
     flask:
       ports:
         - "5002:5000"  # 你要的 port
       container_name: my-flask
   
     mysql:
       ports:
         - "3307:3306"
   
     phpmyadmin:
       ports:
         - "8081:80"
   ```

3. **啟動（會自動合併）：**
   ```bash
   docker-compose up -d
   ```

**注意**：`docker-compose.override.yml` 已加入 `.gitignore`，不會被追蹤。

---

## 🚀 方案 5：管理腳本（推薦 Windows 用戶）

**優點**：圖形化選單，最簡單  
**缺點**：需要 PowerShell

### 使用步驟：

**Windows PowerShell:**

```powershell
# 顯示所有可用配置
.\manage-ports.ps1

# 使用預設配置 A (port 5001, 8080)
.\manage-ports.ps1 dev-a

# 使用預設配置 B (port 5002, 8081)
.\manage-ports.ps1 dev-b

# 自動分配 port
.\manage-ports.ps1 auto

# 自訂 port（互動式）
.\manage-ports.ps1 custom

# 停止所有容器
.\manage-ports.ps1 stop
```

**Linux/Mac (使用 Makefile):**

```bash
# 顯示幫助
make help

# 使用預設配置 A
make dev-a

# 使用預設配置 B
make dev-b

# 查看 port 映射
make ports

# 查看日誌
make logs

# 停止服務
make down
```

---

## 🔍 檢查 Port 是否被占用

### Windows PowerShell:
```powershell
# 檢查特定 port
netstat -ano | findstr :5001

# 找出占用 port 的程式
Get-Process -Id (Get-NetTCPConnection -LocalPort 5001).OwningProcess
```

### Linux/Mac:
```bash
# 檢查特定 port
lsof -i :5001

# 或使用 netstat
netstat -tuln | grep 5001
```

---

## 🎯 選擇建議

### 個人開發：
- **方案 1 (環境變數)** - 簡單直接
- **方案 2 (自動分配)** - 不在意 port 號碼

### 團隊協作：
- **方案 3 (Profile)** - 統一預設配置
- **方案 4 (Override)** - 最靈活，不互相影響
- **方案 5 (腳本)** - 最方便，適合初學者

### 頻繁切換環境：
- **方案 5 (管理腳本)** - 一鍵切換

---

## 🚨 Port 衝突排查

### 如果遇到 port 衝突：

1. **檢查哪個程式占用 port：**
   ```powershell
   # Windows
   netstat -ano | findstr :5001
   ```

2. **解決方法：**
   - **方法 A**：關閉占用 port 的程式
   - **方法 B**：換一個 port
   - **方法 C**：使用方案 2（自動分配）

3. **快速測試可用 port：**
   ```powershell
   # 測試 port 5001-5010
   5001..5010 | ForEach-Object {
       $port = $_
       $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
       if (-not $connection.TcpTestSucceeded) {
           Write-Host "Port $port 可用" -ForegroundColor Green
       }
   }
   ```

---

## 📝 常見問題

### Q: 我應該選哪個方案？
**A:** 
- 新手/個人：方案 1 或 5
- 團隊：方案 3 或 4
- 不想管 port：方案 2

### Q: 可以同時運行多個實例嗎？
**A:** 可以！使用方案 3 (Profile) 或設定不同的 `CONTAINER_PREFIX`。

### Q: Port 修改後需要重建容器嗎？
**A:** 不用，只需要：
```bash
docker-compose down
docker-compose up -d
```

### Q: 如何查看當前使用的 port？
**A:**
```bash
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

---

## 💡 最佳實踐

1. **團隊協作**：使用方案 3 或 4，統一規範
2. **個人開發**：使用方案 1 或 5，簡單高效
3. **臨時測試**：使用方案 2，零衝突
4. **生產環境**：使用固定 port（方案 1），便於監控

---

## 🔗 相關檔案

- `docker-compose.yml` - 主配置檔（方案 1）
- `docker-compose.auto-port.yml` - 自動分配 port（方案 2）
- `docker-compose.profiles.yml` - Profile 模式（方案 3）
- `docker-compose.override.yml.example` - Override 範本（方案 4）
- `manage-ports.ps1` - PowerShell 管理腳本（方案 5）
- `Makefile` - Linux/Mac 管理腳本（方案 5）
