# 🎓 Git 手動操作完整流程

> **給自己的 Git 指令複習筆記** - 不依賴工具,自己推送代碼

---

## 📖 目錄

1. [每日標準流程](#每日標準流程)
2. [常用指令速查](#常用指令速查)
3. [完整推送流程](#完整推送流程)
4. [分支操作](#分支操作)
5. [錯誤處理](#錯誤處理)

---

## 🌅 每日標準流程

### 早上開始工作

```bash
# 1. 進入專案目錄
cd ~/Desktop/AI-project-crawler-test

# 2. 檢查當前分支
git branch
# 顯示: * develop (星號表示當前分支)

# 3. 確保在 develop 分支
git checkout develop

# 4. 拉取最新代碼
git pull origin develop
# 或簡寫: git pull
```

### 下班前提交

```bash
# 1. 查看修改了什麼
git status

# 2. 查看具體修改內容
git diff

# 3. 提交代碼 (三步驟)
git add .                    # 加入所有修改
git commit -m "說明訊息"      # 提交到本地
git push origin develop      # 推送到遠端
```

---

## 🚀 完整推送流程 (詳細版)

### 步驟 1: 查看狀態

```bash
git status
```

**輸出範例**:
```
On branch develop
Changes not staged for commit:
  modified:   README.md
  modified:   app/app.py

Untracked files:
  FRONTEND_INTEGRATION_GUIDE.md
```

**解讀**:
- `modified`: 已存在的檔案被修改
- `Untracked files`: 新建立的檔案

---

### 步驟 2: 查看修改內容 (可選)

```bash
# 查看所有修改
git diff

# 查看特定檔案的修改
git diff README.md

# 查看簡短摘要
git diff --stat
```

**快捷鍵** (在 diff 畫面中):
- `空白鍵`: 往下翻頁
- `q`: 退出查看

---

### 步驟 3: 加入暫存區 (Staging)

```bash
# 方法 A: 加入所有修改 (最常用)
git add .

# 方法 B: 加入特定檔案
git add README.md
git add app/app.py

# 方法 C: 加入特定目錄
git add docs/

# 方法 D: 互動式選擇 (進階)
git add -p
```

**驗證**:
```bash
git status
# 應該顯示: Changes to be committed (綠色)
```

---

### 步驟 4: 提交到本地 (Commit)

```bash
# 基本提交
git commit -m "feat: 新增前後端整合指南"

# 多行訊息 (按 Enter 可換行)
git commit -m "feat: 新增前後端整合指南

- 說明推送流程
- 提供測試步驟
- 加入溝通範本"
```

**Commit Message 格式**:
```
<type>: <subject>

<body>
```

**常用 type**:
- `feat`: 新功能
- `fix`: 修復 bug
- `docs`: 文檔更新
- `style`: 代碼格式調整
- `refactor`: 重構代碼
- `test`: 測試相關
- `chore`: 其他修改

---

### 步驟 5: 推送到遠端 (Push)

```bash
# 推送到 develop 分支
git push origin develop

# 簡寫 (如果已設定追蹤)
git push
```

**如果推送被拒絕** (有人先推送了):
```bash
# 1. 先拉取遠端更新
git pull origin develop

# 2. 解決衝突 (如果有)
# 編輯衝突檔案...

# 3. 再次推送
git push origin develop
```

---

## 📝 常用指令速查

### 查看類指令

```bash
# 查看狀態
git status

# 查看修改內容
git diff                    # 尚未加入暫存的修改
git diff --staged           # 已加入暫存的修改

# 查看提交歷史
git log                     # 完整歷史
git log --oneline           # 簡短歷史
git log --oneline -5        # 最近 5 筆
git log --graph             # 圖形化顯示

# 查看分支
git branch                  # 本地分支
git branch -a               # 所有分支 (含遠端)
git branch -v               # 顯示最後一次提交
```

---

### 修改類指令

```bash
# 加入暫存
git add .                   # 所有修改
git add <file>              # 特定檔案

# 提交
git commit -m "訊息"        # 提交並附訊息
git commit --amend          # 修改最後一次提交

# 推送
git push origin develop     # 推送到遠端 develop
git push origin main        # 推送到遠端 main

# 拉取
git pull origin develop     # 從遠端拉取
git fetch origin            # 只下載不合併
```

---

### 撤銷類指令

```bash
# 撤銷工作目錄的修改 (危險!)
git checkout -- <file>      # 撤銷特定檔案
git checkout -- .           # 撤銷所有修改

# 從暫存區移除 (但保留修改)
git reset HEAD <file>       # 移除特定檔案
git reset HEAD .            # 移除所有

# 撤銷最後一次 commit (保留修改)
git reset --soft HEAD~1

# 撤銷最後一次 commit (不保留修改,危險!)
git reset --hard HEAD~1
```

---

## 🌿 分支操作

### 查看分支

```bash
# 查看本地分支
git branch

# 查看所有分支 (含遠端)
git branch -a

# 查看遠端分支
git branch -r
```

---

### 切換分支

```bash
# 切換到現有分支
git checkout develop
git checkout main

# 創建並切換到新分支
git checkout -b feature_new_function

# 新版指令 (推薦)
git switch develop          # 切換分支
git switch -c new_branch    # 創建並切換
```

---

### 合併分支

```bash
# 合併其他分支到當前分支
git merge develop           # 將 develop 合併到當前分支

# 保留合併歷史
git merge develop --no-ff   # 建議用這個

# 取消合併 (如果有衝突)
git merge --abort
```

---

### 刪除分支

```bash
# 刪除本地分支
git branch -d branch_name   # 安全刪除 (已合併)
git branch -D branch_name   # 強制刪除

# 刪除遠端分支
git push origin --delete branch_name
```

---

## ⚠️ 錯誤處理

### 錯誤 1: 推送被拒絕

```
! [rejected]  develop -> develop (fetch first)
```

**原因**: 遠端有新的提交

**解決**:
```bash
git pull origin develop     # 拉取遠端更新
# 解決衝突 (如果有)
git push origin develop     # 再次推送
```

---

### 錯誤 2: 合併衝突

```
CONFLICT (content): Merge conflict in README.md
```

**解決步驟**:
```bash
# 1. 打開衝突檔案
# 會看到:
<<<<<<< HEAD
你的代碼
=======
遠端的代碼
>>>>>>> origin/develop

# 2. 手動編輯,保留需要的代碼

# 3. 標記為已解決
git add README.md

# 4. 完成合併
git commit -m "merge: 解決衝突"

# 5. 推送
git push origin develop
```

---

### 錯誤 3: 忘記 commit message

```
error: Aborting commit due to empty commit message.
```

**原因**: 沒有輸入提交訊息

**解決**:
```bash
# 重新提交並加上訊息
git commit -m "feat: 你的提交訊息"
```

---

### 錯誤 4: 不小心修改了 main 分支

```bash
# 1. 暫存你的修改
git stash

# 2. 切換到 develop
git checkout develop

# 3. 恢復修改
git stash pop

# 4. 正常提交
git add .
git commit -m "訊息"
git push origin develop
```

---

## 🎯 實戰範例

### 範例 1: 修改文檔並推送

```bash
# 1. 編輯檔案
vim README.md

# 2. 查看狀態
git status
# 顯示: modified: README.md

# 3. 查看修改內容
git diff README.md

# 4. 加入暫存
git add README.md

# 5. 提交
git commit -m "docs: 更新 README 說明"

# 6. 推送
git push origin develop
```

---

### 範例 2: 新增檔案並推送

```bash
# 1. 創建新檔案
touch FRONTEND_INTEGRATION_GUIDE.md

# 2. 編輯內容
vim FRONTEND_INTEGRATION_GUIDE.md

# 3. 查看狀態
git status
# 顯示: Untracked files: FRONTEND_INTEGRATION_GUIDE.md

# 4. 加入版本控制
git add FRONTEND_INTEGRATION_GUIDE.md

# 5. 提交
git commit -m "docs: 新增前後端整合指南"

# 6. 推送
git push origin develop
```

---

### 範例 3: 同時修改多個檔案

```bash
# 1. 編輯多個檔案
vim README.md
vim app/app.py
touch NEW_FILE.md

# 2. 查看所有修改
git status

# 3. 查看修改統計
git diff --stat

# 4. 加入所有修改
git add .

# 5. 提交
git commit -m "feat: 更新文檔和應用程式

- 更新 README 說明
- 優化 app.py 路由
- 新增整合指南"

# 6. 推送
git push origin develop
```

---

## 🔄 完整工作流程圖

```
開始工作
  ↓
git checkout develop        # 切換到 develop 分支
  ↓
git pull origin develop     # 拉取最新代碼
  ↓
(編輯檔案...)               # 開發功能
  ↓
git status                  # 查看修改
  ↓
git diff                    # 查看詳細修改 (可選)
  ↓
git add .                   # 加入暫存區
  ↓
git status                  # 確認已加入 (可選)
  ↓
git commit -m "訊息"        # 提交到本地
  ↓
git push origin develop     # 推送到遠端
  ↓
完成! ✅
```

---

## 📋 每日檢查清單

### 開始工作前:
- [ ] `git checkout develop`
- [ ] `git pull origin develop`
- [ ] `git status` (確認工作目錄乾淨)

### 提交前:
- [ ] `git status` (檢查修改)
- [ ] `git diff` (查看修改內容)
- [ ] `git add .` (加入暫存)
- [ ] `git commit -m "訊息"` (提交)

### 推送前:
- [ ] `git log --oneline -3` (確認提交)
- [ ] `git push origin develop` (推送)

### 推送後:
- [ ] 在 GitHub 確認推送成功
- [ ] 通知組員 (如有需要)

---

## 💡 進階技巧

### 查看某個檔案的歷史

```bash
# 查看檔案的提交歷史
git log --follow README.md

# 查看檔案的每一行是誰修改的
git blame README.md
```

---

### 暫存修改

```bash
# 暫時儲存修改 (切換分支時很有用)
git stash

# 查看暫存列表
git stash list

# 恢復最後一次暫存
git stash pop

# 恢復特定暫存
git stash apply stash@{0}
```

---

### 標籤 (Tag)

```bash
# 創建標籤
git tag v1.0.0

# 推送標籤
git push origin v1.0.0

# 查看所有標籤
git tag
```

---

## 🆘 救命指令

### 我改錯分支了!

```bash
git stash                   # 暫存修改
git checkout develop        # 切換到正確分支
git stash pop               # 恢復修改
```

---

### 我想撤銷最後一次提交!

```bash
# 保留修改,只撤銷 commit
git reset --soft HEAD~1

# 不保留修改,完全撤銷
git reset --hard HEAD~1
```

---

### 我不小心刪除了檔案!

```bash
# 恢復已刪除的檔案
git checkout HEAD -- <file>

# 恢復所有刪除的檔案
git checkout HEAD -- .
```

---

### 我想回到某個歷史版本!

```bash
# 查看歷史
git log --oneline

# 回到特定版本
git checkout <commit-hash>

# 回到最新版本
git checkout develop
```

---

## 🎓 記憶口訣

### 推送三步驟 (最常用):
```
add → commit → push
加入 → 提交  → 推送
```

### 完整記憶:
```
status  → 看狀態
diff    → 看修改
add     → 加暫存
commit  → 提本地
push    → 送遠端
```

### 分支操作:
```
branch   → 看分支
checkout → 切分支
merge    → 合分支
```

---

## ✅ 快速參考卡

### 最常用的 10 個指令:

| 指令 | 用途 | 使用頻率 |
|------|------|---------|
| `git status` | 查看狀態 | ⭐⭐⭐⭐⭐ |
| `git add .` | 加入所有修改 | ⭐⭐⭐⭐⭐ |
| `git commit -m "訊息"` | 提交 | ⭐⭐⭐⭐⭐ |
| `git push origin develop` | 推送 | ⭐⭐⭐⭐⭐ |
| `git pull origin develop` | 拉取 | ⭐⭐⭐⭐⭐ |
| `git diff` | 查看修改 | ⭐⭐⭐⭐ |
| `git log --oneline` | 查看歷史 | ⭐⭐⭐ |
| `git checkout develop` | 切換分支 | ⭐⭐⭐ |
| `git branch` | 查看分支 | ⭐⭐ |
| `git merge` | 合併分支 | ⭐⭐ |

---

**建立日期**: 2025-11-26  
**最後更新**: 2025-11-26  
**維護人**: liaoyiting

---

💡 **建議**: 把這份文檔加入書籤,忘記指令時隨時查閱!
