-- =============================================
-- RAG 評分系統 Demo 展示查詢
-- =============================================
-- 
-- � DBeaver 執行說明:
-- 1. 選擇要執行的查詢 (Ctrl+Enter 執行當前查詢)
-- 2. 或者逐個查詢執行 (選中後 Ctrl+Enter)
-- 3. 避免一次執行所有查詢導致結果標籤頁過多
-- 
-- =============================================

-- �📊 展示 1: 所有測試商品的原始評分統計
-- =============================================
-- 說明: 查看測試資料的基本評分統計
-- 
SELECT 
    i.id as 商品ID,
    i.name as 商品名稱,
    s.avg_rating as 平均評分,
    s.rating_count as 評分次數,
    s.high_rating_ratio as 好評率
FROM items i
INNER JOIN item_stats s ON s.item_id = i.id
WHERE s.item_source = 'items'
ORDER BY s.avg_rating DESC;

-- ⚠️ 展示 2: 無權重推薦的問題
-- =============================================
-- 說明: 只看平均評分的推薦方式會把評分次數少的商品排前面
-- 問題: 4.9★(2次) 會排在 4.8★(25次) 前面,但可靠性不足
-- 
SELECT 
    i.name as 商品名稱,
    s.avg_rating as 平均評分,
    s.rating_count as 評分次數,
    CASE 
        WHEN s.rating_count < 5 THEN '⚠️ 評分太少,不可靠'
        WHEN s.rating_count >= 20 THEN '✅ 評分充足,可靠'
        ELSE '⚡ 評分一般'
    END as 可靠性
FROM items i
INNER JOIN item_stats s ON s.item_id = i.id
WHERE s.item_source = 'items'
ORDER BY s.avg_rating DESC, s.rating_count DESC
LIMIT 10;

-- ✅ 展示 3: RAG 權重推薦 (完整計算過程)
-- =============================================
-- 說明: 使用規則式參數計算綜合分數
-- 公式: 評分權重 × 人氣權重 = 綜合分數
-- 
SELECT 
    i.name as 商品名稱,
    s.avg_rating as 平均評分,
    s.rating_count as 評分次數,
    CASE
        WHEN s.avg_rating >= 4.5 THEN 1.5
        WHEN s.avg_rating >= 3.5 THEN 1.25
        WHEN s.avg_rating >= 2.5 THEN 1.0
        ELSE 0.75
    END as 評分權重,
    CASE
        WHEN s.rating_count >= 20 THEN 1.3
        WHEN s.rating_count >= 10 THEN 1.2
        WHEN s.rating_count >= 5  THEN 1.1
        ELSE 1.0
    END as 人氣權重,
    ROUND(
        (CASE WHEN s.avg_rating >= 4.5 THEN 1.5
              WHEN s.avg_rating >= 3.5 THEN 1.25
              WHEN s.avg_rating >= 2.5 THEN 1.0
              ELSE 0.75 END) * 
        (CASE WHEN s.rating_count >= 20 THEN 1.3
              WHEN s.rating_count >= 10 THEN 1.2
              WHEN s.rating_count >= 5  THEN 1.1
              ELSE 1.0 END), 
        2
    ) as 綜合分數,
    CASE 
        WHEN s.rating_count >= 20 AND s.avg_rating >= 4.5 THEN '🌟 高分熱門'
        WHEN s.rating_count >= 10 AND s.avg_rating >= 4.0 THEN '⭐ 常評高分'
        WHEN s.rating_count < 5 AND s.avg_rating >= 4.5 THEN '⚠️ 新品高分'
        ELSE '📊 一般商品'
    END as 推薦等級
FROM items i
INNER JOIN item_stats s ON s.item_id = i.id
WHERE s.item_source = 'items'
ORDER BY 綜合分數 DESC, s.avg_rating DESC
LIMIT 10;

-- 🔄 展示 4: 並排對比 (無權重 vs RAG 權重)
-- =============================================
-- 說明: 對比無權重推薦 vs RAG 權重推薦的結果差異
-- 注意: 這個查詢會產生兩個結果集,可以分開執行
-- 
-- 4-1: 無權重推薦結果 (只看平均評分)
SELECT 
    '無權重' as 推薦方式,
    RANK() OVER (ORDER BY s.avg_rating DESC, s.rating_count DESC) as 排名,
    i.name as 商品名稱,
    s.avg_rating as 平均評分,
    s.rating_count as 評分次數,
    NULL as 綜合分數
FROM items i
INNER JOIN item_stats s ON s.item_id = i.id
WHERE s.item_source = 'items'
ORDER BY s.avg_rating DESC, s.rating_count DESC
LIMIT 5;

-- 4-2: RAG 權重推薦結果 (綜合評分與人氣)
SELECT 
    'RAG權重' as 推薦方式,
    RANK() OVER (ORDER BY 
        (CASE WHEN s.avg_rating >= 4.5 THEN 1.5
              WHEN s.avg_rating >= 3.5 THEN 1.25
              WHEN s.avg_rating >= 2.5 THEN 1.0
              ELSE 0.75 END) * 
        (CASE WHEN s.rating_count >= 20 THEN 1.3
              WHEN s.rating_count >= 10 THEN 1.2
              WHEN s.rating_count >= 5  THEN 1.1
              ELSE 1.0 END) DESC
    ) as 排名,
    i.name as 商品名稱,
    s.avg_rating as 平均評分,
    s.rating_count as 評分次數,
    ROUND(
        (CASE WHEN s.avg_rating >= 4.5 THEN 1.5
              WHEN s.avg_rating >= 3.5 THEN 1.25
              WHEN s.avg_rating >= 2.5 THEN 1.0
              ELSE 0.75 END) * 
        (CASE WHEN s.rating_count >= 20 THEN 1.3
              WHEN s.rating_count >= 10 THEN 1.2
              WHEN s.rating_count >= 5  THEN 1.1
              ELSE 1.0 END), 
        2
    ) as 綜合分數
FROM items i
INNER JOIN item_stats s ON s.item_id = i.id
WHERE s.item_source = 'items'
ORDER BY 綜合分數 DESC
LIMIT 5;

-- 📈 展示 5: 使用視圖查詢 (v_items_with_ratings)
-- =============================================
-- 說明: 直接使用視圖查詢,權重已經預先計算好
-- 優勢: 查詢速度快,結果一致
-- 
SELECT 
    name as 商品名稱,
    avg_rating as 平均評分,
    rating_count as 評分次數,
    rating_weight as 評分權重,
    popularity_weight as 人氣權重,
    final_score as 綜合分數
FROM v_items_with_ratings
ORDER BY final_score DESC
LIMIT 10;

-- 💡 展示 6: RAG 優勢說明
-- =============================================
-- 說明: 分析問題商品與優質商品,展示 RAG 如何處理
-- 
SELECT 
    '問題商品' as 分析類型,
    i.name as 商品名稱,
    s.avg_rating as 平均評分,
    s.rating_count as 評分次數,
    '評分次數太少,平均分不可靠' as 問題說明,
    '無權重推薦會排在前面' as 無權重排名,
    'RAG 會適度降權,避免過度推薦' as RAG處理
FROM items i
INNER JOIN item_stats s ON s.item_id = i.id
WHERE s.item_source = 'items' 
  AND s.rating_count < 5 
  AND s.avg_rating >= 4.5

UNION ALL

SELECT 
    '優質商品' as 分析類型,
    i.name as 商品名稱,
    s.avg_rating as 平均評分,
    s.rating_count as 評分次數,
    '高評分且評價充足,可靠推薦' as 問題說明,
    '無權重推薦可能排後面' as 無權重排名,
    'RAG 會優先推薦,因為可靠性高' as RAG處理
FROM items i
INNER JOIN item_stats s ON s.item_id = i.id
WHERE s.item_source = 'items' 
  AND s.rating_count >= 20 
  AND s.avg_rating >= 4.5;
