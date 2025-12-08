# Docker 建構最佳實踐指南

## 🎯 核心原則

### 1. **確保每次都使用最新配置**
- ✅ 使用 `--no-cache` 重建
- ✅ 先刪除 volumes (`-v`)
- ✅ 清理舊 images

### 2. **init 目錄結構規範**
```
init/
├── 00_init_with_data.sql    ✅ 主要資料檔 (會被執行)
├── 01_schema_only.sql        ✅ 備用結構檔 (會被執行)
├── 03_modify_tables.sql      ✅ 額外修改 (會被執行)
├── archived/                 📦 備份檔案 (不會被複製)
│   └── *.sql.backup
├── scripts/                  🔧 工具腳本 (不會被複製)
│   ├── *.py
│   ├── *.sh
│   ├── *.json
│   └── *.txt
└── docs/                     📚 文件 (不會被複製)
    └── *.md
```

**重要**: Docker 只會複製 `init/*.sql`,子目錄會被自動排除!

---

## 🔧 常用命令

### **完全清理重建** (推薦)
```bash
./rebuild-clean.sh
```

### **手動步驟**
```bash
# 1. 停止並刪除所有
docker-compose down -v
docker rmi stylerec-mysql stylerec-flask
docker volume rm stylerec_mysql_data

# 2. 重新建置 (no-cache)
docker-compose build --no-cache mysql
docker-compose build --no-cache

# 3. 啟動
docker-compose up -d

# 4. 等待初始化
sleep 45

# 5. 驗證
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "DESCRIBE items;"
```

### **快速重啟** (僅當 SQL 檔案未變更時)
```bash
docker-compose down
docker-compose up -d
```

---

## ⚠️ 常見問題

### **問題 1: Items 表還是舊結構 (15 個欄位)**
**原因**: Docker volume 保留了舊資料
**解決**:
```bash
docker-compose down -v  # -v 會刪除 volumes
docker-compose build --no-cache mysql
docker-compose up -d
```

### **問題 2: SQL 檔案修改後沒有生效**
**原因**: Docker image 層快取
**解決**:
```bash
docker-compose build --no-cache mysql  # 強制重建
```

### **問題 3: 資料庫初始化失敗 (Column count mismatch)**
**原因**: INSERT 語句欄位數與表結構不符
**檢查**:
```bash
docker logs outfit-mysql | grep ERROR
```
**解決**:
1. 確認 `00_init_with_data.sql` 的 INSERT 語句欄位數
2. 確認與 CREATE TABLE 的欄位數一致
3. 執行 `python init/scripts/fix_insert_columns.py`

### **問題 4: Docker 讀到子目錄的舊檔案**
**原因**: 舊版 `Dockerfile.mysql` 使用 `COPY ./init /docker-entrypoint-initdb.d/`
**解決**: 已修正為 `COPY ./init/*.sql /docker-entrypoint-initdb.d/`

---

## 📋 驗證清單

每次重建後執行:

```bash
# ✅ 1. 檢查容器狀態
docker-compose ps

# ✅ 2. 檢查 items 表結構 (應該是 12 個欄位)
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db \
  -e "DESCRIBE items;"

# ✅ 3. 檢查資料量
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db \
  -e "SELECT COUNT(*) FROM items; SELECT COUNT(*) FROM users;"

# ✅ 4. 檢查 price 欄位類型 (應該是 DECIMAL(10,2))
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db \
  -e "SHOW COLUMNS FROM items LIKE 'price';"

# ✅ 5. 測試 Flask 應用
curl http://localhost:5001/

# ✅ 6. 測試推薦 API
curl -X POST http://localhost:5001/recommend \
  -H "Content-Type: application/json" \
  -d '{"message":"測試"}'
```

---

## 🚀 最佳實踐

### **1. 修改 SQL 檔案後**
```bash
./rebuild-clean.sh
```

### **2. 修改 Python 程式碼後**
```bash
docker-compose restart flask
# 或
docker-compose build --no-cache flask && docker-compose up -d
```

### **3. 修改 .env 檔案後**
```bash
docker-compose down
docker-compose up -d
```

### **4. 日常開發**
- 不要直接修改 Docker 容器內的檔案
- 修改本地檔案後重建
- 使用 `docker logs` 查看錯誤

### **5. 提交前檢查**
```bash
# 確保 init 目錄乾淨
ls init/*.sql  # 應該只有 SQL 檔案

# 確保 .gitignore 正確
git status  # 不應該有 .env, venv/, __pycache__ 等

# 測試重建流程
./rebuild-clean.sh
```

---

## 📦 Dockerfile.mysql 說明

### **舊版問題**
```dockerfile
COPY ./init /docker-entrypoint-initdb.d/  # ❌ 複製整個目錄
```
會複製所有檔案,包括:
- `.py` 腳本
- `.md` 文件
- `.backup` 備份
- 子目錄內容

### **新版改進**
```dockerfile
COPY ./init/*.sql /docker-entrypoint-initdb.d/  # ✅ 只複製 SQL
```
只複製頂層 SQL 檔案,排除:
- 子目錄 (`scripts/`, `archived/`, `docs/`)
- 非 SQL 檔案

---

## 🔍 除錯技巧

### **查看容器內檔案**
```bash
docker exec outfit-mysql ls -lh /docker-entrypoint-initdb.d/
```

### **查看 MySQL 初始化日誌**
```bash
docker logs outfit-mysql | grep -E "running|ERROR|Note"
```

### **進入容器手動執行 SQL**
```bash
docker exec -it outfit-mysql bash
mysql -uroot -prootpassword outfit_db
DESCRIBE items;
SELECT COUNT(*) FROM items;
```

### **檢查 volume 內容**
```bash
docker volume inspect stylerec_mysql_data
```

### **完全重置環境**
```bash
docker system prune -a --volumes -f
./rebuild-clean.sh
```

---

## 📝 更新記錄

### v2.0 (2025-12-08)
- ✅ 修正 `Dockerfile.mysql`: 只複製 `*.sql` 檔案
- ✅ 整理 init 目錄結構: 子目錄隔離
- ✅ 創建 `rebuild-clean.sh` 自動化腳本
- ✅ 優化 build cache 策略
- ✅ 添加完整驗證流程

### v1.0 (2025-12-03)
- 初始版本
- 使用 `COPY ./init /docker-entrypoint-initdb.d/`
