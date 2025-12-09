#!/bin/bash

# API 測試腳本 - 評分權重推薦系統
# 使用 demo_user (ID: 54) 進行測試

# 設定變數
BASE_URL="http://localhost:5001"
USER_ID=54
ITEM_SOURCE="items"

# 顏色輸出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "評分權重推薦系統 API 測試"
echo "=========================================="
echo ""

# 函數: 執行 API 測試
test_api() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    
    echo -e "${YELLOW}測試: ${name}${NC}"
    echo "請求: $method $endpoint"
    
    if [ -z "$data" ]; then
        response=$(curl -s -X $method "${BASE_URL}${endpoint}")
    else
        echo "資料: $data"
        response=$(curl -s -X $method \
            -H "Content-Type: application/json" \
            -d "$data" \
            "${BASE_URL}${endpoint}")
    fi
    
    echo "回應:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    echo ""
    echo "----------------------------------------"
    echo ""
}

# ===========================
# 1. 測試提交評分
# ===========================

echo -e "${GREEN}=== 1. 測試提交評分 ===${NC}"
echo ""

# 1.1 提交高分評分
test_api "提交高分評分 (5星)" "POST" "/recommendation/api/rating" \
'{
    "item_id": 5092,
    "item_source": "items",
    "rating_value": 5,
    "review_text": "超級喜歡這件商品!"
}'

# 1.2 提交低分評分
test_api "提交低分評分 (2星)" "POST" "/recommendation/api/rating" \
'{
    "item_id": 5102,
    "item_source": "items",
    "rating_value": 2,
    "review_text": "不太適合我"
}'

# 1.3 更新評分 (同一商品)
test_api "更新評分 (改為4星)" "POST" "/recommendation/api/rating" \
'{
    "item_id": 5092,
    "item_source": "items",
    "rating_value": 4,
    "review_text": "重新評估後覺得是4星"
}'

# ===========================
# 2. 測試推薦查詢
# ===========================

echo -e "${GREEN}=== 2. 測試推薦查詢 ===${NC}"
echo ""

# 2.1 取得帶權重推薦 (前10件)
test_api "取得帶權重推薦 (前10件)" "GET" \
"/recommendation/api/recommendations?item_source=items&limit=10&exclude_rated=true"

# 2.2 取得推薦比較 (無權重 vs 有權重)
test_api "推薦比較 (無權重 vs 有權重)" "GET" \
"/recommendation/api/recommendations/comparison?item_source=items&limit=5"

# 2.3 取得高評分商品
test_api "取得高評分商品 (前5件)" "GET" \
"/recommendation/api/top-rated?item_source=items&limit=5&min_rating_count=3"

# ===========================
# 3. 測試用戶評分查詢
# ===========================

echo -e "${GREEN}=== 3. 測試用戶評分查詢 ===${NC}"
echo ""

# 3.1 查詢用戶所有評分
test_api "查詢用戶所有評分" "GET" \
"/recommendation/api/ratings/user/${USER_ID}?limit=10"

# 3.2 查詢用戶評分摘要
test_api "查詢用戶評分摘要" "GET" \
"/recommendation/api/ratings/user/${USER_ID}/summary"

# ===========================
# 4. 測試商品統計查詢
# ===========================

echo -e "${GREEN}=== 4. 測試商品統計查詢 ===${NC}"
echo ""

# 4.1 查詢商品統計
test_api "查詢商品統計 (ID: 5092)" "GET" \
"/recommendation/api/item-stats/5092?item_source=items"

# 4.2 檢查是否已評分
test_api "檢查是否已評分 (ID: 5092)" "GET" \
"/recommendation/api/rating/check/5092?item_source=items"

# 4.3 檢查未評分商品
test_api "檢查未評分商品 (ID: 5120)" "GET" \
"/recommendation/api/rating/check/5120?item_source=items"

# ===========================
# 5. 測試全站統計
# ===========================

echo -e "${GREEN}=== 5. 測試全站統計 ===${NC}"
echo ""

test_api "查詢全站評分統計" "GET" "/recommendation/api/statistics"

# ===========================
# 6. 測試刪除評分
# ===========================

echo -e "${GREEN}=== 6. 測試刪除評分 ===${NC}"
echo ""

# 6.1 刪除評分
test_api "刪除評分 (ID: 5102)" "DELETE" \
"/recommendation/api/rating/5102?item_source=items"

# 6.2 驗證刪除 (檢查是否還存在)
test_api "驗證刪除結果" "GET" \
"/recommendation/api/rating/check/5102?item_source=items"

echo ""
echo -e "${GREEN}=========================================="
echo "測試完成!"
echo "==========================================${NC}"
echo ""
echo "注意事項:"
echo "1. 確保 Flask 應用程式正在運行 (port 5001)"
echo "2. 確保 demo_user (ID: 54) 已建立"
echo "3. 確保測試商品 (ID: 5092-5121) 已存在"
echo ""
