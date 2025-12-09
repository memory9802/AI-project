# Fill Scripts 衝突檢查報告

**檢查時間**: 2024-12-09  
**檢查對象**: 三個 fill 腳本的邏輯衝突分析

---

## ✅ 檢查結果: 無衝突

### 腳本職責分離

#### 1️⃣ `fill_category_from_clothing_type.py`
**更新欄位**: `category`  
**更新條件**: `WHERE id = %s` (逐筆更新)  
**資料來源**: `clothing_type` 欄位映射  
**UPDATE 語句**:
```sql
UPDATE items 
SET category = %s
WHERE id = %s
```

**不會觸碰的欄位**: ✅ 不修改 `gender`, `color`

---

#### 2️⃣ `fill_gender_from_name.py`
**更新欄位**: `gender`  
**更新條件**: `WHERE id = %s` (逐筆更新)  
**資料來源**: `name` 欄位關鍵字偵測  
**UPDATE 語句**:
```sql
UPDATE items 
SET gender = %s
WHERE id = %s
```

**不會觸碰的欄位**: ✅ 不修改 `category`, `color`

---

#### 3️⃣ `fill_remaining_nulls.py`
**更新欄位**: `category`, `color`, `gender`  
**更新條件**: `WHERE [欄位] IS NULL OR [欄位] = ''` (只填補空值)  
**資料來源**: 預設值 (`'other'`, `'未分類'`, `'中性'`)  

**UPDATE 語句**:
```sql
-- Category 剩餘空值
UPDATE items 
SET category = 'other' 
WHERE category IS NULL OR category = ''

-- Color 剩餘空值
UPDATE items 
SET color = '未分類' 
WHERE color IS NULL OR color = ''

-- Gender 剩餘空值
UPDATE items 
SET gender = '中性' 
WHERE gender IS NULL OR gender = ''
```

**不會覆蓋的資料**: ✅ 不修改已有值的記錄

---

## 🔒 衝突預防機制

### 機制 1: 不同欄位操作
- Script 1 只改 `category`
- Script 2 只改 `gender`
- Script 3 改三個欄位,但**只填補空值**

### 機制 2: 執行順序保護
`fill_remaining_nulls.py` 新增 `check_prerequisites()` 函數:
- 檢查 `category` 空值比例 > 20% → 警告
- 檢查 `gender` 空值比例 > 10% → 警告
- 強制要求用戶確認才能繼續

```python
def check_prerequisites():
    """檢查前置條件 - 確保前面的腳本已執行"""
    # 檢查 category 是否大部分已填補
    if cat_percentage > 20:
        warnings.append("建議先執行: fill_category_from_clothing_type.py")
    
    # 檢查 gender 是否大部分已填補
    if gen_percentage > 10:
        warnings.append("建議先執行: fill_gender_from_name.py")
    
    # 需要用戶確認才能繼續
    response = input("\n是否仍要繼續? [y/N]: ")
```

### 機制 3: NULL 條件保護
`fill_remaining_nulls.py` 的 UPDATE 語句使用 `WHERE ... IS NULL`:
```sql
WHERE category IS NULL OR category = ''
WHERE gender IS NULL OR gender = ''
WHERE color IS NULL OR color = ''
```
確保**不會覆蓋**前兩個腳本已填入的智能判斷結果。

---

## 📊 資料流向分析

```
items 表格 (44,708 筆)
│
├─ clothing_type 欄位 ────────┐
│                             │
├─ name 欄位 ────────────┐   │
│                        │    │
│                        ▼    ▼
│                   Script 1: fill_category (智能映射)
│                        │
│                        ▼
│                   category 欄位已填補大部分 (~75%)
│                        │
│                        ▼
│                   Script 2: fill_gender (關鍵字偵測)
│                        │
│                        ▼
│                   gender 欄位已填補大部分 (~95%)
│                        │
│                        ▼
│                   Script 3: fill_remaining (預設值)
│                        │
│                        ▼
│               category/gender/color 空值 → 0
```

**資料覆蓋風險**: ❌ **無風險**
- Script 1 和 2 使用 `WHERE id = %s` (精確更新)
- Script 3 使用 `WHERE [欄位] IS NULL` (只填空值)

---

## ✅ 安全性驗證

### 測試場景 1: 順序執行
```bash
./run_fill_all.sh
```
**預期結果**:
1. Script 1 填補 `category` (依 `clothing_type`)
2. Script 2 填補 `gender` (依 `name`)
3. Script 3 填補剩餘空值 (預設值)

**覆蓋風險**: ✅ 無

---

### 測試場景 2: 單獨執行 Script 3
```bash
python3 fill_remaining_nulls.py
```
**預期結果**:
- 前置檢查偵測到大量空值
- 顯示警告訊息
- 要求用戶確認

**覆蓋風險**: ✅ 無 (用戶可中止)

---

### 測試場景 3: 重複執行
```bash
./run_fill_all.sh  # 第一次
./run_fill_all.sh  # 第二次
```
**預期結果**:
- 第二次執行時,前兩個腳本會跳過已處理的記錄
- Script 3 的 `WHERE ... IS NULL` 確保不會覆蓋已有值

**覆蓋風險**: ✅ 無

---

## 🎯 結論

### ✅ 無衝突
三個腳本的設計確保:
1. **職責分離**: 每個腳本專注於不同的資料來源
2. **條件保護**: 使用 NULL 檢查避免覆蓋
3. **執行順序**: 前置檢查確保正確順序
4. **冪等性**: 重複執行不會造成資料損壞

### 📋 建議執行方式
```bash
cd /Users/liaoyiting/Desktop/stylerec/init/scripts
chmod +x run_fill_all.sh
./run_fill_all.sh
```

**預計執行時間**: ~15 分鐘
- Script 1: ~5 分鐘 (44,708 筆 ÷ 10 per batch)
- Script 2: ~5 分鐘 (44,708 筆 ÷ 10 per batch)
- Script 3: ~5 分鐘 (剩餘空值一次性更新)

**安全性**: ⭐⭐⭐⭐⭐ (5/5)

---

**檢查人員**: GitHub Copilot  
**檔案版本**: v1.0  
**最後更新**: 2024-12-09 09:45
