#!/usr/bin/env python3
"""
穩定的 category 填補腳本 - 從 clothing_type 映射到大分類
========================================================
特性:
✅ 小批次處理 (每次 10 筆)
✅ 進度保存,可中斷恢復
✅ 不依賴網路,本地規則映射
✅ 詳細日誌記錄
✅ 適合通勤時使用

大分類:
- top (上衣)
- bottom (下衣)
- shoes (鞋子)
- accessories (飾品配件)
- underwear (內衣)
- dress (洋裝連身)
- beauty (美妝保養)
- bags (包包)
- other (其他)
"""

import mysql.connector
import json
import os
from datetime import datetime
import time

# 資料庫連接設定
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'rootpassword',
    'database': 'outfit_db'
}

# 進度檔案路徑
PROGRESS_FILE = '/Users/liaoyiting/Desktop/stylerec/init/category_fill_progress.json'
LOG_FILE = '/Users/liaoyiting/Desktop/stylerec/init/category_fill_log.txt'

# 每批次處理數量 (建議 5-20)
BATCH_SIZE = 10

# clothing_type → category 映射規則
CATEGORY_MAPPING = {
    'top': [
        # 上衣類
        'Tshirts', 'T-Shirts', 'Shirts', 'Tops',
        'Sweaters', 'Sweatshirts', 'Jackets', 'Blazers',
        'Kurtas', 'Kurtis', 'Tunics', 'Nehru Jackets',
        'Shrug', 'Waistcoat', 'Vest', 'Topwear',
        'Jersey', 'Tank Tops'
    ],
    'bottom': [
        # 下衣類
        'Jeans', 'Trousers', 'Pants', 'Track Pants',
        'Shorts', 'Skirts', 'Leggings', 'Capris',
        'Jeggings', 'Patiala', 'Salwar', 'Churidar',
        'Dhoti Pants', 'Bottomwear'
    ],
    'shoes': [
        # 鞋類
        'Shoes', 'Casual Shoes', 'Formal Shoes', 'Sports Shoes',
        'Heels', 'Flats', 'Sandals', 'Flip Flops',
        'Sneakers', 'Boots', 'Slippers', 'Floaters',
        'Mules', 'Wedges', 'Loafers', 'Shoe Accessories'
    ],
    'accessories': [
        # 飾品配件類
        'Watches', 'Belts', 'Sunglasses', 'Caps',
        'Wallets', 'Ties', 'Socks', 'Scarves', 'Stoles',
        'Cufflinks', 'Mufflers', 'Gloves', 'Hat',
        'Accessory Gift Set', 'Ring', 'Earrings',
        'Necklace and Chains', 'Pendant', 'Bracelet',
        'Bangle', 'Jewellery Set', 'Dupatta',
        'Umbrellas', 'Mobile Pouch', 'Key chain',
        'Hair Accessory', 'Headband', 'Wristbands'
    ],
    'underwear': [
        # 內衣類
        'Bra', 'Briefs', 'Boxers', 'Trunk', 'Trunks',
        'Innerwear Vests', 'Thermals', 'Shapewear',
        'Lingerie Set', 'Nightdress', 'Night suits',
        'Nightwear', 'Loungewear', 'Robe', 'Pyjamas',
        'Camisoles', 'Stockings'
    ],
    'dress': [
        # 洋裝連身類
        'Dresses', 'Gowns', 'Jumpsuits', 'Rompers',
        'Sarees', 'Lehenga Choli', 'Salwar Suit',
        'Kurta Sets', 'Dress Material', 'Patiala Suit',
        'Blouse', 'Lehenga', 'Ethnic Sets'
    ],
    'beauty': [
        # 美妝保養類
        'Perfume and Body Mist', 'Deodorant',
        'Lipstick', 'Lip Gloss', 'Lip Liner', 'Lip Care',
        'Kajal and Eyeliner', 'Nail Polish', 'Nail Care',
        'Foundation and Primer', 'Compact', 'Face Moisturisers',
        'Eye Cream', 'Night Cream', 'Face Wash',
        'Makeup Remover', 'Face Scrub', 'Hair Colour',
        'Hair Oil', 'Shampoo', 'Conditioner',
        'Fragrance Gift Set', 'Body Lotion', 'Body Wash',
        'Sunscreen', 'Kajal', 'Mascara', 'Concealer',
        'Beauty Accessory', 'Makeup Kit'
    ],
    'bags': [
        # 包包類
        'Handbags', 'Backpacks', 'Messenger Bag',
        'Laptop Bag', 'Travel Bag', 'Duffel Bag',
        'Trolley Bag', 'Clutches', 'Waist Pouch',
        'Rucksacks', 'Sling Bag', 'Tote Bag',
        'Basket', 'Luggage'
    ],
    'other': [
        # 其他
        'Free Gifts', 'Gift Set', 'Sports Equipment',
        'Water Bottle', 'Stationery', 'Baby Care',
        'Home Furnishing', 'Bath Towels', 'Bedsheets',
        'Curtains', 'Cushions', 'Frames'
    ]
}

def log_message(message, print_to_console=True):
    """寫入日誌"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {message}\n"
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_line)
    
    if print_to_console:
        print(message)

def connect_db():
    """連接資料庫"""
    return mysql.connector.connect(**DB_CONFIG)

def load_progress():
    """載入處理進度"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'last_processed_id': 0,
        'total_processed': 0,
        'total_updated': 0,
        'started_at': datetime.now().isoformat(),
        'last_updated': None,
        'category_stats': {}
    }

def save_progress(progress):
    """保存處理進度"""
    progress['last_updated'] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def detect_category_from_clothing_type(clothing_type):
    """
    從 clothing_type 判斷 category
    返回: ('top'|'bottom'|'shoes'|'accessories'|...|None, 信心度)
    """
    if not clothing_type:
        return None, 0.0
    
    clothing_type_clean = clothing_type.strip()
    
    # 直接匹配
    for category, type_list in CATEGORY_MAPPING.items():
        if clothing_type_clean in type_list:
            return category, 1.0
    
    # 模糊匹配 (處理複數、大小寫等)
    clothing_type_upper = clothing_type_clean.upper()
    for category, type_list in CATEGORY_MAPPING.items():
        for item in type_list:
            if item.upper() in clothing_type_upper or clothing_type_upper in item.upper():
                return category, 0.8
    
    # 無法判斷
    return None, 0.0

def get_null_category_count():
    """獲取 category 空值總數"""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM items 
        WHERE category IS NULL OR category = ''
    """)
    
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    return count

def process_batch(start_id, batch_size):
    """
    處理一個批次
    返回: (處理數量, 更新數量, 最後處理的 ID, 無法映射數量)
    """
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    
    # 查詢需要處理的資料
    cursor.execute("""
        SELECT id, name, clothing_type, category
        FROM items
        WHERE (category IS NULL OR category = '')
          AND id > %s
        ORDER BY id
        LIMIT %s
    """, (start_id, batch_size))
    
    items = cursor.fetchall()
    
    if not items:
        cursor.close()
        conn.close()
        return 0, 0, start_id, 0
    
    processed_count = 0
    updated_count = 0
    unmapped_count = 0
    last_id = start_id
    
    for item in items:
        item_id = item['id']
        item_name = item['name']
        clothing_type = item['clothing_type']
        
        # 判斷 category
        detected_category, confidence = detect_category_from_clothing_type(clothing_type)
        
        if detected_category:
            # 更新資料庫
            update_cursor = conn.cursor()
            update_cursor.execute("""
                UPDATE items 
                SET category = %s
                WHERE id = %s
            """, (detected_category, item_id))
            
            if update_cursor.rowcount > 0:
                updated_count += 1
                log_message(
                    f"  ✅ ID {item_id:5d}: {clothing_type:30s} → {detected_category:12s} "
                    f"(信心度: {confidence:.2f})",
                    print_to_console=False
                )
            
            update_cursor.close()
        else:
            unmapped_count += 1
            log_message(
                f"  ⚠️  ID {item_id:5d}: {clothing_type:30s} → 無法映射",
                print_to_console=False
            )
        
        processed_count += 1
        last_id = item_id
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return processed_count, updated_count, last_id, unmapped_count

def analyze_results():
    """分析處理結果"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # 統計各 category 數量
    cursor.execute("""
        SELECT 
            category,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM items), 2) as percentage
        FROM items
        GROUP BY category
        ORDER BY count DESC
    """)
    
    results = cursor.fetchall()
    
    print("\n" + "=" * 60)
    print("📊 category 分布統計")
    print("=" * 60)
    
    for row in results:
        category = row[0] if row[0] else '(NULL)'
        count = row[1]
        percentage = row[2]
        print(f"{category:15s}: {count:6,} 筆 ({percentage:5.2f}%)")
    
    # 檢查剩餘空值
    cursor.execute("""
        SELECT COUNT(*) 
        FROM items 
        WHERE category IS NULL OR category = ''
    """)
    
    remaining = cursor.fetchone()[0]
    print(f"\n⚠️  剩餘空值: {remaining:,} 筆")
    
    # 顯示無法映射的 clothing_type
    if remaining > 0:
        cursor.execute("""
            SELECT 
                clothing_type,
                COUNT(*) as count
            FROM items
            WHERE category IS NULL OR category = ''
            GROUP BY clothing_type
            ORDER BY count DESC
            LIMIT 10
        """)
        
        print(f"\n無法映射的 clothing_type (前 10 項):")
        print("-" * 60)
        for row in cursor.fetchall():
            print(f"{row[0]:35s}: {row[1]:5,} 筆")
    
    cursor.close()
    conn.close()

def main():
    """主程式"""
    print("\n" + "🚀" * 30)
    print("開始填補 category 欄位 (從 clothing_type 映射)")
    print("🚀" * 30)
    
    # 初始化日誌
    log_message("\n" + "=" * 60)
    log_message("新的處理任務開始 - category 填補")
    log_message("=" * 60)
    
    # 載入進度
    progress = load_progress()
    log_message(f"📂 載入進度: 已處理 {progress['total_processed']} 筆, "
                f"已更新 {progress['total_updated']} 筆")
    
    # 檢查剩餘數量
    remaining_count = get_null_category_count()
    log_message(f"📊 剩餘待處理: {remaining_count:,} 筆")
    
    if remaining_count == 0:
        print("\n✅ 所有資料已處理完成!")
        analyze_results()
        return
    
    # 計算預估時間
    estimated_batches = (remaining_count // BATCH_SIZE) + 1
    estimated_minutes = (estimated_batches * 2) / 60  # 假設每批次 2 秒
    
    log_message(f"⏱️  預估批次數: {estimated_batches:,} 個")
    log_message(f"⏱️  預估時間: {estimated_minutes:.1f} 分鐘")
    log_message(f"⚙️  批次大小: {BATCH_SIZE} 筆/批次")
    
    print("\n" + "-" * 60)
    print("開始批次處理...")
    print("💡 可隨時按 Ctrl+C 中斷,下次會自動繼續")
    print("-" * 60 + "\n")
    
    start_time = time.time()
    batch_num = 0
    total_unmapped = 0
    
    try:
        while True:
            batch_num += 1
            batch_start_time = time.time()
            
            # 處理一個批次
            processed, updated, last_id, unmapped = process_batch(
                progress['last_processed_id'],
                BATCH_SIZE
            )
            
            if processed == 0:
                log_message("\n✅ 所有批次處理完成!")
                break
            
            # 更新進度
            progress['last_processed_id'] = last_id
            progress['total_processed'] += processed
            progress['total_updated'] += updated
            total_unmapped += unmapped
            save_progress(progress)
            
            # 計算速度
            batch_time = time.time() - batch_start_time
            elapsed_time = time.time() - start_time
            
            # 顯示進度
            remaining_now = get_null_category_count()
            progress_percentage = ((remaining_count - remaining_now) / remaining_count * 100) if remaining_count > 0 else 100
            
            print(f"批次 {batch_num:4d}: 處理 {processed:2d} 筆, "
                  f"更新 {updated:2d} 筆, 無法映射 {unmapped:2d} 筆 | "
                  f"剩餘 {remaining_now:6,} 筆 ({progress_percentage:5.1f}%) | "
                  f"耗時 {batch_time:.2f}s")
            
            log_message(
                f"批次 {batch_num}: 處理 {processed} 筆, 更新 {updated} 筆, "
                f"無法映射 {unmapped} 筆, 最後 ID: {last_id}, 剩餘: {remaining_now}"
            )
            
            # 短暫休息,避免資料庫壓力
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  使用者中斷處理")
        log_message("使用者中斷處理 (Ctrl+C)")
        print(f"✅ 進度已保存: {progress['total_processed']} 筆已處理")
        print(f"💡 下次執行會從 ID {progress['last_processed_id']} 繼續")
    
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        log_message(f"錯誤: {e}")
        print(f"✅ 進度已保存,可重新執行繼續處理")
    
    finally:
        # 總結
        total_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("📊 處理總結")
        print("=" * 60)
        print(f"總處理筆數: {progress['total_processed']:,}")
        print(f"總更新筆數: {progress['total_updated']:,}")
        print(f"無法映射筆數: {total_unmapped:,}")
        print(f"映射成功率: {(progress['total_updated']/progress['total_processed']*100):.1f}%")
        print(f"執行時間: {total_time:.2f} 秒 ({total_time/60:.1f} 分鐘)")
        if total_time > 0:
            print(f"平均速度: {progress['total_processed']/total_time:.1f} 筆/秒")
        print("=" * 60)
        
        log_message(f"處理完成: 總計 {progress['total_processed']} 筆, "
                    f"更新 {progress['total_updated']} 筆, "
                    f"耗時 {total_time:.2f} 秒")
        
        # 分析結果
        analyze_results()
        
        print(f"\n💾 進度檔案: {PROGRESS_FILE}")
        print(f"📝 日誌檔案: {LOG_FILE}")
        print("\n💡 如果還有剩餘空值,可能需要新增映射規則或手動處理\n")

if __name__ == '__main__':
    try:
        main()
    except mysql.connector.Error as e:
        print(f"\n❌ 資料庫錯誤: {e}")
        log_message(f"資料庫錯誤: {e}")
    except Exception as e:
        print(f"\n❌ 未預期的錯誤: {e}")
        log_message(f"未預期的錯誤: {e}")
