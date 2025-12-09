# Items 表格 NULL 值填補完整指南

**目標**: 填補 items 表格的 `category`, `gender`, `color` 空值  
**資料筆數**: 44,708 筆  
**執行方式**: 分批處理 (每批 10 筆) 避免 token 溢出

---

## 📋 快速開始 (推薦)

### 一鍵執行所有腳本
```bash
cd /Users/liaoyiting/Desktop/stylerec/init/scripts
./run_fill_all.sh
```

**執行時間**: 約 15 分鐘  
**互動性**: 每個步驟間會詢問是否繼續  
**可恢復性**: ✅ 支援中斷後恢復

---

## 🔧 執行順序 (重要!)

### Step 1️⃣: 填補 category (依 clothing_type)
```bash
python3 fill_category_from_clothing_type.py
```

**處理邏輯**:
- 讀取 `clothing_type` 欄位 (如 "Tshirts", "Jeans")
- 映射到 `category` (如 "top", "bottom")
- 使用 9 大分類: top, bottom, shoes, accessories, dress, underwear, beauty, bags, other

**預期結果**:
- 填補約 33,576 筆 (75% 的記錄)
- 剩餘 ~11,132 筆空值 (沒有 `clothing_type` 的記錄)

**進度追蹤**:
- 檔案: `category_fill_progress.json`
- 日誌: `category_fill_log.txt`

---

### Step 2️⃣: 填補 gender (依 name 關鍵字)
```bash
python3 fill_gender_from_name.py
```

**處理邏輯**:
- 讀取 `name` 欄位 (如 "Men Casual Shirt", "Women Party Dress")
- 偵測關鍵字: Men/Women/Boy/Girl/Unisex
- 映射到 `gender`: 男/女/男孩/女孩/中性

**預期結果**:
- 填補約 42,427 筆 (95% 的記錄)
- 剩餘 ~2,281 筆空值 (無明確性別關鍵字)

**進度追蹤**:
- 檔案: `gender_fill_progress.json`
- 日誌: `gender_fill_log.txt`

---

### Step 3️⃣: 填補剩餘空值 (預設值)
```bash
python3 fill_remaining_nulls.py
```

**處理邏輯**:
- `category` 空值 → `'other'`
- `gender` 空值 → `'中性'`
- `color` 空值 → `'未分類'`

**前置檢查** (安全機制):
- 檢查 `category` 空值 > 20% → 警告 (建議先執行 Script 1)
- 檢查 `gender` 空值 > 10% → 警告 (建議先執行 Script 2)
- 需要用戶確認才能繼續

**預期結果**:
- 填補所有剩餘空值
- 最終空值數: 0

---

## 🛡️ 安全性保證

### ✅ 不會覆蓋已有資料
每個腳本都有保護機制:

**Script 1 & 2**: 使用 `WHERE id = %s` 精確更新
```sql
UPDATE items 
SET category = %s
WHERE id = %s  -- ✅ 只更新指定記錄
```

**Script 3**: 使用 `WHERE ... IS NULL` 條件
```sql
UPDATE items 
SET category = 'other' 
WHERE category IS NULL OR category = ''  -- ✅ 只填補空值
```

### 🔄 可重複執行
所有腳本都支援重複執行:
- Script 1 & 2: 會跳過已處理的記錄 (檢查進度檔)
- Script 3: 只更新空值,不會覆蓋已有資料

---

## 📊 預期執行結果

### 填補前 (初始狀態)
```sql
SELECT 
  COUNT(*) as 總筆數,
  SUM(CASE WHEN category IS NULL THEN 1 ELSE 0 END) as category空值,
  SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) as gender空值,
  SUM(CASE WHEN color IS NULL THEN 1 ELSE 0 END) as color空值
FROM items;
```

**預期輸出**:
```
總筆數: 44,708
category空值: 11,132 (25%)
gender空值: 2,281 (5%)
color空值: 80 (0.2%)
```

---

### 執行 Script 1 後
```
總筆數: 44,708
category空值: ~11,132 → ~3,000 (減少約 8,000 筆)
gender空值: 2,281 (不變)
color空值: 80 (不變)
```

---

### 執行 Script 2 後
```
總筆數: 44,708
category空值: ~3,000 (不變)
gender空值: 2,281 → ~500 (減少約 1,781 筆)
color空值: 80 (不變)
```

---

### 執行 Script 3 後 (最終狀態)
```
總筆數: 44,708
category空值: 0 ✅
gender空值: 0 ✅
color空值: 0 ✅
```

---

## 🔍 驗證方法

### 方法 1: 檢查空值數量
```sql
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT 
  COUNT(*) as 總筆數,
  SUM(CASE WHEN category IS NULL THEN 1 ELSE 0 END) as category空值,
  SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) as gender空值,
  SUM(CASE WHEN color IS NULL THEN 1 ELSE 0 END) as color空值
FROM items;
"
```

### 方法 2: 隨機抽樣檢查
```sql
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT id, name, category, gender, color, clothing_type
FROM items
ORDER BY RAND()
LIMIT 20;
"
```

### 方法 3: 檢查預設值分布
```sql
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT 
  category,
  COUNT(*) as 數量,
  ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM items), 2) as 百分比
FROM items
GROUP BY category
ORDER BY 數量 DESC;
"
```

---

## ⚠️ 常見問題

### Q1: 執行中斷了怎麼辦?
**A**: 所有腳本都支援恢復執行!
- 進度保存在 `*_progress.json` 檔案
- 重新執行腳本會從上次中斷處繼續
- 如需重新開始,刪除進度檔即可:
  ```bash
  rm category_fill_progress.json
  rm gender_fill_progress.json
  ```

### Q2: 可以跳過某個步驟嗎?
**A**: 不建議!
- Script 3 有前置檢查,會警告你空值過多
- 建議依順序執行以獲得最佳結果
- 如果真的要跳過,執行時選擇 'y' 強制繼續

### Q3: 執行時間太久可以加速嗎?
**A**: 可以調整批次大小 (但有風險)
```python
# 在腳本開頭修改 (預設 10)
BATCH_SIZE = 50  # 改為 50 可加速 5 倍

# ⚠️ 注意: 批次太大可能導致 token 溢出
```

### Q4: 如何確認沒有資料被錯誤覆蓋?
**A**: 檢查衝突報告
```bash
cat /Users/liaoyiting/Desktop/stylerec/init/scripts/SCRIPT_CONFLICT_CHECK.md
```

---

## 📁 相關檔案

### 腳本檔案
```
init/scripts/
├── run_fill_all.sh                      # 主執行腳本 ⭐
├── fill_category_from_clothing_type.py  # Step 1
├── fill_gender_from_name.py             # Step 2
├── fill_remaining_nulls.py              # Step 3
└── SCRIPT_CONFLICT_CHECK.md             # 衝突檢查報告
```

### 進度檔案 (自動生成)
```
init/scripts/
├── category_fill_progress.json          # Step 1 進度
├── gender_fill_progress.json            # Step 2 進度
├── category_fill_log.txt                # Step 1 日誌
└── gender_fill_log.txt                  # Step 2 日誌
```

---

## 🎯 執行建議

### 最佳實踐
1. ✅ **使用 `run_fill_all.sh`** - 自動處理所有步驟
2. ✅ **在非高峰時段執行** - 避免影響資料庫效能
3. ✅ **備份資料庫** (可選) - 執行前先備份
   ```bash
   cd /Users/liaoyiting/Desktop/stylerec/scripts
   ./export_database.sh
   ```
4. ✅ **監控執行過程** - 觀察終端輸出,確認無錯誤

### 備份資料庫 (可選,但建議)
```bash
# 使用專案提供的備份腳本
cd /Users/liaoyiting/Desktop/stylerec/scripts
./export_database.sh

# 或手動備份
docker exec outfit-mysql mysqldump -uroot -prootpassword outfit_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## 📞 需要協助?

### 檢查日誌
```bash
# 檢查 category 填補日誌
tail -f /Users/liaoyiting/Desktop/stylerec/init/scripts/category_fill_log.txt

# 檢查 gender 填補日誌
tail -f /Users/liaoyiting/Desktop/stylerec/init/scripts/gender_fill_log.txt
```

### 檢查進度
```bash
# 檢查當前處理到哪一筆
cat /Users/liaoyiting/Desktop/stylerec/init/scripts/category_fill_progress.json
cat /Users/liaoyiting/Desktop/stylerec/init/scripts/gender_fill_progress.json
```

---

**文件版本**: v1.0  
**最後更新**: 2024-12-09  
**維護者**: AI Project Team
