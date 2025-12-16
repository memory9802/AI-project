-- =============================================
-- RAG 評分系統 Demo 展示查詢 (DBeaver 優化版)
-- =============================================
-- 
-- 📌 DBeaver 執行指南:
-- 
-- 方法 1: 逐個查詢執行 (推薦)
--   1. 用滑鼠選中要執行的查詢 (整段 SELECT ... FROM ... ;)
--   2. 按 Ctrl+Enter (Mac: Cmd+Enter) 執行選中的查詢
--   3. 查看結果後,選中下一個查詢繼續執行
--
-- 方法 2: 使用分號分隔執行
--   1. 確保每個查詢都以分號結尾
--   2. 按 Alt+X (Mac: Option+X) 執行當前查詢
--   3. DBeaver 會自動定位到下一個查詢
--
-- 方法 3: 關閉警告
--   1. 在警告對話框勾選 "Don't show this message again"
--   2. 或在 Preferences > Database > SQL Editor > Confirm result tabs close
--
-- =============================================


-- ===== 展示 1: 原始評分統計 =====
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


-- ===== 展示 2: 無權重推薦的問題 =====
-- 說明: 只看平均評分,4.9★(2次) 會排在 4.8★(25次) 前面
-- 問題: 評分次數少的商品可靠性不足
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


-- ===== 展示 3: RAG 權重推薦 (完整計算) =====
-- 說明: 評分權重 × 人氣權重 = 綜合分數
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


-- ===== 展示 4-1: 無權重推薦結果 =====
-- 
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


-- ===== 展示 4-2: RAG 權重推薦結果 =====
-- 
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


-- ===== 展示 5: 使用視圖查詢 =====
-- 說明: 權重已預先計算好,查詢速度更快
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


-- ===== 展示 6: RAG 優勢分析 =====
-- 說明: 分析問題商品與優質商品
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


-- =============================================
-- 📝 期末報告展示建議順序
-- =============================================
-- 
-- 1️⃣ 展示原始資料 (展示 1)
--    - 讓老師看到測試資料的基本統計
--
-- 2️⃣ 指出無權重推薦的問題 (展示 2)
--    - 說明只看平均分會有什麼問題
--    - 強調評分次數少的商品不可靠
--
-- 3️⃣ 展示 RAG 權重計算過程 (展示 3)
--    - 說明評分權重公式
--    - 說明人氣權重公式
--    - 展示綜合分數計算
--
-- 4️⃣ 對比推薦結果 (展示 4-1, 4-2)
--    - 並排展示無權重 vs RAG 權重
--    - 指出排名變化
--    - 說明 RAG 更可靠
--
-- 5️⃣ 展示視圖查詢 (展示 5)
--    - 說明使用視圖簡化查詢
--    - 展示系統效能
--
-- 6️⃣ 總結 RAG 優勢 (展示 6)
--    - 分析問題商品與優質商品
--    - 說明 RAG 如何處理
--
-- =============================================
