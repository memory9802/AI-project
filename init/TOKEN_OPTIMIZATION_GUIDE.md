# 🚀 避免 Token 爆量 - 完整指南

## 📊 當前狀態

### Items 表空值統計（44,708 筆資料）
- ✅ **sku**: 0% 空值（全部有值）
- ✅ **clothing_type**: 0% 空值（全部有值）
- ✅ **length**: 0% 空值（全部有值）
- ⚠️ **category**: 24.9% 空值（11,132 筆）- 已改善！原本 46.4%
- ⚠️ **color**: 0.2% 空值（80 筆）
- ⚠️ **gender**: 0.3% 空值（141 筆）
- ❌ **price**: 99.3% 空值（44,407 筆）- 只有 Uniqlo 資料有價格
- ❌ **image_url**: 99.3% 空值（44,407 筆）- 只有 Uniqlo 資料有圖片

---

## 💡 三種解決方案

### **方案 A：直接在 Docker MySQL 中處理（推薦）✨**

**優點**：
- ✅ 不需要修改 SQL 檔案
- ✅ 避免 token 問題
- ✅ 即時生效
- ✅ 可以分批處理

**操作步驟**：

#### 1. 填補 category 空值（剩餘 11,132 筆）

```sql
-- 在 DBeaver 中執行這些 SQL

-- 查看還有哪些 clothing_type 需要映射
SELECT clothing_type, COUNT(*) as count 
FROM items 
WHERE category IS NULL 
GROUP BY clothing_type 
ORDER BY count DESC;

-- 根據結果手動添加映射，例如：
UPDATE items SET category = 'top' WHERE category IS NULL AND clothing_type = 'Sweatshirts';
UPDATE items SET category = 'bottom' WHERE category IS NULL AND clothing_type = 'Jeans';
UPDATE items SET category = 'shoes' WHERE category IS NULL AND clothing_type = 'Sandals';
UPDATE items SET category = 'accessories' WHERE category IS NULL AND clothing_type = 'Jewellery';
```

#### 2. 填補其他小量空值

```sql
-- 填補 color 空值（只有 80 筆）
UPDATE items SET color = '未知' WHERE color IS NULL;

-- 填補 gender 空值（只有 141 筆）
UPDATE items SET gender = '中性' WHERE gender IS NULL;
```

#### 3. 處理 price 和 image_url（99.3% 空值）

**兩種選擇**：

**選項 1：保留空值**（推薦）
```sql
-- 不做任何處理
-- 在應用程式中處理：if item.price is None: display "價格未提供"
```

**選項 2：設定預設值**
```sql
-- 設定預設價格為 0（表示未定價）
UPDATE items SET price = 0 WHERE price IS NULL;

-- 設定預設圖片 URL
UPDATE items SET image_url = '/static/images/no-image.png' WHERE image_url IS NULL;
```

---

### **方案 B：使用 Python 腳本批次處理**

已經提供的腳本：`init/batch_process_items.py`

```bash
# 執行腳本
cd /Users/liaoyiting/Desktop/stylerec/init
python batch_process_items.py
```

**可以修改腳本來處理更多欄位**：
1. 打開 `init/batch_process_items.py`
2. 在 `main()` 函數中添加更多處理邏輯
3. 重新執行

---

### **方案 C：減少資料量（不推薦）**

如果真的需要減少資料：

```sql
-- 只保留有圖片的資料（Uniqlo 資料）
DELETE FROM items WHERE image_url IS NULL;

-- 或只保留特定來源
DELETE FROM items WHERE source != 'uniqlo';
```

⚠️ **警告**：刪除資料後無法復原！建議先備份。

---

## 🎯 推薦做法（最佳實踐）

### 1. **保持現狀，在應用程式中處理**

```python
# 在 Flask 應用中
def display_item(item):
    return {
        'name': item.name,
        'price': item.price if item.price else '價格未提供',
        'image': item.image_url if item.image_url else '/static/images/placeholder.png',
        'category': item.category if item.category else '其他'
    }
```

### 2. **只處理影響功能的空值**

```sql
-- 只填補會影響搜尋和分類的欄位
UPDATE items SET category = 'other' WHERE category IS NULL;
UPDATE items SET color = '未知' WHERE color IS NULL;
UPDATE items SET gender = '中性' WHERE gender IS NULL;

-- price 和 image_url 保持 NULL（在程式中處理顯示）
```

### 3. **建立視圖簡化查詢**

```sql
CREATE VIEW items_display AS
SELECT 
  id,
  name,
  COALESCE(category, 'other') as category,
  COALESCE(color, '未知') as color,
  COALESCE(gender, '中性') as gender,
  COALESCE(price, 0) as price,
  COALESCE(image_url, '/static/images/no-image.png') as image_url,
  clothing_type,
  length,
  source
FROM items;

-- 之後查詢使用
SELECT * FROM items_display WHERE category = 'top';
```

---

## 🔧 避免未來 Token 問題的技巧

### 1. **分批操作**
```bash
# 不要一次處理整個 7.4MB 檔案
# 改用分批 SQL
UPDATE items SET category = 'top' WHERE category IS NULL LIMIT 1000;
```

### 2. **使用資料庫工具**
- ✅ 使用 DBeaver 直接操作
- ✅ 使用 Python 腳本
- ❌ 不要讓 Copilot 處理超大檔案

### 3. **建立索引加速查詢**
```sql
-- 已經有的索引
SHOW INDEX FROM items;

-- 如果需要可以添加
CREATE INDEX idx_price ON items(price);
```

---

## 📋 快速檢查清單

- [x] DBeaver 連接正常
- [x] 表結構正確（12 個欄位，price 是 DECIMAL）
- [x] 44,708 筆資料正常載入
- [x] category 空值從 46.4% 降到 24.9%
- [ ] 決定如何處理剩餘的 category 空值
- [ ] 決定如何處理 price/image_url 空值（建議在程式中處理）
- [ ] 測試應用程式是否正常運作

---

## 🎓 總結建議

### **最佳實踐順序**：

1. **先在 DBeaver 驗證資料庫正常** ✅
   ```sql
   DESCRIBE items;
   SELECT COUNT(*) FROM items;
   ```

2. **填補關鍵空值（category, color, gender）**
   ```sql
   -- 使用上面的 SQL 命令
   UPDATE items SET category = '...' WHERE ...;
   ```

3. **保留 price/image_url 為 NULL**
   - 在 Flask 應用中處理顯示
   - 不需要填補所有空值

4. **如需更複雜處理，使用 Python 腳本**
   ```bash
   python init/batch_process_items.py
   ```

5. **測試應用程式**
   ```bash
   docker-compose up -d
   # 訪問 http://localhost:5000
   ```

---

## ❓ 常見問題

**Q: 為什麼 99.3% 的資料沒有 price/image_url？**  
A: 因為只有 Uniqlo 資料（301 筆）有完整資訊，其他 44,407 筆來自 styles_dataset 和 malefashion，沒有價格和圖片。

**Q: 需要刪除沒有圖片的資料嗎？**  
A: **不建議**。這些資料仍然有用（可以用於風格推薦、顏色搭配等）。在前端顯示時用預設圖片即可。

**Q: 如何避免 Copilot token 爆量？**  
A: 
1. 不要讓 Copilot 讀取整個大型 SQL 檔案
2. 使用 Python 腳本或 SQL 直接操作資料庫
3. 分批處理（LIMIT 1000）

**Q: items 表的欄位可以減少嗎？**  
A: 目前 12 個欄位已經很精簡了。建議保持現狀，只是某些欄位允許 NULL 即可。

---

## 🚀 下一步

1. **在 DBeaver 執行驗證 SQL**
2. **決定空值處理策略**
3. **測試 Flask 應用**
4. **考慮添加預設圖片**（`/static/images/placeholder.png`）

需要我幫忙執行任何步驟嗎？ 😊
