# 🛡️ Git 安全操作指南

**適用對象**: 所有開發者  
**最後更新**: 2025-12-09  
**前置閱讀**: [GIT_WORKFLOW.md](./GIT_WORKFLOW.md), [VERSION_PROTECTION_POLICY.md](./VERSION_PROTECTION_POLICY.md)

---

## 🎯 核心概念

### 📍 本地 vs 遠端

```
工作目錄 (Working Directory)
    ↓ git add
暫存區 (Staging Area)
    ↓ git commit
本地倉庫 (Local Repository) - develop
    ↓ git push
遠端倉庫 (Remote Repository) - origin/develop
```

### 🌲 分支關係圖

```
本地電腦                     GitHub 遠端
┌─────────────────┐         ┌─────────────────┐
│  工作目錄        │         │                  │
│  (編輯中的檔案)  │         │                  │
└─────────────────┘         │                  │
        ↓ git add            │                  │
┌─────────────────┐         │                  │
│  暫存區          │         │                  │
│  (準備提交)      │         │                  │
└─────────────────┘         │                  │
        ↓ git commit         │                  │
┌─────────────────┐         │                  │
│  develop         │ git push │  origin/develop │
│  (本地分支)      │─────────→│  (遠端分支)      │
└─────────────────┘         └─────────────────┘
        ↑ git pull
        │
        └─── 從遠端拉取最新變更
```

---

## 📋 常用安全操作

### 1️⃣ 檢查當前狀態 (最常用!)

```bash
# 查看當前分支和檔案變更狀態
git status

# 輸出範例:
# On branch develop                    ← 你在哪個分支
# Your branch is up to date with 'origin/develop'  ← 與遠端同步狀態
# 
# Changes not staged for commit:      ← 已修改但未暫存
#   modified:   app/app.py
# 
# Untracked files:                    ← 新檔案,尚未追蹤
#   new_feature.py
```

**🔍 狀態解讀:**
- `Changes not staged` = 已修改,但還沒 `git add`
- `Changes to be committed` = 已暫存,準備 `git commit`
- `Untracked files` = 新檔案,Git 還不知道
- `up to date with origin/develop` = 本地和遠端一致
- `ahead of origin/develop by 2 commits` = 本地比遠端多 2 個提交
- `behind origin/develop by 1 commit` = 遠端比本地多 1 個提交

---

### 2️⃣ 確認所在分支

```bash
# 方法 1: 查看當前分支 (簡單)
git branch

# 輸出:
#   1202MVP
# * develop        ← * 代表你現在在這個分支
#   1205MVPbp

# 方法 2: 查看分支和追蹤關係 (詳細)
git branch -vv

# 輸出:
#   1202MVP   656ee1d [origin/1202MVP] ...
# * develop   fb1a91b [origin/develop] security(git): 建立版本防護...
#              ↑         ↑              ↑
#            commit   追蹤的遠端分支    提交訊息

# 方法 3: 圖形化顯示所有分支
git log --oneline --graph --all --decorate -10

# 輸出:
# * fb1a91b (HEAD -> develop, origin/develop) security(git): ...
# * 6083c31 fix(database): ...
#    ↑         ↑        ↑
#  commit   HEAD指向  遠端位置
```

**🔍 術語解釋:**
- `HEAD` = 你現在所在的位置
- `develop` = 本地分支名稱
- `origin/develop` = 遠端分支名稱
- `*` = 當前分支標記

---

### 3️⃣ 暫存本地變更 (保存工作進度)

#### 方法 A: 暫存特定檔案 (推薦!)

```bash
# 暫存單一檔案
git add app/app.py

# 暫存多個檔案
git add app/app.py init/00_init_with_data.sql

# 暫存某個資料夾的所有檔案
git add docs/

# 暫存特定類型的檔案
git add *.py          # 所有 Python 檔案
git add docs/*.md     # docs 資料夾下所有 Markdown 檔案
```

#### 方法 B: 暫存所有變更

```bash
# ⚠️ 暫存所有已修改的檔案 (不含新檔案)
git add -u

# ⚠️ 暫存所有檔案 (包含新檔案和已修改)
git add -A
# 或
git add .

# 💡 建議: 使用前先 git status 確認要暫存什麼
```

#### 檢查暫存狀態

```bash
# 查看已暫存的變更
git diff --staged

# 查看已暫存的檔案清單
git status
```

**🎯 最佳實踐:**
```bash
# 1. 先查看有什麼變更
git status

# 2. 選擇性暫存 (更安全!)
git add 檔案1 檔案2

# 3. 確認暫存內容
git status

# 4. 提交
git commit -m "描述變更內容"
```

---

### 4️⃣ 查看本地和遠端的差異

#### A. 本地變更 vs 暫存區

```bash
# 查看工作目錄中已修改但未暫存的變更
git diff

# 輸出: 顯示每個檔案的修改內容
# - 紅色 = 刪除的內容
# + 綠色 = 新增的內容
```

#### B. 暫存區 vs 最後一次提交

```bash
# 查看已暫存的變更 (準備提交的內容)
git diff --staged
# 或
git diff --cached
```

#### C. 本地分支 vs 遠端分支

```bash
# 🔍 比較本地和遠端的差異 (最重要!)
git diff develop origin/develop

# 輸出: 顯示兩個分支之間的所有差異
```

#### D. 查看特定檔案的差異

```bash
# 查看某個檔案在本地和遠端的差異
git diff origin/develop -- init/00_init_with_data.sql

# 查看某個檔案的工作目錄 vs 暫存區
git diff init/00_init_with_data.sql

# 查看某個檔案在兩個 commit 之間的差異
git diff fb1a91b 6083c31 -- init/00_init_with_data.sql
```

#### E. 查看統計摘要 (不顯示詳細內容)

```bash
# 查看檔案變更統計
git diff --stat develop origin/develop

# 輸出範例:
#  init/00_init_with_data.sql | 307 +++++++++++++++++++++++++++++++++++
#  1 file changed, 307 insertions(+)
```

#### F. 更新遠端分支資訊 (重要!)

```bash
# 先取得最新的遠端資訊 (不會修改本地檔案!)
git fetch origin

# 然後再比較
git diff develop origin/develop
```

**🔍 fetch vs pull 的區別:**
```
git fetch  = 只下載資訊,不修改本地檔案 (安全 ✅)
git pull   = 下載資訊 + 合併到本地 (需要小心 ⚠️)
```

---

### 5️⃣ 提交到本地倉庫

```bash
# 基本提交
git commit -m "簡短描述變更內容"

# 詳細提交訊息 (推薦!)
git commit -m "feat(database): 新增評分系統表格

詳細說明:
- 新增 rating 表格
- 新增 item_stats 表格
- 建立 3 個視圖和 3 個觸發器

相關: #123"

# 修改上一次提交 (還沒 push 的情況下)
git commit --amend -m "修正提交訊息"
```

**🎯 提交訊息格式建議:**
```
類型(範圍): 簡短描述 (不超過 50 字)

詳細說明:
- 變更 1
- 變更 2
- 變更 3

相關: #issue_number
```

**類型範例:**
- `feat` - 新功能
- `fix` - 修復錯誤
- `docs` - 文檔變更
- `refactor` - 重構代碼
- `test` - 測試相關
- `chore` - 雜項 (清理、工具等)
- `security` - 安全性相關

---

### 6️⃣ 推送到遠端 (上傳檔案)

```bash
# 基本推送 (把本地 develop 推送到 origin/develop)
git push origin develop

# 第一次推送新分支 (設定追蹤)
git push -u origin develop
# 或
git push --set-upstream origin develop

# 之後就可以簡化為
git push
```

**⚠️ 推送前檢查清單:**
```bash
# 1. 確認在正確的分支
git branch

# 2. 確認要推送的內容
git log origin/develop..develop --oneline
# 顯示本地比遠端多的 commits

# 3. 確認沒有衝突
git fetch origin
git status
# 看是否顯示 "Your branch is ahead of..."

# 4. 推送
git push origin develop
```

---

### 7️⃣ 從遠端拉取最新變更

```bash
# ⚠️ 拉取前先確認狀態 (重要!)
git status

# 如果有未提交的變更,先提交或暫存
git add .
git commit -m "save: 保存當前進度"

# 方法 1: 取得遠端資訊但不合併 (最安全!)
git fetch origin

# 查看遠端有什麼新的
git log develop..origin/develop --oneline

# 如果確認沒問題,再合併
git merge origin/develop

# 方法 2: 直接拉取並合併 (需要確認!)
git pull origin develop
```

**🔍 pull 的本質:**
```
git pull = git fetch + git merge
```

---

## 🔄 完整工作流程範例

### 場景 1: 日常開發流程

```bash
# ========== 開始工作 ==========
# 1. 確認在正確的分支
git status
git branch

# 2. 取得最新的遠端資訊
git fetch origin

# 3. 查看是否有新的變更
git log develop..origin/develop --oneline

# 4. 如果有新的變更,拉取並合併
git pull origin develop

# ========== 開發階段 ==========
# 5. 編輯檔案 (在 VS Code 中修改)
# ...

# 6. 查看修改了什麼
git status
git diff

# 7. 暫存變更
git add 檔案1 檔案2
# 或暫存所有
git add .

# 8. 確認暫存內容
git status
git diff --staged

# 9. 提交到本地
git commit -m "feat: 新增某功能"

# ========== 上傳到遠端 ==========
# 10. 再次確認遠端沒有新的變更
git fetch origin
git status

# 11. 查看本地比遠端多的提交
git log origin/develop..develop --oneline

# 12. 推送到遠端
git push origin develop

# 13. 確認推送成功
git status
# 應該顯示: Your branch is up to date with 'origin/develop'
```

---

### 場景 2: 發現遠端有新的變更

```bash
# 1. 檢查狀態
git fetch origin
git status

# 輸出: Your branch is behind 'origin/develop' by 2 commits
#       (遠端比本地多 2 個提交)

# 2. 查看遠端的新提交
git log develop..origin/develop --oneline

# 3. 查看具體變更了什麼
git diff develop origin/develop

# 4. 如果確認沒問題,拉取變更
git pull origin develop

# 5. 確認合併成功
git status
# 應該顯示: Your branch is up to date with 'origin/develop'
```

---

### 場景 3: 本地和遠端都有新的變更

```bash
# 1. 檢查狀態
git fetch origin
git status

# 輸出: Your branch and 'origin/develop' have diverged
#       (本地和遠端分歧了!)

# 2. 查看本地的新提交
git log origin/develop..develop --oneline

# 3. 查看遠端的新提交
git log develop..origin/develop --oneline

# 4. 查看差異
git diff develop origin/develop

# 5. 手動合併 (需要選擇策略)
# 策略 A: 拉取並自動合併
git pull origin develop
# 如果有衝突,需要手動解決

# 策略 B: 先拉取,再手動選擇要保留什麼
git fetch origin
git merge origin/develop
# 或者使用 rebase (重寫歷史,更乾淨但更危險)
# git rebase origin/develop  # ⚠️ 需要小心!
```

---

## 🔍 進階查詢指令

### 查看提交歷史

```bash
# 查看簡潔的提交歷史
git log --oneline -10

# 查看圖形化歷史
git log --oneline --graph --all --decorate -20

# 查看某個檔案的修改歷史
git log --oneline -- init/00_init_with_data.sql

# 查看某個作者的提交
git log --author="Rosy" --oneline

# 查看某個時間範圍的提交
git log --since="2025-12-08" --until="2025-12-09" --oneline
```

### 查看特定 commit 的內容

```bash
# 查看某個 commit 的詳細資訊
git show fb1a91b

# 只查看某個 commit 改了哪些檔案
git show --stat fb1a91b

# 查看某個 commit 的某個檔案
git show fb1a91b:init/00_init_with_data.sql
```

### 比較不同版本

```bash
# 比較兩個 commit
git diff fb1a91b 6083c31

# 比較某個檔案在兩個 commit 之間的差異
git diff fb1a91b 6083c31 -- init/00_init_with_data.sql

# 比較當前版本和某個 commit
git diff fb1a91b
```

---

## 🛡️ 安全檢查清單

### ✅ 推送前確認

- [ ] `git status` - 確認在正確的分支
- [ ] `git diff --staged` - 確認暫存的內容正確
- [ ] `git log -1` - 確認提交訊息正確
- [ ] `git fetch origin` - 取得最新遠端資訊
- [ ] `git diff develop origin/develop` - 確認本地和遠端的差異
- [ ] `git push origin develop` - 推送

### ✅ 拉取前確認

- [ ] `git status` - 確認沒有未提交的變更
- [ ] `git fetch origin` - 取得遠端資訊
- [ ] `git log develop..origin/develop` - 查看遠端的新提交
- [ ] `git diff develop origin/develop` - 查看具體差異
- [ ] `git pull origin develop` - 拉取並合併

### ✅ 合併衝突處理

如果 pull 或 merge 時遇到衝突:

```bash
# 1. 查看有衝突的檔案
git status

# 2. 打開衝突檔案,會看到:
# <<<<<<< HEAD
# 你的變更
# =======
# 遠端的變更
# >>>>>>> origin/develop

# 3. 手動編輯,保留需要的內容

# 4. 標記為已解決
git add 衝突檔案

# 5. 完成合併
git commit -m "merge: 解決合併衝突"
```

---

## 📚 常用指令速查表

### 查詢類 (安全,不修改)

| 指令 | 說明 | 範例 |
|------|------|------|
| `git status` | 查看當前狀態 | `git status` |
| `git branch` | 查看分支 | `git branch -vv` |
| `git log` | 查看提交歷史 | `git log --oneline -10` |
| `git diff` | 查看差異 | `git diff develop origin/develop` |
| `git show` | 查看 commit 內容 | `git show fb1a91b` |
| `git fetch` | 取得遠端資訊 | `git fetch origin` |

### 修改類 (需要確認)

| 指令 | 說明 | 範例 |
|------|------|------|
| `git add` | 暫存檔案 | `git add app/app.py` |
| `git commit` | 提交到本地 | `git commit -m "訊息"` |
| `git push` | 推送到遠端 | `git push origin develop` |
| `git pull` | 拉取並合併 | `git pull origin develop` |
| `git merge` | 合併分支 | `git merge origin/develop` |

### 危險操作 (已禁止!)

| 指令 | 為什麼危險 | 替代方案 |
|------|-----------|---------|
| `git reset --hard` | 強制丟棄變更 | 先 `git stash` 保存 |
| `git push --force` | 覆蓋遠端歷史 | 不要用! |
| `git checkout -f` | 強制丟棄變更 | 先提交或暫存 |

---

## 🆘 常見問題

### Q1: 不小心修改了檔案,想恢復?

```bash
# 恢復單一檔案到上次提交的狀態
git restore 檔案名稱

# 恢復所有檔案
git restore .

# ⚠️ 注意: 未提交的變更會丟失!
```

### Q2: 提交訊息寫錯了?

```bash
# 修改最後一次提交的訊息 (還沒 push)
git commit --amend -m "正確的訊息"

# ⚠️ 如果已經 push,不要用 amend!
```

### Q3: 想暫時保存變更,切換到其他分支?

```bash
# 方法 1: 提交當前變更
git add .
git commit -m "wip: 工作進行中"

# 方法 2: 使用 stash (⚠️ 小心使用)
# 已被禁止自動執行,需要手動操作
```

### Q4: 查看某個檔案的修改歷史?

```bash
# 查看檔案的提交歷史
git log --oneline -- 檔案名稱

# 查看檔案每一行的修改者
git blame 檔案名稱

# 查看檔案在某個 commit 的內容
git show commit-hash:檔案名稱
```

---

## 🔗 相關文檔

- [GIT_WORKFLOW.md](./GIT_WORKFLOW.md) - Git 工作流程規範
- [VERSION_PROTECTION_POLICY.md](./VERSION_PROTECTION_POLICY.md) - 版本防護政策
- [COPILOT_PERMISSION_REVOKE.md](./COPILOT_PERMISSION_REVOKE.md) - Copilot 授權撤回記錄
- [DATABASE_MANAGEMENT_POLICY.md](./DATABASE_MANAGEMENT_POLICY.md) - 資料庫管理原則

---

**最後更新**: 2025-12-09  
**維護者**: Rosy  
**版本**: v1.0
