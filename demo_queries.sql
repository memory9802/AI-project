-- =============================================
-- RAG 評分系統 Demo 展示查詢
-- =============================================

-- 📊 展示 1: 所有測試商品的原始評分統計
-- =============================================
SELECT 
    '📊 原始評分統計' as 展示項目;

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
SELECT 
    '⚠️ 無權重推薦 (只看平均評分)' as 展示項目;

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
SELECT 
    '✅ RAG 權重推薦 (評分權重 × 人氣權重)' as 展示項目;

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
SELECT 
    '🔄 推薦結果對比' as 展示項目;

-- 並排顯示
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
SELECT 
    '📈 使用視圖查詢 (v_items_with_ratings)' as 展示項目;

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
SELECT 
    '💡 RAG 系統優勢說明' as 展示項目;

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

-- 📝 說明重點
-- =============================================
SELECT '
RAG 評分推薦系統說明
====================

1️⃣ 無權重推薦的問題:
   - 只看平均評分,會把評分次數少的商品排在前面
   - 例如: 4.9★ (2次) 會排在 4.8★ (25次) 前面
   - 但 2 次評分的平均分不夠可靠

2️⃣ RAG 系統的解決方案:
   - 使用規則式參數: 評分權重 × 人氣權重 = 綜合分數
   - 評分權重: 根據平均評分計算 (5星→1.5, 4星→1.25, 3星→1.0)
   - 人氣權重: 根據評分次數計算 (20+次→1.3, 10+次→1.2, 5+次→1.1)
   - 綜合分數: 平衡評分質量與人氣

3️⃣ RAG 優勢:
   ✅ 優先推薦高分且評分充足的商品 (可靠推薦)
   ✅ 降低評分次數少的商品權重 (避免不可靠推薦)
   ✅ 完全透明可解釋 (每個權重都有明確公式)
   ✅ 不需要訓練資料 (規則式計算)

4️⃣ 技術定位:
   - 這是 RAG (Retrieval + Augmented + Generation) 系統
   - 使用規則式參數,而非機器學習訓練
   - 未來可擴展為 Fine-tuning 權重訓練系統
' as 說明內容;
