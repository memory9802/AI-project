#!/usr/bin/env python3
"""
填補 items 表格剩餘空值
=======================
⚠️  重要: 此腳本應該在其他腳本之後執行!

執行順序:
1. fill_category_from_clothing_type.py (先執行)
2. fill_gender_from_name.py            (第二執行)
3. fill_remaining_nulls.py             (本腳本,最後執行)

處理欄位:
1. category 剩餘空值 → 'other'
2. color 剩餘空值    → '未分類'
3. gender 剩餘空值   → '中性'
"""

import mysql.connector
from datetime import datetime

# 資料庫連接設定
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'rootpassword',
    'database': 'outfit_db'
}

def connect_db():
    """連接資料庫"""
    return mysql.connector.connect(**DB_CONFIG)


def check_prerequisites():
    """檢查前置條件 - 確保前面的腳本已執行"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # 檢查 category 是否大部分已填補
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN category IS NULL OR category = '' THEN 1 ELSE 0 END) as null_count
        FROM items
    """)
    total, cat_null = cursor.fetchone()
    cat_percentage = (cat_null / total) * 100 if total > 0 else 0
    
    # 檢查 gender 是否大部分已填補
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN gender IS NULL OR gender = '' THEN 1 ELSE 0 END) as null_count
        FROM items
    """)
    gen_null = cursor.fetchone()[0]
    gen_percentage = (gen_null / total) * 100 if total > 0 else 0
    
    cursor.close()
    conn.close()
    
    warnings = []
    
    # 如果 category 空值超過 20%,建議先執行 fill_category
    if cat_percentage > 20:
        warnings.append(
            f"⚠️  category 空值 {cat_null:,} 筆 ({cat_percentage:.1f}%)\n"
            f"   建議先執行: fill_category_from_clothing_type.py"
        )
    
    # 如果 gender 空值超過 10%,建議先執行 fill_gender
    if gen_percentage > 10:
        warnings.append(
            f"⚠️  gender 空值 {gen_null:,} 筆 ({gen_percentage:.1f}%)\n"
            f"   建議先執行: fill_gender_from_name.py"
        )
    
    if warnings:
        print("\n" + "=" * 60)
        print("⚠️  前置檢查警告")
        print("=" * 60)
        for warning in warnings:
            print(warning)
        print("\n建議執行順序:")
        print("  1. fill_category_from_clothing_type.py")
        print("  2. fill_gender_from_name.py")
        print("  3. fill_remaining_nulls.py (本腳本)")
        print("=" * 60)
        
        response = input("\n是否仍要繼續? [y/N]: ")
        if response.lower() != 'y':
            print("❌ 已取消執行")
            return False
    
    return True


def analyze_nulls_before():
    """分析填補前的空值情況"""
    conn = connect_db()
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("📊 填補前空值統計")
    print("=" * 60)
    
    cursor.execute("SELECT COUNT(*) FROM items")
    total = cursor.fetchone()[0]
    print(f"總資料筆數: {total:,}\n")
    
    fields = ['category', 'color', 'gender']
    stats = {}
    
    for field in fields:
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM items 
            WHERE {field} IS NULL OR {field} = ''
        """)
        null_count = cursor.fetchone()[0]
        percentage = (null_count / total) * 100
        stats[field] = null_count
        print(f"⚠️  {field:15s}: {null_count:6,} 筆 ({percentage:5.1f}%)")
    
    cursor.close()
    conn.close()
    
    return stats

def fill_category_nulls():
    """填補 category 空值為 'other'"""
    conn = connect_db()
    cursor = conn.cursor()
    
    print("\n" + "-" * 60)
    print("1️⃣  填補 category 空值...")
    print("-" * 60)
    
    cursor.execute("""
        UPDATE items 
        SET category = 'other' 
        WHERE category IS NULL OR category = ''
    """)
    
    updated = cursor.rowcount
    conn.commit()
    
    print(f"✅ 更新 {updated:,} 筆資料 → category = 'other'")
    
    cursor.close()
    conn.close()
    
    return updated

def fill_color_nulls():
    """填補 color 空值為 '未分類'"""
    conn = connect_db()
    cursor = conn.cursor()
    
    print("\n" + "-" * 60)
    print("2️⃣  填補 color 空值...")
    print("-" * 60)
    
    cursor.execute("""
        UPDATE items 
        SET color = '未分類' 
        WHERE color IS NULL OR color = ''
    """)
    
    updated = cursor.rowcount
    conn.commit()
    
    print(f"✅ 更新 {updated:,} 筆資料 → color = '未分類'")
    
    cursor.close()
    conn.close()
    
    return updated

def fill_gender_nulls():
    """填補 gender 空值為 '中性'"""
    conn = connect_db()
    cursor = conn.cursor()
    
    print("\n" + "-" * 60)
    print("3️⃣  填補 gender 空值...")
    print("-" * 60)
    
    cursor.execute("""
        UPDATE items 
        SET gender = '中性' 
        WHERE gender IS NULL OR gender = ''
    """)
    
    updated = cursor.rowcount
    conn.commit()
    
    print(f"✅ 更新 {updated:,} 筆資料 → gender = '中性'")
    
    cursor.close()
    conn.close()
    
    return updated

def analyze_nulls_after():
    """分析填補後的空值情況"""
    conn = connect_db()
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("📊 填補後空值統計")
    print("=" * 60)
    
    cursor.execute("SELECT COUNT(*) FROM items")
    total = cursor.fetchone()[0]
    
    fields = ['category', 'color', 'gender', 'price', 'image_url']
    
    for field in fields:
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM items 
            WHERE {field} IS NULL OR {field} = ''
        """)
        null_count = cursor.fetchone()[0]
        percentage = (null_count / total) * 100
        
        if null_count == 0:
            status = "✅"
        elif percentage > 50:
            status = "📦"  # 高比例空值(如 price/image_url)
        else:
            status = "⚠️"
        
        print(f"{status} {field:15s}: {null_count:6,} 筆 ({percentage:5.1f}%)")
    
    cursor.close()
    conn.close()

def verify_sample_data():
    """驗證填補後的資料範例"""
    conn = connect_db()
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("🔍 驗證資料範例 (隨機 5 筆)")
    print("=" * 60)
    
    cursor.execute("""
        SELECT id, name, category, color, gender, source
        FROM items
        ORDER BY RAND()
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        print(f"ID {row[0]:5d}: {row[1][:30]:30s} | "
              f"category={row[2]:10s} | color={row[3]:10s} | "
              f"gender={row[4]:6s} | source={row[5]}")
    
    cursor.close()
    conn.close()

def main():
    """主程式"""
    start_time = datetime.now()
    
    print("\n" + "🔧" * 30)
    print("開始填補 items 表格空值")
    print("🔧" * 30)
    
    # 0. 前置檢查
    if not check_prerequisites():
        return
    
    # 1. 分析填補前的情況
    stats_before = analyze_nulls_before()
    
    # 2. 執行填補
    total_updated = 0
    
    if stats_before['category'] > 0:
        total_updated += fill_category_nulls()
    else:
        print("\n1️⃣  category 無空值,跳過")
    
    if stats_before['color'] > 0:
        total_updated += fill_color_nulls()
    else:
        print("\n2️⃣  color 無空值,跳過")
    
    if stats_before['gender'] > 0:
        total_updated += fill_gender_nulls()
    else:
        print("\n3️⃣  gender 無空值,跳過")
    
    # 3. 分析填補後的情況
    analyze_nulls_after()
    
    # 4. 驗證資料範例
    verify_sample_data()
    
    # 5. 總結
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 60)
    print("✅ 填補完成!")
    print("=" * 60)
    print(f"共更新 {total_updated:,} 筆資料")
    print(f"執行時間: {duration:.2f} 秒")
    print(f"完成時間: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 提示:")
    print("   - price 和 image_url 保留空值(建議在 Flask 應用中處理)")
    print("   - 可在 DBeaver 中執行驗證查詢確認結果")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    try:
        main()
    except mysql.connector.Error as e:
        print(f"\n❌ 資料庫錯誤: {e}")
    except Exception as e:
        print(f"\n❌ 執行錯誤: {e}")
