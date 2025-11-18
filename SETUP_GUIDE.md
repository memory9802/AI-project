# 🚀 多設備環境設定指南

本專案已配置完整的環境隔離機制，確保在不同設備上運行時不會發生衝突。

## 📦 快速開始

### 方法 1：使用自動設定腳本（推薦）

**Windows PowerShell:**
```powershell
.\setup-env.ps1
```

腳本會引導你輸入：
- API Keys (Gemini/Groq/DeepSeek)
- Port 設定 (Flask/MySQL/phpMyAdmin)
- 容器名稱前綴（可選）

### 方法 2：手動設定

1. **複製範本檔案：**
   ```bash
   cp .env.example .env
   ```

2. **編輯 `.env` 檔案：**
   ```env
   # API Keys
   LLM_API_KEY=你的_Gemini_Key
   GROQ_API_KEY=你的_Groq_Key
   DEEPSEEK_API_KEY=你的_DeepSeek_Key
   
   # Port 設定（根據你的設備調整）
   FLASK_PORT=5001
   MYSQL_PORT=3306
   PHPMYADMIN_PORT=8080
   
   # 容器前綴（可選，用你的名字或代號）
   CONTAINER_PREFIX=ian
   ```

3. **啟動服務：**
   ```bash
   docker-compose up -d
   ```

## 🔧 多設備協作建議

### 團隊成員 Port 分配範例

| 成員 | Flask | MySQL | phpMyAdmin | 容器前綴 |
|------|-------|-------|------------|----------|
| 開發者A | 5001 | 3306 | 8080 | dev-a |
| 開發者B | 5002 | 3307 | 8081 | dev-b |
| 開發者C | 5003 | 3308 | 8082 | dev-c |

### 設定範例

**開發者 A 的 .env：**
```env
FLASK_PORT=5001
MYSQL_PORT=3306
PHPMYADMIN_PORT=8080
CONTAINER_PREFIX=dev-a
```

**開發者 B 的 .env：**
```env
FLASK_PORT=5002
MYSQL_PORT=3307
PHPMYADMIN_PORT=8081
CONTAINER_PREFIX=dev-b
```

## 🛡️ 環境隔離機制

本專案使用以下機制確保環境隔離：

### 1. **Port 自訂**
- 透過 `.env` 設定不同 port
- 避免多個實例同時運行時的 port 衝突

### 2. **容器名稱前綴**
- 使用 `CONTAINER_PREFIX` 區分容器
- 容器名稱格式：`{PREFIX}-flask`, `{PREFIX}-mysql`, `{PREFIX}-phpmyadmin`
- 允許同一台機器運行多個實例

### 3. **獨立 Volume**
- MySQL 資料：`{PREFIX}_mysql_data`
- 對話記錄：`{PREFIX}_conversations`
- 每個實例的資料完全隔離

### 4. **Git 忽略**
- `.env` 檔案不會被追蹤
- 每個開發者可以有自己的設定

## 🔍 常見問題

### Q1: 如何檢查 port 是否被占用？

**Windows:**
```powershell
netstat -ano | findstr :5001
```

**Linux/Mac:**
```bash
lsof -i :5001
```

### Q2: 如何查看當前運行的容器？

```bash
docker ps
```

### Q3: 如何停止並移除所有容器？

```bash
docker-compose down
```

### Q4: 如何重新啟動服務？

```bash
docker-compose restart
```

### Q5: 如果 port 衝突怎麼辦？

1. 修改 `.env` 中的 port 設定
2. 重啟容器：
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Q6: 如何清除所有資料重新開始？

```bash
# 停止並移除容器
docker-compose down

# 移除 volumes（會刪除資料庫和對話記錄）
docker volume rm $(docker volume ls -q | grep outfit)

# 重新啟動
docker-compose up -d
```

## 📝 檢查清單

在新設備上設定環境時，請確認：

- [ ] 已安裝 Docker 和 Docker Compose
- [ ] 已複製 `.env.example` 為 `.env`
- [ ] 已填入有效的 API Keys
- [ ] Port 設定不與其他服務衝突
- [ ] 已設定容器前綴（如果需要）
- [ ] 執行 `docker-compose up -d`
- [ ] 訪問 `http://localhost:{FLASK_PORT}` 確認運行

## 🌐 服務連結

啟動後可訪問：

- **Flask 應用**: `http://localhost:{FLASK_PORT}`
- **phpMyAdmin**: `http://localhost:{PHPMYADMIN_PORT}`
  - 用戶名：`root`
  - 密碼：`rootpassword`

## 🔐 安全提醒

- ⚠️ **絕對不要** 將 `.env` 檔案上傳到 Git
- ⚠️ **絕對不要** 在公開場合分享 API Keys
- ⚠️ 定期更換 API Keys
- ⚠️ 生產環境請使用更安全的密碼

## 💡 提示

- 使用容器前綴可以在同一台機器運行多個獨立實例
- 建議團隊內部統一 port 分配規則
- 定期備份 Docker volumes 中的重要資料
