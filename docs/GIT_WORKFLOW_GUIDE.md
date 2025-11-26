# 🌿 Git 工作流程指南

> 從混亂到有序:建立專業的 Git 協作流程

## 📊 目前狀況分析

### 現有分支
```
* Crawler&Detection      ← 你目前在這裡
  frontend
  integrate-crawler-db
  Jinja
  jinja-test
  openspec
  system
  main                   ← 主分支
```

### 問題診斷

❌ **目前的問題:**
1. 分支太多,不知道哪個是「最新穩定版」
2. 每次開發就開新分支,沒有合併回去
3. 資料庫更新在某個分支,其他分支看不到
4. 不清楚何時該開分支、何時該合併

✅ **改善目標:**
1. 建立清楚的分支策略
2. 定期合併,保持主分支最新
3. 減少長期存在的分支
4. 讓所有人都能看到最新進度

---

## 🎯 推薦策略:簡化版 Git Flow (適合學生專案)

### 分支結構

```
main (主分支)
  ↓
  ├─ develop (開發分支) ← 日常開發在這裡
  │   ↓
  │   ├─ feature/crawler-uniqlo    (功能分支:爬蟲)
  │   ├─ feature/frontend-login    (功能分支:前端登入)
  │   ├─ feature/ai-recommend      (功能分支:AI 推薦)
  │   └─ bugfix/database-charset   (修復分支:資料庫亂碼)
  │
  └─ hotfix/urgent-bug (緊急修復)
```

---

## 📋 分支說明

### 1. `main` 分支 (主分支)

**用途:** 穩定版本,隨時可以 demo 給老師看

**規則:**
- ✅ 只接受從 `develop` 合併的程式碼
- ✅ 所有功能都經過測試
- ❌ 不直接在 main 上開發
- ❌ 不接受未完成的功能

**何時更新:**
- 每週里程碑完成時
- 期中/期末 demo 前
- 重大功能完成時

---

### 2. `develop` 分支 (開發分支)

**用途:** 整合所有人的工作,日常開發的「總部」

**規則:**
- ✅ 所有功能分支從這裡分出
- ✅ 所有功能完成後合併回這裡
- ✅ 可以有小 bug,但不能完全壞掉
- ✅ 資料庫更新在這裡同步

**何時更新:**
- 每天都可能更新
- 任何人完成功能就合併回來

---

### 3. `feature/*` 分支 (功能分支)

**用途:** 開發特定功能

**命名規則:**
```
feature/<功能名稱>

範例:
feature/crawler-uniqlo      # 爬蟲:UNIQLO 網站
feature/frontend-login      # 前端:登入頁面
feature/ai-color-detect     # AI:色彩檢測
feature/database-items      # 資料庫:商品表
```

**規則:**
- ✅ 從 `develop` 分支出來
- ✅ 功能完成後合併回 `develop`
- ✅ 合併後刪除此分支 (不留痕跡)
- ⏱️ 存在時間:1-5 天 (不要超過一週)

**何時使用:**
- 開發新功能
- 需要獨立測試的修改
- 可能影響他人的大改動

---

### 4. `bugfix/*` 分支 (修復分支)

**用途:** 修復非緊急的 bug

**命名規則:**
```
bugfix/<問題描述>

範例:
bugfix/login-error          # 修復登入錯誤
bugfix/database-charset     # 修復資料庫亂碼
bugfix/crawler-timeout      # 修復爬蟲超時
```

**規則:**
- ✅ 從 `develop` 分支出來
- ✅ 修復後合併回 `develop`
- ✅ 合併後刪除
- ⏱️ 存在時間:1-2 天

---

### 5. `hotfix/*` 分支 (緊急修復)

**用途:** 修復 `main` 分支的緊急問題

**命名規則:**
```
hotfix/<緊急問題>

範例:
hotfix/demo-crash           # Demo 時程式崩潰
hotfix/database-lost        # 資料庫資料遺失
```

**規則:**
- ✅ 從 `main` 分支出來 (特殊!)
- ✅ 修復後合併回 `main` 和 `develop`
- ⏱️ 存在時間:幾小時內完成

**何時使用:**
- Demo 前發現重大問題
- 老師要檢查時發現錯誤
- 無法等待正常流程的緊急情況

---

## 🔄 標準工作流程

### 情境 1: 開發新功能 (最常用)

```bash
# 1. 確保在最新的 develop
git checkout develop
git pull origin develop

# 2. 建立功能分支
git checkout -b feature/crawler-uniqlo

# 3. 開發功能 (多次 commit)
git add pipeline/01_crawl_uniqlo.py
git commit -m "新增 UNIQLO 爬蟲基礎架構"

git add pipeline/01_crawl_uniqlo.py
git commit -m "完成商品資料解析"

git add tests/test_uniqlo_crawler.py
git commit -m "新增爬蟲測試"

# 4. 推送到 GitHub (讓組員知道你在做什麼)
git push origin feature/crawler-uniqlo

# 5. 功能完成後,合併回 develop
git checkout develop
git pull origin develop              # 先拉最新版本
git merge feature/crawler-uniqlo     # 合併功能
git push origin develop              # 推送

# 6. 刪除功能分支 (本地和遠端)
git branch -d feature/crawler-uniqlo
git push origin --delete feature/crawler-uniqlo

# 7. 通知組員
# 「✅ UNIQLO 爬蟲已完成並合併到 develop,請更新」
```

---

### 情境 2: 同步組員的更新

```bash
# 每天開始工作前執行
git checkout develop
git pull origin develop

# 如果有資料庫更新
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

# 如果你正在功能分支上
git checkout feature/your-feature
git merge develop    # 把最新的 develop 合併進來
# 解決衝突 (如果有)
```

---

### 情境 3: 準備 Demo (發布到 main)

```bash
# 1. 確保 develop 所有功能都完成
git checkout develop
git pull origin develop

# 2. 測試所有功能
python3 -m pytest tests/
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "SELECT COUNT(*) FROM items;"
# ... 其他測試

# 3. 合併到 main
git checkout main
git pull origin main
git merge develop
git push origin main

# 4. 建立標籤 (可選,但推薦)
git tag -a v1.0 -m "期中 Demo 版本"
git push origin v1.0

# 5. 通知組員
# 「🎉 v1.0 已發布到 main,期中 demo 準備完成」
```

---

### 情境 4: 處理衝突

```bash
# 當合併時出現衝突
git merge develop
# Auto-merging app/app.py
# CONFLICT (content): Merge conflict in app/app.py

# 1. 查看衝突檔案
git status

# 2. 編輯衝突檔案
# 找到 <<<<<<< HEAD 和 >>>>>>> develop 的標記
# 決定要保留哪個版本

# 3. 解決衝突後
git add app/app.py
git commit -m "解決 app.py 的合併衝突"

# 4. 推送
git push origin develop
```

---

## 🗑️ 清理舊分支

你們目前有太多舊分支,需要清理:

### 步驟 1: 確認哪些分支還需要

```bash
# 查看所有分支
git branch -a

# 查看每個分支最後更新時間
git for-each-ref --sort=-committerdate refs/remotes/origin --format='%(refname:short) %(committerdate:relative)'
```

### 步驟 2: 決定處理方式

```
分支名稱               建議處理
─────────────────     ────────────────
main                  ✅ 保留 (主分支)
develop               ✅ 建立 (如果沒有)
Crawler&Detection     🔄 合併到 develop 後刪除
frontend              🔄 合併到 develop 後刪除
integrate-crawler-db  🔄 合併到 develop 後刪除
Jinja                 🔄 合併到 develop 後刪除
jinja-test            ❌ 刪除 (測試用,已不需要)
openspec              ❓ 確認後決定
system                ❓ 確認後決定
```

### 步驟 3: 合併重要分支

```bash
# 1. 先建立 develop 分支 (如果沒有)
git checkout main
git pull origin main
git checkout -b develop
git push origin develop

# 2. 依序合併有用的分支
# 假設 Crawler&Detection 有最新的爬蟲和資料庫
git checkout develop
git merge origin/Crawler&Detection
git push origin develop

# 假設 frontend 有最新的前端
git merge origin/frontend
# 解決衝突 (如果有)
git push origin develop

# 3. 確認 develop 包含所有功能
# 檢查檔案、測試、資料庫等
```

### 步驟 4: 刪除已合併的分支

```bash
# ⚠️ 確認已經合併後才刪除!

# 刪除遠端分支
git push origin --delete Crawler&Detection
git push origin --delete frontend
git push origin --delete integrate-crawler-db
git push origin --delete jinja-test

# 刪除本地分支
git branch -d Crawler&Detection
git branch -d frontend
```

---

## 📏 團隊規範

### Commit Message 規範

```bash
# ✅ 好的 commit message
git commit -m "新增 UNIQLO 爬蟲功能"
git commit -m "修復登入頁面的 CSS 錯誤"
git commit -m "更新資料庫:新增 500 筆商品"
git commit -m "重構 AI 推薦演算法"

# ❌ 不好的 commit message
git commit -m "更新"
git commit -m "fix"
git commit -m "test"
git commit -m "aaa"
```

**格式建議:**
```
<類型>: <簡短描述>

類型:
- 新增 (add/feat): 新功能
- 修復 (fix): Bug 修復
- 更新 (update): 更新內容
- 重構 (refactor): 重構程式碼
- 文檔 (docs): 文檔修改
- 測試 (test): 測試相關
```

---

### 分支命名規範

```bash
# ✅ 好的分支名稱
feature/crawler-uniqlo
feature/frontend-login-page
bugfix/database-charset
hotfix/demo-crash

# ❌ 不好的分支名稱
test
new-branch
john-work
temp
fix123
```

---

### Pull Request (PR) 流程 (推薦)

如果想更專業,可以使用 GitHub PR:

```bash
# 1. 在功能分支開發
git checkout -b feature/crawler-uniqlo
# ... 開發 ...
git push origin feature/crawler-uniqlo

# 2. 到 GitHub 網站建立 Pull Request
#    - 從 feature/crawler-uniqlo 合併到 develop
#    - 寫清楚做了什麼
#    - 請組員 review

# 3. 組員 review 後,在網頁上點擊 Merge

# 4. 刪除分支 (GitHub 會提示)
```

**PR 優點:**
- ✅ 組員可以 review 程式碼
- ✅ 有討論記錄
- ✅ 自動檢查衝突
- ✅ 可以設定自動測試

---

## 🏢 業界實務比較

### 學生專題 vs 業界開發

| 項目 | 學生專題 (你們) | 業界實務 |
|------|----------------|----------|
| **環境** | 本地 Docker | AWS/Azure/GCP |
| **分支策略** | 簡化 Git Flow | Git Flow / Trunk-Based |
| **部署** | 手動 | CI/CD 自動化 |
| **測試** | 手動測試 | 自動化測試 (90%+) |
| **Code Review** | 可選 | 必須 (PR review) |
| **資料庫** | 每人本地 | 共用開發環境 + 正式環境 |

---

### 業界常見流程

#### 1. 環境分離

```
開發環境 (Development)
  ↓ 自動部署
測試環境 (Staging)
  ↓ 手動批准
正式環境 (Production)
```

**對應到你們的專案:**
```
本地 Docker (Development)    ← 你們目前在這裡
  ↓
develop 分支 (Staging)       ← 可以考慮在 EC2 上架設
  ↓
main 分支 (Production)       ← Demo 給老師看的版本
```

---

#### 2. CI/CD 自動化

**業界使用工具:**
- GitHub Actions
- GitLab CI
- Jenkins
- CircleCI

**自動執行:**
- ✅ 跑測試
- ✅ 檢查程式碼風格
- ✅ 建置 Docker image
- ✅ 部署到伺服器

**你們可以先學的:**
```yaml
# .github/workflows/test.yml
name: 測試

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: 執行測試
        run: |
          docker-compose up -d
          python3 -m pytest tests/
```

---

#### 3. Code Review 文化

**業界規則:**
- 所有程式碼必須經過至少 1-2 人 review
- 使用 Pull Request
- 有 checklist

**你們可以採用:**
```markdown
PR Checklist:
- [ ] 程式碼可以運行
- [ ] 沒有明顯的 bug
- [ ] 有註解說明複雜邏輯
- [ ] 資料庫 migration 已測試
- [ ] 更新了相關文檔
```

---

## 🚀 進階:使用 AWS EC2 (老師教完後)

### 為什麼需要伺服器?

**目前問題:**
- ❌ 每個人的資料庫不同步
- ❌ 無法同時測試整合功能
- ❌ Demo 時要確保本地環境正常

**使用伺服器後:**
- ✅ 共用開發資料庫
- ✅ 24/7 運行,隨時測試
- ✅ 所有人看到同樣結果
- ✅ Demo 時更穩定

---

### 簡易架構 (未來可用)

```
GitHub Repository
  ↓ git pull
AWS EC2 (開發伺服器)
  ├─ Docker: MySQL (共用資料庫)
  ├─ Docker: Flask App (後端 API)
  └─ Nginx (前端靜態檔案)
  ↓
組員透過網址訪問
  - http://your-ec2-ip:5000 (API)
  - http://your-ec2-ip (前端)
```

**設定步驟 (簡化版):**
```bash
# 1. 在 EC2 上
git clone <your-repo>
cd AI-project-crawler-test

# 2. 啟動服務
docker-compose up -d

# 3. 匯入資料庫 (一次即可)
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

# 4. 開放防火牆
# AWS Console → Security Groups → 開放 3306, 5000 port

# 5. 組員連接
# MySQL: ec2-xx-xx-xx-xx.compute.amazonaws.com:3306
# API: http://ec2-xx-xx-xx-xx.compute.amazonaws.com:5000
```

---

## 📝 立即行動計畫

### Week 1: 清理分支

```bash
# 1. 建立 develop 分支
git checkout main
git checkout -b develop
git push origin develop

# 2. 合併重要分支到 develop
git checkout develop
git merge origin/Crawler&Detection
git merge origin/frontend
# ... 解決衝突
git push origin develop

# 3. 通知組員切換到 develop
# 「從現在開始,大家都在 develop 分支上工作」
```

---

### Week 2-4: 建立新習慣

**每個人每天:**
```bash
# 早上開始工作
git checkout develop
git pull origin develop

# 如果要開發新功能
git checkout -b feature/your-feature
# ... 開發 ...
git push origin feature/your-feature

# 功能完成
git checkout develop
git pull origin develop
git merge feature/your-feature
git push origin develop
git branch -d feature/your-feature
```

---

### Demo 前: 發布到 main

```bash
# 1. 測試 develop
git checkout develop
git pull origin develop
# 跑完所有測試

# 2. 合併到 main
git checkout main
git merge develop
git push origin main

# 3. 建立標籤
git tag -a v1.0-midterm -m "期中 Demo"
git push origin v1.0-midterm
```

---

## ✅ 檢查清單

### 建立規範後,每次提交前確認:

- [ ] 在正確的分支上 (develop 或 feature/*)
- [ ] Commit message 清楚明確
- [ ] 程式碼可以運行
- [ ] 沒有 console.log 或 print debug 訊息
- [ ] 已經 pull 最新的 develop
- [ ] 衝突已解決
- [ ] 功能分支合併後已刪除

---

## 🎓 學習資源

### 推薦工具

1. **GitKraken** - 視覺化 Git 工具 (免費學生版)
2. **GitHub Desktop** - GitHub 官方工具
3. **SourceTree** - Atlassian 的 Git GUI

### 推薦學習

1. **GitHub Skills** - https://skills.github.com/
2. **Learn Git Branching** - https://learngitbranching.js.org/
3. **Atlassian Git Tutorial** - https://www.atlassian.com/git/tutorials

---

## 📞 常見問題

### Q1: 我該在哪個分支工作?

**A:** 
- 日常開發:在 `develop` 或從 `develop` 開出的 `feature/*` 分支
- Demo 準備:在 `main` 分支
- 緊急修復:在 `hotfix/*` 分支

---

### Q2: 什麼時候該開新分支?

**A:**
- ✅ 開發新功能 (會改很多檔案)
- ✅ 實驗性的修改 (不確定會不會採用)
- ✅ 需要幾天才能完成的工作
- ❌ 修改一個小 bug (直接在 develop)
- ❌ 更新文檔 (直接在 develop)

---

### Q3: 如何避免衝突?

**A:**
1. 每天 pull develop
2. 功能分支不要存在超過一週
3. 經常合併 develop 到你的功能分支
4. 不同人負責不同檔案

---

### Q4: 資料庫更新該在哪個分支?

**A:** 
- 在 `develop` 分支匯出 `outfit_db_with_data.sql`
- 其他人從 `develop` pull 下來
- 保持一個「真相來源」

---

## 🎯 總結

### 立即採用 (Week 1)

1. ✅ 建立 `develop` 分支
2. ✅ 合併重要分支到 `develop`
3. ✅ 刪除舊的、不用的分支
4. ✅ 通知組員新的工作流程

### 逐步改善 (Week 2-4)

1. ✅ 使用 feature/* 命名規範
2. ✅ 功能完成就合併並刪除分支
3. ✅ 改善 commit message
4. ✅ 定期清理分支

### 進階目標 (學期後期)

1. 📚 學習 Pull Request
2. 🤖 設定 GitHub Actions
3. ☁️ 部署到 AWS EC2 (老師教完後)
4. 🧪 加入自動化測試

---

**記住:好的 Git 流程讓協作更順暢!** 🚀

**最後更新:** 2025-11-26  
**維護者:** liaoyiting
