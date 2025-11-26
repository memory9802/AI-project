# 📝 文檔撰寫原則

> **重要準則**: 保持文檔簡潔，避免過多 .md 檔案造成混亂

---

## 🎯 核心原則

### 1. **最小化文檔數量**
- ❌ **不要**: 為每個小變更或階段性更新創建新的 .md 檔案
- ✅ **要做**: 保持主要說明在 `README.md`，只為主要功能創建獨立文檔

### 2. **一個功能一個文檔**
```
✅ 正確範例:
├── README.md              # 專案總覽
├── GIT_GUIDE.md          # Git 功能完整指南
├── DATABASE_GUIDE.md     # 資料庫功能完整指南
└── CRAWLER_GUIDE.md      # 爬蟲功能完整指南

❌ 錯誤範例 (避免):
├── GIT_BASICS.md
├── GIT_ADVANCED.md
├── GIT_COMMANDS.md
├── GIT_WORKFLOWS.md
├── GIT_TROUBLESHOOTING.md
└── GIT_TIPS.md           # 太多分散的文件!
```

### 3. **階段性變更管理**
- ❌ **不要**: 創建 `PHASE1_REPORT.md`, `PHASE2_REPORT.md`, `UPDATE_20251126.md` 等
- ✅ **要做**: 使用 Git commit 記錄變更歷史
- ✅ **要做**: 在 `README.md` 的「更新紀錄」章節簡單記錄

---

## 📂 標準文檔結構

### 主目錄 (3-5 個核心文檔)
```
AI-project/
├── README.md              ⭐ 專案總覽 (必須)
├── QUICK_START.md         ⭐ 快速開始 (可選但推薦)
├── GIT_GUIDE.md           📚 Git 完整指南
├── CHANGELOG.md           📝 變更記錄 (可選)
└── CONTRIBUTING.md        👥 貢獻指南 (可選)
```

### docs/ 目錄 (功能性文檔)
```
docs/
├── DATABASE_GUIDE.md      📚 資料庫完整指南
├── CRAWLER_GUIDE.md       📚 爬蟲完整指南
├── TEAM_GUIDE.md          📚 團隊協作指南
├── API_REFERENCE.md       📚 API 文檔 (如需要)
└── TECHNICAL_SETUP.md     🔧 技術規格 (進階)
```

### 子目錄 README (說明性)
```
init/README.md             📁 資料庫檔案說明
scripts/README.md          📁 腳本使用說明 (如需要)
```

**原則**: 主目錄 + docs/ 合計不超過 **10 個** .md 檔案

---

## ✅ 何時創建新文檔

### 應該創建新文檔的情況:
1. ✅ **新的主要功能** (例如: 新增 API 模組 → `API_GUIDE.md`)
2. ✅ **獨立的技術主題** (例如: 部署流程 → `DEPLOYMENT.md`)
3. ✅ **需要詳細說明的子系統** (例如: 測試框架 → `TESTING.md`)

### 不應該創建新文檔的情況:
1. ❌ 功能小更新 (直接更新對應的 GUIDE.md)
2. ❌ 階段性變更報告 (使用 Git commit message)
3. ❌ 臨時性說明 (加到 README.md 或對應 GUIDE.md)
4. ❌ 問題追蹤 (使用 GitHub Issues)
5. ❌ 會議記錄 (使用其他工具或私人筆記)

---

## 📝 更新現有文檔的流程

### 範例: 資料庫新增功能

```bash
# ❌ 錯誤做法 - 創建新文件
docs/DATABASE_NEW_FEATURE_20251126.md
docs/DATABASE_UPDATE.md
docs/DATABASE_MIGRATION_GUIDE.md

# ✅ 正確做法 - 更新現有文件
1. 編輯 docs/DATABASE_GUIDE.md
2. 在適當章節加入新功能說明
3. 更新目錄 (如果有)
4. Git commit: "docs: 資料庫指南新增 XXX 功能說明"
```

### 更新 README.md 的時機

```markdown
## 📝 更新紀錄

- **2025-11-26** - 資料庫功能增強
  - 新增 XXX 功能
  - 優化 YYY 效能
  - 詳細說明請參考 [DATABASE_GUIDE.md](docs/DATABASE_GUIDE.md)
```

---

## 🔄 文檔維護原則

### 1. **合併相似內容**
當發現多個文檔內容重疊時:
```bash
# 評估是否可以合併
docs/GIT_BASICS.md + docs/GIT_COMMANDS.md 
→ 合併為 GIT_GUIDE.md (包含基礎與指令兩部分)
```

### 2. **定期檢查**
每 1-2 個月檢查:
- [ ] 是否有過時的文檔?
- [ ] 是否有重複的內容?
- [ ] 是否有可以合併的文檔?

### 3. **刪除而非歸檔**
```bash
# ❌ 不要創建 archive/ 資料夾
archive/OLD_DATABASE_GUIDE.md
archive/DEPRECATED_API.md

# ✅ 直接刪除過時文檔
git rm docs/OLD_DATABASE_GUIDE.md
# Git 歷史會保留完整記錄
```

---

## 💡 最佳實踐

### 文檔命名規範
```
✅ 好的命名:
- DATABASE_GUIDE.md      (清楚、簡潔)
- API_REFERENCE.md       (標準命名)
- QUICK_START.md         (一目了然)

❌ 避免的命名:
- database_guide_v2_final_really_final.md  (版本在檔名)
- 資料庫使用說明_20251126.md             (日期在檔名)
- db_guide_temp_backup.md                  (臨時檔案)
```

### 文檔結構建議
```markdown
# 功能指南標準結構

## 📖 目錄
(章節清單)

## 🎯 概述
(功能簡介)

## 🚀 快速開始
(最簡單的使用方式)

## 📚 詳細說明
(完整功能說明)

## 🆘 常見問題
(FAQ)

## 🔗 相關文檔
(交叉引用)
```

---

## 📊 文檔數量參考

### 小型專案 (< 10k LOC)
- 主目錄: 2-3 個 .md (README + QUICK_START)
- docs/: 0-3 個 .md

### 中型專案 (10k-50k LOC)
- 主目錄: 3-5 個 .md
- docs/: 3-7 個 .md
- 總計: **6-12 個 .md**

### 大型專案 (> 50k LOC)
- 主目錄: 4-6 個 .md
- docs/: 8-15 個 .md
- 總計: **12-20 個 .md**

**黃金規則**: 如果文檔超過 20 個，就該考慮合併了！

---

## ✅ 檢查清單

在創建新文檔前，問自己:

- [ ] 這個內容是否可以加入現有文檔?
- [ ] 這是主要功能還是小更新?
- [ ] 這個文檔會長期維護還是暫時性的?
- [ ] 是否可以用 Git commit message 代替?
- [ ] 是否可以用 GitHub Issues/PR 代替?

**如果 3 個以上答案是「否」，才考慮創建新文檔。**

---

## 🎯 總結

### 記住三個原則:
1. **保持簡潔** - 主要說明在 README.md
2. **一功能一文檔** - 不要分散成多個小文件
3. **階段性不記錄** - 使用 Git commit 而非新建文檔

### 目標:
- ✅ 文檔易於查找
- ✅ 內容不重複
- ✅ 維護成本低
- ✅ 新人友善

---

**建立日期**: 2025-11-26  
**最後更新**: 2025-11-26  
**狀態**: 📌 團隊共識

---

*這份文檔本身也遵循「一個功能一個文檔」的原則 - 它是關於「文檔管理」這個功能的完整指南。*
