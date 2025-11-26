# 🔄 AI-Project 分支整理計畫

## 📊 現況分析

### 目前分支狀態

| 分支名稱 | 狀態 | 內容 | 處理方式 |
|---------|------|------|---------|
| **main** | ❌ 過舊 | 最舊版本,無法使用 | 🔄 用 openspec 覆蓋 |
| **Crawler&Detection** | ✅ 重要 | 爬蟲+資料庫整合 | 🔄 合併到 develop |
| **frontend** | ✅ 重要 | 前端網頁內容 | 🔄 合併到 develop |
| **openspec** | ✅ 重要 | 統一開發架構 (較新) | 🔄 作為 develop 基礎 |
| **system** | ⚠️ 次要 | 開發環境設定 (相容 Windows) | 🔄 提取 Windows 相容修改 |
| **Jinja** | ❌ 過時 | 前後端串接測試 | ❌ 刪除 |
| **jinja-test** | ❌ 測試 | 測試用 | ❌ 刪除 |
| **integrate-crawler-db** | ❌ 錯誤 | 內容有誤 | ❌ 刪除 |

---

## 🎯 目標架構

```
main (穩定版本,可 Demo)
  ← 來源: openspec (最新統一架構)
  
develop (開發分支)
  ← 基礎: openspec
  ← 合併: Crawler&Detection (爬蟲+資料庫)
  ← 合併: frontend (前端)
  ← 提取: system (Windows 相容性修改)
```

---

## 📋 執行步驟

### Phase 1: 備份與準備 ✅

```bash
# 1. 確保所有分支都已同步
git fetch --all

# 2. 備份目前的工作 (如果有未提交的修改)
git stash

# 3. 查看所有分支狀態
git branch -a
git log --all --oneline --graph --decorate
```

---

### Phase 2: 建立新的 main (基於 openspec) 🔄

```bash
# 1. 切換到 openspec 分支
git checkout openspec
git pull origin openspec

# 2. 確認 openspec 分支可以正常運行
# 測試 docker-compose up -d
# 測試 flask app

# 3. 建立臨時分支備份舊 main
git checkout main
git pull origin main
git branch main-old-backup

# 4. 用 openspec 覆蓋 main
git checkout main
git reset --hard openspec
git push origin main --force

# ⚠️ 注意: 這會覆蓋 main,請確保已備份!
```

**為什麼用 openspec 作為新 main?**
- ✅ 系統架構最新
- ✅ 統整性最高
- ✅ 有完整的 docker-compose.yml 和 app.py
- ✅ 可作為穩定的 Demo 版本

---

### Phase 3: 建立 develop 分支 🆕

```bash
# 1. 從新的 main 建立 develop
git checkout main
git pull origin main
git checkout -b develop
git push origin develop
```

---

### Phase 4: 合併重要分支到 develop 🔄

#### 4.1 合併 Crawler&Detection (爬蟲+資料庫)

```bash
git checkout develop
git pull origin develop

# 合併 Crawler&Detection
git merge origin/Crawler&Detection -m "合併爬蟲和資料庫功能"

# 如果有衝突:
# 1. 保留 Crawler&Detection 的:
#    - pipeline/ 資料夾 (爬蟲腳本)
#    - init/outfit_db_with_data.sql (資料庫)
#    - dataset/ 資料夾 (資料集)
#    - scripts/ 中的爬蟲相關腳本
#
# 2. 保留 openspec 的:
#    - docker-compose.yml (如果更新)
#    - app/app.py (主程式架構)
#    - 基礎設定檔

# 解決衝突後
git add .
git commit -m "解決 Crawler&Detection 合併衝突"
git push origin develop
```

#### 4.2 合併 frontend (前端)

```bash
git checkout develop
git pull origin develop

# 合併 frontend
git merge origin/frontend -m "合併前端網頁內容"

# 如果有衝突:
# 1. 保留 frontend 的:
#    - app/templates/ (HTML 模板)
#    - app/static/ (CSS, JS, 圖片)
#    - page/ 資料夾 (如果有)
#
# 2. 保留 develop 現有的:
#    - app/app.py (後端邏輯)
#    - 其他非前端檔案

# 解決衝突後
git add .
git commit -m "解決 frontend 合併衝突"
git push origin develop
```

#### 4.3 提取 system 的 Windows 相容性修改

```bash
git checkout develop

# 比較 system 和 openspec 的差異
git diff openspec system

# 手動檢查差異,找出 Windows 相容性修改
# 可能包括:
# - docker-compose.yml 的路徑格式
# - 腳本中的路徑分隔符
# - 編碼設定

# 如果有需要,手動複製這些修改到 develop
# 或者使用 cherry-pick 特定 commit:
git log system --oneline
git cherry-pick <commit-hash>  # 選擇 Windows 相容性修改的 commit

git push origin develop
```

---

### Phase 5: 清理不需要的分支 🗑️

```bash
# 刪除遠端分支
git push origin --delete Jinja
git push origin --delete jinja-test
git push origin --delete integrate-crawler-db

# 可選: 刪除已合併的分支 (保留一段時間作為備份)
# git push origin --delete Crawler&Detection
# git push origin --delete frontend
# git push origin --delete system

# 刪除本地分支
git branch -d Jinja
git branch -d jinja-test
git branch -d integrate-crawler-db
```

---

### Phase 6: 驗證與測試 ✅

```bash
# 1. 切換到 develop
git checkout develop
git pull origin develop

# 2. 測試 Docker 環境
docker-compose down
docker-compose up -d

# 3. 測試資料庫
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'items' as table_name, COUNT(*) as count FROM items;
"

# 預期結果:
# users: 50
# items: 49,707

# 4. 測試 Flask 應用
cd app
python3 app.py
# 訪問 http://localhost:5000

# 5. 測試爬蟲
python3 pipeline/01_crawl_uniqlo.py

# 6. 測試前端
# 打開瀏覽器訪問前端頁面
```

---

### Phase 7: 更新文檔 📝

```bash
# 更新 README.md 說明新的分支結構
# 更新 .github/ 文檔 (如果有)
# 通知組員新的工作流程

git add README.md docs/
git commit -m "更新文檔:說明新的分支架構"
git push origin develop
```

---

## 📋 執行時間表

| 階段 | 預計時間 | 風險等級 |
|------|---------|---------|
| Phase 1: 備份與準備 | 10 分鐘 | 低 |
| Phase 2: 建立新 main | 15 分鐘 | ⚠️ 高 (會覆蓋舊 main) |
| Phase 3: 建立 develop | 5 分鐘 | 低 |
| Phase 4: 合併分支 | 30-60 分鐘 | ⚠️ 中 (可能有衝突) |
| Phase 5: 清理分支 | 10 分鐘 | 低 |
| Phase 6: 驗證測試 | 20 分鐘 | 低 |
| Phase 7: 更新文檔 | 15 分鐘 | 低 |
| **總計** | **2-3 小時** | |

---

## ⚠️ 重要注意事項

### 執行前必須確認

- [ ] ✅ 所有組員都已提交他們的修改
- [ ] ✅ 所有組員都知道即將進行分支整理
- [ ] ✅ 已在本地測試過 openspec 分支可以運行
- [ ] ✅ 已備份重要資料 (特別是資料庫)
- [ ] ✅ 選擇一個沒有人在開發的時間 (晚上或週末)

### 高風險操作

1. **覆蓋 main 分支** (Phase 2)
   - ⚠️ 這會刪除舊 main 的歷史
   - ✅ 已建立 main-old-backup 備份
   - ✅ 可以透過 `git reflog` 恢復

2. **強制推送** (Phase 2)
   - ⚠️ `--force` 會覆蓋遠端分支
   - ✅ 確保沒有組員在 main 上工作

3. **合併衝突** (Phase 4)
   - ⚠️ 可能有大量衝突需要解決
   - ✅ 準備 2-3 小時處理衝突

---

## 🔄 如果出錯怎麼辦?

### 恢復舊 main

```bash
# 如果需要恢復舊 main
git checkout main
git reset --hard main-old-backup
git push origin main --force
```

### 恢復到整理前的狀態

```bash
# 使用 reflog 查看所有操作
git reflog

# 回到特定操作前
git reset --hard HEAD@{n}  # n 是 reflog 中的編號
```

---

## 📢 通知組員的訊息範本

```
🚨 重要通知:Git 分支大整理

各位組員好!

我們即將進行分支整理,請在 [日期時間] 前完成以下事項:

1️⃣ 提交所有修改
   git add .
   git commit -m "整理前保存"
   git push

2️⃣ 記錄你目前的分支
   git branch

3️⃣ [日期時間] 後請暫停開發,等待通知

整理完成後,新的分支架構:
- main: 穩定版本 (基於 openspec)
- develop: 開發分支 (整合所有功能)
- feature/*: 功能分支 (從 develop 開出)

預計整理時間: 2-3 小時

有問題請回覆!
```

---

## ✅ 整理後的最終架構

```
main (穩定版本,可 Demo)
  ├─ 來源: openspec (統一架構)
  ├─ 內容: 完整的開發環境設定
  └─ 用途: 給老師 Demo、期中/期末展示

develop (開發分支,日常工作)
  ├─ 基礎: openspec
  ├─ 包含: 爬蟲功能 (Crawler&Detection)
  ├─ 包含: 前端頁面 (frontend)
  ├─ 包含: 資料庫 (50 users + 49,707 items)
  └─ 包含: Windows 相容性修改 (system)

feature/* (功能分支,按需建立)
  └─ 從 develop 開出,完成後合併回去
```

---

## 🎯 整理後的工作流程

### 日常開發

```bash
# 每天早上
git checkout develop
git pull origin develop

# 開發新功能
git checkout -b feature/your-feature
# ... 開發 ...
git push origin feature/your-feature

# 完成後合併
git checkout develop
git merge feature/your-feature
git push origin develop
```

### 準備 Demo

```bash
# 測試 develop 分支
git checkout develop
# ... 測試所有功能 ...

# 合併到 main
git checkout main
git merge develop
git push origin main

# 建立標籤
git tag -a v1.0-midterm -m "期中 Demo"
git push origin v1.0-midterm
```

---

**準備好開始整理了嗎?請確認上述所有注意事項!** 🚀

**整理人:** liaoyiting  
**計畫建立日期:** 2025-11-26  
**預計執行日期:** ___________
