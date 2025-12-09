#!/bin/bash
"""
Items 表格空值填補 - 執行指南
================================

執行順序 (重要!):
1. fill_category_from_clothing_type.py  (用 clothing_type 填補 category)
2. fill_gender_from_name.py             (用 name 填補 gender)
3. fill_remaining_nulls.py              (填補剩餘 NULL 值)

特性:
✅ 分批處理,避免 token 爆炸
✅ 進度保存,可隨時中斷恢復
✅ 詳細日誌記錄
✅ 低資料庫負載
"""

# ==========================================
# 步驟 1: 填補 category (從 clothing_type)
# ==========================================
echo "步驟 1/3: 填補 category 欄位 (從 clothing_type)"
echo "================================================"
echo ""
python3 fill_category_from_clothing_type.py

if [ $? -ne 0 ]; then
    echo "❌ category 填補失敗,中止流程"
    exit 1
fi

echo ""
echo "✅ category 填補完成"
echo ""
read -p "按 Enter 繼續下一步驟..."
echo ""

# ==========================================
# 步驟 2: 填補 gender (從 name)
# ==========================================
echo "步驟 2/3: 填補 gender 欄位 (從 name)"
echo "====================================="
echo ""
python3 fill_gender_from_name.py

if [ $? -ne 0 ]; then
    echo "❌ gender 填補失敗,中止流程"
    exit 1
fi

echo ""
echo "✅ gender 填補完成"
echo ""
read -p "按 Enter 繼續下一步驟..."
echo ""

# ==========================================
# 步驟 3: 填補剩餘 NULL 值
# ==========================================
echo "步驟 3/3: 填補剩餘 NULL 值"
echo "=========================="
echo ""
python3 fill_remaining_nulls.py

if [ $? -ne 0 ]; then
    echo "❌ 剩餘 NULL 填補失敗"
    exit 1
fi

echo ""
echo "================================================"
echo "🎉 全部填補流程完成!"
echo "================================================"
echo ""
echo "📊 建議執行以下 SQL 查詢驗證結果:"
echo ""
echo "SELECT "
echo "  COUNT(*) as total,"
echo "  SUM(CASE WHEN category IS NULL THEN 1 ELSE 0 END) as category_null,"
echo "  SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) as gender_null,"
echo "  SUM(CASE WHEN color IS NULL THEN 1 ELSE 0 END) as color_null"
echo "FROM items;"
echo ""
