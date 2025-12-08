#!/usr/bin/env python3
"""
分批處理 items 表的空值填補
避免一次性處理大檔案造成記憶體或 token 問題
"""

import mysql.connector
from typing import List, Dict, Any

# 資料庫連接設定
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'rootpassword',
    'database': 'outfit_db',
    'charset': 'utf8mb4'
}

def connect_db():
    """連接資料庫"""
    return mysql.connector.connect(**DB_CONFIG)

def analyze_null_values():
    """分析空值情況"""
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT 
      COUNT(*) as total,
      SUM(CASE WHEN category IS NULL THEN 1 ELSE 0 END) as null_category,
      SUM(CASE WHEN color IS NULL THEN 1 ELSE 0 END) as null_color,
      SUM(CASE WHEN price IS NULL THEN 1 ELSE 0 END) as null_price,
      SUM(CASE WHEN image_url IS NULL THEN 1 ELSE 0 END) as null_image,
      SUM(CASE WHEN sku IS NULL THEN 1 ELSE 0 END) as null_sku,
      SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) as null_gender,
      SUM(CASE WHEN clothing_type IS NULL THEN 1 ELSE 0 END) as null_clothing_type,
      SUM(CASE WHEN length IS NULL THEN 1 ELSE 0 END) as null_length
    FROM items
    """
    
    cursor.execute(query)
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return result

def fill_null_category_by_clothing_type(batch_size=1000):
    """
    根據 clothing_type 填補 category 空值
    例如：Tshirts, Shirts → top
    """
    conn = connect_db()
    cursor = conn.cursor()
    
    # 定義映射規則
    mappings = {
        'top': ['Tshirts', 'Shirts', 'Tops', 'Sweaters', 'Sweatshirts', 'Jackets', 
                'Blazers', 'Kurtas', 'Kurtis', 'Tunics', 'Jersey'],
        'bottom': ['Jeans', 'Trousers', 'Shorts', 'Track Pants', 'Leggings', 
                   'Capris', 'Skirts', 'Pants'],
        'shoes': ['Casual Shoes', 'Formal Shoes', 'Sports Shoes', 'Sandals', 
                  'Flip Flops', 'Heels', 'Flats', 'Boots'],
        'accessories': ['Watches', 'Belts', 'Wallets', 'Sunglasses', 'Caps', 
                        'Backpacks', 'Handbags', 'Clutches', 'Ties', 'Bags',
                        'Nail Polish', 'Jewellery']
    }
    
    total_updated = 0
    
    for category, types in mappings.items():
        for clothing_type in types:
            update_query = f"""
            UPDATE items 
            SET category = %s 
            WHERE category IS NULL 
              AND clothing_type = %s
            LIMIT {batch_size}
            """
            
            cursor.execute(update_query, (category, clothing_type))
            updated = cursor.rowcount
            
            if updated > 0:
                print(f"✅ 更新 {updated} 筆: clothing_type='{clothing_type}' → category='{category}'")
                total_updated += updated
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return total_updated

def fill_null_length(batch_size=1000):
    """填補 length 空值為 '-'（表示不適用）"""
    conn = connect_db()
    cursor = conn.cursor()
    
    update_query = f"""
    UPDATE items 
    SET length = '-' 
    WHERE length IS NULL
    LIMIT {batch_size}
    """
    
    cursor.execute(update_query)
    updated = cursor.rowcount
    
    conn.commit()
    cursor.close()
    conn.close()
    
    if updated > 0:
        print(f"✅ 填補 {updated} 筆 length 空值為 '-'")
    
    return updated

def main():
    print("=" * 60)
    print("📊 分析 items 表空值情況")
    print("=" * 60)
    
    # 分析空值
    stats = analyze_null_values()
    print(f"\n總資料筆數: {stats['total']:,}")
    print(f"\n空值統計:")
    print(f"  - category: {stats['null_category']:,} ({stats['null_category']/stats['total']*100:.1f}%)")
    print(f"  - color: {stats['null_color']:,} ({stats['null_color']/stats['total']*100:.1f}%)")
    print(f"  - price: {stats['null_price']:,} ({stats['null_price']/stats['total']*100:.1f}%)")
    print(f"  - image_url: {stats['null_image']:,} ({stats['null_image']/stats['total']*100:.1f}%)")
    print(f"  - sku: {stats['null_sku']:,} ({stats['null_sku']/stats['total']*100:.1f}%)")
    print(f"  - gender: {stats['null_gender']:,} ({stats['null_gender']/stats['total']*100:.1f}%)")
    print(f"  - clothing_type: {stats['null_clothing_type']:,} ({stats['null_clothing_type']/stats['total']*100:.1f}%)")
    print(f"  - length: {stats['null_length']:,} ({stats['null_length']/stats['total']*100:.1f}%)")
    
    print("\n" + "=" * 60)
    print("🔧 開始填補空值")
    print("=" * 60)
    
    # 執行填補
    if stats['null_category'] > 0:
        print("\n1️⃣ 根據 clothing_type 填補 category...")
        updated = fill_null_category_by_clothing_type()
        print(f"   共更新 {updated:,} 筆資料")
    
    if stats['null_length'] > 0:
        print("\n2️⃣ 填補 length 空值...")
        updated = fill_null_length()
        print(f"   共更新 {updated:,} 筆資料")
    
    # 再次分析
    print("\n" + "=" * 60)
    print("📊 填補後的空值統計")
    print("=" * 60)
    
    stats_after = analyze_null_values()
    print(f"\n空值統計:")
    print(f"  - category: {stats_after['null_category']:,} ({stats_after['null_category']/stats_after['total']*100:.1f}%)")
    print(f"  - color: {stats_after['null_color']:,} ({stats_after['null_color']/stats['total']*100:.1f}%)")
    print(f"  - price: {stats_after['null_price']:,} ({stats_after['null_price']/stats['total']*100:.1f}%)")
    print(f"  - image_url: {stats_after['null_image']:,} ({stats_after['null_image']/stats['total']*100:.1f}%)")
    print(f"  - length: {stats_after['null_length']:,} ({stats_after['null_length']/stats['total']*100:.1f}%)")
    
    print("\n✅ 完成！")

if __name__ == '__main__':
    main()
