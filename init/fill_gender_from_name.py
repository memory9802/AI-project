#!/usr/bin/env python3
"""
穩定的性別填補腳本 - 從 name 判斷 gender
===========================================
特性:
✅ 小批次處理 (每次 10 筆)
✅ 進度保存,可中斷恢復
✅ 不依賴網路,本地規則判斷
✅ 詳細日誌記錄
✅ 適合通勤時使用
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
PROGRESS_FILE = '/Users/liaoyiting/Desktop/stylerec/init/gender_fill_progress.json'
LOG_FILE = '/Users/liaoyiting/Desktop/stylerec/init/gender_fill_log.txt'

# 每批次處理數量 (建議 5-20)
BATCH_SIZE = 10

# 性別判斷規則 (基於常見服飾關鍵字)
GENDER_KEYWORDS = {
    '男': [
        'Men', 'Male', 'Man', 'Boy', 'Mens', "Men's",
        'Gents', 'Masculine', 'Guy', 'Dude', 'Father',
        'Shirt', 'Polo', 'Suit', 'Blazer', 'Tie'
    ],
    '女': [
        'Women', 'Female', 'Woman', 'Girl', 'Womens', "Women's",
        'Ladies', 'Lady', 'Feminine', 'Dress', 'Skirt',
        'Heels', 'Kurta', 'Kurti', 'Saree', 'Lehenga',
        'Bra', 'Dupatta', 'Leggings', 'Clutch'
    ],
    '男孩': ['Boy', 'Boys', 'Kid Boy', 'Toddler Boy'],
    '女孩': ['Girl', 'Girls', 'Kid Girl', 'Toddler Girl'],
    '中性': [
        'Unisex', 'Neutral', 'Kids', 'Children', 'Baby',
        'Watch', 'Belt', 'Wallet', 'Backpack', 'Sunglass',
        'Cap', 'Hat', 'Scarf', 'Gloves', 'Socks',
        'Perfume', 'Fragrance', 'Accessory'
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
        'last_updated': None
    }

def save_progress(progress):
    """保存處理進度"""
    progress['last_updated'] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def detect_gender_from_name(name):
    """
    從商品名稱判斷性別
    返回: ('男'|'女'|'男孩'|'女孩'|'中性', 信心度)
    """
    if not name:
        return '中性', 0.0
    
    name_upper = name.upper()
    
    # 依序檢查:男孩/女孩 → 男/女 → 中性
    for gender, keywords in GENDER_KEYWORDS.items():
        for keyword in keywords:
            if keyword.upper() in name_upper:
                # 計算信心度 (基於關鍵字長度和位置)
                confidence = min(len(keyword) / len(name) * 2, 1.0)
                return gender, confidence
    
    # 無法判斷,返回中性
    return '中性', 0.0

def get_null_gender_count():
    """獲取 gender 空值總數"""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM items 
        WHERE gender IS NULL OR gender = ''
    """)
    
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    return count

def process_batch(start_id, batch_size):
    """
    處理一個批次
    返回: (處理數量, 更新數量, 最後處理的 ID)
    """
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    
    # 查詢需要處理的資料
    cursor.execute("""
        SELECT id, name, gender
        FROM items
        WHERE (gender IS NULL OR gender = '')
          AND id > %s
        ORDER BY id
        LIMIT %s
    """, (start_id, batch_size))
    
    items = cursor.fetchall()
    
    if not items:
        cursor.close()
        conn.close()
        return 0, 0, start_id
    
    processed_count = 0
    updated_count = 0
    last_id = start_id
    
    for item in items:
        item_id = item['id']
        item_name = item['name']
        
        # 判斷性別
        detected_gender, confidence = detect_gender_from_name(item_name)
        
        # 更新資料庫
        update_cursor = conn.cursor()
        update_cursor.execute("""
            UPDATE items 
            SET gender = %s
            WHERE id = %s
        """, (detected_gender, item_id))
        
        if update_cursor.rowcount > 0:
            updated_count += 1
            log_message(
                f"  ✅ ID {item_id:5d}: {item_name[:40]:40s} → {detected_gender:4s} "
                f"(信心度: {confidence:.2f})",
                print_to_console=False
            )
        
        update_cursor.close()
        processed_count += 1
        last_id = item_id
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return processed_count, updated_count, last_id

def analyze_results():
    """分析處理結果"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # 統計各性別數量
    cursor.execute("""
        SELECT 
            gender,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM items), 2) as percentage
        FROM items
        GROUP BY gender
        ORDER BY count DESC
    """)
    
    results = cursor.fetchall()
    
    print("\n" + "=" * 60)
    print("📊 性別分布統計")
    print("=" * 60)
    
    for row in results:
        gender = row[0] if row[0] else '(NULL)'
        count = row[1]
        percentage = row[2]
        print(f"{gender:10s}: {count:6,} 筆 ({percentage:5.2f}%)")
    
    # 檢查剩餘空值
    cursor.execute("""
        SELECT COUNT(*) 
        FROM items 
        WHERE gender IS NULL OR gender = ''
    """)
    
    remaining = cursor.fetchone()[0]
    print(f"\n⚠️  剩餘空值: {remaining:,} 筆")
    
    cursor.close()
    conn.close()

def main():
    """主程式"""
    print("\n" + "🚀" * 30)
    print("開始填補 gender 欄位 (從 name 判斷)")
    print("🚀" * 30)
    
    # 初始化日誌
    log_message("\n" + "=" * 60)
    log_message("新的處理任務開始")
    log_message("=" * 60)
    
    # 載入進度
    progress = load_progress()
    log_message(f"📂 載入進度: 已處理 {progress['total_processed']} 筆, "
                f"已更新 {progress['total_updated']} 筆")
    
    # 檢查剩餘數量
    remaining_count = get_null_gender_count()
    log_message(f"📊 剩餘待處理: {remaining_count:,} 筆")
    
    if remaining_count == 0:
        print("\n✅ 所有資料已處理完成!")
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
    
    try:
        while True:
            batch_num += 1
            batch_start_time = time.time()
            
            # 處理一個批次
            processed, updated, last_id = process_batch(
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
            save_progress(progress)
            
            # 計算速度
            batch_time = time.time() - batch_start_time
            elapsed_time = time.time() - start_time
            
            # 顯示進度
            remaining_now = get_null_gender_count()
            progress_percentage = ((remaining_count - remaining_now) / remaining_count * 100) if remaining_count > 0 else 100
            
            print(f"批次 {batch_num:4d}: 處理 {processed:2d} 筆, "
                  f"更新 {updated:2d} 筆 | "
                  f"剩餘 {remaining_now:6,} 筆 ({progress_percentage:5.1f}%) | "
                  f"耗時 {batch_time:.2f}s")
            
            log_message(
                f"批次 {batch_num}: 處理 {processed} 筆, 更新 {updated} 筆, "
                f"最後 ID: {last_id}, 剩餘: {remaining_now}"
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
        print(f"執行時間: {total_time:.2f} 秒 ({total_time/60:.1f} 分鐘)")
        print(f"平均速度: {progress['total_processed']/total_time:.1f} 筆/秒")
        print("=" * 60)
        
        log_message(f"處理完成: 總計 {progress['total_processed']} 筆, "
                    f"更新 {progress['total_updated']} 筆, "
                    f"耗時 {total_time:.2f} 秒")
        
        # 分析結果
        analyze_results()
        
        print(f"\n💾 進度檔案: {PROGRESS_FILE}")
        print(f"📝 日誌檔案: {LOG_FILE}")
        print("\n💡 如果還有剩餘空值,再次執行此腳本會自動繼續處理\n")

if __name__ == '__main__':
    try:
        main()
    except mysql.connector.Error as e:
        print(f"\n❌ 資料庫錯誤: {e}")
        log_message(f"資料庫錯誤: {e}")
    except Exception as e:
        print(f"\n❌ 未預期的錯誤: {e}")
        log_message(f"未預期的錯誤: {e}")
