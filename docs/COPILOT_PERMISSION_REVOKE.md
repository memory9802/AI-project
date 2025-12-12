# 🔐 VS Code Copilot 授權撤回記錄

**日期**: 2025-12-09  
**操作者**: Rosy  
**狀態**: ✅ 已完成

---

## 📋 撤回原因

在 2025-12-09 16:20:14 發生了版本後退事件,原因是 VS Code Copilot 被授權可以自動執行 `git reset --hard` 等危險操作,在沒有詢問用戶的情況下直接執行,導致本地進度丟失。

**時間線:**
```
16:16:14  提交 f406f97 (503行完整版)
          ↓
16:20:14  Copilot 自動執行: git reset --hard origin/develop
          💥 本地檔案被強制覆蓋成遠端舊版
          ↓
16:39:47  發現問題並手動恢復
```

---

## 🚨 撤回的危險授權

以下操作已被撤回自動授權,現在 Copilot **無法自動執行**:

### ❌ 已撤回 (7 個)
1. `git reset` - 🚨 可能執行 `reset --hard` 強制丟棄變更
2. `git push` - 🚨 可能執行 `push --force` 覆蓋遠端
3. `git checkout` - ⚠️ 切換分支可能丟失未提交變更
4. `git merge` - ⚠️ 合併可能造成衝突和意外變更
5. `git rm` - ⚠️ 刪除檔案可能造成資料遺失
6. `git restore` - ⚠️ 恢復可能丟失當前變更
7. `git rebase` - 🚨 重寫提交歷史,風險極高
8. `git stash` - ⚠️ 暫存可能導致變更難以找回

---

## ✅ 保留的安全授權

以下操作仍可自動執行 (只讀,不修改):

### ✅ 保留 (3 個)
1. `git add` - 暫存檔案 (可恢復)
2. `git fetch` - 只取得資訊,不修改本地
3. `git commit` - 本地提交 (已在 GIT_WORKFLOW.md 中要求確認)

### 📊 查詢類操作 (未在自動授權清單,可直接使用)
- `git status` - 查看狀態
- `git log` - 查看歷史
- `git diff` - 查看差異
- `git show` - 顯示提交
- `git branch` - 列出分支

---

## 🔒 額外安全措施

### 1. 啟用 Git 同步確認
```json
"git.confirmSync": true  // false → true
```
現在執行 `git pull` 或 `git push` 時會彈出確認對話框。

### 2. 備份設定檔
```
~/Library/Application Support/Code/User/
├── settings.json                           # 當前設定
├── settings.json.backup_20251209_164939   # 撤權前備份
└── settings.json.backup_20251209_164227   # 更早的備份
```

---

## 📝 執行記錄

### 撤權操作
```bash
# 執行撤權腳本
python3 scripts/revoke_dangerous_git_permissions.py

# 結果
✅ 移除危險授權: 7 個
✅ 保留安全授權: 31 個
✅ 啟用 Git 同步確認
✅ 建立備份
```

### 驗證結果
```python
# 檢查危險授權是否移除
剩餘危險授權: 0 個 ✅

# 檢查安全授權是否保留
保留安全授權: 3 個 ✅
  ✅ git add
  ✅ git fetch
  ✅ git commit

# 檢查同步確認
git.confirmSync: True ✅
```

---

## 🎯 現在的工作流程

### AI 助手執行 Git 操作時:

1. **可自動執行** (不需詢問):
   ```bash
   git status
   git log
   git diff
   git show
   git branch -vv
   git fetch
   ```

2. **需要詢問確認** (顯示影響後等待同意):
   ```bash
   git add <檔案>
   git commit -m "訊息"
   ```

3. **絕對禁止** (無論如何不執行):
   ```bash
   git reset --hard
   git push --force
   git checkout <其他分支>  # 切換分支
   git merge
   git rm
   git restore
   git rebase
   git stash
   ```

---

## 🔗 相關文檔

- [VERSION_PROTECTION_POLICY.md](./VERSION_PROTECTION_POLICY.md) - 版本變動防護政策
- [GIT_WORKFLOW.md](./GIT_WORKFLOW.md) - Git 工作流程規範
- [DATABASE_MANAGEMENT_POLICY.md](./DATABASE_MANAGEMENT_POLICY.md) - 資料庫管理原則

---

## 💡 重要提醒

### 使設定生效
需要 **重新啟動 VS Code** 使新設定生效:
1. 儲存所有工作
2. 關閉 VS Code
3. 重新開啟 VS Code
4. 確認設定已套用

### 如何驗證
重啟後,可以在 VS Code 的設定中確認:
1. 按 `Cmd+,` 開啟設定
2. 搜尋 `chat.tools.terminal.autoApprove`
3. 確認危險操作已不在清單中

### 如果需要恢復
如果誤刪了需要的授權,可以從備份恢復:
```bash
# 查看備份清單
ls -lht ~/Library/Application\ Support/Code/User/settings.json.backup_*

# 恢復備份 (選擇需要的時間點)
cp ~/Library/Application\ Support/Code/User/settings.json.backup_YYYYMMDD_HHMMSS \
   ~/Library/Application\ Support/Code/User/settings.json
```

---

## ✅ 確認清單

- [x] 撤回 7 個危險授權
- [x] 保留 3 個安全授權
- [x] 啟用 Git 同步確認
- [x] 建立設定備份
- [x] 驗證撤權成功
- [x] 建立文檔記錄
- [ ] 重新啟動 VS Code
- [ ] 測試新的工作流程

---

**最後更新**: 2025-12-09 16:49  
**狀態**: ✅ 授權撤回完成,等待重啟 VS Code
