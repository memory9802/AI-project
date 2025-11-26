# 🌿 Git 分支策略圖解

## 📊 視覺化流程

```
                     main (穩定版本,給老師 demo)
                       │
                       │ ← merge (每週/demo 前)
                       │
                    develop (開發總部,日常工作)
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    feature/        feature/     feature/
    crawler         frontend      ai-rec
    (爬蟲)          (前端)        (AI)
         │             │             │
         │             │             │
     [開發中]       [開發中]       [開發中]
         │             │             │
         └─────────────┴─────────────┘
                       │
                  merge 回 develop
```

---

## 🔄 日常開發循環

```
每天早上 ☀️
    ↓
git checkout develop
git pull origin develop
    ↓
如果要開發新功能?
    ├─ 是 → git checkout -b feature/xxx
    └─ 否 → 直接在 develop 工作
    ↓
寫程式碼 💻
多次 commit
    ↓
功能完成?
    ├─ 否 → 繼續開發
    └─ 是 → 合併回 develop
           ↓
      git checkout develop
      git pull origin develop
      git merge feature/xxx
      git push origin develop
           ↓
      刪除功能分支
      git branch -d feature/xxx
           ↓
      通知組員 📢
```

---

## 📋 分支命名速查表

```
分支類型           命名格式                  範例
──────────────────────────────────────────────────────
主分支            main                     main
開發分支          develop                  develop
功能分支          feature/<功能名>         feature/crawler-uniqlo
                                          feature/frontend-login
                                          feature/ai-color-detect
修復分支          bugfix/<問題描述>        bugfix/login-error
                                          bugfix/database-charset
緊急修復          hotfix/<緊急問題>        hotfix/demo-crash
```

---

## 🎯 快速決策表

### 我該開新分支嗎?

| 情況 | 是否開分支 | 分支類型 |
|------|-----------|---------|
| 開發新的爬蟲功能 | ✅ 是 | feature/crawler-xxx |
| 開發新的前端頁面 | ✅ 是 | feature/frontend-xxx |
| 修改一個小 bug | ❌ 否 | 直接在 develop |
| 更新 README | ❌ 否 | 直接在 develop |
| 實驗性的大改動 | ✅ 是 | feature/experiment-xxx |
| Demo 前發現問題 | ✅ 是 | hotfix/demo-xxx |

---

## 🔧 常用指令速查

### 建立與切換分支

```bash
# 建立並切換到新分支
git checkout -b feature/crawler-uniqlo

# 等同於
git branch feature/crawler-uniqlo
git checkout feature/crawler-uniqlo

# 切換到已存在的分支
git checkout develop

# 查看所有分支
git branch -a
```

---

### 合併分支

```bash
# 合併 feature 到 develop
git checkout develop           # 1. 切換到目標分支
git pull origin develop        # 2. 確保最新
git merge feature/xxx          # 3. 合併
git push origin develop        # 4. 推送

# 如果有衝突
git status                     # 查看衝突檔案
# 編輯檔案解決衝突
git add <解決的檔案>
git commit -m "解決衝突"
git push origin develop
```

---

### 刪除分支

```bash
# 刪除本地分支
git branch -d feature/xxx      # 安全刪除 (已合併)
git branch -D feature/xxx      # 強制刪除 (未合併)

# 刪除遠端分支
git push origin --delete feature/xxx

# 清理遠端已刪除的分支參照
git fetch --prune
```

---

### 同步最新版本

```bash
# 更新本地所有分支資訊
git fetch origin

# 更新當前分支
git pull origin develop

# 更新並合併到功能分支
git checkout feature/your-feature
git merge develop
```

---

## ⚠️ 緊急情況處理

### 情況 1: 我 commit 到錯的分支了!

```bash
# 假設你在 develop,但應該在 feature/xxx

# 1. 記下 commit hash
git log --oneline -1
# 輸出: a1b2c3d 新增爬蟲功能

# 2. 回退這個 commit (但保留修改)
git reset --soft HEAD~1

# 3. 切換到正確分支
git checkout -b feature/crawler

# 4. 重新 commit
git add .
git commit -m "新增爬蟲功能"
```

---

### 情況 2: 我想放棄所有修改!

```bash
# ⚠️ 警告:這會刪除所有未 commit 的修改!

# 放棄所有修改
git reset --hard HEAD

# 放棄特定檔案的修改
git checkout -- app/app.py
```

---

### 情況 3: 我想回到之前的版本

```bash
# 查看歷史
git log --oneline

# 回到特定 commit (不刪除歷史)
git revert a1b2c3d

# 回到特定 commit (刪除之後的歷史,危險!)
git reset --hard a1b2c3d
```

---

## 📊 目前專案的分支清理計畫

### 現有分支狀態

```
✅ 保留:
  - main              # 主分支
  
🆕 建立:
  - develop           # 新建立的開發分支
  
🔄 合併後刪除:
  - Crawler&Detection # 合併到 develop → 刪除
  - frontend          # 合併到 develop → 刪除
  - integrate-crawler-db # 合併到 develop → 刪除
  - Jinja             # 合併到 develop → 刪除
  
❌ 直接刪除:
  - jinja-test        # 測試用,已不需要
  - openspec          # 確認後決定
  - system            # 確認後決定
```

---

### 執行腳本

```bash
#!/bin/bash
# 清理分支腳本

echo "🧹 開始清理 Git 分支..."

# 1. 建立 develop 分支
echo "📝 建立 develop 分支..."
git checkout main
git pull origin main
git checkout -b develop
git push origin develop

# 2. 合併重要分支
echo "🔄 合併 Crawler&Detection..."
git merge origin/Crawler&Detection
git push origin develop

echo "🔄 合併 frontend..."
git merge origin/frontend
# 如果有衝突,手動解決後繼續
git push origin develop

echo "🔄 合併 Jinja..."
git merge origin/Jinja
git push origin develop

# 3. 刪除已合併的遠端分支
echo "🗑️  刪除已合併的分支..."
git push origin --delete Crawler&Detection
git push origin --delete frontend
git push origin --delete integrate-crawler-db
git push origin --delete Jinja
git push origin --delete jinja-test

# 4. 清理本地分支
git branch -d Crawler&Detection
git branch -d frontend
git branch -d integrate-crawler-db
git branch -d Jinja
git branch -d jinja-test

echo "✅ 清理完成!"
echo "📋 剩餘分支:"
git branch -a
```

**使用方式:**
```bash
# 儲存為 cleanup_branches.sh
chmod +x cleanup_branches.sh
./cleanup_branches.sh
```

---

## 🎯 團隊協作規則 (一頁版)

### 每天必做

```bash
# ☀️ 早上開始工作
git checkout develop
git pull origin develop

# 🌙 晚上結束工作
git add .
git commit -m "今日進度:完成 XXX 功能"
git push origin develop  # 或 feature/xxx
```

---

### 開發新功能

```bash
# 1️⃣ 從 develop 開分支
git checkout develop
git pull origin develop
git checkout -b feature/your-feature

# 2️⃣ 開發 (多次 commit)
# ... 寫程式碼 ...
git add .
git commit -m "完成基礎架構"
# ... 繼續寫 ...
git commit -m "完成測試"

# 3️⃣ 推送 (讓組員知道)
git push origin feature/your-feature

# 4️⃣ 完成後合併
git checkout develop
git pull origin develop
git merge feature/your-feature
git push origin develop

# 5️⃣ 刪除分支
git branch -d feature/your-feature
git push origin --delete feature/your-feature

# 6️⃣ 通知組員
# 「✅ XXX 功能完成並合併到 develop」
```

---

### 同步組員更新

```bash
# 如果在 develop
git checkout develop
git pull origin develop

# 如果在 feature 分支
git checkout feature/your-feature
git merge develop  # 把 develop 的更新合併進來
```

---

### Commit Message 格式

```
✅ 好的範例:
─────────────
新增 UNIQLO 爬蟲功能
修復登入頁面的 CSS 錯誤
更新資料庫:新增 500 筆商品
重構 AI 推薦演算法
優化色彩檢測速度

❌ 不好的範例:
─────────────
更新
fix
test
aaa
123
```

---

## 🔍 診斷工具

### 檢查目前狀態

```bash
# 我在哪個分支?
git branch

# 我有什麼修改?
git status

# 我的分支和 develop 差多少?
git log develop..HEAD --oneline

# 有哪些遠端分支?
git branch -r
```

---

### 檢查分支關係

```bash
# 這個分支從哪裡來的?
git log --graph --oneline --all

# 哪些 commit 還沒合併到 develop?
git log develop..feature/xxx --oneline

# 這個分支最後修改時間
git log -1 --format="%ci" feature/xxx
```

---

## 📱 推薦工具

### GUI 工具 (視覺化)

1. **GitKraken** ⭐ (推薦新手)
   - 圖形化介面
   - 可以看到分支樹狀圖
   - 免費學生版
   - https://www.gitkraken.com/

2. **GitHub Desktop**
   - GitHub 官方工具
   - 簡單易用
   - https://desktop.github.com/

3. **SourceTree**
   - 功能強大
   - Atlassian 開發
   - https://www.sourcetreeapp.com/

### VS Code 擴充套件

1. **GitLens** ⭐
   - 顯示每行程式碼的作者和修改時間
   - 超級實用!

2. **Git Graph**
   - 視覺化分支圖

3. **Git History**
   - 瀏覽檔案歷史

---

## 💡 小技巧

### 技巧 1: 使用 alias 簡化指令

```bash
# 在 ~/.gitconfig 加入
[alias]
    st = status
    co = checkout
    br = branch
    cm = commit -m
    lg = log --oneline --graph --all

# 使用
git st        # 等於 git status
git co develop # 等於 git checkout develop
git lg        # 漂亮的 log
```

---

### 技巧 2: 暫存工作 (stash)

```bash
# 你正在 feature 分支,但需要緊急切換到 develop

# 1. 暫存目前修改
git stash

# 2. 切換分支處理緊急事項
git checkout develop
# ... 處理完畢 ...

# 3. 切回來並恢復
git checkout feature/your-feature
git stash pop
```

---

### 技巧 3: 只合併特定檔案

```bash
# 只想從 feature 分支拿特定檔案到 develop

git checkout develop
git checkout feature/xxx -- path/to/file.py
git commit -m "從 feature 分支移植檔案"
```

---

## 📚 學習路徑

### Level 1: 基礎 (必學)
- ✅ git clone
- ✅ git add / commit / push
- ✅ git pull
- ✅ git branch / checkout

### Level 2: 協作 (重要)
- ✅ git merge
- ✅ 解決衝突
- ✅ git fetch vs pull
- ✅ Pull Request

### Level 3: 進階 (有空再學)
- 📚 git rebase
- 📚 git cherry-pick
- 📚 git reflog
- 📚 git bisect

---

**記住:Git 是用來幫助協作的,不是來添麻煩的!** 🚀

**最後更新:** 2025-11-26  
**維護者:** liaoyiting
