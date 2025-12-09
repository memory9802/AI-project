#!/bin/bash

# ========================================
# 拆分 00_init_with_data.sql 為模組化檔案
# ========================================

INIT_DIR="/Users/liaoyiting/Desktop/stylerec/init"
SOURCE_FILE="$INIT_DIR/00_init_with_data.sql"
DATA_DIR="$INIT_DIR/data"
SCHEMA_FILE="$INIT_DIR/00_schema.sql"

echo "🚀 開始拆分資料庫檔案..."
echo "================================"

# 建立目錄
mkdir -p "$DATA_DIR"

# ============================
# 1. 提取表格結構 (schema)
# ============================
echo "📋 步驟 1/6: 提取表格結構..."

{
    # MySQL dump 標頭
    sed -n '1,/^USE outfit_db;$/p' "$SOURCE_FILE"
    echo ""
    
    # 提取所有 CREATE TABLE (不包含 INSERT)
    sed -n '/^DROP TABLE IF EXISTS users;/,/^COMMENT=.*使用者表.*$/p' "$SOURCE_FILE"
    echo ""
    
    sed -n '/^DROP TABLE IF EXISTS items;/,/^COMMENT=.*單品表.*$/p' "$SOURCE_FILE"
    echo ""
    
    sed -n '/^DROP TABLE IF EXISTS user_wardrobe;/,/^COMMENT=.*使用者個人衣櫃.*$/p' "$SOURCE_FILE"
    echo ""
    
    sed -n '/^DROP TABLE IF EXISTS partner_products;/,/^COMMENT=.*合作品牌.*$/p' "$SOURCE_FILE"
    echo ""
    
    sed -n '/^DROP TABLE IF EXISTS conversation_history;/,/^COMMENT=.*AI 聊天對話記錄.*$/p' "$SOURCE_FILE"
    echo ""
    
    sed -n '/^DROP TABLE IF EXISTS rating;/,/^COMMENT=.*商品評分表.*$/p' "$SOURCE_FILE"
    echo ""
    
} > "$SCHEMA_FILE"

echo "✅ 表格結構已儲存到: 00_schema.sql"

# ============================
# 2. 提取 users 資料
# ============================
echo "👤 步驟 2/6: 提取 users 資料..."

{
    echo "-- users 表資料"
    echo "-- 自動生成於 $(date)"
    echo ""
    sed -n '/-- Dumping data for table `users`/,/^UNLOCK TABLES;$/p' "$SOURCE_FILE"
} > "$DATA_DIR/01_users.sql"

echo "✅ users 資料已儲存到: data/01_users.sql"

# ============================
# 3. 提取 items 資料
# ============================
echo "👔 步驟 3/6: 提取 items 資料..."

{
    echo "-- items 表資料"
    echo "-- 自動生成於 $(date)"
    echo "-- 包含商品主資料 (44,708 筆)"
    echo ""
    sed -n '/-- Dumping data for table `items`/,/^UNLOCK TABLES;$/p' "$SOURCE_FILE"
} > "$DATA_DIR/02_items.sql"

echo "✅ items 資料已儲存到: data/02_items.sql"

# ============================
# 4. 提取 user_wardrobe 資料
# ============================
echo "🗄️ 步驟 4/6: 提取 user_wardrobe 資料..."

{
    echo "-- user_wardrobe 表資料"
    echo "-- 自動生成於 $(date)"
    echo ""
    sed -n '/-- Dumping data for table `user_wardrobe`/,/^UNLOCK TABLES;$/p' "$SOURCE_FILE"
} > "$DATA_DIR/03_user_wardrobe.sql"

echo "✅ user_wardrobe 資料已儲存到: data/03_user_wardrobe.sql"

# ============================
# 5. 提取 partner_products 資料
# ============================
echo "🤝 步驟 5/6: 提取 partner_products 資料..."

{
    echo "-- partner_products 表資料"
    echo "-- 自動生成於 $(date)"
    echo ""
    sed -n '/-- Dumping data for table `partner_products`/,/^UNLOCK TABLES;$/p' "$SOURCE_FILE"
} > "$DATA_DIR/04_partner_products.sql"

echo "✅ partner_products 資料已儲存到: data/04_partner_products.sql"

# ============================
# 6. 提取其他表格資料
# ============================
echo "📦 步驟 6/6: 提取其他表格資料..."

{
    echo "-- conversation_history 和 rating 表資料"
    echo "-- 自動生成於 $(date)"
    echo ""
    
    # conversation_history (通常為空)
    sed -n '/-- Dumping data for table `conversation_history`/,/^UNLOCK TABLES;$/p' "$SOURCE_FILE"
    echo ""
    
    # rating (通常為空)
    sed -n '/-- Dumping data for table `rating`/,/^UNLOCK TABLES;$/p' "$SOURCE_FILE"
    
} > "$DATA_DIR/05_others.sql"

echo "✅ 其他表格資料已儲存到: data/05_others.sql"

# ============================
# 7. 顯示檔案大小
# ============================
echo ""
echo "================================"
echo "📊 檔案大小統計:"
echo "================================"
ls -lh "$SCHEMA_FILE" "$DATA_DIR"/*.sql | awk '{print $9 "\t" $5}'

echo ""
echo "🎉 拆分完成!"
echo ""
echo "📁 新結構:"
echo "  init/"
echo "  ├── 00_schema.sql          (表格結構)"
echo "  └── data/"
echo "      ├── 01_users.sql       (組員維護)"
echo "      ├── 02_items.sql       (您維護)"
echo "      ├── 03_user_wardrobe.sql (組員維護)"
echo "      ├── 04_partner_products.sql"
echo "      └── 05_others.sql"
echo ""
echo "💡 下一步:"
echo "  1. 檢查拆分結果: ls -lh init/data/"
echo "  2. 測試導入: ./init/import_all.sh"
echo "  3. 提交變更: git add init/"
