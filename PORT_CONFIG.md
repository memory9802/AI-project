# Port 設定說明

## 如何避免 Port 衝突

本專案使用環境變數來設定 port，讓不同機器可以使用不同的 port 避免衝突。

### 預設 Port
- Flask 應用：`5001`
- MySQL 資料庫：`3306`
- phpMyAdmin：`8080`

### 自訂 Port 方法

#### 方法 1：修改 `.env` 檔案（推薦）
編輯 `.env` 檔案，修改以下設定：

```env
FLASK_PORT=5001        # 改成你想要的 port，例如 5002
MYSQL_PORT=3306        # 如果 3306 被占用，改成 3307
PHPMYADMIN_PORT=8080   # 如果 8080 被占用，改成 8081
```

#### 方法 2：使用命令列設定（臨時）
在啟動時指定 port：

**Windows PowerShell:**
```powershell
$env:FLASK_PORT=5002; $env:MYSQL_PORT=3307; $env:PHPMYADMIN_PORT=8081; docker-compose up -d
```

**Linux/Mac:**
```bash
FLASK_PORT=5002 MYSQL_PORT=3307 PHPMYADMIN_PORT=8081 docker-compose up -d
```

### 常見問題

#### Q: 如何檢查 port 是否被占用？
**Windows:**
```powershell
netstat -ano | findstr :5001
```

**Linux/Mac:**
```bash
lsof -i :5001
```

#### Q: 如果 port 被占用怎麼辦？
1. 方法 1：修改 `.env` 中的 port 設定
2. 方法 2：關閉占用該 port 的程式
3. 方法 3：重啟電腦

### 應用 Port 修改後的步驟

1. 修改 `.env` 檔案中的 port
2. 重啟 Docker 容器：
   ```bash
   docker-compose down
   docker-compose up -d
   ```
3. 訪問新的網址：
   - Flask: `http://localhost:{FLASK_PORT}`
   - phpMyAdmin: `http://localhost:{PHPMYADMIN_PORT}`

### 團隊協作建議

每個團隊成員可以複製 `.env.example` 為 `.env`，並根據自己機器的情況設定不同的 port，`.env` 檔案不會被 git 追蹤，因此不會影響其他人。
