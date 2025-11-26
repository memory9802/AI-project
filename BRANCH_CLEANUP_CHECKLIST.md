# ✅ 分支整理檢查清單

## 📋 執行前檢查 (必須全部完成!)

### 通知與確認
- [ ] 已發送第一階段通知(提前 1-2 天)
- [ ] 所有組員已回覆「已了解」
- [ ] 已選擇沒有人開發的時間(晚上或週末)
- [ ] 已設定執行時間並通知所有人

### 技術準備
- [ ] 已閱讀完整的 `BRANCH_CLEANUP_PLAN.md`
- [ ] 本地 Git 版本 >= 2.20
- [ ] 有 2-3 小時的完整時間
- [ ] 網路連線穩定

### 備份確認
- [ ] 所有組員都已 push 他們的修改
- [ ] 已下載完整的專案備份到本地
- [ ] 已確認資料庫備份檔案存在(`init/outfit_db_with_data.sql`)

### 分支狀態檢查
- [ ] 已確認 openspec 分支可以正常運行
  ```bash
  git checkout openspec
  docker-compose up -d
  # 測試是否正常
  ```
- [ ] 已確認 Crawler&Detection 有最新的爬蟲和資料庫
- [ ] 已確認 frontend 有最新的前端頁面

---

## 🚀 執行階段檢查

### Phase 1: 備份與準備
- [ ] git fetch --all 成功
- [ ] 未提交的修改已 stash
- [ ] 已查看並記錄目前所有分支

### Phase 2: 建立新 main
- [ ] 舊 main 已備份到 main-old-backup
- [ ] main-old-backup 已推送到 GitHub
- [ ] 已用 openspec 覆蓋 main
- [ ] 新 main 已推送成功

### Phase 3: 建立 develop
- [ ] develop 分支已建立
- [ ] develop 已推送到 GitHub
- [ ] develop 基於新的 main

### Phase 4: 合併分支

#### 4.1 Crawler&Detection
- [ ] 已切換到 develop
- [ ] 已 pull 最新的 develop
- [ ] Crawler&Detection 合併成功
  - [ ] 沒有衝突 OR
  - [ ] 衝突已解決並提交
- [ ] 已推送到 GitHub

#### 4.2 frontend
- [ ] 已切換到 develop  
- [ ] 已 pull 最新的 develop
- [ ] frontend 合併成功
  - [ ] 沒有衝突 OR
  - [ ] 衝突已解決並提交
- [ ] 已推送到 GitHub

#### 4.3 system (Windows 相容性)
- [ ] 已比較 openspec 和 system 差異
- [ ] 已檢查差異檔案(`/tmp/system-diff.txt`)
- [ ] Windows 相容性修改已套用(如果需要)

### Phase 5: 清理分支
- [ ] Jinja 已刪除(本地+遠端)
- [ ] jinja-test 已刪除(本地+遠端)
- [ ] integrate-crawler-db 已刪除(本地+遠端)
- [ ] git fetch --prune 已執行

---

## ✅ 執行後驗證

### 分支結構檢查
- [ ] main 分支存在且可用
- [ ] develop 分支存在
- [ ] main-old-backup 分支存在(備份)
- [ ] 不需要的分支已刪除

### 功能驗證

#### Docker 環境
```bash
git checkout develop
docker-compose down
docker-compose up -d
```
- [ ] MySQL 容器正常啟動
- [ ] 沒有錯誤訊息

#### 資料庫驗證
```bash
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'items' as table_name, COUNT(*) as count FROM items;
"
```
- [ ] users 表: 50 筆
- [ ] items 表: 49,707 筆

#### Flask 應用驗證
```bash
cd app
python3 app.py
```
- [ ] Flask 應用正常啟動
- [ ] 訪問 http://localhost:5000 正常
- [ ] 沒有 import 錯誤

#### 前端驗證
- [ ] 前端頁面可以訪問
- [ ] CSS 正常載入
- [ ] JavaScript 正常運作

#### 爬蟲驗證
```bash
python3 pipeline/01_crawl_uniqlo.py
```
- [ ] 爬蟲腳本可以執行
- [ ] 沒有 import 錯誤

### 檔案完整性檢查
- [ ] init/outfit_db_with_data.sql 存在
- [ ] pipeline/ 資料夾存在且有腳本
- [ ] app/ 資料夾存在且有 app.py
- [ ] app/templates/ 資料夾存在且有 HTML
- [ ] app/static/ 資料夾存在且有 CSS/JS
- [ ] docker-compose.yml 存在
- [ ] README.md 存在

---

## 📢 通知組員

### 第二階段通知(整理完成)
- [ ] 已發送「整理完成」通知
- [ ] 通知內容包含:
  - [ ] 新的分支架構說明
  - [ ] 切換步驟(git checkout develop)
  - [ ] 資料庫匯入指令
  - [ ] 驗證步驟
  - [ ] 文檔連結

### 後續追蹤
- [ ] 第一位組員成功切換(請他回報)
- [ ] 第二位組員成功切換(請他回報)
- [ ] 所有組員都已切換完成

---

## 🆘 如果出錯怎麼辦?

### 恢復選項

#### 恢復舊 main
```bash
git checkout main
git reset --hard main-old-backup
git push origin main --force
```
- [ ] 已恢復舊 main
- [ ] 已通知組員

#### 恢復到整理前
```bash
git reflog
git reset --hard HEAD@{n}  # n 是 reflog 編號
```
- [ ] 已查看 reflog
- [ ] 已找到正確的 HEAD 編號
- [ ] 已恢復狀態

### 常見問題處理

#### 合併衝突
- [ ] 已查看衝突檔案
- [ ] 已決定保留哪個版本
- [ ] 已解決所有衝突
- [ ] 已測試解決後的程式碼
- [ ] 已提交解決

#### 組員無法切換
- [ ] 已確認組員執行的指令
- [ ] 已檢查錯誤訊息
- [ ] 已提供解決方案
- [ ] 組員已成功切換

---

## 📝 整理後的工作

### 文檔更新
- [ ] README.md 已更新(說明新架構)
- [ ] docs/GIT_WORKFLOW_GUIDE.md 可訪問
- [ ] docs/GIT_QUICK_REFERENCE.md 可訪問
- [ ] BRANCH_CLEANUP_PLAN.md 標記為「已完成」

### GitHub 設定
- [ ] 已設定 develop 為預設分支(可選)
- [ ] 已設定分支保護規則(可選)
  - [ ] main 需要 PR 才能合併
  - [ ] develop 可以直接 push

### 團隊培訓
- [ ] 已舉辦小型說明會(可選)
- [ ] 已分享 Git 工作流程文檔
- [ ] 已回答組員的所有問題

---

## 📊 最終確認

### 所有組員確認清單

| 組員 | 已切換到 develop | 資料庫正常 | 程式可運行 | 備註 |
|------|----------------|-----------|-----------|------|
| [組員1] | ⬜ | ⬜ | ⬜ | |
| [組員2] | ⬜ | ⬜ | ⬜ | |
| [組員3] | ⬜ | ⬜ | ⬜ | |
| [組員4] | ⬜ | ⬜ | ⬜ | |
| [組員5] | ⬜ | ⬜ | ⬜ | |

---

## 🎉 完成!

當所有檢查項目都完成後:

- [ ] ✅ 分支整理成功完成
- [ ] ✅ 所有組員都已切換完成
- [ ] ✅ 新的工作流程開始運作
- [ ] ✅ 已建立 Git tag 紀念: `git tag -a branch-cleanup-complete -m "分支整理完成"`

**恭喜!你們有了更清晰的 Git 架構!** 🎊

---

**整理執行人:** liaoyiting  
**整理日期:** ___________  
**完成時間:** ___________  
**參與人數:** ___________
