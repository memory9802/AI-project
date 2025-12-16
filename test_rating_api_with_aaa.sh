#!/bin/bash

# 評分推薦系統 API 測試腳本
# 使用 aaa 帳號測試

BASE_URL="http://localhost:5001"
COOKIE_FILE="/tmp/stylerec_cookies.txt"

echo "=========================================="
echo "評分推薦系統 API 測試"
echo "帳號: aaa"
echo "Port: 5001"
echo "=========================================="
echo ""

# 1. 登入取得 session cookie
echo "🔐 步驟 1: 登入系統..."
LOGIN_RESPONSE=$(curl -s -c $COOKIE_FILE -X POST "${BASE_URL}/login/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"aaa","password":"aaaaaa"}')

echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"
echo ""

# 檢查登入是否成功
if echo "$LOGIN_RESPONSE" | grep -q '"success": true'; then
    echo "✅ 登入成功!"
    
    # 取得用戶 ID
    USER_ID=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('user', {}).get('id', 'unknown'))" 2>/dev/null)
    echo "用戶 ID: $USER_ID"
else
    echo "❌ 登入失敗! 請檢查帳號密碼"
    exit 1
fi

echo ""
echo "=========================================="
echo "開始測試 API..."
echo "=========================================="
echo ""

# 2. 測試取得推薦 (帶權重)
echo "📊 步驟 2: 取得推薦商品 (帶權重)..."
curl -s -b $COOKIE_FILE "${BASE_URL}/recommendation/api/recommendations?item_source=items&limit=5&exclude_rated=false" | python3 -m json.tool | head -80
echo ""
echo "---"
echo ""

# 3. 測試全站統計
echo "📈 步驟 3: 查詢全站統計..."
curl -s -b $COOKIE_FILE "${BASE_URL}/recommendation/api/statistics" | python3 -m json.tool
echo ""
echo "---"
echo ""

# 4. 測試提交評分 (選擇第一件商品)
echo "⭐ 步驟 4: 提交評分 (商品 ID: 1, 評分: 5 星)..."
RATING_RESPONSE=$(curl -s -b $COOKIE_FILE -X POST "${BASE_URL}/recommendation/api/rating" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": 1,
    "item_source": "items",
    "rating_value": 5,
    "review_text": "測試評分 - 很棒的商品!"
  }')

echo "$RATING_RESPONSE" | python3 -m json.tool
echo ""
echo "---"
echo ""

# 5. 查詢用戶評分記錄
if [ "$USER_ID" != "unknown" ] && [ ! -z "$USER_ID" ]; then
    echo "📝 步驟 5: 查詢用戶評分記錄..."
    curl -s -b $COOKIE_FILE "${BASE_URL}/recommendation/api/ratings/user/${USER_ID}?limit=5" | python3 -m json.tool | head -80
    echo ""
    echo "---"
    echo ""
    
    # 6. 查詢用戶評分摘要
    echo "📊 步驟 6: 查詢用戶評分摘要..."
    curl -s -b $COOKIE_FILE "${BASE_URL}/recommendation/api/ratings/user/${USER_ID}/summary" | python3 -m json.tool
    echo ""
    echo "---"
    echo ""
fi

# 7. 查詢商品統計
echo "🔍 步驟 7: 查詢商品統計 (商品 ID: 1)..."
curl -s -b $COOKIE_FILE "${BASE_URL}/recommendation/api/item-stats/1?item_source=items" | python3 -m json.tool
echo ""
echo "---"
echo ""

# 8. 檢查是否已評分
echo "✅ 步驟 8: 檢查是否已評分 (商品 ID: 1)..."
curl -s -b $COOKIE_FILE "${BASE_URL}/recommendation/api/rating/check/1?item_source=items" | python3 -m json.tool
echo ""
echo "---"
echo ""

# 9. 測試推薦比較 (無權重 vs 有權重)
echo "🔄 步驟 9: 推薦比較 (無權重 vs 有權重)..."
curl -s -b $COOKIE_FILE "${BASE_URL}/recommendation/api/recommendations/comparison?item_source=items&limit=3" | python3 -m json.tool | head -100
echo ""
echo "---"
echo ""

echo "=========================================="
echo "✅ 測試完成!"
echo "=========================================="
echo ""
echo "Cookie 檔案保存在: $COOKIE_FILE"
echo "你可以使用此 cookie 繼續測試其他 API"
echo ""
echo "例如:"
echo "curl -b $COOKIE_FILE \"${BASE_URL}/recommendation/api/recommendations?limit=10\""
