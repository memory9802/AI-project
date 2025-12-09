#!/bin/bash
# 聊天機器人測試腳本
# 用途: 快速測試 Gemini AI + 資料庫連接功能

echo "======================================"
echo "  聊天機器人功能測試"
echo "======================================"
echo ""

# 檢查容器狀態
echo "📦 檢查 Docker 容器狀態..."
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "outfit-flask|outfit-mysql"
echo ""

# 測試 1: 資料庫查詢 (中文)
echo "✅ 測試 1: 資料庫查詢 (中文類別: 上衣)"
curl -s "http://localhost:5001/aichat/items?category=上衣" | \
  python3 -c "import json, sys; data=json.load(sys.stdin); print(f'  回傳 {len(data)} 件商品'); print(f'  第一件: {data[0][\"name\"] if data else \"無資料\"}')"
echo ""

# 測試 2: 資料庫查詢 (英文)
echo "✅ 測試 2: 資料庫查詢 (英文類別: shoes)"
curl -s "http://localhost:5001/aichat/items?category=shoes" | \
  python3 -c "import json, sys; data=json.load(sys.stdin); print(f'  回傳 {len(data)} 件商品'); print(f'  第一件: {data[0][\"name\"] if data else \"無資料\"}')"
echo ""

# 測試 3: 混合推薦 (DB + AI)
echo "✅ 測試 3: 混合推薦 (資料庫 + Gemini AI)"
RESPONSE=$(curl -s -X POST http://localhost:5001/aichat/wardrobe_recommend \
  -H "Content-Type: application/json" \
  -d '{"message":"推薦我適合約會的衣服","session_id":"test-script","model":"auto"}')

echo "$RESPONSE" | python3 -c "
import json, sys
data = json.load(sys.stdin)
db_count = len(data.get('db_data', []))
ai_response = data.get('response', '')
keywords = data.get('keywords', [])

print(f'  資料庫查詢: {db_count} 件商品 ✅' if db_count > 0 else '  資料庫查詢: 失敗 ❌')

if 'API 配額' in ai_response or '無法回應' in ai_response:
    print(f'  Gemini AI: ⚠️  API 配額限制 (429 錯誤)')
    print(f'  提示: 等待配額恢復或更新 API Key')
elif ai_response:
    print(f'  Gemini AI: ✅ 成功回應')
    print(f'  關鍵字: {keywords}')
else:
    print(f'  Gemini AI: ❌ 無回應')
"
echo ""

# 測試 4: 資料品質檢查
echo "✅ 測試 4: 資料品質檢查"
curl -s http://localhost:5001/aichat/data_quality | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
if 'error' in data:
    print(f'  ❌ 錯誤: {data[\"error\"]}')
else:
    wardrobe_samples = len(data.get('user_wardrobe', {}).get('sample_data', []))
    items_samples = len(data.get('items', {}).get('sample_data', []))
    print(f'  user_wardrobe 樣本: {wardrobe_samples} 件')
    print(f'  items 樣本: {items_samples} 件')
"
echo ""

# 檢查 Gemini API 配額狀態
echo "🔍 檢查 Gemini API 狀態..."
docker logs outfit-flask 2>&1 | grep -E "Gemini|429|quota" | tail -3
echo ""

echo "======================================"
echo "  測試完成!"
echo "======================================"
echo ""
echo "📝 完整測試報告: CHATBOT_TEST_REPORT.md"
echo "📊 資料庫管理: http://localhost:8080 (phpMyAdmin)"
echo "🔗 API 端點: http://localhost:5001/aichat/*"
echo ""
