((venv) ) liaoyiting@MacBook-Air-Rosy stylerec % docker exec outfit-mysql mysql -uroot -prootpassword outfit_db < init/demo_rag_quick.sql
mysql: [Warning] Using a password on the command line interface can be insecure.-- =============================================
-- RAG 權重推薦 Demo 快速展示版
-- =============================================
-- 
-- 📌 使用方法:
-- 
-- 方法 1 - DBeaver (推薦用於報告展示):
--   選中查詢 → Ctrl+Enter (Mac: Cmd+Enter)
--
-- 方法 2 - 終端機互動模式 (推薦):
--   docker exec -it outfit-mysql mysql -uroot -prootpassword outfit_db
--   然後複製貼上下方查詢執行
--
-- 方法 3 - 終端機直接執行單一查詢:
--   docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "SELECT * FROM item_stats WHERE rating_count > 0 ORDER BY rating_count DESC;"
--
-- =============================================

-- 🎯 Demo 1: 評分統計總覽
-- 展示所有有評分的商品
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


-- 🎯 Demo 2: RAG 權重推薦 Top 10
-- 使用公式: Count × Avg × (1 + HighRatio)
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


-- 🎯 Demo 3: 傳統推薦 Top 10 (僅平均分)
-- 展示問題: 評分少的商品會排前面
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


-- 🎯 Demo 4: 直接對比 (Top 1)
-- 清楚展示兩種推薦的差異
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
LIMIT 1

UNION ALL

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


-- 🎯 Demo 5: 詳細星級分布
-- 展示評分構成
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


-- =============================================
-- 📊 重點說明
-- =============================================
-- 
-- 🎯 RAG 推薦優勢:
--    商品 5099: 45評分, 4.07★ → 權重 337.80
--    ✅ 評分充足, 結果可靠
--
-- ⚠️ 傳統推薦問題:
--    商品 5097: 4評分, 5.00★ → 權重 5.00
--    ⚠️ 評分太少, 結果不可靠
--
-- 💡 結論:
--    RAG 權重推薦能有效平衡「評分質量」和「評分數量」
--    避免少數高分商品誤導推薦結果
--
-- =============================================
