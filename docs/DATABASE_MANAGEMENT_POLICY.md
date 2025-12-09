# 資料庫管理原則

**最後更新**: 2025-12-09  
**適用專案**: StyleRec 穿搭推薦系統

---

## 📌 核心原則

### ⚠️ 唯一真相來源 (Single Source of Truth)

**`init/00_init_with_data.sql` 是唯一的完整資料庫定義檔案**

所有團隊成員必須使用這個檔案來初始化或重置資料庫。

---

## 🎯 為什麼這樣做?

### 問題背景
- ❌ 雲端資料庫無法讓多人同時修改
- ❌ 分散的測試資料檔案難以同步
- ❌ 本地開發環境資料不一致
- ❌ 新成員加入時難以快速建立相同環境

### 解決方案
- ✅ **00_init_with_data.sql**: 包含完整表格結構 + 測試資料
- ✅ 所有人下載後立即可用
- ✅ 確保團隊成員擁有相同的資料內容
- ✅ 方便進行功能測試和開發

---

## 📁 檔案說明

### 1. `00_init_with_data.sql` (主要檔案) ⭐
- **用途**: 唯一的完整資料庫定義檔案
- **內容**: 
  - 完整表格結構 (7 個表格)
  - 測試用戶資料 (5 個用戶)
  - 商品資料 (175 件商品)
  - 視圖定義 (3 個視圖)
  - 觸發器定義 (3 個觸發器)
- **使用時機**: 
  - 初次建立資料庫
  - 重置資料庫
  - 需要與團隊同步資料時
- **大小**: ~6.2MB

### 2. `01_schema_only.sql.example` (參考檔案)
- **用途**: 僅供查看資料庫結構
- **內容**: 純表格結構定義 (不含測試資料)
- **使用時機**: 
  - 快速查看表格欄位
  - 了解表格關聯
  - 文檔參考
- **⚠️ 注意**: 請勿直接匯入,僅供參考
- **大小**: ~16KB

### 3. 其他輔助檔案 (可選)
- `demo_test_data.sql`: 額外的示範資料 (可選匯入)
- `fix_rating_charset.sql`: 修復字元集問題 (問題發生時使用)
- `insert_demo_ratings.sql`: 插入示範評分資料 (測試用)

---

## 🔄 資料庫更新流程

### 原則: **永遠更新 00.sql,永遠不分散資料**

當需要修改資料庫結構時,請遵循以下步驟:

#### 1. 在本地開發環境測試
```bash
# 測試新的資料庫變更
mysql -u root -p outfit_db < your_changes.sql
```

#### 2. 更新 00_init_with_data.sql
- 直接在 `00_init_with_data.sql` 中修改
- 確保包含:
  - 新表格的結構定義
  - 新表格的測試資料
  - 相關的視圖/觸發器
  - 更新現有表格的 INSERT 語句

#### 3. 同步更新 01_schema_only.sql.example
- 僅更新表格結構部分
- 不包含 INSERT 語句
- 保持與 00.sql 的結構同步

#### 4. 測試完整性
```bash
# 建立測試資料庫驗證
mysql -u root -p -e "DROP DATABASE IF EXISTS test_outfit_db; CREATE DATABASE test_outfit_db;"
mysql -u root -p test_outfit_db < init/00_init_with_data.sql

# 檢查表格數量
mysql -u root -p test_outfit_db -e "SHOW TABLES;"

# 檢查資料筆數
mysql -u root -p test_outfit_db -e "SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM items;"
```

#### 5. 提交到 Git
```bash
git add init/00_init_with_data.sql init/01_schema_only.sql.example
git commit -m "feat(database): 更新資料庫結構 - [描述變更內容]"
git push origin develop
```

#### 6. 通知團隊
- 在團隊群組通知資料庫有更新
- 說明主要變更內容
- 提醒成員重新匯入 00.sql

---

## 👥 團隊成員使用指南

### 初次設置

```bash
# 1. Clone 專案
git clone https://github.com/RosyL666/stylerec.git
cd stylerec
git checkout develop

# 2. 建立資料庫並匯入
mysql -u root -p -e "CREATE DATABASE outfit_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p outfit_db < init/00_init_with_data.sql

# 3. 驗證
mysql -u root -p outfit_db -e "SHOW TABLES; SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM items;"
```

### 同步最新資料

當收到資料庫更新通知時:

```bash
# 1. 拉取最新代碼
git checkout develop
git pull origin develop

# 2. 重新匯入資料庫
mysql -u root -p outfit_db < init/00_init_with_data.sql

# 3. 驗證更新成功
mysql -u root -p outfit_db -e "SHOW TABLES;"
```

### 重置資料庫

當本地資料庫出現問題時:

```bash
# 完全重置
mysql -u root -p -e "DROP DATABASE IF EXISTS outfit_db; CREATE DATABASE outfit_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p outfit_db < init/00_init_with_data.sql
```

---

## 📊 當前資料庫結構

### 表格列表 (7 個)

1. **users** - 使用者表
   - 5 個測試用戶 (testuser1-5)
   - 密碼皆為: `password123`

2. **items** - 商品庫
   - 175 件商品
   - 來源: UNIQLO 爬蟲資料

3. **user_wardrobe** - 使用者衣櫃
   - 使用者上傳的個人衣物

4. **partner_products** - 合作夥伴商品
   - 可導流購買的外部商品

5. **conversation_history** - 對話歷史
   - AI 聊天機器人的對話記錄

6. **rating** - 評分表 (多態關聯)
   - 支援 items 和 user_wardrobe 雙來源
   - 包含評分值和評論

7. **item_stats** - 評分統計快取表
   - 自動更新的統計資料
   - 加速查詢效能

### 視圖列表 (3 個)

1. **v_item_ratings** - 統一評分統計
2. **v_items_with_ratings** - 商品庫帶權重
3. **v_wardrobe_with_ratings** - 使用者衣櫃帶權重

### 觸發器列表 (3 個)

1. **after_rating_insert** - 插入評分時更新統計
2. **after_rating_update** - 更新評分時更新統計
3. **after_rating_delete** - 刪除評分時更新統計

---

## 🚫 禁止事項

### ❌ 不要做的事情

1. **不要建立分散的測試資料檔案**
   - 所有測試資料必須統整到 `00_init_with_data.sql`

2. **不要只更新部分檔案**
   - 更新 00.sql 時,必須同步更新 01.example

3. **不要在雲端資料庫直接修改結構**
   - 所有結構變更必須先在本地測試
   - 測試完成後更新 00.sql 並推送到 Git

4. **不要使用舊版的 migration 檔案**
   - `migration_rating_system.sql` 已統整到 00.sql,請勿使用

5. **不要保留個人的測試資料在 Git**
   - 個人測試用的資料請在本地自行管理

---

## 🔍 檢查清單

### 更新資料庫前

- [ ] 在本地測試環境驗證變更
- [ ] 確認 00.sql 包含完整結構和資料
- [ ] 確認 01.example 包含相同的結構定義
- [ ] 執行完整性測試
- [ ] 記錄變更內容

### 更新資料庫後

- [ ] 提交到 Git (develop 分支)
- [ ] 通知團隊成員
- [ ] 更新相關文檔
- [ ] 在 CHANGELOG 記錄變更

---

## 📞 問題處理

### 遇到問題時

1. **檢查檔案版本**
   ```bash
   git log init/00_init_with_data.sql
   ```

2. **對比本地和遠端**
   ```bash
   git diff origin/develop init/00_init_with_data.sql
   ```

3. **查看提交歷史**
   ```bash
   git log --oneline --graph develop
   ```

4. **聯繫團隊**
   - 在群組詢問
   - 查看相關文檔
   - 檢查 Git 提交訊息

---

## 📚 相關文檔

- [資料庫指南](docs/DATABASE_GUIDE.md)
- [評分系統完整指南](docs/RATING_SYSTEM_COMPLETE_GUIDE.md)
- [快速開始](QUICK_START.md)
- [技術設置指南](docs/TECHNICAL_SETUP.md)

---

## 📝 變更記錄

### 2025-12-09
- ✅ 建立資料庫管理原則文檔
- ✅ 統整 migration_rating_system.sql 到 00.sql
- ✅ 更新 01_schema_only.sql.example
- ✅ 刪除已統整的 migration 檔案

### 2025-12-08
- ✅ 完成評分權重推薦系統
- ✅ 新增 rating 和 item_stats 表格
- ✅ 建立 3 個視圖和 3 個觸發器

---

**記住: `00_init_with_data.sql` 是唯一真相來源!** 🎯
