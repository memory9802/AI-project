# 📢 分支整理通知訊息範本

## 第一階段:通知即將整理 (提前 1-2 天發送)

```
🚨 重要通知:Git 分支大整理計畫

各位組員好!

我們即將進行 Git 分支整理,讓專案結構更清晰,協作更順暢。

📅 預計執行時間: [具體日期時間,例如:11/27(三) 晚上 8:00]
⏱️ 預計需時: 2-3 小時
🔒 影響: 整理期間請暫停 push 操作

📋 請在 [日期時間] 前完成:

1️⃣ 提交所有修改
   ```bash
   git add .
   git commit -m "整理前保存進度"
   git push origin <你的分支名稱>
   ```

2️⃣ 記錄你目前的工作分支
   ```bash
   git branch
   # 截圖或記下你在哪個分支
   ```

3️⃣ [日期時間] 後請暫停開發
   等待「整理完成」通知

🎯 整理後的新架構:

main (穩定版本,可 Demo)
  ← 來源: openspec (最新統一架構)

develop (開發分支,日常工作)
  ← 整合: 爬蟲、前端、資料庫

feature/* (功能分支,按需建立)
  ← 從 develop 開出

🗑️ 將被刪除的分支:
  - Jinja (已過時)
  - jinja-test (測試用)
  - integrate-crawler-db (內容有誤)

🔄 將被合併的分支:
  - Crawler&Detection → develop
  - frontend → develop

整理完成後會再通知大家!

有任何問題請立即回覆! 🙋
```

---

## 第二階段:執行整理時通知

```
🔧 開始進行分支整理

整理進行中,請暫時不要 push!

預計 2-3 小時完成,完成後會通知大家。

期間如有緊急需求請聯繫我。
```

---

## 第三階段:整理完成通知

```
✅ 分支整理完成!

各位組員好!

Git 分支整理已完成,新的架構如下:

📊 新的分支架構:

1️⃣ main (穩定版本)
   - 基於 openspec 的最新統一架構
   - 用於 Demo 給老師看
   - 不要直接在這裡開發

2️⃣ develop (開發分支) ⭐ 主要工作區
   - 整合了爬蟲、前端、資料庫
   - 日常開發都在這裡
   - 包含 Windows 相容性修改

3️⃣ feature/* (功能分支)
   - 開發新功能時才建立
   - 完成後合併回 develop

🔄 如何切換到新架構:

```bash
# 1. 更新所有分支資訊
git fetch --all

# 2. 切換到 develop (日常開發)
git checkout develop
git pull origin develop

# 3. 確認資料庫檔案是否更新
ls -lh init/outfit_db_with_data.sql

# 4. 重新匯入資料庫
docker-compose up -d
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

# 5. 驗證資料
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "SELECT COUNT(*) FROM items;"
# 應該顯示: 49707
```

📋 新的工作流程:

每天開始工作:
```bash
git checkout develop
git pull origin develop
```

開發新功能:
```bash
git checkout -b feature/your-feature-name
# ... 開發 ...
git push origin feature/your-feature-name
```

功能完成後:
```bash
git checkout develop
git pull origin develop
git merge feature/your-feature-name
git push origin develop
git branch -d feature/your-feature-name
```

📖 詳細說明:
- docs/GIT_WORKFLOW_GUIDE.md (完整指南)
- docs/GIT_QUICK_REFERENCE.md (快速參考)
- BRANCH_CLEANUP_PLAN.md (整理計畫)

🗑️ 已刪除的分支:
- Jinja
- jinja-test  
- integrate-crawler-db

💾 備份:
- 舊 main 已備份到 main-old-backup 分支

✅ 驗證清單:

請確認以下都正常:
- [ ] git checkout develop 成功
- [ ] docker-compose up -d 成功
- [ ] 資料庫有資料 (SELECT COUNT(*) FROM items; = 49707)
- [ ] Flask 可以啟動 (python3 app/app.py)
- [ ] 前端頁面可以訪問

如有任何問題,請立即回報! 🙋

讓我們在新的架構下更高效地協作! 💪
```

---

## 第四階段:常見問題解答 (整理後幾天)

```
❓ 分支整理後的常見問題

Q1: 我的舊分支怎麼辦?
A: 如果你之前在 Crawler&Detection 或 frontend,它們的內容已經合併到 develop。請切換到 develop 繼續工作。

Q2: 我之前的 commit 不見了?
A: 沒有不見!所有 commit 都已經合併到 develop。用 git log 可以看到。

Q3: 資料庫資料不見了?
A: 重新匯入即可:
   docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

Q4: 我該在哪個分支工作?
A: 日常開發在 develop 分支。開發新功能時從 develop 開出 feature/* 分支。

Q5: 什麼時候該開新分支?
A: 
   ✅ 開發需要幾天的新功能
   ✅ 實驗性的修改
   ❌ 修改一個小 bug (直接在 develop)
   ❌ 更新文檔 (直接在 develop)

Q6: 我可以在 main 上開發嗎?
A: ❌ 不行!main 只用來 Demo。日常開發都在 develop。

Q7: 如果我搞混了怎麼辦?
A: 
   1. 先 git stash 保存你的修改
   2. git checkout develop
   3. git pull origin develop
   4. git stash pop
   5. 繼續工作

Q8: Windows 電腦能用嗎?
A: ✅ 可以!develop 已經包含 Windows 相容性修改(來自 system 分支)。

Q9: 怎麼查看我目前在哪個分支?
A: 
   git branch  (有 * 的就是目前分支)

Q10: 我不小心在 main 上改了程式碼!
A: 
   git stash                    # 保存修改
   git checkout develop         # 切換到 develop
   git stash pop               # 恢復修改
   # 然後正常 commit

有其他問題請隨時詢問!
```

---

## Discord/Line 簡化版

```
🚨 Git 分支整理通知

時間: [日期時間]

請在整理前:
✅ git push 所有修改
✅ 記下目前分支
✅ [時間]後暫停 push

整理完後會通知!
詳細說明: [GitHub repo link]
```

```
✅ 整理完成!

新架構:
- main: 穩定版 (Demo用)
- develop: 開發分支 (主要工作)

請執行:
1. git fetch --all
2. git checkout develop
3. git pull origin develop
4. 重新匯入資料庫

詳細步驟看群組訊息!
```

---

## GitHub Issue 版本

### 標題
```
🚨 [重要] Git 分支架構重整計畫
```

### 內容
```markdown
## 📋 整理計畫

為了讓專案結構更清晰,我們將進行分支整理。

### 時程
- **通知時間**: 2025-11-26
- **執行時間**: 2025-11-27 20:00
- **預計完成**: 2025-11-27 23:00

### 新架構
- `main`: 穩定版本 (基於 openspec)
- `develop`: 開發分支 (整合所有功能)
- `feature/*`: 功能分支 (按需建立)

### 執行前請務必
- [ ] 提交所有修改並 push
- [ ] 記錄目前工作分支
- [ ] 執行時間後暫停 push

### 將被刪除的分支
- Jinja
- jinja-test
- integrate-crawler-db

### 將被合併的分支
- Crawler&Detection → develop
- frontend → develop

### 詳細計畫
請參閱: [BRANCH_CLEANUP_PLAN.md](./BRANCH_CLEANUP_PLAN.md)

### 有問題?
請在下方留言!

---

**執行者**: @liaoyiting  
**審核者**: 全體組員
```

---

## Email 版本

### 主旨
```
[AI-Project] 重要:Git 分支整理通知 - 請在 [日期] 前完成準備
```

### 內容
```
親愛的專案組員們:

為了改善我們的協作流程,我們將進行 Git 分支整理。

執行時間: [日期時間]
預計需時: 2-3 小時

請在執行前完成以下準備:

1. 提交所有修改
   git add .
   git commit -m "整理前保存"
   git push

2. 記錄你目前的分支
   git branch

3. [時間]後請暫停 push 操作

整理後的新架構:
- main: 穩定版本 (Demo用)
- develop: 開發分支 (日常工作)
- feature/*: 功能分支 (開發新功能時)

詳細說明請見附件或 GitHub:
https://github.com/memory9802/AI-project

如有任何問題,請立即回覆此信或在群組中詢問。

謝謝配合!

Best regards,
[你的名字]
```

---

**使用建議:**

1. **提前通知**: 至少提前 1-2 天發送第一階段通知
2. **多管道通知**: Line/Discord + GitHub Issue + Email
3. **確認收到**: 請組員回覆「已了解」
4. **分階段通知**: 不要一次發太多訊息
5. **保持更新**: 整理過程中隨時更新進度
