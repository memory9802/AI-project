# 評分權重推薦系統 - 快速開始指南

## 🎯 目標

本指南將幫助您快速啟動並測試評分權重推薦系統的後端 API。

---

## 📋 前置條件

1. **資料庫已遷移** ✅
   - 已執行 `migration_rating_system.sql`
   - rating 表格支援多態關聯
   - item_stats 統計表已建立
   - 視圖和觸發器正常運作

2. **測試資料已插入** ✅
   - demo_user (ID: 54) 已建立
   - 30 件測試商品 (ID: 5092-5121) 已標記 `is_demo=1`
   - 測試評分已插入

3. **後端代碼已部署** ✅
   - `app/blueprints/recommendation/rating_service.py` (核心服務)
   - `app/blueprints/recommendation/routes.py` (API 端點)

---

## 🚀 快速啟動

### 步驟 1: 啟動 Flask 應用程式

```bash
cd /Users/liaoyiting/Desktop/stylerec/app

# 啟動應用程式 (預設 port 5000)
python3 app.py

# 或使用指定 port
PORT=5001 python3 app.py
```

**預期輸出**:
```
* Running on http://0.0.0.0:5000
* Running on http://0.0.0.0:5001
```

---

### 步驟 2: 驗證 API 可訪問

打開瀏覽器或使用 curl:

```bash
# 檢查應用程式是否運行
curl http://localhost:5001/

# 應該重定向到首頁
```

---

### 步驟 3: 登入取得 Session Cookie

⚠️ **重要**: 所有 API 都需要認證,必須先登入!

**方法 1: 使用瀏覽器**
1. 打開 http://localhost:5001/login/login
2. 使用 demo_user 登入:
   - 帳號: `demo_user` 或 email
   - 密碼: (根據資料庫設定)
3. 登入後瀏覽器會保存 session cookie

**方法 2: 使用 curl (保存 cookie)**
```bash
# 登入並保存 cookie
curl -c cookies.txt -X POST http://localhost:5001/login/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_user","password":"your_password"}'

# 之後的請求都帶上 cookie
curl -b cookies.txt http://localhost:5001/recommendation/api/recommendations
```

---

### 步驟 4: 測試 API

#### 方法 A: 使用測試腳本 (推薦)

```bash
# Python 測試腳本
cd /Users/liaoyiting/Desktop/stylerec/scripts
python3 test_rating_api.py

# 或 Bash 測試腳本
chmod +x test_rating_api.sh
./test_rating_api.sh
```

#### 方法 B: 手動測試單個 API

```bash
# 1. 取得帶權重推薦 (前10件)
curl "http://localhost:5001/recommendation/api/recommendations?item_source=items&limit=10&exclude_rated=true"

# 2. 提交評分
curl -X POST http://localhost:5001/recommendation/api/rating \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": 5092,
    "item_source": "items",
    "rating_value": 5,
    "review_text": "超級喜歡!"
  }'

# 3. 查詢用戶評分
curl "http://localhost:5001/recommendation/api/ratings/user/54?limit=10"

# 4. 推薦比較 (無權重 vs 有權重)
curl "http://localhost:5001/recommendation/api/recommendations/comparison?item_source=items&limit=5"

# 5. 查詢商品統計
curl "http://localhost:5001/recommendation/api/item-stats/5092?item_source=items"

# 6. 查詢全站統計
curl "http://localhost:5001/recommendation/api/statistics"
```

---

## 🧪 驗證結果

### 1. 檢查推薦是否帶權重

**預期**: 返回的商品應包含權重欄位

```json
{
  "success": true,
  "data": [
    {
      "item_id": 5095,
      "avg_rating": 4.8,
      "rating_count": 12,
      "rating_weight": 1.4,
      "popularity_weight": 1.2,
      "final_score": 1.68,
      "...": "其他欄位"
    }
  ]
}
```

### 2. 檢查評分提交是否成功

```json
{
  "success": true,
  "message": "評分提交成功"
}
```

### 3. 檢查統計是否自動更新

提交評分後,查詢 `item_stats`:

```bash
curl "http://localhost:5001/recommendation/api/item-stats/5092?item_source=items"
```

**預期**: `rating_count` 和 `avg_rating` 已更新

---

## 🔍 除錯指南

### 問題 1: API 返回 401 Unauthorized

**原因**: 未登入或 session 已過期

**解決**:
1. 確保已登入並取得 session cookie
2. 檢查 cookie 是否正確傳遞
3. 使用瀏覽器開發者工具檢查 cookie

---

### 問題 2: API 返回 500 Internal Server Error

**原因**: 可能是資料庫連線或 SQL 錯誤

**解決**:
1. 檢查 Flask 終端輸出的錯誤日誌
2. 確認資料庫連線正常:
   ```bash
   docker ps | grep mysql
   ```
3. 確認視圖和觸發器已建立:
   ```sql
   SHOW TABLES LIKE 'v_%';
   SHOW TRIGGERS;
   ```

---

### 問題 3: 找不到模組 'rating_service'

**原因**: Python 模組導入錯誤

**解決**:
1. 確認檔案路徑正確:
   ```
   app/blueprints/recommendation/rating_service.py
   ```
2. 確認 `__init__.py` 存在
3. 重啟 Flask 應用程式

---

### 問題 4: 推薦結果為空

**原因**: 測試資料未插入或已全部評分

**解決**:
1. 檢查測試資料是否存在:
   ```sql
   SELECT COUNT(*) FROM items WHERE is_demo = 1;
   SELECT COUNT(*) FROM rating WHERE user_id = 54;
   ```
2. 使用 `exclude_rated=false` 測試
3. 重新執行 `insert_demo_ratings.sql`

---

## 📊 監控和日誌

### 查看 Flask 日誌

```bash
# Flask 會自動輸出日誌到終端
# 包含 SQL 查詢、錯誤訊息等
```

### 查看資料庫日誌

```bash
# 進入 MySQL 容器
docker exec -it stylerec-mysql-1 mysql -u root -p outfit_db

# 查看最近的評分
SELECT * FROM rating ORDER BY created_at DESC LIMIT 10;

# 查看統計表
SELECT * FROM item_stats ORDER BY rating_count DESC LIMIT 10;

# 查看視圖
SELECT * FROM v_items_with_ratings LIMIT 5;
```

---

## 🎉 成功指標

如果以下測試都通過,說明系統運作正常:

- [x] ✅ Flask 應用程式成功啟動
- [ ] ✅ 成功登入並取得 session cookie
- [ ] ✅ 提交評分成功 (返回 200)
- [ ] ✅ 取得推薦列表成功 (包含權重欄位)
- [ ] ✅ 推薦比較顯示差異 (無權重 vs 有權重)
- [ ] ✅ 商品統計自動更新 (觸發器運作)
- [ ] ✅ 用戶評分查詢成功
- [ ] ✅ 全站統計正確

---

## 📖 延伸閱讀

- [API 完整文檔](./RATING_API_GUIDE.md)
- [資料庫遷移指南](../init/MIGRATION_GUIDE.md)
- [系統設計文檔](./RATING_WEIGHT_SYSTEM_DESIGN.md)

---

## 🆘 需要協助?

如果遇到問題:
1. 檢查上述除錯指南
2. 查看 Flask 終端日誌
3. 檢查資料庫連線和資料
4. 參考完整 API 文檔

---

**版本**: v1.0  
**最後更新**: 2024-12-09  
**狀態**: ✅ 後端開發完成,待測試
