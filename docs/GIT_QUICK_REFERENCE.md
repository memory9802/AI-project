# 🚀 Git 安全操作快速參考卡

**給 Rosy 的專用速查表** | 最後更新: 2025-12-09

---

## 🎯 每次開始工作前 (3 步驟)

```bash
# 1. 確認在 develop 分支
git status

# 2. 取得最新遠端資訊
git fetch origin

# 3. 查看是否需要拉取
git log develop..origin/develop --oneline
# 如果有輸出 → 需要 git pull origin develop
# 如果沒輸出 → 可以開始工作
```

---

## 📝 日常開發流程 (6 步驟)

```bash
# 1. 查看修改了什麼
git status
git diff

# 2. 暫存變更
git add 檔案名稱
# 或暫存所有
git add .

# 3. 確認要提交什麼
git status
git diff --staged

# 4. 提交到本地
git commit -m "類型: 簡短描述"

# 5. 確認沒有遠端新變更
git fetch origin
git status

# 6. 推送到遠端
git push origin develop
```

---

## 🔍 快速檢查指令

### 我在哪個分支?
```bash
git branch
# * develop  ← 你在這裡
```

### 本地和遠端同步了嗎?
```bash
git status
# "up to date" = 同步 ✅
# "ahead by X" = 本地多 X 個提交,需要 push
# "behind by X" = 遠端多 X 個提交,需要 pull
```

### 本地比遠端多什麼?
```bash
git log origin/develop..develop --oneline
# 有輸出 = 你有未推送的提交
# 沒輸出 = 已經同步
```

### 遠端比本地多什麼?
```bash
git fetch origin
git log develop..origin/develop --oneline
# 有輸出 = 遠端有新的提交,需要 pull
# 沒輸出 = 已是最新
```

### 查看差異
```bash
# 查看工作目錄的修改 (未暫存)
git diff

# 查看已暫存的修改
git diff --staged

# 查看本地和遠端的差異
git diff develop origin/develop

# 查看特定檔案的差異
git diff -- init/00_init_with_data.sql
```

---

## 📊 查看歷史

```bash
# 最近 10 個提交
git log --oneline -10

# 圖形化顯示
git log --oneline --graph --all -10

# 查看某個檔案的修改歷史
git log --oneline -- 檔案名稱

# 查看某個 commit 的內容
git show fb1a91b
```

---

## 🔄 同步遠端

### 安全拉取 (推薦!)
```bash
# 1. 先取得資訊
git fetch origin

# 2. 查看遠端有什麼新的
git log develop..origin/develop --oneline
git diff develop origin/develop

# 3. 確認沒問題後合併
git merge origin/develop
```

### 快速拉取
```bash
# 直接拉取並合併 (確認沒有未提交的變更!)
git pull origin develop
```

---

## 🆘 常見情況處理

### 情況 1: 修改錯了,想恢復
```bash
# 恢復單一檔案
git restore 檔案名稱

# 恢復所有未暫存的修改
git restore .

# ⚠️ 未提交的變更會丟失!
```

### 情況 2: 暫存錯了,想取消暫存
```bash
# 取消暫存某個檔案
git restore --staged 檔案名稱

# 取消所有暫存
git restore --staged .
```

### 情況 3: 提交訊息寫錯了 (還沒 push)
```bash
git commit --amend -m "正確的訊息"
```

### 情況 4: 遠端和本地都有新的提交
```bash
# 1. 先 fetch 看看差異
git fetch origin
git log develop..origin/develop --oneline  # 遠端的新提交
git log origin/develop..develop --oneline  # 本地的新提交

# 2. 拉取並合併
git pull origin develop

# 3. 如果有衝突,手動解決後:
git add 衝突檔案
git commit -m "merge: 解決合併衝突"
```

---

## ✅ 安全檢查清單

### 推送前
- [ ] `git status` - 在 develop 分支
- [ ] `git fetch origin` - 取得最新資訊
- [ ] `git log origin/develop..develop` - 確認要推送什麼
- [ ] `git push origin develop` - 推送

### 拉取前
- [ ] `git status` - 沒有未提交的變更
- [ ] `git fetch origin` - 取得遠端資訊
- [ ] `git log develop..origin/develop` - 查看遠端新提交
- [ ] `git pull origin develop` - 拉取

---

## 🎨 提交訊息範例

```bash
# 新功能
git commit -m "feat(database): 新增評分系統表格"

# 修復錯誤
git commit -m "fix(api): 修正用戶登入問題"

# 文檔變更
git commit -m "docs: 更新 README 安裝說明"

# 重構代碼
git commit -m "refactor(app): 優化資料庫查詢效能"

# 安全性
git commit -m "security(git): 撤回危險授權"

# 雜項
git commit -m "chore: 清理臨時檔案"
```

---

## 🚨 絕對不要執行的指令

```bash
❌ git reset --hard     # 會丟失變更!
❌ git push --force     # 會覆蓋遠端!
❌ git checkout -f      # 會丟失變更!
❌ git clean -fd        # 會刪除檔案!
```

---

## 🔗 完整文檔

需要更詳細的說明?查看:
- [GIT_SAFE_OPERATIONS.md](./GIT_SAFE_OPERATIONS.md) - 完整操作指南
- [GIT_WORKFLOW.md](./GIT_WORKFLOW.md) - 工作流程規範
- [VERSION_PROTECTION_POLICY.md](./VERSION_PROTECTION_POLICY.md) - 防護政策

---

## 💡 實用技巧

### 別名設定 (可選)
在 `~/.gitconfig` 加入:
```ini
[alias]
    st = status
    br = branch -vv
    lg = log --oneline --graph --all --decorate -10
    df = diff
    dfs = diff --staged
    cm = commit -m
    ps = push origin develop
    pl = pull origin develop
    ft = fetch origin
```

設定後可以用簡短指令:
```bash
git st    # = git status
git lg    # = git log --oneline --graph...
git cm "訊息"  # = git commit -m "訊息"
```

---

**記住**: 有疑問就用 `git status` 和 `git diff` 檢查!
