# 聊天機器人測試報告

**測試日期**: 2025-12-09  
**測試目的**: 驗證聊天機器人能否正確連接 Gemini AI 和資料庫

---

## ✅ 測試成功項目

### 1. Flask 應用程式啟動
- **狀態**: ✅ 成功
- **容器**: `outfit-flask` 正常運行
- **端口**: `http://localhost:5001`
- **健康檢查**: 通過

### 2. 資料庫連線
- **狀態**: ✅ 成功
- **資料庫**: `outfit_db` (MySQL 8.0)
- **資料表**: `items` (44,708 筆商品資料)
- **類別分布**:
  - top: 15,546 件
  - shoes: 9,243 件
  - accessories: 8,348 件
  - bags: 2,947 件
  - bottom: 2,702 件
  - beauty: 2,270 件
  - dress: 923 件
  - other: 534 件
  - underwear: 2,195 件

### 3. 中英文類別查詢功能
- **狀態**: ✅ 成功
- **功能**: 新增 `normalize_category()` 函數
- **測試結果**:
  ```bash
  # 中文查詢
  GET /aichat/items?category=上衣  → 回傳 top 類別商品 ✅
  GET /aichat/items?category=鞋子  → 回傳 shoes 類別商品 ✅
  
  # 英文查詢
  GET /aichat/items?category=top   → 回傳 top 類別商品 ✅
  GET /aichat/items?category=shoes → 回傳 shoes 類別商品 ✅
  ```

### 4. 資料標準化功能
- **狀態**: ✅ 成功
- **功能**: 
  - `standardize_item()` - 標準化 items 表格資料
  - `standardize_wardrobe_item()` - 標準化 user_wardrobe 表格資料
- **測試結果**: 成功將資料轉換為統一格式,包含 `_id`, `_title`, `_category`, `_source` 等欄位

### 5. 混合推薦查詢
- **狀態**: ✅ 成功
- **功能**: 查詢 `items` 表格 (系統商品)
- **測試結果**: 
  ```bash
  POST /aichat/wardrobe_recommend
  Body: {"message":"推薦我適合約會的上衣"}
  
  回應: 
  - db_data: 10 件商品 ✅
  - 資料格式正確 ✅
  - 欄位標準化成功 ✅
  ```

---

## ⚠️ 需要注意的問題

### 1. Gemini API 配額限制
- **狀態**: ⚠️ API 配額已用完
- **錯誤訊息**: `429 You exceeded your current quota`
- **影響**: 
  - 關鍵字分類功能無法使用
  - AI 推薦回應無法生成
- **解決方案**: 
  1. 等待配額重置 (每日/每月)
  2. 升級 Gemini API 方案
  3. 使用新的 API Key
- **備註**: **資料庫查詢功能不受影響,仍可正常運作**

### 2. user_wardrobe 表格欄位缺失
- **狀態**: ⚠️ 警告
- **缺失欄位**: `occasion` (場合)
- **影響**: 個人衣櫃推薦時無法依場合篩選
- **建議**: 
  ```sql
  ALTER TABLE user_wardrobe ADD COLUMN occasion VARCHAR(100);
  ```

---

## 📊 API 端點測試摘要

| API 端點 | 方法 | 功能 | 狀態 |
|---------|------|------|------|
| `/aichat/items` | GET | 查詢商品 (支援中英文類別) | ✅ 成功 |
| `/aichat/recommend` | POST | 全球搜索 (純 LLM) | ⚠️ API 配額限制 |
| `/aichat/wardrobe_recommend` | POST | 混合推薦 (DB + AI) | ✅ 部分成功 (DB ✅, AI ⚠️) |
| `/aichat/data_quality` | GET | 資料品質檢查 | ✅ 成功 |

---

## 🔧 已修正的技術問題

### 1. Gunicorn 啟動失敗
- **問題**: `Failed to find attribute 'app' in 'app'`
- **原因**: Factory Pattern 需要特殊配置
- **解決**: 修改 Dockerfile CMD 為 `gunicorn app:create_app()`

### 2. OpenAI 匯入錯誤
- **問題**: `OpenAIError: The api_key client option must be set`
- **原因**: `langchain_openai` 在匯入時檢查環境變數
- **解決**: 改為條件式匯入,僅在需要時載入

### 3. 函數名稱不匹配
- **問題**: `ImportError: cannot import name 'get_outfit_fields'`
- **原因**: 重構後函數名稱變更
- **解決**: 更新為 `get_wardrobe_fields()` 和 `get_item_fields()`

---

## 📝 程式碼更新摘要

### 新增功能

1. **中英文類別對照表** (`services.py`)
   ```python
   CATEGORY_MAPPING = {
       "上衣": "top",
       "褲子": "bottom",
       "鞋子": "shoes",
       "包包": "bags",
       # ... 更多對照
   }
   ```

2. **類別標準化函數** (`services.py`)
   ```python
   def normalize_category(category: str) -> str:
       """將中文類別轉換為資料庫的英文類別"""
       return CATEGORY_MAPPING.get(category.lower(), category)
   ```

3. **增強關鍵字提取** (`services.py`)
   ```python
   def extract_keywords(text: str):
       """自動將 AI 回傳的關鍵字標準化為英文類別"""
       raw_keywords = agent.classify_keywords(text)
       return [normalize_category(kw) for kw in raw_keywords]
   ```

4. **更新 API 路由** (`routes.py`)
   ```python
   @aichat_bp.route("/items", methods=["GET"])
   def get_items():
       category = request.args.get("category")
       if category:
           normalized_category = normalize_category(category)
           sql += " AND category=%s"
   ```

---

## 🎯 測試結論

### 核心功能驗證
✅ **資料庫連接**: 完全正常  
✅ **商品查詢**: 支援中英文類別  
✅ **資料標準化**: 成功整合 items 和 user_wardrobe  
⚠️ **AI 推薦**: 受 Gemini API 配額限制,待配額恢復後測試

### 聊天機器人雙資訊來源測試
- **外部 LLM (Gemini)**: ⚠️ 配額用完,暫時無法測試完整功能
- **資料庫查詢**: ✅ 完全正常,可正確查詢並回傳商品資料

### 下一步建議
1. **更新 Gemini API Key** 或等待配額重置
2. **補充 user_wardrobe 表格的 occasion 欄位**
3. **完整測試 AI + DB 混合推薦功能**
4. **測試前端網頁與後端 API 的整合**

---

## 📞 技術支援資訊

- **Docker 容器**: `outfit-flask`, `outfit-mysql`
- **API 端點**: `http://localhost:5001/aichat/*`
- **資料庫管理**: `http://localhost:8080` (phpMyAdmin)
- **日誌查看**: `docker logs outfit-flask`

---

**測試人員**: GitHub Copilot  
**專案路徑**: `/Users/liaoyiting/Desktop/stylerec`  
**Git 分支**: `1202MVP`
