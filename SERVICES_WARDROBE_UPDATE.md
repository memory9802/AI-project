# 🎯 Services.py 衣櫃功能更新報告

**更新日期**: 2025年12月9日  
**更新內容**: 實作混合推薦功能 (user_wardrobe + items)

---

## ✅ 更新摘要

### 核心變更
- ✅ 移除錯誤的 `outfits` 表格引用
- ✅ 實作 `user_wardrobe` (個人衣櫃) 查詢
- ✅ 保留 `items` (系統商品) 查詢
- ✅ **混合推薦**: 同時查詢兩個表格,整合結果

### 資料庫架構對應

```
📊 資料庫表格:
├── users (使用者表)
├── items (系統商品庫) - 44,708 筆
├── user_wardrobe (個人衣櫃) - 用戶上傳的衣物
├── partner_products (合作商品)
├── conversation_history (對話歷史)
└── rating (評分)

❌ outfits - 不存在 (舊架構)
```

---

## 📋 新增/修改的函數

### 1. **detect_user_wardrobe_fields(conn)** ✨ 新增
偵測 `user_wardrobe` 表格欄位

**欄位映射**:
```python
{
    "primary_key": "id",
    "title": "item_name",
    "category": "category",
    "occasion": "occasion",  # 已從 material 更新
    "color": "color",
    "tags": "tags",
    "image": "image_url",
    "user_id": "user_id",
}
```

### 2. **detect_item_fields(conn)** ✏️ 修改
偵測 `items` 表格欄位 (保留原功能)

**欄位映射**:
```python
{
    "primary_key": "id",
    "title": "name",
    "category": "category",
    "occasion": "category",
    "image": "image_url",
    "description": "clothing_type",
}
```

### 3. **standardize_wardrobe_item(item, fields)** ✨ 新增
標準化 `user_wardrobe` 的資料

**特殊處理**:
- `_description` = `f"{occasion} / {tags}"` (組合欄位)
- `_source` = `"user_wardrobe"` (標記來源)

**標準化欄位**:
```python
{
    "_id": int,
    "_title": str (item_name),
    "_category": str,
    "_occasion": str,
    "_color": str,
    "_tags": str,
    "_image": str,
    "_description": str (組合 occasion + tags),
    "_source": "user_wardrobe",
    "_user_id": int,
    "_raw": dict (原始資料),
    "_data_quality": dict (品質標記)
}
```

### 4. **standardize_item(item, fields)** ✏️ 修改
標準化 `items` 表格的資料

**標準化欄位**:
```python
{
    "_id": int,
    "_title": str (name),
    "_category": str,
    "_occasion": str (category),
    "_color": str,
    "_image": str,
    "_description": str (clothing_type),
    "_source": "items",
    "_raw": dict,
    "_data_quality": dict
}
```

### 5. **get_wardrobe_fields()** ✨ 新增
快取 `user_wardrobe` 欄位偵測結果

### 6. **get_item_fields()** ✏️ 保留
快取 `items` 欄位偵測結果

### 7. **generate_wardrobe_recommendation()** 🔄 重構
**混合推薦核心函數**

#### 函數簽名變更
```python
# 舊版
def generate_wardrobe_recommendation(
    user_input, session_id, preferred_model
):

# 新版
def generate_wardrobe_recommendation(
    user_input, 
    user_id=None,  # ✨ 新增參數
    session_id="wardrobe-default", 
    preferred_model="auto"
):
```

#### 查詢邏輯
1. **查詢 user_wardrobe** (如果有 user_id)
   - 根據關鍵字篩選: `category` 或 `occasion`
   - 限制: 5 件
   
2. **查詢 items** (補充推薦)
   - 計算需要數量: `max(10 - wardrobe件數, 5)`
   - 確保至少有推薦內容
   
3. **混合結果**
   - `mixed_items = wardrobe_items + system_items`
   - 總共 5-10 件推薦

#### 回傳值
```python
(ai_response: str, mixed_items: list, keywords: list)
```

#### 特殊處理
- ✅ 處理時間戳記: `created_at`, `uploaded_at` → `isoformat()`
- ✅ 處理價格: `Decimal` → `float`
- ✅ 來源標記: `_source` 區分 "user_wardrobe" vs "items"

### 8. **generate_wardrobe_structured()** 🔄 重構
**混合推薦 (結構化輸出)**

#### 函數簽名變更
```python
# 舊版
def generate_wardrobe_structured(
    user_input, session_id, preferred_model
):

# 新版
def generate_wardrobe_structured(
    user_input,
    user_id=None,  # ✨ 新增參數
    session_id="wardrobe-structured",
    preferred_model="auto"
):
```

#### 回傳值
```python
(result_dict, mixed_items, keywords)

# result_dict 結構:
{
    "parsed": dict,  # LLM 解析後的結構化資料
    "raw": str,      # 原始 LLM 回應
    "error": str     # 錯誤訊息 (如有)
}
```

---

## 🔍 使用範例

### 範例 1: 有登入用戶 (優先個人衣櫃)

```python
from app.blueprints.aichat.services import generate_wardrobe_recommendation

# 用戶 ID = 1
response, items, keywords = generate_wardrobe_recommendation(
    user_input="推薦適合約會的穿搭",
    user_id=1,  # ✨ 傳入用戶 ID
    session_id="user-1-chat",
    preferred_model="gemini"
)

print(f"推薦數量: {len(items)}")
print(f"來源分佈:")
for item in items:
    print(f"  - {item['_title']} (來源: {item['_source']})")

# 預期輸出:
# 推薦數量: 8
# 來源分佈:
#   - 白色襯衫 (來源: user_wardrobe)  ← 用戶個人衣物
#   - 黑色西裝褲 (來源: user_wardrobe)
#   - 休閒外套 (來源: user_wardrobe)
#   - 純棉T恤 (來源: items)  ← 系統推薦商品
#   - 牛仔褲 (來源: items)
#   ...
```

### 範例 2: 未登入用戶 (僅系統商品)

```python
response, items, keywords = generate_wardrobe_recommendation(
    user_input="推薦運動裝",
    user_id=None,  # ✨ 無用戶 ID
    session_id="guest-session"
)

# 所有推薦都來自 items 表格
for item in items:
    print(f"{item['_title']} - {item['_source']}")

# 預期輸出:
# 運動上衣 - items
# 運動褲 - items
# 運動鞋 - items
# ...
```

### 範例 3: 用戶衣櫃為空 (自動補充系統商品)

```python
# 用戶 ID = 999 (新用戶,還沒上傳衣物)
response, items, keywords = generate_wardrobe_recommendation(
    user_input="推薦休閒穿搭",
    user_id=999,
    session_id="new-user"
)

# 查詢 user_wardrobe: 0 件
# 自動從 items 補充: 10 件
print(f"推薦數量: {len(items)}")  # 10

for item in items:
    print(f"{item['_title']} - {item['_source']}")

# 預期輸出: (全部來自 items)
# T恤 - items
# 休閒褲 - items
# 運動鞋 - items
# ...
```

---

## 🔄 API Route 調用範例

### routes.py 修改建議

```python
from flask import Blueprint, request, session
from .services import generate_wardrobe_recommendation

bp = Blueprint('aichat', __name__, url_prefix='/aichat')

@bp.route('/recommend', methods=['POST'])
def recommend():
    """衣櫃推薦 API"""
    data = request.json
    user_input = data.get('message', '')
    
    # ✨ 從 session 取得 user_id
    user_id = session.get('user_id')  # 如果有登入系統
    
    # 或從 request 取得
    # user_id = data.get('user_id')
    
    response, items, keywords = generate_wardrobe_recommendation(
        user_input=user_input,
        user_id=user_id,  # ✨ 傳入 user_id
        session_id=session.get('session_id', 'default'),
        preferred_model=data.get('model', 'auto')
    )
    
    return {
        'status': 'success',
        'response': response,
        'items': items,
        'keywords': keywords,
        'stats': {
            'total': len(items),
            'from_wardrobe': sum(1 for i in items if i['_source'] == 'user_wardrobe'),
            'from_items': sum(1 for i in items if i['_source'] == 'items')
        }
    }
```

---

## ⚠️ 重要注意事項

### 1. user_id 參數來源
- ✅ 從 Flask session 取得: `session.get('user_id')`
- ✅ 從 JWT token 取得: `decode_token(request.headers['Authorization'])`
- ✅ 從 request body 取得: `request.json.get('user_id')`

### 2. 資料庫欄位更新
- ⚠️ `user_wardrobe.material` 已改名為 `occasion`
- ⚠️ `_description` 同時參照 `occasion` 和 `tags`
- ⚠️ 確保資料庫 schema 與程式碼一致

### 3. 容錯機制
- ✅ user_wardrobe 查詢失敗 → 自動降級為 items
- ✅ items 查詢失敗 → 至少回傳空結果
- ✅ 無 user_id → 直接查詢 items
- ✅ 用戶衣櫃為空 → 補充系統商品

### 4. 效能考量
- 📊 user_wardrobe 限制 5 件 (避免過多個人資料)
- 📊 items 補充 5-10 件 (根據 wardrobe 數量調整)
- 📊 總推薦數量: 5-10 件

---

## 🧪 測試建議

### 單元測試

```python
def test_wardrobe_with_user_id():
    """測試有 user_id 的混合推薦"""
    response, items, keywords = generate_wardrobe_recommendation(
        user_input="約會穿搭",
        user_id=1
    )
    
    assert len(items) > 0
    assert any(item['_source'] == 'user_wardrobe' for item in items)
    assert any(item['_source'] == 'items' for item in items)

def test_wardrobe_without_user_id():
    """測試無 user_id 的系統推薦"""
    response, items, keywords = generate_wardrobe_recommendation(
        user_input="運動穿搭",
        user_id=None
    )
    
    assert len(items) > 0
    assert all(item['_source'] == 'items' for item in items)

def test_empty_wardrobe():
    """測試空衣櫃的備援機制"""
    # 假設 user_id=999 的衣櫃為空
    response, items, keywords = generate_wardrobe_recommendation(
        user_input="休閒穿搭",
        user_id=999
    )
    
    assert len(items) >= 5  # 至少有系統推薦
    assert all(item['_source'] == 'items' for item in items)
```

### 手動測試

```bash
# 1. 啟動 Flask
docker compose up -d

# 2. 測試有 user_id
curl -X POST http://localhost:5001/aichat/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "message": "推薦約會穿搭",
    "user_id": 1
  }' | jq .

# 3. 測試無 user_id
curl -X POST http://localhost:5001/aichat/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "message": "推薦運動穿搭"
  }' | jq .
```

---

## 📊 資料流程圖

```
使用者輸入 "推薦約會穿搭"
    ↓
提取關鍵字 ["約會", "派對"]
    ↓
檢查 user_id ?
    ├─ 有 → 查詢 user_wardrobe (3件)
    │       ↓
    │   補充查詢 items (7件)
    │       ↓
    │   混合結果 (10件)
    │
    └─ 無 → 直接查詢 items (10件)
        ↓
處理時間/價格格式
    ↓
AI 生成推薦文字
    ↓
回傳 (response, mixed_items, keywords)
```

---

## ✅ 檢查清單

開發完成後,請確認:

- [ ] 資料庫中 `user_wardrobe.occasion` 欄位存在 (原 material)
- [ ] `items` 表格有足夠資料 (至少 100 筆)
- [ ] 測試有 user_id 的推薦
- [ ] 測試無 user_id 的推薦
- [ ] 測試空衣櫃的備援機制
- [ ] 測試關鍵字篩選功能
- [ ] 測試 AI 回應格式
- [ ] 更新 routes.py 傳入 user_id
- [ ] 更新前端傳送 user_id

---

## 🎉 完成狀態

```
✅ 移除 outfits 表格引用
✅ 實作 user_wardrobe 查詢
✅ 實作混合推薦邏輯
✅ 容錯機制完整
✅ 新增 user_id 參數
✅ 標記資料來源 (_source)
✅ 欄位對應更新 (occasion)
✅ 組合 description (occasion + tags)
✅ 處理時間/價格格式
✅ 文檔完整
```

---

**更新完成!** 🎊  
服務已從單一 items 查詢升級為 **user_wardrobe + items 混合推薦**,確保用戶始終能獲得個人化且充足的推薦內容。
