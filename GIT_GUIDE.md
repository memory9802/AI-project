# 📚 Git 版本管理完整指南

> **統整文檔**: 包含 Git 工作流程、分支管理、分支整理等所有版本控制相關內容  
> **更新日期**: 2025年11月26日

---

## 📖 目錄

1. [當前分支架構](#當前分支架構)
2. [日常 Git 工作流程](#日常-git-工作流程)
3. [常用 Git 指令](#常用-git-指令)
4. [分支整理記錄](#分支整理記錄)
5. [衝突解決](#衝突解決)
6. [緊急情況處理](#緊急情況處理)

---

## 🌳 當前分支架構

### 分支說明

```
✅ main (穩定版本)
   └── 基於 openspec 的優化架構
   └── 用途: 生產環境,不直接修改

✅ develop (日常開發) ← 所有人都在這裡工作
   ├── 包含爬蟲 pipeline
   ├── 包含前端頁面
   ├── 包含資料庫腳本
   └── 包含完整文檔

✅ main-old-backup (備份)
   └── 舊 main 的完整備份,僅供參考

📦 參考分支 (可選保留)
   ├── crawler_detection (已合併到 develop)
   ├── frontend (已合併到 develop)
   ├── system (Windows 相容性參考)
   └── openspec (原始架構參考)
```

### ⚠️ 重要規則

1. **所有開發都在 develop** - 不要直接修改 main
2. **統一命名規範** - 使用小寫+底線 (例: `feature_user_login`)
3. **不使用特殊符號** - 避免 `&`, `-`, 大小寫混合

---

## 🚀 日常 Git 工作流程

### 情境 1: 開始新的一天

```bash
# 1. 切換到 develop
git checkout develop

# 2. 獲取最新代碼
git pull origin develop

# 3. 查看狀態
git status

# 4. 開始開發...
```

### 情境 2: 提交代碼

```bash
# 1. 查看修改
git status
git diff

# 2. 添加修改
git add .
# 或針對特定檔案
git add app/app.py init/outfit_db.sql

# 3. 提交
git commit -m "feat: 新增用戶登入功能"

# 4. 推送
git push origin develop
```

### 情境 3: 開發新功能 (建議)

```bash
# 1. 從 develop 創建新分支
git checkout develop
git pull origin develop
git checkout -b feature_user_profile

# 2. 開發...
git add .
git commit -m "feat: 新增用戶個人資料頁面"

# 3. 合併回 develop
git checkout develop
git pull origin develop
git merge feature_user_profile

# 4. 推送
git push origin develop

# 5. 刪除功能分支 (可選)
git branch -d feature_user_profile
```

---

## 📝 常用 Git 指令

### 基礎指令

```bash
# 查看狀態
git status

# 查看分支
git branch -a

# 查看提交歷史
git log --oneline -10
git log --oneline --graph -10  # 圖形化

# 查看差異
git diff                        # 查看未暫存的修改
git diff --staged              # 查看已暫存的修改
git diff main develop          # 比較兩個分支
```

### 分支操作

```bash
# 切換分支
git checkout develop

# 創建新分支
git checkout -b feature_new_page

# 重命名分支
git branch -m old_name new_name

# 刪除本地分支
git branch -d branch_name       # 安全刪除
git branch -D branch_name       # 強制刪除

# 刪除遠端分支
git push origin :branch_name
# 或
git push origin --delete branch_name
```

### 同步操作

```bash
# 獲取遠端更新 (不合併)
git fetch origin

# 獲取所有分支
git fetch --all

# 獲取並合併
git pull origin develop

# 推送到遠端
git push origin develop

# 清理已刪除的遠端分支引用
git fetch --prune
```

### 提交管理

```bash
# 修改最後一次提交訊息
git commit --amend -m "新的提交訊息"

# 查看某個提交的詳細內容
git show commit_hash

# 查看檔案的修改歷史
git log --follow -- path/to/file

# 查看誰修改了哪一行 (blame)
git blame path/to/file
```

---

## 📊 分支整理記錄

### 2025年11月26日 完成

#### 執行內容

1. **分支重命名**
   - `Crawler&Detection` → `crawler_detection`
   - `Jinja` → `jinja_old`

2. **刪除無用分支**
   - ❌ `jinja-test` (測試分支)
   - ❌ `integrate-crawler-db` (有錯誤)

3. **建立新架構**
   - ✅ 用 `openspec` 覆蓋 `main`
   - ✅ 創建 `develop` 分支
   - ✅ 合併 `crawler_detection` 到 `develop`
   - ✅ 合併 `frontend` 到 `develop`
   - ✅ 備份舊 `main` 到 `main-old-backup`

#### 成果

- ✅ 統一分支命名規範 (小寫+底線)
- ✅ 清晰的 main/develop 架構
- ✅ 所有功能整合到 develop
- ✅ 完整的備份保留

---

## 🔧 衝突解決

### 情境 1: Pull 時發生衝突

```bash
# 拉取時發生衝突
git pull origin develop
# CONFLICT (content): Merge conflict in app/app.py

# 1. 查看衝突檔案
git status

# 2. 打開衝突檔案,會看到:
<<<<<<< HEAD
你的代碼
=======
遠端的代碼
>>>>>>> origin/develop

# 3. 手動編輯,保留需要的代碼

# 4. 標記為已解決
git add app/app.py

# 5. 完成合併
git commit -m "解決衝突: 合併 app.py 的修改"

# 6. 推送
git push origin develop
```

### 情境 2: 合併分支時衝突

```bash
git merge feature_branch
# CONFLICT...

# 解決方法同上
# 1. 查看衝突
git status

# 2. 編輯檔案解決衝突

# 3. 添加並提交
git add .
git commit -m "merge: 合併 feature_branch 並解決衝突"
```

### 衝突解決原則

#### 資料庫衝突
```bash
# ⚠️ 不要手動編輯 SQL 檔案!

# 選項 A: 使用遠端版本
git checkout --theirs init/outfit_db_with_data.sql
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

# 選項 B: 使用本地版本
git checkout --ours init/outfit_db_with_data.sql

# 選項 C: 合併兩者
# 1. 使用遠端版本
git checkout --theirs init/outfit_db_with_data.sql
# 2. 匯入資料庫
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql
# 3. 執行本地的腳本 (重新匯入資料)
python3 pipeline/05_database_import.py
# 4. 重新匯出
./scripts/export_database.sh
```

#### 代碼衝突

**保留規則:**
- 功能代碼: 兩邊都保留,合併功能
- 配置檔案: 保留較新的版本
- 文檔: 合併內容

---

## 🆘 緊急情況處理

### 情境 1: 誤刪檔案

```bash
# 查看刪除記錄
git log --diff-filter=D --summary

# 恢復已刪除的檔案
git checkout HEAD -- path/to/file

# 從特定提交恢復
git checkout commit_hash -- path/to/file
```

### 情境 2: 想撤銷最後一次提交

```bash
# 保留修改,只撤銷提交
git reset --soft HEAD~1

# 撤銷提交和暫存,保留修改
git reset --mixed HEAD~1

# 完全撤銷 (危險!)
git reset --hard HEAD~1
```

### 情境 3: 想放棄本地所有修改

```bash
# 放棄所有未提交的修改
git reset --hard HEAD

# 刪除所有未追蹤的檔案
git clean -fd

# 組合使用 (完全重置)
git reset --hard HEAD && git clean -fd
```

### 情境 4: Push 錯了想撤回

```bash
# ⚠️ 只在自己的分支使用!
# ⚠️ 不要在 main/develop 使用!

# 1. 本地回退
git reset --hard HEAD~1

# 2. 強制推送
git push origin branch_name --force
```

### 情境 5: 不小心在 main 修改了

```bash
# 1. 暫存修改
git stash

# 2. 切換到 develop
git checkout develop

# 3. 恢復修改
git stash pop
```

### 情境 6: 找回"丟失"的提交

```bash
# 查看所有操作記錄 (最近 90 天)
git reflog

# 會看到:
# a1b2c3d HEAD@{0}: commit: 最新提交
# d4e5f6g HEAD@{1}: commit: 之前的提交
# ...

# 恢復到特定狀態
git reset --hard HEAD@{1}
```

---

## 📋 Commit Message 規範

### 格式

```
<type>: <subject>

<body>
```

### Type 類型

- `feat`: 新功能
- `fix`: 修復 bug
- `docs`: 文檔更新
- `style`: 代碼格式 (不影響功能)
- `refactor`: 重構
- `test`: 測試相關
- `chore`: 其他修改

### 範例

```bash
# 好的 commit message
git commit -m "feat: 新增用戶登入功能"
git commit -m "fix: 修復資料庫連接錯誤"
git commit -m "docs: 更新 README.md"

# 詳細的 commit message
git commit -m "feat: 新增用戶登入功能

- 實作登入 API (/api/login)
- 新增 bcrypt 密碼驗證
- 新增 session 管理
- 更新前端登入表單
"
```

---

## 🎯 最佳實踐

### ✅ 推薦做法

1. **經常 pull** - 每天開始工作前
2. **小步提交** - 完成一個小功能就提交
3. **清楚的訊息** - 說明做了什麼
4. **測試後提交** - 確保代碼可運行
5. **同步資料庫** - 修改資料庫後通知組員

### ❌ 避免做法

1. ❌ 直接修改 main 分支
2. ❌ 累積大量修改才提交
3. ❌ Commit message 寫 "update" "fix"
4. ❌ 未測試就推送
5. ❌ 忽略衝突直接覆蓋

---

## 🔗 相關文檔

- **資料庫同步**: 參考 `docs/DATABASE_GUIDE.md`
- **爬蟲資料上傳**: 參考 `docs/CRAWLER_GUIDE.md`
- **團隊協作**: 參考 `docs/TEAM_GUIDE.md`
- **快速開始**: 參考主目錄 `QUICK_START.md`

---

**更新日期:** 2025年11月26日  
**維護人:** liaoyiting
