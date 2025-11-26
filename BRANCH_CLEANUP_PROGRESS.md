# 🎯 分支整理進度追蹤

**執行日期:** 2025年11月26日  
**執行人:** liaoyiting  
**目標:** 統一分支命名,整理成 main/develop 架構

---

## ✅ Phase 0: 分支重命名 (已完成)

### 0.1 統一命名規範 ✅
**問題:** 分支名稱有特殊符號 (&) 和不一致的命名方式
**解決:** 全部改用 小寫 + 底線

| 舊名稱 | 新名稱 | 狀態 |
|--------|--------|------|
| `Crawler&Detection` | `crawler_detection` | ✅ 已重命名並推送 |
| `Jinja` | `jinja_old` | ✅ 已重命名並推送 |
| `jinja-test` | *(已刪除)* | ✅ 已刪除 |
| `integrate-crawler-db` | *(已刪除)* | ✅ 已刪除 |
| `frontend` | `frontend` | ✅ 已符合規範 |
| `openspec` | `openspec` | ✅ 已符合規範 |
| `system` | `system` | ✅ 已符合規範 |
| `main` | `main` | ✅ 保持不變 |

### 0.2 清理結果 ✅
```
當前分支列表:
* crawler_detection  (你目前在這裡)
  jinja_old
  remotes/origin/crawler_detection
  remotes/origin/frontend
  remotes/origin/jinja_old
  remotes/origin/main
  remotes/origin/openspec
  remotes/origin/system
```

**✅ 成果:**
- 刪除了 2 個無用分支 (`jinja-test`, `integrate-crawler-db`)
- 重命名了 2 個有問題的分支 (去除特殊符號)
- 現在所有分支名稱都符合規範 ✨

---

## 📋 Phase 1: 備份與準備

### 1.1 檢查當前狀態 ⬜
```bash
git fetch --all
git status
```

### 1.2 Stash 未提交的修改 ⬜
```bash
git stash save "分支整理前的備份 $(date +%Y%m%d-%H%M%S)"
git stash list
```

### 1.3 記錄當前分支狀態 ⬜
```bash
git branch -a > /tmp/branches-before-cleanup.txt
cat /tmp/branches-before-cleanup.txt
```

---

## 🚀 Phase 2: 建立新的 main (基於 openspec)

⚠️ **高風險操作 - 需要謹慎**

### 2.1 備份舊的 main ⬜
```bash
git checkout main
git checkout -b main-old-backup
git push origin main-old-backup
```

### 2.2 用 openspec 覆蓋 main ⬜
```bash
git checkout main
git reset --hard openspec
git push origin main --force
```

**⚠️ 確認項目:**
- [ ] main-old-backup 已成功推送
- [ ] 已通知所有組員暫停推送
- [ ] 確定要覆蓋 main

---

## 🌿 Phase 3: 建立 develop 分支

### 3.1 從新 main 建立 develop ⬜
```bash
git checkout main
git pull origin main
git checkout -b develop
git push origin develop
```

---

## 🔀 Phase 4: 合併功能分支

### 4.1 合併 crawler_detection ⬜
```bash
git checkout develop
git pull origin develop
git merge crawler_detection --no-ff -m "merge: 整合爬蟲、資料庫和所有文檔"
git push origin develop
```

**包含內容:**
- 完整的爬蟲 pipeline
- 資料庫結構和初始化腳本
- 所有 Git 工作流程文檔
- 資料庫同步工具

### 4.2 合併 frontend ⬜
```bash
git checkout develop
git pull origin develop
git merge frontend --no-ff -m "merge: 整合前端頁面和靜態資源"
git push origin develop
```

**包含內容:**
- 前端 HTML/CSS/JS
- 靜態資源 (圖片)

### 4.3 提取 system 的 Windows 相容性修改 ⬜
```bash
# 比較差異
git diff openspec system > /tmp/system-windows-diff.txt

# 查看差異
cat /tmp/system-windows-diff.txt

# 如果有需要的修改,手動套用到 develop
git checkout develop
# (手動編輯檔案)
git add .
git commit -m "fix: 套用 Windows 相容性修改"
git push origin develop
```

---

## 🗑️ Phase 5: 清理舊分支

### 5.1 刪除 jinja_old (已確認不需要) ⬜
```bash
# 先確認內容
git log jinja_old --oneline -10

# 確定刪除
git push origin :jinja_old
git branch -D jinja_old
```

### 5.2 保留 system 作為參考 ⬜
暫時保留,以防需要查看 Windows 相容性修改

---

## ✅ Phase 6: 驗證與測試

### 6.1 檢查分支結構 ⬜
```bash
git branch -a
```

**預期結果:**
- `main` (基於 openspec)
- `develop` (整合了 crawler_detection + frontend)
- `main-old-backup` (備份)
- `system` (保留參考)

### 6.2 測試 develop 分支 ⬜
```bash
git checkout develop
docker-compose down
docker-compose up -d

# 測試資料庫
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'items', COUNT(*) FROM items;
"

# 測試 Flask
cd app
python3 app.py
# 訪問 http://localhost:5000

# 測試爬蟲
python3 pipeline/01_crawl_uniqlo.py
```

**驗證清單:**
- [ ] Docker 容器正常啟動
- [ ] 資料庫有 50 users + 49,707 items
- [ ] Flask 應用正常運行
- [ ] 前端頁面可以訪問
- [ ] 爬蟲腳本可以執行

---

## 📢 Phase 7: 通知組員

### 7.1 更新 GitHub 預設分支 ⬜
GitHub → Settings → Branches → Default branch → 改為 `develop`

### 7.2 通知組員切換 ⬜
使用 `TEAM_NOTIFICATION_TEMPLATES.md` 的第三階段通知

**組員需要執行:**
```bash
git fetch --all
git checkout develop
git pull origin develop

# 重新匯入資料庫
docker-compose down
docker-compose up -d
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db.sql
```

---

## 📊 最終分支架構

```
main (穩定版本,基於 openspec)
  └── main-old-backup (舊 main 備份)

develop (日常開發)
  ├── 包含 crawler_detection 的所有功能
  ├── 包含 frontend 的所有頁面
  └── 包含 system 的 Windows 相容性修改

feature/* (未來的新功能分支)
bugfix/* (未來的錯誤修復分支)
```

---

## 🎉 完成檢查清單

- [x] ✅ 分支重命名完成 (去除特殊符號)
- [x] ✅ 刪除無用分支 (jinja-test, integrate-crawler-db)
- [ ] ⬜ 備份舊 main
- [ ] ⬜ 建立新 main (基於 openspec)
- [ ] ⬜ 建立 develop
- [ ] ⬜ 合併 crawler_detection
- [ ] ⬜ 合併 frontend
- [ ] ⬜ 提取 system 修改
- [ ] ⬜ 驗證所有功能
- [ ] ⬜ 通知組員切換

---

## 💾 重要備份位置

1. **Git reflog:** `git reflog` (最近 90 天的所有操作)
2. **main-old-backup:** 舊 main 的備份分支
3. **本地分支列表:** `/tmp/branches-before-cleanup.txt`
4. **系統差異:** `/tmp/system-windows-diff.txt`

---

**下一步:** 執行 Phase 2 - 建立新的 main
