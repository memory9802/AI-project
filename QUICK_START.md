# 🚀 快速開始指南

> **5 分鐘啟動專案** - 給第一次使用的組員或每日快速啟動

---

## 📖 目錄

1. [一分鐘檢查](#一分鐘檢查)
2. [首次設定](#首次設定)
3. [每日啟動](#每日啟動)
4. [常用指令](#常用指令)
5. [緊急救援](#緊急救援)

---

## ✅ 一分鐘檢查

### 確認你已經有這些

```bash
# 1. Docker Desktop 正在運行?
docker --version
# 應該顯示版本號

# 2. Git 已設定?
git config --global user.name
git config --global user.email
# 應該顯示你的名字和 Email

# 3. Python 3.12+?
python3 --version
# 應該 >= 3.12

# 4. 在專案資料夾內?
pwd
# 應該看到 ...AI-project-crawler-test
```

✅ **全部通過** → 跳到 [每日啟動](#每日啟動)  
❌ **有失敗** → 繼續看 [首次設定](#首次設定)

---

## 🎯 首次設定

### macOS 使用者

```bash
# 1. 安裝 Homebrew (如果還沒有)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 安裝必要軟體
brew install git python@3.12 docker

# 3. 下載專案
git clone https://github.com/memory9802/AI-project.git
cd AI-project

# 4. 切換到開發分支
git checkout develop

# 5. 啟動 Docker Desktop (在應用程式裡打開)
open -a Docker
# 等待右上角 Docker 圖示變綠色

# 6. 啟動資料庫容器
docker-compose up -d

# 7. 匯入資料庫
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db.sql

# 8. 測試
python3 app/app.py
# 訪問 http://localhost:5000
```

### Windows 使用者

```powershell
# 1. 安裝 Chocolatey (以管理員身份執行 PowerShell)
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 2. 安裝必要軟體
choco install git python312 docker-desktop

# 3. 重啟電腦 (重要!)
Restart-Computer

# 4. 下載專案
git clone https://github.com/memory9802/AI-project.git
cd AI-project

# 5. 切換到開發分支
git checkout develop

# 6. 啟動 Docker Desktop (從開始選單啟動,等待完成)

# 7. 啟動資料庫容器
docker-compose up -d

# 8. 匯入資料庫
Get-Content init\outfit_db.sql | docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db

# 9. 測試
python app\app.py
# 訪問 http://localhost:5000
```

### 驗證設定成功

```bash
# 檢查資料庫有資料
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "SELECT COUNT(*) FROM items;"
# 應該顯示數字 (例如 49707)

# 如果顯示數字 → ✅ 設定成功!
# 如果錯誤 → 查看下面的「緊急救援」
```

---

## ☀️ 每日啟動

### 早上開始工作

```bash
# 1. 進入專案資料夾
cd ~/Desktop/AI-project-crawler-test
# 或 cd 你的專案路徑

# 2. 啟動 Docker
docker-compose up -d

# 3. 獲取最新代碼
git pull origin develop

# 4. 如果有人更新資料庫,同步資料
# (檢查群組訊息,如果有人發「📢 資料庫已更新」)
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

# 5. 啟動開發伺服器
python3 app/app.py

# 6. 開始開發! 💻
# 訪問 http://localhost:5000
```

### 下班前提交

```bash
# 1. 查看修改了什麼
git status

# 2. 如果只改了代碼
git add .
git commit -m "feat: 你做了什麼功能"
git push origin develop

# 3. 如果有改資料庫
./scripts/export_database.sh
git add init/outfit_db_with_data.sql
git commit -m "更新資料庫: 說明你加了什麼"
git push origin develop

# 4. 在群組通知大家
```

---

## 🛠️ 常用指令

### Git 基礎指令

```bash
# 查看當前狀態
git status

# 查看修改內容
git diff

# 獲取最新代碼
git pull origin develop

# 提交代碼
git add .
git commit -m "說明你做了什麼"
git push origin develop

# 查看提交歷史
git log --oneline

# 放棄所有本地修改 (危險!)
git reset --hard HEAD
```

### Docker 常用指令

```bash
# 啟動容器
docker-compose up -d

# 停止容器
docker-compose down

# 查看運行中的容器
docker ps

# 查看容器日誌
docker logs outfit-mysql

# 進入容器內部
docker exec -it outfit-mysql bash

# 重啟容器
docker-compose restart
```

### 資料庫常用指令

```bash
# 連接資料庫
docker exec -it outfit-mysql mysql -uroot -prootpassword outfit_db

# 執行 SQL 查詢
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "SELECT COUNT(*) FROM users;"

# 匯出資料庫
./scripts/export_database.sh

# 匯入資料庫
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

# 查看所有資料表
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "SHOW TABLES;"
```

### 測試帳號

| 用戶名 | 密碼 | 說明 |
|--------|------|------|
| admin | admin123 | 管理員 |
| demo | demo123 | 展示用 |
| test | test123 | 測試用 |

---

## 🆘 緊急救援

### 問題 1: Docker 無法啟動

```bash
# 解決方法
1. 確認 Docker Desktop 正在運行 (查看右上角/右下角圖示)
2. 如果沒有運行,手動打開 Docker Desktop
3. 等待圖示變成綠色
4. 再執行: docker-compose up -d
```

### 問題 2: 資料庫連接失敗

```bash
# 解決方法
# 1. 檢查容器
docker ps | grep outfit-mysql

# 2. 如果沒看到,重啟
docker-compose down
docker-compose up -d

# 3. 重新匯入
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db.sql
```

### 問題 3: Git push 被拒絕

```bash
# 解決方法
# 1. 先拉取遠端代碼
git pull origin develop

# 2. 如果有衝突,查看衝突檔案
git status

# 3. 手動編輯衝突檔案 (打開檔案,刪除 <<<< ==== >>>> 標記)

# 4. 標記為已解決
git add <衝突檔案>

# 5. 完成合併
git commit -m "解決衝突"

# 6. 推送
git push origin develop
```

### 問題 4: Python 模組找不到

```bash
# 解決方法
# 1. 建立虛擬環境 (只需執行一次)
python3 -m venv venv

# 2. 啟動虛擬環境
source venv/bin/activate  # macOS
# venv\Scripts\Activate    # Windows

# 3. 安裝依賴
pip install -r app/requirements.txt

# 4. 再次運行
python3 app/app.py
```

### 問題 5: 端口被佔用

```bash
# 解決方法 (macOS)
# 1. 找出佔用 5000 端口的進程
lsof -i :5000

# 2. 殺掉該進程
kill -9 <PID>

# 解決方法 (Windows)
# 1. 找出佔用 5000 端口的進程
netstat -ano | findstr :5000

# 2. 殺掉該進程
taskkill /PID <PID> /F
```

### 問題 6: 不小心把 main 刪除了

```bash
# 解決方法
# 1. 不要慌! Git 有保護機制
git reflog

# 2. 找到刪除前的 commit (例如 abc1234)
git checkout -b main abc1234

# 3. 推送回去
git push origin main
```

### 問題 7: 本地代碼全亂了

```bash
# 解決方法 (慎用! 會失去所有本地修改)
# 1. 放棄所有本地修改
git reset --hard origin/develop

# 2. 刪除未追蹤的檔案
git clean -fd

# 3. 重新拉取
git pull origin develop
```

---

## 📚 更多幫助

遇到問題? 查看詳細文檔:

- **Git 操作**: 參考主目錄 `GIT_GUIDE.md`
- **資料庫同步**: 參考 `docs/DATABASE_GUIDE.md`
- **爬蟲使用**: 參考 `docs/CRAWLER_GUIDE.md`
- **團隊協作**: 參考 `docs/TEAM_GUIDE.md`
- **測試帳號**: 參考 `docs/TEST_ACCOUNTS.md`

或直接在群組詢問! 🙋‍♂️

---

## 🎯 記得

1. ☀️ **每天早上**: `git pull origin develop`
2. 🌙 **每天下班**: `git push origin develop`
3. 📢 **改了資料庫**: 通知大家
4. 🆘 **遇到問題**: 立即詢問

---

**最後更新:** 2025年11月26日  
**維護人:** liaoyiting
