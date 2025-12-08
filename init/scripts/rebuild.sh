#!/bin/bash

# 輸出檔案
OUTPUT="00_init_with_data_new.sql"

# 清空輸出檔案
> "$OUTPUT"

# 1. MySQL dump 標頭 (從備份檔取得前 20 行)
head -n 20 00_init_with_data.sql.backup >> "$OUTPUT"
echo "" >> "$OUTPUT"

# 2. 從 schema 檔案提取每個表的 DROP TABLE 和 CREATE TABLE
# users 表
sed -n '/^DROP TABLE IF EXISTS users;/,/^COMMENT=.*使用者表.*$/p' 01_schema_only.sql >> "$OUTPUT"
echo "" >> "$OUTPUT"

# users 資料
echo "--" >> "$OUTPUT"
echo "-- Dumping data for table \`users\`" >> "$OUTPUT"
echo "--" >> "$OUTPUT"
echo "" >> "$OUTPUT"
sed -n '181,185p' 00_init_with_data.sql.backup >> "$OUTPUT"
echo "" >> "$OUTPUT"

# items 表
sed -n '/^DROP TABLE IF EXISTS items;/,/^COMMENT=.*單品表.*$/p' 01_schema_only.sql >> "$OUTPUT"
echo "" >> "$OUTPUT"

# items 資料
echo "--" >> "$OUTPUT"
echo "-- Dumping data for table \`items\`" >> "$OUTPUT"
echo "--" >> "$OUTPUT"
echo "" >> "$OUTPUT"
sed -n '82,93p' 00_init_with_data.sql.backup >> "$OUTPUT"
echo "" >> "$OUTPUT"

# user_wardrobe 表
sed -n '/^DROP TABLE IF EXISTS user_wardrobe;/,/^COMMENT=.*使用者個人衣櫃.*$/p' 01_schema_only.sql >> "$OUTPUT"
echo "" >> "$OUTPUT"

# user_wardrobe 資料 (空)
echo "--" >> "$OUTPUT"
echo "-- Dumping data for table \`user_wardrobe\`" >> "$OUTPUT"
echo "--" >> "$OUTPUT"
echo "" >> "$OUTPUT"
sed -n '152,155p' 00_init_with_data.sql.backup >> "$OUTPUT"
echo "" >> "$OUTPUT"

# partner_products 表
sed -n '/^DROP TABLE IF EXISTS partner_products;/,/^COMMENT=.*合作品牌.*$/p' 01_schema_only.sql >> "$OUTPUT"
echo "" >> "$OUTPUT"

# partner_products 資料
echo "--" >> "$OUTPUT"
echo "-- Dumping data for table \`partner_products\`" >> "$OUTPUT"
echo "--" >> "$OUTPUT"
echo "" >> "$OUTPUT"
sed -n '119,123p' 00_init_with_data.sql.backup >> "$OUTPUT"
echo "" >> "$OUTPUT"

# conversation_history 表 (新結構)
sed -n '/^DROP TABLE IF EXISTS conversation_history;/,/^COMMENT=.*AI 聊天對話記錄.*$/p' 01_schema_only.sql >> "$OUTPUT"
echo "" >> "$OUTPUT"

# conversation_history 資料 (空)
echo "--" >> "$OUTPUT"
echo "-- Dumping data for table \`conversation_history\`" >> "$OUTPUT"
echo "--" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "LOCK TABLES \`conversation_history\` WRITE;" >> "$OUTPUT"
echo "/*!40000 ALTER TABLE \`conversation_history\` DISABLE KEYS */;" >> "$OUTPUT"
echo "/*!40000 ALTER TABLE \`conversation_history\` ENABLE KEYS */;" >> "$OUTPUT"
echo "UNLOCK TABLES;" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# rating 表 (新增)
sed -n '/^DROP TABLE IF EXISTS rating;/,/^COMMENT=.*商品評分表.*$/p' 01_schema_only.sql >> "$OUTPUT"
echo "" >> "$OUTPUT"

# rating 資料 (空)
echo "--" >> "$OUTPUT"
echo "-- Dumping data for table \`rating\`" >> "$OUTPUT"
echo "--" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "LOCK TABLES \`rating\` WRITE;" >> "$OUTPUT"
echo "/*!40000 ALTER TABLE \`rating\` DISABLE KEYS */;" >> "$OUTPUT"
echo "/*!40000 ALTER TABLE \`rating\` ENABLE KEYS */;" >> "$OUTPUT"
echo "UNLOCK TABLES;" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# 3. MySQL dump 結尾
tail -n 2 00_init_with_data.sql.backup >> "$OUTPUT"

echo "✅ 成功生成新檔案: $OUTPUT"
echo "📝 已使用乾淨的結構定義並保留所有資料"
