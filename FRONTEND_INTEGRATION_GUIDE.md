# 🤝 前後端整合溝通指南

> **給前端組員的協作說明** - 如何將前端網頁整合到最新版專案

---

## 📊 當前專案狀態

### 後端 (你的部分) - 已完成 ✅

| 項目 | 狀態 | 分支 |
|------|------|------|
| 資料庫結構 | ✅ 完成 | develop/main |
| 50 個測試用戶 | ✅ 已匯入 | develop/main |
| 49,707 個商品資料 | ✅ 已匯入 | develop/main |
| Flask API 路由 | ✅ 已設定 | develop/main |
| AI 聊天機器人後端 | ✅ 已整合 | develop/main |
| Docker 環境 | ✅ 已優化 | develop/main |

**測試狀態**: 上週版本可以連接資料庫 ✅

---

### 前端 (組員的部分) - 需要整合 ⏳

| 檔案 | 位置 | 狀態 |
|------|------|------|
| 前端頁面 | `frontend` 分支 | ⏳ 尚未合併到 develop/main |
| 最新開發 | 組員本地 | ❓ 未知狀態 |

**問題**: 前端組員的最新網頁尚未推送，無法測試前後端連接

---

## 🎯 整合目標

### 需要達成的目標:
1. ✅ 前端頁面可以呼叫後端 API
2. ✅ AI 聊天機器人可以連接資料庫
3. ✅ 用戶登入功能正常運作
4. ✅ 商品推薦功能可以顯示資料

---

## 📋 給前端組員的推送建議

### 🚀 **方案 A: 推送到 develop 分支 (推薦)** ⭐

**適用情況**: 前端功能正在開發中，需要測試

```bash
# 前端組員執行步驟:

# 1. 確保在自己的分支
git status

# 2. 提交所有前端變更
git add app/static/*.html app/static/*.css app/static/*.js
git commit -m "feat: 更新前端頁面 - 聊天機器人/推薦/衣櫃介面"

# 3. 拉取最新的 develop 分支
git checkout develop
git pull origin develop

# 4. 合併自己的變更 (如果在其他分支)
git merge your-branch-name

# 5. 解決衝突 (如果有)
# 編輯衝突檔案...
git add .
git commit -m "merge: 整合前端更新到 develop"

# 6. 推送到 develop
git push origin develop
```

**優點**:
- ✅ 可以立即測試前後端整合
- ✅ 有問題可以快速修正
- ✅ 不影響 main 分支的穩定性

---

### 🎖️ **方案 B: 推送到 main 分支 (穩定版才用)**

**適用情況**: 前端功能已完整測試，確認無誤

```bash
# 前端組員執行步驟:

# 1. 先推送到 develop 並測試
(執行方案 A 的步驟)

# 2. 確認測試通過後
git checkout main
git pull origin main

# 3. 合併 develop 到 main
git merge develop --no-ff -m "release: 前端功能整合 - 完成測試"

# 4. 推送到 main
git push origin main
```

**重要**: ⚠️ **只有測試完全通過才推送到 main！**

---

## 📁 需要推送的檔案清單

### 前端頁面檔案

```
✅ 必須推送:
app/static/
├── home.html              # 首頁
├── login.html             # 登入頁面
├── recommendation.html    # 推薦頁面
├── wardrobe.html          # 衣櫃管理
├── share.html             # 分享頁面
├── *.css                  # 所有樣式檔案
├── *.js                   # 所有 JavaScript 檔案
└── pic/                   # 圖片資源

app/templates/
├── index.html             # Jinja2 模板
└── page1.html             # 其他模板頁面

⚠️ 確認檔案:
app/app.py                 # 確認路由設定正確
```

### 不應該推送的檔案

```
❌ 不要推送:
- 個人的 .env 檔案 (包含 API keys)
- node_modules/ (如果有)
- __pycache__/ 
- .DS_Store (macOS)
- *.pyc (Python 編譯檔)
- venv/ 或 .venv/ (虛擬環境)
```

---

## 🔍 整合前檢查清單

### 前端組員自我檢查:

- [ ] **API 端點確認**: 前端呼叫的 API 路徑是否正確?
  ```javascript
  // 範例: 確認這些路徑
  fetch('/recommend', { method: 'POST', ... })
  fetch('/items', { method: 'GET', ... })
  fetch('/chat', { method: 'POST', ... })
  ```

- [ ] **靜態檔案路徑**: CSS/JS/圖片的路徑是否正確?
  ```html
  <!-- 確認路徑格式 -->
  <link href="/static/HomeCSS.css" rel="stylesheet">
  <script src="/static/Chat.js"></script>
  ```

- [ ] **資料庫連接測試**: 登入功能是否需要資料庫?
  - 測試帳號: `admin` / `admin123`
  - 測試帳號: `demo` / `demo123`

- [ ] **AI 聊天機器人**: 聊天介面是否連接到 `/chat` API?

- [ ] **商品推薦**: 推薦頁面是否可以顯示資料庫中的商品?

---

## 🧪 整合後測試步驟

### 測試流程 (你們一起執行):

```bash
# 1. 啟動 Docker 資料庫
docker-compose up -d

# 2. 確認資料庫有資料
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "SELECT COUNT(*) FROM items;"
# 應該顯示: 49707

# 3. 啟動 Flask 應用
python3 app/app.py

# 4. 測試前端頁面
# 瀏覽器訪問: http://localhost:5000
```

### 測試項目:

1. ✅ **登入功能**
   - 訪問 `http://localhost:5000/login.html`
   - 使用測試帳號: admin / admin123
   - 確認可以成功登入

2. ✅ **AI 聊天機器人**
   - 訪問聊天介面
   - 輸入訊息測試
   - 確認機器人可以回應

3. ✅ **商品推薦**
   - 訪問推薦頁面
   - 確認可以顯示商品
   - 確認推薦演算法運作

4. ✅ **衣櫃管理**
   - 確認可以新增/刪除衣物
   - 確認資料儲存到資料庫

---

## 💬 溝通訊息範本

### 給前端組員的訊息 (複製使用):

```
Hi [組員名稱],

我這邊已經完成後端和資料庫的整合,目前狀態:
✅ 資料庫: 50 個用戶 + 49,707 個商品資料
✅ Flask API: 所有路由已設定好
✅ AI 聊天機器人: 後端已整合 Google Gemini
✅ Docker 環境: 已優化並可正常運作

現在需要整合你的前端頁面來測試完整功能。請問:

1. 你的前端頁面目前的狀態如何?是否已完成測試?
2. 哪些檔案需要推送? (login.html, home.html, recommendation.html 等)
3. 是否有使用新的 API 端點?請提供一下路徑

建議推送流程:
- 先推送到 develop 分支
- 我們一起測試前後端連接
- 確認無誤後再合併到 main

我準備了詳細的整合指南,可以參考這個檔案:
📄 FRONTEND_INTEGRATION_GUIDE.md

測試帳號:
- admin / admin123
- demo / demo123

如果有問題隨時問我! 🙋‍♂️
```

---

## 🔧 常見問題解決

### Q1: 前端呼叫 API 出現 CORS 錯誤?

**解決方法**: 檢查 `app/app.py` 是否有設定 CORS

```python
from flask_cors import CORS
app = Flask(__name__)
CORS(app)  # 允許跨域請求
```

---

### Q2: 靜態檔案 404 找不到?

**解決方法**: 確認 Flask 靜態檔案設定

```python
app = Flask(__name__, 
    static_folder='static',
    static_url_path='/static'
)
```

檔案路徑應為: `/static/home.html` 而非 `/home.html`

---

### Q3: 資料庫連接失敗?

**檢查清單**:
```bash
# 1. 確認 Docker 容器運行
docker ps | grep outfit-mysql

# 2. 測試資料庫連接
docker exec outfit-mysql mysql -uroot -prootpassword -e "SELECT 1;"

# 3. 檢查 Flask 資料庫設定
# 應為: mysql://root:rootpassword@localhost:3306/outfit_db
```

---

### Q4: AI 聊天機器人無回應?

**檢查清單**:
- [ ] `.env` 檔案是否有設定 `GOOGLE_AI_API_KEY`?
- [ ] API Key 是否有效?
- [ ] 前端是否正確呼叫 `/chat` API?
- [ ] 檢查 Flask 終端的錯誤訊息

---

## 📅 建議的整合時程

### 階段 1: 推送與同步 (30 分鐘)
- 前端組員推送最新檔案到 `develop`
- 你拉取最新的 `develop` 分支
- 解決可能的檔案衝突

### 階段 2: 本地測試 (1 小時)
- 一起啟動 Docker + Flask
- 測試所有前端頁面
- 記錄發現的問題

### 階段 3: 修正問題 (依問題複雜度)
- 前端修正介面問題
- 你修正後端 API 問題
- 反覆測試直到穩定

### 階段 4: 合併到 main (15 分鐘)
- 確認所有功能正常
- 合併 `develop` 到 `main`
- 通知其他組員更新

---

## 🎯 整合成功的標準

### 最低標準 (必須達成):
- ✅ 登入功能正常運作
- ✅ 頁面可以正確顯示
- ✅ 資料庫連接無錯誤
- ✅ 沒有 JavaScript 報錯

### 完整標準 (理想狀態):
- ✅ AI 聊天機器人可以對話
- ✅ 商品推薦功能運作正常
- ✅ 衣櫃管理可以新增/刪除
- ✅ 所有頁面樣式正確顯示
- ✅ 響應式設計在手機上正常

---

## 🔗 相關文檔

- 📚 [DATABASE_GUIDE.md](docs/DATABASE_GUIDE.md) - 資料庫使用說明
- 🚀 [QUICK_START.md](QUICK_START.md) - 快速啟動指南
- 👥 [TEAM_GUIDE.md](docs/TEAM_GUIDE.md) - 團隊協作規範
- 📝 [GIT_GUIDE.md](GIT_GUIDE.md) - Git 使用指南

---

## ✅ 檢查清單總結

### 前端組員 Todo:
- [ ] 整理要推送的前端檔案
- [ ] 提交到本地 Git
- [ ] 推送到 `develop` 分支
- [ ] 通知你已經推送

### 你的 Todo:
- [ ] 拉取最新的 `develop` 分支
- [ ] 確認 Docker 資料庫運行
- [ ] 啟動 Flask 應用
- [ ] 協助測試前端功能

### 一起 Todo:
- [ ] 測試登入功能
- [ ] 測試 AI 聊天機器人
- [ ] 測試商品推薦
- [ ] 測試衣櫃管理
- [ ] 確認所有功能正常
- [ ] 合併到 `main` 分支

---

**建立日期**: 2025-11-26  
**維護人**: liaoyiting (後端) + [前端組員名稱]  
**狀態**: 📌 等待前端整合

---

💡 **記住**: develop 是開發測試分支，main 是穩定發布分支。先在 develop 測試通過，再推送到 main！
