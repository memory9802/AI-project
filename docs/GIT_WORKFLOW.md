# Git 工作流程規範

**專案**: StyleRec  
**主要工作分支**: `develop`  
**遠端倉庫**: `origin` (https://github.com/RosyL666/stylerec.git)  
**最後更新**: 2025-12-09

---

## 🎯 核心原則

### ⚠️ 絕對規則 (AI 助手必須遵守)

1. **禁止自動執行的命令** (必須先徵求用戶同意):
   ```bash
   ❌ git reset --hard [任何參數]
   ❌ git checkout [切換到其他分支]
   ❌ git pull --rebase
   ❌ git stash
   ❌ git push --force
   ❌ git branch -D [刪除分支]
   ❌ git clean -fd
   ```

2. **安全的查詢命令** (可以直接執行):
   ```bash
   ✅ git status
   ✅ git log
   ✅ git diff
   ✅ git branch -vv
   ✅ git remote -v
   ✅ git show
   ```

3. **需要確認的操作** (說明後等待確認):
   ```bash
   ⚠️ git add [檔案]
   ⚠️ git commit -m "訊息"
   ⚠️ git push origin develop
   ⚠️ git pull origin develop
   ```

---

## 📋 標準工作流程

### 1️⃣ 開始工作前 (每次開機/開始開發)

```bash
# 步驟 1: 確認當前分支
git branch --show-current
# 預期結果: develop

# 步驟 2: 檢查工作區狀態
git status
# 確認是否有未提交的變更

# 步驟 3: 查看遠端狀態
git fetch origin
git log HEAD..origin/develop --oneline
# 檢查遠端是否有新提交
```

**AI 助手行為**:
- ✅ 自動執行步驟 1-2
- ⚠️ 如果發現遠端有新提交,詢問: "遠端有 X 個新提交,是否要拉取?"
- ⚠️ 如果本地有未提交變更,詢問: "發現 X 個未提交的變更,要先提交嗎?"

---

### 2️⃣ 進行開發工作

```bash
# 正常編輯檔案
# 使用 IDE 或 AI 助手修改程式碼
```

**AI 助手行為**:
- ✅ 可以直接使用 `create_file`, `replace_string_in_file` 等工具
- ✅ 不涉及 Git 操作,完全安全

---

### 3️⃣ 提交變更 (定期保存進度)

```bash
# 步驟 1: 檢查變更
git status
git diff [檔案名稱]  # 可選,查看具體變更

# 步驟 2: 暫存變更
git add [檔案1] [檔案2] ...
# 或
git add -A  # 暫存所有變更

# 步驟 3: 提交
git commit -m "類型(範圍): 簡短描述

詳細說明變更內容
- 變更點 1
- 變更點 2"

# 步驟 4: 推送到遠端
git push origin develop
```

**AI 助手行為**:
- ⚠️ **必須先說明**: "準備提交 X 個檔案的變更,包括: [列出檔案]"
- ⚠️ **必須先展示**: commit message 內容
- ⚠️ **等待確認**: "是否確認提交並推送?"
- ✅ **得到同意後**: 執行 `git add` → `git commit` → `git push`

---

### 4️⃣ 同步遠端變更 (團隊協作)

#### 情境 A: 遠端有新提交,本地無變更

```bash
# 步驟 1: 拉取遠端變更
git pull origin develop

# 步驟 2: 確認同步成功
git log --oneline -5
```

**AI 助手行為**:
- ⚠️ **先詢問**: "遠端有 X 個新提交,本地工作區乾淨,是否要拉取?"
- ✅ **得到同意後**: 執行 `git pull origin develop`
- ✅ **提示結果**: "已成功同步,新增 X 個提交"

#### 情境 B: 遠端有新提交,本地也有變更

```bash
# ❌ 絕對不要用 git reset --hard

# 正確做法:
# 步驟 1: 先提交本地變更
git add -A
git commit -m "本地變更描述"

# 步驟 2: 拉取遠端變更 (可能有衝突)
git pull origin develop

# 步驟 3a: 如果沒有衝突
git push origin develop

# 步驟 3b: 如果有衝突
# 手動解決衝突後:
git add [解決衝突的檔案]
git commit -m "merge: 合併遠端變更"
git push origin develop
```

**AI 助手行為**:
- ⚠️ **先詢問**: "檢測到本地和遠端都有變更,建議操作順序:
  1. 先提交本地變更
  2. 拉取遠端變更
  3. 如果衝突,需要手動解決
  是否繼續?"
- ⚠️ **逐步確認**: 每個步驟都需要確認
- ❌ **絕不執行**: `git reset --hard` 或 `git stash`

#### 情境 C: 本地領先遠端 (您常見的情況)

```bash
# 步驟 1: 檢查差異
git log origin/develop..HEAD --oneline
# 查看本地領先幾個提交

# 步驟 2: 直接推送
git push origin develop
```

**AI 助手行為**:
- ✅ **先說明**: "本地領先遠端 X 個提交,準備推送"
- ⚠️ **詢問確認**: "是否要推送到遠端?"
- ✅ **得到同意後**: 執行 `git push origin develop`

---

### 5️⃣ 緊急情況處理

#### 問題: 誤操作後想恢復

```bash
# 步驟 1: 查看操作歷史
git reflog

# 步驟 2: 恢復到之前的狀態
git reset --hard [commit-hash]
```

**AI 助手行為**:
- ⚠️ **絕對不會主動執行 reset**
- ✅ 只提供建議: "可以使用 `git reflog` 查看歷史,然後告訴我要恢復到哪個提交"
- ⚠️ 等待用戶提供 commit hash 後再執行

---

## 🔍 檢查清單

### 每次提交前

- [ ] `git status` 確認變更範圍
- [ ] `git diff` 查看具體變更 (可選)
- [ ] commit message 清楚描述變更
- [ ] 本地測試通過

### 每次推送前

- [ ] `git log origin/develop..HEAD` 確認要推送的提交
- [ ] 確認沒有敏感資訊
- [ ] 確認不會覆蓋他人的工作

### 每次拉取前

- [ ] `git status` 確認工作區狀態
- [ ] 如有未提交變更,先提交
- [ ] `git fetch origin` 查看遠端狀態

---

## 📞 AI 助手的標準對話流程

### 場景 1: 需要推送變更

```
AI: 檢測到 3 個檔案有變更:
- init/00_init_with_data.sql (modified)
- docs/DATABASE_MANAGEMENT_POLICY.md (new)
- init/migration_rating_system.sql (deleted)

準備提交訊息:
"docs(database): 建立資料庫管理原則並統整檔案結構"

是否確認提交並推送到 origin/develop?
[等待用戶回應: 是/否/修改訊息]
```

### 場景 2: 需要拉取變更

```
AI: 遠端 origin/develop 有 2 個新提交:
- abc1234 feat: 新增功能 X
- def5678 fix: 修復問題 Y

目前本地工作區狀態: 乾淨/有 N 個未提交變更

是否要拉取遠端變更?
選項:
A) 直接拉取 (工作區乾淨時)
B) 先提交本地變更再拉取 (有未提交變更時)
C) 取消,我手動處理

[等待用戶選擇]
```

### 場景 3: 發現分支衝突

```
AI: ⚠️ 警告:檢測到本地和遠端歷史不一致

本地 develop: commit A → B → C
遠端 develop: commit A → D → E

這可能導致衝突或丟失進度。

建議方案:
1. 保留本地進度,強制推送 (會覆蓋遠端)
2. 放棄本地進度,使用遠端 (會丟失 B、C)
3. 手動合併 (需要解決衝突)

❌ 我不會自動執行任何操作,請告訴我您的決定。
```

---

## 🎯 總結: AI 助手的權限

### ✅ 可以自動執行 (查詢類)
- `git status`
- `git log`
- `git diff`
- `git branch -vv`
- `git remote -v`
- `git fetch origin`

### ⚠️ 需要確認 (修改類)
- `git add`
- `git commit`
- `git push`
- `git pull`

### ❌ 絕對禁止 (危險操作)
- `git reset --hard`
- `git checkout [切換分支]`
- `git push --force`
- `git clean -fd`
- `git stash` (除非明確要求)

---

## 📝 常見問題

### Q1: 如何確保不丟失本地進度?

**A**: 
1. 定期提交 (每完成一個功能)
2. 定期推送到遠端 (每天至少一次)
3. 重要變更前先備份分支: `git branch backup-YYYYMMDD`

### Q2: 如果 AI 助手做了危險操作怎麼辦?

**A**:
1. 立即執行 `git reflog` 查看歷史
2. 找到操作前的 commit hash
3. 執行 `git reset --hard [hash]` 恢復
4. 回報問題,改進流程

### Q3: 如何避免遠端和本地不同步?

**A**:
1. 每次開始工作前先 `git fetch origin` 檢查
2. 每次完成工作後立即推送
3. 團隊約定: develop 分支由主要開發者維護
4. 其他成員從 develop 分支創建 feature 分支

---

**最後更新**: 2025-12-09  
**維護者**: RosyL666
