# 權重推薦系統上傳摘要

**上傳日期**: 2024-12-12  
**目標倉庫**: https://github.com/memory9802/AI-project/tree/1202MVP  
**Commit ID**: 49b486e  
**狀態**: ✅ 上傳成功

---

## 📦 上傳內容

### 修改的檔案 (4 個)

1. **app/blueprints/recommendation/rating_service.py**
   - 10 個核心業務邏輯函數
   - 權重計算和推薦排序
   
2. **app/blueprints/recommendation/routes.py**
   - 10 個正式 API 端點
   - 4 個測試端點 (不需登入)
   
3. **app/database.py**
   - 資料庫連線管理
   - 支援本機和 Docker 雙模式
   
4. **FRONTEND_INTEGRATION_GUIDE.md** (新增)
   - 前端整合完整文檔
   - API 使用說明和代碼範例

---

## ⚠️ 不可更動的核心檔案

### 1. rating_service.py

**檔案路徑**: `app/blueprints/recommendation/rating_service.py`

**不可修改的關鍵程式碼**:

```python
# Line 48-51: SQL 查詢的主鍵列名 (已修正 Bug)
if item_source == 'items':
    id_column = 'id'  # ⚠️ 必須是 'id',不能改為 'item_id'
else:
    id_column = 'id'  # ⚠️ 必須是 'id',不能改為 'wardrobe_id'
```

```python
# Line 122-130: 推薦比較的 SQL 查詢 (同樣修正)
if item_source == 'items':
    id_column = 'id'  # ⚠️ 不可修改
else:
    id_column = 'id'  # ⚠️ 不可修改
```

**10 個核心函數** (⚠️ 函數簽名和返回值不可修改):
1. `get_weighted_recommendations(user_id, item_source, limit, exclude_rated, **filters)`
2. `get_recommendations_comparison(user_id, item_source, limit)`
3. `submit_rating(user_id, item_id, item_source, rating_value, review_text)`
4. `delete_rating(user_id, item_id, item_source)`
5. `get_user_ratings(user_id, item_source, limit, offset)`
6. `get_item_stats(item_id, item_source)`
7. `get_top_rated_items(item_source, min_rating, min_rating_count, limit)`
8. `check_user_rated(user_id, item_id, item_source)`
9. `get_user_rating_summary(user_id)`
10. `get_rating_statistics()`

---

### 2. routes.py

**檔案路徑**: `app/blueprints/recommendation/routes.py`

**不可修改的 API 路由**:

```python
# 正式 API 端點 (需要 @login_required)
@recommendation_bp.route('/api/recommendations', methods=['GET'])        # ⚠️ 路由不可修改
@recommendation_bp.route('/api/rating', methods=['POST'])               # ⚠️ 路由不可修改
@recommendation_bp.route('/api/rating/<int:item_id>', methods=['DELETE']) # ⚠️ 路由不可修改
@recommendation_bp.route('/api/ratings/user/<int:user_id>', methods=['GET']) # ⚠️ 路由不可修改
# ... 其他 6 個端點
```

**測試端點 (Line 420-550)** (可在生產環境移除):
```python
# 測試端點 (不需登入)
@recommendation_bp.route('/api/test/recommendations', methods=['GET'])
@recommendation_bp.route('/api/test/comparison', methods=['GET'])
@recommendation_bp.route('/api/test/top-rated', methods=['GET'])
@recommendation_bp.route('/api/test/statistics', methods=['GET'])
```

---

### 3. database.py

**檔案路徑**: `app/database.py`

**不可修改的關鍵程式碼**:

```python
# Line 11: 環境變數支援 (修正後的版本)
db_host = os.environ.get('DB_HOST', 'localhost')  # ⚠️ 不可移除環境變數

# Line 13-21: 資料庫連線參數
connection = pymysql.connect(
    host=db_host,              # ⚠️ 必須使用變數
    user=db_user,
    password=db_password,
    database=db_name,
    port=3306,
    cursorclass=pymysql.cursors.DictCursor,
    charset='utf8mb4'
)
```

**使用方式**:
- 本機運行: 使用預設 `localhost`
- Docker 容器內: 設定環境變數 `DB_HOST=mysql`

---

## 🔧 權重計算邏輯 (不可修改)

### 資料庫視圖

```sql
-- v_items_with_ratings 和 v_wardrobe_with_ratings
CREATE OR REPLACE VIEW v_items_with_ratings AS
SELECT 
    i.id,                                                    -- ⚠️ 主鍵列名是 'id'
    i.name,
    i.category,
    i.color,
    i.price,
    i.image_url,
    COALESCE(s.avg_rating, 0) AS avg_rating,
    COALESCE(s.rating_count, 0) AS rating_count,
    
    -- 評分權重計算 (⚠️ 不可修改)
    CASE 
        WHEN COALESCE(s.avg_rating, 0) >= 4.5 THEN 1.5
        WHEN COALESCE(s.avg_rating, 0) >= 3.5 THEN 1.25
        WHEN COALESCE(s.avg_rating, 0) >= 2.5 THEN 1.0
        WHEN COALESCE(s.avg_rating, 0) >= 1.5 THEN 0.75
        ELSE 0.5
    END AS rating_weight,
    
    -- 人氣權重計算 (⚠️ 不可修改)
    CASE 
        WHEN COALESCE(s.rating_count, 0) >= 20 THEN 1.3
        WHEN COALESCE(s.rating_count, 0) >= 10 THEN 1.2
        WHEN COALESCE(s.rating_count, 0) >= 5 THEN 1.1
        ELSE 1.1  -- 修正: 1-4次評分使用 1.1 (原本是 1.0)
    END AS popularity_weight,
    
    -- 綜合分數 (⚠️ 不可修改)
    (CASE 
        WHEN COALESCE(s.avg_rating, 0) >= 4.5 THEN 1.5
        WHEN COALESCE(s.avg_rating, 0) >= 3.5 THEN 1.25
        WHEN COALESCE(s.avg_rating, 0) >= 2.5 THEN 1.0
        WHEN COALESCE(s.avg_rating, 0) >= 1.5 THEN 0.75
        ELSE 0.5
    END) * (CASE 
        WHEN COALESCE(s.rating_count, 0) >= 20 THEN 1.3
        WHEN COALESCE(s.rating_count, 0) >= 10 THEN 1.2
        WHEN COALESCE(s.rating_count, 0) >= 5 THEN 1.1
        ELSE 1.1
    END) AS final_score
    
FROM items i
LEFT JOIN item_stats s ON i.id = s.item_id AND s.item_source = 'items';
```

---

## ✅ 測試結果 (已驗證)

### 測試數據
- 總評分數: 25 筆
- 參與用戶: 1 人
- 平均評分: 3.64 分
- 商品總數: 25 件 (18 items + 7 wardrobe)

### 測試項目
1. ✅ 帶權重推薦 API
   - 權重計算正確: rating_weight=1.5, popularity_weight=1.1, final_score=1.65
   
2. ✅ 評分提交 API
   - INSERT ON DUPLICATE KEY UPDATE 正常運作
   
3. ✅ 推薦比較 API
   - 無權重 vs 有權重排序正常
   
4. ✅ 全站統計 API
   - 所有統計數據正確

### 測試腳本
- `test_weight_system.py`: 完整功能測試
- `test_db_connection.py`: 資料庫連線測試
- 測試端點: `/recommendation/api/test/*`

---

## 📱 前端整合指南

請參考: **FRONTEND_INTEGRATION_GUIDE.md**

### 包含內容:
- ✅ 完整的 API 端點說明
- ✅ JavaScript 代碼範例 (可直接使用)
- ✅ HTML/CSS 組件範例
- ✅ 星級評分組件實現
- ✅ 錯誤處理和測試方法

---

## 🚨 重要提醒

### 給組員的注意事項:

1. **不要修改核心檔案的關鍵程式碼**
   - rating_service.py 的 10 個函數簽名
   - routes.py 的 API 路由路徑
   - database.py 的連線邏輯

2. **不要修改資料庫視圖**
   - v_items_with_ratings
   - v_wardrobe_with_ratings
   - 權重計算公式

3. **環境變數必須保留**
   - `DB_HOST`: 支援本機和 Docker
   - 不可移除或重新編碼

4. **測試端點處理**
   - 開發期間: 保留測試端點方便測試

5. **前端整合**
   - 請參考 FRONTEND_INTEGRATION_GUIDE.md
   - 所有 API 範例都已測試通過
   - 可以直接複製代碼使用

---

## 📞 聯絡資訊

如有任何問題,請聯繫:
- **負責人**: 廖怡婷
---

**祝整合順利! 🚀**
