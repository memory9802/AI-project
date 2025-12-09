# 資料庫管理原則 (Database Management Principles)

## 📋 核心原則

### 🎯 唯一真實來源 (Single Source of Truth)

**`init/00_init_with_data.sql` 是資料庫的唯一權威來源**

- ✅ 包含完整的表格結構定義
- ✅ 包含完整的測試資料
- ✅ 包含所有視圖 (Views) 定義
- ✅ 包含所有觸發器 (Triggers) 定義
- ✅ 隨時保持最新狀態

---

## 🚀 使用情境

### 新成員加入專案

```bash
# 步驟 1: 啟動 MySQL 容器
docker-compose up -d mysql

# 步驟 2: 執行 00.sql 初始化資料庫
mysql -h 127.0.0.1 -P 3306 -u root -p outfit_db < init/00_init_with_data.sql
# 或使用 DBeaver 直接執行 00.sql

# 完成!資料庫結構和測試資料已就緒
```

### 資料庫結構變更

當需要修改資料庫結構時 (新增表格/欄位/視圖/觸發器):

1. **直接修改 `00_init_with_data.sql`**
2. **測試修改後的 SQL**
3. **同步更新 `01_schema_only.sql.example`** (僅結構定義,供參考)
4. **提交變更到 Git**

```bash
# 修改 00.sql
vim init/00_init_with_data.sql

# 測試 (重新初始化資料庫)
docker-compose restart mysql
mysql -h 127.0.0.1 -P 3306 -u root -p outfit_db < init/00_init_with_data.sql

# 同步到 01.example (僅結構)
# (由團隊維護,保持與 00.sql 結構一致)

# 提交 Git
git add init/00_init_with_data.sql init/01_schema_only.sql.example
git commit -m "feat(db): 更新資料庫結構 - [描述變更]"
git push
```

---

## 📁 檔案說明

### `00_init_with_data.sql` ⭐ (主要檔案)

**用途**: 唯一完整的資料庫初始化檔案

**內容**:
- ✅ 完整表格結構定義 (7 張表格)
  - users (使用者表)
  - items (單品表)
  - user_wardrobe (使用者衣櫃)
  - partner_products (合作夥伴商品)
  - conversation_history (對話歷史)
  - rating (評分表 - 多態關聯)
  - item_stats (評分統計快取)

- ✅ 完整測試資料 (INSERT 語句)
  - 5 個測試使用者
  - 175+ 商品資料
  - 測試評分資料
  - 對話歷史範例

- ✅ 3 個視圖定義
  - v_item_ratings (統一評分統計)
  - v_items_with_ratings (商品帶權重)
  - v_wardrobe_with_ratings (衣櫃帶權重)

- ✅ 3 個觸發器
  - after_rating_insert (自動更新統計)
  - after_rating_update (自動更新統計)
  - after_rating_delete (自動更新統計)

**誰使用**: 所有團隊成員

**何時使用**: 
- 初次設定開發環境
- 重置資料庫到乾淨狀態
- 同步最新資料庫結構

---

### `01_schema_only.sql.example` (參考檔案)

**用途**: 僅供參考的資料庫結構定義 (不含資料)

**內容**:
- ✅ 完整表格結構定義 (與 00.sql 相同)
- ✅ 視圖定義
- ✅ 觸發器定義
- ❌ 不含測試資料 (無 INSERT 語句)

**誰使用**: 
- 想快速查看資料庫結構的開發者
- CI/CD 工具 (如需要純結構檔案)

**何時使用**: 
- 僅查閱結構,不需要資料
- 文檔參考

**重要**: 此檔案由團隊維護,必須與 `00.sql` 的結構保持同步

---

## ⚠️ 禁止事項

### ❌ 不要建立分散的遷移腳本

**錯誤做法**:
```
init/
  00_init_with_data.sql        ← 基礎結構
  migration_v1.sql             ← ❌ 禁止!
  migration_v2.sql             ← ❌ 禁止!
  migration_rating_system.sql  ← ❌ 禁止!
```

**原因**: 
- 無法保證執行順序
- 容易遺漏某個遷移腳本
- 新成員難以理解完整結構
- 團隊成員資料庫狀態不一致

**正確做法**: 直接修改 `00_init_with_data.sql`

---

### ❌ 不要在本地直接修改資料庫結構

**錯誤做法**:
```sql
-- 在 DBeaver 或 MySQL CLI 直接執行
ALTER TABLE items ADD COLUMN new_field VARCHAR(50);
```

**原因**:
- 其他團隊成員無法同步
- Git 無法追蹤變更
- 容易造成資料庫結構不一致

**正確做法**: 
1. 修改 `00_init_with_data.sql`
2. 提交 Git
3. 團隊成員重新執行 `00.sql`

---

## 🔄 同步流程

### 團隊成員 A 修改資料庫結構

```bash
# A: 修改 00.sql
vim init/00_init_with_data.sql

# A: 測試
docker-compose restart mysql
mysql -h 127.0.0.1 -P 3306 -u root -p outfit_db < init/00_init_with_data.sql

# A: 更新 01.example
# (移除 INSERT 語句,保留結構)

# A: 提交
git add init/00_init_with_data.sql init/01_schema_only.sql.example
git commit -m "feat(db): 新增 xxx 欄位到 items 表格"
git push
```

### 團隊成員 B 同步資料庫

```bash
# B: 拉取最新程式碼
git pull

# B: 重新初始化資料庫
docker-compose restart mysql
mysql -h 127.0.0.1 -P 3306 -u root -p outfit_db < init/00_init_with_data.sql

# 完成!資料庫已同步
```

---

## 📊 當前資料庫狀態

### 最後更新: 2025-12-09

**表格數**: 7 張
- users (使用者表)
- items (單品表) - 175+ 商品
- user_wardrobe (使用者衣櫃)
- partner_products (合作夥伴商品)
- conversation_history (對話歷史)
- rating (評分表 - 多態關聯)
- item_stats (評分統計快取)

**視圖數**: 3 個
- v_item_ratings (統一評分統計)
- v_items_with_ratings (商品帶權重)
- v_wardrobe_with_ratings (衣櫃帶權重)

**觸發器數**: 3 個
- after_rating_insert
- after_rating_update
- after_rating_delete

**測試資料**:
- ✅ 5 個測試使用者 (testuser1-5)
- ✅ 175+ UNIQLO 商品 (含顏色分析)
- ✅ 評分測試資料
- ✅ 對話歷史範例

---

## 🛠️ 常見問題

### Q1: 我想新增一個表格,該怎麼做?

**A**: 
1. 在 `00_init_with_data.sql` 中新增表格定義
2. 在 `00_init_with_data.sql` 中新增測試資料 (如需要)
3. 測試完整的 `00.sql`
4. 同步更新 `01_schema_only.sql.example`
5. 提交 Git

### Q2: 我想修改某個欄位,該怎麼做?

**A**: 
1. 在 `00_init_with_data.sql` 中找到表格定義
2. 修改欄位定義 (例如: 改變類型、長度、預設值)
3. 如果有相關的 INSERT 語句,一併修改
4. 測試完整的 `00.sql`
5. 同步更新 `01_schema_only.sql.example`
6. 提交 Git

### Q3: 為什麼不使用 migration 腳本?

**A**: 
- 因為專案處於開發階段,頻繁變更結構
- 使用 `00.sql` 作為唯一來源更簡單直接
- 避免 migration 腳本累積過多導致維護困難
- 團隊成員可以快速獲得一致的資料庫狀態

**未來**: 當專案進入生產環境後,可考慮使用 migration 工具 (如 Alembic, Flyway)

### Q4: 我可以刪除 `01_schema_only.sql.example` 嗎?

**A**: 
- 可以,但不建議
- `01.example` 提供快速查看結構的方式 (不用捲動大量 INSERT 語句)
- 建議保留,但必須與 `00.sql` 保持同步

### Q5: 如何確認我的資料庫與團隊一致?

**A**:
```bash
# 重新執行 00.sql 即可
docker-compose restart mysql
mysql -h 127.0.0.1 -P 3306 -u root -p outfit_db < init/00_init_with_data.sql
```

---

## 📝 更新歷史

### 2025-12-09
- ✅ 統整評分系統擴展到 `00.sql`
- ✅ 刪除 `migration_rating_system.sql`
- ✅ 更新 `01_schema_only.sql.example`
- ✅ 建立此管理原則文檔

### 2025-12-05
- ✅ 初始化資料庫結構 (6 張表格)
- ✅ 匯入 175+ UNIQLO 商品資料
- ✅ 建立 5 個測試使用者

---

## 🎓 團隊協作建議

1. **每次 Pull 後檢查 `init/` 資料夾**
   - 如果有變更,重新執行 `00.sql`

2. **修改資料庫前先溝通**
   - 避免多人同時修改同一張表格
   - 使用 Git branch 隔離變更

3. **測試後再提交**
   - 確保 `00.sql` 可以完整執行
   - 確保 `01.example` 與 `00.sql` 結構一致

4. **使用有意義的 commit message**
   ```
   feat(db): 新增 xxx 表格
   fix(db): 修正 yyy 欄位類型
   refactor(db): 重構 zzz 視圖
   ```

---

## 📞 聯絡資訊

如有任何資料庫相關問題,請聯絡:
- 技術負責人: [填寫負責人]
- GitHub Issues: [專案 Issues 連結]

---

**最後更新**: 2025-12-09  
**維護者**: StyleRec 團隊
