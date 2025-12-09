#!/usr/bin/env python3
"""
智能填充 items 表格 - category 和 gender 欄位
================================================
根據 name 欄位智能判斷並填入 category 和 gender

特性:
✅ 小批次處理 (每次 50 筆,可調整)
✅ 進度保存,可隨時中斷恢復
✅ 智能關鍵字匹配
✅ 詳細日誌和統計
✅ 低 token 消耗
✅ 支援 Docker 容器內執行
"""

import mysql.connector
import json
import os
import re
from datetime import datetime
from typing import Tuple, Optional, Dict

# ==================== 配置區 ====================

# 資料庫連接設定
DB_CONFIG = {
    'host': 'localhost',  # Docker: 'outfit-mysql'
    'port': 3306,
    'user': 'root',
    'password': 'rootpassword',
    'database': 'outfit_db'
}

# 檔案路徑
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROGRESS_FILE = os.path.join(SCRIPT_DIR, 'smart_fill_progress.json')
LOG_FILE = os.path.join(SCRIPT_DIR, 'smart_fill_log.txt')

# 處理參數
BATCH_SIZE = 50  # 每批次處理數量
MAX_RETRIES = 3  # 失敗重試次數

# ==================== 關鍵字規則 ====================

# Category 分類規則 (優先級由高到低)
CATEGORY_RULES = {
    'top': {
        'keywords': [
            # 上衣類型
            'shirt', 't-shirt', 'tshirt', 'tee', 'top', 'blouse', 
            'sweater', 'sweatshirt', 'hoodie', 'jacket', 'coat', 
            'blazer', 'cardigan', 'vest', 'tank', 'polo',
            # 中文
            '上衣', '襯衫', 'T恤', '外套', '夾克', '毛衣',
            '連帽', '背心', 'POLO', '針織衫'
        ],
        'priority': 10
    },
    'bottom': {
        'keywords': [
            # 下身類型
            'pants', 'jeans', 'trousers', 'shorts', 'skirt',
            'leggings', 'joggers', 'chinos', 'cargo', 'denim',
            # 中文
            '褲', '牛仔褲', '短褲', '長褲', '裙', '內搭褲'
        ],
        'priority': 9
    },
    'shoes': {
        'keywords': [
            # 鞋類
            'shoes', 'sneakers', 'boots', 'sandals', 'heels',
            'loafers', 'slippers', 'flats', 'oxfords', 'pumps',
            'moccasins', 'trainers',
            # 中文
            '鞋', '靴', '涼鞋', '拖鞋', '高跟鞋', '運動鞋'
        ],
        'priority': 8
    },
    'accessories': {
        'keywords': [
            # 配件
            'bag', 'backpack', 'wallet', 'belt', 'watch',
            'hat', 'cap', 'scarf', 'tie', 'bow', 'gloves',
            'socks', 'sunglasses', 'glasses', 'jewelry',
            'necklace', 'bracelet', 'ring', 'earrings',
            'clutch', 'purse', 'handbag', 'tote',
            # 中文
            '包', '背包', '錢包', '皮帶', '手錶', '帽',
            '圍巾', '領帶', '手套', '襪', '太陽眼鏡',
            '項鍊', '手鍊', '戒指', '耳環'
        ],
        'priority': 7
    }
}

# Gender 性別規則
GENDER_RULES = {
    '男': {
        'keywords': [
            # 英文關鍵字
            'men', 'male', 'man', "men's", 'mens', 'gents',
            'masculine', 'boy', 'boys', 'father', 'guy',
            # 服飾特徵
            'suit', 'blazer', 'tie', 'tuxedo',
            # 中文
            '男', '男士', '男裝', '男生', '紳士'
        ],
        'priority': 10
    },
    '女': {
        'keywords': [
            # 英文關鍵字
            'women', 'female', 'woman', "women's", 'womens',
            'ladies', 'lady', 'feminine', 'girl', 'girls',
            'mother', 'mom',
            # 服飾特徵
            'dress', 'skirt', 'heels', 'bra', 'leggings',
            'kurta', 'kurti', 'saree', 'lehenga', 'dupatta',
            'clutch', 'pumps',
            # 中文
            '女', '女士', '女裝', '女生', '淑女'
        ],
        'priority': 10
    },
    '男孩': {
        'keywords': [
            'boy', 'boys', 'kid boy', 'toddler boy',
            'child boy', 'youth boy',
            '男孩', '男童', '小男孩'
        ],
        'priority': 9
    },
    '女孩': {
        'keywords': [
            'girl', 'girls', 'kid girl', 'toddler girl',
            'child girl', 'youth girl',
            '女孩', '女童', '小女孩'
        ],
        'priority': 9
    },
    '中性': {
        'keywords': [
            # 明確中性
            'unisex', 'neutral', 'gender neutral',
            # 兒童(不分性別)
            'kids', 'children', 'baby', 'infant', 'toddler',
            # 配件(通常中性)
            'watch', 'belt', 'wallet', 'backpack', 'bag',
            'sunglasses', 'cap', 'hat', 'scarf', 'gloves',
            'socks', 'perfume', 'fragrance',
            # 中文
            '中性', '兒童', '寶寶', '配件'
        ],
        'priority': 5
    }
}

# ==================== 核心功能 ====================

def log(message: str, level: str = 'INFO'):
    """寫入日誌"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] [{level}] {message}\n"
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_line)
    
    print(f"[{level}] {message}")

def connect_db() -> mysql.connector.MySQLConnection:
    """連接資料庫"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        log(f"✅ 成功連接資料庫: {DB_CONFIG['database']}")
        return conn
    except Exception as e:
        log(f"❌ 資料庫連接失敗: {e}", 'ERROR')
        raise

def load_progress() -> Dict:
    """載入處理進度"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                progress = json.load(f)
                log(f"📂 載入進度: 已處理 {progress['total_processed']} 筆")
                return progress
        except Exception as e:
            log(f"⚠️  進度檔案損壞,重新開始: {e}", 'WARNING')
    
    # 初始進度
    return {
        'last_processed_id': 0,
        'total_processed': 0,
        'category_updated': 0,
        'gender_updated': 0,
        'both_updated': 0,
        'started_at': datetime.now().isoformat(),
        'last_updated': None,
        'batches_completed': 0
    }

def save_progress(progress: Dict):
    """保存處理進度"""
    progress['last_updated'] = datetime.now().isoformat()
    try:
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log(f"⚠️  進度保存失敗: {e}", 'WARNING')

def detect_category(name: str) -> Tuple[Optional[str], float]:
    """
    從商品名稱判斷分類
    返回: (category, confidence)
    """
    if not name:
        return None, 0.0
    
    name_lower = name.lower()
    best_match = None
    best_score = 0.0
    
    for category, rule in CATEGORY_RULES.items():
        score = 0.0
        matches = 0
        
        for keyword in rule['keywords']:
            # 使用正則表達式進行完整單詞匹配
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, name_lower):
                matches += 1
                score += rule['priority']
        
        if matches > 0:
            # 計算信心度: (匹配數 * 優先級) / 可能的最大分數
            confidence = min(score / 10.0, 1.0)
            if score > best_score:
                best_score = score
                best_match = category
    
    if best_match:
        confidence = min(best_score / 10.0, 1.0)
        return best_match, confidence
    
    return None, 0.0

def detect_gender(name: str) -> Tuple[Optional[str], float]:
    """
    從商品名稱判斷性別
    返回: (gender, confidence)
    """
    if not name:
        return '中性', 0.5
    
    name_lower = name.lower()
    scores = {}
    
    for gender, rule in GENDER_RULES.items():
        score = 0.0
        matches = 0
        
        for keyword in rule['keywords']:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, name_lower):
                matches += 1
                score += rule['priority']
        
        if matches > 0:
            scores[gender] = score
    
    # 如果沒有匹配,返回中性
    if not scores:
        return '中性', 0.3
    
    # 選擇最高分
    best_gender = max(scores, key=scores.get)
    best_score = scores[best_gender]
    
    # 計算信心度
    confidence = min(best_score / 10.0, 1.0)
    
    return best_gender, confidence

def process_batch(conn: mysql.connector.MySQLConnection, 
                  start_id: int, 
                  batch_size: int) -> Tuple[int, int, int]:
    """
    處理一個批次的資料
    返回: (處理數量, category更新數, gender更新數)
    """
    cursor = conn.cursor(dictionary=True)
    
    # 查詢需要處理的資料 (category 或 gender 為 NULL)
    query = """
        SELECT id, name, category, gender 
        FROM items 
        WHERE id > %s 
        AND (category IS NULL OR gender IS NULL)
        ORDER BY id 
        LIMIT %s
    """
    
    cursor.execute(query, (start_id, batch_size))
    rows = cursor.fetchall()
    
    if not rows:
        log("✅ 沒有更多需要處理的資料")
        cursor.close()
        return 0, 0, 0
    
    category_updates = 0
    gender_updates = 0
    
    for row in rows:
        item_id = row['id']
        name = row['name']
        current_category = row['category']
        current_gender = row['gender']
        
        updates = []
        params = []
        
        # 判斷 category (如果為 NULL)
        if current_category is None:
            category, cat_conf = detect_category(name)
            if category:
                updates.append("category = %s")
                params.append(category)
                category_updates += 1
        
        # 判斷 gender (如果為 NULL)
        if current_gender is None:
            gender, gen_conf = detect_gender(name)
            if gender:
                updates.append("gender = %s")
                params.append(gender)
                gender_updates += 1
        
        # 如果有需要更新的欄位
        if updates:
            update_query = f"""
                UPDATE items 
                SET {', '.join(updates)}
                WHERE id = %s
            """
            params.append(item_id)
            
            try:
                cursor.execute(update_query, params)
                conn.commit()
            except Exception as e:
                log(f"⚠️  更新失敗 ID={item_id}: {e}", 'WARNING')
                conn.rollback()
    
    processed = len(rows)
    cursor.close()
    
    return processed, category_updates, gender_updates

def get_total_nulls(conn: mysql.connector.MySQLConnection) -> Tuple[int, int]:
    """取得需要處理的總數"""
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM items WHERE category IS NULL")
    category_nulls = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM items WHERE gender IS NULL")
    gender_nulls = cursor.fetchone()[0]
    
    cursor.close()
    return category_nulls, gender_nulls

def show_statistics(conn: mysql.connector.MySQLConnection):
    """顯示統計資訊"""
    cursor = conn.cursor()
    
    # 總數
    cursor.execute("SELECT COUNT(*) FROM items")
    total = cursor.fetchone()[0]
    
    # Category 統計
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN category IS NULL THEN 1 ELSE 0 END) as null_count,
            SUM(CASE WHEN category = 'top' THEN 1 ELSE 0 END) as top_count,
            SUM(CASE WHEN category = 'bottom' THEN 1 ELSE 0 END) as bottom_count,
            SUM(CASE WHEN category = 'shoes' THEN 1 ELSE 0 END) as shoes_count,
            SUM(CASE WHEN category = 'accessories' THEN 1 ELSE 0 END) as acc_count
        FROM items
    """)
    cat_stats = cursor.fetchone()
    
    # Gender 統計
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) as null_count,
            SUM(CASE WHEN gender = '男' THEN 1 ELSE 0 END) as male_count,
            SUM(CASE WHEN gender = '女' THEN 1 ELSE 0 END) as female_count,
            SUM(CASE WHEN gender = '中性' THEN 1 ELSE 0 END) as neutral_count,
            SUM(CASE WHEN gender = '男孩' THEN 1 ELSE 0 END) as boy_count,
            SUM(CASE WHEN gender = '女孩' THEN 1 ELSE 0 END) as girl_count
        FROM items
    """)
    gen_stats = cursor.fetchone()
    
    cursor.close()
    
    print("\n" + "="*60)
    print("📊 資料庫統計")
    print("="*60)
    print(f"總筆數: {total:,}")
    print()
    print(f"📂 Category 分佈:")
    print(f"  - NULL:        {cat_stats[0]:>8,} ({cat_stats[0]/total*100:>5.1f}%)")
    print(f"  - top:         {cat_stats[1]:>8,} ({cat_stats[1]/total*100:>5.1f}%)")
    print(f"  - bottom:      {cat_stats[2]:>8,} ({cat_stats[2]/total*100:>5.1f}%)")
    print(f"  - shoes:       {cat_stats[3]:>8,} ({cat_stats[3]/total*100:>5.1f}%)")
    print(f"  - accessories: {cat_stats[4]:>8,} ({cat_stats[4]/total*100:>5.1f}%)")
    print()
    print(f"👤 Gender 分佈:")
    print(f"  - NULL:   {gen_stats[0]:>8,} ({gen_stats[0]/total*100:>5.1f}%)")
    print(f"  - 男:     {gen_stats[1]:>8,} ({gen_stats[1]/total*100:>5.1f}%)")
    print(f"  - 女:     {gen_stats[2]:>8,} ({gen_stats[2]/total*100:>5.1f}%)")
    print(f"  - 中性:   {gen_stats[3]:>8,} ({gen_stats[3]/total*100:>5.1f}%)")
    print(f"  - 男孩:   {gen_stats[4]:>8,} ({gen_stats[4]/total*100:>5.1f}%)")
    print(f"  - 女孩:   {gen_stats[5]:>8,} ({gen_stats[5]/total*100:>5.1f}%)")
    print("="*60 + "\n")

# ==================== 主程式 ====================

def main():
    """主程式"""
    print("\n" + "="*60)
    print("🚀 智能填充 items 表格 - category & gender")
    print("="*60)
    
    # 載入進度
    progress = load_progress()
    
    # 連接資料庫
    try:
        conn = connect_db()
    except Exception:
        return
    
    # 顯示當前統計
    show_statistics(conn)
    
    # 取得需要處理的總數
    cat_nulls, gen_nulls = get_total_nulls(conn)
    total_nulls = max(cat_nulls, gen_nulls)
    
    if total_nulls == 0:
        log("✅ 所有資料都已填充完成!")
        conn.close()
        return
    
    log(f"📋 待處理: category={cat_nulls:,}, gender={gen_nulls:,}")
    
    # 詢問是否繼續
    response = input(f"\n是否開始處理? (每批次 {BATCH_SIZE} 筆) [y/N]: ")
    if response.lower() != 'y':
        log("❌ 使用者取消操作")
        conn.close()
        return
    
    # 批次處理
    start_id = progress['last_processed_id']
    batch_num = progress['batches_completed']
    
    try:
        while True:
            batch_num += 1
            log(f"\n🔄 批次 {batch_num}: 處理 ID > {start_id}")
            
            processed, cat_updated, gen_updated = process_batch(
                conn, start_id, BATCH_SIZE
            )
            
            if processed == 0:
                break
            
            # 更新進度
            progress['total_processed'] += processed
            progress['category_updated'] += cat_updated
            progress['gender_updated'] += gen_updated
            progress['batches_completed'] = batch_num
            
            # 取得最後處理的 ID
            cursor = conn.cursor()
            cursor.execute("""
                SELECT MAX(id) FROM items 
                WHERE id > %s 
                LIMIT %s
            """, (start_id, BATCH_SIZE))
            max_id = cursor.fetchone()[0]
            cursor.close()
            
            if max_id:
                progress['last_processed_id'] = max_id
                start_id = max_id
            
            save_progress(progress)
            
            log(f"✅ 批次 {batch_num} 完成: 處理 {processed} 筆, "
                f"category={cat_updated}, gender={gen_updated}")
            
            # 檢查是否還有需要處理的資料
            cat_nulls, gen_nulls = get_total_nulls(conn)
            remaining = max(cat_nulls, gen_nulls)
            
            if remaining == 0:
                log("🎉 全部處理完成!")
                break
            
            log(f"📊 剩餘: category={cat_nulls:,}, gender={gen_nulls:,}")
            
            # 短暫休息 (避免資料庫負載過高)
            import time
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        log("\n⏸️  使用者中斷,進度已保存", 'WARNING')
    except Exception as e:
        log(f"\n❌ 錯誤: {e}", 'ERROR')
        import traceback
        log(traceback.format_exc(), 'ERROR')
    finally:
        conn.close()
        log("🔌 資料庫連接已關閉")
    
    # 最終統計
    print("\n" + "="*60)
    print("📈 處理摘要")
    print("="*60)
    print(f"總處理筆數:    {progress['total_processed']:>8,}")
    print(f"Category 更新: {progress['category_updated']:>8,}")
    print(f"Gender 更新:   {progress['gender_updated']:>8,}")
    print(f"完成批次:      {progress['batches_completed']:>8}")
    print("="*60)
    
    # 顯示最終統計
    conn = connect_db()
    show_statistics(conn)
    conn.close()

if __name__ == '__main__':
    main()
