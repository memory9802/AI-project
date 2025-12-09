# 評分權重推薦系統 API 文檔

## 目錄
- [概述](#概述)
- [API 端點列表](#api-端點列表)
- [詳細說明](#詳細說明)
- [錯誤處理](#錯誤處理)
- [測試方法](#測試方法)

---

## 概述

評分權重推薦系統提供完整的 RESTful API 介面,支援:
- ✅ 提交/更新/刪除評分
- ✅ 帶權重的商品推薦查詢
- ✅ 用戶評分記錄管理
- ✅ 商品統計資料查詢
- ✅ 全站評分統計

**基礎 URL**: `http://localhost:5001/recommendation/api`

**認證方式**: Session Cookie (需先登入)

---

## API 端點列表

| 方法 | 端點 | 功能 | 需要認證 |
|------|------|------|----------|
| POST | `/rating` | 提交或更新評分 | ✅ |
| DELETE | `/rating/<item_id>` | 刪除評分 | ✅ |
| GET | `/recommendations` | 取得帶權重推薦 | ✅ |
| GET | `/recommendations/comparison` | 推薦比較 | ✅ |
| GET | `/ratings/user/<user_id>` | 查詢用戶評分 | ✅ |
| GET | `/ratings/user/<user_id>/summary` | 用戶評分摘要 | ✅ |
| GET | `/item-stats/<item_id>` | 商品統計資料 | ✅ |
| GET | `/rating/check/<item_id>` | 檢查是否已評分 | ✅ |
| GET | `/top-rated` | 高評分商品列表 | ✅ |
| GET | `/statistics` | 全站統計 | ✅ |

---

## 詳細說明

### 1. 提交或更新評分

**端點**: `POST /rating`

**功能**: 提交新評分或更新現有評分

**Request Body**:
```json
{
  "item_id": 5092,
  "item_source": "items",        // 'items' 或 'user_wardrobe'
  "rating_value": 5,              // 1-5 星
  "review_text": "超級喜歡!"      // 可選
}
```

**Response (成功)**:
```json
{
  "success": true,
  "message": "評分提交成功"
}
```

**Response (失敗)**:
```json
{
  "success": false,
  "error": "評分必須在 1-5 之間"
}
```

---

### 2. 刪除評分

**端點**: `DELETE /rating/<item_id>`

**Query Parameters**:
- `item_source` (必要): 商品來源 (`items` 或 `user_wardrobe`)

**範例**: `DELETE /rating/5092?item_source=items`

**Response (成功)**:
```json
{
  "success": true,
  "message": "評分刪除成功"
}
```

---

### 3. 取得帶權重推薦

**端點**: `GET /recommendations`

**功能**: 取得帶權重計算的推薦商品列表

**Query Parameters**:
- `item_source` (可選): 商品來源,預設 `items`
- `limit` (可選): 返回數量,預設 20
- `exclude_rated` (可選): 是否排除已評分,預設 `true`
- `min_rating` (可選): 最低平均評分過濾
- `category` (可選): 商品類別過濾

**範例**: 
```
GET /recommendations?item_source=items&limit=10&exclude_rated=true&min_rating=4.0
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "item_id": 5092,
      "productDisplayName": "藍色牛仔褲",
      "avg_rating": 4.5,
      "rating_count": 10,
      "rating_weight": 1.25,
      "popularity_weight": 1.15,
      "final_score": 1.4375,
      "...": "其他商品欄位"
    }
  ],
  "count": 10
}
```

**權重計算說明**:
- `rating_weight`: 0.5-1.5 (根據平均評分)
  - 5.0星: 1.5
  - 4.0星: 1.25
  - 3.0星: 1.0
  - 2.0星: 0.75
  - 1.0星: 0.5

- `popularity_weight`: 1.0-1.3 (根據評分次數)
  - 20+ 次: 1.3
  - 10-19 次: 1.2
  - 5-9 次: 1.1
  - 1-4 次: 1.0

- `final_score` = `rating_weight` × `popularity_weight`

---

### 4. 推薦比較 (無權重 vs 有權重)

**端點**: `GET /recommendations/comparison`

**功能**: 同時返回無權重和有權重的推薦結果,用於測試和展示

**Query Parameters**:
- `item_source` (可選): 商品來源,預設 `items`
- `limit` (可選): 每種推薦的返回數量,預設 10

**範例**: `GET /recommendations/comparison?item_source=items&limit=5`

**Response**:
```json
{
  "success": true,
  "data": {
    "without_weight": [
      { "item_id": 5092, "avg_rating": 5.0, "..." },
      { "item_id": 5093, "avg_rating": 4.8, "..." }
    ],
    "with_weight": [
      { "item_id": 5095, "final_score": 1.56, "..." },
      { "item_id": 5092, "final_score": 1.50, "..." }
    ]
  }
}
```

---

### 5. 查詢用戶評分記錄

**端點**: `GET /ratings/user/<user_id>`

**功能**: 取得用戶的評分記錄列表

**Query Parameters**:
- `item_source` (可選): 過濾商品來源
- `limit` (可選): 返回數量,預設 50

**範例**: `GET /ratings/user/54?item_source=items&limit=10`

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "user_id": 54,
      "item_source": "items",
      "item_id": 5092,
      "rating_value": 5,
      "review_text": "超級喜歡!",
      "created_at": "2024-12-09 10:30:00",
      "updated_at": "2024-12-09 10:30:00"
    }
  ],
  "count": 1
}
```

**權限控制**: 只能查詢自己的評分記錄

---

### 6. 用戶評分摘要

**端點**: `GET /ratings/user/<user_id>/summary`

**功能**: 取得用戶的評分統計摘要

**範例**: `GET /ratings/user/54/summary`

**Response**:
```json
{
  "success": true,
  "data": {
    "total_ratings": 25,
    "items_ratings": 18,
    "wardrobe_ratings": 7,
    "avg_rating": 4.2,
    "rating_distribution": {
      "1": 1,
      "2": 2,
      "3": 3,
      "4": 8,
      "5": 11
    }
  }
}
```

---

### 7. 查詢商品統計資料

**端點**: `GET /item-stats/<item_id>`

**功能**: 取得商品的評分統計資料 (來自 `item_stats` 表格)

**Query Parameters**:
- `item_source` (必要): 商品來源

**範例**: `GET /item-stats/5092?item_source=items`

**Response**:
```json
{
  "success": true,
  "data": {
    "item_id": 5092,
    "item_source": "items",
    "avg_rating": 4.5,
    "rating_count": 10,
    "rating_5_count": 6,
    "rating_4_count": 3,
    "rating_3_count": 1,
    "rating_2_count": 0,
    "rating_1_count": 0,
    "last_updated": "2024-12-09 12:00:00"
  }
}
```

---

### 8. 檢查是否已評分

**端點**: `GET /rating/check/<item_id>`

**功能**: 檢查當前用戶是否已評分該商品

**Query Parameters**:
- `item_source` (必要): 商品來源

**範例**: `GET /rating/check/5092?item_source=items`

**Response (已評分)**:
```json
{
  "success": true,
  "rated": true,
  "data": {
    "id": 1,
    "rating_value": 5,
    "review_text": "超級喜歡!",
    "...": "其他評分欄位"
  }
}
```

**Response (未評分)**:
```json
{
  "success": true,
  "rated": false,
  "data": null
}
```

---

### 9. 高評分商品列表

**端點**: `GET /top-rated`

**功能**: 取得高評分商品列表

**Query Parameters**:
- `item_source` (可選): 商品來源,預設 `items`
- `limit` (可選): 返回數量,預設 10
- `min_rating_count` (可選): 最少評分次數,預設 3

**範例**: `GET /top-rated?item_source=items&limit=5&min_rating_count=5`

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "item_id": 5095,
      "avg_rating": 4.8,
      "rating_count": 12,
      "...": "其他商品欄位"
    }
  ],
  "count": 5
}
```

---

### 10. 全站統計

**端點**: `GET /statistics`

**功能**: 取得全站評分統計資料

**範例**: `GET /statistics`

**Response**:
```json
{
  "success": true,
  "data": {
    "total_ratings": 250,
    "total_users": 15,
    "total_items": 100,
    "avg_rating": 4.1,
    "items_count": 180,
    "wardrobe_count": 70
  }
}
```

---

## 錯誤處理

### HTTP 狀態碼

- `200 OK`: 請求成功
- `400 Bad Request`: 請求參數錯誤
- `403 Forbidden`: 無權限訪問
- `404 Not Found`: 資源不存在
- `500 Internal Server Error`: 伺服器錯誤

### 錯誤回應格式

```json
{
  "success": false,
  "error": "錯誤訊息"
}
```

### 常見錯誤

1. **缺少必要欄位**
```json
{
  "success": false,
  "error": "缺少必要欄位: item_id"
}
```

2. **評分值範圍錯誤**
```json
{
  "success": false,
  "error": "評分必須在 1-5 之間"
}
```

3. **商品不存在**
```json
{
  "success": false,
  "error": "商品不存在 (ID: 9999, 來源: items)"
}
```

4. **無權限**
```json
{
  "success": false,
  "error": "無權限查詢其他用戶的評分"
}
```

---

## 測試方法

### 方法 1: 使用 Bash 腳本

```bash
chmod +x scripts/test_rating_api.sh
./scripts/test_rating_api.sh
```

### 方法 2: 使用 Python 腳本

```bash
cd scripts
python3 test_rating_api.py
```

### 方法 3: 使用 curl

```bash
# 提交評分
curl -X POST http://localhost:5001/recommendation/api/rating \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": 5092,
    "item_source": "items",
    "rating_value": 5,
    "review_text": "超級喜歡!"
  }'

# 取得推薦
curl http://localhost:5001/recommendation/api/recommendations?item_source=items&limit=10

# 查詢用戶評分
curl http://localhost:5001/recommendation/api/ratings/user/54?limit=10
```

### 方法 4: 使用 Postman

1. 匯入 API 端點到 Postman
2. 設定基礎 URL: `http://localhost:5001/recommendation/api`
3. 確保 Cookie 已設定 (需先登入)
4. 執行測試

---

## 注意事項

1. **認證**: 所有 API 都需要先登入並取得 session cookie
2. **測試資料**: 測試前確保 demo_user (ID: 54) 和測試商品 (ID: 5092-5121) 已存在
3. **權重計算**: 權重自動由觸發器更新,無需手動計算
4. **字符集**: 評論文字支援 UTF-8 中文字符
5. **性能**: 視圖查詢已優化,支援大量商品推薦

---

## 下一步

- [ ] 前端整合評分 UI
- [ ] 新增評分通知功能
- [ ] 新增評分排行榜
- [ ] 支援評分篩選和排序
- [ ] 新增評分匯出功能
