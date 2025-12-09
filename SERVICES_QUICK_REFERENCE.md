# 🚀 Services.py 衣櫃功能 - 快速參考

## 📋 函數簽名變更

### generate_wardrobe_recommendation()

```python
# 舊版 ❌
def generate_wardrobe_recommendation(
    user_input: str, 
    session_id: str = "wardrobe-default", 
    preferred_model: str = "auto"
):
    # 只查詢 items 表格

# 新版 ✅
def generate_wardrobe_recommendation(
    user_input: str,
    user_id: int = None,  # ← 新增參數!
    session_id: str = "wardrobe-default",
    preferred_model: str = "auto"
):
    # 混合查詢 user_wardrobe + items
```

### generate_wardrobe_structured()

```python
# 舊版 ❌
def generate_wardrobe_structured(
    user_input: str, 
    session_id: str = "wardrobe-structured", 
    preferred_model: str = "auto"
):

# 新版 ✅
def generate_wardrobe_structured(
    user_input: str,
    user_id: int = None,  # ← 新增參數!
    session_id: str = "wardrobe-structured",
    preferred_model: str = "auto"
):
```

---

## 🔧 Routes.py 修改範例

### 修改前

```python
# app/blueprints/aichat/routes.py
from .services import generate_wardrobe_recommendation

@bp.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    
    # ❌ 舊版: 沒有傳入 user_id
    response, items, keywords = generate_wardrobe_recommendation(
        user_input=data.get('message'),
        session_id=session.get('session_id'),
        preferred_model=data.get('model', 'auto')
    )
    
    return {'response': response, 'items': items}
```

### 修改後

```python
# app/blueprints/aichat/routes.py
from .services import generate_wardrobe_recommendation

@bp.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    
    # ✅ 新版: 傳入 user_id
    user_id = session.get('user_id')  # 從 session 取得
    # 或: user_id = data.get('user_id')  # 從 request 取得
    
    response, items, keywords = generate_wardrobe_recommendation(
        user_input=data.get('message'),
        user_id=user_id,  # ← 新增!
        session_id=session.get('session_id'),
        preferred_model=data.get('model', 'auto')
    )
    
    # 新增統計資訊
    stats = {
        'total': len(items),
        'from_wardrobe': sum(1 for i in items if i['_source'] == 'user_wardrobe'),
        'from_items': sum(1 for i in items if i['_source'] == 'items')
    }
    
    return {
        'response': response,
        'items': items,
        'keywords': keywords,
        'stats': stats  # ← 新增!
    }
```

---

## 📊 資料結構變更

### 標準化後的 item 物件

```python
# user_wardrobe 來源
{
    "_id": 1,
    "_title": "白色襯衫",
    "_category": "上衣",
    "_occasion": "正式",
    "_color": "白色",
    "_tags": "商務,辦公",
    "_image": "http://...",
    "_description": "場合: 正式 / 標籤: 商務,辦公",  # ← 組合欄位
    "_source": "user_wardrobe",  # ← 標記來源
    "_user_id": 1,
    "_raw": {...},
    "_data_quality": {...},
    # ... 其他原始欄位
}

# items 來源
{
    "_id": 1001,
    "_title": "純棉T恤",
    "_category": "上衣",
    "_occasion": "上衣",
    "_color": "白色",
    "_image": "http://...",
    "_description": "短袖上衣",
    "_source": "items",  # ← 標記來源
    "_raw": {...},
    "_data_quality": {...},
    "price": 399.0,  # ← items 才有價格
    # ... 其他原始欄位
}
```

---

## 🎯 使用場景

### 場景 1: 登入用戶 (有個人衣櫃)

```python
# 查詢: user_wardrobe (3件) + items (7件) = 10件
response, items, keywords = generate_wardrobe_recommendation(
    user_input="推薦約會穿搭",
    user_id=1  # ✅ 有 user_id
)

# 結果:
# - 白色襯衫 (user_wardrobe)
# - 黑色西裝褲 (user_wardrobe)
# - 休閒鞋 (user_wardrobe)
# - 領帶 (items)
# - 皮帶 (items)
# - ...
```

### 場景 2: 未登入用戶

```python
# 查詢: items (10件)
response, items, keywords = generate_wardrobe_recommendation(
    user_input="推薦運動穿搭",
    user_id=None  # ❌ 無 user_id
)

# 結果: 全部來自 items
```

### 場景 3: 新用戶 (衣櫃為空)

```python
# 查詢: user_wardrobe (0件) + items (10件) = 10件
response, items, keywords = generate_wardrobe_recommendation(
    user_input="推薦休閒穿搭",
    user_id=999  # ✅ 有 user_id, 但衣櫃是空的
)

# 結果: 自動補充系統商品
```

---

## ⚠️ 重要提醒

### 1. 必須傳入 user_id (如果可能)

```python
# ❌ 錯誤: 有登入但沒傳 user_id
user_id = session.get('user_id')  # user_id = 1
response, items, keywords = generate_wardrobe_recommendation(
    user_input="推薦穿搭",
    # user_id 沒傳! ← 會錯過個人衣櫃
)

# ✅ 正確
user_id = session.get('user_id')
response, items, keywords = generate_wardrobe_recommendation(
    user_input="推薦穿搭",
    user_id=user_id  # ← 傳入 user_id
)
```

### 2. 資料庫欄位已更新

```sql
-- ❌ 舊欄位
user_wardrobe.material

-- ✅ 新欄位
user_wardrobe.occasion
```

### 3. 檢查資料來源

```python
# 區分推薦來源
for item in items:
    if item['_source'] == 'user_wardrobe':
        print(f"📦 您的衣物: {item['_title']}")
    elif item['_source'] == 'items':
        print(f"🛍️ 推薦商品: {item['_title']}")
```

---

## 🧪 測試清單

- [ ] 有 user_id + 衣櫃有資料 → 混合推薦
- [ ] 有 user_id + 衣櫃為空 → 自動補充 items
- [ ] 無 user_id → 只推薦 items
- [ ] 關鍵字篩選正常
- [ ] `_source` 標記正確
- [ ] 時間格式處理正常
- [ ] 價格格式處理正常

---

## 📞 需要幫助?

如果遇到問題:
1. 檢查 `user_id` 是否正確傳入
2. 確認資料庫欄位 `occasion` 存在
3. 查看 Flask logs: `docker compose logs -f flask`
4. 查看 `_source` 欄位確認資料來源

---

**更新完成!** ✅
