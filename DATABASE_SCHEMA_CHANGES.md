# 資料庫欄位刪除變更記錄

**日期**: 2025-12-03  
**變更類型**: 刪除 items 表格欄位  
**影響檔案**: 
- `init/01_schema_only.sql`
- `init/00_init_with_data.sql`

---

## 📋 變更內容

### 從 `items` 表格中刪除的欄位

| 欄位名稱 | 原始類型 | 刪除原因 |
|---------|---------|---------|
| `size` | VARCHAR(20) | 不需要尺寸資訊 |
| `price` | DECIMAL(10,2) | 使用 price_text 欄位取代 |
| `description` | TEXT | 不需要詳細描述 |

---

## ✅ 更新後的 items 表格結構

```sql
CREATE TABLE items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  category VARCHAR(100) DEFAULT NULL COMMENT 'top, bottom, shoes, accessories',
  color VARCHAR(50) DEFAULT NULL,
  image_url VARCHAR(255) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  sku VARCHAR(50) UNIQUE DEFAULT NULL,
  gender VARCHAR(20) DEFAULT NULL COMMENT '男, 女, 中性, 男孩, 女孩',
  clothing_type VARCHAR(50) DEFAULT NULL,
  length VARCHAR(20) DEFAULT NULL COMMENT '短, 長, 中',
  price_text VARCHAR(20) DEFAULT NULL,
  source VARCHAR(50) DEFAULT 'manual' COMMENT 'manual, uniqlo, styles_dataset, malefashion',
  
  INDEX idx_category (category),
  INDEX idx_color (color),
  INDEX idx_gender (gender),
  INDEX idx_source (source),
  INDEX idx_sku (sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='單品表 - 支援多來源資料';
```

---

## 📊 保留的欄位清單 (11 個)

1. ✅ `id` - 主鍵
2. ✅ `name` - 商品名稱 (必填)
3. ✅ `category` - 分類 (top, bottom, shoes, accessories)
4. ✅ `color` - 顏色
5. ✅ `image_url` - 圖片網址
6. ✅ `created_at` - 建立時間
7. ✅ `sku` - 商品編號 (唯一)
8. ✅ `gender` - 性別 (男, 女, 中性, 男孩, 女孩)
9. ✅ `clothing_type` - 服裝類型
10. ✅ `length` - 長度 (短, 長, 中)
11. ✅ `price_text` - 價格文字 (保留此欄位而非 price)
12. ✅ `source` - 資料來源

---

## 🔧 影響分析

### 需要檢查的程式碼

以下程式碼可能需要更新，請確認是否有使用已刪除的欄位：

1. **Flask 後端**:
   - `app/langchain_agent.py` - AI 推薦邏輯
   - `app/blueprints/*/routes.py` - 各 Blueprint 路由
   - `app/blueprints/*/services.py` - 業務邏輯

2. **資料庫查詢**:
   ```python
   # 需要移除對以下欄位的引用
   # - item['size']
   # - item['price']
   # - item['description']
   ```

3. **前端模板**:
   - `app/templates/index.html`
   - `app/templates/recommendation.html`
   - 其他可能顯示商品資訊的頁面

4. **Pipeline 腳本**:
   - `pipeline/04_data_processing.py` - 資料處理
   - `pipeline/05_database_import.py` - 資料庫匯入

---

## ✅ 執行步驟

### 1. 已完成的變更 ✅
- [x] 更新 `init/01_schema_only.sql` - 刪除三個欄位定義
- [x] 更新 `init/00_init_with_data.sql` - 刪除三個欄位定義
- [x] 備份原始檔案 `init/00_init_with_data.sql.backup`

### 2. 需要執行的資料庫遷移

如果現有資料庫需要同步此變更，請執行：

```sql
-- 從現有 items 表格中刪除欄位
ALTER TABLE items DROP COLUMN size;
ALTER TABLE items DROP COLUMN price;
ALTER TABLE items DROP COLUMN description;
```

### 3. 建議的測試步驟

```bash
# 1. 停止現有容器
docker compose down

# 2. 重新建立資料庫 (使用更新後的 schema)
docker compose up -d mysql

# 3. 匯入資料 (如果需要)
docker exec -i outfit_db_container mysql -uroot -proot_password outfit_db < init/00_init_with_data.sql

# 4. 啟動應用
docker compose up -d flask

# 5. 驗證 AI 聊天機器人
curl -X POST http://localhost:5001/recommend_page -d "message=推薦上衣"
```

---

## ⚠️ 注意事項

1. **相容性**: 確保程式碼不再使用已刪除的欄位
2. **資料遷移**: 現有資料庫需要執行 ALTER TABLE 來移除欄位
3. **備份**: 已建立 `init/00_init_with_data.sql.backup` 備份
4. **測試**: 變更後需要完整測試 AI 推薦功能

---

## 📝 相關檔案

- ✅ `init/01_schema_only.sql` - 僅結構定義 (已更新)
- ✅ `init/00_init_with_data.sql` - 包含資料 (已更新)
- 📦 `init/00_init_with_data.sql.backup` - 原始備份
- 📄 本文件: `DATABASE_SCHEMA_CHANGES.md`
