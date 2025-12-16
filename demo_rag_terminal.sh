#!/bin/bash
# =============================================
# RAG 權重推薦 Demo - 終端機執行腳本
# =============================================

# 顏色定義
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}   RAG 權重推薦系統 Demo 展示${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

# Demo 1: 評分統計總覽
echo -e "${GREEN}🎯 Demo 1: 評分統計總覽${NC}"
echo "展示所有有評分的商品"
echo ""
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -t -e "
SELECT 
    item_id as ID,
    rating_count as Count,
    ROUND(avg_rating, 2) as Avg,
    ROUND(high_rating_ratio, 2) as HighRatio,
    CASE 
        WHEN rating_count >= 20 THEN 'HIGH'
        WHEN rating_count >= 10 THEN 'MEDIUM'
        ELSE 'LOW'
    END as Level
FROM item_stats 
WHERE rating_count > 0 
ORDER BY rating_count DESC;
" 2>/dev/null
echo ""
read -p "按 Enter 繼續..."
echo ""

# Demo 2: RAG 權重推薦 Top 10
echo -e "${GREEN}🎯 Demo 2: RAG 權重推薦 Top 10${NC}"
echo "使用公式: Count × Avg × (1 + HighRatio)"
echo ""
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -t -e "
SELECT 
    s.item_id as ItemID,
    CONCAT('Item-', s.item_id, ' (', UPPER(i.category), ')') as ItemName,
    s.rating_count as Count,
    ROUND(s.avg_rating, 2) as Avg,
    ROUND(s.rating_count * s.avg_rating * (1 + s.high_rating_ratio), 2) as RAG_Score,
    CASE 
        WHEN s.rating_count >= 20 THEN 'STRONG'
        WHEN s.rating_count >= 10 THEN 'MEDIUM'
        ELSE 'NORMAL'
    END as Level
FROM item_stats s
JOIN items i ON s.item_id = i.id
WHERE s.rating_count > 0
ORDER BY RAG_Score DESC
LIMIT 10;
" 2>/dev/null
echo ""
read -p "按 Enter 繼續..."
echo ""

# Demo 3: 傳統推薦 Top 10
echo -e "${GREEN}🎯 Demo 3: 傳統推薦 Top 10 (僅平均分)${NC}"
echo "展示問題: 評分少的商品會排前面"
echo ""
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -t -e "
SELECT 
    s.item_id as ItemID,
    CONCAT('Item-', s.item_id, ' (', UPPER(i.category), ')') as ItemName,
    s.rating_count as Count,
    ROUND(s.avg_rating, 2) as Avg,
    CASE 
        WHEN s.rating_count < 3 THEN 'TOO_FEW'
        WHEN s.rating_count < 10 THEN 'FEW'
        ELSE 'OK'
    END as Warning
FROM item_stats s
JOIN items i ON s.item_id = i.id
WHERE s.rating_count > 0
ORDER BY s.avg_rating DESC, s.rating_count DESC
LIMIT 10;
" 2>/dev/null
echo ""
read -p "按 Enter 繼續..."
echo ""

# Demo 4: 直接對比
echo -e "${GREEN}🎯 Demo 4: RAG vs 傳統推薦 (Top 1 對比)${NC}"
echo ""
echo -e "${YELLOW}RAG 推薦 Top 1:${NC}"
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -t -e "
SELECT 
    'RAG' as Method,
    s.item_id as ID,
    s.rating_count as Count,
    ROUND(s.avg_rating, 2) as Avg,
    ROUND(s.rating_count * s.avg_rating * (1 + s.high_rating_ratio), 2) as Score,
    'Reliable' as Status
FROM item_stats s
WHERE s.rating_count > 0
ORDER BY (s.rating_count * s.avg_rating * (1 + s.high_rating_ratio)) DESC
LIMIT 1;
" 2>/dev/null

echo ""
echo -e "${YELLOW}傳統推薦 Top 1:${NC}"
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -t -e "
SELECT 
    'Traditional' as Method,
    s.item_id as ID,
    s.rating_count as Count,
    ROUND(s.avg_rating, 2) as Avg,
    ROUND(s.avg_rating, 2) as Score,
    CASE WHEN s.rating_count < 10 THEN 'Unreliable' ELSE 'OK' END as Status
FROM item_stats s
WHERE s.rating_count > 0
ORDER BY s.avg_rating DESC
LIMIT 1;
" 2>/dev/null
echo ""
read -p "按 Enter 繼續..."
echo ""

# Demo 5: 星級分布
echo -e "${GREEN}🎯 Demo 5: 詳細星級分布${NC}"
echo "展示評分構成"
echo ""
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -t -e "
SELECT 
    item_id as ID,
    rating_count as Total,
    rating_5_count as Star5,
    rating_4_count as Star4,
    rating_3_count as Star3,
    rating_2_count as Star2,
    rating_1_count as Star1,
    CONCAT(ROUND(rating_5_count * 100.0 / rating_count, 1), '%') as Star5_Pct,
    ROUND(avg_rating, 2) as Avg
FROM item_stats
WHERE rating_count > 0
ORDER BY rating_count DESC
LIMIT 10;
" 2>/dev/null
echo ""

# 總結
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}   📊 重點說明${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}🎯 RAG 推薦優勢:${NC}"
echo "   商品 5099: 45評分, 4.07★ → 權重 337.80"
echo "   ✅ 評分充足, 結果可靠"
echo ""
echo -e "${YELLOW}⚠️  傳統推薦問題:${NC}"
echo "   商品 5097: 4評分, 5.00★ → 權重 5.00"
echo "   ⚠️  評分太少, 結果不可靠"
echo ""
echo -e "${GREEN}💡 結論:${NC}"
echo "   RAG 權重推薦能有效平衡「評分質量」和「評分數量」"
echo "   避免少數高分商品誤導推薦結果"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
